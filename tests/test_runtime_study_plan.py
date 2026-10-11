"""Proposed schedule accounting is not eligibility or independent evidence."""

import copy
from unittest.mock import patch

import pytest

from scripts import runtime_study_plan as module


def test_deterministic_group_held_out_and_no_execution():
    plan = module.build()
    assert plan == module.build()
    assert len({s["slot_id"] for s in plan["slots"]}) == 36
    for family in {s["family_id"] for s in plan["slots"]}:
        rows = [s for s in plan["slots"] if s["family_id"] == family]
        assert len({s["split"] for s in rows}) == 1
        assert sorted(s["repeat"] for s in rows) == [1, 2, 3]
    report = module.validate_plan(plan)
    assert report["outcomes"]["not_launched"] == 36
    assert report["declared_launched_slots"] == 0
    assert report["model_fitting_authorized"] is False
    assert report["capture_eligibility_verified"] is False


@pytest.mark.parametrize(
    "field,value",
    [
        ("repeat", True),
        ("repeat", 1.5),
        ("family_id", "other"),
        ("split", "other"),
        ("status", "accepted"),
        ("receipt_sha256", "0" * 64),
    ],
)
def test_changed_or_fake_slot_refused(field, value):
    plan = module.build()
    plan["slots"][0][field] = value
    with pytest.raises(ValueError):
        module.validate_plan(plan)


@pytest.mark.parametrize(
    "defect", ["missing", "duplicate", "reorder", "extra", "authorized", "bad_root"]
)
def test_plan_changes_refused(defect):
    plan = module.build()
    if defect == "missing":
        plan["slots"].pop()
    elif defect == "duplicate":
        plan["slots"][1] = copy.deepcopy(plan["slots"][0])
    elif defect == "reorder":
        plan["slots"].reverse()
    elif defect == "extra":
        plan["extra"] = True
    elif defect == "authorized":
        plan["collection_authorized"] = True
    else:
        plan = []
    with pytest.raises(ValueError):
        module.validate_plan(plan)


@pytest.mark.parametrize(
    "status",
    [
        "launch_failed",
        "collection_failed",
        "capture_rejected",
        "capture_pending_review",
    ],
)
def test_all_negative_and_pending_outcomes_remain_in_denominator(status):
    plan = module.build()
    plan["slots"][0].update(status=status, receipt_sha256="a" * 64)
    report = module.validate_plan(plan)
    assert report["outcomes"][status] == 1
    assert report["outcomes"]["not_launched"] == 35
    assert report["declared_launched_slots"] == (0 if status == "launch_failed" else 1)
    assert sum(report["outcomes"].values()) == 36
    assert report["model_fitting_authorized"] is False


@pytest.mark.parametrize("digest", [None, True, "a" * 63, "A" * 64])
def test_attempt_without_valid_receipt_hash_refused(digest):
    plan = module.build()
    plan["slots"][0].update(status="collection_failed", receipt_sha256=digest)
    with pytest.raises(ValueError):
        module.validate_plan(plan)


def test_changed_proposal_refused():
    with patch.object(module, "read_bytes", return_value=b"changed"):
        with pytest.raises(ValueError, match="proposal bytes"):
            module.collect(None)


def test_existing_output_refused_before_plan_activity(tmp_path):
    path = tmp_path / "original.json"
    path.write_bytes(b"failed study evidence")
    with (
        patch("sys.argv", ["plan", "--output", str(path)]),
        patch.object(module, "collect") as collect,
    ):
        assert module.evidence_main(collect) == 1
    collect.assert_not_called()
    assert path.read_bytes() == b"failed study evidence"
