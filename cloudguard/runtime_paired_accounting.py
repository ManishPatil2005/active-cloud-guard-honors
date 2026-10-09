"""Matched synthetic decision arithmetic, never a detector effectiveness study."""

from collections import Counter
import hashlib
import json

from .metrics import fp_reduction
from .runtime_accounting import DECISIONS, summarize_synthetic


def compare_synthetic(document):
    if (
        type(document) is not dict
        or set(document) != {"schema_version", "origin", "baseline", "variant"}
        or document["schema_version"] != "synthetic_paired_accounting_v1"
        or document["origin"] != "synthetic_fixture"
    ):
        raise ValueError("invalid synthetic paired accounting document")
    baseline = summarize_synthetic(document["baseline"])
    variant = summarize_synthetic(document["variant"])
    left = {row["unit_id"]: row for row in document["baseline"]["units"]}
    right = {row["unit_id"]: row for row in document["variant"]["units"]}
    if left.keys() != right.keys():
        raise ValueError("paired units must match exactly")
    transitions, known_transitions = Counter(), Counter()
    changed = 0
    for unit, row in left.items():
        other = right[unit]
        if any(
            row[field] != other[field] for field in ("run_id", "label", "availability")
        ):
            raise ValueError("paired unit context must match exactly")
        transitions[row["decision"], other["decision"]] += 1
        changed += row["decision"] != other["decision"]
        if row["availability"] == "observed" and row["label"] != "unknown":
            known_transitions[row["decision"], other["decision"]] += 1

    def cells(counts):
        return {a: {b: counts[a, b] for b in DECISIONS} for a in DECISIONS}

    def difference(a, b):
        return None if a is None or b is None else b - a

    differences = {
        name: difference(baseline["conditional_metrics"][name], value)
        for name, value in variant["conditional_metrics"].items()
    }
    for name in (
        "all_known_positive_detection_fraction",
        "all_known_negative_flag_fraction",
        "known_decision_coverage",
        "observed_decision_coverage",
    ):
        differences[name] = difference(baseline[name], variant[name])
    return dict(
        protocol="synthetic_paired_accounting_report_v1",
        evidence_level="synthetic_software_only",
        status="paired_accounting_computed" if left else "no_declared_units",
        input_canonical_sha256=hashlib.sha256(
            json.dumps(document, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        matched_unit_count=len(left),
        decision_changed_unit_count=changed,
        all_declared_decision_transitions=cells(transitions),
        known_observed_decision_transitions=cells(known_transitions),
        baseline=baseline,
        variant=variant,
        variant_minus_baseline=differences,
        conditional_confusion_changes={
            name: value - baseline["conditional_confusion"][name]
            for name, value in variant["conditional_confusion"].items()
        },
        fp_count_reduction=fp_reduction(
            baseline["conditional_confusion"]["fp"],
            variant["conditional_confusion"]["fp"],
        ),
        positive_abstention_change=variant["positive_abstentions"]
        - baseline["positive_abstentions"],
        negative_abstention_change=variant["negative_abstentions"]
        - baseline["negative_abstentions"],
        supervisor_approval_verified=False,
        independent_evaluation_verified=False,
        real_data_evaluation_authorized=False,
        labels_created=False,
        model_fitting_performed=False,
        model_predictions_generated=False,
        calibrated=False,
        threat_confirmed=False,
        actions_executed=[],
        limitations=[
            "Invented supplied decisions only, not Engine1/Engine2 predictions or independent labels.",
            "Exact unit/run/label/availability equality establishes declared pairing, not authentic provenance or independent groups.",
            "Conditional metrics can improve by abstaining; inclusive denominators and coverage remain separate.",
            "FP count reduction is not false-positive-rate reduction; undefined metrics/differences remain null and negative changes are retained.",
            "No confidence intervals, bootstrap, significance, calibrated thresholds, held-out effectiveness, latency, overhead or energy evaluation.",
        ],
    )
