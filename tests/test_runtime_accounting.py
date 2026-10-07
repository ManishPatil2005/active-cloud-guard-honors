import copy
import itertools
import json
from pathlib import Path
import subprocess
import sys

import pytest

from cloudguard.runtime_accounting import summarize_synthetic, LABELS, DECISIONS
from cloudguard.metrics import metrics

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def document():
    return json.loads((ROOT / "data/runtime/accounting-synthetic.json").read_text())


def test_example_counts_and_inclusive_denominators(document):
    before = copy.deepcopy(document)
    report = summarize_synthetic(document)
    assert document == before
    assert report["availability_counts"] == dict(observed=9, missing=1, unusable=1)
    assert report["conditional_confusion"] == dict(tp=1, fp=1, tn=1, fn=1)
    assert report["conditional_metrics"] == dict(
        precision=0.5, recall=0.5, false_positive_rate=0.5, f1=0.5
    )
    assert report["all_known_positive_detection_fraction"] == 1 / 3
    assert report["all_known_negative_flag_fraction"] == 1 / 3
    assert (
        report["known_decision_coverage"]
        == report["observed_decision_coverage"]
        == 2 / 3
    )
    assert report["known_decided_unit_count"] == 4
    assert report["represented_run_count"] == 4
    assert sum(report["availability_counts"].values()) == report["declared_unit_count"]
    assert sum(report["observed_label_counts"].values()) == 9
    assert sum(sum(row.values()) for row in report["observed_cells"].values()) == 9
    assert report["actions_executed"] == []
    for name in (
        "supervisor_approval_verified",
        "independent_evaluation_verified",
        "real_data_evaluation_authorized",
        "labels_created",
        "model_fitting_performed",
        "model_predictions_generated",
        "calibrated",
        "threat_confirmed",
    ):
        assert report[name] is False


@pytest.mark.parametrize("label,decision", itertools.product(LABELS, DECISIONS))
def test_all_observed_cells(document, label, decision):
    document["units"] = [
        dict(
            unit_id="one",
            run_id="r",
            label=label,
            decision=decision,
            availability="observed",
        )
    ]
    report = summarize_synthetic(document)
    assert report["observed_cells"][label][decision] == 1
    assert sum(report["conditional_confusion"].values()) == int(
        label != "unknown" and decision != "abstained"
    )


@pytest.mark.parametrize("kind", ["empty", "unknown", "abstained", "unavailable"])
def test_undefined_and_all_abstention(document, kind):
    document["units"] = [
        row
        for row in document["units"]
        if {
            "empty": False,
            "unknown": row["availability"] == "observed" and row["label"] == "unknown",
            "abstained": row["availability"] == "observed"
            and row["decision"] == "abstained",
            "unavailable": row["availability"] != "observed",
        }[kind]
    ]
    report = summarize_synthetic(document)
    assert all(value is None for value in report["conditional_metrics"].values())
    if kind != "abstained":
        assert report["all_known_positive_detection_fraction"] is None
    else:
        assert report["all_known_positive_detection_fraction"] == 0
        assert report["positive_abstentions"] == report["negative_abstentions"] == 1


@pytest.mark.parametrize(
    "key,value",
    [
        ("label", True),
        ("label", "attack"),
        ("decision", False),
        ("decision", "safe"),
        ("availability", None),
        ("unit_id", "../bad id"),
        ("unit_id", "a" * 129),
        ("run_id", 1),
    ],
)
def test_bad_unit_field(document, key, value):
    document["units"][0][key] = value
    with pytest.raises(ValueError):
        summarize_synthetic(document)


@pytest.mark.parametrize(
    "kind",
    [
        "origin",
        "schema",
        "extra",
        "tuple",
        "duplicate",
        "bound",
        "unit_extra",
        "unavailable_known",
        "unavailable_decided",
    ],
)
def test_document_and_unit_refusals(document, kind):
    if kind == "origin":
        document["origin"] = "human_submission"
    elif kind == "schema":
        document["schema_version"] = "runtime_review_v1"
    elif kind == "extra":
        document["supervisor_approval"] = True
    elif kind == "tuple":
        document["units"] = tuple(document["units"])
    elif kind == "duplicate":
        document["units"].append(document["units"][0])
    elif kind == "bound":
        document["units"] = [document["units"][0]] * 2001
    elif kind == "unit_extra":
        document["units"][0]["secret_reason"] = "do not leak"
    elif kind == "unavailable_known":
        document["units"][-1]["label"] = "benign"
    else:
        document["units"][-1]["decision"] = "not_flagged"
    with pytest.raises(ValueError):
        summarize_synthetic(document)


def test_binary_subset_matches_existing_metrics(document):
    rows = [
        row
        for row in document["units"]
        if row["availability"] == "observed"
        and row["label"] != "unknown"
        and row["decision"] != "abstained"
    ]
    reference = metrics(
        {row["unit_id"]: row["label"] == "suspicious" for row in rows},
        {row["unit_id"]: row["decision"] == "flagged" for row in rows},
    )
    report = summarize_synthetic(document)
    assert all(
        report["conditional_confusion"][key] == reference[key]
        for key in ("tp", "fp", "tn", "fn")
    )
    assert all(
        report["conditional_metrics"][key] == reference[key]
        for key in report["conditional_metrics"]
    )
    assert not any("wilson" in key for key in report)


def test_order_independent_counts_and_no_id_projection(document):
    first = summarize_synthetic(document)
    document["units"].reverse()
    second = summarize_synthetic(document)
    assert first.pop("input_canonical_sha256") != second.pop("input_canonical_sha256")
    assert first == second
    assert "fixture-tp" not in json.dumps(first)


def test_cli_exclusive_and_no_other_artifact(tmp_path):
    output = tmp_path / "check.json"
    args = [
        sys.executable,
        str(ROOT / "scripts/runtime_accounting_check.py"),
        "--output",
        str(output),
    ]
    result = subprocess.run(args, capture_output=True, text=True)
    assert result.returncode == 0 and not result.stderr
    before = output.read_bytes()
    assert all(json.loads(before)["checks"].values())
    assert subprocess.run(args, capture_output=True).returncode == 1
    assert output.read_bytes() == before
    assert list(tmp_path.iterdir()) == [output]


@pytest.mark.parametrize("value", [None, [], True, 0, "fixture", {}])
def test_non_document_types_and_missing_keys(value):
    with pytest.raises(ValueError):
        summarize_synthetic(value)


@pytest.mark.parametrize("value", [None, [], True, 0])
def test_non_unit_types(document, value):
    document["units"] = [value]
    with pytest.raises(ValueError):
        summarize_synthetic(document)


def test_exact_window_budget_boundary(document):
    document["units"] = [
        dict(
            unit_id=f"unit-{index}",
            run_id="r",
            label="unknown",
            decision="abstained",
            availability="observed",
        )
        for index in range(2000)
    ]
    report = summarize_synthetic(document)
    assert report["declared_unit_count"] == 2000
    assert report["known_decision_coverage"] is None
    assert report["observed_decision_coverage"] == 0


def test_unknown_flag_does_not_become_false_alarm(document):
    document["units"] = [row for row in document["units"] if row["label"] == "unknown"]
    report = summarize_synthetic(document)
    assert report["conditional_confusion"] == dict(tp=0, fp=0, tn=0, fn=0)
    assert report["observed_cells"]["unknown"]["flagged"] == 1
    assert report["conditional_metrics"]["false_positive_rate"] is None
