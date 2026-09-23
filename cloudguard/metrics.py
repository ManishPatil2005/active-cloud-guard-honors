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
