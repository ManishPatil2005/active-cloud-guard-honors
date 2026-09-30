# Test and verification plan

30 September alignment increment: 300 tests passed each OS (Windows 2.08 s, Linux 3.45 s), saved as output/engine2-alignment-{windows,linux}-tests-20260930.xml. Two new cases and extended boundary assertions cover signed offsets, exact half-open regions, preservation of export order and failed-normalization refusal. Both unchanged live logs reanalyzed offline; this does not validate cross-clock alignment. Ruff lint/format and Windows pip check pass. See EVENT_ALIGNMENT.md.

Latest audit (29 September, reviewed 30 September): unchanged source passed 298 tests on Windows (2.03 s) and Linux (2.97 s), Ruff lint/format (62 files), Windows pip check and publication checks. Fresh paired batch passed all five jobs; subsequent offline normalization/metrics succeeded. ON-2 interval discrepancy remains unresolved despite passing software tests. See PAIRED_PILOT_RESULTS.md. No new independent accuracy or full overhead validation.

Latest paired tooling: 298 tests passed on each OS; output/engine2-paired-final-{windows,linux}-tests-20260929.xml. Ten new tests cover two-PING warm-up, target preflight and complete-pair summary guards. Real batch passed clock gate but failed OFF-1 before measurement; no sensor-on/control comparison. Preflight passed after Docker/Redis recovery. See PAIRED_PILOT.md; source hashes preserve pre-hardening execution.

Latest clock/control increment: initial 287 and final 288 tests passed each OS; final output/engine2-control-final-{windows,linux}-tests-20260929.xml. Tests include no Docker access on failed diagnostic. Real six-sample clock check rejected one sample; controls were not run. See CLOCK_AND_CONTROLS.md. Do not equate unit-tested controls with live-observed controls.

29 September workload increment: 279 passed on Windows/Linux, output/engine2-workload-{windows,linux}-tests-20260929.xml. Eleven tests cover fixed scheduling, overrun/clock/PONG rejection, profile allowlist and nanosecond half-open selection. Live pilot: one timing-rejected run, one accepted run. See RUNTIME_WORKLOAD_PROTOCOL.md; no retrospective boundary assignment or score for failed run.

Latest instrumentation: 268 tests passed on each OS; output/engine2-instrumented-{windows,linux}-tests-20260928.xml. Eighteen new tests cover selected identity, bounded readiness and metric integrity/minimization. Separate live trial observed readiness, stable identity, 80 events and 16 metrics snapshots; collector-wide zero drops is not a complete-coverage assertion. See ENGINE2_INSTRUMENTATION.md for exact commands and untested lifecycle branches.

Latest adapter increment: 250 tests pass on Windows and Linux, saved separately as output/engine2-adapter-windows-tests-20260928.xml and output/engine2-adapter-linux-tests-20260928.xml. Thirty-four additions cover strict offline normalization and CLI preservation. The prior real log was normalized and accepted by runtime loader/windowing; no new live collector or baseline-score experiment. See ENGINE2_ADAPTER.md for exact commands and limits.

Latest sensor increment (28 September): 216 tests pass on Windows and Linux; separate output/engine2-sensor-{windows,linux}-tests-20260928.xml reports. Twelve additions validate rule IDs, minimized fields, report preservation and selected event scope/results. Live smoke separately observed 40 Redis-cgroup records, PONG and cleanup. See ENGINE2_SENSOR_TRIAL.md for commands/failures. Live normalization, complete loss accounting, accuracy and all Docker lifecycle failures remain untested. Earlier no-sensor statements below are historical snapshots.

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

28 September Linux validation: full suite 204 passed in ACG-Research, with pinned core/test packages in requirements-linux-core-20260928.txt. Use `-o cache_dir=/home/acgresearch/.cache/acg-pytest` to avoid sharing Windows cache permissions. Both initial (two cache warnings) and final clean XML reports retained as output/engine2-linux-tests*-20260928.xml. Ruff lint/format, pip check and synthetic runtime replay passed. This validates software on Linux, not live Chroma/LLM transport, loaded sensor, performance or independent detection accuracy.

Engine 2 preflight: eight additional cases cover non-Linux path skipping, Linux no-certification outcomes, path type/absence, permission failure and real CLI non-overwrite behavior. Full suite: output/engine2-preflight-tests.xml, 204 passed. `python scripts/runtime_preflight.py --output output/engine2-host-new.json` saves facts; zero exit is not readiness. Windows executed live; Linux branches use mocks. No sensor/kernel capability or live capture test has run.

Engine 2 foundation: `python -m pytest -q --junitxml=output/engine2-foundation-tests.xml` records regression results; choose a new filename for subsequent experiments. `python scripts/runtime_check.py --output output/engine2-new-replay.json` checks versioned synthetic data without network/Docker/model access. Expected statuses exercise a constructed count deviation, not threat-detection accuracy. Real sensor capture, ML and CPU overhead have not been tested.

V2.2: `python -m pytest -q --junitxml=output/engine1-v22-tests.xml` captured 168 checks. Use a new filename for future revisions. `python scripts/service_check.py --output output/service-new-observation.json` captures identity and actual credential-free protocol checks against the already-running local lab. A mismatch blocks protocol traffic; all historical reports are retained. Protocol positive/negative alternatives use mocks; only observed live outcomes are claimed in ENGINE1_BASELINE.md.

V2.1: `python -m pytest -q --junitxml=output/verification-v21-tests.xml` records 136 tests (use a new report filename for future revisions). `python scripts/verification_check.py --output output/verification-v21-new-run.json` starts an ephemeral loopback listener, observes allowed/forbidden synthetic policies and rejects stale binding. No Docker/model/real-human-review inference is implied. Unit checks cover approved/unapproved and model-only candidates, request/candidate/model identity changes, scope rejection, duplicate JSON/policies, strict inventory, source changes during audit, fresh probes and no finding suppression.

V2 regression suite: `python -m pytest -q` covers exact reuse, changed model/source/input/policy/budget, expiry, corrupted/schema-invalid records, truncation, rejected-candidate preservation, failed writes, index reuse/repair and repeated probes. `python scripts/benchmark_v2.py --output output/v2-new-run.json` performs real forced/reused indexing and four sequential lexical pipeline runs with one development fixture. Preserve the output on failure; choose a new filename on rerun. Unit mocks do not establish live latency. The script intentionally does not run the old reports/summary generators.

Documentation-only changes need document/link/publication checks; a final software regression run may establish the committed snapshot. Do not repeat expensive live experiments without a relevant change or uncertainty. Log old evidence as historical when it was not rerun. Preserve prior reports before a rerun that changes their experimental meaning.

Before publication: inspect staged files, verify sensitive-path exclusions, compare actual local credential bytes against staged content without printing values, check expected evidence files, and verify the remote commit. The repository checker is a bounded check, not a comprehensive secret scanner or formal security audit.
