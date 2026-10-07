from pathlib import Path
import json
import subprocess
import sys
from unittest.mock import patch

import pytest

from cloudguard import integration, runtime_ml, runtime_autoencoder

ROOT = Path(__file__).resolve().parents[1]


def replay(**options):
    return integration.replay(
        ROOT / "data/integration/redis-auth-only.yaml",
        [ROOT / "data/runtime/ml-baseline-synthetic.json"],
        ROOT / "data/runtime/ml-observation-synthetic.json",
        ROOT / "testbed/inventory.json",
        **options,
    )


@pytest.mark.parametrize("selection", [False, True, 1, [], "unknown", ""])
def test_invalid_selection(selection):
    with pytest.raises(ValueError, match="selection"):
        replay(runtime_ml=selection)


@pytest.mark.parametrize("selection", ["isolation-forest", "autoencoder", "both"])
def test_actual_comparators(selection):
    result = replay(runtime_ml=selection, threshold=7)
    assert result["engine2"]["windows"]
    assert result["joint_priority_calculated"] is False
    assert result["actions_executed"] == []
    for name, report in result["runtime_comparators"].items():
        compare = (
            runtime_ml.compare_synthetic
            if name == "isolation_forest"
            else runtime_autoencoder.compare_synthetic
        )
        direct = compare(
            [ROOT / "data/runtime/ml-baseline-synthetic.json"],
            ROOT / "data/runtime/ml-observation-synthetic.json",
            ROOT / "testbed/inventory.json",
        )
        assert report == direct
        assert report["scored_window_count"] + report["abstained_window_count"] == 3
        assert all(w["binary_prediction"] is None for w in report["windows"])
        redis = next(
            a for a in result["asset_contexts"] if a["asset_id"] == "compose/redis"
        )
        assert redis["runtime_comparator_window_indices"][name] == [0, 1, 2]


def test_default_does_not_import_or_fit():
    with patch.object(runtime_ml, "compare_synthetic", side_effect=AssertionError):
        assert "runtime_comparators" not in replay()


def test_model_failure_prevents_pipeline():
    with (
        patch.object(runtime_ml, "compare_synthetic", side_effect=RuntimeError),
        patch("cloudguard.pipeline.run") as run,
    ):
        with pytest.raises(RuntimeError):
            replay(
                runtime_ml="both",
                engine1_pipeline=True,
                kb=ROOT / "knowledge/sources.json",
            )
        run.assert_not_called()


def test_sensor_declaration_refused_before_fit_or_pipeline():
    original = integration.analyze_runtime

    def declared_sensor(*args, **kwargs):
        result = original(*args, **kwargs)
        result["observation"]["source"] = "sensor"
        return result

    with (
        patch.object(integration, "analyze_runtime", side_effect=declared_sensor),
        patch.object(runtime_ml, "compare_synthetic") as fit,
        patch("cloudguard.pipeline.run") as run,
    ):
        with pytest.raises(ValueError, match="synthetic data only"):
            replay(
                runtime_ml="both",
                engine1_pipeline=True,
                kb=ROOT / "knowledge/sources.json",
            )
        fit.assert_not_called()
        run.assert_not_called()


@pytest.mark.parametrize("defect", ["window", "count", "input", "source"])
def test_component_mismatch_refused(defect):
    original = runtime_ml.compare_synthetic

    def corrupt(*args, **kwargs):
        result = original(*args, **kwargs)
        if defect == "window":
            result["windows"][0]["start_epoch"] += 1
        elif defect == "count":
            result["scored_window_count"] += 1
        elif defect == "input":
            result["statistical_comparator"]["inventory_sha256"] = "0" * 64
        else:
            result["implementation_sha256"]["runtime_ml.py"] = "0" * 64
        return result

    with patch.object(runtime_ml, "compare_synthetic", side_effect=corrupt):
        with pytest.raises(ValueError, match="mismatch"):
            replay(runtime_ml="isolation-forest")


def test_ml_cli_and_fixed_runner(tmp_path):
    command = [
        sys.executable,
        "-m",
        "cloudguard.cli",
        "integrated-replay",
        str(ROOT / "data/integration/redis-auth-only.yaml"),
        str(ROOT / "data/runtime/ml-observation-synthetic.json"),
        "--baseline",
        str(ROOT / "data/runtime/ml-baseline-synthetic.json"),
        "--inventory",
        str(ROOT / "testbed/inventory.json"),
        "--runtime-ml",
        "both",
    ]
    cli = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=True)
    assert set(json.loads(cli.stdout)["runtime_comparators"]) == {
        "isolation_forest",
        "autoencoder",
    }
    output = tmp_path / "fresh.json"
    command = [
        sys.executable,
        str(ROOT / "scripts/integration_check.py"),
        "--engine1-pipeline",
        "--runtime-ml",
        "both",
        "--output",
        str(output),
    ]
    subprocess.run(command, cwd=ROOT, capture_output=True, check=True)
    raw = output.read_bytes()
    assert all(json.loads(raw)["checks"].values())
    assert subprocess.run(command, cwd=ROOT, capture_output=True).returncode == 1
    assert output.read_bytes() == raw
