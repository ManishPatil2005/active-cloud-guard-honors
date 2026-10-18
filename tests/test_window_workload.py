"""Virtual-clock tests; no Redis/Falco workload is launched."""

import pytest

from scripts.window_workload import collect, definition, run, validate_timing


class Clock:
    def __init__(self):
        self.now = 0
        self.wall_offset = 10**18
        self.calls = 0
        self.sleeps = 0

    def mono(self):
        return self.now

    def wall(self):
        return self.now + self.wall_offset

    def sleep(self, seconds):
        self.sleeps += 1
        self.now += round(seconds * 10**9)

    def ping(self):
        self.calls += 1
        self.now += 10_000_000
        return "PONG"

    def execute(self, ping=None, sleep=None):
        return run(
            ping or self.ping,
            monotonic_ns=self.mono,
            wall_ns=self.wall,
            sleep=sleep or self.sleep,
        )


def test_full_window_keeps_coverage_and_labels_unverified():
    clock = Clock()
    report = clock.execute()
    assert report["status"] == "completed"
    assert report["attempted_calls"] == report["completed_calls"] == 60
    assert report["unattempted_calls"] == 0
    assert report["timing"]["elapsed_monotonic_ns"] == 60 * 10**9
    assert [row["dispatch_offset_ns"] for row in report["calls"]] == definition()[
        "offsets_ns"
    ]
    assert report["collector_coverage"] == "not_verified"
    assert report["labels_created"] is False
    assert report["independent_evaluation_verified"] is False
    assert report["overhead_estimate"] is None


@pytest.mark.parametrize("reply", [None, False, [], "ERROR", "PONG\n"])
def test_wrong_reply_stops_without_padding_or_retry(reply):
    clock = Clock()

    def ping():
        clock.ping()
        return reply

    report = clock.execute(ping)
    assert report["status"] == "unexpected_reply"
    assert report["attempted_calls"] == 1
    assert report["unattempted_calls"] == 59
    assert clock.now == 10_000_000


def test_callback_exception_retains_attempt_not_private_message():
    clock = Clock()

    def ping():
        raise TimeoutError("private diagnostic must not leak")

    report = clock.execute(ping)
    assert report["status"] == "callback_failed"
    assert report["calls"][0]["error_type"] == "TimeoutError"
    assert report["calls"][0]["pong"] is None
    assert "private diagnostic" not in str(report)
    assert report["unattempted_calls"] == 59


def test_late_dispatch_does_not_catch_up():
    clock = Clock()

    def sleep(seconds):
        clock.sleep(seconds)
        if clock.sleeps == 2:
            clock.now += 250_000_001

    report = clock.execute(sleep=sleep)
    assert report["status"] == "dispatch_outside_tolerance"
    assert clock.calls == 1
    assert report["unattempted_calls"] == 59


@pytest.mark.parametrize("duration", [0, -1, 750_000_001, 61 * 10**9])
def test_round_trip_budget_failure_retained(duration):
    clock = Clock()

    def ping():
        clock.now += duration
        return "PONG"

    report = clock.execute(ping)
    assert report["status"] == "round_trip_outside_tolerance"
    assert report["attempted_calls"] == 1
    assert report["workload_timing_accepted"] is False


def test_transient_call_clock_jump_rejected():
    clock = Clock()

    def ping():
        result = clock.ping()
        clock.wall_offset += 50_000_001
        return result

    report = clock.execute(ping)
    assert report["status"] == "call_clock_outside_tolerance"
    assert report["attempted_calls"] == 1


@pytest.mark.parametrize("mode", ["late_end", "clock_end", "sleep_exception"])
def test_window_end_failure_or_exception_never_accepted(mode):
    clock = Clock()

    def sleep(seconds):
        clock.sleep(seconds)
        if clock.sleeps == 61:
            if mode == "late_end":
                clock.now += 100_000_001
            elif mode == "clock_end":
                clock.wall_offset += 50_000_001
            else:
                raise RuntimeError("private")

    report = clock.execute(sleep=sleep)
    assert report["status"] != "completed"
    assert report["completed_calls"] == 60
    assert report["workload_timing_accepted"] is False
    assert "private" not in str(report)


@pytest.mark.parametrize("name", ["ping", "monotonic_ns", "wall_ns", "sleep"])
def test_bad_callbacks_refused_before_activity(name):
    clock = Clock()
    args = dict(
        ping=clock.ping, monotonic_ns=clock.mono, wall_ns=clock.wall, sleep=clock.sleep
    )
    args[name] = None
    with pytest.raises(ValueError):
        run(**args)
    assert clock.calls == clock.sleeps == 0


def test_specification_cli_does_not_launch_workload():
    reports, code = collect(None)
    assert code == 0
    assert reports["output"]["actions_executed"] == []
    spec = reports["output"]["definition"]
    assert spec["collector_watchdog_compatible"] is False
    assert spec["live_transport_integrated"] is False
    assert spec["collection_authorized"] is False


@pytest.mark.parametrize("step", [-5_000_000, 5_000_000])
def test_cumulative_clock_drift_stops_before_sixty_calls(step):
    clock = Clock()

    def ping():
        result = clock.ping()
        clock.wall_offset += step
        return result

    report = clock.execute(ping)
    assert report["status"] == "window_clock_outside_tolerance"
    assert report["attempted_calls"] == 11
    assert report["completed_calls"] == 10
    assert report["unattempted_calls"] == 49
    assert report["clock_stop"]["phase"] == "after_command"
    assert report["clock_stop"]["timing"]["clock_difference_ns"] == 11 * step
    assert report["workload_timing_accepted"] is False


@pytest.mark.parametrize("step", [-50_000_001, 50_000_001])
def test_between_call_clock_fault_is_not_hidden_by_later_recovery(step):
    clock = Clock()

    def sleep(seconds):
        clock.sleep(seconds)
        if clock.sleeps == 10:
            clock.wall_offset += step
        if clock.sleeps == 11:
            clock.wall_offset -= step

    report = clock.execute(sleep=sleep)
    assert report["status"] == "window_clock_outside_tolerance"
    assert clock.calls == 9
    assert report["clock_stop"]["phase"] == "before_command"
    assert report["clock_stop"]["index"] == 9


@pytest.mark.parametrize("step", [-50_000_001, 50_000_001])
def test_clock_fault_before_first_command_never_calls_callback(step):
    clock = Clock()

    def sleep(seconds):
        clock.sleep(seconds)
        clock.now += 1_000
        clock.wall_offset += step

    report = clock.execute(sleep=sleep)
    assert report["status"] == "window_clock_outside_tolerance"
    assert clock.calls == 0
    assert report["clock_stop"]["index"] == 0


@pytest.mark.parametrize("step", [-50_000_000, 50_000_000])
def test_initial_clock_limit_is_not_silently_tightened(step):
    clock = Clock()

    def sleep(seconds):
        clock.sleep(seconds)
        if clock.sleeps == 1:
            clock.now += 1_000
            clock.wall_offset += step

    report = clock.execute(sleep=sleep)
    assert report["workload_timing_accepted"] is True
    assert report["completed_calls"] == 60


@pytest.mark.parametrize(
    "fault", ["negative_span", "boolean_span", "fake_dispatch", "fake_rtt"]
)
def test_receipt_clock_numbers_and_transport_brackets_must_be_consistent(fault):
    report = Clock().execute()
    call = report["calls"][0]
    if fault == "negative_span":
        report["first"]["sampling_span_ns"] = -1
    elif fault == "boolean_span":
        report["first"]["sampling_span_ns"] = False
    elif fault == "fake_dispatch":
        call["dispatch_offset_ns"] = 200_000_000
    else:
        call["round_trip_ns"] = 700_000_000
    with pytest.raises(ValueError):
        validate_timing(report)


def test_unmodified_virtual_clock_receipt_is_admissible():
    validate_timing(Clock().execute())


@pytest.mark.parametrize("key", ["wall_ns", "monotonic_mid_ns", "sampling_span_ns"])
@pytest.mark.parametrize("bad", [True, -1, 0.5])
def test_each_clock_sample_requires_nonnegative_integer_nanoseconds(key, bad):
    report = Clock().execute()
    report["calls"][20]["last"][key] = bad
    with pytest.raises(ValueError):
        validate_timing(report)


@pytest.mark.parametrize(
    "key", ["scheduled_offset_ns", "dispatch_offset_ns", "round_trip_ns"]
)
def test_boolean_transport_numbers_are_not_nanoseconds(key):
    report = Clock().execute()
    report["calls"][0][key] = False if key != "round_trip_ns" else True
    with pytest.raises(ValueError):
        validate_timing(report)


def test_realistic_odd_width_sampling_brackets_remain_admissible():
    clock = Clock()

    def mono():
        clock.now += 1001
        return clock.now

    report = run(clock.ping, monotonic_ns=mono, wall_ns=clock.wall, sleep=clock.sleep)
    assert report["workload_timing_accepted"] is True
    assert report["first"]["sampling_span_ns"] == 1001
    validate_timing(report)
