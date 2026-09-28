"""Offline adapter for the bounded ACG Falco trial, not arbitrary Falco alerts."""

from collections import Counter
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re

from .runtime import CAPTURE_SCHEMA
from .verification import load_inventory, read_json, validate

RULE = "ACG Redis selected syscall smoke"
KINDS = {
    "execve": "process_start",
    "execveat": "process_start",
    "open": "file_open",
    "openat": "file_open",
    "openat2": "file_open",
    "connect": "network_connect",
}
IMAGE = "falcosecurity/falco@sha256:788f1129c542171813083d4afc61b16730a47dde8c23d9c39370acef996349b6"
ENVELOPE = {
    "hostname",
    "output",
    "output_fields",
    "priority",
    "rule",
    "source",
    "tags",
    "time",
}
FIELDS = {"evt.rawres", "evt.rawtime", "evt.time", "evt.type", "thread.cgroups"}


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_key")
        result[key] = value
    return result


def reject_constant(_):
    raise ValueError("nonfinite_json")


def normalize(raw_path, trial_path, inventory, *, asset_id, capture_id, scenario_group):
    """Return minimized capture plus accounting; rejected inputs never yield a capture."""
    assets, inventory_hash = load_inventory(inventory)
    trial, trial_hash = read_json(trial_path)
    if not isinstance(trial, dict) or not (
        trial.get("image") == IMAGE
        and trial.get("status") == "events_observed"
        and type(trial.get("exit_code")) is int
        and trial["exit_code"] == 0
        and trial.get("sensor_removed") is True
        and trial.get("workload_result") == "PONG"
    ):
        raise ValueError("successful supported trial receipt required")
    container = trial.get("container_id")
    if not isinstance(container, str) or not re.fullmatch("[a-f0-9]{64}", container):
        raise ValueError("full container identity required")
    if asset_id not in assets:
        raise ValueError("unknown inventory asset")
    capture = dict(
        schema_version="1.0",
        capture_id=capture_id,
        scenario_group=scenario_group,
        source="normalized_sensor_export",
        bindings=[dict(container_id=container, asset_id=asset_id)],
        events=[],
    )
    validate(capture, CAPTURE_SCHEMA)
    with Path(raw_path).open("rb") as stream:
        raw = stream.read(1_000_001)
    if len(raw) > 1_000_000:
        raise ValueError("raw export exceeds 1 MB")
    digest = hashlib.sha256(raw).hexdigest()
    if digest != trial.get("raw_log_sha256"):
        raise ValueError("raw export hash mismatch")
    text = raw.decode("utf-8", errors="strict")
    lines = text.splitlines()
    if len(lines) > 10000:
        raise ValueError("raw export exceeds line limit")
    rejected, counts = Counter(), Counter()
    diagnostic_lines = 0
    seen = set()
    for line in lines:
        # The harness concatenates JSON stdout with diagnostic stderr. Never infer
        # sensor loss from diagnostic strings, including '0 drop occurrences'.
        if not line.lstrip().startswith(("{", "[")):
            diagnostic_lines += 1
            continue
        try:
            event = json.loads(
                line, object_pairs_hook=unique, parse_constant=reject_constant
            )
            if not isinstance(event, dict) or set(event) != ENVELOPE:
                raise ValueError("envelope_schema")
            if event["source"] != "syscall" or event["rule"] != RULE:
                raise ValueError("event_selection")
            fields = event["output_fields"]
            if not isinstance(fields, dict) or set(fields) != FIELDS:
                raise ValueError("field_schema")
            kind = fields["evt.type"]
            result = fields["evt.rawres"]
            ns = fields["evt.rawtime"]
            cgroups = fields["thread.cgroups"]
            if not isinstance(kind, str) or kind not in KINDS:
                raise ValueError("event_kind")
            if type(result) is not int or result < 0:
                raise ValueError("event_result")
            if type(ns) is not int or not 0 <= ns < 4133980800 * 10**9:
                raise ValueError("event_timestamp")
            if type(fields["evt.time"]) is not int or fields["evt.time"] != ns:
                raise ValueError("timestamp_disagreement")
            seconds, fraction = divmod(ns, 10**9)
            instant = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(
                seconds=seconds
            )
            stamp = instant.strftime("%Y-%m-%dT%H:%M:%S") + f".{fraction:09d}Z"
            if event["time"] != stamp:
                raise ValueError("timestamp_disagreement")
            if not isinstance(cgroups, str) or not re.search(
                r"(?<![a-f0-9])" + container + r"(?![a-f0-9])", cgroups
            ):
                raise ValueError("container_scope")
            # Content identity is independent of file order/name. Same projection
            # cannot be disambiguated by this minimal collector: fail closed.
            identity = hashlib.sha256(
                f"{container}:{ns}:{kind}:{result}".encode()
            ).hexdigest()
            if identity in seen:
                raise ValueError("duplicate_projection")
            if len(capture["events"]) >= 2000:
                raise ValueError("event_limit")
            seen.add(identity)
            counts[kind] += 1
            capture["events"].append(
                dict(
                    event_id=identity,
                    timestamp=stamp,
                    container_id=container,
                    kind=KINDS[kind],
                )
            )
        except (ValueError, TypeError, RecursionError) as error:
            reason = str(error) if type(error) is ValueError else "invalid_json"
            allowed = {
                "duplicate_key",
                "nonfinite_json",
                "envelope_schema",
                "event_selection",
                "field_schema",
                "event_kind",
                "event_result",
                "event_timestamp",
                "timestamp_disagreement",
                "container_scope",
                "duplicate_projection",
                "event_limit",
            }
            rejected[reason if reason in allowed else "invalid_json"] += 1
    declared_counts = trial.get("event_type_counts")
    receipt_matches = (
        type(trial.get("matched_event_count")) is int
        and isinstance(declared_counts, dict)
        and all(type(n) is int and n >= 0 for n in declared_counts.values())
        and trial["matched_event_count"] == sum(counts.values())
        and declared_counts == dict(counts)
    )
    accepted = bool(counts) and not rejected and receipt_matches
    capture["events"].sort(key=lambda e: (e["timestamp"], e["event_id"]))
    validate(capture, CAPTURE_SCHEMA)
    return dict(
        capture=capture if accepted else None,
        accounting=dict(
            adapter_version="0.1",
            status="normalized" if accepted else "rejected",
            raw_sha256=digest,
            trial_sha256=trial_hash,
            inventory_sha256=inventory_hash,
            line_count=len(lines),
            diagnostic_line_count=diagnostic_lines,
            validated_event_count=sum(counts.values()),
            rejected_record_count=sum(rejected.values()),
            rejection_reasons=dict(rejected),
            event_type_counts=dict(counts),
            receipt_counts_match=receipt_matches,
            sensor_dropped_events=None,
            collection_coverage="partial_or_unknown",
            binding_verified=False,
            threat_confirmed=False,
            actions_executed=[],
            timestamp_precision="nanoseconds retained; runtime parser truncates to microseconds before floating-point windowing",
        ),
    )
