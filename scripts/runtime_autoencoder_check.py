"""Fixed synthetic reconstruction check, never a real threat benchmark."""

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.runtime_autoencoder import compare_synthetic


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-iter", type=int, default=500)
    args = parser.parse_args()
    try:
        with Path(args.output).open("x", encoding="utf-8") as stream:
            try:
                result = compare_synthetic(
                    [ROOT / "data/runtime/ml-baseline-synthetic.json"],
                    ROOT / "data/runtime/ml-observation-synthetic.json",
                    ROOT / "testbed/inventory.json",
                    max_iter=args.max_iter,
                )
                checks = dict(
                    three_units=len(result["windows"]) == 3,
                    synthetic_training=result["synthetic_fitting_performed"] is True,
                    valid_scores=all(
                        row["reconstruction_error"] is not None
                        and math.isfinite(row["reconstruction_error"])
                        and row["reconstruction_error"] >= 0
                        for row in result["windows"]
                    ),
                    denominators=result["scored_window_count"]
                    + result["abstained_window_count"]
                    == 3,
                    no_binary_predictions=all(
                        row["binary_prediction"] is None for row in result["windows"]
                    ),
                    no_real_authority=result["real_data_fitting_authorized"] is False
                    and result["independent_evaluation_verified"] is False
                    and result["actions_executed"] == [],
                )
                code = 0 if all(checks.values()) else 1
                report = dict(
                    executed_at=datetime.now(timezone.utc).isoformat(),
                    evidence_level="synthetic_software_only",
                    result=result,
                    checks=checks,
                    status="synthetic_check_passed"
                    if code == 0
                    else "synthetic_check_failed",
                )
            except (Exception, KeyboardInterrupt) as error:
                report = dict(
                    status="rejected",
                    error_type=type(error).__name__,
                    evidence_level="synthetic_software_only",
                    actions_executed=[],
                )
                code = 1
            json.dump(report, stream, indent=2)
            stream.write("\n")
        print(json.dumps(dict(status=report["status"])))
        return code
    except (Exception, KeyboardInterrupt) as error:
        print(
            json.dumps(
                dict(status="output_refused_or_failed", error_type=type(error).__name__)
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
