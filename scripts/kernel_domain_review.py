"""Offline clock-domain accounting from saved receipts; never collects or sets time."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard import clock_lineage as lineage, kernel_clock_state as kernel
from cloudguard.limits import read_bytes
from scripts import kernel_clock_diagnostic as diagnostic


def offsets(sample):
    """Conservative bounds; no comparison of distinct clock epochs as elapsed time."""
    return {
        "wall_minus_mono": (
            sample["realtime_ns"] - sample["mono_after_ns"],
            sample["realtime_ns"] - sample["mono_before_ns"],
        ),
        "wall_minus_boot": (sample["offset_lower_ns"], sample["offset_upper_ns"]),
        "boot_minus_mono": (
            sample["boot_before_ns"] - sample["mono_after_ns"],
            sample["boot_after_ns"] - sample["mono_before_ns"],
        ),
        "raw_minus_mono": (
            sample["raw_before_ns"] - sample["mono_after_ns"],
            sample["raw_after_ns"] - sample["mono_before_ns"],
        ),
    }


def changes(current, origin):
    return {
        name: lineage.interval(low - origin[name][1], high - origin[name][0])
        for name, (low, high) in current.items()
    }


def review_batch(raw_reports):
    if type(raw_reports) not in (list, tuple) or len(raw_reports) not in (1, 4):
        raise ValueError("one saved block or exactly four planned blocks required")
    reports, bindings = [], []
    for raw in raw_reports:
        if type(raw) is not bytes:
            raise ValueError("saved receipt bytes required")
        verified = diagnostic.review(raw)  # Existing strict 100KB/schema/source checks.
        reports.append(lineage.strict_json(raw))
        bindings.append(verified["input_sha256"])
    first = reports[0]
    origin = offsets(first["packets"][0]["sample"])
    previous = None
    previous_offsets = None
    rows = []
    for block, report in enumerate(reports):
        if not lineage.same(report["backend"], first["backend"]):
            raise ValueError("backend changed across blocks")
        for packet in report["packets"]:
            kernel.checked_pair(
                packet, previous
            )  # Also checks cross-block domain/order.
            current = offsets(packet["sample"])
            row = dict(
                block=block,
                index=packet["index"],
                from_first=changes(current, origin),
                from_previous=None
                if previous is None
                else changes(current, previous_offsets),
                state_before=packet["before"]["state"],
                state_after=packet["after"]["state"],
            )
            rows.append(row)
            previous, previous_offsets = packet, current
    return dict(
        protocol="saved_kernel_domain_changes_v1",
        status="reviewed",
        input_sha256=bindings,
        blocks=len(reports),
        samples=len(rows),
        rows=rows,
        reviewer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        source_sha256=diagnostic.source_hashes(),
        live_actions_executed=[],
        clock_settings_modified=False,
        step_vs_slew_identified=False,
        causal_attribution="not_proven",
        stable_full_minute_verified=False,
        collector_capacity_verified=False,
        independently_evaluated=False,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, action="append")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if len(args.input) not in (1, 4):
        parser.error("one input or exactly four inputs required")
    with Path(args.output).open("x", encoding="utf-8") as stream:
        try:
            result = review_batch(
                [read_bytes(path, limit=100_000) for path in args.input]
            )
            code = 0
        except (Exception, KeyboardInterrupt) as error:
            result = dict(
                status="rejected",
                error_type=type(error).__name__,
                live_actions_executed=[],
                causal_attribution="not_proven",
            )
            code = 1
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps(dict(status=result["status"], live_actions_executed=[])))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
