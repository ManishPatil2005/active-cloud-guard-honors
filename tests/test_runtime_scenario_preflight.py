"""Actual existing workloads cannot be promoted to an independent benchmark."""

import copy
from unittest.mock import patch

import pytest

from scripts import runtime_scenario_preflight as module


def inventory():
    return [{"asset_id": "compose/redis", "host": "127.0.0.1", "port": 16379}]


def test_existing_profiles_have_one_family_and_no_execution_authority():
    report = module.inspect(module.build(), inventory(), module.PROFILES)
    assert report["declared_development_families"] == 1
    assert report["proposed_study_families"] == 12
    assert report["proposed_window_seconds"] == 60
    assert report["measurement_covers_study_window"] is False
    assert [p["measurement_ping_count"] for p in report["profiles"]] == [1, 4]
    assert all(p["measurement_duration_seconds"] == 4 for p in report["profiles"])
    assert report["actions_executed"] == []
    for key in (
        "execution_ready",
        "collection_authorized",
        "labels_created",
        "model_fitting_authorized",
    ):
        assert report[key] is False


@pytest.mark.parametrize(
    "field,value",
    [
        ("host", "0.0.0.0"),
        ("host", "localhost"),
        ("port", True),
        ("port", 0),
        ("port", 65536),
        ("port", 6379),
        ("asset_id", []),
        ("asset_id", "other"),
        ("asset_id", "x" * 129),
    ],
)
def test_bad_or_changed_endpoint_refused(field, value):
    rows = inventory()
    rows[0][field] = value
    with pytest.raises(ValueError):
        module.inspect(module.build(), rows, module.PROFILES)


@pytest.mark.parametrize("rows", [None, [], [{}], inventory() * 2, inventory() * 33])
def test_bad_inventory_refused(rows):
    with pytest.raises(ValueError):
        module.inspect(module.build(), rows, module.PROFILES)


@pytest.mark.parametrize(
    "profiles",
    [
        None,
        {},
        {"ping_1": (False,), "ping_4": (0, 1, 2, 3)},
        {"ping_1": [0], "ping_4": (0, 1, 2, 3)},
        {"ping_1": (0,), "ping_4": (0, 1, 2, 3, 4)},
        {"ping_1": (0,), "ping_4": (0, 1, 2, 3), "shell": (0,)},
    ],
)
def test_changed_workload_requires_review(profiles):
    with pytest.raises(ValueError):
        module.inspect(module.build(), inventory(), profiles)


def test_proposed_plan_cannot_claim_authority():
    plan = copy.deepcopy(module.build())
    plan["collection_authorized"] = True
    with pytest.raises(ValueError):
        module.inspect(plan, inventory(), module.PROFILES)


def test_actual_offline_files_bind_without_execution():
    with patch("subprocess.run", side_effect=AssertionError("no execution")):
        reports, code = module.collect(None)
    assert code == 0
    report = reports["output"]
    assert len(report["source_sha256"]) == 8
    assert (
        report["source_sha256"]["docs/ENGINE2_SUPERVISOR_REVIEW_PROPOSAL.md"]
        == module.PROPOSAL_SHA
    )
    assert report["execution_ready"] is False


def test_changed_proposal_refused():
    with patch.object(module, "read_bytes", return_value=b"changed"):
        with pytest.raises(ValueError, match="proposal bytes"):
            module.collect(None)


def test_existing_evidence_refused_before_inputs(tmp_path):
    target = tmp_path / "kept.json"
    target.write_bytes(b"historical")
    with patch("sys.argv", ["preflight", "--output", str(target)]):
        with patch.object(
            module, "collect", side_effect=AssertionError("must not run")
        ):
            assert module.evidence_main(module.collect) == 1
    assert target.read_bytes() == b"historical"
