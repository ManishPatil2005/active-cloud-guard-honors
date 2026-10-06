"""Selected offline receipt arithmetic/binding, never coverage or attestation."""

from collections import Counter

from .clock_check import compare
from .runtime import timestamp
from .sensor_adapter import IMAGE, KINDS
from .verification import HASH, object_schema, validate

MAX_NS = 4_133_980_800 * 10**9
ID = dict(
    type="string",
    minLength=1,
    maxLength=128,
    pattern=r"^[A-Za-z0-9_./:-]+$",
    **{"not": {"pattern": r"\s"}},
)
REF = object_schema(
    dict(path=dict(type="string", minLength=1, maxLength=256), sha256=HASH)
)
WRAPPER = object_schema(
    dict(
        schema_version={"const": "runtime_receipt_v1"},
        kind={"enum": ["accounting", "identity", "timing"]},
        run_id=ID,
        capture_sha256=HASH,
        inventory_sha256=HASH,
        collection_protocol={"const": "acg_falco_selected_v1"},
        origin={"enum": ["synthetic_fixture", "recorded_projection"]},
        source=REF,
    )
)
COUNT = dict(type="integer", minimum=0, maximum=10000)
BOOL = dict(type="boolean")
FALSE = dict(type="boolean", const=False)
NS = dict(type="integer", minimum=0, maximum=MAX_NS)
SIGNED_NS = dict(type="integer", minimum=-MAX_NS, maximum=MAX_NS)
SAMPLE = object_schema(dict(wall_ns=NS, monotonic_mid_ns=NS, sampling_span_ns=NS))
CLOCK = object_schema(
    dict(
        first=SAMPLE,
        last=SAMPLE,
        elapsed_monotonic_ns=SIGNED_NS,
        clock_difference_ns=SIGNED_NS,
        sampling_uncertainty_ns=NS,
        within_tolerance=BOOL,
    )
)
IDENTITY = object_schema(
    dict(
        id=HASH,
        image=dict(
            type="string", pattern=r"^sha256:[a-f0-9]{64}$", minLength=71, maxLength=71
        ),
        started_at=dict(type="string", minLength=20, maxLength=40),
        running=BOOL,
        restarts=COUNT,
        project=ID,
        service={"const": "redis"},
    )
)
ACCOUNTING = object_schema(
    dict(
        adapter_version={"const": "0.1"},
        status={"enum": ["normalized", "rejected"]},
        raw_sha256=HASH,
        trial_sha256=HASH,
        inventory_sha256=HASH,
        line_count=COUNT,
        diagnostic_line_count=COUNT,
        validated_event_count=COUNT,
        rejected_record_count=COUNT,
        rejection_reasons=dict(
            type="object", maxProperties=20, additionalProperties=COUNT
        ),
        event_type_counts=dict(
            type="object",
            properties={kind: COUNT for kind in KINDS},
            additionalProperties=False,
        ),
        receipt_counts_match=BOOL,
        sensor_dropped_events={"type": "null"},
        collection_coverage={"const": "partial_or_unknown"},
        binding_verified=FALSE,
        threat_confirmed=FALSE,
        actions_executed=dict(type="array", maxItems=0),
        timestamp_precision={
            "const": "nanoseconds retained; runtime parser truncates to microseconds before floating-point windowing"
        },
    )
)


def exact_numbers(value):
    """JSON Schema accepts integral floats; these receipt counters do not."""
    if isinstance(value, float):
        raise ValueError("exact receipt integers required")
    if isinstance(value, dict):
        for child in value.values():
            exact_numbers(child)
    elif isinstance(value, list):
        for child in value:
            exact_numbers(child)


def accounting(source, capture, inventory_hash):
    validate(source, ACCOUNTING)
    exact_numbers(source)
    if source["inventory_sha256"] != inventory_hash:
        raise ValueError("accounting inventory mismatch")
    validated, rejected, diagnostic = (
        source[key]
        for key in (
            "validated_event_count",
            "rejected_record_count",
            "diagnostic_line_count",
        )
    )
    counts = Counter()
    for name, count in source["event_type_counts"].items():
        counts[KINDS[name]] += count
    observed = Counter(event["kind"] for event in capture["events"])
    if (
        sum(counts.values()) != validated
        or validated != len(capture["events"])
        or counts != observed
        or sum(source["rejection_reasons"].values()) != rejected
        or source["line_count"] != validated + rejected + diagnostic
    ):
        raise ValueError("accounting arithmetic/capture counts mismatch")
    normalized = (
        validated > 0 and rejected == 0 and source["receipt_counts_match"] is True
    )
    if (source["status"] == "normalized") != normalized:
        raise ValueError("accounting status contradicts recorded counts")
    return dict(
        scope="adapter_counts_only",
        recorded_outcome=source["status"],
        rejected_record_count=rejected,
        coverage_verified=False,
    )


def identity(source, container):
    before, after = (
        source.get("target_identity_before"),
        source.get("target_identity_after"),
    )
    for value in (before, after):
        validate(value, IDENTITY)
        exact_numbers(value)
        timestamp(value["started_at"])
        if value["id"] != container:
            raise ValueError("identity/capture container mismatch")
    stable = before == after and before["running"] is True
    if (
        type(source.get("target_identity_stable")) is not bool
        or source["target_identity_stable"] != stable
    ):
        raise ValueError("identity stable flag contradicts snapshots")
    return dict(
        scope="selected_recorded_snapshots_only",
        recorded_outcome="stable" if stable else "changed_or_not_running",
        deployment_binding_authenticated=False,
    )


def timing(source):
    measurement = source.get("measurement")
    if (
        not isinstance(measurement, dict)
        or measurement.get("timing_protocol") != "per_call_brackets_v1"
    ):
        raise ValueError("supported endpoint timing protocol required")
    row = measurement.get("clock_sampling")
    validate(row, CLOCK)
    exact_numbers(row)
    computed = compare(row["first"], row["last"])
    if any(row[key] != value for key, value in computed.items()):
        raise ValueError("timing arithmetic/flag mismatch")
    endpoints = dict(
        start_unix_ns=row["first"]["wall_ns"],
        end_unix_ns=row["last"]["wall_ns"],
        elapsed_monotonic_ns=computed["elapsed_monotonic_ns"],
        clock_difference_ns=computed["clock_difference_ns"],
    )
    for key, value in endpoints.items():
        if type(measurement.get(key)) is not int or measurement[key] != value:
            raise ValueError("measurement endpoint mismatch")
    # Preserve the recorded collector rejection without trusting its truth value.
    correlation = source.get("correlation")
    excluded = (
        correlation.get("zero_excluded_samples")
        if isinstance(correlation, dict)
        else None
    )
    if excluded is not None and (type(excluded) is not int or not 0 <= excluded <= 4):
        raise ValueError("invalid recorded alignment rejection count")
    return dict(
        scope="harness_endpoints_only",
        local_clock_within_tolerance=computed["within_tolerance"],
        recorded_outcome="within_local_tolerance"
        if computed["within_tolerance"]
        else "rejected_local_timing",
        recorded_collector_zero_excluded_samples=excluded,
        collector_alignment_verified=False,
        long_term_stability_verified=False,
    )


def inspect_receipts(run, capture, capture_document, inventory_hash, read_json):
    """read_json uses the intake bundle's existing role/hash/byte/postflight guards."""
    checks, sources = {}, {}
    for kind, ref in run["receipts"].items():
        if ref is None:
            continue
        wrapper = read_json(ref)
        validate(wrapper, WRAPPER)
        if (
            wrapper["kind"] != kind
            or wrapper["run_id"] != run["run_id"]
            or wrapper["capture_sha256"] != capture["sha256"]
            or wrapper["inventory_sha256"] != inventory_hash
        ):
            raise ValueError("typed receipt context mismatch")
        if (
            capture["source"] == "synthetic"
            and wrapper["origin"] != "synthetic_fixture"
        ):
            raise ValueError("synthetic capture cannot claim recorded provenance")
        if (
            capture["source"] != "synthetic"
            and wrapper["origin"] != "recorded_projection"
        ):
            raise ValueError("sensor export requires declared recorded projection")
        source = read_json(wrapper["source"])
        if not isinstance(source, dict):
            raise ValueError("receipt source object required")
        if (
            source.get("fixture_only") is True
            and wrapper["origin"] != "synthetic_fixture"
        ):
            raise ValueError("explicit fixture source cannot claim recorded provenance")
        sources[kind] = (wrapper["source"]["sha256"], source)
        if kind == "accounting":
            result = accounting(source, capture, inventory_hash)
        else:
            bindings = capture_document["bindings"]
            if len(bindings) != 1 or bindings[0]["asset_id"] != "compose/redis":
                raise ValueError("selected receipt protocol supports one Redis binding")
            container = bindings[0]["container_id"]
            if (
                source.get("image") != IMAGE
                or source.get("container_id") != container
                or source.get("deployment_binding_authenticated") is not False
            ):
                raise ValueError("unsupported selected trial/capture identity")
            result = (
                identity(source, container) if kind == "identity" else timing(source)
            )
        checks[kind] = dict(
            wrapper_sha256=ref["sha256"],
            source_sha256=wrapper["source"]["sha256"],
            origin_declared=wrapper["origin"],
            selected_consistency_checked=True,
            **result,
        )
    for kind in ("identity", "timing"):
        if "accounting" in sources and kind in sources:
            account, trial = sources["accounting"][1], sources[kind][1]
            if account["trial_sha256"] != sources[kind][0] or account[
                "raw_sha256"
            ] != trial.get("raw_log_sha256"):
                raise ValueError("accounting/trial source binding mismatch")
            declared = trial.get("event_type_counts")
            if (
                type(trial.get("matched_event_count")) is not int
                or trial["matched_event_count"] != account["validated_event_count"]
                or not isinstance(declared, dict)
                or any(type(count) is not int for count in declared.values())
                or declared != account["event_type_counts"]
            ):
                raise ValueError("trial counts contradict accounting source")
    if (
        "identity" in sources
        and "timing" in sources
        and sources["identity"][0] != sources["timing"][0]
    ):
        raise ValueError("identity/timing must bind same selected trial")
    return checks
