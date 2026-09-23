# Test and verification plan

## Software checks

Run from the repository root with the project environment:

```powershell
.\.venv\Scripts\python.exe -m ruff check cloudguard scripts tests
.\.venv\Scripts\python.exe -m ruff format --check cloudguard scripts tests
.\.venv\Scripts\python.exe -m pytest -q --junitxml=output/test-results.xml
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts\repository_check.py
```

Coverage includes the 45 seeded cases, ambiguous/unsafe YAML, unsupported inputs, secret redaction, mult-document/init-container handling, probe scope and failure states, score bounds/monotonicity/missing runtime, metric denominators, retrieval identity, invalid model outputs, invented locations, narrow auth grounding and pipeline evidence boundaries. Current Chroma stale-index unit tests use mocks; actual embeddings/index retrieval are tested separately in the live script.

## Local integration and experiments

| Command (Python script) | Prerequisites | Expected meaning |
|---|---|---|
| scripts/evaluate.py | Generated corpus | Exact rule-set regression; five timing repeats; development only |
| scripts/live_check.py | Four running services | Local TCP availability and HTTP responses; not exploitation |
| scripts/rag_check.py | Ollama + Qwen model | Actual structured candidate/rejection output and latency |
| scripts/vector_check.py | Ollama models + Chroma | Index, expected source retrieval and one actual audit |
| scripts/integrated_check.py | Index + model + services | Full vector-RAG/probe/score path |
| scripts/trivy_baseline.py | Docker + Trivy image | Independent execution per compatible fixture; 34 exclusions |
| scripts/capture_environment.py | Docker images + Ollama | Dependency lock, image/model digests and source identities |
| scripts/summarize.py | Required saved reports | Derived results ledger, not a fresh experiment |

A script's successful return does not prove the model's conclusions correct. Inspect candidate content and rejection/abstention fields. A model can pass JSON/schema checks while being wrong. Do not report a smoke run as a scientific accuracy study.

## Change-specific policy

V2 regression suite: `python -m pytest -q` covers exact reuse, changed model/source/input/policy/budget, expiry, corrupted/schema-invalid records, truncation, rejected-candidate preservation, failed writes, index reuse/repair and repeated probes. `python scripts/benchmark_v2.py --output output/v2-new-run.json` performs real forced/reused indexing and four sequential lexical pipeline runs with one development fixture. Preserve the output on failure; choose a new filename on rerun. Unit mocks do not establish live latency. The script intentionally does not run the old reports/summary generators.

Documentation-only changes need document/link/publication checks; a final software regression run may establish the committed snapshot. Do not repeat expensive live experiments without a relevant change or uncertainty. Log old evidence as historical when it was not rerun. Preserve prior reports before a rerun that changes their experimental meaning.

Before publication: inspect staged files, verify sensitive-path exclusions, compare actual local credential bytes against staged content without printing values, check expected evidence files, and verify the remote commit. The repository checker is a bounded check, not a comprehensive secret scanner or formal security audit.
