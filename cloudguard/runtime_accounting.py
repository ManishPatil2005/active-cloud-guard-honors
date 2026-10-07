"""Synthetic decision-accounting arithmetic, not independent detector evaluation."""

from collections import Counter
import hashlib
import json
import re

from .runtime import IDENTIFIER

LABELS = ("benign", "suspicious", "unknown")
DECISIONS = ("flagged", "not_flagged", "abstained")
AVAILABILITY = ("observed", "missing", "unusable")


def summarize_synthetic(document):
    if (
        type(document) is not dict
        or set(document) != {"schema_version", "origin", "units"}
        or document["schema_version"] != "synthetic_runtime_accounting_v1"
        or document["origin"] != "synthetic_fixture"
        or type(document["units"]) is not list
        or len(document["units"]) > 2000
    ):
        raise ValueError("invalid synthetic accounting document")
    seen, runs = set(), set()
    availability, labels, decisions = Counter(), Counter(), Counter()
    cells = Counter()
    for row in document["units"]:
        if type(row) is not dict or set(row) != {
            "unit_id",
            "run_id",
            "label",
            "decision",
            "availability",
        }:
            raise ValueError("invalid synthetic accounting unit")
        for key in ("unit_id", "run_id"):
            if type(row[key]) is not str or not re.fullmatch(
                IDENTIFIER["pattern"], row[key], flags=re.ASCII
            ):
                raise ValueError("invalid synthetic accounting identifier")
        if row["unit_id"] in seen:
            raise ValueError("duplicate synthetic accounting unit")
        if (
            type(row["label"]) is not str
            or row["label"] not in LABELS
            or type(row["decision"]) is not str
            or row["decision"] not in DECISIONS
            or type(row["availability"]) is not str
            or row["availability"] not in AVAILABILITY
        ):
            raise ValueError("invalid synthetic accounting category")
        if row["availability"] != "observed" and (
            row["label"] != "unknown" or row["decision"] != "abstained"
        ):
            raise ValueError("unavailable units must stay unknown and abstained")
        seen.add(row["unit_id"])
        runs.add(row["run_id"])
        availability[row["availability"]] += 1
        if row["availability"] == "observed":
            labels[row["label"]] += 1
            decisions[row["decision"]] += 1
            cells[row["label"], row["decision"]] += 1
    tp, fn = cells["suspicious", "flagged"], cells["suspicious", "not_flagged"]
    fp, tn = cells["benign", "flagged"], cells["benign", "not_flagged"]
    positive_abstentions = cells["suspicious", "abstained"]
    negative_abstentions = cells["benign", "abstained"]
    known = labels["suspicious"] + labels["benign"]

    def ratio(a, b):
        return a / b if b else None

    return dict(
        protocol="synthetic_runtime_accounting_report_v1",
        evidence_level="synthetic_software_only",
        status="accounting_computed" if seen else "no_declared_units",
        input_canonical_sha256=hashlib.sha256(
            json.dumps(document, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        declared_unit_count=len(seen),
        represented_run_count=len(runs),
        availability_counts={name: availability[name] for name in AVAILABILITY},
        observed_label_counts={name: labels[name] for name in LABELS},
        observed_decision_counts={name: decisions[name] for name in DECISIONS},
        observed_cells={
            label: {decision: cells[label, decision] for decision in DECISIONS}
            for label in LABELS
        },
        known_observed_unit_count=known,
        known_decided_unit_count=tp + fn + fp + tn,
        conditional_confusion=dict(tp=tp, fp=fp, tn=tn, fn=fn),
        positive_abstentions=positive_abstentions,
        negative_abstentions=negative_abstentions,
        conditional_metrics=dict(
            precision=ratio(tp, tp + fp),
            recall=ratio(tp, tp + fn),
            false_positive_rate=ratio(fp, fp + tn),
            f1=ratio(2 * tp, 2 * tp + fp + fn),
        ),
        all_known_positive_detection_fraction=ratio(tp, labels["suspicious"]),
        all_known_negative_flag_fraction=ratio(fp, labels["benign"]),
        known_decision_coverage=ratio(tp + fn + fp + tn, known),
        observed_decision_coverage=ratio(
            decisions["flagged"] + decisions["not_flagged"], availability["observed"]
        ),
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
            "Synthetic supplied labels/decisions only; metadata is not authenticated provenance.",
            "Conditional confusion excludes unknown labels, unavailable units and abstentions; all remain counted separately.",
            "Declared units/run IDs are not authenticated coverage, independent groups or a complete planned-run ledger.",
            "No thresholds, model-score conversion, real-data eligibility, human labeling, fitting or detector evaluation.",
            "No confidence intervals, grouped uncertainty, delay, overhead, energy or production-readiness claim.",
        ],
    )
