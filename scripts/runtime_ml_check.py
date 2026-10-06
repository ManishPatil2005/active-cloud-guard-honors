"""Fixed synthetic Isolation Forest smoke check; no real evaluation or actions."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.runtime_ml import compare_synthetic


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        with Path(args.output).open("x", encoding="utf-8") as stream:
            try:
                result = compare_synthetic(
                    [ROOT / "data/runtime/ml-baseline-synthetic.json"],
                    ROOT / "data/runtime/ml-observation-synthetic.json",
                    ROOT / "testbed/inventory.json",
                )
                checks = dict(
                    three_observed_units=len(result["windows"]) == 3,
                    synthetic_fit=result["synthetic_fitting_performed"] is True,
                    finite_scores=all(
                        row["isolation_score"] is not None
                        and 0 <= row["isolation_score"] <= 1
                        for row in result["windows"]
                    ),
                    no_binary_predictions=all(
                        row["binary_prediction"] is None for row in result["windows"]
                    ),
                    no_real_authority=result["real_data_fitting_authorized"] is False
                    and result["independent_evaluation_verified"] is False
                    and result["threat_confirmed"] is False,
                    no_actions=result["actions_executed"] == [],
                )
                if not all(checks.values()):
                    raise ValueError("synthetic ML software acceptance failed")
                report = dict(
                    executed_at=datetime.now(timezone.utc).isoformat(),
                    evidence_level="synthetic_software_only",
                    result=result,
                    checks=checks,
                )
                code = 0
            except (Exception, KeyboardInterrupt) as error:
                report = dict(
                    status="rejected",
                    error_type=type(error).__name__,
                    evidence_level="synthetic_software_only",
                    real_data_fitting_authorized=False,
                    actions_executed=[],
                )
                code = 1
            json.dump(report, stream, indent=2)
            stream.write("\n")
        print(
            json.dumps(
                dict(status="synthetic_check_passed" if code == 0 else "rejected")
            )
        )
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
