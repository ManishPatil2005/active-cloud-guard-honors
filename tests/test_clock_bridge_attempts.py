import json
import sys

import pytest

from scripts import clock_bridge, sensor_trial
from tests.test_clock_bridge import point


def setup_run(monkeypatch, tmp_path):
    destination = tmp_path / "receipt.json"
    monkeypatch.setattr(
        sys, "argv", ["clock_bridge", "--record-attempts", "--output", str(destination)]
    )
    monkeypatch.setattr(clock_bridge, "local_daemon", lambda: None)
    monkeypatch.setattr(clock_bridge, "check_sensor_absent", lambda: None)
    monkeypatch.setattr(clock_bridge.time, "sleep", lambda seconds: None)
    monkeypatch.setattr(clock_bridge, "command", lambda *args, **kwargs: "a" * 64)
    monkeypatch.setattr(
        clock_bridge, "target_identity", lambda cid: dict(id=cid, running=True)
    )
    ticks = iter([point(10**9 + i * 10_000_000, i * 10_000_000) for i in range(12)])
    monkeypatch.setattr(sensor_trial, "sample", lambda: next(ticks))
    calls = []

    def command(*args, **kwargs):
        assert args == (
            "exec",
            "a" * 64,
            "redis-cli",
            "--raw",
            "-h",
            "127.0.0.1",
            "TIME",
        )
        assert kwargs == dict(timeout=5)
        calls.append(args)
        return f"1\n{(len(calls) - 1) * 20000 + 5000}"

    monkeypatch.setattr(sensor_trial, "command", command)
    return destination, calls


def test_six_reads_share_failure_recorder(monkeypatch, tmp_path):
    destination, calls = setup_run(monkeypatch, tmp_path)
    sleeps = []
    monkeypatch.setattr(clock_bridge.time, "sleep", sleeps.append)
    clock_bridge.main()
    report = json.loads(destination.read_text())
    assert (
        len(calls) == len(report["samples"]) == len(report["time_read_attempts"]) == 6
    )
    assert (
        report["status"] == "observed"
        and report["protocol"] == "redis_time_failure_evidence_v1"
    )
    assert report["sources_unchanged"] and len(report["source_sha256"]) == 6
    assert report["known_sensor_absent_before"] and report["known_sensor_absent_after"]
    assert report["sensor_started"] is False and report["correction_applied"] is False
    assert [a["phase"] for a in report["time_read_attempts"]] == [
        f"time_{i}" for i in range(1, 7)
    ]
    assert all(a["status"] == "accepted" for a in report["time_read_attempts"])
    assert sleeps == [1] * 5


def test_rejected_clock_read_stops_without_retry(monkeypatch, tmp_path):
    destination, calls = setup_run(monkeypatch, tmp_path)
    sleeps = []
    monkeypatch.setattr(clock_bridge.time, "sleep", sleeps.append)
    ticks = iter([point(10**9, 0), point(1_200_000_000, 10_000_000)])
    monkeypatch.setattr(sensor_trial, "sample", lambda: next(ticks))
    with pytest.raises(ValueError):
        clock_bridge.main()
    report = json.loads(destination.read_text())
    assert (
        len(calls) == len(report["time_read_attempts"]) == 1 and report["samples"] == []
    )
    attempt = report["time_read_attempts"][0]
    assert attempt["clock_comparison"]["clock_difference_ns"] == 190_000_000
    assert attempt["clock_rejection_reasons"] == ["clock_outside_tolerance"]
    assert report["status"] == "failed" and "identity_after" not in report
    assert sleeps == []


@pytest.mark.parametrize("mode", ["preflight", "identity", "sources", "overwrite"])
def test_lifecycle_refusal_keeps_safe_receipt(monkeypatch, tmp_path, mode):
    destination, calls = setup_run(monkeypatch, tmp_path)
    if mode == "preflight":

        def refuse():
            raise ValueError("private details")

        monkeypatch.setattr(clock_bridge, "check_sensor_absent", refuse)
    elif mode == "identity":
        identities = iter([dict(id="a" * 64), dict(id="b" * 64)])
        monkeypatch.setattr(
            clock_bridge, "target_identity", lambda cid: next(identities)
        )
    elif mode == "sources":
        hashes = iter([dict(one="a" * 64), dict(one="b" * 64)])
        monkeypatch.setattr(clock_bridge, "source_hashes", lambda: next(hashes))
    else:
        destination.write_text("preserve original")
    with pytest.raises((ValueError, FileExistsError)):
        clock_bridge.main()
    if mode == "overwrite":
        assert destination.read_text() == "preserve original" and calls == []
    else:
        report = json.loads(destination.read_text())
        assert (
            report["status"] == "failed"
            and "private details" not in destination.read_text()
        )
        assert len(calls) == (0 if mode == "preflight" else 6)


def test_legacy_mode_keeps_legacy_protocol(monkeypatch, tmp_path):
    destination, calls = setup_run(monkeypatch, tmp_path)
    monkeypatch.setattr(sys, "argv", ["clock_bridge", "--output", str(destination)])
    ticks = iter([point(10**9 + i * 10_000_000, i * 10_000_000) for i in range(12)])
    monkeypatch.setattr(clock_bridge, "sample", lambda: next(ticks))
    monkeypatch.setattr(
        clock_bridge,
        "command",
        lambda *args, **kwargs: "1\n5000" if args[-1] == "TIME" else "a" * 64,
    )
    clock_bridge.main()
    report = json.loads(destination.read_text())
    assert report["protocol"] == "redis_time_brackets_v1"
    assert "time_read_attempts" not in report and "source_sha256" not in report
