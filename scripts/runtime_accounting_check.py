"""Fixed invented accounting example, not predictions from Engine 2."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.runtime_accounting import summarize_synthetic
from cloudguard.verification import read_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        with Path(args.output).open("x", encoding="utf-8") as stream:
            try:
                path = ROOT / "data/runtime/accounting-synthetic.json"
                document, digest = read_json(path)
                result = summarize_synthetic(document)
                if read_json(path)[1] != digest:
                    raise ValueError("accounting fixture changed")
                checks = dict(
                    declared_units=result["declared_unit_count"] == 11,
                    availability=result["availability_counts"]
                    == dict(observed=9, missing=1, unusable=1),
                    conditional_confusion=result["conditional_confusion"]
                    == dict(tp=1, fp=1, tn=1, fn=1),
                    retained_abstentions=result["positive_abstentions"]
                    == result["negative_abstentions"]
                    == 1,
                    inclusive_positive_denominator=result[
                        "all_known_positive_detection_fraction"
                    ]
                    == 1 / 3,
                    no_evaluation_authority=result["real_data_evaluation_authorized"]
                    is False
                    and result["model_predictions_generated"] is False,
                )
                code = 0 if all(checks.values()) else 1
                report = dict(
                    executed_at=datetime.now(timezone.utc).isoformat(),
                    status="synthetic_check_passed"
                    if code == 0
                    else "synthetic_check_failed",
                    input_file_sha256=digest,
                    implementation_sha256=hashlib.sha256(
                        (ROOT / "cloudguard/runtime_accounting.py").read_bytes()
                    ).hexdigest(),
                    checks=checks,
                    result=result,
                )
            except (Exception, KeyboardInterrupt) as error:
                code = 1
                report = dict(
                    status="rejected",
                    error_type=type(error).__name__,
                    actions_executed=[],
                )
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
