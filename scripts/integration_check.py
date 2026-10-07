"""Save a fixed synthetic integration demonstration without replacing old reports."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.integration import replay
from cloudguard.verification import file_hash


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--engine1-pipeline",
        action="store_true",
        help="Fixed no-model/non-network configuration example using the existing pipeline",
    )
    args = parser.parse_args()
    try:
        with Path(args.output).open("x", encoding="utf-8") as stream:
            try:
                launcher_hash = file_hash(__file__)
                result = replay(
                    ROOT
                    / (
                        "data/integration/redis-auth-only.yaml"
                        if args.engine1_pipeline
                        else "data/development/redis-all.yaml"
                    ),
                    [ROOT / "data/runtime/baseline-synthetic.json"],
                    ROOT / "data/runtime/observation-synthetic.json",
                    ROOT / "testbed/inventory.json",
                    engine1_pipeline=args.engine1_pipeline,
                    kb=ROOT / "knowledge/sources.json"
                    if args.engine1_pipeline
                    else None,
                )
                if file_hash(__file__) != launcher_hash:
                    raise ValueError("integration launcher changed")
                redis = next(
                    a
                    for a in result["asset_contexts"]
                    if a["asset_id"] == "compose/redis"
                )
                checks = dict(
                    static_preserved=result["configuration_finding_count"] == 1
                    and result["engine1"]["findings"][0]["rule_id"]
                    == ("AUTH002" if args.engine1_pipeline else "NET001"),
                    expected_runtime_states=[
                        w["status"] for w in result["engine2"]["windows"]
                    ]
                    == ["no_threshold_exceedance", "deviation_for_review"],
                    exact_context=redis["runtime_window_indices"] == [0, 1]
                    and redis["configuration_finding_ids"]
                    == [result["engine1"]["findings"][0]["id"]],
                    missing_preserved=sum(
                        a["runtime_evidence_state"] == "no_observed_window"
                        for a in result["asset_contexts"]
                    )
                    == 3,
                    no_priority_or_authority=result["joint_priority_calculated"]
                    is False
                    and result["deployment_binding_verified"] is False
                    and result["threat_confirmed"] is False
                    and result["actions_executed"] == [],
                    synthetic_source=result["engine2"]["observation"]["source"]
                    == "synthetic",
                )
                if args.engine1_pipeline:
                    checks["existing_pipeline_executed"] = (
                        result["engine1_pipeline_executed"] is True
                        and result["engine1"]["retrieval_mode"] == "lexical"
                        and bool(result["engine1"]["retrieved_sources"])
                        and result["engine1"]["findings"][0]["priority"][
                            "runtime_observed"
                        ]
                        is False
                    )
                    checks["no_model_or_network"] = (
                        result["engine1"]["rag"] is None
                        and result["active_verification_asset_count"] == 0
                    )
                code = 0 if all(checks.values()) else 1
                report = dict(
                    executed_at=datetime.now(timezone.utc).isoformat(),
                    status="synthetic_check_passed"
                    if code == 0
                    else "synthetic_check_failed",
                    launcher_sha256=launcher_hash,
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
