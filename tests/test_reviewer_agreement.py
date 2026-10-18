"""Invented votes verify arithmetic, not independent human reliability."""

from fractions import Fraction
import itertools
import json
from pathlib import Path
import subprocess
import sys

import pytest

from cloudguard.runtime_intake import _reviewer_agreement, inspect
from test_runtime_intake import make_bundle, review, save

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "data/runtime/intake-example/manifest.json"


def summarize(a, b):
    assert len(a) == len(b)
    keys = set(range(len(a)))
    return _reviewer_agreement([dict(enumerate(a)), dict(enumerate(b))], keys)


def test_balanced_half_agreement_is_zero_kappa():
    r = summarize(
        ["benign", "benign", "suspicious", "suspicious"],
        ["benign", "suspicious", "benign", "suspicious"],
    )
    assert r["known_agreement_fraction"] == r["known_chance_agreement"] == 0.5
    assert r["known_cohen_kappa"] == 0
    assert r["known_pair_coverage"] == 1


@pytest.mark.parametrize(
    "other,expected", [(["benign", "suspicious"], 1), (["suspicious", "benign"], -1)]
)
def test_perfect_agreement_and_reversal(other, expected):
    assert summarize(["benign", "suspicious"], other)["known_cohen_kappa"] == expected


@pytest.mark.parametrize(
    "a,b,reason",
    [
        ([], [], "no_known_pairs"),
        (["unknown"], ["unknown"], "no_known_pairs"),
        (["benign"], ["benign"], "chance_agreement_is_one"),
    ],
)
def test_undefined_kappa_is_null(a, b, reason):
    r = summarize(a, b)
    assert r["known_cohen_kappa"] is None and r["kappa_undefined_reason"] == reason


def test_unknowns_are_retained_in_full_table_and_coverage():
    r = summarize(
        ["benign", "suspicious", "unknown", "unknown"],
        ["benign", "suspicious", "benign", "unknown"],
    )
    assert (r["known_pairs"], r["unknown_pairs"], r["paired_windows"]) == (2, 2, 4)
    assert r["known_pair_coverage"] == 0.5
    assert r["all_label_agreement_fraction"] == 0.75
    assert r["known_cohen_kappa"] == 1
    assert r["original_label_pair_counts"]["unknown"]["benign"] == 1
    assert r["original_label_pair_counts"]["unknown"]["unknown"] == 1


@pytest.mark.parametrize("votes", [[], [{0: "benign"}]])
def test_incomplete_reviews_do_not_create_pairs(votes):
    r = _reviewer_agreement(votes, {0})
    assert r["status"] == "requires_two_reviews"
    assert r["paired_windows"] == 0 and r["known_pair_coverage"] is None
    assert r["known_cohen_kappa"] is None


def test_exhaustive_three_window_oracle_and_reviewer_swap():
    labels = ("benign", "suspicious", "unknown")
    for a in itertools.product(labels, repeat=3):
        for b in itertools.product(labels, repeat=3):
            r = summarize(a, b)
            known = [(x, y) for x, y in zip(a, b) if "unknown" not in (x, y)]
            n = len(known)
            expected = None
            if n:
                po = Fraction(sum(x == y for x, y in known), n)
                pe = sum(
                    Fraction(
                        sum(x == label for x, y in known)
                        * sum(y == label for x, y in known),
                        n * n,
                    )
                    for label in labels[:2]
                )
                expected = float((po - pe) / (1 - pe)) if pe != 1 else None
            assert r["known_cohen_kappa"] == expected
            assert r["known_cohen_kappa"] == summarize(b, a)["known_cohen_kappa"]
            assert (
                sum(
                    sum(row.values())
                    for row in r["original_label_pair_counts"].values()
                )
                == 3
            )


def test_opt_in_preserves_default_report_and_original_agreement():
    default = inspect(EXAMPLE)
    enhanced = inspect(EXAMPLE, include_review_agreement=True)
    stats = enhanced.pop("reviewer_agreement")
    assert enhanced == default
    assert (
        stats["known_agreement_fraction"]
        == default["pre_adjudication_agreement"]["known_agreement_fraction"]
    )
    assert stats["computed_before_adjudication"] is True
    assert stats["independent_review_verified"] is False
    assert enhanced["model_fitting_authorized"] is False


@pytest.mark.parametrize("bad", [None, 0, 1, "yes", [], {}])
def test_exact_boolean_required_before_input_read(bad):
    with pytest.raises(ValueError, match="exact boolean"):
        inspect("absent.json", include_review_agreement=bad)


def test_cli_report_is_exclusive_and_does_not_export_reasons(tmp_path):
    destination = tmp_path / "fresh.json"
    command = [
        sys.executable,
        str(ROOT / "scripts/runtime_intake.py"),
        "--manifest",
        str(EXAMPLE),
        "--output",
        str(destination),
        "--review-agreement",
    ]
    r = subprocess.run(command, capture_output=True, text=True, timeout=15)
    assert r.returncode == 0
    raw = destination.read_bytes()
    report = json.loads(raw)
    assert (
        "reviewer_agreement" in report and "reason" not in report["reviewer_agreement"]
    )
    assert report["independent_evaluation_verified"] is False
    assert subprocess.run(command, capture_output=True, timeout=15).returncode == 1
    assert destination.read_bytes() == raw


@pytest.mark.parametrize(
    "manifest_name,reviews", [("manifest.json", 2), ("manifest-typed-counted.json", 0)]
)
def test_both_intake_formats_preserve_supplied_review_counts(manifest_name, reviews):
    r = inspect(EXAMPLE.parent / manifest_name, include_review_agreement=True)
    stats = r["reviewer_agreement"]
    assert stats["supplied_reviews"] == reviews
    if reviews == 2:
        assert stats["known_pairs"] == 2 and stats["unknown_pairs"] == 1
        assert stats["known_pair_coverage"] == 2 / 3
        assert stats["known_cohen_kappa"] == 0
    else:
        assert stats["status"] == "requires_two_reviews"
        assert (
            stats["known_pair_coverage"] is None and stats["known_cohen_kappa"] is None
        )
    assert r["model_fitting_authorized"] is False


@pytest.mark.parametrize("review_count", [0, 1])
def test_missing_review_in_bundle_keeps_statistics_unavailable(tmp_path, review_count):
    bundle = make_bundle(tmp_path)
    root, manifest = bundle
    if review_count:
        review(bundle, "review-a")
    save(root, "manifest.json", manifest)
    r = inspect(root / "manifest.json", include_review_agreement=True)
    stats = r["reviewer_agreement"]
    assert stats["supplied_reviews"] == review_count
    assert stats["status"] == "requires_two_reviews"
    assert stats["known_cohen_kappa"] is None


def test_cli_conflicting_modes_refused_before_output(tmp_path):
    output = tmp_path / "unused.json"
    r = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/runtime_intake.py"),
            "--manifest",
            str(EXAMPLE),
            "--output",
            str(output),
            "--annotation-index",
            "--review-agreement",
        ],
        capture_output=True,
        timeout=15,
    )
    assert r.returncode == 2 and not output.exists()
