import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from cloudguard.runtime_paired_accounting import compare_synthetic
from cloudguard.runtime_accounting import summarize_synthetic

ROOT = Path(__file__).resolve().parents[1]


def document():
    return json.loads(
        (ROOT / "data/runtime/paired-accounting-synthetic.json").read_text()
    )


def test_fixed_arithmetic_and_complete_denominators():
    source = document()
    report = compare_synthetic(source)
    assert report["baseline"] == summarize_synthetic(source["baseline"])
    assert report["variant"] == summarize_synthetic(source["variant"])
    assert report["matched_unit_count"] == 4
    assert report["decision_changed_unit_count"] == 1
    assert report["fp_count_reduction"] == 1
    assert report["variant_minus_baseline"]["precision"] == 0.5
    assert report["variant_minus_baseline"]["false_positive_rate"] is None
    assert report["variant_minus_baseline"]["known_decision_coverage"] == -0.5
    assert report["negative_abstention_change"] == 1
    assert report["conditional_confusion_changes"] == dict(tp=0, fp=-1, tn=0, fn=0)


@pytest.mark.parametrize("label", ["benign", "suspicious", "unknown"])
@pytest.mark.parametrize("before", ["flagged", "not_flagged", "abstained"])
@pytest.mark.parametrize("after", ["flagged", "not_flagged", "abstained"])
def test_every_transition_retained(label, before, after):
    doc = document()
    for name, decision in (("baseline", before), ("variant", after)):
        doc[name]["units"] = [
            dict(
                unit_id="one",
                run_id="run",
                label=label,
                decision=decision,
                availability="observed",
            )
        ]
    report = compare_synthetic(doc)
    assert report["all_declared_decision_transitions"][before][after] == 1
    assert report["known_observed_decision_transitions"][before][after] == (
        label != "unknown"
    )
    assert report["decision_changed_unit_count"] == (before != after)
    assert (
        sum(
            sum(row.values())
            for row in report["all_declared_decision_transitions"].values()
        )
        == 1
    )


@pytest.mark.parametrize("bad", [None, [], "bad", {}, {"origin": "synthetic_fixture"}])
def test_invalid_outer_documents(bad):
    with pytest.raises(ValueError):
        compare_synthetic(bad)


@pytest.mark.parametrize(
    "field,value",
    [
        ("origin", "real"),
        ("schema_version", True),
        ("extra", 1),
        ("baseline", None),
        ("variant", []),
    ],
)
def test_strict_fields_and_child_schemas(field, value):
    doc = document()
    doc[field] = value
    with pytest.raises(ValueError):
        compare_synthetic(doc)


@pytest.mark.parametrize(
    "field,value",
    [("unit_id", "different"), ("run_id", "different"), ("label", "benign")],
)
def test_mismatched_context_rejected(field, value):
    doc = document()
    doc["variant"]["units"][0][field] = value
    with pytest.raises(ValueError, match="paired"):
        compare_synthetic(doc)


def test_availability_cannot_be_removed_or_promoted():
    doc = document()
    row = doc["variant"]["units"][-1]
    row["availability"] = "observed"
    with pytest.raises(ValueError, match="context"):
        compare_synthetic(doc)


def test_missing_units_and_duplicates_rejected():
    doc = document()
    doc["variant"]["units"].pop()
    with pytest.raises(ValueError, match="units"):
        compare_synthetic(doc)
    doc = document()
    doc["baseline"]["units"].append(copy.deepcopy(doc["baseline"]["units"][0]))
    with pytest.raises(ValueError, match="duplicate"):
        compare_synthetic(doc)


def test_empty_denominators_remain_null():
    doc = document()
    for name in ("baseline", "variant"):
        doc[name]["units"] = []
    report = compare_synthetic(doc)
    assert report["status"] == "no_declared_units"
    assert report["fp_count_reduction"] is None
    assert all(value is None for value in report["variant_minus_baseline"].values())


def test_negative_changes_preserved():
    doc = document()
    doc["baseline"], doc["variant"] = doc["variant"], doc["baseline"]
    report = compare_synthetic(doc)
    assert report["fp_count_reduction"] is None
    assert report["variant_minus_baseline"]["precision"] == -0.5
    assert report["negative_abstention_change"] == -1
    doc["baseline"]["units"][1]["decision"] = "flagged"
    extra = dict(
        unit_id="extra",
        run_id="run",
        label="benign",
        decision="not_flagged",
        availability="observed",
    )
    doc["baseline"]["units"].append(extra)
    doc["variant"]["units"].append(dict(extra, decision="flagged"))
    assert compare_synthetic(doc)["fp_count_reduction"] == -1


def test_order_independent_pairing_and_nonmutation():
    doc = document()
    before = copy.deepcopy(doc)
    first = compare_synthetic(doc)
    assert doc == before
    doc["variant"]["units"].reverse()
    second = compare_synthetic(doc)
    for report in (first, second):
        report.pop("input_canonical_sha256")
        report["variant"].pop("input_canonical_sha256")
    assert first == second


def test_no_predictions_authority_or_raw_units_projected():
    report = compare_synthetic(document())
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
    assert "units" not in report["baseline"] and "units" not in report["variant"]
    assert "practice-" not in json.dumps(report)


def test_fixed_runner_and_output_preservation(tmp_path):
    output = tmp_path / "fresh.json"
    command = [
        sys.executable,
        str(ROOT / "scripts/runtime_paired_accounting_check.py"),
        "--output",
        str(output),
    ]
    result = subprocess.run(
        command, cwd=ROOT, capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0 and not result.stderr
    raw = output.read_bytes()
    assert all(json.loads(raw)["checks"].values())
    assert (
        subprocess.run(command, cwd=ROOT, capture_output=True, timeout=30).returncode
        == 1
    )
    assert output.read_bytes() == raw
