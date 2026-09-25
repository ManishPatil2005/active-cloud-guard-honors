"""Save local Engine 2 host facts without installing or starting anything."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.runtime_preflight import collect


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    with Path(args.output).open("x", encoding="utf-8") as stream:
        report = collect()
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(report["status"])
    # Success means a report was saved, not that a sensor is ready.


if __name__ == "__main__":
    main()
