# Research milestone: actual implementation and test evidence

Historical first-three-month evidence summary for Manish Patil. Generated 2026-10-09T13:32:33.368506+00:00; input files retain their original timestamps. This is not the current full-project status or a completed effectiveness study.

## Verified engineering outcomes

| Check | Observed result |
|---|---|
| Automated software tests | 87 tests; 0 failures/errors |
| Seeded development corpus | 45 cases; 0 rule-set mismatches |
| Rule scan timing | Median 0.320 ms; p95 0.573 ms; five repeats/case |
| Live services | 4/4 TCP accepts from localhost |
| HTTP checks | 2/2 HTTP 200 responses |
| Chroma index | 9 source summaries; local embeddings |
| Semantic source checks | 3/3 expected sources in top three |
| Trivy baseline execution | 11 independently scanned fixtures; 34 excluded for coverage |

## Real LLM observations

Model: `qwen2.5:3b`. These cases were used for development and prompt/model selection.

| Case | Retained candidates | Rejected candidates | Latency | Error |
|---|---:|---:|---:|---|
| postgres-trust.yaml | 1 | 0 | 12.44 s | none |
| redis-unprotected.yaml | 1 | 0 | 12.30 s | none |
| postgres-reference.yaml | 0 | 1 | 12.83 s | none |

The first 1.5B model produced schema errors and hallucinated fields. The 3B model also produced an unsupported PostgreSQL-trust claim for a password placeholder. Original observations are preserved. Exact input-location checks and narrow deterministic PostgreSQL/Redis evidence guards now reject unsupported candidates. Other policy types still require human entailment review. A rejected candidate is an abstention, not proof that the configuration is clean.

Model latency exceeds the proposed 3.5-second target on these runs. That target is not achieved. The scanner-only timing above excludes retrieval and LLM inference. No 90% false-positive reduction, held-out F1 .92, runtime AUC .95 or CPU-overhead target is claimed.

## Architecture and research corrections

The implementation separates configuration predicates, live network observations and policy decisions. The provisional score never lowers risk merely because an endpoint is reachable. A refused/inconclusive TCP probe never erases a secret or authorization finding. LLM candidates require review and do not directly authorize deployment or probing.

The original sequence needs an isolated staging deployment before live verification; it cannot probe a service that does not yet exist. A dedicated Docker bridge with loopback publishing is used here; egress is not isolated. Historical image tags and model digests are recorded for reproduction, not recommended for production.

## What remains before research claims are justified

1. Independent label review and an untouched, grouped evaluation set.
2. Full-text verification of inaccessible references and expanded related-work search.
3. Matched policy coverage across established scanner, LLM-only, RAG and verification variants.
4. Evaluation of hallucinations, unsupported inputs, abstentions and recall loss on that independent set.
5. TCI calibration and richer authentication-aware, multi-vantage checks.
6. Later-month Linux telemetry, runtime ML, overhead measurements and full-system experiments.

## Files to review

- [Run instructions](../README.md)
- [Slide-by-slide audit](../docs/DECK_AUDIT.md)
- [Month-by-month acceptance ledger](../docs/MONTHS_1_TO_3.md)
- [Experimental protocol](../docs/EXPERIMENT_PROTOCOL.md)
- [Literature audit](../docs/LITERATURE.md)
- [Software test results](test-results.xml)
- [Baseline raw results](baseline-development.json)
- [Live observations](live-testbed.json)
- [LLM output and rejected candidates](rag-smoke.json)
- [Vector retrieval observations](vector-smoke.json)
- [Trivy raw output](trivy-baseline.json)
- [Reproduction identities](environment.json)
