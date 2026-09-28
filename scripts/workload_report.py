"""Select a declared measured interval from a strict normalized saved trial."""

import argparse
from collections import Counter
from datetime import datetime
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.sensor_adapter import normalize
from cloudguard.verification import read_json


def report(raw, trial_path, inventory):
    trial, digest = read_json(trial_path)
    interval = trial.get("measurement", {})
    start, end = interval.get("start_unix_ns"), interval.get("end_unix_ns")
    if (
        interval.get("status") != "completed"
        or type(start) is not int
        or type(end) is not int
        or not 0 <= start < end
        or trial.get("target_identity_stable") is not True
    ):
        raise ValueError("completed measured interval and stable identity required")
    bundle = normalize(
        raw,
        trial_path,
        inventory,
        asset_id="compose/redis",
        capture_id="interval-" + digest,
        scenario_group="redis-ping-development",
    )
    if bundle["capture"] is None:
        raise ValueError("raw normalization rejected")
    counts = Counter()
    outside = 0
    for event in bundle["capture"]["events"]:
        seconds, fraction = event["timestamp"].split(".")
        ns = int(datetime.fromisoformat(seconds + "+00:00").timestamp()) * 10**9 + int(
            fraction[:-1]
        )
        if start <= ns < end:
            counts[event["kind"]] += 1
        else:
            outside += 1
    return dict(
        trial_sha256=digest,
        raw_sha256=bundle["accounting"]["raw_sha256"],
        inventory_sha256=bundle["accounting"]["inventory_sha256"],
        measurement=interval,
        interval_semantics="half-open [start,end)",
        measured_event_count=sum(counts.values()),
        measured_kind_counts=dict(counts),
        outside_interval_event_count=outside,
        coverage="partial_or_unknown",
        independent_evaluation=False,
        threat_confirmed=False,
        limits=[
            "Time exclusion is not causal attribution or complete canary exclusion.",
            "Round trip includes Docker exec overhead; no sensor-off comparison exists.",
        ],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("raw", "trial", "inventory", "output"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    if Path(args.output).exists():
        raise FileExistsError("choose a new output path")
    result = report(args.raw, args.trial, args.inventory)
    with Path(args.output).open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
