# Active Cloud Guard - Honors Research

Working first-three-month research prototype for Manish Patil's proposal, **An Active AI Security Layer for Misconfiguration & Exposure Prevention in Cloud-Hosted Open-Source Software**.

Read [the deck audit](docs/DECK_AUDIT.md), [experimental protocol](docs/EXPERIMENT_PROTOCOL.md), and [source audit](docs/LITERATURE.md). These explain the scope, corrected score and what the experiments can actually establish.

Start with [the actual results ledger](output/RESEARCH_STATUS.md) for measured outcomes, model failures and remaining research gates.

For detailed project context and maintenance, use the [documentation index](docs/INDEX.md), [work log](docs/WORK_LOG.md), [incident history](docs/INCIDENTS.md) and [task ledger](TASKS.md). The repository is private: [ManishPatil2005/active-cloud-guard-honors](https://github.com/ManishPatil2005/active-cloud-guard-honors).

Enable the included local commit guard after cloning: `git config core.hooksPath .githooks`. It checks documentation and publication exclusions; see the [maintenance contract](docs/DOCUMENTATION_WORKFLOW.md). No GitHub-hosted CI run is implied.

## What is implemented

- Nine explicit baseline predicates across selected Compose, Kubernetes, Terraform, Dockerfile and service configuration constructs.
- A 45-case development corpus with labels and content hashes, generated reproducibly.
- Nine source summaries with official documentation provenance; lexical retrieval and persistent Chroma semantic retrieval using local Ollama embeddings.
- Actual local Ollama auditing with JSON-schema validation and source-ID checks. The model is not allowed to execute tools or choose network destinations.
- Explicit loopback inventory, bounded TCP probes, tri-state evidence and configuration-to-staging linkage.
- Monotonic provisional prioritization; a refused or inconclusive probe never erases a static finding.
- A four-service Docker lab, testing scripts and machine-readable observations.

No runtime anomaly model, eBPF collector, automated isolation or production deployment is included in this M1-3 milestone. They belong to later months in the supplied deck. The existing fixtures are not a held-out benchmark.

## Reproduce on Windows PowerShell

Use Python 3.11+ and Docker Desktop with Linux containers. All commands run from this repository. On this computer the virtual environment is already installed.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe scripts\build_corpus.py
.\.venv\Scripts\python.exe -m pytest -q --junitxml=output/test-results.xml
.\.venv\Scripts\python.exe scripts\evaluate.py
.\.venv\Scripts\python.exe scripts\init_secrets.py
docker compose -f testbed/compose.yaml --profile ai up -d
docker compose -f testbed/compose.yaml exec -T ollama ollama pull qwen2.5:3b
docker compose -f testbed/compose.yaml exec -T ollama ollama pull nomic-embed-text
.\.venv\Scripts\python.exe scripts\live_check.py
.\.venv\Scripts\python.exe scripts\rag_check.py
.\.venv\Scripts\python.exe scripts\vector_check.py
.\.venv\Scripts\python.exe scripts\integrated_check.py
docker pull aquasec/trivy:0.60.0
.\.venv\Scripts\python.exe scripts\trivy_baseline.py
.\.venv\Scripts\python.exe scripts\capture_environment.py
.\.venv\Scripts\python.exe scripts\summarize.py
.\.venv\Scripts\python.exe scripts\repository_check.py
```

For a minimal installation without semantic retrieval use `pip install -e .` plus pytest. Chroma can be installed with `pip install -e '.[vector,test]'`. The captured full lock records the tested Windows/Python environment; other platforms may need a separately resolved lock. Initial image/model downloads consume several GB. CPU inference can take much longer than the deck's target latency.

## CLI examples

```powershell
.\.venv\Scripts\python.exe -m cloudguard.cli scan data/development/postgres-trust.yaml
.\.venv\Scripts\python.exe -m cloudguard.cli retrieve "PostgreSQL trust authentication"
.\.venv\Scripts\python.exe -m cloudguard.cli audit data/development/postgres-trust.yaml --model qwen2.5:3b
.\.venv\Scripts\python.exe -m cloudguard.cli index
.\.venv\Scripts\python.exe -m cloudguard.cli vector-retrieve "Redis protected mode"
.\.venv\Scripts\python.exe -m cloudguard.cli probe --inventory testbed/inventory.json --asset compose/redis
.\.venv\Scripts\python.exe -m cloudguard.cli run data/development/redis-all.yaml --inventory testbed/inventory.json
```

`run` defaults to lexical retrieval; add `--vector-index output/chroma --model qwen2.5:3b` to use semantic retrieval and real model auditing. LLM candidates remain review-required and separate from rule findings; schema validity, source membership and exact input-location checks do not establish factual correctness.

## Lab behavior

Engine 1 v2 (package 0.2.0) supports optional repeated-audit reuse with `--cache-dir output/audit-cache`, generation limits with `--max-tokens 512 --timeout 180`, and index reuse (`index --force` rebuilds). Applicable probes always run fresh. See [v2 design and reproduction](docs/ENGINE1_V2.md). No faster uncached inference, general accuracy improvement or energy saving is implied by cache-hit speed.

Ports: Redis 16379, PostgreSQL 15432, Nginx 18080, MinIO 19000, Ollama 11434; all bind to 127.0.0.1. The dedicated bridge is **not egress-isolated**. Docker's internal-network configuration on this host ignored published mappings, so a standard bridge is used. Do not treat local reachability as public exposure.

PostgreSQL and MinIO credentials are generated under ignored `testbed/secrets/` and never printed. PostgreSQL and MinIO data are disposable tmpfs; container recreation discards that lab data. Redis persistence is disabled. Model downloads are retained in a named Docker volume. Image tags are pinned for this reproduction; their digests are recorded in output/environment.json. These historical lab image versions are not a production-hardening recommendation.

Stop without deleting model data:

```powershell
docker compose -f testbed/compose.yaml --profile ai stop
```

Restart with `up -d`. Only run the declared lab services. Corpus files with intentionally weak settings are static scan inputs, not deployment recipes.

## Evidence and limitations

| Artifact | Meaning |
|---|---|
| output/test-results.xml | Automated software checks |
| output/baseline-development.json | Exact seeded-rule regression and timings; not independent accuracy |
| output/live-testbed.json | Time- and vantage-specific live service observations |
| output/pipeline-demo.json | Static finding, staging TCP evidence and provisional priority |
| output/rag-smoke.json | Three real local-model audits including errors and timing |
| output/vector-smoke.json | Semantic index/retrieval and one real RAG audit |
| output/trivy-baseline.json | Established-tool execution on 11 supported-format fixtures; different policy coverage |
| output/environment.json | Versions, image/model digests and file identities |

Important limits: no general Terraform evaluation, no Helm rendering, no arbitrary service discovery, no auth/exploitability checks, no comprehensive secret detector, no role-binding graph, no calibrated TCI and no independently labeled effectiveness study. Unsupported constructs produce warnings or errors where recognized; the parser is not a completeness validator. Do not interpret an empty finding list as security certification.

The first 1.5B-model runs contained invalid schemas and unsupported findings; those observations are preserved in `output/rag-smoke-initial-failures.json` and `output/rag-smoke-ungrounded-candidates.json`. The default 3B model and input-location constraints were selected using development cases. This is prompt/model tuning, so those cases cannot later be claimed as an untouched test set.

The 3B model also made a false trust-authentication claim on a password placeholder. `grounding.py` adds narrow deterministic corroboration for PostgreSQL trust and Redis protected mode, preserving rejected candidates and an abstention flag. This guard is an engineering control, not independent ground truth or evidence that RAG outperforms the rule baseline. Other policies remain review-required. See `output/rag-smoke-3b-before-policy-guard.json` for the earlier unfiltered observation.

Run the established-tool smoke baseline with `python scripts/trivy_baseline.py` after pulling `aquasec/trivy:0.60.0`. It runs containers with networking disabled and bundled checks. Dockerfile, Kubernetes and Terraform fixtures are scanned independently; the other 34 cases are explicitly excluded. Trivy checks additional policies that the small custom baseline does not label, so its extra findings cannot automatically be counted as false positives.
