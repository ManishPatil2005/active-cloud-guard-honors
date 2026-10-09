import json
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace

import pytest

from scripts import (
    clock_comparison_transport as transport,
    clock_restore_watchdog as worker,
)
from scripts import clock_comparison_review as review, clock_comparison_batch as batch

COMMAND = transport.command


@pytest.fixture(autouse=True)
def no_live_service_commands(monkeypatch):
    monkeypatch.setattr(
        transport,
        "command",
        lambda *a, **k: pytest.fail("unexpected live service/WSL command"),
    )


def request(directory, mode="inert", seconds=1):
    value = dict(
        mode=mode,
        approved=True,
        nonce="a" * 64,
        deadline_ns=time.monotonic_ns() + int(seconds * 1_000_000_000),
        sources=review.execution_source_hashes(),
    )
    transport.save_exclusive(directory / "watchdog-request.json", value)
    return value


@pytest.mark.parametrize("value", [False, 0, -1, 46, float("nan"), float("inf"), "5"])
def test_timeout_refusals(value):
    with pytest.raises(ValueError):
        transport.timeout_value(value)


def test_fixed_vector_hidden_redacted_failure_and_timeout(monkeypatch):
    monkeypatch.setattr(transport.sys, "platform", "win32")
    calls = []

    def run(vector, **kwargs):
        calls.append((vector, kwargs))
        return SimpleNamespace(returncode=0, stdout=b"active\n")

    monkeypatch.setattr(transport.subprocess, "run", run)
    assert (
        COMMAND(["/usr/bin/systemctl", "start", "systemd-timesyncd"], 5, root=True)
        == "active"
    )
    args, flags = calls[0]
    assert args[:5] == ["wsl.exe", "-d", "ACG-Research", "-u", "root"]
    assert flags["shell"] is False and flags["creationflags"] == transport.HIDDEN
    assert flags["stderr"] == subprocess.DEVNULL and flags["timeout"] == 5
    monkeypatch.setattr(
        transport.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(returncode=1, stdout=b"private"),
    )
    with pytest.raises(ValueError, match="operation failed"):
        COMMAND(["fixed"], 5)

    def expired(*a, **k):
        raise subprocess.TimeoutExpired(["private"], 5, output=b"private")

    monkeypatch.setattr(transport.subprocess, "run", expired)
    with pytest.raises(TimeoutError) as error:
        COMMAND(["fixed"], 5)
    assert "private" not in str(error.value)
    monkeypatch.setattr(transport.sys, "platform", "linux")
    with pytest.raises(ValueError, match="Windows"):
        COMMAND(["fixed"], 5)


@pytest.mark.parametrize(
    "text",
    [
        "ActiveState=active\nSubState=running\nUnitFileState=enabled",
        "ActiveState=active\nActiveState=active\nSubState=running",
        "garbage",
        "ActiveState=active\nSubState=running\nUnitFileState=enabled\nExtra=x",
    ],
)
def test_property_parser_exact_and_duplicate_refusal(text, monkeypatch):
    monkeypatch.setattr(transport, "command", lambda *a, **k: text)
    if text.endswith("UnitFileState=enabled"):
        assert transport.service_state(5) == dict(
            active="active", sub="running", unit="enabled"
        )
    else:
        with pytest.raises(ValueError):
            transport.service_state(5)


def make_ops(tmp_path, monkeypatch):
    monkeypatch.setattr(transport.sys, "platform", "win32")
    monkeypatch.setattr(transport, "ROOT", tmp_path)
    (tmp_path / "output").mkdir()
    monkeypatch.setattr(transport, "RUN_DIR", tmp_path / "output" / transport.RUN_NAME)
    return transport.NativeOps(approved=True)


def test_approval_platform_and_exclusive_directory(tmp_path, monkeypatch):
    with pytest.raises(ValueError, match="approval"):
        transport.NativeOps()
    monkeypatch.setattr(transport.sys, "platform", "linux")
    with pytest.raises(ValueError, match="Windows"):
        transport.NativeOps(approved=True)
    ops = make_ops(tmp_path, monkeypatch)
    assert ops.directory.is_dir()
    with pytest.raises(FileExistsError):
        transport.NativeOps(approved=True)
    with pytest.raises(ValueError, match="watchdog"):
        ops.stop_service(5)


def test_collection_fixed_guest_timeout_and_existing_partial_preserved(
    tmp_path, monkeypatch
):
    ops = make_ops(tmp_path, monkeypatch)
    calls = []

    def command(args, timeout, **kwargs):
        calls.append(args)
        (ops.directory / "before.json").write_bytes(b'{"partial":true}')
        raise TimeoutError("simulated client timeout")

    monkeypatch.setattr(transport, "command", command)
    with pytest.raises(TimeoutError):
        ops.collect("before", 5)
    assert calls[0][:4] == [
        "/usr/bin/timeout",
        "--signal=INT",
        "--kill-after=0.5s",
        "4.000000s",
    ]
    saved = (ops.directory / "before.json").read_bytes()
    with pytest.raises(FileExistsError):
        ops.collect("before", 5)
    assert (ops.directory / "before.json").read_bytes() == saved
    with pytest.raises(ValueError):
        ops.collect("wrong", 5)


@pytest.mark.parametrize("cancel", ["none", "valid", "wrong", "malformed"])
def test_worker_deadline_cancel_and_invalid_cancel_never_defeats_restore(
    tmp_path, monkeypatch, cancel
):
    monkeypatch.setattr(worker.sys, "platform", "win32")
    monkeypatch.setattr(transport, "RUN_DIR", tmp_path)
    now = [time.monotonic_ns()]
    value = request(tmp_path, mode="restore", seconds=0.1)
    calls = []
    monkeypatch.setattr(
        transport, "start_service", lambda timeout: calls.append("start")
    )
    monkeypatch.setattr(
        transport,
        "service_state",
        lambda timeout: dict(active="active", sub="running", unit="enabled"),
    )
    if cancel != "none":
        data = dict(nonce=value["nonce"] if cancel == "valid" else "b" * 64)
        if cancel == "malformed":
            (tmp_path / "watchdog-cancel.json").write_bytes(b"{bad}")
        else:
            transport.save_exclusive(tmp_path / "watchdog-cancel.json", data)
        (tmp_path / "watchdog-cancel.signal").touch()
    assert (
        worker.watch(
            tmp_path,
            clock=lambda: now[0],
            sleep=lambda seconds: now.__setitem__(0, now[0] + 200_000_000),
        )
        == 0
    )
    outcome = transport.read_json(tmp_path / "watchdog-outcome.json")
    assert outcome["status"] == (
        "disarmed" if cancel == "valid" else "restored_at_deadline"
    )
    assert calls == ([] if cancel == "valid" else ["start"])


def test_worker_interrupt_attempts_restoration_and_failed_restore_retained(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(worker.sys, "platform", "win32")
    monkeypatch.setattr(transport, "RUN_DIR", tmp_path)
    request(tmp_path, "restore")
    calls = []

    def start(timeout):
        calls.append("start")
        raise ValueError("private sentinel")

    def interrupted(seconds):
        raise KeyboardInterrupt()

    monkeypatch.setattr(transport, "start_service", start)
    assert worker.watch(tmp_path, sleep=interrupted) == 1
    raw = (tmp_path / "watchdog-outcome.json").read_bytes()
    assert calls == ["start"] and b"private sentinel" not in raw
    assert json.loads(raw)["trigger_error_type"] == "KeyboardInterrupt"


@pytest.mark.parametrize("mode", ["wrong_mode", "sources", "deadline", "approval"])
def test_request_refusals_before_ready(tmp_path, mode):
    value = request(tmp_path)
    if mode == "wrong_mode":
        value["mode"] = "restore"
    elif mode == "sources":
        value["sources"] = {}
    elif mode == "deadline":
        value["deadline_ns"] = True
    else:
        value["approved"] = 1
    (tmp_path / "watchdog-request.json").write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError):
        worker.watch(tmp_path, inert=True)
    assert not (tmp_path / "watchdog-ready.signal").exists()


def test_batch_cli_without_flag_never_constructs_backend(monkeypatch):
    monkeypatch.setattr(batch.sys, "argv", ["batch"])
    monkeypatch.setattr(
        transport,
        "NativeOps",
        lambda **kwargs: pytest.fail("backend constructed without flag"),
    )
    with pytest.raises(SystemExit) as error:
        batch.main()
    assert error.value.code == 2


def wait_file(path, seconds=5):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if path.exists():
            return
        time.sleep(0.02)
    pytest.fail("inert helper did not produce expected marker")


def test_real_inert_helper_after_parent_is_killed(tmp_path):
    # Real process lifecycle; the child is explicitly inert, never a service test.
    request(tmp_path, seconds=3)
    script = Path(worker.__file__).resolve()
    code = (
        "import subprocess,sys,time;"
        "p=subprocess.Popen([sys.executable,sys.argv[1],'--directory',sys.argv[2],'--inert'],"
        "stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,"
        "close_fds=True,creationflags=int(sys.argv[3]));"
        "print(p.pid,flush=True);time.sleep(20)"
    )
    parent = subprocess.Popen(
        [
            transport.helper_python(),
            "-c",
            code,
            str(script),
            str(tmp_path),
            str(transport.helper_flags()),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=transport.HIDDEN if sys.platform == "win32" else 0,
    )
    try:
        pid_line = parent.stdout.readline().decode().strip()
        if not pid_line:
            _, error = parent.communicate(timeout=3)
            pytest.fail(
                f"inert parent failed before helper PID: exit={parent.returncode}; "
                f"stderr={error[:4096].decode(errors='replace')}"
            )
        pid = int(pid_line)
        wait_file(tmp_path / "watchdog-ready.signal")
        parent.kill()
        parent.wait(timeout=3)
        wait_file(tmp_path / "watchdog-outcome.json")
        outcome = transport.read_json(tmp_path / "watchdog-outcome.json")
        assert outcome == dict(
            mode="inert", nonce="a" * 64, pid=pid, status="inert_elapsed"
        )
    finally:
        if parent.poll() is None:
            parent.kill()
            parent.wait(timeout=3)
        parent.stdout.close()
        parent.stderr.close()


def test_native_handshake_fixed_flags_and_verified_disarm(tmp_path, monkeypatch):
    ops = make_ops(tmp_path, monkeypatch)
    monkeypatch.setattr(transport, "helper_python", lambda: "direct-python.exe")
    calls = []

    class Process:
        pid = 1234
        returncode = None

        def poll(self):
            return self.returncode

        def wait(self, timeout):
            self.returncode = 0
            transport.save_exclusive(
                ops.directory / "watchdog-outcome.json",
                dict(
                    mode="restore",
                    nonce=ops.nonce,
                    status="disarmed",
                    pid=self.pid,
                ),
            )

    process = Process()

    def spawn(args, **kwargs):
        calls.append((args, kwargs))
        transport.save_exclusive(
            ops.directory / "watchdog-ready.json",
            dict(
                mode="restore",
                nonce=ops.nonce,
                pid=process.pid,
                deadline_ns=ops.deadline_ns,
            ),
        )
        (ops.directory / "watchdog-ready.signal").touch()
        return process

    monkeypatch.setattr(transport.subprocess, "Popen", spawn)
    assert ops.arm_restore_watchdog(60, 5)["armed"] is True and ops.armed
    args, flags = calls[0]
    assert args[0] == "direct-python.exe"
    assert (
        flags["creationflags"]
        == transport.HIDDEN | transport.BREAKAWAY | transport.NEW_GROUP
    )
    assert flags["shell"] is False and flags["close_fds"] is True
    native = []
    monkeypatch.setattr(
        transport,
        "command",
        lambda args, timeout, **kwargs: native.append((args, kwargs)),
    )
    ops.stop_service(5)
    assert native == [
        (["/usr/bin/systemctl", "stop", "systemd-timesyncd"], dict(root=True))
    ]
    monkeypatch.setattr(
        transport,
        "service_state",
        lambda timeout: dict(active="active", sub="running", unit="enabled"),
    )
    assert ops.disarm_restore_watchdog(5) is True and not ops.armed


def test_unacknowledged_alive_process_cannot_stop_service(tmp_path, monkeypatch):
    ops = make_ops(tmp_path, monkeypatch)
    ops.process = SimpleNamespace(poll=lambda: None)
    ops.deadline_ns = time.monotonic_ns() + 60_000_000_000
    with pytest.raises(ValueError, match="watchdog"):
        ops.stop_service(5)


def test_collect_bounded_complete_file_without_native_action(tmp_path, monkeypatch):
    ops = make_ops(tmp_path, monkeypatch)

    def collect(args, timeout, **kwargs):
        assert args[-1].startswith(transport.GUEST_ROOT + "/output/")
        (ops.directory / "before.json").write_bytes(b"{}")

    monkeypatch.setattr(transport, "command", collect)
    assert ops.collect("before", 5) == b"{}"


def test_preflight_refuses_known_sensor_without_root_commands(tmp_path, monkeypatch):
    ops = make_ops(tmp_path, monkeypatch)
    monkeypatch.setattr(
        transport,
        "service_state",
        lambda timeout: dict(active="active", sub="running", unit="enabled"),
    )

    def command(args, timeout, **kwargs):
        assert not kwargs.get("root")
        return "sensor-id" if args[0] == "docker" else "passed"

    monkeypatch.setattr(transport, "command", command)
    with pytest.raises(ValueError, match="sensor"):
        ops.preflight(5)


def test_real_inert_cancel_never_has_restoration_mode(tmp_path):
    value = request(tmp_path, seconds=3)
    process = subprocess.Popen(
        [
            transport.helper_python(),
            str(Path(worker.__file__).resolve()),
            "--directory",
            str(tmp_path),
            "--inert",
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
        creationflags=transport.helper_flags(),
    )
    try:
        wait_file(tmp_path / "watchdog-ready.signal")
        transport.save_exclusive(
            tmp_path / "watchdog-cancel.json", dict(nonce=value["nonce"])
        )
        (tmp_path / "watchdog-cancel.signal").touch()
        assert process.wait(timeout=5) == 0
        assert (
            transport.read_json(tmp_path / "watchdog-outcome.json")["status"]
            == "inert_disarmed"
        )
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=3)


@pytest.mark.parametrize("delivery", ["pending", "wrong", "malformed", "orphan", "ack"])
def test_worker_cancel_requires_unambiguous_stop_ack(tmp_path, monkeypatch, delivery):
    monkeypatch.setattr(worker.sys, "platform", "win32")
    monkeypatch.setattr(transport, "RUN_DIR", tmp_path)
    now = [time.monotonic_ns()]
    value = request(tmp_path, mode="restore", seconds=0.1)
    if delivery != "orphan":
        transport.save_exclusive(
            tmp_path / "stop-dispatch.json", dict(nonce=value["nonce"])
        )
    if delivery != "pending":
        if delivery == "malformed":
            (tmp_path / "stop-ack.json").write_bytes(b"{broken")
        else:
            transport.save_exclusive(
                tmp_path / "stop-ack.json",
                dict(nonce=value["nonce"] if delivery == "ack" else "b" * 64),
            )
    transport.save_exclusive(
        tmp_path / "watchdog-cancel.json", dict(nonce=value["nonce"])
    )
    (tmp_path / "watchdog-cancel.signal").touch()
    calls = []
    monkeypatch.setattr(
        transport, "start_service", lambda timeout: calls.append("start")
    )
    monkeypatch.setattr(
        transport,
        "service_state",
        lambda timeout: dict(active="active", sub="running", unit="enabled"),
    )
    result = worker.watch(
        tmp_path,
        clock=lambda: now[0],
        sleep=lambda seconds: now.__setitem__(0, now[0] + 200_000_000),
    )
    outcome = transport.read_json(tmp_path / "watchdog-outcome.json")
    if delivery == "ack":
        assert result == 0 and outcome["status"] == "disarmed" and calls == []
    else:
        assert result == 1 and calls == ["start"]
        assert outcome["status"] == "active_observed_delivery_uncertain"
        assert outcome["operator_recovery_required"] is True


def armed_ops(tmp_path, monkeypatch):
    ops = make_ops(tmp_path, monkeypatch)
    ops.process = SimpleNamespace(poll=lambda: None)
    ops.armed = True
    ops.deadline_ns = time.monotonic_ns() + 60_000_000_000
    return ops


@pytest.mark.parametrize("error", [TimeoutError, ValueError, KeyboardInterrupt])
def test_failed_stop_retains_dispatch_and_refuses_cancel_before_state_read(
    tmp_path, monkeypatch, error
):
    ops = armed_ops(tmp_path, monkeypatch)

    def delayed(args, timeout, **kwargs):
        assert transport.read_json(ops.directory / "stop-dispatch.json") == dict(
            nonce=ops.nonce
        )
        raise error("private sentinel")

    monkeypatch.setattr(transport, "command", delayed)
    with pytest.raises(error):
        ops.stop_service(5)
    assert ops.stop_uncertain and not (ops.directory / "stop-ack.json").exists()
    with pytest.raises(ValueError, match="uncertain"):
        ops.disarm_restore_watchdog(5)
    assert not (ops.directory / "watchdog-cancel.signal").exists()


def test_stop_ack_write_failure_preserves_uncertainty(tmp_path, monkeypatch):
    ops = armed_ops(tmp_path, monkeypatch)
    calls = []
    monkeypatch.setattr(transport, "command", lambda *a, **k: calls.append("stop"))
    original = transport.save_exclusive

    def write(path, value):
        if path.name == "stop-ack.json":
            raise OSError("private filesystem error")
        original(path, value)

    monkeypatch.setattr(transport, "save_exclusive", write)
    with pytest.raises(OSError):
        ops.stop_service(5)
    assert calls == ["stop"] and ops.stop_uncertain
    with pytest.raises(ValueError, match="uncertain"):
        ops.disarm_restore_watchdog(5)


def test_dispatch_file_failure_never_sends_stop(tmp_path, monkeypatch):
    ops = armed_ops(tmp_path, monkeypatch)
    transport.save_exclusive(
        ops.directory / "stop-dispatch.json", dict(nonce=ops.nonce)
    )
    with pytest.raises(FileExistsError):
        ops.stop_service(5)
    assert ops.stop_uncertain and not (ops.directory / "stop-ack.json").exists()


def test_shared_pending_marker_refuses_cancel_even_if_local_flag_lost(
    tmp_path, monkeypatch
):
    ops = armed_ops(tmp_path, monkeypatch)
    transport.save_exclusive(
        ops.directory / "stop-dispatch.json", dict(nonce=ops.nonce)
    )
    assert ops.stop_uncertain is False
    with pytest.raises(ValueError, match="uncertain"):
        ops.disarm_restore_watchdog(5)
    assert not (ops.directory / "watchdog-cancel.json").exists()
