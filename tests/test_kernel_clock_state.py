import ctypes
import json

import pytest

from cloudguard import kernel_clock_state as kernel
from scripts import kernel_clock_diagnostic as runner
from test_raw_clock_lineage import raw_packets


def state():
    return dict(
        query_modes=0,
        time_state=0,
        status=8193,
        frequency_scaled_ppm=-65536,
        tick_usec=10000,
        phase_offset=100,
        phase_offset_unit="ns",
        time_constant=2,
        maxerror_usec=50,
        esterror_usec=10,
        tolerance_scaled_ppm=32768000,
    )


def fixture():
    result = []
    for p in raw_packets(1000):
        g = p["guest"]["sample"]
        result.append(
            dict(
                index=p["index"],
                status="accepted",
                sample=g,
                domain=p["guest"]["domain"],
                before=dict(
                    raw_before_ns=g["raw_before_ns"] - 20,
                    raw_after_ns=g["raw_before_ns"] - 10,
                    state=state(),
                ),
                after=dict(
                    raw_before_ns=g["raw_after_ns"] + 10,
                    raw_after_ns=g["raw_after_ns"] + 20,
                    state=state(),
                ),
            )
        )
    return result


def metadata():
    return dict(
        abi=kernel.ABI,
        glibc_version="2.39",
        timex_bytes=208,
        libc_sha256="a" * 64,
        unprivileged_user=True,
    )


@pytest.mark.parametrize("result", [0, 5, -1])
def test_zero_only_input_and_state_not_clean_verdict(result):
    calls = []

    def query(pointer):
        value = pointer._obj
        assert bytes(value) == b"\0" * 208 and value.modes == 0
        calls.append(value.modes)
        value.tick, value.freq, value.status = 10000, -65536, 8193
        return result

    if result == -1:
        with pytest.raises(OSError):
            kernel.read_state(query)
    else:
        observed = kernel.read_state(query)
        assert observed["time_state"] == result
        assert observed["frequency_scaled_ppm"] == -65536
        assert observed["phase_offset_unit"] == "ns"
    assert calls == [0]


@pytest.mark.parametrize(
    "mode", ["bool", "overflow", "modes", "unit", "tick", "state", "extra", "negative"]
)
def test_state_refusals(mode):
    s = state()
    if mode == "bool":
        s["query_modes"] = False
    elif mode == "overflow":
        s["frequency_scaled_ppm"] = 2**63
    elif mode == "modes":
        s["query_modes"] = 2
    elif mode == "unit":
        s["phase_offset_unit"] = "us"
    elif mode == "tick":
        s["tick_usec"] = 0
    elif mode == "state":
        s["time_state"] = 6
    elif mode == "extra":
        s["message"] = "not published"
    else:
        s["maxerror_usec"] = -1
    with pytest.raises(ValueError):
        kernel.checked_state(s)


@pytest.mark.parametrize("width", [10, 5_000_001, -1])
def test_sample_retains_fields_before_width_validation(width, monkeypatch):
    monkeypatch.setattr(kernel.time, "CLOCK_MONOTONIC_RAW", 4, raising=False)
    readings = iter([10_000_000, 10_000_000 + width])
    monkeypatch.setattr(kernel, "read_state", lambda query: state())
    evidence = {}
    if width == 10:
        kernel.state_sample(None, lambda clock: next(readings), evidence=evidence)
    else:
        with pytest.raises(ValueError):
            kernel.state_sample(None, lambda clock: next(readings), evidence=evidence)
    assert (
        evidence["state"] == state() and evidence["raw_after_ns"] == 10_000_000 + width
    )


def test_query_failure_preserves_first_raw_without_message(monkeypatch):
    monkeypatch.setattr(kernel.time, "CLOCK_MONOTONIC_RAW", 4, raising=False)
    evidence = {}

    def fail(query):
        raise OSError("private details")

    monkeypatch.setattr(kernel, "read_state", fail)
    with pytest.raises(OSError):
        kernel.state_sample(None, lambda clock: 100, evidence=evidence)
    assert evidence == dict(raw_before_ns=100)
    monkeypatch.delattr(kernel.time, "CLOCK_MONOTONIC_RAW")
    with pytest.raises(ValueError, match="no fallback"):
        kernel.state_sample(None)


def test_layout_and_nonlinux_refusal(monkeypatch):
    kernel.check_layout()
    assert ctypes.sizeof(kernel.Timex) == 208 and kernel.Timex.tick.offset == 88
    monkeypatch.setattr(kernel.sys, "platform", "win32")
    monkeypatch.setattr(
        kernel.ctypes, "CDLL", lambda *a, **k: pytest.fail("backend loaded on Windows")
    )
    with pytest.raises(ValueError, match="Linux"):
        kernel.native_backend()


@pytest.mark.parametrize("mode", ["valid", "version", "size", "hash", "root"])
def test_metadata(mode):
    m = metadata()
    if mode == "version":
        m["glibc_version"] = "2.40"
    elif mode == "size":
        m["timex_bytes"] = 208.0
    elif mode == "hash":
        m["libc_sha256"] = "invalid"
    elif mode == "root":
        m["unprivileged_user"] = False
    if mode == "valid":
        kernel.checked_metadata(m)
    else:
        with pytest.raises(ValueError):
            kernel.checked_metadata(m)


def test_complete_reduction_no_causal_claim():
    values = fixture()
    values[-1]["after"]["state"]["frequency_scaled_ppm"] = -131072
    summary = kernel.summarize(values)
    assert summary["state_read_count"] == 32
    assert summary["sampled_state_values"]["frequency_scaled_ppm"] == [-131072, -65536]
    assert summary["rows"][-1]["raw_minus_mono_elapsed"] == dict(
        lower_ns=14984, upper_ns=15016, includes_zero=False
    )
    assert summary["causal_attribution"] == "not_proven"


@pytest.mark.parametrize(
    "mode", ["count", "index", "failed", "pair_order", "domain", "sequence"]
)
def test_complete_pair_refusals(mode):
    values = fixture()
    p = values[-1]
    if mode == "count":
        values.pop()
    elif mode == "index":
        p["index"] = True
    elif mode == "failed":
        p["status"] = "failed"
    elif mode == "pair_order":
        p["before"]["raw_after_ns"] = p["sample"]["raw_before_ns"] + 1
    elif mode == "domain":
        p["domain"]["time_namespace"] = "time:[99]"
    else:
        p.update(
            sample=values[0]["sample"],
            before=values[0]["before"],
            after=values[0]["after"],
        )
    with pytest.raises(ValueError):
        kernel.summarize(values)


def test_record_packet_preserves_rejected_state(monkeypatch):
    g = raw_packets()[0]["guest"]
    monkeypatch.setattr(runner.guest, "guest_snapshot", lambda **kwargs: g)
    monkeypatch.setattr(runner.guest, "SOURCES", ("fixture",))
    calls = []

    def sampling(query, *, evidence):
        calls.append(evidence)
        evidence.update(raw_before_ns=100, state=state(), raw_after_ns=5_000_101)
        kernel.checked_sample(evidence)

    monkeypatch.setattr(runner.kernel, "state_sample", sampling)
    saved = []
    with pytest.raises(ValueError):
        runner.record_packet(saved, None, {"fixture": "a" * 64}, 0)
    assert len(calls) == 1 and saved[0]["stage"] == "state_before"
    assert saved[0]["before"]["state"] == state() and saved[0]["status"] == "failed"


def test_observe_fixed_count_gap_source_backend_and_review(tmp_path, monkeypatch):
    backend_file = tmp_path / "libc"
    backend_file.write_bytes(b"fixture")
    m = metadata()
    m["libc_sha256"] = runner.hashlib.sha256(b"fixture").hexdigest()
    monkeypatch.setattr(runner.kernel, "LIBC", backend_file)
    monkeypatch.setattr(runner.kernel, "native_backend", lambda: (None, m))
    monkeypatch.setattr(runner, "source_hashes", lambda: {"fixture": "a" * 64})
    saved = fixture()
    monkeypatch.setattr(runner, "record_packet", lambda p, q, s, i: p.append(saved[i]))
    gaps = []
    monkeypatch.setattr(runner.time, "sleep", gaps.append)
    report = dict(
        protocol=kernel.PROTOCOL,
        packets=[],
        planned_reads=16,
        spacing_seconds=1,
        clock_settings_modified=False,
        sensor_started=False,
    )
    runner.observe(report)
    assert report["status"] == "observed" and gaps == [1] * 15
    assert (
        runner.review(json.dumps(report).encode())["local_consistency_verified"] is True
    )
    report["summary"]["state_read_count"] = 32.0
    with pytest.raises(ValueError, match="summary"):
        runner.review(json.dumps(report).encode())


def test_cli_refuses_overwrite_and_preserves_failed_stage(tmp_path, monkeypatch):
    target = tmp_path / "new.json"
    monkeypatch.setattr(runner.sys, "argv", ["kernel", "--output", str(target)])

    def fail(report):
        report["phase"] = "backend"
        raise ValueError("private details")

    monkeypatch.setattr(runner, "observe", fail)
    assert runner.main() == 1
    before = target.read_bytes()
    assert b"private" not in before and b'"phase": "backend"' in before
    with pytest.raises(FileExistsError):
        runner.main()
    assert target.read_bytes() == before


@pytest.mark.parametrize("mode", ["root", "version", "valid"])
def test_native_backend_guards_without_native_queries(tmp_path, monkeypatch, mode):
    class Function:
        def __call__(self):
            return b"2.40" if mode == "version" else b"2.39"

    class Library:
        gnu_get_libc_version = Function()
        adjtimex = Function()

    library = Library()
    backend = tmp_path / "libc"
    backend.write_bytes(b"synthetic")
    monkeypatch.setattr(kernel, "LIBC", backend)
    monkeypatch.setattr(kernel.sys, "platform", "linux")
    monkeypatch.setattr(kernel.platform, "machine", lambda: "x86_64")
    monkeypatch.setattr(
        kernel.os, "geteuid", lambda: 0 if mode == "root" else 1000, raising=False
    )
    monkeypatch.setattr(kernel.ctypes, "c_long", ctypes.c_int64)
    loads = []
    monkeypatch.setattr(
        kernel.ctypes, "CDLL", lambda *a, **k: loads.append((a, k)) or library
    )
    if mode != "valid":
        with pytest.raises(ValueError):
            kernel.native_backend()
        assert len(loads) == (0 if mode == "root" else 1)
    else:
        query, m = kernel.native_backend()
        assert query is library.adjtimex
        assert (
            query.argtypes == [ctypes.POINTER(kernel.Timex)]
            and query.restype is ctypes.c_int
        )
        kernel.checked_metadata(m)
        assert loads == [((str(backend),), dict(use_errno=True))]


def test_first_pair_failure_stops_all_later_reads(monkeypatch):
    monkeypatch.setattr(runner, "source_hashes", lambda: {"fixture": "a" * 64})
    monkeypatch.setattr(kernel, "native_backend", lambda: (None, metadata()))
    calls, gaps = [], []

    def fail(packets, query, sources, index):
        calls.append(index)
        raise ValueError("synthetic first failure")

    monkeypatch.setattr(runner, "record_packet", fail)
    monkeypatch.setattr(runner.time, "sleep", gaps.append)
    with pytest.raises(ValueError):
        runner.observe(dict(packets=[]))
    assert calls == [0] and gaps == []


def test_interruption_retains_partial_packet_and_cli_receipt(tmp_path, monkeypatch):
    def interrupted(query, *, evidence):
        evidence["raw_before_ns"] = 100
        raise KeyboardInterrupt()

    monkeypatch.setattr(kernel, "state_sample", interrupted)
    target = tmp_path / "interrupted.json"
    monkeypatch.setattr(runner.sys, "argv", ["kernel", "--output", str(target)])

    def observe(report):
        report["phase"] = "pairs"
        runner.record_packet(report["packets"], None, {}, 0)

    monkeypatch.setattr(runner, "observe", observe)
    assert runner.main() == 1
    report = json.loads(target.read_bytes())
    assert report["error_type"] == "KeyboardInterrupt"
    assert report["packets"][0]["before"] == dict(raw_before_ns=100)
    assert report["packets"][0]["status"] == "failed"
