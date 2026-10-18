"""Reproducible baseline regression evaluation with raw predictions and timing."""

import argparse
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
from cloudguard.metrics import metrics, rule_metrics
from cloudguard.verification import file_hash, read_json

SOURCE_ROOT = ROOT


def evaluate():
    manifest = ROOT / "data/labels.json"
    records, manifest_hash = read_json(manifest)
    if type(records) is not list or not records or len(records) > 10000:
        raise ValueError("development manifest must be a bounded nonempty list")
    expected_rules = {}
    for record in records:
        if type(record) is not dict or type(record.get("id")) is not str:
            raise ValueError("invalid development record")
        if record["id"] in expected_rules:
            raise ValueError("duplicate development case identity")
        expected_rules[record["id"]] = record.get("expected_rules")
    # Validate all label identities before scanning; this is not a prediction run.
    rule_metrics(expected_rules, {case: [] for case in expected_rules})
    sources = [
        SOURCE_ROOT / name
        for name in (
            "scripts/evaluate.py",
            "cloudguard/scanner.py",
            "cloudguard/metrics.py",
            "cloudguard/verification.py",
            "cloudguard/limits.py",
        )
    ]
    source_hashes = {path.name: file_hash(path) for path in sources}
    labels = {}
    predictions = {}
    predicted_rules = {}
    rows = []
    timings = []
    mismatches = []
    for record in records:
        path = ROOT / record["path"]
        if file_hash(path) != record["sha256"]:
            raise ValueError("fixture checksum mismatch")
        samples = []
        for _ in range(5):
            start = time.perf_counter()
            result = scan(path)
            samples.append((time.perf_counter() - start) * 1000)
        actual = sorted(set(f["rule_id"] for f in result["findings"]))
        labels[record["id"]] = bool(record["expected_rules"])
        predictions[record["id"]] = bool(actual)
        predicted_rules[record["id"]] = actual
        if actual != sorted(record["expected_rules"]):
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
    if read_json(manifest)[1] != manifest_hash or any(
        file_hash(ROOT / record["path"]) != record["sha256"] for record in records
    ):
        raise ValueError("development evaluation inputs changed")
    if any(file_hash(path) != source_hashes[path.name] for path in sources):
        raise ValueError("development evaluation selected implementation changed")
    return dict(
        status="development_regression_failed"
        if mismatches
        else "development_regression_passed",
        manifest_file_sha256=manifest_hash,
        selected_implementation_sha256=source_hashes,
        run_at=datetime.now(timezone.utc).isoformat(),
        stage="development regression, NOT independent benchmark",
        python=sys.version,
        platform=platform.platform(),
        metrics=metrics(labels, predictions),
        rule_metrics=rule_metrics(expected_rules, predicted_rules),
        rule_set_mismatches=mismatches,
        median_ms=statistics.median(timings),
        p95_ms=sorted(timings)[int(0.95 * (len(timings) - 1))],
        repetitions=5,
        raw=rows,
        limitations=[
            "Fixtures authored alongside implementation; optimistic scores expected.",
            "Legacy binary case metrics collapse multiple findings; rule_metrics counts exact case/rule identities, not asset/location matches.",
            "No RAG effectiveness, FP reduction, cloud exposure, runtime ML or overhead conclusion.",
        ],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        required=True,
        help="Fresh report filename; existing files are refused",
    )
    args = parser.parse_args()
    try:
        with Path(args.output).open("x", encoding="utf-8") as stream:
            try:
                report = evaluate()
                code = 1 if report["rule_set_mismatches"] else 0
            except (Exception, KeyboardInterrupt) as error:
                code = 1
                report = dict(
                    status="rejected",
                    error_type=type(error).__name__,
                    stage="development regression, NOT independent benchmark",
                    actions_executed=[],
                )
            json.dump(report, stream, indent=2)
            stream.write("\n")
        print(json.dumps(dict(status=report["status"])))
        return code
    except (Exception, KeyboardInterrupt) as error:
        print(
            json.dumps(
                dict(status="output_refused_or_failed", error_type=type(error).__name__)
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
