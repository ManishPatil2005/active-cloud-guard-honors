"""Undercomplete reconstruction MLP on declared synthetic data only."""

import hashlib
import math
from numbers import Integral
from pathlib import Path
import sys
import warnings

from cloudguard import runtime, runtime_ml as shared


def _backend():
    try:
        from sklearn.neural_network import MLPRegressor
        from sklearn.preprocessing import StandardScaler
        from sklearn.exceptions import ConvergenceWarning
        from threadpoolctl import threadpool_limits
    except ImportError as error:
        raise shared._import_failure(error) from None
    shared._verify_backend_version()
    return MLPRegressor, StandardScaler, ConvergenceWarning, threadpool_limits


def compare_synthetic(
    baseline_paths,
    observation_path,
    inventory,
    *,
    window_seconds=60,
    seed=42,
    latent_dim=2,
    max_iter=500,
):
    for value, low, high in (
        (seed, 0, 2**32 - 1),
        (latent_dim, 1, 3),
        (max_iter, 1, 2000),
        (window_seconds, 1, 3600),
    ):
        if type(value) is not int or not low <= value <= high:
            raise ValueError("invalid bounded synthetic autoencoder parameter")
    context = shared._prepare_synthetic(
        baseline_paths, observation_path, inventory, window_seconds
    )
    results, attempts = [], []
    for asset in sorted(context["grouped"]):
        rows, observed = context["training"][asset], context["grouped"][asset]
        status = shared._baseline_status(rows)
        errors = [None] * len(observed)
        if status == "uncalibrated_synthetic_score":
            MLP, Scaler, Convergence, limits = _backend()
            scaler = Scaler()
            model = MLP(
                hidden_layer_sizes=(latent_dim,),
                activation="tanh",
                solver="lbfgs",
                alpha=0.0001,
                tol=0.0001,
                max_iter=max_iter,
                max_fun=max_iter * 20,
                random_state=seed,
                shuffle=False,
                early_stopping=False,
                warm_start=False,
            )
            with limits(limits=1):
                with warnings.catch_warnings(record=True) as recorded:
                    warnings.simplefilter("always")
                    scaled = scaler.fit_transform(rows)
                    model.fit(scaled, scaled)
                iterations, loss = model.n_iter_, float(model.loss_)
                if (
                    isinstance(iterations, bool)
                    or not isinstance(iterations, Integral)
                    or not 1 <= iterations <= max_iter
                    or not math.isfinite(loss)
                    or loss < 0
                ):
                    raise RuntimeError("invalid synthetic training diagnostics")
                convergence = any(
                    issubclass(item.category, Convergence) for item in recorded
                )
                status = (
                    "synthetic_optimizer_not_converged"
                    if convergence
                    else "synthetic_training_warning"
                    if recorded
                    else "uncalibrated_synthetic_reconstruction"
                )
                attempts.append(
                    dict(
                        asset_id=asset,
                        training_window_count=len(rows),
                        iterations=int(iterations),
                        training_loss=loss,
                        warning_count=len(recorded),
                        convergence_warning=convergence,
                        training_status=status,
                        reconstruction_attempted=False,
                        reconstruction_warning_count=0,
                    )
                )
                if not recorded:
                    matrix = [
                        [row["counts"][name] for name in runtime.FEATURES]
                        for row in observed
                    ]
                    attempts[-1]["reconstruction_attempted"] = True
                    with warnings.catch_warnings(
                        record=True
                    ) as reconstruction_warnings:
                        warnings.simplefilter("always")
                        transformed = scaler.transform(matrix)
                        reconstructed = model.predict(transformed)
                    attempts[-1]["reconstruction_warning_count"] = len(
                        reconstruction_warnings
                    )
                    if reconstruction_warnings:
                        status = "synthetic_reconstruction_warning"
                    else:
                        errors = _errors(transformed, reconstructed, len(observed))
        for row, error in zip(observed, errors, strict=True):
            results.append(
                dict(
                    asset_id=asset,
                    start_epoch=row["start_epoch"],
                    status=status,
                    reconstruction_error=error,
                    binary_prediction=None,
                    observation_coverage="partial_or_unknown",
                )
            )
    shared._unchanged_synthetic(context)
    scored = sum(row["reconstruction_error"] is not None for row in results)
    versions = {"python": sys.version.split()[0]}
    if attempts:
        versions.update(shared._dependency_versions())
    return dict(
        protocol="runtime_synthetic_autoencoder_v1",
        evidence_level="synthetic_software_only",
        status="no_observations"
        if not results
        else "synthetic_scores_computed"
        if scored
        else "synthetic_scoring_abstained",
        model="scikit_learn_undercomplete_reconstruction_mlp",
        dependency_versions=versions,
        feature_order=list(runtime.FEATURES),
        parameters=dict(
            seed=seed,
            latent_dim=latent_dim,
            max_iter=max_iter,
            max_fun=max_iter * 20,
            window_seconds=window_seconds,
            solver="lbfgs",
            activation="tanh",
            alpha=0.0001,
            tol=0.0001,
            thread_limit=1,
        ),
        training_attempts=attempts,
        windows=results,
        scored_window_count=scored,
        abstained_window_count=len(results) - scored,
        statistical_comparator=context["statistical"],
        synthetic_fitting_performed=bool(attempts),
        synthetic_scoring_performed=bool(scored),
        real_data_fitting_authorized=False,
        supervisor_approval_verified=False,
        independent_evaluation_verified=False,
        labels_created=False,
        calibrated=False,
        threat_confirmed=False,
        runtime_sensor_connected=False,
        actions_executed=[],
        implementation_sha256={
            name: hashlib.sha256(Path(path).read_bytes()).hexdigest()
            for name, path in (
                ("runtime_autoencoder.py", __file__),
                ("runtime_ml.py", shared.__file__),
                ("runtime.py", runtime.__file__),
            )
        },
        limitations=[
            "Declared synthetic data only; source declarations are not authenticated provenance.",
            "Undercomplete input-to-input reconstruction, not a binary threat classifier or probability.",
            "Scaler and network fit baseline windows only; no observation-driven calibration or labels.",
            "Training warnings cause abstention; iteration/evaluation budgets are not hard runtime guarantees.",
            "Standardized reconstruction MSE is not on the Isolation Forest score scale; do not rank methods by raw score magnitude.",
            "No independent accuracy, coverage, clock alignment, overhead or real-data authority established.",
        ],
    )


def _errors(transformed, reconstructed, count):
    if len(reconstructed) != count or len(transformed) != count:
        raise RuntimeError("invalid synthetic reconstruction length")
    errors = []
    for original, rebuilt in zip(transformed, reconstructed, strict=True):
        if len(original) != 4 or len(rebuilt) != 4:
            raise RuntimeError("invalid synthetic reconstruction width")
        left, right = (
            [float(value) for value in original],
            [float(value) for value in rebuilt],
        )
        if not all(math.isfinite(value) for value in [*left, *right]):
            raise RuntimeError("nonfinite synthetic reconstruction")
        try:
            error = sum((a - b) ** 2 for a, b in zip(left, right, strict=True)) / 4
        except OverflowError:
            raise RuntimeError("invalid synthetic reconstruction error") from None
        if not math.isfinite(error) or error < 0:
            raise RuntimeError("invalid synthetic reconstruction error")
        errors.append(error)
    return errors
