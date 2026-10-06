"""Fixed Windows/WSL transport; no service action on import or construction refusal."""

import json
import math
from pathlib import Path
import secrets
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard import clock_comparison as control, clock_lineage as lineage
from scripts import clock_comparison_review as review

RUN_NAME = "engine2-guest-client-comparison-20261006"
RUN_DIR = ROOT / "output" / RUN_NAME
GUEST_ROOT = "/mnt/d/research f1"
WSL = ("wsl.exe", "-d", "ACG-Research")
HIDDEN = 0x08000000
BREAKAWAY = 0x01000000
NEW_GROUP = 0x00000200


def timeout_value(value):
    if (
        type(value) not in {int, float}
        or not math.isfinite(value)
        or not 0 < value <= 45
    ):
        raise ValueError("invalid operation timeout")
    return value


def command(arguments, timeout, root=False):
    if sys.platform != "win32":
        raise ValueError("Windows transport required")
    timeout = timeout_value(timeout)
    vector = [
        *WSL,
        "-u",
        "root" if root else "acgresearch",
        "--cd",
        GUEST_ROOT,
        "--exec",
        *arguments,
    ]
    try:
        result = subprocess.run(
            vector,
            timeout=timeout,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            shell=False,
            creationflags=HIDDEN,
        )
    except subprocess.TimeoutExpired:
        raise TimeoutError("fixed WSL operation timed out") from None
    if result.returncode != 0 or len(result.stdout) > 16384:
        raise ValueError("fixed WSL operation failed")
    return result.stdout.decode("utf-8", errors="strict").strip()


def service_state(timeout):
    text = command(
        [
            "/usr/bin/systemctl",
            "show",
            "systemd-timesyncd",
            "--property=ActiveState",
            "--property=SubState",
            "--property=UnitFileState",
        ],
        timeout,
    )
    lines = [line.split("=", 1) for line in text.splitlines()]
    if len(lines) != 3 or any(len(row) != 2 for row in lines):
        raise ValueError("invalid service properties")
    values = dict(lines)
    if set(values) != {"ActiveState", "SubState", "UnitFileState"}:
        raise ValueError("ambiguous service properties")
    return dict(
        active=values["ActiveState"],
        sub=values["SubState"],
        unit=values["UnitFileState"],
    )


def start_service(timeout):
    command(["/usr/bin/systemctl", "start", "systemd-timesyncd"], timeout, root=True)


def save_exclusive(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def read_json(path):
    with Path(path).open("rb") as stream:
        return lineage.strict_json(stream.read(100001))


def helper_flags():
    return HIDDEN | BREAKAWAY | NEW_GROUP if sys.platform == "win32" else 0


def helper_python():
    # Windows venv python.exe may be a redirector: its Popen PID isn't the worker.
    candidate = (
        Path(sys.base_prefix) / "python.exe"
        if sys.platform == "win32"
        else Path(sys.executable)
    )
    if not candidate.is_file():
        raise ValueError("direct helper interpreter unavailable")
    return str(candidate.resolve())


class NativeOps:
    def __init__(self, *, approved=False):
        if approved is not True:
            raise ValueError("specific intervention approval required")
        if sys.platform != "win32":
            raise ValueError("Windows host required")
        if RUN_DIR.resolve() != ROOT / "output" / RUN_NAME:
            raise ValueError("unexpected resolved batch path")
        RUN_DIR.mkdir(exist_ok=False)
        self.directory = RUN_DIR
        self.process = None
        self.armed = False
        self.nonce = secrets.token_hex(32)
        self.deadline_ns = None

    def source_hashes(self, timeout):
        started = time.monotonic()
        timeout_value(timeout)
        value = review.execution_source_hashes()
        if time.monotonic() - started > timeout:
            raise TimeoutError("source read deadline exceeded")
        return value

    def service_state(self, timeout):
        return service_state(timeout)

    def start_service(self, timeout):
        start_service(timeout)

    def preflight(self, timeout):
        deadline = time.monotonic() + timeout_value(timeout)
        state = service_state(deadline - time.monotonic())
        control.checked_service(state)
        command(
            [
                "/home/acgresearch/acg-venv/bin/python",
                "scripts/paired_pilot.py",
                "--preflight-only",
            ],
            deadline - time.monotonic(),
        )
        sensors = command(
            [
                "docker",
                "ps",
                "-a",
                "--filter",
                "name=acg-falco-",
                "--format",
                "{{.ID}}",
            ],
            deadline - time.monotonic(),
        )
        if sensors:
            raise ValueError("known sensor present")
        return dict(lab_ready=True, known_sensor_absent=True, service=state)

    def collect(self, label, timeout):
        if label not in control.LABELS:
            raise ValueError("unknown block")
        timeout = timeout_value(timeout)
        target = self.directory / f"{label}.json"
        if target.exists():
            raise FileExistsError("block receipt already exists")
        guest_target = GUEST_ROOT + "/" + target.relative_to(ROOT).as_posix()
        # Guest timeout is secondary; the Windows timeout bounds the WSL client.
        guest_limit = max(0.05, timeout - 1)
        command(
            [
                "/usr/bin/timeout",
                "--signal=INT",
                "--kill-after=0.5s",
                f"{guest_limit:.6f}s",
                "/home/acgresearch/acg-venv/bin/python",
                "scripts/kernel_clock_diagnostic.py",
                "--output",
                guest_target,
            ],
            timeout,
        )
        with target.open("rb") as stream:
            raw = stream.read(100001)
        if len(raw) > 100000:
            raise ValueError("receipt too large")
        return raw

    def arm_restore_watchdog(self, deadline_seconds, timeout):
        if (
            type(deadline_seconds) is not int
            or deadline_seconds != 60
            or self.process is not None
        ):
            raise ValueError("watchdog already requested or wrong deadline")
        timeout = timeout_value(timeout)
        until = time.monotonic() + timeout
        self.deadline_ns = time.monotonic_ns() + 60_000_000_000
        request = dict(
            mode="restore",
            approved=True,
            nonce=self.nonce,
            deadline_ns=self.deadline_ns,
            sources=review.execution_source_hashes(),
        )
        save_exclusive(self.directory / "watchdog-request.json", request)
        self.process = subprocess.Popen(
            [
                helper_python(),
                str(ROOT / "scripts/clock_restore_watchdog.py"),
                "--directory",
                str(self.directory),
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
            shell=False,
            creationflags=helper_flags(),
        )
        while time.monotonic() < until:
            if self.process.poll() is not None:
                raise ValueError("restore helper exited before readiness")
            if (self.directory / "watchdog-ready.signal").exists():
                ready = read_json(self.directory / "watchdog-ready.json")
                if ready != dict(
                    mode="restore",
                    nonce=self.nonce,
                    pid=self.process.pid,
                    deadline_ns=self.deadline_ns,
                ):
                    raise ValueError("restore helper acknowledgement differs")
                if self.deadline_ns - time.monotonic_ns() < 50_000_000_000:
                    raise TimeoutError("insufficient watchdog margin")
                self.armed = True
                return dict(armed=True, independent_process=True, deadline_seconds=60)
            time.sleep(0.02)
        raise TimeoutError("restore helper not ready")

    def stop_service(self, timeout):
        if (
            not self.armed
            or self.process is None
            or self.process.poll() is not None
            or self.deadline_ns is None
        ):
            raise ValueError("live watchdog required before stop")
        if self.deadline_ns - time.monotonic_ns() < 50_000_000_000:
            raise TimeoutError("watchdog margin too short")
        command(["/usr/bin/systemctl", "stop", "systemd-timesyncd"], timeout, root=True)

    def disarm_restore_watchdog(self, timeout):
        deadline = time.monotonic() + timeout_value(timeout)
        control.checked_service(service_state(deadline - time.monotonic()))
        if self.process is None:
            return True  # Failed launch never armed a child or stopped the service.
        save_exclusive(self.directory / "watchdog-cancel.json", dict(nonce=self.nonce))
        (self.directory / "watchdog-cancel.signal").open("x").close()
        self.process.wait(timeout=timeout_value(deadline - time.monotonic()))
        outcome = read_json(self.directory / "watchdog-outcome.json")
        valid = self.process.returncode == 0 and outcome == dict(
            mode="restore",
            nonce=self.nonce,
            status="disarmed",
            pid=self.process.pid,
        )
        if valid:
            self.armed = False
        return valid
