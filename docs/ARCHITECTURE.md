# Existing architecture

QA-020 preserves embedded Chroma/local Ollama/two-engine flow. Vector query results now pass corpus provenance validation before entering research knowledge: IDs select current corpus documents, stored metadata must agree, distances/envelopes are bounded and typed. Native ranking and trusted store/model/corpus assumptions unchanged; no third engine or dependency migration. [Contract](VECTOR_RESULT_BOUNDARY.md).

QA-015 adds an isolated operator qualifier using existing bounded child/evidence/strictJSON helpers; pinned Chroma1.0.20 PersistentClient with explicit synthetic vectors only. No core CLI/algorithm/default/stack change; test source and ignored fresh store separated from working index. [Compatibility/security limits](VECTOR_PROFILE_QUALIFICATION.md).

QA-014 changes build qualification only: pinned setuptools83.0.0/fresh ignored builders/minimized wheels/local installed targets and opt-in packaging tests. CLI/library/engine algorithms/version0.5.0/Compose/Ollama/Chroma unchanged. Explicit external inputs remain separate from the42module wheel; default source-tree setup retained. [Contract](PACKAGE_QUALIFICATION.md).

QA-013 adds an isolated operator script, not a third engine: fixed bounded profile reads + reused installed metadata inventory + existing exclusive evidence publisher. No network/installer/runtime package imports or core pipeline dependency; all-pin equality is distinct from vulnerability/runtime/vector/research acceptance. [Contract](CORE_PROFILE_VERIFICATION.md).

QA-008 adds stdlib-only legacy_io.InputBudget and process_runner.run_bounded shared by selected legacy scripts; two concurrent bounded pipe readers supervise/reap direct client only. Existing core engines/algorithms/model policy/stack unchanged; evidence publisher caps serialized reports8MB. Trivy/environment preserve partial failures and metadata PDF path portable. New helpers are not imported by clock comparison preflight/core pipeline; no native source-freeze expansion/control action. [Contract](LEGACY_RUNNER_BUDGETS.md).

QA-007 keeps existing adapter modules: llm owns chat envelope validation/owned rejection/shared model-tags validation, vector reuses model identity validation and explicitly checks embedding envelope. Existing valid schema/grounding/score/probe semantics retained; policy4 invalidates old audit keys. No dependency/new module/stack/model algorithm change. [Contract](MODEL_ENVELOPE_VALIDATION.md)/[readiness gates](PRODUCTION_RESEARCH_ROADMAP.md).

QA-005/QA-006 adds shared evidence.py exclusive publication and limits.py selected byte/JSON structure helpers without changing engines/stack. Seven legacy scripts expose explicit destinations; scanner UniqueLoader bounds YAML composition and refuses aliases. Selected verification/retrieval/cache/model/vector paths use bounded reads; file_hash streams64KB. Integration/evaluator/clock preflight selected source lists include limits.py. [Contract/research status](RESEARCH_COMPLETION_STATUS_20261009.md); no global sandbox/native intervention acceptance.

QA-004 keeps existing adapters/endpoints: llm validates exact integer port before URL/cache use and owns LocalOnlyRedirect; vector reuses handler for fixed tags/embedding requests. Proxies remain disabled; cache guard version2/local-only invalidates old-policy audits, no index/history rewrite. Same dependencies/algorithms/CLI; [audit/scope](ENGINE_AUDIT_20261009.md).

QA-003 changes only scripts/evaluate.py calculation/publication separation: required fresh output opens exclusively before reads/scans, existing45fixture/five-repeat metrics returned unchanged, mismatch/error receipts retained with selected pre/post hashes. Scanner/metrics/core pipelines/default engine algorithms untouched; summary.py intentionally reads historical baseline. [Contract/compatibility](EVALUATOR_EVIDENCE_PRESERVATION.md).

E2-046 adds an isolated runtime_paired_accounting library reusing existing runtime_accounting/metrics helpers, plus fixed runner/fixture/tests. It consumes only caller-supplied synthetic accounting documents, not engine outputs or telemetry; no core CLI, model/scanner/intake/algorithm/dependency/stack changes. [Schema/pairing/limits](SYNTHETIC_PAIRED_ACCOUNTING.md).

E2-045 integration.py builds transient comparator→asset→ordered window-index dictionaries once after unchanged component validation; contexts use lookup instead of per-asset re-filtering. No persistent cache, public schema/algorithm/dependency or engine change. Extra local map memory traded for fewer row visits. [Equivalence/work-count evidence](INTEGRATION_WINDOW_INDEX.md).

E2-044: integration.py owns opt-in local timing boundaries around existing component calls and overall replay; CLI/fixed runner forward --measure-stages. Existing reports remain intact; additional execution_cost only when requested, no imported profiler/dependency/service or algorithm change. [Scope/clock semantics](INTEGRATION_EXECUTION_COST.md).

E2-043 adds optional synthetic comparators after saved runtime validation and before optional Engine1 execution: existing runtime_ml/runtime_autoencoder -> intact reports + exact asset/window indices. Source/input/count/window checks, synthetic pre-fit refusal and no score fusion. CLI/runner selection only; same stack/models/dependencies. [Contract](SYNTHETIC_ML_INTEGRATION.md).

E2-042 extends existing integration.py/CLI/fixed runner with explicit Engine1 pipeline mode: scanner/runtime prevalidation -> existing pipeline.run -> complete pipeline report + unchanged saved-runtime report/context. Knowledge/optional policy/reviews join bounded hash checks; selected sources expand5to11 only in this mode. Reviewed model_verification_indices use existing operator mapping; no automatic alias/priority fusion. No pipeline/runtime/model algorithm/dependency/stack migration. New fixture and tests are development-only. [Contract](PIPELINE_RUNTIME_INTEGRATION.md).

E2-041 adds integration.py: existing scan + runtime.analyze -> preserved component reports + exact declared asset references, input/selected-source pre/post checks. Opt-in integrated-replay CLI/fixed integration_check.py, same stack/dependencies/default commands. No RAG/probe/model/collector/score/action stage is executed by the wrapper. Combined priority null, binding/evaluation/calibration false; full fusion remains open. [Contract](INTEGRATED_REPLAY.md).

QA-002 changes only scanner.py environment-list normalization: first-equals split, nonempty string name, duplicate rejection before report emission. Existing mapping path/rule predicates/report format and Engine2 unchanged; CLI/pipeline reuse existing exception handling. [Contract and regression evidence](COMPOSE_ENVIRONMENT_VALIDATION.md).

QA-001/V2-002 cache maintenance: destination validation precedes filesystem mutation, existing target excluded from eviction and atomic publication precedes capacity eviction. No new service/dependency/engine/scoring/model path; historical baseline unchanged. Current source differs by this narrow fix; [audit](REFINEMENT_AUDIT_20261007.md) records evidence and sequential/crash/concurrency limits.

E2-040 diagnostic-only refinement: existing runtime_ml.py owns RuntimeMLBackendError/import-category/metadata pin checks/redacted CLI projection; autoencoder reuses them, both fixed runners attach backend_diagnostic on recognized failure. Success calculations/algorithm/parameters/synthetic-only/default/native23-source/stack/dependency boundaries unchanged. No retry/fallback/install/cache cleanup. [Contract](RUNTIME_ML_BACKEND_DIAGNOSTICS.md), INC-057 distinguishes reproduced reporting gap from unresolved INC-056 actual fault.

E2-039 adds isolated synthetic decision-accounting library/fixed runner/one arithmetic fixture, no core/default/ML/capture/intake/native23-source/stack/dependency change. Caller-authored practice decisions, not model-score conversion; observed3×3label/decision table, availability totals, explicit positive/negative abstention and decided-known/inclusive denominators. Reuse runtime identifier convention/read_json; existing binary metrics remain unchanged and cross-checked on decided-known subset without transferring independent-case intervals. [Contract](SYNTHETIC_RUNTIME_ACCOUNTING.md). No new real evaluation/fitting authority.

E2-037 adds isolated `runtime_autoencoder.py`/fixed `runtime_autoencoder_check.py`, reusing existing optional scikit-learn 1.9.1 with no dependency installation. Per-asset baseline-only scaler plus undercomplete input-to-input MLP (4→2→4), unrounded standardized reconstruction MSE, explicit warning abstention/actual fitting diagnostics. Shared synthetic preparation/baseline/postflight/dependency helpers extracted in runtime_ml.py; unchanged Isolation Forest calculated output checked against historical final receipt. Default runtime/intake/CLI/Engine1/native23-source closure unchanged. No model serialization, real-data authority, third engine, binary threat classifier or stack migration. [Autoencoder contract](SYNTHETIC_RUNTIME_AUTOENCODER.md); earlier milestones below historical.

E2-036 synthetic ML: new isolated cloudguard/runtime_ml.py/synthetic-only compare_synthetic, optional lazy scikit-learn1.9.1 extra, fixed scripts/runtime_ml_check.py and two development captures. Reuse runtime.load_capture/windows/analyze and inventory parsing; initial/statistical/postfit hash consistency. Per-asset ephemeral forest, baseline-only fit, same4features, bounded single-job/temporary thread context, no serialized model/default import/CLI integration or new engine. Optional dependency snapshot separate from historical core/vector lockfiles. Default runtime.py/intake/Engine1/source-freeze23/Compose/Ollama/Chroma unchanged. Actual synthetic fitting/scoring recorded, real-data approval/independence/actions false. INC-052 abstention status/count fix; [contract](SYNTHETIC_RUNTIME_ML.md). Earlier snapshots below historical.

E2-035 observed-unit refinement: runtime_intake.inspect adds keyword-only include_window_index=false (exact boolean), using the existing validated key set after postflight. annotation_index projects coordinator-only keys/hashes/counts/false gates; existing scripts/runtime_intake.py adds opt-in --annotation-index with separate runtime_annotation_index_v1 output. No new module/dependency, window algorithm, label generation, collector/model/default-engine/stack/native/source-freeze23 change. Default v1/typed reports exactly preserved by regression. This is allocation tooling, not approval/context/blinding/eligibility. [Contract](RUNTIME_ANNOTATION_INDEX.md); earlier architecture checkpoints below are historical.

E2-035 annotation preparation: [draft coordinator pack](RUNTIME_LABELING_PROTOCOL.md)/[capture checklist](RUNTIME_CAPTURE_ELIGIBILITY.md) are manual governance, not an execution path or automatic eligibility policy. Existing runtime intake review/adjudication schemas unchanged. Only code change is publication checker exclusion of reserved private/runtime-labeling/ (case-insensitive); .gitignore also excludes it. No engine/model/collector/dependency/Compose/Ollama/Chroma/native/source-freeze23 change, no fitting/action authority. Blank templates intentionally invalid until genuinely completed; no approved human protocol/data.

E2-035 typed refinement: runtime_intake_v2 opt-in selects new runtime_receipts.py through existing offline intake; original v1 reports preserved. Wrapper/source hashes bound under bundle byte/path/postflight guards; existing sensor_adapter KINDS/IMAGE and clock_check.compare reused, no thresholds changed. Selected accounting/capture/trial counts, saved identity snapshots and harness endpoints only; full protocol/coverage/alignment/authenticity/eligibility/fitting false. Identity/timing restricted to single compose/redis binding in selected pinned receipt family. No new dependency/collector/default-engine/comparison source-freeze23 integration. RUNTIME_RECEIPTS.md/INC-049.

Initial E2-035 checkpoint added isolated intake/CLI using runtime/verification, bounded bundle/group/label checks and fresh reports. Typed-source bindings were planned then, implemented above now; not a new engine or default integration. Original v1 schema/report/calculations and historical bytes unchanged. Full eligibility/fitting/action gates false; [intake contract](RUNTIME_INTAKE.md).

## Stack and execution

DOC-004 historical checkpoint changed cloudguard/runtime.py metadata/limitation text only: implemented replay baseline, not full research; calculations/guards/version unchanged. runtime.py already in the23-file comparison list; no native comparison/historical-map rewrite. E2-035 intake was planned then, partly implemented above; CURRENT_STATUS is current summary.

E2-034 durable follow-up adds isolated cloudguard/inert_job_gate.py importing only guest_fence/systemd_job. It reuses inert session initialization/shared lock/deadline/seal, but not old bare-True completion methods; scope-bound supplied-evidence writer/exclusive intent/reply/event/window/fault/recovery records and locked replay. No native bus/CLI/subprocess/service adapter/default-engine/controller/transport/helper/23-source freeze changes.60new tests/four actual inert Linux process cases, all native/quiescence/disarm flags false even simulated done. DURABLE_JOB_GATE.md; native receiver/job-owner/recovery integration still open.

E2-034 adds test-only scripts/systemd_native_fixture.py/tests/test_systemd_native_fixture.py, not a new production adapter/engine. A private unnamed socketpair supplies native message objects; proxy intercepts AddMatch and permits selected readers/close only, callback invoked directly through ctypes. No broker routing/authentication, real Subscribe/service jobs or controller/fence integration.28native cases/3portable checks,791collected; production sources/23-file comparison freeze/stack unchanged. NATIVE_CALLBACK_VALIDATION.md; durable guest binding remains open.

E2-033 bounded follow-up live-observed the existing isolated receiver's connection/match/Subscribe/epoch/Unsubscribe/close and child-reap path once,0selected events; no native callback delivery/fault/job-gate authority. Explicitly authorized Docker Desktop startup restored local engine/integration without configuration changes; no default engine/controller/fence/clock source or stack changes. Actual minimized receipts versus manual environment context remain separate. SYSTEMD_RECEIVER_CAPTURE.md; native event validation/durable guest binding still open.

E2-033 capture follow-up adds separate scripts/systemd_receiver_capture.py ordinary-user Linux parent/child CLI, fixed exclusive observation directory/start/result storage, four-source freeze and minimized receipt validation. Native child18second alarm/parent20second deadline with2+2cleanup; receiver failure errno numeric only. No change to stack/default engines/controller/fence/23-source comparison freeze/clock observer; one read-only native observation separately declared after publication. SYSTEMD_RECEIVER_CAPTURE.md.

E2-033 adds isolated cloudguard/systemd_receiver.py only, not imported by engines/controller/fence. Stdlib ctypes binds selected nonvariadic functions in the pinned installed libsystemd; no package installation/stack change. A persistent fixed-address ordinary-user connection may read broker/manager epoch and request transient notifications, but service-control methods are refused. Five-second/512-step/32-selected-event receive checks never establish submitted-job binding or recovery authority. Native reception/exclusive launcher/durable gate integration remain open; comparison freeze23unchanged. SYSTEMD_RECEIVER.md.

E2-032 adds only isolated systemd_job.py offline event contract/tests, plus read-only schema-review artifact; no bus client/connection/native library/dependency/service binding. Supplied decoded events model returned-path matching under declared boot/bus/manager epoch and receive continuity, never recovery authority. Existing comparison/fence/native-observer sources/23-file freeze unchanged; SYSTEMD_JOB_CONTRACT.md. Native persistent adapter/durable guest integration still open.

E2-031 adds isolated cloudguard/guest_fence.py and its tests only: inert session storage/terminal seal, Linux advisory lock with simulation callbacks and unknown interrupted jobs. No CLI/subprocess/service implementation or import by comparison/engines;23-file live comparison source list unchanged because this prototype is not integrated. Guest-local job identity/privilege/storage/boot/source hardening still needed; GUEST_FENCE_PROTOTYPE.md. No stack migration.

E2-030 adds controller stop-delivery state/operator recovery flag and transport exclusive stop-dispatch/stop-ack nonce metadata; normal helper consults same metadata before cancellation. No new service/command/dependency/default-engine/observer path. Pending/error delivery prevents disarm, active-but-uncertain deadline outcome fails safely in reporting; not guest-side fencing/termination proof. CLOCK_STOP_DELIVERY.md, partial native safety gate remains open.

E2-029 changes only comparison source coverage/order:23files cover static local preflight imports and package initializer, frozen before preflight with detached failure-retained mapping. AST audit parses without executing imports; external/runtime/binary/data attestation not provided. No new command/dependency/default-engine/observer path. CLOCK_COMPARISON_PREFLIGHT.md documents remaining late queued-request safety prerequisite before native use.

E2-028 adds scripts/clock_comparison_transport.py (fixed Windows/WSL operations), clock_restore_watchdog.py (independent one-shot restore/inert helper) and clock_comparison_batch.py (approval-gated exclusive launcher/manifest). Controller selected-source list expands to11; underlying six-file native observer and default engines untouched. No new dependency/service or clock-policy migration; real service use pending approval/protocol/native validation. Stdlib-only helper uses direct base Python and hidden breakaway flags/PID handshake; inert integration not service-restoration proof. CLOCK_COMPARISON_TRANSPORT.md.

E2-027 adds cloudguard/clock_comparison.py as a pure injected operations state machine and scripts/clock_comparison_review.py as an offline-only three-receipt reducer using the unchanged native full reviewer. No concrete WSL service transport/watchdog/launcher or new dependencies. Tests simulate service operations; no default-engine or observer source changes. Future live adapter requires explicit approval and tested independent restoration/process deadlines; CLOCK_COMPARISON_CONTROLLER.md.

E2-025 adds separate cloudguard/kernel_clock_state.py (reviewed native Linux ABI/query/state/interval validation) and scripts/kernel_clock_diagnostic.py (fixed paired observation/offline review), reusing unchanged guest sampling. No new services/dependencies/default-engine path; Windows reviews but cannot collect native state. Zero-mode ordinary-user libc calls/file-source continuity are diagnostic, not correction or attestation. KERNEL_CLOCK_STATE.md.

E2-024 adds opt-in --raw-clock to existing lineage tool, native RAW enclosing the old sequence, strict raw-only field validation, separate protocol and extra host/raw/raw-minus-mono interval reductions. Same command/source/domain/privacy/fixed limits; ordinary engine/sensor/legacy sampling unchanged. Historical hashes remain revision-bound. Sequential provider facts are a manually transcribed evidence artifact, not an authenticated live timex snapshot. CLOCK_PROVIDER_REVIEW.md; no new dependencies or synchronization changes.

E2-023 adds separate scripts/clock_lineage.py Windows-host orchestration and cloudguard/clock_lineage.py native/interval validation. Fixed WSL child reads clock/proc/source facts only; no Docker/sensor/service/model calls. Count/gap/timeout/strict source and namespace gates, sanitized partial receipts and offline full reduction; not runtime baseline input. Single-domain validation extracted from boot_clock's existing three-domain checks without changing those gates. Execution hashes are revision-specific; old receipt sources remain historical. CLOCK_LINEAGE.md; architecture/engines unchanged.

E2-022 read_time optional boot flag surrounds each TIME command bracket with two validated native boot/realtime sandwiches, saved before existing acceptance validation. Only clocked_ping boot mode requests them; sensor-free/legacy/default paths unchanged. Boot_v2 receipt distinguishes 16 added nested TIME endpoints from original 11 launch/PING summary; complete ordered reduction reviewed offline. No collector calibration read/correction/new dependency; RECORDED_BOOT_CLOCK_FOLLOWUP.md.

E2-021 extracts sanitized TIME recording into scripts/sensor_trial.read_time, shared by existing clocked_ping and opt-in clock_bridge --record-attempts. New sensor-free protocol has six reads maximum/five one-second gaps, source freeze/identity/known-sensor absence gates, stops on rejection. No PING, boot sample, collector startup, model or runtime baseline path. Legacy bridge mode unchanged; SENSOR_FREE_TIME_ATTEMPTS.md. Source hashes change through the refactor, historical receipts remain bound to old code.

E2-020 extends only clocked_ping diagnostic observations with ordered time_read_attempts: phase/status, available clock endpoints/comparison, clock rejection flags, response SHA256 and failure stage/class. Evidence appended before validation; exceptions still propagate and redis_bracket remains authoritative. Accepted before/after schemas unchanged; bookkeeping perturbs instrumentation slightly and source hashes distinguish future runs. No new service/model, correction or gate relaxation; historical receipts not enriched retroactively.

sensor_trial --boot-clock requires the separate clock-domain diagnostic. cloudguard/boot_clock.py brackets native CLOCK_REALTIME with CLOCK_BOOTTIME, recomputes saved bounds and reports offset-change/event-implied ranges, never correction or scoring. Fixed proc reads gate active/children namespaces, zero offsets and shared boot-ID hash; facts must remain unchanged. Eleven sandwiches, seven frozen source hashes and distinct container_pid_connect_boot_v1 label; default engines unchanged. Extra proc execs perturb workload, so no latency/baseline reuse. Existing sensor duration/permissions retained; BOOT_CLOCK_DIAGNOSTIC.md.

scripts/collector_source_check.py is a separate metadata/source reviewer: existing pinned image --version with no capabilities/network/mounts and read-only filesystem, followed by bounded HTTPS reads of six official immutable release files. Records hashes/versions/marker lines, never runs downloaded source or loads a sensor. No engine or clock-correction path; matching releases are not build attestation. See COLLECTOR_TIMESTAMP_REVIEW.md.

Opt-in sensor_trial --clock-domains adds eight fixed Redis TIME reads around four precisely bracketed identified PINGs. cloudguard/clock_domains.py shares Redis bracket arithmetic with clock_bridge and produces separate server/harness and collector/server diagnostic bounds, without correction/score. Distinct container_pid_connect_clock_v1 receipts cannot enter repeat acceptance/latency pairing; ordinary sensor path unchanged. Extra TIME events/unassigned counts retained. Source hashes freeze this diagnostic; no new permissions or permanent collector. See CLOCK_DOMAINS.md.

scripts/repeat_readiness.py orchestrates exactly three frozen diagnostic slots, hashes selected execution sources, validates saved measurement fields and aborts on failure without replacements. Absolute destination is resolved before collection. Child launch accounting distinguishes no-start from timeout; final sensor enumeration remains an operator requirement after interruption. No change to collector protocol or ML path.

Diagnostic readiness protocol identified_second_canary_v1 shares connection_counts parsing with final correlation. It records two bounded attempt snapshots and gates measured dispatch on the second canary's unique connect. Default noncorrelated readiness remains unchanged; existing latency-pilot exclusions still apply.

Correlation v2 adds optional identified warmup callbacks and separate two-warmup/four-measured PID accounting. Default noncorrelated mode remains unchanged. Diagnostic output includes warmup statuses, unassigned connects and all-six flag; coverage stays unknown regardless of counts.

cloudguard/correlation.py validates opt-in diagnostic PID/connect associations and per-call clock bounds. sensor_trial --correlate requires fixed warmup/ping_4 and adds proc.vpid only in that mode. It is separate diagnostic evidence, not runtime baseline input; paired_report excludes its receipts. Default capture schema remains unchanged.

scripts/clock_bridge.py is a separate bounded Redis TIME diagnostic: six local-identity-gated reads and delay-aware server/harness offset intervals. It does not collect sensor events, synchronize clocks, fit baselines or change the existing stack.

Paired-report reduction recomputes saved clock comparisons and checks schedule/boundary/call-bracket consistency before comparing runs. All four runs must share a recognized timing protocol; legacy receipts stay explicitly legacy. This is local consistency validation, not authenticated experiment provenance.

Measured workload receipts now label timing_protocol=per_call_brackets_v1 and include per-PING before/after clock samples and rejection on call clock disagreement. This is harness instrumentation, not collector synchronization or event correlation; old receipts are preserved without fabricated fields.

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
| runtime.py | Engine 2 normalized replay, explicit asset bindings, windows and count-deviation baseline; no sensor or actions |
| runtime_preflight.py | Read-only host and Linux marker facts; no compatibility certification, sensor or subprocess |
| scripts/sensor_trial.py | Separate bounded Falco/Redis smoke harness; local raw logs and minimized summary, not connected to runtime.py |
| sensor_adapter.py / scripts/normalize_sensor.py | Offline saved-trial hash/schema validation and minimized runtime capture; parser accounting, no measured sensor loss |
| sensor_metrics.py / scripts/sensor_metrics_report.py | Hash-bound minimized collector-wide metric snapshots; separate from target-specific event accounting |
| workload.py / scripts/workload_report.py | Fixed measured PING schedules with timing rejection, exact interval/region counts and offline connect-offset diagnostics; no causal mapping, clock correction, model fitting or overhead estimate |
| clock_check.py / scripts/clock_diagnostic.py | Bracketed wall/monotonic sampling and six fixed diagnostic intervals; never changes clocks |
| scripts/workload_control.py | Gated sensor-off fixed workload controls, not sensor exports or overhead estimates |
| scripts/paired_pilot.py / scripts/paired_report.py | Preflight, declared four-run orchestration and complete-pair descriptive latency reports; fresh completed pilot reviewed in PAIRED_PILOT_RESULTS.md, not general overhead |
| scoring.py | Bounded monotonic provisional score with missing-data handling |
| pipeline.py | Connect stages; retain origin and review boundaries |
| metrics.py | Confusion counts, explicit undefined ratios and descriptive intervals |
| cli.py | User commands and visible operation failures |

`data/` contains synthetic development inputs and labels; `knowledge/` contains reviewed summaries; `testbed/` contains service definitions/inventory; `scripts/` contains reproduction/evaluation commands; `tests/` contains software regression checks; `output/` contains saved evidence. The generated Chroma database is local, reproducible and excluded from Git.

## Operational boundaries

V2.2 adds a separate `verify-service` workflow against the actual Compose input. Docker identity is collected before/after the protocol observation; no application settings are changed. This does not elevate the legacy inventory-only path to verified deployment equivalence. See [Engine 1 baseline](ENGINE1_BASELINE.md).

Engine 1 v2 adds optional local response reuse, idempotent vector indexing, explicit generation limits and per-stage timing without changing the stack. Cached responses still pass current guards and remain review-required. See [v2 design](ENGINE1_V2.md) for identity, retention and metric semantics. Package 0.2.0 remains pre-production research software.

All published ports bind to 127.0.0.1: 16379, 15432, 18080, 19000 and 11434. The dedicated bridge permits outbound traffic; it is not an egress sandbox. PostgreSQL/MinIO data are disposable tmpfs, Redis persistence is disabled, model downloads persist in a named volume. Local generated secrets are mounted from ignored files.

The custom scanner is incomplete by design. Chroma/source-ID checks do not prove entailment. Grounding guards cover two predicates only. TCI settings are uncalibrated. Engine 2 now has an observation-only replay foundation; live telemetry, ML models and integrated threat evaluation remain later work.

Engine 2 flow: saved bounded Falco trial -> offline adapter -> declared normalized capture -> schema/asset/time checks -> nonempty per-asset time windows -> comparison with separate baseline captures -> reviewable deviations. Only the synthetic example has a fitted comparator; the real 40-event sample has normalization/windowing evidence, not a separate real baseline. It neither imports executable models nor feeds provisional runtime scores into TCI. See [foundation report](ENGINE2_FOUNDATION.md) and [adapter](ENGINE2_ADAPTER.md).
