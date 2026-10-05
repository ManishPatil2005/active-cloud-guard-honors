"""Linux LP64 timex observation: zero modes only, never a clock-setting API."""

import ctypes
import hashlib
import os
from pathlib import Path
import platform
import re
import sys
import time

from cloudguard import boot_clock, clock_lineage as lineage

PROTOCOL = "linux_raw_timex_pairs_v1"
LIBC = Path("/lib/x86_64-linux-gnu/libc.so.6")
ABI = "linux_x86_64_glibc239_timex208_v1"
READS = 16


class Timeval(ctypes.Structure):
    _fields_ = [("seconds", ctypes.c_int64), ("fraction", ctypes.c_int64)]


class Timex(ctypes.Structure):
    # Independent fixed-width LP64 representation; unsupported native ABIs refused.
    _fields_ = [
        ("modes", ctypes.c_uint32),
        *[
            (name, ctypes.c_int64)
            for name in ("offset", "freq", "maxerror", "esterror")
        ],
        ("status", ctypes.c_int32),
        *[(name, ctypes.c_int64) for name in ("constant", "precision", "tolerance")],
        ("time", Timeval),
        ("tick", ctypes.c_int64),
        ("ppsfreq", ctypes.c_int64),
        ("jitter", ctypes.c_int64),
        ("shift", ctypes.c_int32),
        *[
            (name, ctypes.c_int64)
            for name in ("stabil", "jitcnt", "calcnt", "errcnt", "stbcnt")
        ],
        ("tai", ctypes.c_int32),
        ("reserved", ctypes.c_int32 * 11),
    ]


def check_layout():
    offsets = {
        "modes": 0,
        "offset": 8,
        "freq": 16,
        "status": 40,
        "constant": 48,
        "tolerance": 64,
        "time": 72,
        "tick": 88,
        "tai": 160,
    }
    if ctypes.sizeof(Timex) != 208 or any(
        getattr(Timex, k).offset != v for k, v in offsets.items()
    ):
        raise ValueError("unsupported timex layout")


def native_backend():
    check_layout()
    if (
        sys.platform != "linux"
        or platform.machine() != "x86_64"
        or sys.byteorder != "little"
        or ctypes.sizeof(ctypes.c_long) != 8
        or ctypes.sizeof(ctypes.c_int) != 4
    ):
        raise ValueError("Linux x86_64 LP64 little-endian required")
    if os.geteuid() == 0:
        raise ValueError("unprivileged user required")
    library = ctypes.CDLL(str(LIBC), use_errno=True)
    version = library.gnu_get_libc_version
    version.argtypes, version.restype = [], ctypes.c_char_p
    if version() != b"2.39":
        raise ValueError("reviewed glibc 2.39 required")
    query = library.adjtimex
    query.argtypes, query.restype = [ctypes.POINTER(Timex)], ctypes.c_int
    metadata = dict(
        abi=ABI,
        glibc_version="2.39",
        timex_bytes=208,
        libc_sha256=hashlib.sha256(LIBC.read_bytes()).hexdigest(),
        unprivileged_user=True,
    )
    return query, metadata


def checked_state(value):
    signed = ("frequency_scaled_ppm", "phase_offset", "time_constant")
    positive = ("tick_usec",)
    nonnegative = ("status", "maxerror_usec", "esterror_usec", "tolerance_scaled_ppm")
    expected = {
        *signed,
        *positive,
        *nonnegative,
        "query_modes",
        "time_state",
        "phase_offset_unit",
    }
    if set(value) != expected:
        raise ValueError("unexpected kernel state fields")
    for key in (*signed, *positive, *nonnegative, "query_modes", "time_state"):
        n = value[key]
        if type(n) is not int or not -(2**63) <= n < 2**63:
            raise ValueError("invalid kernel state scalar")
    if (
        value["query_modes"] != 0
        or not 0 <= value["time_state"] <= 5
        or not 0 <= value["status"] <= 65535
        or any(value[k] < 0 for k in nonnegative)
        or value["tick_usec"] <= 0
        or value["phase_offset_unit"] != ("ns" if value["status"] & 0x2000 else "us")
    ):
        raise ValueError("incompatible kernel state")
    return value


def read_state(query):
    check_layout()
    buffer = Timex()  # Every input byte, including padding, is zero.
    if bytes(buffer) != b"\0" * 208 or buffer.modes != 0:
        raise ValueError("nonzero query input refused")
    result = query(ctypes.byref(buffer))
    if result == -1:
        raise OSError(ctypes.get_errno(), "kernel state query failed")
    return checked_state(
        dict(
            query_modes=0,
            time_state=result,
            status=buffer.status,
            frequency_scaled_ppm=buffer.freq,
            tick_usec=buffer.tick,
            phase_offset=buffer.offset,
            phase_offset_unit="ns" if buffer.status & 0x2000 else "us",
            time_constant=buffer.constant,
            maxerror_usec=buffer.maxerror,
            esterror_usec=buffer.esterror,
            tolerance_scaled_ppm=buffer.tolerance,
        )
    )


def state_sample(query, clock=None, *, evidence=None):
    if not hasattr(time, "CLOCK_MONOTONIC_RAW"):
        raise ValueError("native RAW required; no fallback")
    clock = clock or time.clock_gettime_ns
    value = {} if evidence is None else evidence
    value["raw_before_ns"] = clock(time.CLOCK_MONOTONIC_RAW)
    value["state"] = read_state(query)
    value["raw_after_ns"] = clock(time.CLOCK_MONOTONIC_RAW)
    return checked_sample(value)


def checked_sample(value):
    if set(value) != {"raw_before_ns", "raw_after_ns", "state"}:
        raise ValueError("unexpected state-sample fields")
    a, b = value["raw_before_ns"], value["raw_after_ns"]
    if any(type(n) is not int or n < 0 for n in (a, b)) or not 0 <= b - a <= 5_000_000:
        raise ValueError("invalid state-query RAW bracket")
    checked_state(value["state"])
    return value


def checked_metadata(value):
    if (
        set(value)
        != {"abi", "glibc_version", "timex_bytes", "libc_sha256", "unprivileged_user"}
        or value["abi"] != ABI
        or value["glibc_version"] != "2.39"
        or type(value["timex_bytes"]) is not int
        or value["timex_bytes"] != 208
        or value["unprivileged_user"] is not True
        or not isinstance(value["libc_sha256"], str)
        or not re.fullmatch(r"[0-9a-f]{64}", value["libc_sha256"])
    ):
        raise ValueError("incompatible backend metadata")


def checked_pair(p, previous=None):
    if p["status"] != "accepted":
        raise ValueError("incomplete kernel-state packet")
    a, b = checked_sample(p["before"]), checked_sample(p["after"])
    g = lineage.checked_guest(p["sample"], raw=True)
    boot_clock.checked_domain(p["domain"])
    if (
        not a["raw_after_ns"]
        <= g["raw_before_ns"]
        <= g["raw_after_ns"]
        <= b["raw_before_ns"]
    ):
        raise ValueError("kernel-state/sample order invalid")
    if previous:
        if p["domain"] != previous["domain"]:
            raise ValueError("clock domain changed")
        if (
            a["raw_before_ns"] < previous["after"]["raw_after_ns"]
            or g["mono_before_ns"] < previous["sample"]["mono_after_ns"]
            or g["boot_before_ns"] < previous["sample"]["boot_after_ns"]
        ):
            raise ValueError("kernel-state pairs out of sequence")


def summarize(packets):
    if (
        len(packets) != READS
        or any(type(p["index"]) is not int for p in packets)
        or [p["index"] for p in packets] != list(range(READS))
    ):
        raise ValueError("sixteen complete kernel-state pairs required")
    states, rows = [], []
    previous = None
    origin = packets[0]["sample"]
    for p in packets:
        checked_pair(p, previous)
        a, b = checked_sample(p["before"]), checked_sample(p["after"])
        g = lineage.checked_guest(p["sample"], raw=True)
        previous = p
        states += [a["state"], b["state"]]
        row = dict(index=p["index"])
        if p["index"]:
            raw_low = g["raw_before_ns"] - origin["raw_after_ns"]
            raw_high = g["raw_after_ns"] - origin["raw_before_ns"]
            mono_low = g["mono_before_ns"] - origin["mono_after_ns"]
            mono_high = g["mono_after_ns"] - origin["mono_before_ns"]
            row["raw_minus_mono_elapsed"] = lineage.interval(
                raw_low - mono_high, raw_high - mono_low
            )
        low, high = g["offset_lower_ns"], g["offset_upper_ns"]
        row["wall_minus_boot_change"] = lineage.interval(
            low - origin["offset_upper_ns"], high - origin["offset_lower_ns"]
        )
        rows.append(row)
    return dict(
        protocol=PROTOCOL,
        rows=rows,
        sampled_state_values={k: sorted({s[k] for s in states}) for k in states[0]},
        state_read_count=len(states),
        correction_applied=False,
        causal_attribution="not_proven",
        independent_evaluation=False,
    )
