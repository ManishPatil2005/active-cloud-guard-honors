"""Synthetic-only Isolation Forest software comparator, not threat evaluation."""

from collections import defaultdict
from importlib import metadata
import hashlib
import math
from pathlib import Path
import sys

from cloudguard import runtime
from cloudguard.verification import load_inventory

SKLEARN_VERSION = "1.9.1"
MIN_WINDOWS = 8
TRAIN_WINDOW_LIMIT = 4096


def _backend():
    try:
        from sklearn.ensemble import IsolationForest
        from threadpoolctl import threadpool_limits
    except ImportError:
        raise RuntimeError("install the optional runtime-ml dependency") from None
    if metadata.version("scikit-learn") != SKLEARN_VERSION:
        raise RuntimeError("runtime-ml dependency version mismatch")
    return IsolationForest, threadpool_limits


def compare_synthetic(
    baseline_paths,
    observation_path,
    inventory,
    *,
    window_seconds=60,
    seed=42,
    n_estimators=64,
    max_samples=256,
):
    """Fit ephemeral forests on declared synthetic baseline windows only.

    Never accept declared sensor exports, load model files, calibrate on
    observations or return binary attack/benign predictions. Source declarations
    cannot authenticate that arbitrary caller-provided files were invented.
    """
    for value, low, high in (
        (seed, 0, 2**32 - 1),
        (n_estimators, 1, 128),
        (max_samples, 2, 256),
        (window_seconds, 1, 3600),
    ):
        if type(value) is not int or not low <= value <= high:
            raise ValueError("invalid bounded synthetic model parameter")
    if (
        not isinstance(baseline_paths, (list, tuple))
        or not 1 <= len(baseline_paths) <= 20
    ):
        raise ValueError("provide 1..20 synthetic baseline captures")
    assets, inventory_hash = load_inventory(inventory)
    captures = [runtime.load_capture(path, assets) for path in baseline_paths]
    observation = runtime.load_capture(observation_path, assets)
    if any(capture["source"] != "synthetic" for capture in [*captures, observation]):
        raise ValueError("this comparator accepts declared synthetic data only")
    statistical = runtime.analyze(
        baseline_paths, observation_path, inventory, window_seconds=window_seconds
    )  # Inherit ID/group/event-overlap and original statistical checks.
    if statistical["inventory_sha256"] != inventory_hash or any(
        current["sha256"] != expected["sha256"]
        for current, expected in zip(
            [*statistical["baseline"], statistical["observation"]],
            [*captures, observation],
            strict=True,
        )
    ):
        raise ValueError("inputs changed during statistical comparison")
    train_rows = sorted(
        [
            row
            for capture in captures
            for row in runtime.windows(capture, window_seconds)
        ],
        key=lambda row: (row["asset_id"], row["capture_id"], row["start_epoch"]),
    )
    if len(train_rows) > TRAIN_WINDOW_LIMIT:
        raise ValueError("synthetic training window limit exceeded")
    training = defaultdict(list)
    for row in train_rows:
        training[row["asset_id"]].append(
            [row["counts"][name] for name in runtime.FEATURES]
        )
    observations = runtime.windows(observation, window_seconds)
    grouped = defaultdict(list)
    for row in observations:
        grouped[row["asset_id"]].append(row)
    results, fitted = [], []
    versions = {"python": sys.version.split()[0]}
    for asset in sorted(grouped):
        rows = training[asset]
        status = (
            "insufficient_synthetic_baseline"
            if len(rows) < MIN_WINDOWS
            else "uninformative_synthetic_baseline"
            if len({tuple(row) for row in rows}) < 2
            else "uncalibrated_synthetic_score"
        )
        scores = [None] * len(grouped[asset])
        if status == "uncalibrated_synthetic_score":
            Forest, limits = _backend()
            forest = Forest(
                n_estimators=n_estimators,
                max_samples=min(max_samples, len(rows)),
                max_features=1.0,
                contamination="auto",
                bootstrap=False,
                random_state=seed,
                n_jobs=1,
                warm_start=False,
            )
            with limits(limits=1):
                forest.fit(rows)
                matrix = [
                    [row["counts"][name] for name in runtime.FEATURES]
                    for row in grouped[asset]
                ]
                scores = [-float(score) for score in forest.score_samples(matrix)]
            if any(not math.isfinite(score) or not 0 <= score <= 1 for score in scores):
                raise RuntimeError("invalid synthetic isolation score")
            fitted.append(
                dict(
                    asset_id=asset,
                    training_window_count=len(rows),
                    subsample_size=min(max_samples, len(rows)),
                )
            )
        for row, score in zip(grouped[asset], scores, strict=True):
            results.append(
                dict(
                    asset_id=asset,
                    start_epoch=row["start_epoch"],
                    status=status,
                    isolation_score=None if score is None else round(score, 6),
                    binary_prediction=None,
                    observation_coverage="partial_or_unknown",
                )
            )
    # Re-read all input identities after fit/score; not hostile filesystem attestation.
    for path, expected in zip(
        [*baseline_paths, observation_path], [*captures, observation], strict=True
    ):
        if runtime.load_capture(path, assets)["sha256"] != expected["sha256"]:
            raise ValueError("capture changed during synthetic model comparison")
    if load_inventory(inventory)[1] != inventory_hash:
        raise ValueError("inventory changed during synthetic model comparison")
    if fitted:
        versions.update(
            {
                name: metadata.version(name)
                for name in (
                    "scikit-learn",
                    "numpy",
                    "scipy",
                    "joblib",
                    "threadpoolctl",
                    "narwhals",
                    "cloudpickle",
                )
            }
        )
    scored = sum(row["isolation_score"] is not None for row in results)
    return dict(
        protocol="runtime_synthetic_iforest_v1",
        evidence_level="synthetic_software_only",
        status="no_observations"
        if not results
        else "synthetic_scores_computed"
        if scored
        else "synthetic_scoring_abstained",
        model="scikit_learn_isolation_forest",
        library_pin=SKLEARN_VERSION,
        dependency_versions=versions,
        feature_order=list(runtime.FEATURES),
        parameters=dict(
            seed=seed,
            n_estimators=n_estimators,
            max_samples=max_samples,
            window_seconds=window_seconds,
            n_jobs=1,
            thread_limit=1,
        ),
        fitted_assets=fitted,
        windows=results,
        scored_window_count=scored,
        abstained_window_count=len(results) - scored,
        statistical_comparator=statistical,
        synthetic_fitting_performed=bool(fitted),
        synthetic_scoring_performed=bool(fitted),
        real_data_fitting_authorized=False,
        independent_evaluation_verified=False,
        supervisor_approval_verified=False,
        labels_created=False,
        calibrated=False,
        threat_confirmed=False,
        runtime_sensor_connected=False,
        actions_executed=[],
        implementation_sha256={
            "runtime_ml.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "runtime.py": hashlib.sha256(
                Path(runtime.__file__).read_bytes()
            ).hexdigest(),
        },
        limitations=[
            "Declared synthetic software data only; source metadata is not authenticated provenance.",
            "Higher isolation score means shorter isolation paths, not attack probability or confirmed threats.",
            "No binary predictions, calibrated threshold, independent labels or real-data evaluation.",
            "Minimum windows and forest budgets are engineering choices, not adequate research sample size.",
            "Only nonempty windows; partial coverage and missing intervals are not benign observations.",
            "Grouping/overlap guards are limited; no complete semantic leakage or physical identity proof.",
            "Correlated total/kind count features match the baseline; feature design needs future protocol review.",
        ],
    )
