import copy
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

import pytest

from cloudguard import integration

ROOT = Path(__file__).resolve().parents[1]


def replay(**options):
    return integration.replay(
        ROOT / "data/integration/redis-auth-only.yaml",
        [ROOT / "data/runtime/ml-baseline-synthetic.json"],
        ROOT / "data/runtime/ml-observation-synthetic.json",
        ROOT / "testbed/inventory.json",
        **options,
    )


@pytest.mark.parametrize("value", [None, 0, 1, "true", [], {}])
def test_measurement_flag_strict(value):
    with pytest.raises(ValueError, match="boolean"):
        replay(measure_stages=value)


def test_disabled_reads_no_measurement_clocks():
    with patch.object(integration._Measurements, "_read", side_effect=AssertionError):
        assert "execution_cost" not in replay()


def test_known_clock_intervals_preserve_calculations():
    original = replay()
    # Total begin; rule begin/end; runtime begin/end; total end.
    with patch.object(
        integration._Measurements,
        "_read",
        side_effect=[(0, 0), (10, 2), (30, 8), (40, 10), (70, 17), (100, 25)],
    ):
        measured = replay(measure_stages=True)
    cost = measured.pop("execution_cost")
    assert measured == original
    assert cost["stages"] == {
        "configuration_rule_baseline": {"wall_ns": 20, "process_cpu_ns": 6},
        "runtime_statistical": {"wall_ns": 30, "process_cpu_ns": 7},
    }
    assert cost["total"] == {"wall_ns": 100, "process_cpu_ns": 25}


@pytest.mark.parametrize("end", [(-1, 0), (0, -1), (0.5, 0)])
def test_invalid_intervals_refused(end):
    with patch.object(
        integration._Measurements, "_read", side_effect=[(0, 0), (0, 0), end]
    ):
        with pytest.raises(ValueError, match="clock interval"):
            replay(measure_stages=True)


@pytest.mark.parametrize("pipeline", [False, True])
@pytest.mark.parametrize("selection", [None, "isolation-forest", "autoencoder", "both"])
def test_actual_selected_stage_scope(pipeline, selection):
    result = replay(
        measure_stages=True,
        runtime_ml=selection,
        engine1_pipeline=pipeline,
        kb=ROOT / "knowledge/sources.json" if pipeline else None,
    )
    cost = result["execution_cost"]
    expected = {"configuration_rule_baseline", "runtime_statistical"}
    if pipeline:
        expected.add("engine1_pipeline")
    expected.update(result.get("runtime_comparators", {}))
    assert set(cost["stages"]) == expected
    for metric in ("wall_ns", "process_cpu_ns"):
        assert all(
            type(row[metric]) is int and row[metric] >= 0
            for row in cost["stages"].values()
        )
        assert cost["total"][metric] >= sum(
            row[metric] for row in cost["stages"].values()
        )
    assert cost["sensor_overhead_evaluated"] is False
    assert cost["energy_measured"] is False
    assert cost["independent_performance_evaluation"] is False
    assert set(cost["clocks"]) == {"wall", "process_cpu"}
    assert result["threat_confirmed"] is False
    assert result["actions_executed"] == []
    assert all(a["combined_priority"] is None for a in result["asset_contexts"])


def test_pipeline_evidence_preserved_with_measurement():
    options = dict(engine1_pipeline=True, kb=ROOT / "knowledge/sources.json")
    original = replay(**options)
    measured = replay(**options, measure_stages=True)
    measured.pop("execution_cost")
    for report in (original, measured):
        report["engine1"].pop("timings_ms")
    assert measured == original


def test_failed_component_does_not_become_partial_success():
    with patch.object(
        integration, "analyze_runtime", side_effect=RuntimeError("injected")
    ):
        with pytest.raises(RuntimeError, match="injected"):
            replay(measure_stages=True)


def test_cli_and_exclusive_fixed_runner(tmp_path):
    args = [
        sys.executable,
        "-m",
        "cloudguard.cli",
        "integrated-replay",
        str(ROOT / "data/integration/redis-auth-only.yaml"),
        str(ROOT / "data/runtime/observation-synthetic.json"),
        "--baseline",
        str(ROOT / "data/runtime/baseline-synthetic.json"),
        "--inventory",
        str(ROOT / "testbed/inventory.json"),
        "--measure-stages",
    ]
    cli = subprocess.run(
        args, cwd=ROOT, capture_output=True, text=True, timeout=30, check=True
    )
    assert "execution_cost" in json.loads(cli.stdout)
    output = tmp_path / "fresh.json"
    args = [
        sys.executable,
        str(ROOT / "scripts/integration_check.py"),
        "--engine1-pipeline",
        "--measure-stages",
        "--output",
        str(output),
    ]
    subprocess.run(args, cwd=ROOT, capture_output=True, timeout=30, check=True)
    raw = output.read_bytes()
    report = json.loads(raw)
    assert len(report["checks"]) == 9 and all(report["checks"].values())
    assert (
        subprocess.run(args, cwd=ROOT, capture_output=True, timeout=30).returncode == 1
    )
    assert output.read_bytes() == raw


def test_clock_metadata_is_detached():
    measured = replay(measure_stages=True)
    previous = copy.deepcopy(measured["execution_cost"])
    again = replay(measure_stages=True)
    again["execution_cost"]["clocks"]["wall"]["name"] = "changed"
    assert measured["execution_cost"] == previous
