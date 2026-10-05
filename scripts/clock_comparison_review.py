"""Offline three-receipt comparison only: no service commands or live launcher."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard import clock_comparison as comparison, clock_lineage as lineage
from scripts import kernel_clock_diagnostic as observer


def execution_source_hashes():
    return {
        p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
        for p in comparison.EXECUTION_SOURCES
    }


def verify_receipt(raw, label):
    if label not in comparison.LABELS:
        raise ValueError("unknown comparison label")
    reviewed = observer.review(raw)
    receipt = lineage.strict_json(raw)
    return dict(
        label=label,
        input_sha256=reviewed["input_sha256"],
        backend=receipt["backend"],
        sources=receipt["source_sha256"],
        first=receipt["packets"][0],
        last=receipt["packets"][-1],
        summary=reviewed["summary"],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for label in comparison.LABELS:
        parser.add_argument(f"--{label}", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    blocks = []
    for label in comparison.LABELS:
        with Path(getattr(args, label)).open("rb") as stream:
            raw = stream.read(100001)
        blocks.append(verify_receipt(raw, label))
    summary = comparison.compare_verified(blocks)
    with Path(args.output).open("x", encoding="utf-8") as stream:
        json.dump(summary, stream, indent=2)
        stream.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
