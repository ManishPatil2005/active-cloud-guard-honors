"""Reproducible baseline regression evaluation with raw predictions and timing."""

import hashlib
import json
import platform
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.scanner import scan
from cloudguard.metrics import metrics


def main():
    records = json.loads((ROOT / "data/labels.json").read_text())
    labels = {}
    predictions = {}
    rows = []
    timings = []
    mismatches = []
    for record in records:
        path = ROOT / record["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
            raise ValueError("fixture checksum mismatch")
        samples = []
        for _ in range(5):
            start = time.perf_counter()
            result = scan(path)
            samples.append((time.perf_counter() - start) * 1000)
        actual = sorted(set(f["rule_id"] for f in result["findings"]))
        labels[record["id"]] = bool(record["expected_rules"])
        predictions[record["id"]] = bool(actual)
        if actual != record["expected_rules"]:
            mismatches.append(record["id"])
        timings.extend(samples)
        rows.append(
            dict(
                id=record["id"],
                expected=record["expected_rules"],
                predicted=actual,
                latency_ms=samples,
                sha256=record["sha256"],
            )
        )
    report = dict(
        run_at=datetime.now(timezone.utc).isoformat(),
        stage="development regression, NOT independent benchmark",
        python=sys.version,
        platform=platform.platform(),
        metrics=metrics(labels, predictions),
        rule_set_mismatches=mismatches,
        median_ms=statistics.median(timings),
        p95_ms=sorted(timings)[int(0.95 * (len(timings) - 1))],
        repetitions=5,
        raw=rows,
        limitations=[
            "Fixtures authored alongside implementation; optimistic scores expected.",
            "Binary case metrics collapse multiple findings. Exact rule-set checks are reported separately.",
            "No RAG effectiveness, FP reduction, cloud exposure, runtime ML or overhead conclusion.",
        ],
    )
    out = ROOT / "output"
    out.mkdir(exist_ok=True)
    (out / "baseline-development.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps({k: v for k, v in report.items() if k != "raw"}, indent=2))
    if mismatches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
