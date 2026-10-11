import copy
import itertools
import json
from pathlib import Path
import random

import pytest

from cloudguard import runtime_uncertainty as uncertainty
from cloudguard.runtime_accounting import summarize_synthetic
from cloudguard.runtime_paired_accounting import compare_synthetic

ROOT = Path(__file__).resolve().parents[1]


def document():
    return json.loads(
        (ROOT / "data/runtime/grouped-uncertainty-synthetic.json").read_text()
    )


def test_original_estimates_and_denominators_unchanged():
    doc = document()
    before = copy.deepcopy(doc)
    report = uncertainty.grouped_synthetic(doc, draws=1000)
    assert doc == before
    assert report["paired"] == compare_synthetic(doc["paired"])
    assert report["declared_family_count"] == 4
    assert report["declared_family_sizes"] == [8, 8, 8, 8]
    for key, value in report["differences"].items():
        assert value["estimate"] == report["paired"]["variant_minus_baseline"][key]
        assert value["defined_draws"] + value["undefined_draws"] == 1000
    assert report["paired"]["baseline"]["availability_counts"] == dict(
        observed=24, missing=4, unusable=4
    )


@pytest.mark.parametrize(
    "label,decision",
    itertools.product(
        ("benign", "suspicious", "unknown"), ("flagged", "not_flagged", "abstained")
    ),
)
def test_reducer_matches_existing_accounting_for_all_cells(label, decision):
    rows = [
        dict(
            unit_id="u",
            run_id="r",
            label=label,
            decision=decision,
            availability="observed",
        )
    ]
    reference = summarize_synthetic(
        dict(
            schema_version="synthetic_runtime_accounting_v1",
            origin="synthetic_fixture",
            units=rows,
        )
    )
    expected = {
        **reference["conditional_metrics"],
        **{name: reference[name] for name in uncertainty.METRICS[4:]},
    }
    assert uncertainty._rates(uncertainty._vector(rows)) == expected


def test_random_mixed_reducer_matches_reference():
    rng = random.Random(73)
    for _ in range(30):
        rows = []
        for i in range(50):
            availability = rng.choice(("observed", "missing", "unusable"))
            rows.append(
                dict(
                    unit_id=f"u{i}",
                    run_id="r",
                    availability=availability,
                    label=rng.choice(("benign", "suspicious", "unknown"))
                    if availability == "observed"
                    else "unknown",
                    decision=rng.choice(("flagged", "not_flagged", "abstained"))
                    if availability == "observed"
                    else "abstained",
                )
            )
        ref = summarize_synthetic(
            dict(
                schema_version="synthetic_runtime_accounting_v1",
                origin="synthetic_fixture",
                units=rows,
            )
        )
        assert uncertainty._rates(uncertainty._vector(rows)) == {
            **ref["conditional_metrics"],
            **{name: ref[name] for name in uncertainty.METRICS[4:]},
        }


def test_exact_cluster_pairing_and_unequal_sizes(monkeypatch):
    doc = document()
    # Retain two families with unequal unit counts; do not renormalize family weights.
    keep = [u for u in doc["unit_groups"] if doc["unit_groups"][u] == "family-a"]
    keep += [u for u in doc["unit_groups"] if doc["unit_groups"][u] == "family-b"][:2]
    doc["unit_groups"] = {u: doc["unit_groups"][u] for u in keep}
    for side in ("baseline", "variant"):
        doc["paired"][side]["units"] = [
            r for r in doc["paired"][side]["units"] if r["unit_id"] in keep
        ]

    class Fixed:
        def __init__(self):
            self.calls = 0

        def randrange(self, count):
            assert count == 2
            # All four possible ordered family samples repeated 250 times.
            value = (0, 0, 0, 1, 1, 0, 1, 1)[self.calls % 8]
            self.calls += 1
            return value

    fixed = Fixed()
    monkeypatch.setattr(uncertainty.random, "Random", lambda seed: fixed)
    report = uncertainty.grouped_synthetic(doc, draws=1000)
    assert fixed.calls == 2000  # Not 4000 independently chosen system indices.
    assert report["declared_family_sizes"] == [2, 8]
    distribution = {name: [] for name in uncertainty.METRICS}
    for draw in (
        ("family-a", "family-a"),
        ("family-a", "family-b"),
        ("family-b", "family-a"),
        ("family-b", "family-b"),
    ):
        paired = copy.deepcopy(doc["paired"])
        for side in ("baseline", "variant"):
            paired[side]["units"] = [
                dict(
                    row,
                    unit_id=f"draw{j}-{row['unit_id']}",
                    run_id=f"draw{j}-{row['run_id']}",
                )
                for j, family in enumerate(draw)
                for row in doc["paired"][side]["units"]
                if doc["unit_groups"][row["unit_id"]] == family
            ]
        for name, delta in compare_synthetic(paired)["variant_minus_baseline"].items():
            if delta is not None:
                distribution[name] += [delta] * 250
    for name, values in distribution.items():
        result = report["differences"][name]
        assert result["defined_draws"] == len(values)
        if len(values) == 1000 and result["estimate"] is not None:
            # Each extreme occurs at least 25%, so the 2.5/97.5 percentiles are extrema.
            assert result["percentile95"] == [min(values), max(values)]
        else:
            assert result["percentile95"] is None


def test_identical_systems_have_zero_paired_differences():
    doc = document()
    doc["paired"]["variant"] = copy.deepcopy(doc["paired"]["baseline"])
    report = uncertainty.grouped_synthetic(doc, draws=1000)
    for result in report["differences"].values():
        assert result["estimate"] == 0
        assert result["percentile95"] == [0, 0]
        assert result["degenerate_distribution"]


def test_swapping_systems_negates_intervals():
    doc = document()
    report = uncertainty.grouped_synthetic(doc, draws=1000)
    doc["paired"]["baseline"], doc["paired"]["variant"] = (
        doc["paired"]["variant"],
        doc["paired"]["baseline"],
    )
    reverse = uncertainty.grouped_synthetic(doc, draws=1000)
    for name, result in report["differences"].items():
        assert reverse["differences"][name]["estimate"] == -result["estimate"]
        interval = result["percentile95"]
        if interval is not None:
            assert reverse["differences"][name]["percentile95"] == pytest.approx(
                [-interval[1], -interval[0]]
            )


def test_no_global_rng_effect_and_reproducibility():
    state = random.getstate()
    a = uncertainty.grouped_synthetic(document(), draws=1000)
    assert random.getstate() == state
    assert a == uncertainty.grouped_synthetic(document(), draws=1000)


def test_input_order_does_not_change_draws():
    doc = document()
    a = uncertainty.grouped_synthetic(doc, draws=1000)
    for side in ("baseline", "variant"):
        doc["paired"][side]["units"].reverse()
    doc["unit_groups"] = dict(reversed(list(doc["unit_groups"].items())))
    b = uncertainty.grouped_synthetic(doc, draws=1000)
    assert a["differences"] == b["differences"]


@pytest.mark.parametrize("groups", [0, 1])
def test_insufficient_families_no_draws(groups):
    doc = document()
    if groups == 0:
        doc["unit_groups"] = {}
        for side in ("baseline", "variant"):
            doc["paired"][side]["units"] = []
    else:
        doc["unit_groups"] = dict.fromkeys(doc["unit_groups"], "one-family")
    report = uncertainty.grouped_synthetic(doc)
    assert report["performed_draws"] == 0
    for result in report["differences"].values():
        assert result["percentile95"] is None
        assert result["interval_withheld_reason"] == "insufficient_declared_families"


def test_undefined_draws_preserved_not_resampled():
    doc = document()
    for side in ("baseline", "variant"):
        for row in doc["paired"][side]["units"]:
            if (
                doc["unit_groups"][row["unit_id"]] != "family-a"
                and row["availability"] == "observed"
            ):
                row.update(label="benign", decision="not_flagged")
    report = uncertainty.grouped_synthetic(doc, draws=1000)
    precision = report["differences"]["precision"]
    assert precision["estimate"] is not None
    assert 0 < precision["undefined_draws"] < 1000
    assert precision["percentile95"] is None
    assert precision["interval_withheld_reason"] == "undefined_resamples"
    assert report["performed_draws"] == 1000


def test_all_unknown_has_no_original_ratios():
    doc = document()
    for side in ("baseline", "variant"):
        for row in doc["paired"][side]["units"]:
            row["label"] = "unknown"
    report = uncertainty.grouped_synthetic(doc, draws=1000)
    result = report["differences"]["precision"]
    assert result["interval_withheld_reason"] == "undefined_original_ratio"
    assert result["percentile95"] is None
    assert result["undefined_draws"] == 1000


@pytest.mark.parametrize("draws", [True, 0, 999, 10001, 1000.0, "1000", None])
def test_invalid_draw_budget(draws):
    with pytest.raises(ValueError):
        uncertainty.grouped_synthetic(document(), draws=draws)


@pytest.mark.parametrize("seed", [True, -1, 2**32, 1.0, "1", None])
def test_invalid_seed(seed):
    with pytest.raises(ValueError):
        uncertainty.grouped_synthetic(document(), seed=seed)


@pytest.mark.parametrize(
    "field,value",
    [
        ("origin", "recorded"),
        ("schema_version", True),
        ("unit_groups", []),
        ("extra", 1),
    ],
)
def test_schema_and_real_data_refused(field, value):
    doc = document()
    doc[field] = value
    with pytest.raises(ValueError):
        uncertainty.grouped_synthetic(doc)


@pytest.mark.parametrize(
    "kind", ["missing", "extra", "bad_id", "split_run", "too_many"]
)
def test_invalid_group_mapping(kind):
    doc = document()
    unit = next(iter(doc["unit_groups"]))
    if kind == "missing":
        del doc["unit_groups"][unit]
    elif kind == "extra":
        doc["unit_groups"]["extra"] = "x"
    elif kind == "bad_id":
        doc["unit_groups"][unit] = "../bad"
    elif kind == "split_run":
        doc["unit_groups"][unit] = "new-family"
    else:
        doc["unit_groups"] = {f"u{i}": f"g{i}" for i in range(101)}
        for side in ("baseline", "variant"):
            doc["paired"][side]["units"] = [
                dict(
                    unit_id=f"u{i}",
                    run_id=f"r{i}",
                    label="benign",
                    decision="not_flagged",
                    availability="observed",
                )
                for i in range(101)
            ]
    with pytest.raises(ValueError):
        uncertainty.grouped_synthetic(doc)


def test_quantile_interpolation():
    assert uncertainty._percentile([3, 0, 2, 1], 0.025) == pytest.approx(0.075)
    assert uncertainty._percentile([3, 0, 2, 1], 0.975) == pytest.approx(2.925)


def test_no_evaluation_authority_or_generated_labels():
    report = uncertainty.grouped_synthetic(document(), draws=1000)
    for key in (
        "independent_evaluation_verified",
        "real_data_evaluation_authorized",
        "sample_size_adequacy_verified",
        "labels_created",
        "model_fitting_performed",
        "model_predictions_generated",
    ):
        assert report[key] is False
    assert report["actions_executed"] == []
    assert "unit_groups" not in report


def test_cli_exclusive_output(tmp_path):
    from scripts import runtime_uncertainty_check as runner

    path = tmp_path / "evidence.json"
    assert runner.main(["--output", str(path)]) == 0
    original = path.read_bytes()
    assert runner.main(["--output", str(path)]) == 1
    assert path.read_bytes() == original
    saved = json.loads(original)
    assert all(saved["checks"].values())


def test_cli_failure_preserves_safe_receipt(tmp_path, monkeypatch):
    from scripts import runtime_uncertainty_check as runner

    def fail(*args, **kwargs):
        raise ValueError("PRIVATE-detail")

    monkeypatch.setattr(runner, "grouped_synthetic", fail)
    path = tmp_path / "rejected.json"
    assert runner.main(["--output", str(path)]) == 1
    assert "PRIVATE" not in path.read_text()
    assert json.loads(path.read_text())["status"] == "rejected"
