import json

import pytest

from cloudguard import boot_clock
from scripts import sensor_trial
from tests.test_clock_bridge import point


@pytest.mark.parametrize("rejected", [False, True])
def test_time_boot_endpoints_retained_before_clock_validation(monkeypatch, rejected):
    shift = 60_000_000 if rejected else 0
    clocks = iter([point(10**9, 0), point(1_010_000_000 + shift, 10_000_000)])
    boots = iter(
        [
            boot_clock.bounds(0, 10**9, 1),
            boot_clock.bounds(10_000_000, 1_010_000_000 + shift, 10_000_001),
        ]
    )
    monkeypatch.setattr(sensor_trial, "sample", lambda: next(clocks))
    monkeypatch.setattr(sensor_trial.boot_clock, "sample", lambda: next(boots))
    monkeypatch.setattr(sensor_trial, "command", lambda *args, **kwargs: "1\n5000")
    attempts = []
    if rejected:
        with pytest.raises(ValueError):
            sensor_trial.read_time("a" * 64, attempts, "before", boot=True)
    else:
        sensor_trial.read_time("a" * 64, attempts, "before", boot=True)
    attempt = attempts[0]
    first, last = (
        boot_clock.checked(attempt["boot_before"]),
        boot_clock.checked(attempt["boot_after"]),
    )
    low = last["offset_lower_ns"] - first["offset_upper_ns"]
    high = last["offset_upper_ns"] - first["offset_lower_ns"]
    assert (low, high) == (shift - 1, shift + 1)
    assert attempt["clock_comparison"]["clock_difference_ns"] == shift
    assert attempt["status"] == ("failed" if rejected else "accepted")


@pytest.mark.parametrize("stage", ["first", "last"])
def test_boot_sampling_failure_preserves_safe_stage(monkeypatch, stage):
    clocks = iter([point(10**9, 0), point(1_010_000_000, 10_000_000)])
    monkeypatch.setattr(sensor_trial, "sample", lambda: next(clocks))
    monkeypatch.setattr(sensor_trial, "command", lambda *args, **kwargs: "1\n5000")
    calls = []

    def boot_sample():
        calls.append(True)
        if stage == "first" or len(calls) == 2:
            raise ValueError("private diagnostic details")
        return boot_clock.bounds(0, 10**9, 1)

    monkeypatch.setattr(sensor_trial.boot_clock, "sample", boot_sample)
    attempts = []
    with pytest.raises(ValueError):
        sensor_trial.read_time("a" * 64, attempts, "before", boot=True)
    attempt = attempts[0]
    assert attempt["failed_stage"] == f"sampling_boot_{stage}"
    assert "private diagnostic details" not in json.dumps(attempt)
    assert ("last" in attempt) is (stage == "last")
    assert "boot_after" not in attempt


def test_clocked_ping_records_six_boot_sandwiches(monkeypatch):
    ticks = iter([point(10**9 + i * 10_000_000, i * 10_000_000) for i in range(6)])
    boots = iter(
        [
            boot_clock.bounds(
                i * 10_000_000, 10**9 + i * 10_000_000, i * 10_000_000 + 1
            )
            for i in range(6)
        ]
    )
    monkeypatch.setattr(sensor_trial, "sample", lambda: next(ticks))
    monkeypatch.setattr(sensor_trial.boot_clock, "sample", lambda: next(boots))
    monkeypatch.setattr(
        sensor_trial,
        "command",
        lambda *args, **kwargs: "1\n5000" if args[-1] == "TIME" else "42\nPONG",
    )
    attempts, ids = [], []
    assert sensor_trial.clocked_ping("a" * 64, ids, attempts, boot=True) == "PONG"
    o = attempts[0]
    assert ids == [42] and len(o["time_read_attempts"]) == 2
    assert all(
        "boot_before" in a and "boot_after" in a for a in o["time_read_attempts"]
    )
    assert "boot_before" in o and "boot_after" in o
