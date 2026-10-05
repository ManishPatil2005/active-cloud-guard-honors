import copy
import sys
import json
from pathlib import Path

import pytest

from cloudguard.clock_domains import redis_bracket, summarize
from cloudguard.clock_check import compare
from scripts import sensor_trial
from scripts.repeat_readiness import accept
from tests.test_clock_bridge import point


def observations(offset=0, event_offset=0):
    records, matches = [], []
    for pid in range(1, 5):
        start = pid * 10**9
        before = redis_bracket(
            point(start, start),
            point(start + 100_000_000, start + 100_000_000),
            f"{pid}\n{(50_000_000 + offset) // 1000}",
        )
        after = redis_bracket(
            point(start + 300_000_000, start + 300_000_000),
            point(start + 400_000_000, start + 400_000_000),
            f"{pid}\n{(350_000_000 + offset) // 1000}",
        )
        first, last = (
            point(start + 100_000_000, start + 100_000_000),
            point(start + 200_000_000, start + 200_000_000),
        )
        event = start + 150_000_000 + event_offset
        low, high = event - last["wall_ns"], event - first["wall_ns"]
        records.append(
            dict(
                process_id=pid,
                before=before,
                after=after,
                ping_clock=dict(first=first, last=last, **compare(first, last)),
            )
        )
        matches.append(
            dict(
                process_id=pid,
                event_unix_ns=event,
                offset_lower_ns=low,
                offset_upper_ns=high,
                zero_within_bounds=low <= 0 <= high,
            )
        )
    return records, dict(matches=matches)


@pytest.mark.parametrize(
    "server_offset,event_offset,server_ok,harness_ok",
    [
        (0, 0, True, True),
        (0, -800_000_000, False, False),
        (200_000_000, 200_000_000, True, False),
    ],
)
def test_separate_clock_domains(server_offset, event_offset, server_ok, harness_ok):
    records, correlation = observations(server_offset, event_offset)
    result = summarize(records, correlation)
    assert all(s["event_inside_server_bracket"] == server_ok for s in result["samples"])
    assert all(s["event_harness_zero"] == harness_ok for s in result["samples"])
    assert result["correction_applied"] is False
    assert result["falco_alignment_verified"] is False


@pytest.mark.parametrize(
    "mode", ["partial", "duplicate", "pid", "flag", "bounds", "order", "backwards"]
)
def test_saved_inconsistency_rejected(mode):
    records, correlation = observations()
    if mode == "partial":
        records.pop()
    elif mode == "duplicate":
        records[1]["process_id"] = 1
    elif mode == "pid":
        correlation["matches"][0]["process_id"] = 99
    elif mode == "flag":
        records[0]["before"]["zero_within_bounds"] = False
    elif mode == "bounds":
        correlation["matches"][0]["offset_lower_ns"] += 1
    elif mode == "order":
        records[0]["after"] = copy.deepcopy(records[0]["before"])
    else:
        records[0]["after"] = redis_bracket(
            point(1_300_000_000, 1_300_000_000),
            point(1_400_000_000, 1_400_000_000),
            "0\n900000",
        )
    with pytest.raises(ValueError):
        summarize(records, correlation)


@pytest.mark.parametrize(
    "protocol",
    [
        "container_pid_connect_clock_v1",
        "container_pid_connect_boot_v1",
        "container_pid_connect_boot_v2",
    ],
)
def test_diagnostic_cannot_enter_repeat_acceptance(protocol):
    root = Path(__file__).resolve().parents[1]
    receipt = json.loads(
        (root / "output/engine2-identified-readiness-20260930.json").read_text()
    )
    receipt["diagnostic_protocol"] = protocol
    with pytest.raises(ValueError, match="trial acceptance failed"):
        accept(receipt)


@pytest.mark.parametrize("mode", ["scalar", "event", "ping_flag"])
def test_invalid_saved_scalars_or_ping_flag(mode):
    records, correlation = observations()
    if mode == "scalar":
        records[0]["before"]["redis_unix_ns"] = True
    elif mode == "event":
        correlation["matches"][0]["event_unix_ns"] = True
    else:
        records[0]["ping_clock"]["within_tolerance"] = False
    with pytest.raises(ValueError):
        summarize(records, correlation)


def test_clock_domain_flag_requires_correlation(tmp_path, monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["sensor_trial", "--output", str(tmp_path / "new"), "--clock-domains"],
    )
    with pytest.raises(SystemExit):
        sensor_trial.main()
    assert not (tmp_path / "new").exists()


@pytest.mark.parametrize("fail_after", [False, True])
def test_clocked_ping_keeps_identity_and_partial_evidence(monkeypatch, fail_after):
    ticks = iter([point(10**9 + i * 10_000_000, i * 10_000_000) for i in range(6)])
    monkeypatch.setattr(sensor_trial, "sample", lambda: next(ticks))
    commands = []

    def command(*args, **kwargs):
        commands.append(args)
        if args[-1] == "TIME":
            if len(commands) == 3 and fail_after:
                raise ValueError("synthetic TIME failure")
            return "1\n5000" if len(commands) == 1 else "1\n45000"
        return "42\nPONG"

    monkeypatch.setattr(sensor_trial, "command", command)
    pids, records = [], []
    if fail_after:
        with pytest.raises(ValueError):
            sensor_trial.clocked_ping("a" * 64, pids, records)
        assert "after" not in records[0]
    else:
        assert sensor_trial.clocked_ping("a" * 64, pids, records) == "PONG"
        assert "after" in records[0]
    assert pids == [42] and records[0]["process_id"] == 42
    assert len(commands) == 3 and "before" in records[0] and "ping_clock" in records[0]
    attempts = records[0]["time_read_attempts"]
    assert attempts[0]["status"] == "accepted"
    assert attempts[1]["status"] == ("failed" if fail_after else "accepted")
    assert attempts[1]["phase"] == "after"


@pytest.mark.parametrize(
    "mode", ["drift", "width", "wide", "reply", "command", "first", "last"]
)
def test_failed_time_read_keeps_sanitized_evidence(monkeypatch, mode):
    first = point(10**9, 0)
    last = point(1_010_000_000, 10_000_000)
    if mode == "drift":
        last["wall_ns"] += 60_000_000
    elif mode == "width":
        first["sampling_span_ns"] = 6_000_000
    elif mode == "wide":
        last = point(1_600_000_000, 600_000_000)
    ticks = iter([first, last])
    sample_calls = []

    def sample():
        sample_calls.append(True)
        if mode == "first" or (mode == "last" and len(sample_calls) == 2):
            raise ValueError("private diagnostic detail")
        return next(ticks)

    def command(*args, **kwargs):
        assert args[-1] == "TIME"
        if mode == "command":
            raise RuntimeError("private diagnostic detail")
        return "private diagnostic detail" if mode == "reply" else "1\n5000"

    monkeypatch.setattr(sensor_trial, "sample", sample)
    monkeypatch.setattr(sensor_trial, "command", command)
    pids, records = [], []
    with pytest.raises((ValueError, RuntimeError)):
        sensor_trial.clocked_ping("a" * 64, pids, records)
    assert pids == [] and "before" not in records[0]
    attempt = records[0]["time_read_attempts"][0]
    assert attempt["status"] == "failed" and attempt["phase"] == "before"
    assert "private diagnostic detail" not in json.dumps(records)
    if mode not in {"first", "last", "command"}:
        assert attempt["first"] == first and attempt["last"] == last
        assert attempt["clock_comparison"] == compare(first, last)
        assert attempt["failed_stage"] == "validating_bracket"
        assert attempt["clock_rejection_reasons"] == (
            ["round_trip_exceeds_500ms"]
            if mode == "wide"
            else []
            if mode == "reply"
            else ["clock_outside_tolerance"]
        )
        assert len(attempt["response_sha256"]) == 64
    else:
        assert (
            attempt["failed_stage"]
            == {
                "first": "sampling_first",
                "last": "sampling_last",
                "command": "command_running",
            }[mode]
        )
