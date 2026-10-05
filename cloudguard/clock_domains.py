"""Diagnostic time bounds only; no clock correction or baseline acceptance."""

import re
from .clock_check import compare


def redis_bracket(first, last, reply):
    for value in (first, last):
        if any(
            type(value.get(k)) is not int or value[k] < 0
            for k in ("wall_ns", "monotonic_mid_ns", "sampling_span_ns")
        ):
            raise ValueError("invalid clock sample")
    timing = compare(first, last)
    if not timing["within_tolerance"] or timing["elapsed_monotonic_ns"] > 500_000_000:
        raise ValueError("unstable or excessively wide clock bracket")
    parts = reply.splitlines()
    if len(parts) != 2 or any(not re.fullmatch(r"[0-9]{1,10}", p) for p in parts):
        raise ValueError("unexpected Redis TIME response")
    seconds, micros = map(int, parts)
    if not 0 <= seconds < 4133980800 or not 0 <= micros < 1_000_000:
        raise ValueError("Redis TIME outside supported range")
    remote = seconds * 10**9 + micros * 1000
    allowance = timing["sampling_uncertainty_ns"] + abs(timing["clock_difference_ns"])
    low = remote - last["wall_ns"] - allowance
    high = remote + 999 - first["wall_ns"] + allowance
    return dict(
        first=first,
        last=last,
        **timing,
        redis_unix_ns=remote,
        offset_lower_ns=low,
        offset_upper_ns=high,
        zero_within_bounds=low <= 0 <= high,
    )


def summarize(observations, correlation):
    rows = correlation["matches"]
    if len(observations) != 4 or len(rows) != 4:
        raise ValueError("four complete clock-domain observations required")
    ids = [o.get("process_id") for o in observations]
    if any(type(p) is not int or p <= 0 for p in ids) or len(set(ids)) != 4:
        raise ValueError("distinct positive measured IDs required")
    results = []
    for observation, row in zip(observations, rows):
        if observation["process_id"] != row["process_id"]:
            raise ValueError("clock-domain PID mismatch")
        before, after = observation["before"], observation["after"]
        ping = observation["ping_clock"]
        timing = compare(ping["first"], ping["last"])
        if not timing["within_tolerance"] or any(
            type(ping.get(k)) is not type(v) or ping[k] != v for k, v in timing.items()
        ):
            raise ValueError("invalid PING clock bracket")
        for remote in (before, after):
            # Recompute from saved scalar/time fields; do not trust saved flags.
            if type(remote.get("redis_unix_ns")) is not int:
                raise ValueError("invalid Redis time scalar")
            seconds, nanos = divmod(remote["redis_unix_ns"], 10**9)
            if (
                nanos % 1000
                or redis_bracket(
                    remote["first"], remote["last"], f"{seconds}\n{nanos // 1000}"
                )
                != remote
            ):
                raise ValueError("inconsistent Redis bracket")
        if not (
            before["last"]["monotonic_mid_ns"]
            <= ping["first"]["monotonic_mid_ns"]
            < ping["last"]["monotonic_mid_ns"]
            <= after["first"]["monotonic_mid_ns"]
        ):
            raise ValueError("clock-domain command ordering invalid")
        if after["redis_unix_ns"] < before["redis_unix_ns"]:
            raise ValueError("Redis clock moved backwards across PING")
        event = row["event_unix_ns"]
        if type(event) is not int or not 0 <= event < 4133980800 * 10**9:
            raise ValueError("invalid event time scalar")
        allowance = (
            abs(timing["clock_difference_ns"]) + timing["sampling_uncertainty_ns"]
        )
        low = event - ping["last"]["wall_ns"] - allowance
        high = event - ping["first"]["wall_ns"] + allowance
        if (
            low != row["offset_lower_ns"]
            or high != row["offset_upper_ns"]
            or (low <= 0 <= high) != row["zero_within_bounds"]
        ):
            raise ValueError("inconsistent event/harness bounds")
        results.append(
            dict(
                process_id=row["process_id"],
                server_harness_before_zero=before["zero_within_bounds"],
                server_harness_after_zero=after["zero_within_bounds"],
                event_harness_zero=row["zero_within_bounds"],
                event_server_lower_ns=event - after["redis_unix_ns"] - 999,
                event_server_upper_ns=event - before["redis_unix_ns"],
                event_inside_server_bracket=before["redis_unix_ns"]
                <= event
                <= after["redis_unix_ns"] + 999,
            )
        )
    return dict(
        protocol="redis_time_ping_time_v1",
        samples=results,
        correction_applied=False,
        falco_alignment_verified=False,
        independent_evaluation=False,
        limits=[
            "Sequential read bounds assume clock stability between server reads.",
            "No midpoint, constant-offset fit or historical timestamp correction.",
            "Added TIME calls change workload and are excluded from latency/baseline studies.",
            "PID and server identities are local observations, not authentication.",
        ],
    )
