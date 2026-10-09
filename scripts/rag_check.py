"""Run a real local LLM with recorded evidence and timings; failures remain visible."""

import hashlib
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.llm import audit
from cloudguard.retrieval import retrieve
from cloudguard.evidence import evidence_main
from cloudguard.legacy_io import InputBudget


def collect(args):
    budget = InputBudget()
    results = []
    names = (
        "postgres-trust.yaml",
        "redis-unprotected.yaml",
        "postgres-reference.yaml",
    )
    inputs = {name: budget.text(ROOT / "data/development" / name) for name in names}
    budget.bytes(ROOT / "knowledge/sources.json")
    for name, text in inputs.items():
        budget.check()
        sources = retrieve(text, ROOT / "knowledge/sources.json")
        start = time.perf_counter()
        try:
            output = audit(text, sources, args.model, timeout=budget.timeout())
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
    return {"output": report}, int(any(r["error"] for r in results))


def main():
    return evidence_main(collect, model=True)


if __name__ == "__main__":
    raise SystemExit(main())
