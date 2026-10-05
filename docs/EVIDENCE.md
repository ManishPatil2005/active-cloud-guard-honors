# Evidence index

## Boot-clock implementation (2026-10-05)

[Protocol](BOOT_CLOCK_DIAGNOSTIC.md), software [Windows](../output/engine2-boot-clock-implementation-windows-tests-20261005.xml) / [Linux](../output/engine2-boot-clock-implementation-linux-tests-20261005.xml): 407 each. Native clock/namespace validation is software-tested; a live boot-clock trial has not run at this checkpoint. No corrected timestamp, causal or independent evaluation claim.

## Pinned collector source review (2026-10-05)

[Review](COLLECTOR_TIMESTAMP_REVIEW.md), [metadata/source receipt](../output/engine2-collector-source-review-20261005.json), software [Windows](../output/engine2-collector-review-windows-tests-20261005.xml) / [Linux](../output/engine2-collector-review-linux-tests-20261005.xml): 378 each. Local Falco/libs versions, immutable upstream URLs, hashes and line markers; no copied/executed upstream source. Initialization-offset mechanism reviewed, not proven experimental cause or binary-source attestation. No new sensor/clock intervention.

## Same-trial clock domains (2026-10-05)

[Protocol/results](CLOCK_DOMAINS.md), [receipt](../output/engine2-clock-domains-20261005.json), [metrics](../output/engine2-clock-domains-metrics-20261005.json), software [Windows](../output/engine2-clock-domains-windows-tests-20261005.xml) / [Linux](../output/engine2-clock-domains-linux-tests-20261005.xml): 368 each. Eight server/harness brackets include zero; all four collector events outside nested PING and server brackets. Offline source/raw/correlation/summary checks passed; sensor removed. Negative alignment result, not a corrected baseline, overhead study or proven cause. Raw logs remain private/local; INC-032.

## Separate repeatability follow-up (2026-10-05)

[Protocol and review](READINESS_REPEATS.md), [manifest](../output/engine2-readiness-repeats-20261005/manifest.json), trial [1](../output/engine2-readiness-repeats-20261005/trial-1.json) / [2](../output/engine2-readiness-repeats-20261005/trial-2.json) / [3](../output/engine2-readiness-repeats-20261005/trial-3.json), metrics [1](../output/engine2-readiness-repeats-20261005/trial-1-metrics.json) / [2](../output/engine2-readiness-repeats-20261005/trial-2-metrics.json) / [3](../output/engine2-readiness-repeats-20261005/trial-3-metrics.json). Three launched, two accepted, third timing-rejected despite unique PID matches. Frozen source/receipt/raw-correlation and cross-trial identity checked offline. No repeated-stability, full coverage, ML accuracy or general overhead claim. Fresh [Windows](../output/engine2-repeat-followup-windows-tests-20261005.xml) / [Linux](../output/engine2-repeat-followup-linux-tests-20261005.xml) software reports: 351 each. Raw logs stay local/ignored; INC-032.

## Aborted paired pilot (2026-09-29)

[Manifest](../output/engine2-paired-pilot-20260929/manifest.json), [clock](../output/engine2-paired-pilot-20260929/clock.json), [OFF-1 failure](../output/engine2-paired-pilot-20260929/off-1.json): later jobs not executed; no empirical paired result. [Report](PAIRED_PILOT.md) records restored guest NTP and Docker/Redis recovery. [Windows](../output/engine2-paired-final-windows-tests-20260929.xml) / [Linux](../output/engine2-paired-final-linux-tests-20260929.xml): 298 tests each.

## Clock/control gate (2026-09-29 local)

[Diagnostic](../output/engine2-clock-diagnostic-20260929.json): one of six sensor-free intervals rejected. [Report](CLOCK_AND_CONTROLS.md) includes time-service observations, exact commands and deferred controls. Final [Windows](../output/engine2-control-final-windows-tests-20260929.xml) and [Linux](../output/engine2-control-final-linux-tests-20260929.xml) suites: 288 each. No live control or overhead result.

## Measured workloads (2026-09-29 local)

[Protocol/results](RUNTIME_WORKLOAD_PROTOCOL.md), [rejected ping_1](../output/engine2-ping1-measured-20260929.json), [accepted ping_4](../output/engine2-ping4-measured-20260929.json), [interval](../output/engine2-ping4-interval-20260929.json), [metrics](../output/engine2-ping4-metrics-20260929.json). One accepted/one rejected pilot is not a valid paired benchmark. [Windows](../output/engine2-workload-windows-tests-20260929.xml) and [Linux](../output/engine2-workload-linux-tests-20260929.xml): 279 tests each.

## Instrumented trial (2026-09-28)

[Trial](../output/engine2-instrumented-trial-20260928.json), [metrics](../output/engine2-metrics-20260928.json), [normalized accounting](../output/engine2-instrumented-normalized-20260928/accounting.json): observed readiness, stable selected identity, 80 records, 16 collector-wide snapshots and cleanup. [Windows](../output/engine2-instrumented-windows-tests-20260928.xml) / [Linux](../output/engine2-instrumented-linux-tests-20260928.xml): 268 tests each. Interpretation and exact commands: [instrumentation report](ENGINE2_INSTRUMENTATION.md). Not independent evaluation or full-coverage evidence.

## Offline adapter (2026-09-28)

[Adapter report](ENGINE2_ADAPTER.md), [minimized capture](../output/engine2-normalized-20260928/capture.json) and [accounting](../output/engine2-normalized-20260928/accounting.json): prior live log processed offline, 40 validated records, zero rejected, unknown sensor loss. [Windows tests](../output/engine2-adapter-windows-tests-20260928.xml) and [Linux tests](../output/engine2-adapter-linux-tests-20260928.xml): 250 passed each. No independent baseline or detection result.

## Bounded sensor smoke (2026-09-28)

[Trial record](ENGINE2_SENSOR_TRIAL.md) explains all preserved attempts and limits. [Verified summary](../output/engine2-sensor-trial-verified-20260928.json): 40 selected syscall records, PONG, exit 0, sensor removed; no threat/completeness claim. Raw logs local only, digest published. [Windows](../output/engine2-sensor-windows-tests-20260928.xml) and [Linux](../output/engine2-sensor-linux-tests-20260928.xml): 216 tests passed each. Earlier sensor-absent snapshots remain historical.

## Linux regression and Docker integration (2026-09-28)

- [First Linux suite](../output/engine2-linux-tests-20260928.xml): 204 passed; two cache warnings in command output, recorded in INC-023.
- [Clean Linux rerun](../output/engine2-linux-tests-final-20260928.xml): 204 passed after Linux-local cache selection.
- [Linux synthetic replay](../output/engine2-linux-replay-20260928.json): all four software smoke checks passed, no live telemetry.
- [Core/test dependency snapshot](../requirements-linux-core-20260928.txt) and WL-011 record reproduction and actual Windows/WSL Redis ID match. No claim of sensor visibility.

## Linux provisioning (2026-09-25)

[WSL Linux preflight](../output/engine2-linux-wsl-preflight.json): actual ACG-Research execution, UID 1000, Linux 6.6.114.1, three markers present. Not a loaded-probe test, full Linux regression suite or real telemetry capture. [Setup record](WINDOWS_LINUX_SETUP.md) and WL-010 document commands and unresolved Docker integration.

## Engine 2 host preflight (2026-09-25)

- [Windows host facts](../output/engine2-windows-preflight.json): actual local OS observation, linux_host_required. Not a Linux/sensor test.
- [Preflight regression suite](../output/engine2-preflight-tests.xml): 204 software tests passed; Linux branches mocked. No accuracy, collection or overhead claim.

These files are observations, not marketing claims. Timestamps in JSON are UTC; work occurred on 2026-09-23 in Asia/Calcutta. Original reports can contain local file paths. Repository visibility is private.

| ID | Artifact | What it establishes / limit |
|---|---|---|
| EV-001 | source/Honors_Research_1st_Monitoring_Deck.pdf | Original proposal, not proof of implementation |
| EV-002 | ../data/labels.json and development/ fixtures | Seeded development expectations and hashes; not independent ground truth |
| EV-003 | ../output/test-results.xml | Saved software-test outcomes; latest snapshot may be refreshed after relevant code checks |
| EV-004 | ../output/baseline-development.json | 45 exact-rule comparisons and repeated scanner timing; no generalization claim |
| EV-005 | ../output/live-testbed.json | Four local TCP observations and two HTTP checks at recorded time |
| EV-006 | ../output/pipeline-demo.json | Rule candidate linked to explicit staging endpoint and provisional score |
| EV-007 | ../output/rag-smoke-initial-failures.json | Initial 1.5B schema failure summaries; earliest malformed response bodies were not saved |
| EV-008 | ../output/rag-smoke-ungrounded-candidates.json | Unsupported 1.5B model candidates despite schema-valid output |
| EV-009 | ../output/rag-smoke-3b-before-policy-guard.json | 3B unsupported trust-authentication claim before narrow guard |
| EV-010 | ../output/rag-smoke.json | Final three-case candidates, rejections and timing; tuned development data |
| EV-011 | ../output/vector-smoke.json | Actual vector index, source checks and one model audit |
| EV-012 | ../output/trivy-baseline.json | Per-fixture established-tool observations and exclusions; policy scope differs |
| EV-013 | ../output/integrated-demo.json | Full vector-RAG, explicit probe and priority path executed |
| EV-014 | ../output/environment.json | Historical dependency/image/model identities and hashes for files then present |
| EV-015 | ../output/RESEARCH_STATUS.md | Generated interpretation of the saved reports, not an additional experiment |
| EV-016 | ../output/test-results-initial-84.xml | Preserved original 84-test snapshot before three repository-check tests were added |

The historical environment snapshot is not a manifest of documentation added later. Git identifies the complete committed snapshot. Do not regenerate historical experiment output merely to refresh documentation dates.

## Evidence preservation

Engine 2 initial evidence: [synthetic replay](../output/engine2-replay-smoke.json) and [software suite](../output/engine2-foundation-tests.xml). Source fixtures live under data/runtime/ and are explicitly invented, including timestamps/container ID. They are not eBPF/Kubernetes recordings or independent labels. ENGINE2_FOUNDATION.md documents interpretation.

V2.2: [initial local service observation](../output/service-identity-v22.json), [final identity/protocol observation](../output/service-identity-v22-final.json), [168-test report](../output/engine1-v22-tests.xml). Both real lab services matched selected identity checks; Redis denied via protected mode, PostgreSQL challenged via SASL. No passwords/data/SQL were sent. Interpretation: ENGINE1_BASELINE.md.

V2.1 additions: [136-test report](../output/verification-v21-tests.xml) and [real loopback/synthetic-policy smoke](../output/verification-v21-smoke.json). [Refinement report](ENGINE1_REFINEMENT.md) defines their scope. Model-review integration is mock-tested, not independently reviewed or live-model evaluated. No historical result is replaced.

V2 additions: [efficiency smoke](../output/v2-efficiency-smoke.json) records actual model/index/probe observations, full model/corpus identity and timings. [V2 test report](../output/v2-test-results.xml) records software regression results. Historical v1 artifacts above remain unchanged. ENGINE1_V2.md describes conditions and limitations.

For a changed experiment, preserve the earlier report under a descriptive revision name or rely on an already committed version, then record the new run's date, command, inputs, software/model identities and changed conditions. Keep failures, exclusions and abstentions. Never claim a mock-based unit test is a live inference run. Derived summaries must identify their source reports.
