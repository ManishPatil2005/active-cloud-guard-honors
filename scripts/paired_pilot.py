"""One predeclared OFF/ON/ON/OFF pilot; caller manages approved NTP stop/restore."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.deployment import local_daemon
from scripts.sensor_trial import command, target_identity
from scripts.workload_control import check_sensor_absent


def preflight():
    local_daemon()
    check_sensor_absent()
    ids = command(
        "ps",
        "--no-trunc",
        "-q",
        "--filter",
        "label=com.docker.compose.project=honors-cloud-guard",
        "--filter",
        "label=com.docker.compose.service=redis",
    ).splitlines()
    if len(ids) != 1:
        raise ValueError("one running Redis required before changing any service")
    target_identity(ids[0])


def inactive():
    result = subprocess.run(
        ["systemctl", "is-active", "systemd-timesyncd"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.stdout.strip() != "inactive" or result.returncode != 3:
        raise ValueError("guest NTP must remain inactive for this approved pilot")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir")
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    preflight()
    if args.preflight_only:
        print("Docker, known-sensor absence and Redis identity preflight passed")
        return
    if not args.output_dir:
        parser.error("--output-dir is required for the pilot")
    destination = Path(args.output_dir).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    receipt = dict(
        executed_at=datetime.now(timezone.utc).isoformat(),
        protocol="off_on_on_off_ping4_v1",
        sequence=[],
        status="started",
        source_sha256={
            p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
            for p in [
                "scripts/paired_pilot.py",
                "scripts/sensor_trial.py",
                "scripts/workload_control.py",
                "cloudguard/workload.py",
                "cloudguard/clock_check.py",
            ]
        },
    )
    try:
        jobs = [
            ("clock", "clock_diagnostic.py", []),
            (
                "off-1",
                "workload_control.py",
                ["--clock-report", str(destination / "clock.json")],
            ),
            ("on-1", "sensor_trial.py", ["--fixed-warmup"]),
            ("on-2", "sensor_trial.py", ["--fixed-warmup"]),
            (
                "off-2",
                "workload_control.py",
                ["--clock-report", str(destination / "clock.json")],
            ),
        ]
        for name, script, extra in jobs:
            inactive()
            command = [
                sys.executable,
                str(ROOT / "scripts" / script),
                "--output",
                str(destination / (name + ".json")),
                *extra,
            ]
            if name != "clock":
                command += ["--profile", "ping_4"]
            result = subprocess.run(
                command, cwd=ROOT, capture_output=True, text=True, timeout=55
            )
            receipt["sequence"].append(dict(name=name, exit_code=result.returncode))
            print(name + " exit=" + str(result.returncode), flush=True)
            if result.returncode != 0:
                raise ValueError("pilot stopped at failed planned run; no retries")
        inactive()
        receipt["status"] = "completed"
    except Exception as error:
        receipt.update(status="failed", error_type=type(error).__name__)
        raise
    finally:
        with (destination / "manifest.json").open("x", encoding="utf-8") as stream:
            json.dump(receipt, stream, indent=2)
            stream.write("\n")


if __name__ == "__main__":
    main()
