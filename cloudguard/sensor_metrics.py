"""Minimized, hash-bound metrics from the pinned Falco trial; no completeness claim."""

import hashlib
import json
from pathlib import Path

from .sensor_adapter import unique, reject_constant

COUNTERS = ("scap.n_evts", "scap.n_drops", "falco.outputs_queue_num_drops")


def summarize(path, expected_sha256):
    with Path(path).open("rb") as stream:
        raw = stream.read(1_000_001)
    if len(raw) > 1_000_000:
        raise ValueError("metrics exceed 1 MB")
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected_sha256:
        raise ValueError("metrics hash mismatch")
    lines = raw.decode("utf-8", errors="strict").splitlines()
    if not 2 <= len(lines) <= 1000:
        raise ValueError("require 2..1000 metrics snapshots")
    selected = []
    for line in lines:
        row = json.loads(line, object_pairs_hook=unique, parse_constant=reject_constant)
        if not isinstance(row, dict) or not isinstance(row.get("output_fields"), dict):
            raise ValueError("invalid metrics envelope")
        fields = row["output_fields"]
        keys = ("evt.time", "falco.duration_sec", *COUNTERS)
        if any(type(fields.get(k)) is not int or fields[k] < 0 for k in keys):
            raise ValueError("missing or invalid metrics counter")
        sample = {k: fields[k] for k in keys}
        if selected and (
            sample["evt.time"] <= selected[-1]["evt.time"]
            or any(sample[k] < selected[-1][k] for k in keys[1:])
        ):
            raise ValueError("metrics time/counter reset or reordering")
        selected.append(sample)
    return dict(
        metrics_sha256=digest,
        snapshot_count=len(selected),
        first=selected[0],
        last=selected[-1],
        observed_counter_deltas={k: selected[-1][k] - selected[0][k] for k in COUNTERS},
        scope="collector-wide, not Redis-specific",
        coverage="partial_or_unknown",
        threat_confirmed=False,
        limits=[
            "Snapshots do not prove full capture interval coverage or absence of log rotation.",
            "Counters describe selected collector events, not all possible syscalls.",
            "Zero reported drops is not proof of complete delivery or benign behavior.",
        ],
    )
