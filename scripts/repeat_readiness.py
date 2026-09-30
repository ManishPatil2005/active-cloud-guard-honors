"""Three fixed engineering trials, abort on failure, no replacement runs."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.paired_pilot import preflight
from scripts.paired_report import checked_measurement
from cloudguard.verification import read_json

SOURCES = [
    "scripts/sensor_trial.py",
    "cloudguard/correlation.py",
    "cloudguard/workload.py",
    "cloudguard/clock_check.py",
    "testbed/falco-trial.yaml",
    "scripts/repeat_readiness.py",
]


def hashes():
    return {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCES
    }


def accept(run, identity=None):
    if (
        run.get("status") != "events_observed"
        or run.get("sensor_removed") is not True
        or run.get("target_identity_stable") is not True
        or run.get("target_identity_before") != run.get("target_identity_after")
        or not run.get("target_identity_before")
        or run.get("readiness_protocol") != "identified_second_canary_v1"
        or run.get("readiness", {}).get("status") != "identified_canary_observed"
        or run.get("diagnostic_protocol") != "container_pid_connect_v2"
    ):
        raise ValueError("trial acceptance failed")
    if identity is not None and run["target_identity_before"] != identity:
        raise ValueError("target changed across repeats")
    m = run.get("measurement", {})
    if (
        m.get("status") != "completed"
        or m.get("profile") != "ping_4"
        or len(m.get("calls", [])) != 4
        or any(c.get("pong") is not True for c in m["calls"])
    ):
        raise ValueError("measured workload rejected")
    if checked_measurement(m) != "per_call_brackets_v1":
        raise ValueError("per-call timing required")
    attempts = run.get("readiness_attempts", [])
    warmup = run.get("warmup_process_ids", [])
    measured = run.get("correlation_process_ids", [])
    if (
        len(attempts) != 2
        or len(warmup) != 2
        or len(measured) != 4
        or len(set(warmup + measured)) != 6
    ):
        raise ValueError("invalid tracked identities")
    if (
        any(
            a.get("process_id") != pid or a.get("attempt") != i + 1
            for i, (a, pid) in enumerate(zip(attempts, warmup))
        )
        or type(attempts[-1].get("connect_count")) is not int
        or attempts[-1]["connect_count"] != 1
    ):
        raise ValueError("identified readiness not established")
    c = run.get("correlation", {})
    rows = c.get("matches", [])
    if (
        len(rows) != 4
        or [r.get("process_id") for r in rows] != measured
        or any(
            r.get("zero_within_bounds") is not True
            or not r.get("offset_lower_ns", 1) <= 0 <= r.get("offset_upper_ns", -1)
            for r in rows
        )
    ):
        raise ValueError("measured timestamp mismatch")
    return run["target_identity_before"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    # Resolve once before experiments; never consult a transient WSL cwd mid-batch.
    destination = (ROOT / Path(args.output_dir)).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    manifest = dict(
        executed_at=datetime.now(timezone.utc).isoformat(),
        protocol="three_readiness_trials_v1",
        planned_trials=3,
        trials=[],
        status="started",
        source_sha256=hashes(),
        independent_evaluation=False,
    )
    identity = None
    try:
        for number in range(1, 4):
            manifest["phase"] = f"preflight_{number}"
            preflight()
            if hashes() != manifest["source_sha256"]:
                raise ValueError("frozen sources changed")
            path = destination / f"trial-{number}.json"
            entry = dict(trial=number, status="started", child_started=False)
            manifest["trials"].append(entry)
            manifest["phase"] = f"trial_{number}"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/sensor_trial.py"),
                    "--profile",
                    "ping_4",
                    "--fixed-warmup",
                    "--correlate",
                    "--output",
                    str(path),
                ],
                cwd=ROOT,
                capture_output=True,
                timeout=60,
            )
            entry["child_started"] = True
            entry["exit_code"] = result.returncode
            if path.exists():
                run, digest = read_json(path)
                entry["receipt_sha256"] = digest
            if result.returncode != 0:
                entry["status"] = "failed"
                raise ValueError("trial failed; no replacements")
            identity = accept(run, identity)
            preflight()
            entry["status"] = "accepted"
            entry["all_six_commands_uniquely_observed"] = run["correlation"][
                "all_six_commands_uniquely_observed"
            ]
            print(f"trial-{number} accepted", flush=True)
        if hashes() != manifest["source_sha256"]:
            raise ValueError("frozen sources changed")
        manifest["status"] = "completed"
    except Exception as error:
        if isinstance(error, subprocess.TimeoutExpired) and manifest["trials"]:
            manifest["trials"][-1]["child_started"] = True
        manifest.update(status="failed", error_type=type(error).__name__)
        if manifest["trials"] and manifest["trials"][-1]["status"] == "started":
            manifest["trials"][-1]["status"] = "failed"
        raise
    finally:
        manifest["not_run_trials"] = 3 - sum(
            t["child_started"] for t in manifest["trials"]
        )
        with (destination / "manifest.json").open("x", encoding="utf-8") as stream:
            json.dump(manifest, stream, indent=2)
            stream.write("\n")


if __name__ == "__main__":
    main()
