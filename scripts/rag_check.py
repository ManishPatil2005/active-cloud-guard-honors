"""Run a real local LLM with recorded evidence and timings; failures remain visible."""

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.llm import audit
from cloudguard.retrieval import retrieve


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen2.5:3b")
    args = parser.parse_args()
    results = []
    for name in (
        "postgres-trust.yaml",
        "redis-unprotected.yaml",
        "postgres-reference.yaml",
    ):
        text = (ROOT / "data/development" / name).read_text()
        sources = retrieve(text, ROOT / "knowledge/sources.json")
        start = time.perf_counter()
        try:
            output = audit(text, sources, args.model)
            error = None
        except Exception as exc:
            output = {"rejected_raw": getattr(exc, "raw_output", None)}
            error = type(exc).__name__
        results.append(
            dict(
                case=name,
                sha256=hashlib.sha256(text.encode()).hexdigest(),
                sources=sources,
                result=output,
                error=error,
                elapsed_s=time.perf_counter() - start,
            )
        )
    report = dict(
        observed_at=datetime.now(timezone.utc).isoformat(),
        model=args.model,
        cases=results,
        scope="three-case functional smoke test; not RAG accuracy benchmark",
    )
    (ROOT / "output").mkdir(exist_ok=True)
    (ROOT / "output/rag-smoke.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    if any(r["error"] for r in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
