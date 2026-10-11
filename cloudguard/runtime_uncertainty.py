"""Paired family bootstrap preparation on synthetic decisions, not research results."""

import hashlib
import json
import math
import random
import re

from .runtime import IDENTIFIER
from .runtime_accounting import AVAILABILITY, DECISIONS, LABELS
from .runtime_paired_accounting import compare_synthetic

METRICS = (
    "precision",
    "recall",
    "false_positive_rate",
    "f1",
    "all_known_positive_detection_fraction",
    "all_known_negative_flag_fraction",
    "known_decision_coverage",
    "observed_decision_coverage",
)


def _vector(rows):
    # Three availability counts followed by the 3x3 observed label/decision table.
    counts = [0] * 12
    for row in rows:
        counts[AVAILABILITY.index(row["availability"])] += 1
        if row["availability"] == "observed":
            counts[
                3 + 3 * LABELS.index(row["label"]) + DECISIONS.index(row["decision"])
            ] += 1
    return counts


def _rates(counts):
    observed, _, _, fp, tn, na, tp, fn, pa, uf, un, _ = counts
    known = tp + fn + pa + fp + tn + na

    def ratio(a, b):
        return a / b if b else None

    return dict(
        zip(
            METRICS,
            (
                ratio(tp, tp + fp),
                ratio(tp, tp + fn),
                ratio(fp, fp + tn),
                ratio(2 * tp, 2 * tp + fp + fn),
                ratio(tp, tp + fn + pa),
                ratio(fp, fp + tn + na),
                ratio(tp + fn + fp + tn, known),
                ratio(tp + fn + fp + tn + uf + un, observed),
            ),
        )
    )


def _percentile(values, probability):
    """Linear interpolation at (n-1)*p, never substitutes for missing ratios."""
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    low, high = math.floor(position), math.ceil(position)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def grouped_synthetic(document, *, draws=2000, seed=20261011):
    """Keep all windows/runs of a declared family together in each paired draw.

    The estimand is the difference of pooled unit-weighted ratios, not the mean
    of family ratios. IDs do not authenticate independence. No fitting or labels
    are generated, and this interface cannot authorize real-data evaluation.
    """
    if (
        type(document) is not dict
        or set(document) != {"schema_version", "origin", "paired", "unit_groups"}
        or document["schema_version"] != "synthetic_grouped_uncertainty_v1"
        or document["origin"] != "synthetic_fixture"
        or type(document["unit_groups"]) is not dict
        or type(draws) is not int
        or not 1000 <= draws <= 10000
        or type(seed) is not int
        or not 0 <= seed < 2**32
    ):
        raise ValueError("invalid synthetic grouped uncertainty document or budget")
    paired = compare_synthetic(document["paired"])
    left = {row["unit_id"]: row for row in document["paired"]["baseline"]["units"]}
    right = {row["unit_id"]: row for row in document["paired"]["variant"]["units"]}
    groups = document["unit_groups"]
    if groups.keys() != left.keys():
        raise ValueError("family mapping must cover exactly the paired units")
    families, runs = {}, {}
    for unit in sorted(left):
        group = groups[unit]
        if type(group) is not str or not re.fullmatch(
            IDENTIFIER["pattern"], group, flags=re.ASCII
        ):
            raise ValueError("invalid family identifier")
        run = left[unit]["run_id"]
        if run in runs and runs[run] != group:
            raise ValueError("one run cannot be split between families")
        runs[run] = group
        families.setdefault(group, []).append(unit)
    if len(families) > 100:
        raise ValueError("family budget exceeded")
    vectors = [
        (_vector(left[u] for u in families[g]), _vector(right[u] for u in families[g]))
        for g in sorted(families)
    ]
    distributions = {name: [] for name in METRICS}
    count = len(vectors)
    performed = draws if count >= 2 else 0
    rng = random.Random(seed)
    for _ in range(performed):
        baseline, variant = [0] * 12, [0] * 12
        # Draw family indices once: never independently resample the two systems.
        for _ in range(count):
            a, b = vectors[rng.randrange(count)]
            for j in range(12):
                baseline[j] += a[j]
                variant[j] += b[j]
        a, b = _rates(baseline), _rates(variant)
        for name in METRICS:
            if a[name] is not None and b[name] is not None:
                distributions[name].append(b[name] - a[name])
    intervals = {}
    for name, values in distributions.items():
        point = paired["variant_minus_baseline"][name]
        reason = (
            "insufficient_declared_families"
            if count < 2
            else "undefined_original_ratio"
            if point is None
            else "undefined_resamples"
            if len(values) != performed
            else None
        )
        intervals[name] = dict(
            estimate=point,
            percentile95=None
            if reason
            else [_percentile(values, 0.025), _percentile(values, 0.975)],
            interval_withheld_reason=reason,
            defined_draws=len(values),
            undefined_draws=performed - len(values),
            degenerate_distribution=bool(values) and min(values) == max(values),
        )
    return dict(
        protocol="synthetic_grouped_uncertainty_report_v1",
        evidence_level="synthetic_software_only",
        method="paired_family_percentile_bootstrap",
        estimand="variant_minus_baseline_pooled_unit_weighted_ratios",
        nominal_confidence_level=0.95,
        quantile_method="linear_at_n_minus_one_times_p",
        random_generator="python_random_MT19937_randrange",
        input_canonical_sha256=hashlib.sha256(
            json.dumps(document, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        seed=seed,
        requested_draws=draws,
        performed_draws=performed,
        declared_family_count=count,
        declared_family_sizes=sorted(len(units) for units in families.values()),
        paired=paired,
        differences=intervals,
        independent_evaluation_verified=False,
        real_data_evaluation_authorized=False,
        sample_size_adequacy_verified=False,
        labels_created=False,
        model_fitting_performed=False,
        model_predictions_generated=False,
        actions_executed=[],
        limitations=[
            "Invented decisions only; declared family/run IDs do not prove independent sampling or authentic labels.",
            "Whole families are sampled with replacement using the same multiplicities for both systems; unequal families retain all their units.",
            "All original missing, unusable, unknown and abstained units remain in paired accounting; conditional metrics still exclude some units.",
            "Any undefined resample withholds that interval; no dropping, replacement draws, zero imputation or perfect-ratio substitution.",
            "Fewer than two families withholds intervals; two or more is an arithmetic prerequisite, not adequate study size.",
            "Percentile intervals are exploratory software output, not guaranteed coverage, BCa, significance tests or multiplicity-adjusted intervals.",
            "Final method/sample rationale and fixed-recall operating point require review before independent evaluation; no new approval is asserted.",
        ],
    )
