"""Bounded lab PID correlation; no command text or historical time correction."""

from datetime import datetime, timezone
import json
import re

from .sensor_adapter import ENVELOPE, FIELDS, RULE, unique, reject_constant
from .clock_check import compare


def parse_ping(reply):
    parts = reply.splitlines()
    if (
        len(parts) != 2
        or not re.fullmatch(r"[1-9][0-9]{0,9}", parts[0])
        or parts[1] != "PONG"
    ):
        raise ValueError("expected local PID and PONG")
    return int(parts[0])


def correlate(raw, container, pids, calls):
    if not re.fullmatch(r"[a-f0-9]{64}", container):
        raise ValueError("full target identity required")
    if (
        len(pids) != 4
        or len(calls) != 4
        or len(set(pids)) != 4
        or any(type(p) is not int or p <= 0 for p in pids)
    ):
        raise ValueError("four distinct measured process identities required")
    if len(raw) > 1_000_000:
        raise ValueError("oversized diagnostic log")
    matches = {p: [] for p in pids}
    for line in raw.decode("utf-8").splitlines():
        if not line.lstrip().startswith(("{", "[")):
            continue
        event = json.loads(
            line, object_pairs_hook=unique, parse_constant=reject_constant
        )
        if (
            not isinstance(event, dict)
            or set(event) != ENVELOPE
            or event["rule"] != RULE
            or event["source"] != "syscall"
        ):
            raise ValueError("unexpected diagnostic envelope")
        fields = event["output_fields"]
        if not isinstance(fields, dict) or set(fields) != FIELDS | {"proc.vpid"}:
            raise ValueError("unexpected diagnostic fields")
        pid, ns, result = (
            fields["proc.vpid"],
            fields["evt.rawtime"],
            fields["evt.rawres"],
        )
        if (
            type(pid) is not int
            or pid <= 0
            or type(ns) is not int
            or not 0 <= ns < 4133980800 * 10**9
            or type(result) is not int
            or result < 0
        ):
            raise ValueError("invalid diagnostic numbers")
        seconds, fraction = divmod(ns, 10**9)
        stamp = (
            datetime.fromtimestamp(seconds, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
            + f".{fraction:09d}Z"
        )
        if (
            type(fields["evt.time"]) is not int
            or fields["evt.time"] != ns
            or event["time"] != stamp
        ):
            raise ValueError("timestamp disagreement")
        if (
            fields["evt.type"]
            not in {"execve", "execveat", "open", "openat", "openat2", "connect"}
            or not isinstance(fields["thread.cgroups"], str)
            or not re.search(
                r"(?<![a-f0-9])" + container + r"(?![a-f0-9])", fields["thread.cgroups"]
            )
        ):
            raise ValueError("unexpected diagnostic scope")
        if fields["evt.type"] == "connect" and pid in matches:
            matches[pid].append(ns)
    rows = []
    for pid, call in zip(pids, calls):
        if len(matches[pid]) != 1:
            raise ValueError("missing or ambiguous process connection")
        clock = call["clock_sampling"]
        timing = compare(clock["first"], clock["last"])
        if not timing["within_tolerance"] or call.get("pong") is not True:
            raise ValueError("invalid command clock bracket")
        ns = matches[pid][0]
        allowance = (
            abs(timing["clock_difference_ns"]) + timing["sampling_uncertainty_ns"]
        )
        low = ns - clock["last"]["wall_ns"] - allowance
        high = ns - clock["first"]["wall_ns"] + allowance
        rows.append(
            dict(
                process_id=pid,
                event_unix_ns=ns,
                offset_lower_ns=low,
                offset_upper_ns=high,
                zero_within_bounds=low <= 0 <= high,
            )
        )
    return dict(
        protocol="container_pid_connect_v1",
        matches=rows,
        zero_excluded_samples=sum(not r["zero_within_bounds"] for r in rows),
        authenticated=False,
        correction_applied=False,
        coverage="partial_or_unknown",
    )
