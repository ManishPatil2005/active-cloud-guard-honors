"""Provisional monotonic prioritization; not a calibrated probability."""

import math


def score(
    static,
    criticality,
    exposure="not_tested",
    anomaly=None,
    weights=(0.6, 0.2, 0.2),
    beta=0.25,
):
    values = [static, criticality, beta, *weights] + (
        [] if anomaly is None else [anomaly]
    )
    if any(
        not isinstance(v, (int, float))
        or isinstance(v, bool)
        or not math.isfinite(v)
        or not 0 <= v <= 1
        for v in values
    ):
        raise ValueError("all components must be finite numbers in [0,1]")
    if len(weights) != 3 or not math.isclose(sum(weights), 1):
        raise ValueError("three weights must sum to one")
    if exposure not in (
        "reachable",
        "unreachable",
        "inconclusive",
        "not_tested",
        "not_applicable",
    ):
        raise ValueError("invalid exposure state")
    # Unreachable from one vantage never cancels a static finding.
    adjusted = static + beta * (1 - static) if exposure == "reachable" else static
    ws, wa, wc = weights
    if anomaly is None:
        if ws + wc == 0:
            raise ValueError("no observed score components have weight")
        value = (ws * adjusted + wc * criticality) / (ws + wc)
    else:
        value = ws * adjusted + wa * anomaly + wc * criticality
    return dict(
        value=round(value, 6),
        runtime_observed=anomaly is not None,
        exposure=exposure,
        policy="tci-v0.1-provisional",
        calibrated=False,
    )
