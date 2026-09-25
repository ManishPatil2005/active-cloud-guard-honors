# Existing architecture

## Stack and execution

Python 3.11+ library/CLI (measured on Python 3.12.14, Windows 11), PyYAML, python-hcl2, jsonschema, pytest and Ruff. Docker Compose runs Redis, PostgreSQL, Nginx, MinIO and Ollama. Chroma stores locally generated nomic-embed-text vectors. Default smoke auditing uses qwen2.5:3b; the earlier 1.5B failures remain in evidence. No cloud model API is required.

## Flow

```text
Configuration file -> bounded parser / rule baseline -> structured candidates
         |
         +-> lexical OR Chroma retrieval -> local Ollama -> schema/location checks
                                                        -> narrow policy guards
                                                        -> review-required candidates

Explicit staging inventory -> loopback TCP evidence -> network rule findings
                                                   -> provisional priority

All stages -> JSON evidence -> evaluation/status scripts -> reviewed research report
```

Staging services already exist before verification. The program does not deploy arbitrary input manifests. Model candidates remain separate from rule findings. V2.1 permits TCP evidence only for candidates explicitly approved through hash-bound operator review and inventory policy; they receive no automatic score. Unapproved candidates never dispatch probes. Network rule linkage/scoring remains unchanged. See [refinement report](ENGINE1_REFINEMENT.md).

## Module ownership

| Module | Responsibility |
|---|---|
| scanner.py | Selected configuration predicates; input checks; asset/rule IDs |
| retrieval.py | Deterministic lexical comparison baseline |
| vector.py | Chroma index; Ollama embeddings; corpus/model identity |
| llm.py | Local request, structured output and source/location validation |
| cache.py | Opt-in bounded exact-request response reuse; never caches probes |
| grounding.py | Narrow PostgreSQL-trust and Redis-protection corroboration |
| probe.py | Explicit loopback TCP checks and timestamped outcomes |
| verification.py | Strict inventory/policy/review validation; exact-byte/request/candidate binding and conservative assessments |
| deployment.py | Read-only local Docker/Compose identity checks for Redis/PostgreSQL |
| service_probe.py | Identity-gated credential-free Redis PING/PostgreSQL startup observations |
| scoring.py | Bounded monotonic provisional score with missing-data handling |
| pipeline.py | Connect stages; retain origin and review boundaries |
| metrics.py | Confusion counts, explicit undefined ratios and descriptive intervals |
| cli.py | User commands and visible operation failures |

`data/` contains synthetic development inputs and labels; `knowledge/` contains reviewed summaries; `testbed/` contains service definitions/inventory; `scripts/` contains reproduction/evaluation commands; `tests/` contains software regression checks; `output/` contains saved evidence. The generated Chroma database is local, reproducible and excluded from Git.

## Operational boundaries

V2.2 adds a separate `verify-service` workflow against the actual Compose input. Docker identity is collected before/after the protocol observation; no application settings are changed. This does not elevate the legacy inventory-only path to verified deployment equivalence. See [Engine 1 baseline](ENGINE1_BASELINE.md).

Engine 1 v2 adds optional local response reuse, idempotent vector indexing, explicit generation limits and per-stage timing without changing the stack. Cached responses still pass current guards and remain review-required. See [v2 design](ENGINE1_V2.md) for identity, retention and metric semantics. Package 0.2.0 remains pre-production research software.

All published ports bind to 127.0.0.1: 16379, 15432, 18080, 19000 and 11434. The dedicated bridge permits outbound traffic; it is not an egress sandbox. PostgreSQL/MinIO data are disposable tmpfs, Redis persistence is disabled, model downloads persist in a named volume. Local generated secrets are mounted from ignored files.

The custom scanner is incomplete by design. Chroma/source-ID checks do not prove entailment. Grounding guards cover two predicates only. TCI settings are uncalibrated. Runtime telemetry/anomaly detection remains on the later-month roadmap, not a hidden implemented component.
