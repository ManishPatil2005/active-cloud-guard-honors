import copy
import json
from types import SimpleNamespace

import pytest

from cloudguard import clock_lineage as lineage
from scripts import clock_lineage as runner
from test_clock_lineage import packets

SOURCES = {"fixture": "a" * 64}


def raw_packets(difference=0):
    result = packets()
    for p in result:
        g = p["guest"]["sample"]
        center = (g["mono_before_ns"] + g["mono_after_ns"]) // 2
        g.update(
            raw_before_ns=center + 300 + p["index"] * difference - 5,
            raw_after_ns=center + 300 + p["index"] * difference + 5,
        )
    return result


@pytest.mark.parametrize("difference", [0, 1000, -1000])
def test_raw_intervals_and_distinct_protocol(difference):
    result = lineage.summarize(raw_packets(difference), SOURCES, raw=True)
    assert result["protocol"] == lineage.RAW_PROTOCOL
    row = result["rows"][-1]
    shift = 15 * difference
    assert row["raw_minus_mono_elapsed"] == lineage.interval(shift - 16, shift + 16)
    assert row["host_minus_guest_raw_elapsed"] == lineage.interval(
        -212 - shift, 212 - shift
    )
    assert result["correction_applied"] is False


@pytest.mark.parametrize(
    "mode", ["missing", "boolean", "wide", "backward", "order", "legacy"]
)
def test_raw_saved_refusals(mode):
    saved = raw_packets()
    g = saved[-1]["guest"]["sample"]
    if mode == "missing":
        g.pop("raw_after_ns")
    elif mode == "boolean":
        g["raw_before_ns"] = True
    elif mode == "wide":
        g["raw_after_ns"] = g["raw_before_ns"] + 5_000_001
    elif mode == "backward":
        g["raw_after_ns"] = g["raw_before_ns"] - 1
    elif mode == "order":
        g.update(raw_before_ns=100, raw_after_ns=110)
    with pytest.raises((ValueError, KeyError)):
        lineage.summarize(saved, SOURCES, raw=mode != "legacy")


def test_native_raw_read_order_and_no_fallback(monkeypatch):
    for name, value in [
        ("CLOCK_BOOTTIME", 7),
        ("CLOCK_MONOTONIC", 1),
        ("CLOCK_REALTIME", 0),
        ("CLOCK_MONOTONIC_RAW", 4),
    ]:
        monkeypatch.setattr(lineage.time, name, value, raising=False)
    calls = []
    readings = iter([700, 100, 500, 1000, 501, 101, 701])

    def clock(which):
        calls.append(which)
        return next(readings)

    sample = lineage.native_snapshot(clock, raw=True)
    assert calls == [4, 1, 7, 0, 7, 1, 4]
    assert sample["raw_before_ns"] == 700 and sample["raw_after_ns"] == 701
    monkeypatch.delattr(lineage.time, "CLOCK_MONOTONIC_RAW")
    with pytest.raises(ValueError, match="no fallback"):
        lineage.native_snapshot(clock, raw=True)


def test_raw_fixed_command_retained_on_host_rejection(monkeypatch):
    p = raw_packets()[0]
    first, last = p["host_first"], copy.deepcopy(p["host_last"])
    last["wall_ns"] += 10**9
    readings = iter([first, last])
    monkeypatch.setattr(runner, "host_sample", lambda: next(readings))
    calls = []

    def command(args, **kwargs):
        calls.append((args, kwargs))
        return SimpleNamespace(stdout=json.dumps(p["guest"]).encode())

    monkeypatch.setattr(runner.subprocess, "run", command)
    saved = []
    with pytest.raises(ValueError):
        runner.record_packet(saved, SOURCES, 0, raw=True)
    assert calls == [
        (
            runner.GUEST_COMMAND + ("--raw-clock",),
            dict(capture_output=True, timeout=5, check=True),
        )
    ]
    assert (
        saved[0]["status"] == "failed"
        and "raw_before_ns" in saved[0]["guest"]["sample"]
    )


def test_raw_observe_fixed_gaps_and_offline_binding(monkeypatch):
    monkeypatch.setattr(runner.sys, "platform", "win32")
    monkeypatch.setattr(runner, "source_hashes", lambda: SOURCES)
    saved = raw_packets()
    calls, gaps = [], []

    def packet(p, s, i, *, raw):
        calls.append(raw)
        p.append(saved[i])

    monkeypatch.setattr(runner, "record_packet", packet)
    monkeypatch.setattr(runner.time, "sleep", gaps.append)
    report = dict(
        protocol=lineage.RAW_PROTOCOL,
        packets=[],
        raw_clock=True,
        planned_reads=16,
        spacing_seconds=1,
        clock_settings_modified=False,
        sensor_started=False,
    )
    runner.observe(report)
    assert calls == [True] * 16 and gaps == [1] * 15
    reviewed = runner.review(json.dumps(report).encode())
    assert reviewed["summary"]["protocol"] == lineage.RAW_PROTOCOL
    report["raw_clock"] = False
    with pytest.raises(ValueError, match="protocol/source"):
        runner.review(json.dumps(report).encode())


def test_raw_cli_routes_guest_and_refuses_ambiguous_review(tmp_path, monkeypatch):
    monkeypatch.setattr(
        runner.sys, "argv", ["clock_lineage", "--guest-snapshot", "--raw-clock"]
    )
    calls = []
    monkeypatch.setattr(
        runner, "guest_snapshot", lambda **kwargs: calls.append(kwargs) or {}
    )
    assert runner.main() == 0 and calls == [dict(raw=True)]
    output = tmp_path / "new.json"
    monkeypatch.setattr(
        runner.sys,
        "argv",
        ["clock_lineage", "--review", "unused", "--raw-clock", "--output", str(output)],
    )
    with pytest.raises(SystemExit):
        runner.main()
    assert not output.exists()
