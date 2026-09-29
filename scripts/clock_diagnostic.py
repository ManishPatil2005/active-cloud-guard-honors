"""Six predefined four-second clock checks; no sensor, network or clock adjustment."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.clock_check import sample, compare


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    with Path(args.output).open("x", encoding="utf-8") as stream:
        report = dict(
            executed_at=datetime.now(timezone.utc).isoformat(),
            samples=[],
            clock_settings_modified=False,
            historical_cause_resolved=False,
        )
        try:
            for _ in range(6):
                first = sample()
                time.sleep(4)
                last = sample()
                report["samples"].append(
                    dict(first=first, last=last, **compare(first, last))
                )
            report["status"] = (
                "checks_passed"
                if all(s["within_tolerance"] for s in report["samples"])
                else "timing_rejected"
            )
        finally:
            json.dump(report, stream, indent=2)
            stream.write("\n")
    print(json.dumps(report))
    if report["status"] != "checks_passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
