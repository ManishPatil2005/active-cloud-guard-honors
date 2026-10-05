import copy
import json
from types import SimpleNamespace

import pytest

from cloudguard import boot_clock, clock_check, clock_lineage as lineage
from scripts import clock_lineage as runner


def packets():
    domain = boot_clock.namespace_facts(
        "time:[123]",
        "monotonic 0 0\nboottime 0 0",
        "12345678-1234-1234-1234-123456789abc",
    )
    domain["time_namespace_for_children"] = domain["time_namespace"]
    result = []
    for i in range(lineage.READS):
        t = 10**12 + i * 2 * 10**9
        wall = 10**18 + t
        first = dict(wall_ns=wall - 100, monotonic_mid_ns=t - 100, sampling_span_ns=2)
        last = dict(wall_ns=wall + 100, monotonic_mid_ns=t + 100, sampling_span_ns=2)
        guest = dict(
            sample=dict(
                **boot_clock.bounds(t + 498, wall, t + 502),
                mono_before_ns=t - 3,
                mono_after_ns=t + 3,
            ),
            domain=copy.deepcopy(domain),
            source_sha256={"fixture": "a" * 64},
        )
        result.append(
            dict(
                index=i,
                status="accepted",
                host_first=first,
                host_last=last,
                comparison=clock_check.compare(first, last),
                guest=guest,
            )
        )
    return result


def test_intervals_and_no_epoch_or_midpoint_assumption():
    values = packets()
    summary = lineage.summarize(values, {"fixture": "a" * 64})
    assert len(summary["rows"]) == 16
    row = summary["rows"][-1]
    assert row["wall_minus_boot_change"] == lineage.interval(-4, 4)
    assert row["host_minus_guest_boot_elapsed"] == lineage.interval(-206, 206)
    assert row["host_minus_guest_mono_elapsed"] == lineage.interval(-208, 208)
    assert row["guest_minus_host_wall"] == lineage.interval(-102, 102)
    assert summary["correction_applied"] is False
    assert summary["causal_attribution"] == "not_proven"


def test_guest_wall_jump_is_observation_not_fitted_correction():
    values = packets()
    for p in values[1:]:
        g = p["guest"]["sample"]
        g.update(
            boot_clock.bounds(
                g["boot_before_ns"], g["realtime_ns"] + 123 * 10**9, g["boot_after_ns"]
            )
        )
    rows = lineage.summarize(values, {"fixture": "a" * 64})["rows"]
    assert rows[-1]["wall_minus_boot_change"]["lower_ns"] == 123 * 10**9 - 4
    assert rows[-1]["guest_minus_host_wall"]["includes_zero"] is False
    assert rows[-1]["host_minus_guest_boot_elapsed"]["includes_zero"] is True


@pytest.mark.parametrize(
    "mode",
    [
        "count",
        "index",
        "status",
        "source",
        "domain",
        "gap",
        "order",
        "summary",
        "boolean",
        "width",
        "round_trip",
        "host_clock",
    ],
)
def test_invalid_saved_packets(mode):
    values = packets()
    p = values[-1]
    if mode == "count":
        values.pop()
    elif mode == "index":
        p["index"] = 3
    elif mode == "status":
        p["status"] = "failed"
    elif mode == "source":
        p["guest"]["source_sha256"] = {}
    elif mode == "domain":
        p["guest"]["domain"]["time_namespace"] = "time:[456]"
    elif mode == "gap":
        p["host_first"] = values[-2]["host_last"]
        p["comparison"] = clock_check.compare(p["host_first"], p["host_last"])
    elif mode == "order":
        p["guest"]["sample"] = values[0]["guest"]["sample"]
    elif mode == "summary":
        p["guest"]["sample"]["offset_lower_ns"] += 1
    elif mode == "boolean":
        p["host_first"]["wall_ns"] = True
    elif mode == "width":
        p["host_first"]["sampling_span_ns"] = 5_000_001
    elif mode == "round_trip":
        p["host_last"]["wall_ns"] += 3 * 10**9
        p["host_last"]["monotonic_mid_ns"] += 3 * 10**9
        p["comparison"] = clock_check.compare(p["host_first"], p["host_last"])
    else:
        p["host_last"]["wall_ns"] += 10**9
        p["comparison"] = clock_check.compare(p["host_first"], p["host_last"])
    with pytest.raises(ValueError):
        lineage.summarize(values, {"fixture": "a" * 64})


def test_native_sequence_and_no_fallback(monkeypatch):
    monkeypatch.setattr(lineage.time, "CLOCK_BOOTTIME", 7, raising=False)
    monkeypatch.setattr(lineage.time, "CLOCK_MONOTONIC", 1, raising=False)
    monkeypatch.setattr(lineage.time, "CLOCK_REALTIME", 0, raising=False)
    calls = []
    readings = iter([100, 501, 1000, 502, 103])

    def clock(which):
        calls.append(which)
        return next(readings)

    result = lineage.native_snapshot(clock)
    assert calls == [1, 7, 0, 7, 1] and result["mono_after_ns"] == 103
    monkeypatch.delattr(lineage.time, "CLOCK_BOOTTIME")
    with pytest.raises(ValueError, match="native CLOCK_BOOTTIME"):
        lineage.native_snapshot(clock)


@pytest.mark.parametrize(
    "raw",
    [b'{"x":1,"x":2}', b'{"x":NaN}', b" " * 100001],
    ids=["duplicate", "nonfinite", "overlarge"],
)
def test_strict_json(raw):
    with pytest.raises(ValueError):
        lineage.strict_json(raw)


def test_command_scope_and_retained_failed_bracket(monkeypatch):
    p = packets()[0]
    last = copy.deepcopy(p["host_last"])
    last["wall_ns"] += 10**9
    readings = iter([p["host_first"], last])
    monkeypatch.setattr(runner, "host_sample", lambda: next(readings))
    calls = []

    def command(args, **kwargs):
        calls.append((args, kwargs))
        return SimpleNamespace(stdout=json.dumps(p["guest"]).encode())

    monkeypatch.setattr(runner.subprocess, "run", command)
    evidence = []
    with pytest.raises(ValueError):
        runner.record_packet(evidence, {"fixture": "a" * 64}, 0)
    assert evidence[0]["status"] == "failed"
    assert evidence[0]["host_last"] == last and "guest" in evidence[0]
    assert evidence[0]["stage"] == "validate_packet"
    assert calls == [
        (runner.GUEST_COMMAND, dict(capture_output=True, timeout=5, check=True))
    ]
    assert all("docker" not in a and "systemctl" not in a for a in runner.GUEST_COMMAND)


def test_timeout_preserves_first_sample_only(monkeypatch):
    monkeypatch.setattr(runner, "host_sample", lambda: packets()[0]["host_first"])

    def command(*args, **kwargs):
        raise runner.subprocess.TimeoutExpired("fixed", 5, stderr=b"private details")

    monkeypatch.setattr(runner.subprocess, "run", command)
    evidence = []
    with pytest.raises(runner.subprocess.TimeoutExpired):
        runner.record_packet(evidence, {}, 0)
    assert evidence[0]["stage"] == "guest_command"
    assert evidence[0]["error_type"] == "TimeoutExpired"
    assert "host_last" not in evidence[0] and "private" not in str(evidence)


def test_observe_fixed_gaps_stop_and_host_gate(monkeypatch):
    monkeypatch.setattr(runner.sys, "platform", "win32")
    monkeypatch.setattr(runner, "source_hashes", lambda: {"fixture": "a" * 64})
    saved = packets()
    monkeypatch.setattr(runner, "record_packet", lambda p, s, i: p.append(saved[i]))
    gaps = []
    monkeypatch.setattr(runner.time, "sleep", gaps.append)
    report = dict(packets=[])
    runner.observe(report)
    assert gaps == [1] * 15 and report["status"] == "observed"

    def fail(p, s, i):
        p.append(dict(index=i, status="failed"))
        raise ValueError("stop")

    monkeypatch.setattr(runner, "record_packet", fail)
    gaps.clear()
    report = dict(packets=[])
    with pytest.raises(ValueError):
        runner.observe(report)
    assert len(report["packets"]) == 1 and gaps == []
    monkeypatch.setattr(runner.sys, "platform", "linux")
    with pytest.raises(ValueError, match="Windows host"):
        runner.observe(dict(packets=[]))


def test_cli_preserves_failure_and_refuses_overwrite(tmp_path, monkeypatch):
    target = tmp_path / "new.json"
    monkeypatch.setattr(runner.sys, "argv", ["clock_lineage", "--output", str(target)])

    def fail(report):
        report["packets"].append(dict(status="failed"))
        raise ValueError("private message")

    monkeypatch.setattr(runner, "observe", fail)
    assert runner.main() == 1
    raw = target.read_bytes()
    assert b'"error_type": "ValueError"' in raw and b"private" not in raw
    with pytest.raises(FileExistsError):
        runner.main()
    assert target.read_bytes() == raw


def test_offline_review_source_and_summary_binding(monkeypatch):
    sources = {"fixture": "a" * 64}
    monkeypatch.setattr(runner, "source_hashes", lambda: sources)
    saved = packets()
    report = dict(
        protocol=lineage.PROTOCOL,
        status="observed",
        planned_reads=16,
        spacing_seconds=1,
        source_sha256=sources,
        source_sha256_after=sources,
        clock_settings_modified=False,
        sensor_started=False,
        packets=saved,
        summary=lineage.summarize(saved, sources),
    )
    checked = runner.review(json.dumps(report).encode())
    assert checked["local_consistency_verified"] is True
    report["summary"]["correction_applied"] = True
    with pytest.raises(ValueError, match="summary differs"):
        runner.review(json.dumps(report).encode())
    report["source_sha256_after"] = {}
    with pytest.raises(ValueError, match="protocol/source"):
        runner.review(json.dumps(report).encode())


@pytest.mark.parametrize("mode", ["index_bool", "comparison_float", "domain_extra"])
def test_coercion_and_unexpected_fields_refused(mode):
    saved = packets()
    if mode == "index_bool":
        saved[0]["index"] = False
    elif mode == "comparison_float":
        saved[0]["comparison"]["clock_difference_ns"] = 0.0
    else:
        saved[0]["guest"]["domain"]["unexpected"] = "not published"
    with pytest.raises(ValueError):
        lineage.summarize(saved, {"fixture": "a" * 64})


def test_invalid_reply_not_retained(monkeypatch):
    readings = iter([packets()[0]["host_first"], packets()[0]["host_last"]])
    monkeypatch.setattr(runner, "host_sample", lambda: next(readings))
    monkeypatch.setattr(
        runner.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(stdout=b'{"private": "sentinel"}'),
    )
    evidence = []
    with pytest.raises(ValueError):
        runner.record_packet(evidence, {}, 0)
    assert "guest" not in evidence[0] and "sentinel" not in str(evidence)
