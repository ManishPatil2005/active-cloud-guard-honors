"""Synthetic ML software contracts, not independent threat/accuracy evidence."""

import builtins
import copy
from contextlib import nullcontext
import json
import math
import subprocess
import sys

import pytest

from cloudguard import runtime, runtime_ml as ml
from test_runtime_intake import ROOT, save


@pytest.fixture
def bundle(tmp_path):
    return make_bundle(tmp_path)


def make_bundle(tmp_path):
    root = tmp_path / "ml"
    root.mkdir()
    for target, source in (
        ("train.json", "ml-baseline-synthetic.json"),
        ("observation.json", "ml-observation-synthetic.json"),
    ):
        save(root, target, json.loads((ROOT / "data/runtime" / source).read_text()))
    save(
        root,
        "inventory.json",
        [{"asset_id": "compose/redis", "host": "127.0.0.1", "port": 16379}],
    )
    return root


@pytest.fixture
def dependency():
    pytest.importorskip("sklearn", reason="optional runtime-ml extra not installed")


def execute(root, **options):
    return ml.compare_synthetic(
        [root / "train.json"],
        root / "observation.json",
        root / "inventory.json",
        **options,
    )


def edit(root, filename, change):
    value = json.loads((root / filename).read_text())
    change(value)
    save(root, filename, value)


def fake_backend(monkeypatch, score=-0.5, callback=None):
    models = []

    class Forest:
        def __init__(self, **parameters):
            self.parameters = parameters
            models.append(self)

        def fit(self, matrix):
            self.training = copy.deepcopy(matrix)
            return self

        def score_samples(self, matrix):
            self.observations = copy.deepcopy(matrix)
            if callback:
                callback()
            return [score] * len(matrix)

    monkeypatch.setattr(ml, "_backend", lambda: (Forest, lambda **_: nullcontext()))
    monkeypatch.setattr(ml.metadata, "version", lambda _: ml.SKLEARN_VERSION)
    return models


@pytest.mark.parametrize(
    "name,value",
    [
        ("seed", -1),
        ("seed", 2**32),
        ("seed", True),
        ("seed", 3.1),
        ("n_estimators", 0),
        ("n_estimators", 129),
        ("n_estimators", True),
        ("n_estimators", 2.5),
        ("max_samples", 1),
        ("max_samples", 257),
        ("max_samples", True),
        ("max_samples", None),
        ("window_seconds", 0),
        ("window_seconds", 3601),
        ("window_seconds", True),
        ("window_seconds", 1.1),
    ],
)
def test_bounded_exact_parameters(bundle, name, value):
    with pytest.raises(ValueError):
        execute(bundle, **{name: value})


@pytest.mark.parametrize("paths", [[], ["unused"] * 21, None])
def test_baseline_path_bound_before_loading(bundle, paths):
    with pytest.raises(ValueError):
        ml.compare_synthetic(
            paths, bundle / "observation.json", bundle / "inventory.json"
        )


@pytest.mark.parametrize("filename", ["train.json", "observation.json"])
def test_declared_sensor_export_refused_before_backend(bundle, monkeypatch, filename):
    edit(
        bundle, filename, lambda value: value.update(source="normalized_sensor_export")
    )
    monkeypatch.setattr(ml, "_backend", lambda: pytest.fail("must not import or fit"))
    with pytest.raises(ValueError, match="synthetic data only"):
        execute(bundle)


@pytest.mark.parametrize("violation", ["identity", "group", "events"])
def test_existing_leakage_checks_remain_active(bundle, violation):
    train = json.loads((bundle / "train.json").read_text())
    if violation == "identity":
        edit(
            bundle,
            "observation.json",
            lambda value: value.update(capture_id=train["capture_id"]),
        )
    elif violation == "group":
        edit(
            bundle,
            "observation.json",
            lambda value: value.update(scenario_group=train["scenario_group"]),
        )
    else:
        edit(
            bundle,
            "observation.json",
            lambda value: value.update(events=train["events"]),
        )
    with pytest.raises(ValueError):
        execute(bundle)


def test_only_baseline_rows_fit_and_no_binary_prediction(bundle, monkeypatch):
    models = fake_backend(monkeypatch)
    result = execute(bundle)
    assert len(models) == 1
    model = models[0]
    assert len(model.training) == 32 and len(model.observations) == 3
    assert model.observations[1] == [19, 1, 16, 2]
    assert max(row[2] for row in model.training) == 3
    assert model.parameters == dict(
        n_estimators=64,
        max_samples=32,
        max_features=1.0,
        contamination="auto",
        bootstrap=False,
        random_state=42,
        n_jobs=1,
        warm_start=False,
    )
    assert result["feature_order"] == list(runtime.FEATURES)
    assert result["evidence_level"] == "synthetic_software_only"
    assert result["synthetic_fitting_performed"] is True
    for key in (
        "real_data_fitting_authorized",
        "independent_evaluation_verified",
        "supervisor_approval_verified",
        "labels_created",
        "calibrated",
        "threat_confirmed",
        "runtime_sensor_connected",
    ):
        assert result[key] is False
    assert result["actions_executed"] == []
    assert all(row["binary_prediction"] is None for row in result["windows"])
    assert all(row["isolation_score"] == 0.5 for row in result["windows"])


def test_observation_change_cannot_change_training_rows(bundle, monkeypatch):
    models = fake_backend(monkeypatch)
    execute(bundle)
    edit(bundle, "observation.json", lambda value: value["events"].pop())
    execute(bundle)
    assert models[0].training == models[1].training
    assert models[0].observations != models[1].observations


@pytest.mark.parametrize(
    "kind", ["empty_observation", "few_training_windows", "constant_training"]
)
def test_missing_or_uninformative_windows_abstain_without_backend(
    bundle, monkeypatch, kind
):
    if kind == "empty_observation":
        edit(bundle, "observation.json", lambda value: value.update(events=[]))
    elif kind == "few_training_windows":
        edit(
            bundle,
            "train.json",
            lambda value: value.update(
                events=[
                    event
                    for event in value["events"]
                    if int(event["timestamp"][14:16]) < 7
                ]
            ),
        )
    else:

        def constant(value):
            selected = {}
            for event in value["events"]:
                selected.setdefault(event["timestamp"][:16], event)
            value["events"] = list(selected.values())

        edit(bundle, "train.json", constant)
    monkeypatch.setattr(ml, "_backend", lambda: pytest.fail("no model should fit"))
    result = execute(bundle)
    assert result["fitted_assets"] == []
    assert result["synthetic_fitting_performed"] is False
    assert result["synthetic_scoring_performed"] is False
    assert result["scored_window_count"] == 0
    assert result["abstained_window_count"] == len(result["windows"])
    assert all(row["isolation_score"] is None for row in result["windows"])
    if kind == "empty_observation":
        assert result["windows"] == [] and result["status"] == "no_observations"
    else:
        expected = (
            "insufficient_synthetic_baseline"
            if kind == "few_training_windows"
            else "uninformative_synthetic_baseline"
        )
        assert {row["status"] for row in result["windows"]} == {expected}
        assert result["status"] == "synthetic_scoring_abstained"


@pytest.mark.parametrize("score", [math.nan, math.inf, -math.inf, 0.1, -1.1])
def test_bad_backend_scores_fail_not_fabricate(bundle, monkeypatch, score):
    fake_backend(monkeypatch, score=score)
    with pytest.raises(RuntimeError, match="invalid synthetic isolation score"):
        execute(bundle)


def test_training_window_resource_bound(bundle, monkeypatch):
    monkeypatch.setattr(ml, "TRAIN_WINDOW_LIMIT", 31)
    with pytest.raises(ValueError, match="window limit"):
        execute(bundle)


@pytest.mark.parametrize(
    "filename", ["train.json", "observation.json", "inventory.json"]
)
def test_mutation_during_scoring_refused(bundle, monkeypatch, filename):
    def mutate():
        path = bundle / filename
        path.write_bytes(path.read_bytes() + b" ")

    fake_backend(monkeypatch, callback=mutate)
    with pytest.raises(ValueError, match="changed"):
        execute(bundle)


def test_dependency_version_mismatch(bundle, dependency, monkeypatch):
    monkeypatch.setattr(ml.metadata, "version", lambda _: "not-the-pin")
    with pytest.raises(RuntimeError, match="version mismatch"):
        execute(bundle)


def test_missing_optional_dependency_has_no_fallback(monkeypatch):
    original = builtins.__import__

    def blocked(name, *args, **kwargs):
        if name == "sklearn.ensemble":
            raise ImportError("private environment must not leak")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked)
    with pytest.raises(RuntimeError, match="optional runtime-ml"):
        ml._backend()


def test_actual_backend_deterministic_and_statistical_result_unchanged(
    bundle, dependency
):
    first = execute(bundle)
    edit(bundle, "train.json", lambda value: value["events"].reverse())
    second = execute(bundle)
    assert first["windows"] == second["windows"]
    assert all(0 <= row["isolation_score"] <= 1 for row in first["windows"])
    assert second["statistical_comparator"] == runtime.analyze(
        [bundle / "train.json"], bundle / "observation.json", bundle / "inventory.json"
    )
    assert (
        first["statistical_comparator"]["windows"]
        == second["statistical_comparator"]["windows"]
    )
    assert (
        first["statistical_comparator"]["baseline"][0]["sha256"]
        != second["statistical_comparator"]["baseline"][0]["sha256"]
    )
    assert first["dependency_versions"]["scikit-learn"] == ml.SKLEARN_VERSION


def test_actual_scores_match_established_backend(bundle, dependency):
    from sklearn.ensemble import IsolationForest
    from threadpoolctl import threadpool_limits
    from cloudguard.verification import load_inventory

    assets, _ = load_inventory(bundle / "inventory.json")
    train = runtime.windows(runtime.load_capture(bundle / "train.json", assets), 60)
    obs = runtime.windows(runtime.load_capture(bundle / "observation.json", assets), 60)
    forest = IsolationForest(n_estimators=64, max_samples=32, random_state=42, n_jobs=1)
    with threadpool_limits(limits=1):
        forest.fit(
            [[row["counts"][name] for name in runtime.FEATURES] for row in train]
        )
        expected = [
            -float(value)
            for value in forest.score_samples(
                [[row["counts"][name] for name in runtime.FEATURES] for row in obs]
            )
        ]
    assert [row["isolation_score"] for row in execute(bundle)["windows"]] == [
        round(value, 6) for value in expected
    ]


def test_default_engine_report_still_matches_saved_evidence():
    result = runtime.analyze(
        [ROOT / "data/runtime/baseline-synthetic.json"],
        ROOT / "data/runtime/observation-synthetic.json",
        ROOT / "testbed/inventory.json",
    )
    old = json.loads(
        (ROOT / "output/engine2-status-clarification-replay-20261006.json").read_text()
    )
    assert result == old["result"]


def test_assets_fit_separately(bundle, monkeypatch):
    other = "b" * 64

    def extend(value, kind):
        value["bindings"].append(dict(container_id=other, asset_id="compose/web"))
        value["events"].extend(
            [
                dict(event, event_id=event["event_id"] + "-other", container_id=other)
                for event in list(value["events"])
                if event["kind"] == kind
            ]
        )

    edit(bundle, "train.json", lambda value: extend(value, "file_open"))
    edit(bundle, "observation.json", lambda value: extend(value, "network_connect"))
    assets = json.loads((bundle / "inventory.json").read_text())
    assets.append(dict(asset_id="compose/web", host="127.0.0.1", port=18080))
    save(bundle, "inventory.json", assets)
    models = fake_backend(monkeypatch)
    result = execute(bundle)
    assert len(models) == len(result["fitted_assets"]) == 2
    assert len(result["windows"]) == 6
    assert all(row[1] == row[2] == 0 and row[0] == row[3] for row in models[1].training)
    assert all(
        row[1] == row[3] == 0 and row[0] == row[2] for row in models[1].observations
    )
    assert models[0].training != models[1].training


def test_valid_parameter_extremes_and_no_saved_model(bundle, dependency):
    before = {path.name for path in bundle.iterdir()}
    result = execute(bundle, seed=2**32 - 1, n_estimators=1, max_samples=2)
    assert all(row["isolation_score"] is not None for row in result["windows"])
    assert {path.name for path in bundle.iterdir()} == before
    assert "estimators_" not in json.dumps(result)


def test_partial_asset_scoring_keeps_abstention_denominator(bundle, monkeypatch):
    def add_observed_asset(value):
        value["bindings"].append(dict(container_id="b" * 64, asset_id="compose/web"))
        value["events"].extend(
            [
                dict(
                    event, event_id=event["event_id"] + "-other", container_id="b" * 64
                )
                for event in list(value["events"])
            ]
        )

    edit(bundle, "observation.json", add_observed_asset)
    assets = json.loads((bundle / "inventory.json").read_text())
    assets.append(dict(asset_id="compose/web", host="127.0.0.1", port=18080))
    save(bundle, "inventory.json", assets)
    models = fake_backend(monkeypatch)
    result = execute(bundle)
    assert len(models) == 1 and len(result["windows"]) == 6
    assert result["status"] == "synthetic_scores_computed"
    assert result["scored_window_count"] == result["abstained_window_count"] == 3
    assert sum(row["isolation_score"] is None for row in result["windows"]) == 3


def test_fixed_cli_no_overwrite(tmp_path, dependency):
    output = tmp_path / "fresh.json"
    args = [
        sys.executable,
        str(ROOT / "scripts/runtime_ml_check.py"),
        "--output",
        str(output),
    ]
    result = subprocess.run(args, capture_output=True, text=True)
    assert result.returncode == 0 and not result.stderr
    before = output.read_bytes()
    report = json.loads(before)
    assert all(report["checks"].values())
    assert report["evidence_level"] == "synthetic_software_only"
    result = subprocess.run(args, capture_output=True, text=True)
    assert result.returncode == 1 and not result.stderr
    assert json.loads(result.stdout)["error_type"] == "FileExistsError"
    assert output.read_bytes() == before
