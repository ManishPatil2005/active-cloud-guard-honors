"""Six read-only Redis TIME brackets; not Falco calibration or clock correction."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.clock_check import sample
from cloudguard.clock_domains import redis_bracket as bracket
from cloudguard.deployment import local_daemon
from scripts.sensor_trial import command, target_identity
from scripts.workload_control import check_sensor_absent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
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
            report["phase"] = "preflight"
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
            report["identity_before"] = target_identity(ids[0])
            report["phase"] = "six_time_reads"
            for _ in range(6):
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
