"""Join configuration and saved runtime context without granting verdict authority."""

from collections import defaultdict
from contextlib import contextmanager
import hashlib
from pathlib import Path
import time

from .runtime import analyze as analyze_runtime
from .scanner import scan
from .verification import load_inventory

INPUT_LIMIT = 1_000_000
FINDING_LIMIT = 1000
SELECTED_SOURCES = (
    "integration.py",
    "scanner.py",
    "runtime.py",
    "verification.py",
    "cache.py",
)
PIPELINE_SOURCES = (
    "pipeline.py",
    "retrieval.py",
    "llm.py",
    "grounding.py",
    "scoring.py",
    "vector.py",
)


class _Measurements:
    """Opt-in local elapsed/process CPU observations, never detector metrics."""

    def __init__(self, enabled):
        self.enabled = enabled
        self.stages = {}
        self.start = self._read() if enabled else None

    @staticmethod
    def _read():
        return time.perf_counter_ns(), time.process_time_ns()

    def _elapsed(self, start):
        end = self._read()
        values = dict(wall_ns=end[0] - start[0], process_cpu_ns=end[1] - start[1])
        if any(type(value) is not int or value < 0 for value in values.values()):
            raise ValueError("invalid local execution clock interval")
        return values

    @contextmanager
    def stage(self, name):
        start = self._read() if self.enabled else None
        yield
        if self.enabled:
            self.stages[name] = self._elapsed(start)

    def report(self):
        total = self._elapsed(self.start)
        clocks = {}
        for role, name in (("wall", "perf_counter"), ("process_cpu", "process_time")):
            info = time.get_clock_info(name)
            clocks[role] = dict(
                name=name,
                implementation=info.implementation,
                resolution_seconds=info.resolution,
                monotonic=info.monotonic,
                adjustable=info.adjustable,
            )
        return dict(
            protocol="integrated_process_cost_v1",
            scope="single_process_development_observation",
            clocks=clocks,
            stages=self.stages,
            total=total,
            sensor_overhead_evaluated=False,
            energy_measured=False,
            independent_performance_evaluation=False,
            limitations=[
                "Total covers replay after option validation through report assembly, not CLI startup or JSON output.",
                "Stages are non-overlapping component calls; total also includes input/source hashing, imports, checks and context assembly.",
                "ML stage includes its existing parsing, validation, lazy backend import, fitting and scoring, not fit-only cost.",
                "Process CPU includes this process's threads, not child processes, Ollama server, sensor or system-wide CPU.",
                "Local clocks are not cross-system event alignment; single development execution is not matched overhead, latency distribution or energy evidence.",
            ],
        )


def _digest(path):
    with Path(path).open("rb") as stream:
        raw = stream.read(INPUT_LIMIT + 1)
    if len(raw) > INPUT_LIMIT:
        raise ValueError("integrated replay input exceeds 1 MB")
    return hashlib.sha256(raw).hexdigest()


def replay(
    configuration,
    baseline_paths,
    observation,
    inventory,
    *,
    window_seconds=60,
    threshold=3.0,
    engine1_pipeline=False,
    kb=None,
    model=None,
    vector_index=None,
    cache_dir=None,
    timeout=180,
    max_tokens=512,
    policy=None,
    reviews=None,
    runtime_ml=None,
    measure_stages=False,
):
    if type(measure_stages) is not bool:
        raise ValueError("measure_stages must be a boolean")
    if runtime_ml is not None and (
        type(runtime_ml) is not str
        or runtime_ml not in ("isolation-forest", "autoencoder", "both")
    ):
        raise ValueError("invalid synthetic comparator selection")
    if type(engine1_pipeline) is not bool:
        raise ValueError("engine1_pipeline must be a boolean")
    if engine1_pipeline and kb is None:
        raise ValueError("Engine1 pipeline integration requires a knowledge corpus")
    if not engine1_pipeline and (
        any(
            value is not None
            for value in (kb, model, vector_index, cache_dir, policy, reviews)
        )
        or timeout != 180
        or max_tokens != 512
    ):
        raise ValueError("Engine1 options require explicit pipeline mode")
    if inventory is None:
        raise ValueError("integrated replay requires an inventory")
    if type(baseline_paths) not in (list, tuple) or not 1 <= len(baseline_paths) <= 20:
        raise ValueError("provide 1..20 baseline captures")
    baseline_paths = tuple(baseline_paths)
    measurements = _Measurements(measure_stages)
    paths = {
        "configuration": Path(configuration),
        "inventory": Path(inventory),
        "observation": Path(observation),
        **{f"baseline_{i}": Path(path) for i, path in enumerate(baseline_paths)},
    }
    if engine1_pipeline:
        paths["knowledge"] = Path(kb)
        for role, path in (("policy", policy), ("reviews", reviews)):
            if path is not None:
                paths[role] = Path(path)
    hashes = {role: _digest(path) for role, path in paths.items()}
    ml_sources = (
        ("runtime_ml.py", "runtime_autoencoder.py")
        if runtime_ml in ("autoencoder", "both")
        else ("runtime_ml.py",)
        if runtime_ml
        else ()
    )
    sources = {
        name: Path(__file__).parent / name
        for name in SELECTED_SOURCES
        + (PIPELINE_SOURCES if engine1_pipeline else ())
        + ml_sources
    }
    source_hashes = {name: _digest(path) for name, path in sources.items()}
    assets, inventory_hash = load_inventory(inventory)
    with measurements.stage("configuration_rule_baseline"):
        static = scan(configuration)
    if len(static["findings"]) > FINDING_LIMIT:
        raise ValueError("integrated replay exceeds 1000 configuration findings")
    with measurements.stage("runtime_statistical"):
        runtime = analyze_runtime(
            baseline_paths,
            observation,
            inventory,
            window_seconds=window_seconds,
            threshold=threshold,
        )
    component_hashes = {
        "inventory": inventory_hash,
        "observation": runtime["observation"]["sha256"],
        **{f"baseline_{i}": c["sha256"] for i, c in enumerate(runtime["baseline"])},
    }
    if runtime["inventory_sha256"] != hashes["inventory"] or any(
        hashes[role] != value for role, value in component_hashes.items()
    ):
        raise ValueError("integrated replay component input mismatch")
    comparators = {}
    if runtime_ml:
        if any(
            c["source"] != "synthetic"
            for c in [*runtime["baseline"], runtime["observation"]]
        ):
            raise ValueError("integrated ML accepts declared synthetic data only")
        if any(_digest(path) != hashes[role] for role, path in paths.items()):
            raise ValueError("integrated replay input changed before synthetic fitting")
        if any(_digest(path) != source_hashes[name] for name, path in sources.items()):
            raise ValueError(
                "integrated replay implementation changed before synthetic fitting"
            )
        from .runtime_ml import compare_synthetic as isolation

        selected = (
            [("isolation_forest", isolation)]
            if runtime_ml in ("isolation-forest", "both")
            else []
        )
        if runtime_ml in ("autoencoder", "both"):
            from .runtime_autoencoder import compare_synthetic as autoencoder

            selected.append(("autoencoder", autoencoder))
        keys = [(w["asset_id"], w["start_epoch"]) for w in runtime["windows"]]
        for name, compare in selected:
            with measurements.stage(name):
                result = compare(
                    baseline_paths,
                    observation,
                    inventory,
                    window_seconds=window_seconds,
                )
            nested = result["statistical_comparator"]
            if any(
                nested[field] != runtime[field]
                for field in ("inventory_sha256", "baseline", "observation")
            ):
                raise ValueError("synthetic comparator input mismatch")
            if [
                (w["asset_id"], w["start_epoch"]) for w in result["windows"]
            ] != keys or len(set(keys)) != len(keys):
                raise ValueError("synthetic comparator window mismatch")
            if result["scored_window_count"] + result["abstained_window_count"] != len(
                keys
            ):
                raise ValueError("synthetic comparator count mismatch")
            if any(
                source_hashes[k] != v
                for k, v in result["implementation_sha256"].items()
            ):
                raise ValueError("synthetic comparator implementation mismatch")
            comparators[name] = result
    if engine1_pipeline:
        # Validate saved runtime and all frozen inputs before optional active stages.
        if any(_digest(path) != hashes[role] for role, path in paths.items()):
            raise ValueError("integrated replay input changed before Engine1 pipeline")
        if any(_digest(path) != source_hashes[name] for name, path in sources.items()):
            raise ValueError(
                "integrated replay implementation changed before Engine1 pipeline"
            )
        from .pipeline import run

        with measurements.stage("engine1_pipeline"):
            static = run(
                configuration,
                kb,
                inventory,
                model,
                vector_index,
                cache_dir=cache_dir,
                timeout=timeout,
                max_tokens=max_tokens,
                policy=policy,
                reviews=reviews,
            )
        if (
            static["configuration_bytes_sha256"] != hashes["configuration"]
            or static["inventory_sha256"] != hashes["inventory"]
        ):
            raise ValueError("Engine1 pipeline input mismatch")
        if len(static["findings"]) > FINDING_LIMIT:
            raise ValueError("integrated replay exceeds 1000 configuration findings")
    findings, windows = defaultdict(list), defaultdict(list)
    model_verifications = defaultdict(list)
    if engine1_pipeline:
        for index, verification in enumerate(static["model_verifications"]):
            model_verifications[verification["approval"]["inventory_asset_id"]].append(
                index
            )
    for finding in static["findings"]:
        findings[finding["asset_id"]].append(finding["id"])
    for index, window in enumerate(runtime["windows"]):
        windows[window["asset_id"]].append(index)
    contexts = []
    for asset in sorted(set(assets) | set(findings) | set(windows)):
        indices = windows[asset]
        rows = [runtime["windows"][i] for i in indices]
        insufficient = sum(w["status"] == "insufficient_baseline" for w in rows)
        state = (
            "no_observed_window"
            if not rows
            else "insufficient_baseline"
            if insufficient == len(rows)
            else "partial_baseline"
            if insufficient
            else "observations_available"
        )
        contexts.append(
            dict(
                asset_id=asset,
                inventory_asset_present=asset in assets,
                association="declared_asset_id_only"
                if asset in assets
                else "unmapped_static_asset",
                configuration_finding_ids=findings[asset],
                runtime_window_indices=indices,
                runtime_evidence_state=state,
                runtime_review_required=any(w["review_required"] for w in rows)
                if rows
                else None,
                review_required=True,
                deployment_binding_verified=False,
                combined_priority=None,
            )
        )
        if engine1_pipeline:
            contexts[-1]["model_verification_indices"] = model_verifications[asset]
        if runtime_ml:
            contexts[-1]["runtime_comparator_window_indices"] = {
                name: [
                    i
                    for i, row in enumerate(result["windows"])
                    if row["asset_id"] == asset
                ]
                for name, result in comparators.items()
            }
    if any(_digest(path) != hashes[role] for role, path in paths.items()):
        raise ValueError("integrated replay input changed")
    if any(_digest(path) != source_hashes[name] for name, path in sources.items()):
        raise ValueError("integrated replay selected implementation changed")
    report = dict(
        protocol="integrated_configuration_runtime_replay_v1",
        mode="offline_context_join",
        evidence_level="software_context_only",
        configuration_bytes_sha256=hashes["configuration"],
        input_sha256=hashes,
        selected_implementation_sha256=source_hashes,
        engine1=static,
        engine2=runtime,
        asset_contexts=contexts,
        configuration_finding_count=len(static["findings"]),
        runtime_window_count=len(runtime["windows"]),
        joint_priority_calculated=False,
        deployment_binding_verified=False,
        independent_evaluation_verified=False,
        real_data_evaluation_authorized=False,
        runtime_sensor_connected=False,
        calibrated=False,
        threat_confirmed=False,
        actions_executed=[],
        limitations=[
            "Engine1 component is the configuration rule baseline; no model audit or active verification runs here.",
            "Matching declared asset IDs supplies context, not authenticated deployment or temporal equivalence.",
            "Missing windows remain unknown; insufficient baseline and all original findings/windows are retained.",
            "Saved runtime deviations are uncalibrated; no score conversion, TCI fusion, threat verdict or action.",
            "Pre/post input and selected source hashes check observed consistency, not hostile filesystem races or complete import attestation.",
            "Supplied sensor exports retain their development/provenance limits; this command cannot authorize real evaluation.",
        ],
    )
    if engine1_pipeline:
        observed_assets = {
            f["asset_id"] for f in static["findings"] if f["probe"] is not None
        } | {v["approval"]["inventory_asset_id"] for v in static["model_verifications"]}
        report.update(
            protocol="integrated_engine1_pipeline_runtime_replay_v1",
            mode="engine1_pipeline_with_saved_runtime_context",
            engine1_pipeline_executed=True,
            engine1_model_requested=model is not None,
            active_verification_asset_count=len(observed_assets),
        )
        report["limitations"][0] = (
            "Engine1 pipeline retains its retrieval/model/probe/priority/review evidence; "
            "requested model and TCP stages can perform existing local operations."
        )
    if runtime_ml:
        report.update(
            protocol="integrated_synthetic_runtime_comparators_v1",
            runtime_ml_selection=runtime_ml,
            runtime_comparators=comparators,
            synthetic_fitting_performed=any(
                c["synthetic_fitting_performed"] for c in comparators.values()
            ),
            synthetic_scoring_performed=any(
                c["synthetic_scoring_performed"] for c in comparators.values()
            ),
        )
        report["limitations"].append(
            "Optional models fit declared synthetic baselines only. Scores and abstentions remain separate; "
            "nested statistical comparators retain threshold 3 independently of the parent threshold."
        )
    if measure_stages:
        report["execution_cost"] = measurements.report()
    return report
