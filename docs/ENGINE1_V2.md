# Engine 1 v2: bounded repeat-work efficiency

## Maintenance refinement — 7 October 2026

QA-001/V2-002: validate write destination before side effects, exclude replacement key from eviction and evict only after successful publication. Three reproduced failures/regression fixes and whole-suite receipts: [audit](REFINEMENT_AUDIT_20261007.md). Historical engine1-v2.2 baseline/tag and old smoke results unchanged; current maintenance source differs, not a measured new engine version. Sequential capacity can briefly exceed its bound between replacement and eviction; eviction failure may leave excess entries/new response and existing warning. No transaction/concurrency/crash guarantee added.

Date: 2026-09-23. Engine report version 2.0; Python package release 0.2.0 remains a research prototype, not a production-stability claim.

## Scope and acceptance

Preserve Python, Docker Compose, Ollama, Chroma, existing nine rule predicates and human review boundaries. Improve repeated audits and index builds without disguising cached results as new inference or caching live network observations.

| Task | Acceptance |
|---|---|
| V2-001 | Opt-in exact-request cache; input, evidence, model digest, policy or generation-budget changes invalidate reuse |
| V2-002 | Expired, corrupted or schema-invalid cached output is not reused; grounding checks and abstentions remain visible |
| V2-003 | Unchanged corpus/model collection skips embeddings; force rebuild remains available; unexpected IDs removed after successful upsert |
| V2-004 | Token budget and socket timeout exposed; explicit incomplete/truncated generation is an error, not a clean verdict |
| V2-005 | Per-stage timings and inference/cache metadata exposed; every pipeline run makes fresh applicable probes |
| V2-006 | Unit checks, reproducible live smoke, preserved prior evidence and maintained documentation |

## Design and tradeoffs

`cache.py` stores local Ollama response records only when `--cache-dir` is provided. The key hashes the exact serialized request context, actual model digest, corpus identities and guard-policy version. It is not semantic similarity caching: whitespace changes also miss. Cached responses rerun schema, source membership, location and narrow policy guards. A cache entry does not authorize a finding or replace human review. Cache hits require a live local model-identity lookup; this is not an offline fallback. Identity is checked again before storing fresh inference.

Default retention is one hour with at most 128 hash-named records in sequential use, each at most 2 MB (approximately 256 MB maximum payload). Expiration prevents reuse; it is not a timed secure deletion service. Writes use atomic replacement. Multiple processes can race on eviction; this is a single-user prototype cache, not a transactional shared service. Failed writes retain the valid fresh audit with a warning. Inputs/prompts are not stored by this cache, but generated findings can repeat sensitive input. Use a trusted, access-controlled directory; checksum detects accidental corruption, not malicious tampering. `output/audit-cache/` is ignored and publication-blocked. Custom cache paths must also be kept outside Git.

Index reuse verifies collection identity, count and exact document IDs. It trusts the locally generated vector database; IDs alone do not prove vectors have not been tampered with. `index --force` recomputes vectors. Query embeddings still run on vector retrieval; the v2 smoke uses lexical retrieval to isolate generation reuse.

Default generation ceiling is 512 tokens (CLI range 32-4096). `--timeout` defaults to 180 seconds and must be greater than zero and at most 180. This is the HTTP socket timeout, not a total workflow deadline, server cancellation or a memory guarantee. Explicit `done_reason=length` or `done=false` is rejected even when the partial body parses. A smaller budget may require increasing it for a legitimate large finding set; errors are not silently retried at a larger budget.

`elapsed_ms` and pipeline `timings_ms` measure the current call. `total_duration_ns`, `prompt_eval_count` and `generation_tokens` describe original generation; a hit explicitly labels these `inference_metrics_origin=cached_original`. `inference_performed=false` means no chat generation for that call, not zero total work or energy. Fresh scan, retrieval, identity lookup, validation and probes still run.

## Reproduction

From repository root with dependencies, local secrets, models and lab already set up:

```text
python -m cloudguard.cli index
python -m cloudguard.cli index --force
python -m cloudguard.cli run data/development/redis-all.yaml --inventory testbed/inventory.json --model qwen2.5:3b --cache-dir output/audit-cache --max-tokens 512 --timeout 180
python scripts/benchmark_v2.py --output output/v2-new-run.json
```

Run the same `run` command twice for reuse. Omit `--cache-dir` for fresh inference. Use a new benchmark output filename: the script refuses to overwrite an existing observation and records failures/partial results. Benchmarks create a fresh cache subdirectory. Do not run old summary scripts to overwrite v1 evidence.

## Observed smoke result

Saved in [v2 efficiency smoke](../output/v2-efficiency-smoke.json), 2026-09-23, Windows/Python 3.12.14, qwen2.5:3b and nomic-embed-text (full model/corpus digests in report):

| Operation | Wall time | Work performed |
|---|---|---|
| Forced vector index build | 5.804 s | Nine documents embedded |
| Unchanged index reuse | 0.084 s | Zero documents embedded |
| First uncached lexical pipeline | 17.424 s | Fresh chat generation and probe |
| Warm cache-miss pipeline | 5.256 s | Fresh chat generation and probe |
| Cache-hit pipeline 1 | 0.084 s | No chat generation; fresh probe |
| Cache-hit pipeline 2 | 0.072 s | No chat generation; fresh probe |

Both hits retained the same review-required candidate as the cache miss. Redis TCP observations have four distinct timestamps and all report reachable. This says nothing about Redis authentication or public exposure. Model finding asset `services/redis` still requires human reconciliation with inventory `compose/redis`; no automatic LLM-driven probe linkage was added. The cache correctly preserves that review boundary rather than treating a cached candidate as independently verified.

## Interpretation limits

This targets repeated exact inputs, not faster reasoning for unseen configurations. The smoke is one development fixture with sequential, warm-state effects; it is neither a matched v1 comparison nor an accuracy benchmark. The original 3.5-second uncached inference target remains a separate gate. Avoided generation and embeddings are resource-use proxies, not measured energy, carbon, monetary savings or independent vulnerability-detection improvements. No new runtime engine, hosted service, architecture migration or deployment is included.
