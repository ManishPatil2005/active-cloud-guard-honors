import json
from datetime import datetime, timezone
import pytest
from cloudguard.correlation import correlate, parse_ping
from cloudguard.clock_check import compare
from scripts.sensor_trial import rules


def test_fields_only_profile_keeps_legacy_envelope_strict():
    from cloudguard.correlation import connection_counts

    _, events = inputs()
    for event in events:
        del event["output"]
    raw = ("\n".join(json.dumps(e) for e in events) + "\n").encode()
    with pytest.raises(ValueError):
        connection_counts(raw, "a" * 64, [1, 2, 3, 4])
    counts, extra = connection_counts(raw, "a" * 64, [1, 2, 3, 4], fields_only=True)
    assert all(len(v) == 1 for v in counts.values()) and extra == 0


@pytest.mark.parametrize("flag", [None, 1, "true"])
def test_format_is_explicit_boolean_not_truthiness(flag):
    from cloudguard.correlation import connection_counts

    with pytest.raises(ValueError):
        connection_counts(b"", "a" * 64, [1], fields_only=flag)


@pytest.mark.parametrize(
    "fault", ["legacy_output", "pid", "scope", "time", "field", "kind"]
)
def test_fields_only_rejects_unexpected_or_invalid_original_fields(fault):
    from cloudguard.correlation import connection_counts

    _, events = inputs()
    row = events[0]
    row.pop("output")
    fields = row["output_fields"]
    if fault == "legacy_output":
        row["output"] = "not the declared profile"
    elif fault == "pid":
        fields["proc.vpid"] = True
    elif fault == "scope":
        fields["thread.cgroups"] = "b" * 64
    elif fault == "time":
        fields["evt.rawtime"] += 1
    elif fault == "field":
        fields["unexpected"] = 0
    elif fault == "kind":
        fields["evt.type"] = "unsupported"
    with pytest.raises(ValueError):
        connection_counts(
            (json.dumps(row) + "\n").encode(), "a" * 64, [1], fields_only=True
        )


def test_fields_only_never_increases_the_raw_byte_limit():
    from cloudguard.correlation import connection_counts

    with pytest.raises(ValueError, match="oversized"):
        connection_counts(b" " * 1_000_001, "a" * 64, [1], fields_only=True)


def inputs():
    calls, events = [], []
    for p in range(1, 5):
        start = p * 10**9
        a = dict(wall_ns=start, monotonic_mid_ns=start, sampling_span_ns=0)
        b = dict(
            wall_ns=start + 100_000_000,
            monotonic_mid_ns=start + 100_000_000,
            sampling_span_ns=0,
        )
        calls.append(
            dict(pong=True, clock_sampling=dict(first=a, last=b, **compare(a, b)))
        )
        ns = start + 50_000_000
        events.append(
            dict(
                hostname="synthetic",
                output="synthetic",
                priority="Informational",
                rule="ACG Redis selected syscall smoke",
                source="syscall",
                tags=[],
                time=datetime.fromtimestamp(p, timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%S"
                )
                + ".050000000Z",
                output_fields={
                    "evt.rawres": 0,
                    "evt.rawtime": ns,
                    "evt.time": ns,
                    "evt.type": "connect",
                    "thread.cgroups": "a" * 64,
                    "proc.vpid": p,
                },
            )
        )
    return calls, events


@pytest.mark.parametrize(
    "mode",
    ["valid", "missing", "duplicate", "wrong_scope", "extra", "bad_time", "pid_reuse"],
)
def test_correlation(mode):
    calls, events = inputs()
    pids = [1, 2, 3, 4]
    if mode == "missing":
        events.pop()
    elif mode == "duplicate":
        events.append(events[0])
    elif mode == "wrong_scope":
        events[0]["output_fields"]["thread.cgroups"] = "b" * 64
    elif mode == "extra":
        events[0]["output_fields"]["proc.cmdline"] = "forbidden"
    elif mode == "bad_time":
        events[0]["output_fields"]["evt.rawtime"] += 1
    elif mode == "pid_reuse":
        pids[1] = 1
    raw = "\n".join(json.dumps(e) for e in events).encode()
    if mode == "valid":
        result = correlate(raw, "a" * 64, pids, calls)
        assert result["zero_excluded_samples"] == 0
        assert result["authenticated"] is False
    else:
        with pytest.raises(ValueError):
            correlate(raw, "a" * 64, pids, calls)


@pytest.mark.parametrize(
    "reply", ["1\nPONG", "1\nwrong", "PONG", "0\nPONG", "1\nPONG\nextra"]
)
def test_ping_identity(reply):
    if reply == "1\nPONG":
        assert parse_ping(reply) == 1
    else:
        with pytest.raises(ValueError):
            parse_ping(reply)


def test_opt_in_fields():
    assert "proc.vpid" not in rules("a" * 64)
    diagnostic = rules("a" * 64, correlation=True)
    assert "proc.vpid" in diagnostic
    assert "proc.cmdline" not in diagnostic


@pytest.mark.parametrize("mode", ["missing", "both", "ambiguous", "overlap", "boolean"])
def test_warmup_accounting(mode):
    calls, events = inputs()
    warmup = [5, 6]
    if mode in {"both", "ambiguous"}:
        for pid in [5, 6] + ([5] if mode == "ambiguous" else []):
            event = json.loads(json.dumps(events[0]))
            event["output_fields"]["proc.vpid"] = pid
            events.append(event)
    if mode == "overlap":
        warmup = [1, 6]
    if mode == "boolean":
        warmup = [True, 6]
    raw = "\n".join(json.dumps(e) for e in events).encode()
    if mode in {"overlap", "boolean"}:
        with pytest.raises(ValueError):
            correlate(raw, "a" * 64, [1, 2, 3, 4], calls, warmup_pids=warmup)
    else:
        report = correlate(raw, "a" * 64, [1, 2, 3, 4], calls, warmup_pids=warmup)
        assert report["all_six_commands_uniquely_observed"] is (mode == "both")
        assert (
            report["warmup_accounting"][0]["status"]
            == {
                "missing": "not_observed",
                "both": "unique_match",
                "ambiguous": "ambiguous",
            }[mode]
        )
        assert report["coverage"] == "partial_or_unknown"
