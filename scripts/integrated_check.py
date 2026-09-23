"""One complete run: parse, vector retrieval, local model, staging probe, score."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.pipeline import run


def main():
    report = run(
        ROOT / "data/development/redis-all.yaml",
        ROOT / "knowledge/sources.json",
        ROOT / "testbed/inventory.json",
        model="qwen2.5:3b",
        vector_index=ROOT / "output/chroma",
    )
    (ROOT / "output/integrated-demo.json").write_text(json.dumps(report, indent=2))
    assert report["retrieval_mode"] == "chroma_ollama"
    assert report["rag"]["origin"] == "ollama_rag"
    assert report["findings"][0]["probe"]["outcome"] == "reachable"
    assert report["findings"][0]["priority"]["calibrated"] is False
    print("Integrated vector RAG + explicit staging probe + priority run passed.")


if __name__ == "__main__":
    main()
