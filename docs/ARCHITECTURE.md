# Existing architecture

## Stack and execution

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
