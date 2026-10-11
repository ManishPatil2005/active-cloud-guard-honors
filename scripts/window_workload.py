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
    )
    try:
        first = sample(monotonic_ns, wall_ns)
        report["first"] = first
        start = first["monotonic_mid_ns"]
        for offset in spec["offsets_ns"]:
            sleep(max(0, (start + offset - monotonic_ns()) / 1_000_000_000))
            before = sample(monotonic_ns, wall_ns)
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
