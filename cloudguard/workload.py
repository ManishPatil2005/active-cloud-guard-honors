"""Fixed-duration development PING schedules; not independent labeled workloads."""

import time

PROFILES = {"ping_1": (0,), "ping_4": (0, 1, 2, 3)}


def run(
    profile,
    ping,
    *,
    monotonic_ns=time.monotonic_ns,
    wall_ns=time.time_ns,
    sleep=time.sleep,
):
    if profile not in PROFILES:
        raise ValueError("unsupported fixed workload profile")
    start = monotonic_ns()
    wall_start = wall_ns()
    duration = 4_000_000_000
    calls = []
    failure = None
    for offset in PROFILES[profile]:
        sleep(max(0, (start + offset * 10**9 - monotonic_ns()) / 10**9))
        dispatch = monotonic_ns()
        if dispatch - start >= duration:
            failure = "schedule_overrun"
            break
        result = ping()
        complete = monotonic_ns()
        calls.append(
            dict(
                scheduled_offset_ns=offset * 10**9,
                dispatch_offset_ns=dispatch - start,
                docker_exec_round_trip_ns=complete - dispatch,
                pong=result == "PONG",
            )
        )
        if result != "PONG":
            failure = "workload_failed"
            break
    sleep(max(0, (start + duration - monotonic_ns()) / 10**9))
    elapsed = monotonic_ns() - start
    wall_end = wall_ns()
    drift = (wall_end - wall_start) - elapsed
    if failure is None and (
        abs(drift) > 50_000_000
        or not duration <= elapsed <= duration + 100_000_000
        or any(
            c["dispatch_offset_ns"] - c["scheduled_offset_ns"] > 250_000_000
            for c in calls
        )
    ):
        failure = "timing_outside_tolerance"
    return dict(
        profile=profile,
        scenario_group="redis-ping-development",
        status=failure or "completed",
        start_unix_ns=wall_start,
        end_unix_ns=wall_end,
        elapsed_monotonic_ns=elapsed,
        clock_difference_ns=drift,
        planned_duration_ns=duration,
        calls=calls,
        causal_attribution="not_proven",
        overhead_estimate=None,
    )
