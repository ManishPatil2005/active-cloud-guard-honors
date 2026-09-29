"""Sensor-off development control, not an overhead estimate or sensor export."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.sensor_trial import IMAGE, command, target_identity
from cloudguard.deployment import local_daemon
from cloudguard.workload import PROFILES, run
from cloudguard.verification import read_json


def check_sensor_absent():
    if command("ps", "-q", "--filter", "name=acg-falco-") or command(
        "ps", "-q", "--filter", "ancestor=" + IMAGE
    ):
        raise ValueError("known trial sensor is running; control refused")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=tuple(PROFILES), required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--clock-report", required=True)
    args = parser.parse_args()
    with Path(args.output).open("x", encoding="utf-8") as stream:
        report = dict(
            executed_at=datetime.now(timezone.utc).isoformat(),
            mode="sensor_off_control",
            sensor_started=False,
            overhead_estimate=None,
            absence_scope="known trial name/image at endpoints only; not all host collectors",
        )
        try:
            report["phase"] = "clock_gate"
            diagnostic, diagnostic_hash = read_json(args.clock_report)
            if (
                not isinstance(diagnostic, dict)
                or diagnostic.get("status") != "checks_passed"
            ):
                raise ValueError("passing clock diagnostic required before control")
            report["clock_diagnostic_sha256"] = diagnostic_hash
            report["phase"] = "docker_prerequisites"
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
                raise ValueError("one running Redis required")
            container = ids[0]
            report["phase"] = "target_identity_before"
            report["identity_before"] = target_identity(container)
            report["warmup_protocol"] = "two_pings_v1"
            report["phase"] = "warmup"
            time.sleep(1)
            # Same command/sleep schedule as sensor --fixed-warmup; sensor log
            # inspection still adds processing time and must be acknowledged.
            for _ in range(2):
                if (
                    command("exec", container, "redis-cli", "-h", "127.0.0.1", "PING")
                    != "PONG"
                ):
                    raise ValueError("warmup failed")
                time.sleep(1)
            report["warmup_pings"] = 2
            time.sleep(1)
            report["phase"] = "measurement"
            report["measurement"] = run(
                args.profile,
                lambda: command(
                    "exec", container, "redis-cli", "-h", "127.0.0.1", "PING"
                ),
            )
            report["phase"] = "post_checks"
            report["identity_after"] = target_identity(container)
            check_sensor_absent()
            report["identity_stable"] = (
                report["identity_before"] == report["identity_after"]
            )
            report["status"] = (
                "completed"
                if report["identity_stable"]
                and report["measurement"]["status"] == "completed"
                else "rejected"
            )
            report["phase"] = "finished"
        except Exception as error:
            report.update(status="failed", error_type=type(error).__name__)
            raise
        finally:
            json.dump(report, stream, indent=2)
            stream.write("\n")
    print(json.dumps(report))
    if report["status"] != "completed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
