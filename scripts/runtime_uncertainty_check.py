"""Fixed invented grouped-comparison example; no model or real-data evaluation."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.runtime_uncertainty import grouped_synthetic
from cloudguard.verification import read_json, file_hash


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        with Path(args.output).open("x", encoding="utf-8") as stream:
            try:
                fixture = ROOT / "data/runtime/grouped-uncertainty-synthetic.json"
                sources = [
                    ROOT / "cloudguard" / name
                    for name in (
                        "runtime_uncertainty.py",
                        "runtime_paired_accounting.py",
                        "runtime_accounting.py",
                        "runtime.py",
                        "metrics.py",
                        "verification.py",
                        "limits.py",
                    )
                ] + [Path(__file__)]
                hashes = {p.relative_to(ROOT).as_posix(): file_hash(p) for p in sources}
                document, digest = read_json(fixture)
                result = grouped_synthetic(document)
                if read_json(fixture)[1] != digest or any(
                    file_hash(p) != hashes[p.relative_to(ROOT).as_posix()]
                    for p in sources
                ):
                    raise ValueError(
                        "grouped example inputs or selected source changed"
                    )
                checks = dict(
                    all_units_retained=result["paired"]["matched_unit_count"] == 32,
                    four_whole_families=result["declared_family_sizes"] == [8, 8, 8, 8],
                    fixed_draw_budget=result["performed_draws"] == 2000,
                    complete_draw_denominators=all(
                        v["defined_draws"] + v["undefined_draws"] == 2000
                        for v in result["differences"].values()
                    ),
                    synthetic_only=result["independent_evaluation_verified"] is False
                    and result["real_data_evaluation_authorized"] is False
                    and result["labels_created"] is False,
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
            json.dump(report, stream, indent=2, allow_nan=False)
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
