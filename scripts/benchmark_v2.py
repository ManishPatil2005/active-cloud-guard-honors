"""Local v2 efficiency smoke, not an independent accuracy study."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import time
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.pipeline import run
from cloudguard.vector import index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", required=True, help="New evidence file; never overwritten"
    )
    parser.add_argument("--model", default="qwen2.5:3b")
    args = parser.parse_args()
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("x", encoding="utf-8") as stream:
        stream.write("{}\n")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    cache = Path("output/audit-cache") / stamp
    source = Path("data/development/redis-all.yaml")
    kb = Path("knowledge/sources.json")
    result = dict(
        started_at=datetime.now(timezone.utc).isoformat(),
        platform=platform.platform(),
        python=platform.python_version(),
        model=args.model,
        input_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        corpus_sha256=hashlib.sha256(kb.read_bytes()).hexdigest(),
        protocol="Forced index build, reuse; lexical uncached, cache miss, two hits. Sequential development smoke; cache miss is warm-model, not cold-model.",
        limitations=[
            "No matched v1 comparison",
            "No accuracy or energy measurement",
            "Vector query embeddings are not cached",
            "Single fixture; not a latency distribution",
        ],
        index_runs=[],
        pipeline_runs=[],
    )

    def save():
        destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    try:
        for force in (True, False):
            start = time.perf_counter()
            observation = index(kb, "output/chroma", force=force)
            result["index_runs"].append(
                dict(
                    force=force,
                    elapsed_ms=round((time.perf_counter() - start) * 1000, 3),
                    result=observation,
                )
            )
            save()
        for label in ("uncached", "cache_miss", "cache_hit_1", "cache_hit_2"):
            observation = run(
                source,
                kb,
                "testbed/inventory.json",
                model=args.model,
                cache_dir=None if label == "uncached" else cache,
                max_tokens=512,
            )
            result["pipeline_runs"].append(dict(label=label, report=observation))
            save()
        audits = [entry["report"]["rag"] for entry in result["pipeline_runs"]]
        result["checks"] = dict(
            cache_sequence=[a["cache_status"] for a in audits]
            == ["disabled", "miss", "hit", "hit"],
            cached_candidates_unchanged=all(
                a["output"] == audits[1]["output"]
                and a["rejected_findings"] == audits[1]["rejected_findings"]
                for a in audits[2:]
            ),
            reused_index_without_embeddings=result["index_runs"][1]["result"][
                "embedded_documents"
            ]
            == 0,
        )
        result["completed_at"] = datetime.now(timezone.utc).isoformat()
        save()
        if not all(result["checks"].values()):
            raise RuntimeError("v2 smoke acceptance check failed")
    except Exception as error:
        result["error"] = dict(
            type=type(error).__name__,
            message=str(error),
            raw_output=getattr(error, "raw_output", None),
        )
        save()
        raise
    print(json.dumps(dict(output=str(destination), checks=result["checks"])))


if __name__ == "__main__":
    main()
