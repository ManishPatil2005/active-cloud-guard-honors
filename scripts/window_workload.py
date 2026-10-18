"""Fixed full-window qualification scheduler; live transport integration pending."""

from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.clock_check import compare, sample
from cloudguard.evidence import evidence_main


def definition():
    return dict(
        protocol="redis_ping_window_60s_v1",
        family_id="redis-ping-development",
        duration_ns=60_000_000_000,
        offsets_ns=[second * 1_000_000_000 for second in range(60)],
        dispatch_lateness_limit_ns=250_000_000,
        round_trip_limit_ns=750_000_000,
        end_lateness_limit_ns=100_000_000,
        expected_reply="PONG",
        collector_watchdog_compatible=False,
        live_transport_integrated=False,
        collection_authorized=False,
        independent_evaluation_verified=False,
    )


def _progress_ok(first, current, timing, first_call=False):
    # An identical zero-elapsed initial sample is possible with virtual/coarse
    # clocks. Do not skip a real initial fault merely because the offset is zero.
    return timing["within_tolerance"] or (
        first_call and first == current and first["sampling_span_ns"] <= 5_000_000
    )


def validate_timing(report):
    """Recompute admission from actual endpoints; flags are not timing proof."""
    spec = definition()
    first, last, calls = report["first"], report["last"], report["calls"]

    def checked_sample(value):
        for key in ("wall_ns", "monotonic_mid_ns", "sampling_span_ns"):
            if type(value[key]) is not int or value[key] < 0:
                raise ValueError("invalid clock sample integer")
        if value["sampling_span_ns"] > 5_000_000:
            raise ValueError("clock sample exceeds width limit")
        mid, span = value["monotonic_mid_ns"], value["sampling_span_ns"]
        lower, upper = mid - span // 2, mid + (span + 1) // 2
        if lower < 0:
            raise ValueError("invalid monotonic sample bracket")
        return lower, upper

    checked_sample(first)
    checked_sample(last)
    timing = compare(first, last)
    if (
        report["status"] != "completed"
        or report["workload_timing_accepted"] is not True
        or report["timing"] != timing
        or not timing["within_tolerance"]
        or not spec["duration_ns"]
        <= timing["elapsed_monotonic_ns"]
        <= spec["duration_ns"] + spec["end_lateness_limit_ns"]
        or len(calls) != 60
    ):
        raise ValueError("measured window timing not independently recomputed")
    previous = first
    for index, call in enumerate(calls):
        a, b = call["first"], call["last"]
        _, before_end = checked_sample(a)
        after_start, _ = checked_sample(b)
        for key in ("scheduled_offset_ns", "dispatch_offset_ns", "round_trip_ns"):
            if type(call[key]) is not int or call[key] < 0:
                raise ValueError("invalid transport timing integer")
        dispatch = first["monotonic_mid_ns"] + call["dispatch_offset_ns"]
        complete = dispatch + call["round_trip_ns"]
        local = compare(a, b)
        before, after = compare(first, a), compare(first, b)
        offset = spec["offsets_ns"][index]
        if (
            call["status"] != "completed"
            or call["pong"] is not True
            or not local["within_tolerance"]
            or call["timing"] != local
            or not _progress_ok(first, a, before, index == 0)
            or not after["within_tolerance"]
            or a["monotonic_mid_ns"] < previous["monotonic_mid_ns"]
            or b["monotonic_mid_ns"] > last["monotonic_mid_ns"]
            or call["scheduled_offset_ns"] != offset
            or not offset
            <= call["dispatch_offset_ns"]
            <= offset + spec["dispatch_lateness_limit_ns"]
            or not 0 < call["round_trip_ns"] <= spec["round_trip_limit_ns"]
            or dispatch < before_end
            or complete > after_start
            or ("window_timing" in call and call["window_timing"] != after)
        ):
            raise ValueError("command or cumulative clock evidence rejected")
        previous = b


def run(
    ping, *, monotonic_ns=time.monotonic_ns, wall_ns=time.time_ns, sleep=time.sleep
):
    """Caller must enforce callback deadline; this is not a process supervisor.

    Preserve attempted failures; never catch up missed dispatches, retry, pad
    telemetry, infer labels, or turn timing success into collector coverage.
    """
    if not all(callable(item) for item in (ping, monotonic_ns, wall_ns, sleep)):
        raise ValueError("workload callbacks must be callable")
    spec = definition()
    report = dict(
        protocol=spec["protocol"],
        family_id=spec["family_id"],
        status="started",
        planned_duration_ns=spec["duration_ns"],
        planned_calls=60,
        calls=[],
        first=None,
        last=None,
        timing=None,
        collector_coverage="not_verified",
        independent_evaluation_verified=False,
        labels_created=False,
        overhead_estimate=None,
        callback_deadline_enforcement="caller_required",
        clock_check_protocol="cumulative_window_samples_v3",
        clock_stop=None,
    )
    try:
        first = sample(monotonic_ns, wall_ns)
        report["first"] = first
        start = first["monotonic_mid_ns"]
        for offset in spec["offsets_ns"]:
            sleep(max(0, (start + offset - monotonic_ns()) / 1_000_000_000))
            before = sample(monotonic_ns, wall_ns)
            progress = compare(first, before)
            if not _progress_ok(first, before, progress, offset == 0):
                report.update(
                    status="window_clock_outside_tolerance",
                    clock_stop=dict(
                        phase="before_command",
                        index=len(report["calls"]),
                        first=first,
                        last=before,
                        timing=progress,
                    ),
                )
                break
            dispatch = monotonic_ns()
            if (
                not offset
                <= dispatch - start
                <= offset + spec["dispatch_lateness_limit_ns"]
            ):
                report["status"] = "dispatch_outside_tolerance"
                break
            call = dict(
                scheduled_offset_ns=offset,
                dispatch_offset_ns=dispatch - start,
                first=before,
                last=None,
                timing=None,
                round_trip_ns=None,
                pong=None,
                status="attempted",
            )
            report["calls"].append(call)
            try:
                reply = ping()
            except Exception as error:
                call.update(status="callback_failed", error_type=type(error).__name__)
                report["status"] = "callback_failed"
                break
            complete = monotonic_ns()
            call["round_trip_ns"] = complete - dispatch
            call["pong"] = type(reply) is str and reply == "PONG"
            after = sample(monotonic_ns, wall_ns)
            call["last"] = after
            call["timing"] = compare(before, after)
            if not call["pong"]:
                call["status"] = "unexpected_reply"
            elif not 0 < call["round_trip_ns"] <= spec["round_trip_limit_ns"]:
                call["status"] = "round_trip_outside_tolerance"
            elif not call["timing"]["within_tolerance"]:
                call["status"] = "call_clock_outside_tolerance"
            else:
                call["status"] = "completed"
            # Local command brackets can pass while small changes accumulate
            # beyond the unchanged full-window gate. Never wait until the end
            # (or a later recovery) to notice an already sampled clock fault.
            progress = compare(first, after)
            call["window_timing"] = progress
            if call["status"] == "completed" and not progress["within_tolerance"]:
                call["status"] = "window_clock_outside_tolerance"
                report["clock_stop"] = dict(
                    phase="after_command",
                    index=len(report["calls"]) - 1,
                    first=first,
                    last=after,
                    timing=progress,
                )
            if call["status"] != "completed":
                report["status"] = call["status"]
                break
        if report["status"] == "started":
            sleep(
                max(0, (start + spec["duration_ns"] - monotonic_ns()) / 1_000_000_000)
            )
            report["status"] = "completed"
        last = sample(monotonic_ns, wall_ns)
        report["last"] = last
        timing = compare(first, last)
        report["timing"] = timing
        if report["status"] == "completed" and (
            not timing["within_tolerance"]
            or not spec["duration_ns"]
            <= timing["elapsed_monotonic_ns"]
            <= spec["duration_ns"] + spec["end_lateness_limit_ns"]
        ):
            report["status"] = "window_timing_outside_tolerance"
    except Exception as error:
        report.update(status="scheduler_failed", error_type=type(error).__name__)
    report["attempted_calls"] = len(report["calls"])
    report["completed_calls"] = sum(
        call["status"] == "completed" for call in report["calls"]
    )
    report["unattempted_calls"] = 60 - report["attempted_calls"]
    report["workload_timing_accepted"] = report["status"] == "completed"
    return report


def collect(args):
    # CLI publishes specification only. Never wire a live callback implicitly.
    return {"output": dict(definition=definition(), actions_executed=[])}, 0


if __name__ == "__main__":
    raise SystemExit(evidence_main(collect))
