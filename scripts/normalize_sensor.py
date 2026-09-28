"""Normalize a saved bounded trial offline into a new local output directory."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.sensor_adapter import normalize


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in (
        "raw",
        "trial",
        "inventory",
        "asset-id",
        "capture-id",
        "scenario-group",
        "output-dir",
    ):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    destination = Path(args.output_dir)
    if destination.exists():
        raise FileExistsError("choose a new output directory")
    bundle = normalize(
        args.raw,
        args.trial,
        args.inventory,
        asset_id=args.asset_id,
        capture_id=args.capture_id,
        scenario_group=args.scenario_group,
    )
    destination.mkdir(parents=True, exist_ok=False)
    for name, value in bundle.items():
        if value is not None:
            with (destination / (name + ".json")).open("x", encoding="utf-8") as stream:
                json.dump(value, stream, indent=2)
                stream.write("\n")
    print(json.dumps(bundle["accounting"]))
    if bundle["capture"] is None:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
