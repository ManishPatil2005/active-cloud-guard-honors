"""Six read-only Redis TIME brackets; not Falco calibration or clock correction."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.clock_check import sample
from cloudguard.clock_domains import redis_bracket as bracket
from cloudguard.deployment import local_daemon
from scripts.sensor_trial import command, target_identity, read_time
from scripts.workload_control import check_sensor_absent

SOURCES = (
    "scripts/clock_bridge.py",
    "scripts/sensor_trial.py",
    "scripts/workload_control.py",
    "cloudguard/clock_domains.py",
    "cloudguard/clock_check.py",
    "cloudguard/deployment.py",
)


def source_hashes():
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in SOURCES}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument("--record-attempts", action="store_true")
    args = parser.parse_args()
    with Path(args.output).open("x", encoding="utf-8") as stream:
        report = dict(
            executed_at=datetime.now(timezone.utc).isoformat(),
            protocol="redis_time_brackets_v1",
            samples=[],
            status="started",
            clock_settings_modified=False,
            sensor_started=False,
            falco_alignment_verified=False,
            correction_applied=False,
        )
        try:
            if args.record_attempts:
                report.update(
                    protocol="redis_time_failure_evidence_v1",
                    time_read_attempts=[],
                    source_sha256=source_hashes(),
                    absence_scope="known trial name/image at endpoints only",
                    planned_reads=6,
                    spacing_seconds=1,
                    independent_evaluation=False,
                )
            report["phase"] = "preflight"
            local_daemon()
            check_sensor_absent()
            if args.record_attempts:
                report["known_sensor_absent_before"] = True
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
            report["identity_before"] = target_identity(ids[0])
            report["phase"] = "six_time_reads"
            for index in range(6):
                if args.record_attempts:
                    report["samples"].append(
                        read_time(
                            ids[0], report["time_read_attempts"], f"time_{index + 1}"
                        )
                    )
                    if index < 5:
                        time.sleep(1)
                    continue
                first = sample()
                reply = command(
                    "exec",
                    ids[0],
                    "redis-cli",
                    "--raw",
                    "-h",
                    "127.0.0.1",
                    "TIME",
                    timeout=5,
                )
                last = sample()
                report["samples"].append(bracket(first, last, reply))
            report["phase"] = "postflight"
            report["identity_after"] = target_identity(ids[0])
            check_sensor_absent()
            if args.record_attempts:
                report["known_sensor_absent_after"] = True
                report["source_sha256_after"] = source_hashes()
                report["sources_unchanged"] = (
                    report["source_sha256"] == report["source_sha256_after"]
                )
                if not report["sources_unchanged"]:
                    raise ValueError("diagnostic sources changed")
            if report["identity_before"] != report["identity_after"]:
                raise ValueError("target identity changed")
            report["status"] = "observed"
            report["zero_excluded_samples"] = sum(
                not s["zero_within_bounds"] for s in report["samples"]
            )
        except Exception as error:
            report.update(status="failed", error_type=type(error).__name__)
            raise
        finally:
            json.dump(report, stream, indent=2)
            stream.write("\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
