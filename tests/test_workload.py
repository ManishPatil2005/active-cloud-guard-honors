import pytest

from cloudguard.workload import run
from scripts import workload_report


@pytest.mark.parametrize("profile,number", [("ping_1", 1), ("ping_4", 4)])
def test_fixed_schedule(profile, number):
    now = [0]

    def sleep(seconds):
        now[0] += int(seconds * 10**9)

    def ping():
        now[0] += 100_000_000
        return "PONG"

    result = run(
        profile,
        ping,
        monotonic_ns=lambda: now[0],
        wall_ns=lambda: now[0] + 10**18,
        sleep=sleep,
    )
    assert result["status"] == "completed"
    assert len(result["calls"]) == number
    assert result["elapsed_monotonic_ns"] == 4 * 10**9
    assert result["clock_difference_ns"] == 0
    assert result["overhead_estimate"] is None
    assert result["timing_protocol"] == "per_call_brackets_v1"
    assert all(c["clock_sampling"]["within_tolerance"] for c in result["calls"])


@pytest.mark.parametrize("mode", ["late", "clock", "pong"])
def test_failures_not_success(mode):
    now = [0]
    wall_calls = [0]

    def wall():
        wall_calls[0] += 1
        return now[0] + (10**9 if mode == "clock" and wall_calls[0] == 2 else 0)

    def sleep(seconds):
        now[0] += int(seconds * 10**9)

    def ping():
        now[0] += 5 * 10**9 if mode == "late" else 100_000_000
        return "wrong" if mode == "pong" else "PONG"

    result = run("ping_4", ping, monotonic_ns=lambda: now[0], wall_ns=wall, sleep=sleep)
    assert result["status"] != "completed"


def test_unknown_profile_does_not_execute():
    with pytest.raises(ValueError):
        run("arbitrary", lambda: pytest.fail("must not execute"))


def test_transient_call_clock_jump_rejected_even_when_endpoint_clocks_agree():
    now = [0]
    readings = iter([0, 0, 200_000_000, 4_000_000_000])

    def sleep(seconds):
        now[0] += int(seconds * 10**9)

    def ping():
        now[0] += 100_000_000
        return "PONG"

    result = run(
        "ping_4",
        ping,
        monotonic_ns=lambda: now[0],
        wall_ns=lambda: next(readings),
        sleep=sleep,
    )
    assert result["status"] == "call_clock_outside_tolerance"
    assert len(result["calls"]) == 1
    assert result["calls"][0]["pong"] is True
    assert result["clock_difference_ns"] == 0
    assert result["calls"][0]["clock_sampling"]["clock_difference_ns"] == 100_000_000


def test_interval_is_half_open(monkeypatch):
    trial = dict(
        target_identity_stable=True,
        measurement=dict(
            status="completed", start_unix_ns=10**9, end_unix_ns=2 * 10**9
        ),
    )
    monkeypatch.setattr(workload_report, "read_json", lambda _: (trial, "a" * 64))
    bundle = dict(
        capture=dict(
            events=[
                dict(timestamp=s, kind="file_open")
                for s in [
                    "1970-01-01T00:00:00.999999999Z",
                    "1970-01-01T00:00:01.000000000Z",
                    "1970-01-01T00:00:01.999999999Z",
                    "1970-01-01T00:00:02.000000000Z",
                ]
            ]
        ),
        accounting=dict(raw_sha256="b" * 64, inventory_sha256="c" * 64),
    )
    monkeypatch.setattr(workload_report, "normalize", lambda *a, **kw: bundle)
    result = workload_report.report("raw", "trial", "inventory")
    assert result["measured_event_count"] == 2
    assert result["outside_interval_event_count"] == 2
    assert result["coverage"] == "partial_or_unknown"
    assert result["event_regions"] == {
        "before": {"file_open": 1},
        "inside": {"file_open": 2},
        "after": {"file_open": 1},
    }
    assert result["network_connect_offsets"] == []
    assert result["timestamp_regressions_in_export_order"] == 0


def test_connection_offsets_preserve_order_and_boundaries(monkeypatch):
    trial = dict(
        target_identity_stable=True,
        measurement=dict(
            status="completed", start_unix_ns=10**9, end_unix_ns=2 * 10**9
        ),
    )
    monkeypatch.setattr(workload_report, "read_json", lambda _: (trial, "a" * 64))
    bundle = dict(
        capture=dict(
            events=[
                dict(timestamp=t, kind="network_connect")
                for t in [
                    "1970-01-01T00:00:02.000000000Z",
                    "1970-01-01T00:00:00.999999999Z",
                    "1970-01-01T00:00:01.000000000Z",
                ]
            ]
        ),
        accounting=dict(raw_sha256="b" * 64, inventory_sha256="c" * 64),
    )
    monkeypatch.setattr(workload_report, "normalize", lambda *a, **kw: bundle)
    result = workload_report.report("raw", "trial", "inventory")
    assert result["network_connect_offsets"] == [
        dict(offset_from_start_ns=10**9, region="after"),
        dict(offset_from_start_ns=-1, region="before"),
        dict(offset_from_start_ns=0, region="inside"),
    ]
    assert result["timestamp_regressions_in_export_order"] == 1
    assert result["measured_event_count"] == 1
    assert result["outside_interval_event_count"] == 2
    assert result["coverage"] == "partial_or_unknown"


def test_rejected_normalization_has_no_alignment_report(monkeypatch):
    trial = dict(
        target_identity_stable=True,
        measurement=dict(status="completed", start_unix_ns=1, end_unix_ns=2),
    )
    monkeypatch.setattr(workload_report, "read_json", lambda _: (trial, "a" * 64))
    monkeypatch.setattr(
        workload_report, "normalize", lambda *a, **kw: {"capture": None}
    )
    with pytest.raises(ValueError, match="raw normalization rejected"):
        workload_report.report("raw", "trial", "inventory")


@pytest.mark.parametrize("mode", ["missing", "failed", "unstable", "boolean"])
def test_bad_interval_not_scored(monkeypatch, mode):
    trial = dict(
        target_identity_stable=True,
        measurement=dict(status="completed", start_unix_ns=1, end_unix_ns=2),
    )
    if mode == "missing":
        trial.pop("measurement")
    elif mode == "failed":
        trial["measurement"]["status"] = "workload_failed"
    elif mode == "unstable":
        trial["target_identity_stable"] = False
    else:
        trial["measurement"]["start_unix_ns"] = True
    monkeypatch.setattr(workload_report, "read_json", lambda _: (trial, "a" * 64))
    monkeypatch.setattr(
        workload_report, "normalize", lambda *a, **kw: pytest.fail("must reject first")
    )
    with pytest.raises(ValueError):
        workload_report.report("raw", "trial", "inventory")
