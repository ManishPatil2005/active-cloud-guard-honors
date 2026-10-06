"""Engine 2 observation-only replay foundation, not a live sensor or threat model."""

from collections import defaultdict
from datetime import datetime, timezone
import math
from statistics import mean, pstdev

from .verification import load_inventory, object_schema, read_json, validate

KINDS = ("process_start", "network_connect", "file_open")
FEATURES = ("event_count", *KINDS)
IDENTIFIER = {"type": "string", "pattern": "^[A-Za-z0-9_./:-]{1,128}$"}
CONTAINER = {
    "type": "string",
    "pattern": "^[a-f0-9]{64}$",
    "minLength": 64,
    "maxLength": 64,
}
CAPTURE_SCHEMA = object_schema(
    dict(
        schema_version={"const": "1.0"},
        capture_id=IDENTIFIER,
        scenario_group=IDENTIFIER,
        source={"enum": ["synthetic", "normalized_sensor_export"]},
        bindings={
            "type": "array",
            "minItems": 1,
            "maxItems": 100,
            "items": object_schema(dict(container_id=CONTAINER, asset_id=IDENTIFIER)),
        },
        events={
            "type": "array",
            "maxItems": 2000,
            "items": object_schema(
                dict(
                    event_id=IDENTIFIER,
                    timestamp={"type": "string", "minLength": 20, "maxLength": 40},
                    container_id=CONTAINER,
                    kind={"enum": list(KINDS)},
                )
            ),
        },
    )
)


def timestamp(value):
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None or not 1970 <= parsed.year <= 2100:
            raise ValueError()
        return parsed.astimezone(timezone.utc).timestamp()
    except (ValueError, TypeError, OverflowError):
        raise ValueError(
            "runtime timestamp must be timezone-aware ISO 8601 in 1970..2100"
        ) from None


def load_capture(path, assets):
    capture, digest = read_json(path)  # 1 MB bound and duplicate-key rejection.
    validate(capture, CAPTURE_SCHEMA)
    bindings = {}
    for entry in capture["bindings"]:
        if entry["container_id"] in bindings or entry["asset_id"] not in assets:
            raise ValueError("ambiguous container binding or unknown inventory asset")
        bindings[entry["container_id"]] = entry["asset_id"]
    identifiers = set()
    events = []
    for event in capture["events"]:
        if event["event_id"] in identifiers or event["container_id"] not in bindings:
            raise ValueError("duplicate runtime event or unbound container")
        identifiers.add(event["event_id"])
        events.append(
            dict(
                **event,
                asset_id=bindings[event["container_id"]],
                epoch=timestamp(event["timestamp"]),
            )
        )
    events.sort(key=lambda event: (event["epoch"], event["event_id"]))
    return dict(
        capture_id=capture["capture_id"],
        scenario_group=capture["scenario_group"],
        source=capture["source"],
        sha256=digest,
        events=events,
        binding_verified=False,
    )


def windows(capture, seconds):
    if (
        isinstance(seconds, bool)
        or not isinstance(seconds, int)
        or not 1 <= seconds <= 3600
    ):
        raise ValueError("window size must be an integer in 1..3600 seconds")
    buckets = {}
    for event in capture["events"]:
        start = int(event["epoch"] // seconds) * seconds
        key = (event["asset_id"], start)
        if key not in buckets:
            buckets[key] = dict(
                asset_id=event["asset_id"],
                start_epoch=start,
                capture_id=capture["capture_id"],
                counts=dict.fromkeys(FEATURES, 0),
                observation_coverage="partial_or_unknown",
            )
        buckets[key]["counts"]["event_count"] += 1
        buckets[key]["counts"][event["kind"]] += 1
    return [buckets[key] for key in sorted(buckets)]


def event_keys(capture):
    return {
        (e["asset_id"], e["container_id"], e["epoch"], e["kind"])
        for e in capture["events"]
    }


def analyze(
    baseline_paths, observation_path, inventory, *, window_seconds=60, threshold=3.0
):
    if not 1 <= len(baseline_paths) <= 20:
        raise ValueError("provide 1..20 baseline captures")
    if (
        isinstance(threshold, bool)
        or not isinstance(threshold, (int, float))
        or not math.isfinite(threshold)
        or not 0 < threshold <= 100
    ):
        raise ValueError("threshold must be finite and in (0,100]")
    assets, inventory_hash = load_inventory(inventory)
    captures = [load_capture(path, assets) for path in baseline_paths]
    observation = load_capture(observation_path, assets)
    all_captures = [*captures, observation]
    if len({c["capture_id"] for c in all_captures}) != len(all_captures):
        raise ValueError("capture identities must be distinct")
    if len({c["source"] for c in all_captures}) != 1:
        raise ValueError("synthetic and sensor-export baselines cannot be mixed")
    if observation["scenario_group"] in {c["scenario_group"] for c in captures}:
        raise ValueError("baseline and observation scenario groups must be disjoint")
    seen_events = set()
    for capture in captures:
        keys = event_keys(capture)
        if seen_events & keys:
            raise ValueError("overlapping baseline event records")
        seen_events |= keys
    if seen_events & event_keys(observation):
        raise ValueError("baseline/observation event overlap")
    baseline_windows = [
        window for capture in captures for window in windows(capture, window_seconds)
    ]
    grouped = defaultdict(list)
    for window in baseline_windows:
        grouped[window["asset_id"]].append(window["counts"])
    parameters = {}
    for asset, rows in grouped.items():
        if len(rows) >= 3:
            parameters[asset] = dict(
                window_count=len(rows),
                features={
                    name: dict(
                        mean=mean(row[name] for row in rows),
                        scale=max(1.0, pstdev(row[name] for row in rows)),
                    )
                    for name in FEATURES
                },
            )
    observations = windows(observation, window_seconds)
    for window in observations:
        baseline = parameters.get(window["asset_id"])
        if baseline is None:
            window.update(
                status="insufficient_baseline",
                deviation_score=None,
                review_required=True,
            )
            continue
        deviations = {
            name: abs(window["counts"][name] - values["mean"]) / values["scale"]
            for name, values in baseline["features"].items()
        }
        score = max(deviations.values())
        window.update(
            status="deviation_for_review"
            if score > threshold
            else "no_threshold_exceedance",
            deviation_score=round(score, 6),
            feature_deviations=deviations,
            review_required=score > threshold,
        )

    def provenance(capture):
        return {
            key: capture[key]
            for key in (
                "capture_id",
                "scenario_group",
                "source",
                "sha256",
                "binding_verified",
            )
        }

    return dict(
        engine="engine2",
        engine_version="0.1",
        mode="observation_only_replay",
        model="per_asset_standardized_count_deviation",
        implementation_scope=dict(
            component="runtime_replay_baseline",
            status="implemented",
            live_input=False,
            saved_sensor_export_supported=True,
            trained_ml_model=False,
            independent_detection_evaluation=False,
            automatic_response=False,
        ),
        calibrated=False,
        inventory_sha256=inventory_hash,
        window_seconds=window_seconds,
        threshold=threshold,
        baseline=[provenance(c) for c in captures],
        observation=provenance(observation),
        baseline_parameters=parameters,
        windows=observations,
        status="observations_processed" if observations else "no_observations",
        actions_executed=[],
        runtime_sensor_connected=False,
        threat_confirmed=False,
        limitations=[
            "Synthetic inputs demonstrate software behavior, not threat detection accuracy.",
            "Imported sensor provenance/container mappings are declarations, not authenticated live identity.",
            "Only nonempty windows are evaluated; silence, collection gaps and partial windows are not treated as normal.",
            "Baseline designation is operator supplied; no independent benign labels or calibration are established.",
            "Metadata/event overlap checks reduce accidental leakage, not renamed-template or adversarial leakage.",
            "This replay command accepts saved captures only; live collection and normalization are separate experimental paths.",
            "This baseline has no Kubernetes audit adapter, Isolation Forest, autoencoder, isolation or TCI integration.",
        ],
    )
