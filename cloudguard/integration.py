"""Join configuration and saved runtime context without granting verdict authority."""

from collections import defaultdict
import hashlib
from pathlib import Path

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
):
    if inventory is None:
        raise ValueError("integrated replay requires an inventory")
    if type(baseline_paths) not in (list, tuple) or not 1 <= len(baseline_paths) <= 20:
        raise ValueError("provide 1..20 baseline captures")
    baseline_paths = tuple(baseline_paths)
    paths = {
        "configuration": Path(configuration),
        "inventory": Path(inventory),
        "observation": Path(observation),
        **{f"baseline_{i}": Path(path) for i, path in enumerate(baseline_paths)},
    }
    hashes = {role: _digest(path) for role, path in paths.items()}
    sources = {name: Path(__file__).parent / name for name in SELECTED_SOURCES}
    source_hashes = {name: _digest(path) for name, path in sources.items()}
    assets, inventory_hash = load_inventory(inventory)
    static = scan(configuration)
    if len(static["findings"]) > FINDING_LIMIT:
        raise ValueError("integrated replay exceeds 1000 configuration findings")
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
    findings, windows = defaultdict(list), defaultdict(list)
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
    if any(_digest(path) != hashes[role] for role, path in paths.items()):
        raise ValueError("integrated replay input changed")
    if any(_digest(path) != source_hashes[name] for name, path in sources.items()):
        raise ValueError("integrated replay selected implementation changed")
    return dict(
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
