"""Offline qualification catalogue; no Docker, sensor, model or service execution."""

import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.evidence import evidence_main
from cloudguard.limits import json_value, read_bytes
from cloudguard.workload import PROFILES
from scripts.runtime_study_plan import PROPOSAL_SHA, build, validate_plan


def inspect(plan, inventory, profiles):
    """Validate declarations, not live identity, coverage or human approval."""
    validate_plan(plan)
    if not isinstance(inventory, list) or not 1 <= len(inventory) <= 32:
        raise ValueError("invalid bounded lab inventory")
    assets = set()
    for row in inventory:
        if (
            not isinstance(row, dict)
            or set(row) != {"asset_id", "host", "port"}
            or not isinstance(row["asset_id"], str)
            or not row["asset_id"]
            or len(row["asset_id"]) > 128
            or row["asset_id"] in assets
            or row["host"] != "127.0.0.1"
            or type(row["port"]) is not int
            or not 1 <= row["port"] <= 65535
        ):
            raise ValueError("invalid or non-loopback inventory entry")
        assets.add(row["asset_id"])
    if {
        "asset_id": "compose/redis",
        "host": "127.0.0.1",
        "port": 16379,
    } not in inventory:
        raise ValueError("fixed Redis lab endpoint missing")
    expected = {"ping_1": (0,), "ping_4": (0, 1, 2, 3)}
    if (
        not isinstance(profiles, dict)
        or set(profiles) != set(expected)
        or any(
            type(profiles[key]) is not tuple
            or len(profiles[key]) != len(offsets)
            or any(type(a) is not int or a != b for a, b in zip(profiles[key], offsets))
            for key, offsets in expected.items()
        )
    ):
        raise ValueError("workload profiles changed; catalogue review required")
    return dict(
        protocol="runtime_qualification_catalogue_v1",
        status="preflight_completed_execution_blocked",
        asset_id="compose/redis",
        host_endpoint=dict(host="127.0.0.1", port=16379),
        command_inside_identity_checked_container=[
            "redis-cli",
            "-h",
            "127.0.0.1",
            "PING",
        ],
        profiles=[
            dict(
                profile=key,
                family_id="redis-ping-development",
                measurement_duration_seconds=4,
                measurement_offsets_seconds=list(offsets),
                measurement_ping_count=len(offsets),
                fixed_warmup_ping_count=2,
                expected_reply="PONG",
                purpose="collector qualification only; not independent security data",
            )
            for key, offsets in expected.items()
        ],
        declared_development_families=1,
        proposed_study_families=12,
        proposed_window_seconds=plan["window_seconds"],
        measurement_covers_study_window=False,
        blockers=[
            "four_second_measurement_is_not_sixty_second_observed_coverage",
            "two_ping_profiles_are_one_previously_used_development_family",
            "independent_task_policy_context_and_scenario_definitions_missing",
            "live_collector_identity_timing_and_coverage_not_qualified_here",
            "reviewer_assignments_and_operational_plan_review_required",
        ],
        execution_ready=False,
        collection_authorized=False,
        labels_created=False,
        model_fitting_authorized=False,
        actions_executed=[],
    )


def collect(args):
    paths = (
        "docs/ENGINE2_SUPERVISOR_REVIEW_PROPOSAL.md",
        "testbed/inventory.json",
        "testbed/compose.yaml",
        "cloudguard/workload.py",
        "scripts/sensor_trial.py",
        "scripts/workload_control.py",
        "scripts/runtime_study_plan.py",
        "scripts/runtime_scenario_preflight.py",
    )
    raw = {path: read_bytes(ROOT / path) for path in paths}
    hashes = {path: hashlib.sha256(value).hexdigest() for path, value in raw.items()}
    if hashes[paths[0]] != PROPOSAL_SHA:
        raise ValueError("approved-by-report proposal bytes changed")
    report = inspect(build(), json_value(raw["testbed/inventory.json"]), PROFILES)
    report["source_sha256"] = hashes
    report["source_binding_limit"] = (
        "local snapshot only; no running-container or complete import-closure attestation"
    )
    report["compose_validation"] = "bytes recorded only; not live deployment validation"
    return {"output": report}, 0


if __name__ == "__main__":
    raise SystemExit(evidence_main(collect))
