"""Build/check a proposed coordinator schedule; never collect, label or fit."""

import hashlib
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.evidence import evidence_main
from cloudguard.limits import read_bytes

PROTOCOL = "runtime_study_schedule_draft_v1"
PROPOSAL_SHA = "dada21e7f3d27acc3b2dcf260b61252322453b3c6f349a12f0a955f50090d32b"
SPLITS = ("train",) * 6 + ("validation",) * 3 + ("test",) * 3
SEED = 20261011


def build():
    slots = [
        dict(
            slot_id=f"slot-{family:02d}-{repeat}",
            family_id=f"family-{family:02d}",
            split=split,
            repeat=repeat,
            status="not_launched",
            receipt_sha256=None,
        )
        for family, split in enumerate(SPLITS, 1)
        for repeat in range(1, 4)
    ]
    random.Random(SEED).shuffle(slots)
    return dict(
        protocol=PROTOCOL,
        status="proposed_not_execution_approved",
        proposal_sha256=PROPOSAL_SHA,
        schedule_seed=SEED,
        window_seconds=60,
        slots=slots,
        labels_created=False,
        collection_authorized=False,
        model_fitting_authorized=False,
        independent_evaluation_verified=False,
    )


def validate_plan(plan):
    expected = build()
    if not isinstance(plan, dict) or set(plan) != set(expected):
        raise ValueError("invalid study plan envelope")
    for key in expected.keys() - {"slots"}:
        if type(plan[key]) is not type(expected[key]) or plan[key] != expected[key]:
            raise ValueError("unreviewed study plan change")
    slots = plan["slots"]
    if not isinstance(slots, list) or len(slots) != 36:
        raise ValueError("all 36 planned slots must remain present")
    # Fixed proposed order/IDs/group-held-out splits. Changes need a new version.
    for actual, wanted in zip(slots, expected["slots"], strict=True):
        if not isinstance(actual, dict) or set(actual) != set(wanted):
            raise ValueError("invalid study slot")
        for key in ("slot_id", "family_id", "split", "repeat"):
            if type(actual[key]) is not type(wanted[key]) or actual[key] != wanted[key]:
                raise ValueError("schedule identity, grouping or order changed")
        if actual["status"] not in (
            "not_launched",
            "launch_failed",
            "collection_failed",
            "capture_rejected",
            "capture_pending_review",
        ):
            raise ValueError("unsupported slot outcome")
        digest = actual["receipt_sha256"]
        if actual["status"] == "not_launched":
            if digest is not None:
                raise ValueError("unlaunched slot cannot claim a receipt")
        elif (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(c not in "0123456789abcdef" for c in digest)
        ):
            raise ValueError("attempted slot requires a preserved receipt hash")
    counts = {
        status: sum(s["status"] == status for s in slots)
        for status in (
            "not_launched",
            "launch_failed",
            "collection_failed",
            "capture_rejected",
            "capture_pending_review",
        )
    }
    return dict(
        planned_slots=36,
        proposed_families=12,
        outcomes=counts,
        declared_launched_slots=36 - counts["not_launched"] - counts["launch_failed"],
        capture_eligibility_verified=False,
        model_fitting_authorized=False,
        independent_evaluation_verified=False,
    )


def collect(args):
    digest = hashlib.sha256(
        read_bytes(ROOT / "docs/ENGINE2_SUPERVISOR_REVIEW_PROPOSAL.md")
    ).hexdigest()
    if digest != PROPOSAL_SHA:
        raise ValueError("approved-by-report proposal bytes changed")
    plan = build()
    validate_plan(plan)
    return {"output": plan}, 0


if __name__ == "__main__":
    raise SystemExit(evidence_main(collect))
