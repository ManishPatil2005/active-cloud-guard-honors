"""Reconstruction software checks; no independent threat labels or evaluation."""

import builtins
import copy
from contextlib import nullcontext
import json
import math
import subprocess
import sys
import warnings

import pytest

from cloudguard import runtime_autoencoder as ae, runtime_ml as shared
from test_runtime_ml import ROOT, make_bundle, edit, save


@pytest.fixture
def bundle(tmp_path):
    return make_bundle(tmp_path)


@pytest.fixture
def dependency():
    pytest.importorskip("sklearn", reason="optional runtime-ml extra not installed")


def execute(root, **options):
    return ae.compare_synthetic(
        [root / "train.json"],
        root / "observation.json",
        root / "inventory.json",
        **options,
    )


def fake_backend(
    monkeypatch,
    *,
    warning=None,
    shape=None,
    value=None,
    iterations=None,
    loss=0.02,
    callback=None,
):
    models, scalers = [], []

    class Convergence(UserWarning):
        pass

    class Scaler:
        def __init__(self):
            scalers.append(self)

        def fit_transform(self, rows):
            self.training = copy.deepcopy(rows)
            if warning == "scaler":
                warnings.warn("private scaler warning", UserWarning)
            return copy.deepcopy(rows)

        def transform(self, rows):
            self.observations = copy.deepcopy(rows)
            if warning == "transform":
                warnings.warn("private transform warning", UserWarning)
            return copy.deepcopy(rows)

    class Model:
        def __init__(self, **parameters):
            self.parameters = parameters
            models.append(self)

        def fit(self, x, y):
            self.training, self.targets = copy.deepcopy(x), copy.deepcopy(y)
            self.n_iter_ = (
                min(3, self.parameters["max_iter"])
                if iterations is None
                else iterations
            )
            self.loss_ = loss
            if warning in {"convergence", "other"}:
                warnings.warn(
                    "private warning text must not leak",
                    Convergence if warning == "convergence" else UserWarning,
                )
            if callback:
                callback()
            return self

        def predict(self, rows):
            self.observations = copy.deepcopy(rows)
            if warning == "predict":
                warnings.warn("private predict warning", UserWarning)
            if shape == "short":
                return rows[:-1]
            if shape == "narrow":
                return [row[:-1] for row in rows]
            return [
                [component + 1 if value is None else value for component in row]
                for row in rows
            ]

    monkeypatch.setattr(
        ae, "_backend", lambda: (Model, Scaler, Convergence, lambda **_: nullcontext())
    )
    monkeypatch.setattr(
        shared, "_dependency_versions", lambda: {"scikit-learn": shared.SKLEARN_VERSION}
    )
    return models, scalers


@pytest.mark.parametrize(
    "name,value",
    [
        ("seed", -1),
        ("seed", 2**32),
        ("seed", True),
        ("seed", 2.5),
        ("latent_dim", 0),
        ("latent_dim", 4),
        ("latent_dim", True),
        ("latent_dim", 1.5),
        ("max_iter", 0),
        ("max_iter", 2001),
        ("max_iter", True),
        ("max_iter", 1.5),
        ("window_seconds", 0),
        ("window_seconds", 3601),
        ("window_seconds", True),
        ("window_seconds", 1.5),
    ],
)
def test_parameters_exact_and_bounded(bundle, name, value):
    with pytest.raises(ValueError):
        execute(bundle, **{name: value})


def test_scaler_targets_and_network_fit_only_baseline(bundle, monkeypatch):
    models, scalers = fake_backend(monkeypatch)
    result = execute(bundle)
    model, scaler = models[0], scalers[0]
    assert model.training == model.targets == scaler.training
    assert len(model.training) == 32 and len(model.observations) == 3
    assert max(row[2] for row in model.training) == 3
    assert model.observations[1][2] == 16
    assert model.parameters["hidden_layer_sizes"] == (2,)
    assert model.parameters["solver"] == "lbfgs"
    assert model.parameters["early_stopping"] is False
    assert all(row["reconstruction_error"] == 1 for row in result["windows"])
    assert result["scored_window_count"] == 3 and result["abstained_window_count"] == 0
    for field in (
        "real_data_fitting_authorized",
        "supervisor_approval_verified",
        "independent_evaluation_verified",
        "labels_created",
        "calibrated",
        "threat_confirmed",
        "runtime_sensor_connected",
    ):
        assert result[field] is False
    assert result["actions_executed"] == []
    assert all(row["binary_prediction"] is None for row in result["windows"])


def test_observation_changes_do_not_fit_scaler_or_model(bundle, monkeypatch):
    models, scalers = fake_backend(monkeypatch)
    execute(bundle)
    edit(bundle, "observation.json", lambda value: value["events"].pop())
    execute(bundle)
    assert models[0].training == models[1].training
    assert scalers[0].training == scalers[1].training
    assert models[0].observations != models[1].observations


@pytest.mark.parametrize("warning", ["convergence", "other", "scaler"])
def test_training_warnings_abstain_but_record_actual_attempt(
    bundle, monkeypatch, warning
):
    models, scalers = fake_backend(monkeypatch, warning=warning)
    result = execute(bundle)
    assert result["synthetic_fitting_performed"] is True
    assert result["synthetic_scoring_performed"] is False
    assert result["status"] == "synthetic_scoring_abstained"
    assert result["scored_window_count"] == 0 and result["abstained_window_count"] == 3
    assert not hasattr(models[0], "observations") and not hasattr(
        scalers[0], "observations"
    )
    assert result["training_attempts"][0]["warning_count"] == 1
    assert result["training_attempts"][0]["convergence_warning"] is (
        warning == "convergence"
    )
    assert "private warning" not in json.dumps(result)


@pytest.mark.parametrize("kind", ["empty", "few", "constant"])
def test_baseline_and_empty_abstention_without_training(bundle, monkeypatch, kind):
    if kind == "empty":
        edit(bundle, "observation.json", lambda value: value.update(events=[]))
    elif kind == "few":
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
    monkeypatch.setattr(ae, "_backend", lambda: pytest.fail("must not train"))
    result = execute(bundle)
    assert (
        result["training_attempts"] == []
        and result["synthetic_fitting_performed"] is False
    )
    assert result["scored_window_count"] == 0
    assert result["abstained_window_count"] == len(result["windows"])
    assert result["status"] == (
        "no_observations" if kind == "empty" else "synthetic_scoring_abstained"
    )


@pytest.mark.parametrize("filename", ["train.json", "observation.json"])
def test_real_source_refused_before_backend(bundle, monkeypatch, filename):
    edit(
        bundle, filename, lambda value: value.update(source="normalized_sensor_export")
    )
    monkeypatch.setattr(ae, "_backend", lambda: pytest.fail("must not train"))
    with pytest.raises(ValueError, match="synthetic data only"):
        execute(bundle)


@pytest.mark.parametrize("shape", ["short", "narrow"])
def test_bad_reconstruction_shape_refused(bundle, monkeypatch, shape):
    fake_backend(monkeypatch, shape=shape)
    with pytest.raises(RuntimeError, match="reconstruction"):
        execute(bundle)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf, 1e308])
def test_nonfinite_reconstruction_refused(bundle, monkeypatch, value):
    fake_backend(monkeypatch, value=value)
    with pytest.raises(RuntimeError):
        execute(bundle)


@pytest.mark.parametrize(
    "iterations,loss",
    [(0, 0.1), (501, 0.1), (True, 0.1), (2.5, 0.1), (3, math.nan), (3, -0.1)],
)
def test_bad_optimizer_diagnostics_refused(bundle, monkeypatch, iterations, loss):
    fake_backend(monkeypatch, iterations=iterations, loss=loss)
    with pytest.raises(RuntimeError, match="training diagnostics"):
        execute(bundle)


@pytest.mark.parametrize(
    "filename", ["train.json", "observation.json", "inventory.json"]
)
def test_training_mutation_refused_postflight(bundle, monkeypatch, filename):
    def mutate():
        path = bundle / filename
        path.write_bytes(path.read_bytes() + b" ")

    fake_backend(monkeypatch, callback=mutate)
    with pytest.raises(ValueError, match="changed"):
        execute(bundle)


def test_actual_reconstruction_matches_backend_and_is_deterministic(bundle, dependency):
    from sklearn.neural_network import MLPRegressor
    from sklearn.preprocessing import StandardScaler
    from threadpoolctl import threadpool_limits

    context = shared._prepare_synthetic(
        [bundle / "train.json"],
        bundle / "observation.json",
        bundle / "inventory.json",
        60,
    )
    scaler = StandardScaler()
    model = MLPRegressor(
        hidden_layer_sizes=(2,),
        activation="tanh",
        solver="lbfgs",
        alpha=0.0001,
        tol=0.0001,
        max_iter=500,
        max_fun=10000,
        random_state=42,
        shuffle=False,
        early_stopping=False,
        warm_start=False,
    )
    matrix = [
        [row["counts"][name] for name in shared.runtime.FEATURES]
        for row in context["grouped"]["compose/redis"]
    ]
    with warnings.catch_warnings(record=True) as recorded, threadpool_limits(limits=1):
        scaled = scaler.fit_transform(context["training"]["compose/redis"])
        model.fit(scaled, scaled)
        obs = scaler.transform(matrix)
        rebuilt = model.predict(obs)
    assert not recorded
    expected = [
        sum((float(a) - float(b)) ** 2 for a, b in zip(x, y, strict=True)) / 4
        for x, y in zip(obs, rebuilt, strict=True)
    ]
    result = execute(bundle)
    assert [row["reconstruction_error"] for row in result["windows"]] == pytest.approx(
        expected, rel=1e-12, abs=1e-12
    )
    assert [weights.shape for weights in model.coefs_] == [(4, 2), (2, 4)]
    assert result["windows"] == execute(bundle)["windows"]
    assert result["statistical_comparator"] == context["statistical"]


def test_iforest_calculated_report_unchanged_after_shared_refactor(dependency):
    result = shared.compare_synthetic(
        [ROOT / "data/runtime/ml-baseline-synthetic.json"],
        ROOT / "data/runtime/ml-observation-synthetic.json",
        ROOT / "testbed/inventory.json",
    )
    old = json.loads(
        (
            ROOT / "output/engine2-synthetic-iforest-windows-final-20261006.json"
        ).read_text()
    )["result"]
    result.pop("implementation_sha256")
    old.pop("implementation_sha256")
    result["dependency_versions"].pop("python")
    old["dependency_versions"].pop("python")
    assert result == old


def test_cli_no_overwrite_or_model_files(tmp_path, dependency):
    output = tmp_path / "fresh.json"
    args = [
        sys.executable,
        str(ROOT / "scripts/runtime_autoencoder_check.py"),
        "--output",
        str(output),
    ]
    result = subprocess.run(args, capture_output=True, text=True)
    assert result.returncode == 0 and not result.stderr
    before = output.read_bytes()
    report = json.loads(before)
    assert all(report["checks"].values())
    assert report["result"]["synthetic_fitting_performed"] is True
    assert {path.name for path in tmp_path.iterdir()} == {"fresh.json"}
    result = subprocess.run(args, capture_output=True, text=True)
    assert result.returncode == 1 and not result.stderr
    assert output.read_bytes() == before


def test_missing_optional_dependency(monkeypatch):
    original = builtins.__import__

    def blocked(name, *args, **kwargs):
        if name == "sklearn.neural_network":
            raise ImportError("private details")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked)
    with pytest.raises(RuntimeError, match="optional runtime-ml"):
        ae._backend()


@pytest.mark.parametrize("warning", ["transform", "predict"])
def test_reconstruction_warnings_abstain_and_record_attempt(
    bundle, monkeypatch, warning
):
    fake_backend(monkeypatch, warning=warning)
    result = execute(bundle)
    assert result["status"] == "synthetic_scoring_abstained"
    assert result["synthetic_fitting_performed"] is True
    assert result["synthetic_scoring_performed"] is False
    assert result["abstained_window_count"] == 3
    attempt = result["training_attempts"][0]
    assert attempt["warning_count"] == 0
    assert attempt["reconstruction_attempted"] is True
    assert attempt["reconstruction_warning_count"] == 1
    assert "private" not in json.dumps(result)


def test_partial_asset_denominator(bundle, monkeypatch):
    def extend(value):
        value["bindings"].append(dict(container_id="b" * 64, asset_id="compose/web"))
        value["events"].extend(
            [
                dict(
                    event, event_id=event["event_id"] + "-other", container_id="b" * 64
                )
                for event in list(value["events"])
            ]
        )

    edit(bundle, "observation.json", extend)
    assets = json.loads((bundle / "inventory.json").read_text())
    assets.append(dict(asset_id="compose/web", host="127.0.0.1", port=18080))
    save(bundle, "inventory.json", assets)
    models, _ = fake_backend(monkeypatch)
    result = execute(bundle)
    assert len(models) == 1 and len(result["windows"]) == 6
    assert result["scored_window_count"] == result["abstained_window_count"] == 3


def test_actual_one_iteration_nonconvergence_is_not_a_score(bundle, dependency):
    result = execute(bundle, max_iter=1)
    assert result["status"] == "synthetic_scoring_abstained"
    assert result["synthetic_fitting_performed"] is True
    assert result["scored_window_count"] == 0 and result["abstained_window_count"] == 3
    assert result["training_attempts"][0]["convergence_warning"] is True
    assert result["training_attempts"][0]["reconstruction_attempted"] is False


def test_sub_micro_error_precision_retained(bundle, monkeypatch):
    # Direct tiny-error calculation and the report both retain small positive values.
    tiny = ae._errors([[1, 1, 1, 1]], [[1.00000001] * 4], 1)[0]
    assert 0 < tiny < 1e-12
    fake_backend(monkeypatch)

    # Scale all values to one, so the rebuilt output differs by only 1e-8.
    class Ones:
        def fit_transform(self, rows):
            return [[1.0] * 4 for _ in rows]

        def transform(self, rows):
            return [[1.0] * 4 for _ in rows]

    original = ae._backend
    Model, _, Convergence, limits = original()

    class TinyModel(Model):
        def predict(self, rows):
            return [[1.00000001] * 4 for _ in rows]

    monkeypatch.setattr(ae, "_backend", lambda: (TinyModel, Ones, Convergence, limits))
    result = execute(bundle)
    assert all(0 < row["reconstruction_error"] < 1e-12 for row in result["windows"])
