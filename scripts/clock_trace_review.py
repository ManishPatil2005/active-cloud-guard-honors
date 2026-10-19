"""Offline selected strace accounting; not trace completeness or writer attestation."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.limits import read_bytes

LIMIT = 1_048_576  # Existing QA-037 per-output-file ceiling, not a larger trace budget.
MODES = {
    "ADJ_OFFSET",
    "ADJ_FREQUENCY",
    "ADJ_MAXERROR",
    "ADJ_ESTERROR",
    "ADJ_STATUS",
    "ADJ_TIMECONST",
    "ADJ_TAI",
    "ADJ_SETOFFSET",
    "ADJ_MICRO",
    "ADJ_NANO",
    "ADJ_TICK",
    "ADJ_OFFSET_SINGLESHOT",
    "ADJ_OFFSET_SS_READ",
}
LINE = re.compile(
    r"[0-9]+\.[0-9]{6} (adjtimex|clock_adjtime|clock_settime|settimeofday)"
    r"\((.*)\) = (-?[0-9]+)(?: ([^\r\n]*?))? <[0-9]+\.[0-9]+>"
)


def review_trace(raw, expected_sha256):
    if type(raw) is not bytes or len(raw) > LIMIT:
        raise ValueError("trace byte budget or type rejected")
    digest = hashlib.sha256(raw).hexdigest()
    if (
        type(expected_sha256) is not str
        or not re.fullmatch("[a-f0-9]{64}", expected_sha256)
        or digest != expected_sha256
    ):
        raise ValueError("trace digest mismatch")
    lines = raw.decode("ascii").splitlines()
    if len(lines) > 4096 or any(len(line) > 4096 for line in lines):
        raise ValueError("trace review structure budget exceeded")
    rows = []
    for index, line in enumerate(lines):
        match = LINE.fullmatch(line)
        if match is None:
            rows.append(dict(line=index, status="uninterpreted"))
            continue
        name, args, result, _ = match.groups()
        result = int(result)
        row = dict(
            line=index,
            syscall=name,
            status="uninterpreted",
            return_value=result,
            entry_buffer_verified=False,
        )
        if name in {"adjtimex", "clock_adjtime"}:
            prefix = "" if name == "adjtimex" else "CLOCK_REALTIME, "
            pattern = re.escape(prefix) + r"\{modes=([A-Z0-9_|]+), .+\}"
            mode = re.fullmatch(pattern, args)
            if mode is not None and (result == -1 or 0 <= result <= 5):
                tokens = mode[1].split("|")
                known = len(tokens) == len(set(tokens)) and (
                    tokens == ["0"] or set(tokens) <= MODES
                )
                if known:
                    kind = (
                        "decoded_query_mode"
                        if tokens == ["0"]
                        else "decoded_read_marker"
                        if "ADJ_OFFSET_SS_READ" in tokens
                        else "decoded_nonquery_modes"
                    )
                    row.update(
                        status="parsed",
                        mode_observation=kind,
                        decoded_modes=tokens,
                        decode_phase="syscall_exit",
                        completion="failed"
                        if result == -1
                        else "nonnegative_return_state",
                    )
        elif result in (-1, 0):
            # A setter name, even with return 0, is not proof of a changed clock:
            # NULL arguments, other clock IDs and effects need separate review.
            row.update(
                status="parsed",
                mode_observation="setter_name_only",
                completion="failed" if result == -1 else "zero_return",
            )
        rows.append(row)
    return dict(
        protocol="selected_strace_accounting_v1",
        decoder_profile="strace_6_8_single_pid_ttt_T_s128",
        reviewer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        input_sha256=digest,
        bytes=len(raw),
        lines=len(lines),
        rows=rows,
        parsed_calls=sum(row["status"] == "parsed" for row in rows),
        uninterpreted_lines=sum(row["status"] == "uninterpreted" for row in rows),
        live_actions_executed=[],
        process_identity_verified=False,
        trace_completeness_verified=False,
        entry_buffer_verified=False,
        returned_timex_values_are_requests=False,
        cause_identified=False,
        global_writer_coverage=False,
        independent_evaluation=False,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    with Path(args.output).open("x", encoding="utf-8") as stream:
        try:
            result = review_trace(
                read_bytes(args.input, limit=LIMIT), args.expected_sha256
            )
            code = 0
        except (Exception, KeyboardInterrupt) as error:
            result = dict(
                status="rejected",
                error_type=type(error).__name__,
                live_actions_executed=[],
                cause_identified=False,
            )
            code = 1
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(
        json.dumps(
            dict(
                status="reviewed" if code == 0 else "rejected", live_actions_executed=[]
            )
        )
    )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
