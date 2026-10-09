"""Fixed synthetic paired example, not model predictions or a benchmark."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.runtime_paired_accounting import compare_synthetic
from cloudguard.verification import read_json, file_hash


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        with Path(args.output).open("x", encoding="utf-8") as stream:
            try:
                fixture = ROOT / "data/runtime/paired-accounting-synthetic.json"
                sources = [
                    ROOT / "cloudguard" / name
                    for name in (
                        "runtime_paired_accounting.py",
                        "runtime_accounting.py",
                        "metrics.py",
                        "runtime.py",
                    )
                ]
                hashes = {p.name: file_hash(p) for p in [*sources, Path(__file__)]}
                document, digest = read_json(fixture)
                result = compare_synthetic(document)
                if read_json(fixture)[1] != digest or any(
                    file_hash(p) != hashes[p.name] for p in [*sources, Path(__file__)]
                ):
                    raise ValueError(
                        "paired accounting inputs or implementation changed"
                    )
                checks = dict(
                    exact_pairing=result["matched_unit_count"] == 4,
                    retained_unavailable=result["baseline"]["availability_counts"]
                    == result["variant"]["availability_counts"]
                    == dict(observed=3, missing=1, unusable=0),
                    abstention_not_hidden=result["negative_abstention_change"] == 1
                    and result["variant_minus_baseline"]["known_decision_coverage"] < 0,
                    fp_count_not_rate=result["fp_count_reduction"] == 1
                    and result["variant"]["conditional_metrics"]["false_positive_rate"]
                    is None,
                    unknown_not_confusion=result["variant"]["conditional_confusion"]
                    == dict(tp=1, fp=0, tn=0, fn=0),
                    no_evaluation_authority=result["real_data_evaluation_authorized"]
                    is False
                    and result["model_predictions_generated"] is False
                    and result["actions_executed"] == [],
                )
                code = 0 if all(checks.values()) else 1
                report = dict(
                    status="synthetic_check_passed"
                    if code == 0
                    else "synthetic_check_failed",
                    executed_at=datetime.now(timezone.utc).isoformat(),
                    input_file_sha256=digest,
                    selected_implementation_sha256=hashes,
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
