"""Approval-gated one-batch guest-client comparison; never run without human consent."""

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard import clock_comparison as control
from scripts import (
    clock_comparison_transport as transport,
    clock_comparison_review as review,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-approved",
        action="store_true",
        help="Operator must first obtain explicit human approval",
    )
    args = parser.parse_args()
    if not args.run_approved:
        parser.error("specific human intervention approval and --run-approved required")
    ops = transport.NativeOps(approved=True)
    manifest = dict(
        executed_at=datetime.now(timezone.utc).isoformat(), status="started"
    )
    with (ops.directory / "manifest.json").open("x", encoding="utf-8") as stream:
        try:
            manifest.update(
                control.run_comparison(ops, review.verify_receipt, approved=True)
            )
        except (Exception, KeyboardInterrupt) as error:
            manifest.update(status="failed", error_type=type(error).__name__)
        finally:
            transport.json.dump(manifest, stream, indent=2)
            stream.write("\n")
    print(manifest["status"])
    return 0 if manifest["status"] == "complete" else 1


if __name__ == "__main__":
    sys.exit(main())
