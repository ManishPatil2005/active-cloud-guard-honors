"""Interval-only host/guest clock comparison, not calibration or causal proof."""

import json
import time

from cloudguard import boot_clock, clock_check

PROTOCOL = "windows_wsl_clock_lineage_v1"
READS = 16
GAP_SECONDS = 1
TIMEOUT_SECONDS = 5
MAX_ROUND_TRIP_NS = 2_000_000_000


def interval(low, high):
    if low > high:
        raise ValueError("inverted interval")
    return dict(lower_ns=low, upper_ns=high, includes_zero=low <= 0 <= high)


def native_snapshot(clock=None):
    if not hasattr(time, "CLOCK_BOOTTIME"):
        raise ValueError("native CLOCK_BOOTTIME required")
    clock = clock or time.clock_gettime_ns
    mono_before = clock(time.CLOCK_MONOTONIC)
    sample = boot_clock.sample(clock)
    mono_after = clock(time.CLOCK_MONOTONIC)
    return checked_guest(
        dict(**sample, mono_before_ns=mono_before, mono_after_ns=mono_after)
    )


def checked_guest(value):
    expected = boot_clock.checked(value)
    before, after = value["mono_before_ns"], value["mono_after_ns"]
    if (
        any(type(n) is not int or n < 0 for n in (before, after))
        or not 0 <= after - before <= 5_000_000
    ):
        raise ValueError("invalid guest monotonic bracket")
    expected.update(mono_before_ns=before, mono_after_ns=after)
    if value != expected or set(value) != set(expected):
        raise ValueError("unexpected guest sample fields")
    return expected


def checked_host(value):
    if set(value) != {"wall_ns", "monotonic_mid_ns", "sampling_span_ns"}:
        raise ValueError("unexpected host fields")
    if any(type(n) is not int or n < 0 for n in value.values()):
        raise ValueError("invalid host scalar")
    if value["sampling_span_ns"] > 5_000_000:
        raise ValueError("overwide host sample")
    return value


def counter_bounds(value):
    half = (value["sampling_span_ns"] + 1) // 2
    return value["monotonic_mid_ns"] - half, value["monotonic_mid_ns"] + half


def checked_packet(packet, sources):
    if packet["status"] != "accepted":
        raise ValueError("incomplete packet")
    first, last = checked_host(packet["host_first"]), checked_host(packet["host_last"])
    comparison = clock_check.compare(first, last)
    if not same(packet["comparison"], comparison) or not comparison["within_tolerance"]:
        raise ValueError("host clock bracket incompatible")
    if comparison["elapsed_monotonic_ns"] > MAX_ROUND_TRIP_NS:
        raise ValueError("host round trip exceeds diagnostic bound")
    checked_reply(packet["guest"], sources)


def same(first, last):
    """JSON equality without Python's bool/int or int/float coercion."""
    return json.dumps(first, sort_keys=True, allow_nan=False) == json.dumps(
        last, sort_keys=True, allow_nan=False
    )


def checked_reply(guest, sources):
    if set(guest) != {"sample", "domain", "source_sha256"}:
        raise ValueError("unexpected guest fields")
    if set(guest["domain"]) != {
        "time_namespace",
        "time_namespace_for_children",
        "offsets",
        "kernel_boot_sha256",
    }:
        raise ValueError("unexpected domain fields")
    boot_clock.checked_domain(guest["domain"])
    if guest["source_sha256"] != sources:
        raise ValueError("guest source mismatch")
    checked_guest(guest["sample"])
    return guest


def summarize(packets, sources):
    if (
        len(packets) != READS
        or any(type(p["index"]) is not int for p in packets)
        or [p["index"] for p in packets] != list(range(READS))
    ):
        raise ValueError("fixed sixteen-packet protocol required")
    for packet in packets:
        checked_packet(packet, sources)
    if any(p["guest"]["domain"] != packets[0]["guest"]["domain"] for p in packets):
        raise ValueError("guest domain changed")
    for first, last in zip(packets, packets[1:]):
        if (
            counter_bounds(last["host_first"])[0]
            - counter_bounds(first["host_last"])[1]
            < GAP_SECONDS * 10**9
        ):
            raise ValueError("fixed gap not established")
        for key in ("mono", "boot"):
            if (
                last["guest"]["sample"][f"{key}_before_ns"]
                < first["guest"]["sample"][f"{key}_after_ns"]
            ):
                raise ValueError("guest sequence moved backward")
    initial = packets[0]
    origin = initial["guest"]["sample"]
    rows = []
    for packet in packets:
        guest = packet["guest"]["sample"]
        first, last = packet["host_first"], packet["host_last"]
        allowance = (
            abs(packet["comparison"]["clock_difference_ns"])
            + packet["comparison"]["sampling_uncertainty_ns"]
        )
        row = dict(
            index=packet["index"],
            guest_minus_host_wall=interval(
                guest["realtime_ns"] - last["wall_ns"] - allowance,
                guest["realtime_ns"] - first["wall_ns"] + allowance,
            ),
        )
        for key in ("boot", "mono"):
            low = guest["realtime_ns"] - guest[f"{key}_after_ns"]
            high = guest["realtime_ns"] - guest[f"{key}_before_ns"]
            origin_low = origin["realtime_ns"] - origin[f"{key}_after_ns"]
            origin_high = origin["realtime_ns"] - origin[f"{key}_before_ns"]
            row[f"wall_minus_{key}_change"] = interval(
                low - origin_high, high - origin_low
            )
            if packet["index"]:
                # Guest clock epochs are never compared to the host counter epoch.
                host_low = (
                    counter_bounds(first)[0] - counter_bounds(initial["host_last"])[1]
                )
                host_high = (
                    counter_bounds(last)[1] - counter_bounds(initial["host_first"])[0]
                )
                guest_low = guest[f"{key}_before_ns"] - origin[f"{key}_after_ns"]
                guest_high = guest[f"{key}_after_ns"] - origin[f"{key}_before_ns"]
                row[f"host_minus_guest_{key}_elapsed"] = interval(
                    host_low - guest_high, host_high - guest_low
                )
        rows.append(row)
    return dict(
        protocol=PROTOCOL,
        rows=rows,
        correction_applied=False,
        causal_attribution="not_proven",
        independent_evaluation=False,
    )


def strict_json(raw):
    if len(raw) > 100_000:
        raise ValueError("overlarge diagnostic receipt")

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON field")
            result[key] = value
        return result

    def constant(value):
        raise ValueError("nonfinite JSON value")

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
