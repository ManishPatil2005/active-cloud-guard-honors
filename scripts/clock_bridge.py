"""Six read-only Redis TIME brackets; not Falco calibration or clock correction."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.clock_check import sample, compare
from cloudguard.deployment import local_daemon
from scripts.sensor_trial import command, target_identity
from scripts.workload_control import check_sensor_absent


def bracket(first, last, reply):
    timing = compare(first, last)
    if not timing["within_tolerance"] or timing["elapsed_monotonic_ns"] > 500_000_000:
        raise ValueError("unstable or excessively wide clock bracket")
    parts = reply.splitlines()
    if len(parts) != 2 or any(not re.fullmatch(r"[0-9]{1,10}", p) for p in parts):
        raise ValueError("unexpected Redis TIME response")
    seconds, micros = map(int, parts)
    if not 0 <= seconds < 4133980800 or not 0 <= micros < 1_000_000:
        raise ValueError("Redis TIME outside supported range")
    remote = seconds * 10**9 + micros * 1000
    # Bounds include read-bracket uncertainty, observed endpoint drift, and
    # microsecond timestamp quantization. Network/exec latency is NOT halved.
    allowance = timing["sampling_uncertainty_ns"] + abs(timing["clock_difference_ns"])
    low = remote - last["wall_ns"] - allowance
    high = remote + 999 - first["wall_ns"] + allowance
    return dict(
        first=first,
        last=last,
        **timing,
        redis_unix_ns=remote,
        offset_lower_ns=low,
        offset_upper_ns=high,
        zero_within_bounds=low <= 0 <= high,
    )


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
