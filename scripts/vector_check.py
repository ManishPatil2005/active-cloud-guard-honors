"""Build and functionally check actual local embeddings plus Chroma retrieval."""

import json
import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.vector import index, retrieve_vector
from cloudguard.llm import audit


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen2.5:3b")
    args = parser.parse_args()
    start = time.perf_counter()
    indexed = index(ROOT / "knowledge/sources.json", ROOT / "output/chroma")
    queries = [
        ("PostgreSQL trust authentication", "postgres-trust"),
        ("Redis protected-mode disabled", "redis-security"),
        ("wildcard Kubernetes RBAC permissions", "k8s-rbac"),
    ]
    checks = []
    for query, expected in queries:
        docs = retrieve_vector(
            query, ROOT / "knowledge/sources.json", ROOT / "output/chroma"
        )
        checks.append(
            dict(
                query=query,
                expected=expected,
                retrieved=[d["id"] for d in docs],
                passed=expected in [d["id"] for d in docs],
            )
        )
    text = (ROOT / "data/development/postgres-trust.yaml").read_text()
    docs = retrieve_vector(
        text, ROOT / "knowledge/sources.json", ROOT / "output/chroma"
    )
    try:
        result = audit(text, docs, args.model)
        error = None
    except Exception as exc:
        result = {"rejected_raw": getattr(exc, "raw_output", None)}
        error = type(exc).__name__
    report = dict(
        observed_at=datetime.now(timezone.utc).isoformat(),
        index=indexed,
        checks=checks,
        rag=dict(case="postgres-trust.yaml", sources=docs, result=result, error=error),
        elapsed_s=time.perf_counter() - start,
        limitation="Functional checks on three hand-selected queries; not retrieval generalization or RAG accuracy.",
    )
    (ROOT / "output").mkdir(exist_ok=True)
    (ROOT / "output/vector-smoke.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    if error or not all(c["passed"] for c in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
