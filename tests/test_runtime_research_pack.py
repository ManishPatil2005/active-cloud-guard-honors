"""Draft/template contract checks; no human reviews or eligible data created."""

import hashlib
import json
from pathlib import Path
import re
import subprocess

import pytest

from cloudguard.runtime_intake import ADJUDICATION, REVIEW, _labels
from cloudguard.verification import validate
from scripts.repository_check import forbidden

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "name,schema",
    [
        ("runtime-review.json.example", REVIEW),
        ("runtime-adjudication.json.example", ADJUDICATION),
    ],
)
def test_unfilled_templates_match_fields_but_cannot_pass(name, schema):
    document = json.loads((ROOT / "docs/templates" / name).read_text(encoding="utf-8"))
    assert set(document) == set(schema["required"])
    assert set(document["labels"][0]) == set(
        REVIEW["properties"]["labels"]["items"]["required"]
    )
    assert document["labels"][0]["start_epoch"] is None
    with pytest.raises(ValueError):
        validate(document, schema)


@pytest.mark.parametrize("adjudication", [False, True])
def test_synthetic_in_memory_completion_uses_existing_contract(adjudication):
    name = (
        "runtime-adjudication.json.example"
        if adjudication
        else "runtime-review.json.example"
    )
    document = json.loads((ROOT / "docs/templates" / name).read_text(encoding="utf-8"))
    document["guidelines_sha256"] = hashlib.sha256(
        (ROOT / "docs/RUNTIME_LABELING_GUIDELINES.md").read_bytes()
    ).hexdigest()  # Integrity of a draft, explicitly not approval.
    if adjudication:
        document.update(
            adjudicator_id="synthetic-schema-test", review_sha256=["1" * 64, "2" * 64]
        )
    else:
        document.update(
            reviewer_id="synthetic-schema-test",
            origin="synthetic_fixture",
            blinded=True,
        )
    document["labels"] = [
        dict(
            run_id="fixture-run",
            asset_id="compose/redis",
            start_epoch=1767312000,
            label="unknown",
            reason="Synthetic schema test only; no human annotation.",
        )
    ]
    validate(document, ADJUDICATION if adjudication else REVIEW)
    assert _labels(document, {("fixture-run", "compose/redis", 1767312000)}) == {
        ("fixture-run", "compose/redis", 1767312000): "unknown"
    }


@pytest.mark.parametrize(
    "name",
    [
        "RUNTIME_LABELING_GUIDELINES.md",
        "RUNTIME_LABELING_PROTOCOL.md",
        "RUNTIME_CAPTURE_ELIGIBILITY.md",
        "templates/runtime-supervisor-review.md",
        "templates/runtime-case-ledger.md",
    ],
)
def test_governance_material_is_explicitly_unapproved(name):
    text = (ROOT / "docs" / name).read_text(encoding="utf-8")
    assert "DRAFT — NOT APPROVED" in text
    assert "[x]" not in text.casefold()


def test_capture_checklist_has_all_sixteen_distinct_gates():
    text = (ROOT / "docs/RUNTIME_CAPTURE_ELIGIBILITY.md").read_text(encoding="utf-8")
    assert re.findall(r"^\| (G\d{2}) ", text, flags=re.MULTILINE) == [
        f"G{index:02}" for index in range(1, 17)
    ]


@pytest.mark.parametrize(
    "path,blocked",
    [
        ("private/runtime-labeling/reviewer.json", True),
        ("PRIVATE/Runtime-Labeling/consent/key.md", True),
        ("docs/templates/runtime-review.json.example", False),
        ("private/runtime-labeling-example/README.md", False),
    ],
)
def test_private_review_records_are_publication_excluded(path, blocked):
    assert forbidden(path) is blocked


def test_git_ignore_protects_future_private_work_without_creating_it():
    result = subprocess.run(
        ["git", "check-ignore", "--no-index", "private/runtime-labeling/reviewer.json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "private/runtime-labeling/reviewer.json"
    assert not result.stderr
