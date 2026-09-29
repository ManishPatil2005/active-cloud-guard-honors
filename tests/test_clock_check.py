import pytest
import json
import sys
from cloudguard.clock_check import sample, compare
from scripts import workload_control


def test_bracket():
    values = iter([100, 120])
    assert sample(lambda: next(values), lambda: 500) == dict(
        wall_ns=500, monotonic_mid_ns=110, sampling_span_ns=20
    )


def test_backwards():
    values = iter([2, 1])
    with pytest.raises(ValueError):
        sample(lambda: next(values), lambda: 10)


@pytest.mark.parametrize(
    "drift,span,valid",
    [
        (0, 100, True),
        (60_000_000, 100, False),
        (0, 6_000_000, False),
        (49_999_999, 100, False),
    ],
)
def test_conservative_uncertainty(drift, span, valid):
    a = dict(wall_ns=10**18, monotonic_mid_ns=0, sampling_span_ns=span)
    b = dict(
        wall_ns=10**18 + 4 * 10**9 + drift,
        monotonic_mid_ns=4 * 10**9,
        sampling_span_ns=span,
    )
    assert compare(a, b)["within_tolerance"] is valid


@pytest.mark.parametrize("running", [False, True])
def test_control_refuses_known_sensor(monkeypatch, running):
    monkeypatch.setattr(
        workload_control, "command", lambda *a: "sensor" if running else ""
    )
    if running:
        with pytest.raises(ValueError):
            workload_control.check_sensor_absent()
    else:
        workload_control.check_sensor_absent()


def test_failed_clock_gate_prevents_docker(tmp_path, monkeypatch):
    diagnostic = tmp_path / "clock.json"
    diagnostic.write_text(json.dumps(dict(status="timing_rejected")))
    output = tmp_path / "control.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "control",
            "--profile",
            "ping_1",
            "--output",
            str(output),
            "--clock-report",
            str(diagnostic),
        ],
    )
    monkeypatch.setattr(
        workload_control, "local_daemon", lambda: pytest.fail("Docker must not run")
    )
    with pytest.raises(ValueError, match="passing clock"):
        workload_control.main()
    assert json.loads(output.read_text())["status"] == "failed"
