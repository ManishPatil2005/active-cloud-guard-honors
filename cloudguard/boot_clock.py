"""Read-only boot/realtime bounds; not collector calibration or clock correction."""

import hashlib
import re
import time


def namespace_facts(namespace, offsets, boot_id):
    if not re.fullmatch(r"time:\[[0-9]+\]", namespace):
        raise ValueError("invalid time namespace")
    rows = {}
    for line in offsets.splitlines():
        parts = line.split()
        if (
            len(parts) != 3
            or parts[0] not in {"monotonic", "boottime"}
            or parts[0] in rows
        ):
            raise ValueError("invalid time namespace offsets")
        if any(not re.fullmatch(r"-?[0-9]{1,20}", p) for p in parts[1:]):
            raise ValueError("invalid namespace offset number")
        rows[parts[0]] = list(map(int, parts[1:]))
    if set(rows) != {"monotonic", "boottime"}:
        raise ValueError("missing time namespace offsets")
    if not re.fullmatch(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", boot_id):
        raise ValueError("invalid kernel boot identity")
    return dict(
        time_namespace=namespace,
        offsets=rows,
        kernel_boot_sha256=hashlib.sha256(boot_id.encode()).hexdigest(),
    )


def checked_domain(domain):
    """Validate one local domain without claiming other domains were observed."""
    if not re.fullmatch(
        r"time:\[[0-9]+\]", domain.get("time_namespace", "")
    ) or not re.fullmatch(r"[0-9a-f]{64}", domain.get("kernel_boot_sha256", "")):
        raise ValueError("invalid saved clock-domain facts")
    offsets = domain.get("offsets", {})
    if domain.get("time_namespace_for_children") != domain["time_namespace"]:
        raise ValueError("time namespace differs from children; offsets ambiguous")
    if set(offsets) != {"monotonic", "boottime"} or any(
        not isinstance(row, list)
        or len(row) != 2
        or any(type(n) is not int for n in row)
        for row in offsets.values()
    ):
        raise ValueError("invalid saved namespace offsets")
    if domain["offsets"] != {"monotonic": [0, 0], "boottime": [0, 0]}:
        raise ValueError("nonzero time namespace offset; boot comparison refused")


def checked_domains(domains):
    if len(domains) != 3:
        raise ValueError("harness, Redis and sensor clock domains required")
    for domain in domains:
        checked_domain(domain)
    if len({d["kernel_boot_sha256"] for d in domains}) != 1:
        raise ValueError("kernel identity differs; boot comparison refused")


def bounds(before, wall, after):
    if any(type(v) is not int or v < 0 for v in (before, wall, after)):
        raise ValueError("invalid boot-clock sample")
    if not before <= after or after - before > 5_000_000:
        raise ValueError("backward or overwide boot-clock sample")
    return dict(
        boot_before_ns=before,
        realtime_ns=wall,
        boot_after_ns=after,
        sampling_span_ns=after - before,
        offset_lower_ns=wall - after,
        offset_upper_ns=wall - before,
    )


def sample(clock=None):
    if not hasattr(time, "CLOCK_BOOTTIME"):
        raise ValueError("native CLOCK_BOOTTIME required; no monotonic fallback")
    clock = clock or time.clock_gettime_ns
    before = clock(time.CLOCK_BOOTTIME)
    wall = clock(time.CLOCK_REALTIME)
    after = clock(time.CLOCK_BOOTTIME)
    return bounds(before, wall, after)


def checked(value):
    expected = bounds(
        value["boot_before_ns"], value["realtime_ns"], value["boot_after_ns"]
    )
    if any(
        type(value.get(k)) is not type(v) or value[k] != v for k, v in expected.items()
    ):
        raise ValueError("inconsistent saved boot-clock bounds")
    return expected


def summarize(snapshots, observations, correlation):
    if (
        len(snapshots) != 3
        or [s["phase"] for s in snapshots]
        != ["before_sensor_launch", "after_sensor_launch", "after_readiness"]
        or len(observations) != 4
        or len(correlation["matches"]) != 4
    ):
        raise ValueError("fixed boot-clock diagnostic shape required")
    initial = checked(snapshots[0]["sample"])
    pids = [o.get("process_id") for o in observations]
    if any(type(p) is not int or p <= 0 for p in pids) or len(set(pids)) != 4:
        raise ValueError("four distinct boot-clock process IDs required")
    samples = [checked(s["sample"]) for s in snapshots]
    rows = []
    for o, row in zip(observations, correlation["matches"]):
        if o["process_id"] != row["process_id"]:
            raise ValueError("boot-clock process identity mismatch")
        first, last = checked(o["boot_before"]), checked(o["boot_after"])
        if last["boot_before_ns"] < first["boot_after_ns"]:
            raise ValueError("boot clock moved backwards across PING")
        samples += [first, last]
        event = row["event_unix_ns"]
        if type(event) is not int or not 0 <= event < 4133980800 * 10**9:
            raise ValueError("invalid event timestamp")
        low, high = event - last["boot_after_ns"], event - first["boot_before_ns"]
        rows.append(
            dict(
                process_id=o["process_id"],
                event_implied_offset_lower_ns=low,
                event_implied_offset_upper_ns=high,
                intersects_prelaunch_offset=low <= initial["offset_upper_ns"]
                and high >= initial["offset_lower_ns"],
            )
        )
    if any(
        b["boot_before_ns"] < a["boot_after_ns"] for a, b in zip(samples, samples[1:])
    ):
        raise ValueError("boot snapshots out of sequence")
    return dict(
        protocol="boot_realtime_brackets_v1",
        offset_changes_from_prelaunch=[
            dict(
                lower_ns=s["offset_lower_ns"] - initial["offset_upper_ns"],
                upper_ns=s["offset_upper_ns"] - initial["offset_lower_ns"],
            )
            for s in samples
        ],
        event_implied_offsets=rows,
        collector_calibration_value_observed=False,
        correction_applied=False,
        causal_attribution="not_proven",
        limits=[
            "Prelaunch is not the actual Falco calibration instant/value.",
            "Endpoint samples cannot exclude transient changes between reads.",
            "Namespace/kernel checks are local facts, not authenticated attestation.",
        ],
    )
