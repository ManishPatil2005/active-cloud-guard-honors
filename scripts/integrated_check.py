"""One complete run: parse, vector retrieval, local model, staging probe, score."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.pipeline import run
from cloudguard.evidence import evidence_main


def collect(args):
    report = run(
        ROOT / "data/development/redis-all.yaml",
        ROOT / "knowledge/sources.json",
        ROOT / "testbed/inventory.json",
        model="qwen2.5:3b",
        vector_index=ROOT / "output/chroma",
    )
    try:
        passed = (
            report["retrieval_mode"] == "chroma_ollama"
            and report["rag"]["origin"] == "ollama_rag"
            and report["findings"][0]["probe"]["outcome"] == "reachable"
            and report["findings"][0]["priority"]["calibrated"] is False
        )
    except (KeyError, IndexError, TypeError):
        passed = False
    return {"output": report}, int(not passed)


def main():
    return evidence_main(collect)


if __name__ == "__main__":
    raise SystemExit(main())
