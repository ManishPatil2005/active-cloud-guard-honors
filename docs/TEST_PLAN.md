# Test and verification plan

E2-023 checks cover native read order/no fallback, interval arithmetic and synthetic wall jump, source/domain/count/gap/order/host-gate corruption, bool/float coercion, duplicate/nonfinite/overlarge JSON, fixed command/timeout, failed-input retention/redaction, stop without retry and exclusive output, offline summary/source binding. Both OS full suites, lint/format/dependency and staged publication checker required before the predeclared observation. CLOCK_LINEAGE.md contains live/offline commands and limitations; passing synthetic tests do not resolve INC-034.

Observed E2-023 software results: 455 Windows/2.20 s and Linux/2.93 s; output/engine2-clock-lineage-{windows,linux}-tests-20261005.xml. Ruff lint and Windows pip check pass; formatter applied to new files, final check required before commit. 27 added cases, lifecycle/scheduling injection not exhaustive. Initial oversized test-ID setup/output issue preserved in INC-035, corrected IDs/passing rerun. Live observation pending; no independent clock authority or research accuracy claim.

E2-022 observed result: one boot_v2 run completed; offline assertions reproduced seven sources, sole SHA-matched raw log/correlation/server/11-sample boot summary, eight TIME response hashes/comparisons, all 27 native bounds/order and unchanged domain/target facts. Metrics reducer: 16 snapshots, zero reported drops/unknown delivery. Cleanup/time service/preflight checked externally. Exploratory old/new prelaunch comparison verified unchanged boot sampler/harness facts and +123.10316 s difference; not a confirmatory protocol gate/cause. No suite during/after collection (last 428 each OS), rejection recording still unit-tested, no new live rejection. INC-034 / RECORDED_BOOT_CLOCK_FOLLOWUP.md.

E2-022 implementation: 428 Windows/2.20 s, Linux/5.62 s; `output/engine2-recorded-boot-{windows,linux}-tests-20261005.xml`. Five new cases verify native TIME endpoints retained on accepted/rejected clock checks, safe first/last boot sampling failures and six sandwiches per TIME/PING/TIME observation; two protocol variants verify boot_v1/v2 exclusion from repeat acceptance. Existing ordinary/bridge/privacy tests pass. Ruff lint/format (76 files), Windows pip check pass. V2 collector-on live attempt pending, failure/lifecycle injection not exhaustive; RECORDED_BOOT_CLOCK_FOLLOWUP.md.

E2-021 live follow-up: one declared run completed six reads/five gaps, no rejection. Offline Windows assertions recomputed all compare/server brackets and six response hashes, checked six source hashes before/after/current, attempt order/count/spacing, identity and absence/no-change flags. External lab preflight passed before/after; timesyncd active/unchanged and sensor enumeration empty. No live collector/independent detection study or additional software suite during collection; last suites 421 each OS. Failure branches are still software-tested only; all-accepted run does not verify historical cause. SENSOR_FREE_TIME_ATTEMPTS.md.

E2-021 implementation: 421 Windows/2.00 s and Linux/2.66 s; `output/engine2-sensor-free-attempts-{windows,linux}-tests-20261005.xml`. Seven additions test six fixed reads/five gaps, shared recorder, first-rejection no retry, preflight refusal, identity/source mismatch, overwrite protection and unchanged legacy mode. Existing E2-020 rejection/privacy tests still pass after extraction. Ruff lint/format (75 files), Windows pip check pass. No live diagnostic at this checkpoint; scheduler stalls/Docker timeout paths not exhaustive. SENSOR_FREE_TIME_ATTEMPTS.md predeclares one separate new attempt, not independent calibration.

E2-020: Windows 414/2.27 s and Linux 414/3.31 s; `output/engine2-time-failure-{windows,linux}-tests-20261005.xml`. Seven new cases retain failure evidence for clock drift, overwide sample, >500 ms round trip, malformed reply, command error and first/last sample errors; existing before-success/after-failure assertions enhanced. Error propagation/gates retained, no private sentinel reply/message exported. Ruff check/format (74 files), Windows pip check pass. No new sensor or workload; lifecycle failures not exhaustively injected and evidence fix not live-validated. Old failed receipt remains byte-identical.

E2-019 live follow-up: single declared attempt aborted at second before-TIME gate. Offline Windows Python assertions verified seven frozen sources, sole SHA-matched raw log, initial three-domain facts, available Redis/PING bounds and five boot samples; one measured connect plus two warmups each unique. No four-PING summary/post facts/metrics or failed bracket samples exist. Sensor absent, timesyncd active, preflight passed afterward. No suite rerun or claim of detection/stability success; last software suite remains 407 each OS. INC-033 / BOOT_CLOCK_DIAGNOSTIC.md.

E2-019 implementation: 407 Windows (2.13 s) / Linux (3.50 s), `output/engine2-boot-clock-implementation-{windows,linux}-tests-20261005.xml`. Twenty-nine additions cover namespace parsing/gates (including active/children ambiguity), native boot bounds, synthetic drift, saved corruption, fixed backend reads and option prerequisites/no fallback. Ruff check/format (74 files), Windows pip check pass. One new live trial predeclared, not run at this checkpoint; resource/lifecycle failures and between-sample transients not exhaustively tested. Software passes do not resolve INC-032 or independently evaluate detection.

E2-018 metadata/source reviewer: 378 Windows (2.11 s) / Linux (2.93 s), `output/engine2-collector-review-{windows,linux}-tests-20261005.xml`. Ten additions cover missing/duplicate/mismatched versions, source allowlist/size/markers, overwrite refusal and failure receipts. Actual capability-free --version/source-hash review completed separately; no sensor loaded. Ruff check/format 72 files, Windows pip check pass. Metadata-container timeout cleanup/HTTP failures not exhaustively tested; source path is not experimental causality or binary-build attestation.

E2-017 clock domains: 368 Windows (2.01 s) / Linux (2.63 s), `output/engine2-clock-domains-{windows,linux}-tests-20261005.xml`, run before one live diagnostic. Seventeen new cases: separate domains, malformed flags/scalars, ordering/backwards server time, PID identity, partial failure, option prerequisites and repeat-study rejection. Existing pairing rejects diagnostic receipts. Live source/raw/summary review separately reproduced incompatible collector bounds despite compatible server/harness reads. Ruff lint/format (70 files), Windows pip check pass; no exhaustive collector lifecycle or independently labeled detection evaluation. See CLOCK_DOMAINS.md.

5 October follow-up: unchanged software passed 351 Windows tests (2.05 s) and 351 Linux tests (3.38 s); fresh `output/engine2-repeat-followup-{windows,linux}-tests-20261005.xml`. Ruff check/format (68 files), Windows pip check pass. Live batch launched three, accepted two, third rejected by cross-clock bounds; sensor cleanup verified before software tests. Offline source/receipt hashes, raw correlation, identity and acceptance reproduced; metrics reductions passed. No new regression cases/source change; software passes do not resolve timing incompatibility. See READINESS_REPEATS.md / INC-032.

Repeat runner: 351 tests each OS; output/engine2-repeat-{windows,linux}-tests-20260930.xml. Eight additions cover acceptance regressions and mocked launch/timeout abort accounting. One live trial accepted before orchestration path failure; remaining two not launched. This is not a completed repeatability evaluation. See READINESS_REPEATS.md.

Identified readiness: 343 tests each OS; output/engine2-readiness-{windows,linux}-tests-20260930.xml. Five new cases reject stale-only/ambiguous/missing IDs and retain first-canary absence. Live readiness plus all six selected command connections observed once; no general completeness or repeated stability established.

Warmup v2: 338 tests each OS, output/engine2-warmup-{windows,linux}-tests-20260930.xml. Six new cases cover missing/ambiguous/all matched warmup, invalid overlaps/booleans and fixed two callback uses. Live first warmup absent, remaining five PIDs matched. Passing measured correlation does not imply all-six capture; see PID_CORRELATION.md.

PID diagnostic: 332 tests each OS; output/engine2-correlation-{windows,linux}-tests-20260930.xml. Fourteen cases added for strict fields/scope/times, match ambiguity, helper PID/PONG, opt-in output and comparison exclusion. One live four-command correlation succeeded; full warmup coverage not established. See PID_CORRELATION.md.

Clock bridge: 318 tests pass each OS; output/engine2-clock-bridge-{windows,linux}-tests-20260930.xml. Ten added checks for TIME parsing and offset/uncertainty rejection. Six live read-only samples succeeded; no Falco sensor calibration. CLI failure branches not exhaustively fault-injected. See CLOCK_BRIDGE.md.

Latest paired-report guards: 308 tests passed each OS; output/engine2-report-guards-{windows,linux}-tests-20260930.xml. Seven added rejection modes: inconsistent clock, duration, schedule, per-call clock, mixed/unknown protocol and missing per-call samples. Historical pilot revalidated offline to engine2-paired-revalidated-20260930.json with unchanged latency contrasts. No sensor-clock calibration claimed.

Latest per-call guard: 301 tests each OS; output/engine2-call-clocks-{windows,linux}-tests-20260930.xml. New regression rejects a transient 100 ms call clock difference even when interval endpoints agree. Existing schedule tests verify per-call timing fields. This is synthetic validation, not live sensor-clock calibration. Beginner guide scan/retrieve/synthetic replay commands also rerun successfully; fresh install and AI commands not rerun.

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
