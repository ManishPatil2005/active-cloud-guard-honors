"""One explicit, journaled Redis/Falco development qualification, never a benchmark."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.clock_check import compare, sample
from cloudguard.correlation import connection_counts
from cloudguard.limits import json_value, read_bytes
from cloudguard.sensor_metrics import summarize
from scripts.window_sensor import SensorLease
from scripts.window_transport import RedisWindowTransport
from scripts.window_workload import run as workload

MINUTE = 60_000_000_000
ALIGNMENT_WAIT_PROTOCOL = "utc_boundary_single_recheck_v2"


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def sources():
    paths = sorted([*ROOT.glob("cloudguard/*.py"), *ROOT.glob("scripts/*.py")])
    paths += [
        ROOT / "testbed/falco-trial.yaml",
        ROOT / "testbed/falco-window.yaml",
        ROOT / "testbed/inventory.json",
    ]
    if not 1 <= len(paths) <= 250:
        raise ValueError("source count outside budget")
    result, total = {}, 0
    for path in paths:
        raw = read_bytes(path)
        total += len(raw)
        if total > 8_000_000:
            raise ValueError("source bytes outside budget")
        result[path.relative_to(ROOT).as_posix()] = digest(raw)
    return result


class Journal:
    """Exclusive, flushed hash-chain checkpoints; trusted local parent required.

    Directory fsync on POSIX only. Neither fsync nor hashes authenticate a host
    or guarantee physical durability on every filesystem. Never auto-resume.
    """

    def __init__(self, directory):
        self.path = Path(directory)
        self.path.mkdir(exist_ok=False)
        self.sequence = 0
        self.previous = None
        self.sealed = False
        self.total = 0
        self._sync_directory(self.path.parent)

    @staticmethod
    def _sync_directory(path):
        if os.name == "posix":
            fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)

    def record(self, phase, payload):
        if self.sealed or self.sequence >= 160:
            raise ValueError("journal sealed or exhausted")
        record = dict(
            sequence=self.sequence,
            previous_sha256=self.previous,
            phase=phase,
            payload=payload,
        )
        raw = (json.dumps(record, sort_keys=True, allow_nan=False) + "\n").encode()
        if len(raw) > 300_000 or self.total + len(raw) > 4_000_000:
            raise ValueError("journal byte budget exceeded")
        with (self.path / f"{self.sequence:03d}.json").open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        self._sync_directory(self.path)
        self.previous = digest(raw)
        self.sequence += 1
        self.total += len(raw)
        self.sealed = phase == "terminal"


def review_journal(directory):
    """Read-only structural recovery: incomplete/invalid means operator review."""
    path = Path(directory)
    rows, previous, total = [], None, 0
    try:
        files = sorted(path.iterdir())
        if not 1 <= len(files) <= 160:
            raise ValueError("journal count")
        for index, file in enumerate(files):
            if file.name != f"{index:03d}.json" or file.is_symlink():
                raise ValueError("journal sequence")
            raw = read_bytes(file, limit=300_000)
            total += len(raw)
            if total > 4_000_000:
                raise ValueError("journal budget")
            row = json_value(raw.decode("utf-8"))
            if (
                set(row) != {"sequence", "previous_sha256", "phase", "payload"}
                or type(row["sequence"]) is not int
                or row["sequence"] != index
                or row["previous_sha256"] != previous
                or type(row["phase"]) is not str
                or not isinstance(row["payload"], dict)
                or (rows and rows[-1]["phase"] == "terminal")
            ):
                raise ValueError("journal chain")
            rows.append(row)
            previous = digest(raw)
        complete = rows[0]["phase"] == "intent" and rows[-1]["phase"] == "terminal"
        return dict(
            status="terminal_record_present" if complete else "incomplete",
            valid_records=len(rows),
            last=rows[-1],
            operator_review_required=not complete,
            authenticated=False,
            actions_executed=[],
        )
    except (ValueError, OSError, TypeError, KeyError):
        return dict(
            status="invalid",
            valid_records=len(rows),
            last=rows[-1] if rows else None,
            operator_review_required=True,
            authenticated=False,
            actions_executed=[],
        )


def check_capture(
    raw, metrics_path, metrics_sha, target, warmup_pids, transport, measured, boundary
):
    """Recompute checks on saved evidence; never certify all telemetry or labels."""
    attempts = transport["attempts"]
    calls = measured["calls"]
    pids = [row["pid"] for row in attempts]
    if (
        len(pids) != 60
        or len(calls) != 60
        or measured["workload_timing_accepted"] is not True
        or transport["fault"] is not None
        or transport["before"] != transport["after"]
        or any(row["status"] != "completed" for row in attempts)
    ):
        raise ValueError("incomplete workload or unstable identity")
    matches, unassigned = connection_counts(raw, target, warmup_pids + pids)
    offsets = []
    for pid, call in zip(pids, calls):
        if len(matches[pid]) != 1 or call["status"] != "completed":
            raise ValueError("missing or ambiguous measured connect")
        timing = compare(call["first"], call["last"])
        if not timing["within_tolerance"]:
            raise ValueError("command clock disagreement")
        stamp = matches[pid][0]
        allowance = (
            abs(timing["clock_difference_ns"]) + timing["sampling_uncertainty_ns"]
        )
        low = stamp - call["last"]["wall_ns"] - allowance
        high = stamp - call["first"]["wall_ns"] + allowance
        if not low <= 0 <= high or not boundary <= stamp < boundary + MINUTE:
            raise ValueError("collector event outside command or UTC window")
        offsets.append(dict(pid=pid, event_ns=stamp, lower_ns=low, upper_ns=high))
    if len(matches[warmup_pids[-1]]) != 1:
        raise ValueError("readiness event lost from final export")
    metric = summarize(metrics_path, metrics_sha)
    metric_raw = read_bytes(metrics_path, limit=1_000_000)
    if digest(metric_raw) != metrics_sha:
        raise ValueError("metrics changed during review")
    timestamps = [
        json_value(line)["output_fields"]["evt.time"]
        for line in metric_raw.decode("utf-8").splitlines()
    ]
    if (
        timestamps[0] > boundary
        or timestamps[-1] < boundary + MINUTE
        or any(b - a > 2_500_000_000 for a, b in zip(timestamps, timestamps[1:]))
        or any(
            metric["observed_counter_deltas"][key] != 0
            for key in ("scap.n_drops", "falco.outputs_queue_num_drops")
        )
    ):
        raise ValueError("unbracketed metrics, excessive gap or reported drops")
    return dict(
        status="selected_development_checks_passed",
        matched_commands=60,
        utc_start_ns=boundary,
        utc_end_ns=boundary + MINUTE,
        command_event_offsets=offsets,
        metrics=metric,
        unassigned_connect_count=unassigned,
        full_telemetry_completeness_verified=False,
        independent_evaluation_verified=False,
    )


def wait_alignment(
    first,
    boundary,
    *,
    monotonic_ns=time.monotonic_ns,
    wall_ns=time.time_ns,
    sleep=time.sleep,
):
    """Return all sampled evidence before the caller decides whether to reject."""
    deadline = first["monotonic_mid_ns"] + boundary - first["wall_ns"]
    while monotonic_ns() < deadline:
        sleep(min(0.5, max(0, (deadline - monotonic_ns()) / 1e9)))
    last = sample(monotonic_ns, wall_ns)
    timing = compare(first, last)
    error = last["wall_ns"] - boundary
    repair = None
    # A small backward wall adjustment can leave the original monotonic deadline
    # early even when the clock-consistency gate passes. Wait once for the actual
    # boundary; retain both samples and reapply every original gate afterward.
    if timing["within_tolerance"] and -50_000_000 <= error < 0:
        repair = dict(
            initial_last=last,
            initial_timing=timing,
            initial_boundary_error_ns=error,
            extra_wait_ns=-error,
            maximum_extra_wait_ns=50_000_000,
        )
        corrected_deadline = last["monotonic_mid_ns"] - error
        while monotonic_ns() < corrected_deadline:
            sleep(max(0, (corrected_deadline - monotonic_ns()) / 1e9))
        last = sample(monotonic_ns, wall_ns)
        timing = compare(first, last)
        error = last["wall_ns"] - boundary
    reasons = []
    if not timing["within_tolerance"]:
        reasons.append("clock_disagreement")
    if not 0 <= error <= 100_000_000:
        reasons.append("utc_boundary_outside_tolerance")
    result = dict(
        wait_protocol=ALIGNMENT_WAIT_PROTOCOL,
        first=first,
        last=last,
        boundary_ns=boundary,
        timing=timing,
        boundary_error_ns=error,
        accepted=not reasons,
        reasons=reasons,
    )
    if repair is not None:
        result["deadline_repair"] = repair
    return result


def alignment_diagnostic(directory):
    """One sensor-free clock observation, no Docker/service/workload operations."""
    journal = Journal(directory)
    frozen = sources()
    first = sample()
    boundary = (first["wall_ns"] // MINUTE + 1) * MINUTE
    journal.record(
        "intent",
        dict(
            protocol="sensor_free_window_alignment_v1",
            first=first,
            boundary_ns=boundary,
            source_sha256=frozen,
            actions_executed=[],
        ),
    )
    try:
        result = wait_alignment(first, boundary)
        journal.record("alignment_result", result)
        unchanged = frozen == sources()
        report = dict(
            status="alignment_observed"
            if result["accepted"] and unchanged
            else "rejected",
            alignment=result,
            source_unchanged=unchanged,
            sensor_or_workload_executed=False,
            historical_cause_resolved=False,
        )
    except (Exception, KeyboardInterrupt) as error:
        report = dict(
            status="rejected",
            error_type=type(error).__name__,
            sensor_or_workload_executed=False,
            historical_cause_resolved=False,
        )
    journal.record("terminal", report)
    return report


def execute(
    directory,
    target,
    endpoint,
    *,
    approved=False,
    lease_factory=SensorLease,
    transport_factory=RedisWindowTransport,
    monotonic_ns=time.monotonic_ns,
    wall_ns=time.time_ns,
    sleep=time.sleep,
):
    if approved is not True:
        raise ValueError("explicit operational approval required")
    journal = Journal(directory)  # Refuse reuse before any external operation.
    lease = None
    report = dict(
        protocol="redis_window_trial_v2",
        status="started",
        independent_evaluation_verified=False,
        labels_created=False,
        complete_telemetry_verified=False,
        faults=[],
        workload=None,
        capture_checks=None,
        source_sha256=None,
        source_unchanged=False,
    )

    def clock():
        return sample(monotonic_ns, wall_ns)

    def save(phase, payload):
        journal.record(phase, payload)

    try:
        frozen = sources()
        lease = lease_factory(target, endpoint)
        report["source_sha256"] = frozen
        save(
            "intent",
            dict(
                protocol=report["protocol"],
                source_sha256=frozen,
                lease=lease.snapshot(),
                approved_by_operator=True,
                workload_calls=60,
                readiness_calls=2,
                independent_evaluation_verified=False,
            ),
        )
        lease.start(approved=True)
        save("sensor_started", lease.snapshot())
        ready_start = clock()
        for number in range(2):
            save("canary_intent", dict(index=number))
            first = clock()
            pong = lease.redis.ping()
            last = clock()
            save(
                "canary_result",
                dict(
                    index=number,
                    first=first,
                    last=last,
                    transport=lease.redis.snapshot(),
                ),
            )
            if pong != "PONG" or not compare(first, last)["within_tolerance"]:
                raise ValueError("canary command rejected")
            sleep(1)
        raw = lease.observe_log()
        warmup = [row["pid"] for row in lease.redis.snapshot()["attempts"]]
        matches, _ = connection_counts(raw, target, warmup)
        ready_end = clock()
        if (
            len(matches[warmup[-1]]) != 1
            or not compare(ready_start, ready_end)["within_tolerance"]
            or ready_end["monotonic_mid_ns"] - ready_start["monotonic_mid_ns"]
            > 10_000_000_000
        ):
            raise ValueError("canary readiness not qualified")
        canary_timing = compare(first, last)
        allowance = (
            abs(canary_timing["clock_difference_ns"])
            + canary_timing["sampling_uncertainty_ns"]
        )
        if (
            not first["wall_ns"] - allowance
            <= matches[warmup[-1]][0]
            <= last["wall_ns"] + allowance
        ):
            raise ValueError("readiness event outside command clock bracket")
        save(
            "ready",
            dict(
                warmup_pids=warmup,
                snapshot_sha256=digest(raw),
                first=first,
                last=last,
                event_ns=matches[warmup[-1]][0],
            ),
        )
        client = transport_factory(target, endpoint)
        before = client.check_identity()
        if before != lease.redis.snapshot()["before"]:
            raise ValueError("target changed during readiness")
        phase_first = clock()
        boundary = (phase_first["wall_ns"] // MINUTE + 1) * MINUTE
        save("alignment_intent", dict(first=phase_first, boundary_ns=boundary))
        # Bound each sleep so a wall adjustment cannot create an unbounded wait.
        alignment = wait_alignment(
            phase_first,
            boundary,
            monotonic_ns=monotonic_ns,
            wall_ns=wall_ns,
            sleep=sleep,
        )
        save("alignment_result", alignment)
        report["alignment"] = alignment
        if not alignment["accepted"]:
            raise ValueError("UTC alignment rejected")

        def ping():
            save("ping_intent", dict(index=len(client.snapshot()["attempts"])))
            try:
                return client.ping()
            finally:
                save("ping_result", client.snapshot())

        report["workload"] = workload(
            ping, monotonic_ns=monotonic_ns, wall_ns=wall_ns, sleep=sleep
        )
        report["transport"] = client.snapshot()
        save(
            "workload_result",
            dict(workload=report["workload"], transport=report["transport"]),
        )
        if report["workload"]["workload_timing_accepted"] is not True:
            raise ValueError("workload timing rejected")
        client.check_identity()
        report["transport"] = client.snapshot()
        sleep(2)  # Fixed tail for metric bracketing; not an adaptive retry.
        report.update(
            status="collected_pending_review", boundary_ns=boundary, warmup_pids=warmup
        )
    except (Exception, KeyboardInterrupt) as error:
        report.update(status="rejected")
        report["faults"].append(dict(phase="collection", code=type(error).__name__))
    finally:
        # Failed storage must never suppress an owned cleanup attempt.
        try:
            save("cleanup_intent", lease.snapshot() if lease else {})
        except (Exception, KeyboardInterrupt) as error:
            report["status"] = "rejected"
            report["faults"].append(dict(phase="journal", code=type(error).__name__))
        if lease is not None:
            try:
                report["lease"] = lease.cleanup()
            except (Exception, KeyboardInterrupt) as error:
                report["status"] = "rejected"
                report["faults"].append(
                    dict(phase="cleanup", code=type(error).__name__)
                )
    try:
        report["source_unchanged"] = report["source_sha256"] == sources()
        if report["status"] == "collected_pending_review":
            if (
                not report["source_unchanged"]
                or report["lease"]["cleanup_verified"] is not True
            ):
                raise ValueError("source change or unverified cleanup")
            raw_dir = Path(report["lease"]["recovery"]["raw_directory"])
            raw = read_bytes(raw_dir / "sensor.log", limit=1_000_000)
            if digest(raw) != report["lease"]["raw_log_sha256"]:
                raise ValueError("raw capture hash mismatch")
            report["capture_checks"] = check_capture(
                raw,
                raw_dir / "metrics.jsonl",
                report["lease"]["metrics_raw_sha256"],
                target,
                report["warmup_pids"],
                report["transport"],
                report["workload"],
                report["boundary_ns"],
            )
            report["status"] = "development_checks_passed"
    except (Exception, KeyboardInterrupt) as error:
        report["status"] = "rejected"
        report["faults"].append(dict(phase="review", code=type(error).__name__))
    try:
        save("terminal", report)
    except (Exception, KeyboardInterrupt):
        report["status"] = "journal_failed_operator_review_required"
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--directory", required=True, help="Fresh private journal directory"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--review-only", action="store_true")
    mode.add_argument("--alignment-only", action="store_true")
    parser.add_argument("--target")
    parser.add_argument("--endpoint")
    parser.add_argument("--approve-development-trial", action="store_true")
    args = parser.parse_args()
    try:
        if args.review_only:
            result = review_journal(args.directory)
            print(json.dumps(result))
            return 0 if result["status"] == "terminal_record_present" else 1
        if args.alignment_only:
            result = alignment_diagnostic(args.directory)
            print(
                json.dumps(
                    dict(status=result["status"], sensor_or_workload_executed=False)
                )
            )
            return 0 if result["status"] == "alignment_observed" else 1
        if sys.platform != "linux" or not args.approve_development_trial:
            raise ValueError(
                "Linux and explicit reviewed development approval required"
            )
        # Journals can contain private raw locations and must stay excluded.
        parent = (ROOT / "output/runtime-raw").resolve()
        path = Path(args.directory).absolute()
        if path.parent.resolve() != parent:
            raise ValueError("journal must be a fresh child of output/runtime-raw")
        result = execute(path, args.target, args.endpoint, approved=True)
        print(
            json.dumps(
                dict(status=result["status"], independent_evaluation_verified=False)
            )
        )
        return 0 if result["status"] == "development_checks_passed" else 1
    except (Exception, KeyboardInterrupt) as error:
        print(
            json.dumps(
                dict(status="refused_or_failed", error_type=type(error).__name__)
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
