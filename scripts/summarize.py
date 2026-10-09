"""Build a compact evidence ledger from actual saved runs, not guessed results."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.evidence import evidence_main


def collect(args):
    def load(name):
        return json.loads((ROOT / "output" / name).read_text())

    baseline = load("baseline-development.json")
    live = load("live-testbed.json")
    rag = load("rag-smoke.json")
    vector = load("vector-smoke.json")
    trivy = load("trivy-baseline.json")
    tests = ET.parse(ROOT / "output/test-results.xml").getroot()
    suites = list(tests.iter("testsuite"))
    n = sum(int(s.attrib.get("tests", 0)) for s in suites)
    failures = sum(
        int(s.attrib.get("failures", 0)) + int(s.attrib.get("errors", 0))
        for s in suites
    )
    lines = [
        "# Research milestone: actual implementation and test evidence",
        "",
        "Historical first-three-month evidence summary for Manish Patil. Generated "
        + datetime.now(timezone.utc).isoformat()
        + "; input files retain their original timestamps. This is not the current full-project status or a completed effectiveness study.",
        "",
        "## Verified engineering outcomes",
        "",
        "| Check | Observed result |",
        "|---|---|",
        f"| Automated software tests | {n} tests; {failures} failures/errors |",
        f"| Seeded development corpus | {baseline['metrics']['n']} cases; {len(baseline['rule_set_mismatches'])} rule-set mismatches |",
        f"| Rule scan timing | Median {baseline['median_ms']:.3f} ms; p95 {baseline['p95_ms']:.3f} ms; five repeats/case |",
        f"| Live services | {sum(p['outcome'] == 'reachable' for p in live['tcp'])}/4 TCP accepts from localhost |",
        f"| HTTP checks | {sum(p.get('status') == 200 for p in live['http'])}/2 HTTP 200 responses |",
        f"| Chroma index | {vector['index']['count']} source summaries; local embeddings |",
        f"| Semantic source checks | {sum(c['passed'] for c in vector['checks'])}/{len(vector['checks'])} expected sources in top three |",
        f"| Trivy baseline execution | {len(trivy['cases'])} independently scanned fixtures; {len(trivy['excluded'])} excluded for coverage |",
        "",
        "## Real LLM observations",
        "",
        f"Model: `{rag['model']}`. These cases were used for development and prompt/model selection.",
        "",
        "| Case | Retained candidates | Rejected candidates | Latency | Error |",
        "|---|---:|---:|---:|---|",
    ]
    for case in rag["cases"]:
        result = case.get("result") or {}
        lines.append(
            f"| {case['case']} | {len(result.get('output', {}).get('findings', []))} | {len(result.get('rejected_findings', []))} | {case['elapsed_s']:.2f} s | {case['error'] or 'none'} |"
        )
    lines += [
        "",
        "The first 1.5B model produced schema errors and hallucinated fields. The 3B model also produced an unsupported PostgreSQL-trust claim for a password placeholder. Original observations are preserved. Exact input-location checks and narrow deterministic PostgreSQL/Redis evidence guards now reject unsupported candidates. Other policy types still require human entailment review. A rejected candidate is an abstention, not proof that the configuration is clean.",
        "",
        "Model latency exceeds the proposed 3.5-second target on these runs. That target is not achieved. The scanner-only timing above excludes retrieval and LLM inference. No 90% false-positive reduction, held-out F1 .92, runtime AUC .95 or CPU-overhead target is claimed.",
        "",
        "## Architecture and research corrections",
        "",
        "The implementation separates configuration predicates, live network observations and policy decisions. The provisional score never lowers risk merely because an endpoint is reachable. A refused/inconclusive TCP probe never erases a secret or authorization finding. LLM candidates require review and do not directly authorize deployment or probing.",
        "",
        "The original sequence needs an isolated staging deployment before live verification; it cannot probe a service that does not yet exist. A dedicated Docker bridge with loopback publishing is used here; egress is not isolated. Historical image tags and model digests are recorded for reproduction, not recommended for production.",
        "",
        "## What remains before research claims are justified",
        "",
        "1. Independent label review and an untouched, grouped evaluation set.",
        "2. Full-text verification of inaccessible references and expanded related-work search.",
        "3. Matched policy coverage across established scanner, LLM-only, RAG and verification variants.",
        "4. Evaluation of hallucinations, unsupported inputs, abstentions and recall loss on that independent set.",
        "5. TCI calibration and richer authentication-aware, multi-vantage checks.",
        "6. Later-month Linux telemetry, runtime ML, overhead measurements and full-system experiments.",
        "",
        "## Files to review",
        "",
        "- [Run instructions](../README.md)",
        "- [Slide-by-slide audit](../docs/DECK_AUDIT.md)",
        "- [Month-by-month acceptance ledger](../docs/MONTHS_1_TO_3.md)",
        "- [Experimental protocol](../docs/EXPERIMENT_PROTOCOL.md)",
        "- [Literature audit](../docs/LITERATURE.md)",
        "- [Software test results](test-results.xml)",
        "- [Baseline raw results](baseline-development.json)",
        "- [Live observations](live-testbed.json)",
        "- [LLM output and rejected candidates](rag-smoke.json)",
        "- [Vector retrieval observations](vector-smoke.json)",
        "- [Trivy raw output](trivy-baseline.json)",
        "- [Reproduction identities](environment.json)",
        "",
    ]
    return {"output": "\n".join(lines)}, 0


def main():
    return evidence_main(collect, text_outputs=("output",))


if __name__ == "__main__":
    raise SystemExit(main())
