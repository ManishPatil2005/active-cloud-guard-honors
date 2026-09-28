"""Save a minimized metrics report from one existing successful trial."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.sensor_adapter import IMAGE
from cloudguard.sensor_metrics import summarize
from cloudguard.verification import read_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("metrics", "trial", "output"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    if Path(args.output).exists():
        raise FileExistsError("choose a new output path")
    trial, digest = read_json(args.trial)
    if not isinstance(trial, dict) or not (
        trial.get("status") == "events_observed"
        and trial.get("image") == IMAGE
        and trial.get("target_identity_stable") is True
        and trial.get("sensor_removed") is True
    ):
        raise ValueError("successful instrumented trial required")
    report = summarize(args.metrics, trial.get("metrics_raw_sha256"))
    report["trial_sha256"] = digest
    with Path(args.output).open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
