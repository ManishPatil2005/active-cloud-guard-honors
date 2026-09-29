"""Bracket wall-clock reads to expose sampling uncertainty, without clock changes."""

import time


def sample(monotonic_ns=time.monotonic_ns, wall_ns=time.time_ns):
    before = monotonic_ns()
    wall = wall_ns()
    after = monotonic_ns()
    if after < before:
        raise ValueError("monotonic clock moved backwards")
    return dict(
        wall_ns=wall,
        monotonic_mid_ns=(before + after) // 2,
        sampling_span_ns=after - before,
    )


def compare(first, last):
    elapsed = last["monotonic_mid_ns"] - first["monotonic_mid_ns"]
    difference = last["wall_ns"] - first["wall_ns"] - elapsed
    uncertainty = (first["sampling_span_ns"] + last["sampling_span_ns"] + 1) // 2
    return dict(
        elapsed_monotonic_ns=elapsed,
        clock_difference_ns=difference,
        sampling_uncertainty_ns=uncertainty,
        within_tolerance=elapsed > 0
        and abs(difference) + uncertainty <= 50_000_000
        and max(first["sampling_span_ns"], last["sampling_span_ns"]) <= 5_000_000,
    )
