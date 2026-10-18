"""Metrics on independent case IDs, with explicit undefined denominators."""

import math


def metrics(labels, predictions):
    if set(labels) != set(predictions):
        raise ValueError("prediction IDs must exactly match labels")
    if any(type(v) is not bool for v in [*labels.values(), *predictions.values()]):
        raise ValueError("labels must be booleans")
    tp = sum(labels[k] and predictions[k] for k in labels)
    fp = sum(not labels[k] and predictions[k] for k in labels)
    fn = sum(labels[k] and not predictions[k] for k in labels)
    tn = sum(not labels[k] and not predictions[k] for k in labels)

    def ratio(a, b):
        return a / b if b else None

    def wilson(success, n):
        if not n:
            return None
        z = 1.959963984540054
        p = success / n
        den = 1 + z * z / n
        mid = (p + z * z / (2 * n)) / den
        width = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
        return [max(0, mid - width), min(1, mid + width)]

    return dict(
        n=len(labels),
        tp=tp,
        fp=fp,
        fn=fn,
        tn=tn,
        precision=ratio(tp, tp + fp),
        recall=ratio(tp, tp + fn),
        f1=ratio(2 * tp, 2 * tp + fp + fn),
        false_positive_rate=ratio(fp, fp + tn),
        precision_wilson95=wilson(tp, tp + fp),
        recall_wilson95=wilson(tp, tp + fn),
    )


def fp_reduction(before, after):
    if before < 0 or after < 0:
        raise ValueError("counts cannot be negative")
    return None if before == 0 else (before - after) / before


def rule_metrics(labels, predictions):
    """Exact case/rule micro accounting, not asset/location or actionability truth.

    Inputs are normalized unique rule lists for the same complete case inventory.
    There is no declared universe of negative rules, so TN/FPR are undefined.
    """
    for mapping in (labels, predictions):
        if type(mapping) is not dict or not mapping or len(mapping) > 10000:
            raise ValueError("rule accounting requires a bounded nonempty case mapping")
        for case, rules in mapping.items():
            if type(case) is not str or not case.strip() or len(case) > 1024:
                raise ValueError("invalid case identity")
            if type(rules) is not list or len(rules) > 1000:
                raise ValueError("rules must be a bounded normalized list")
            if any(
                type(rule) is not str or not rule.strip() or len(rule) > 256
                for rule in rules
            ) or len(set(rules)) != len(rules):
                raise ValueError("rule identities must be nonempty unique strings")
    if labels.keys() != predictions.keys():
        raise ValueError("prediction IDs must exactly match labels")
    counts = {}
    exact = 0
    for case, expected in labels.items():
        expected, actual = set(expected), set(predictions[case])
        exact += expected == actual
        for rule in sorted(expected | actual):
            row = counts.setdefault(rule, dict(tp=0, fp=0, fn=0))
            key = (
                "tp"
                if rule in expected and rule in actual
                else "fp"
                if rule in actual
                else "fn"
            )
            row[key] += 1
    totals = {
        key: sum(row[key] for row in counts.values()) for key in ("tp", "fp", "fn")
    }
    tp, fp, fn = (totals[key] for key in ("tp", "fp", "fn"))
    return dict(
        unit="case_id_and_rule_id",
        aggregation="micro",
        cases=len(labels),
        exact_match_cases=exact,
        mismatched_cases=len(labels) - exact,
        expected_instances=tp + fn,
        predicted_instances=tp + fp,
        **totals,
        precision=tp / (tp + fp) if tp + fp else None,
        recall=tp / (tp + fn) if tp + fn else None,
        f1=2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None,
        tn=None,
        false_positive_rate=None,
        per_rule={rule: counts[rule] for rule in sorted(counts)},
        limitations=[
            "Case/rule presence collapses repeated assets and locations within a case.",
            "No declared negative-rule universe: TN and false-positive rate undefined.",
            "No independent labels, actionability, uncertainty or calibrated scores established.",
        ],
    )
