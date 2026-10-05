# Evidence index

## Live kernel-state observation (2026-10-05)

[Receipt](../output/engine2-kernel-clock-state-20261005.json), [offline review](../output/engine2-kernel-clock-state-review-20261005.json), [protocol/result](KERNEL_CLOCK_STATE.md): one16-packet/32-query run, six sources/libc continuity/domains/bounds/summary reproduced; SHA834018876154de8a435048b88d063996ecaab029321bb563242ad6fa84ea13cf. Tick/frequency changes directly sampled with RAW/MONO gap~0.46324s and wall/BOOT change~0.867156s. INC-039, TIME_OK not stable-clock/cause/ML acceptance. No intervention/retry/source change since504 suites; old receipt hashes unchanged. Offline arithmetic is local consistency, not independent scientific evaluation.

## Live kernel-state implementation (2026-10-05)

Software: [Windows504](../output/engine2-kernel-state-windows-tests-20261005.xml), [final Linux504](../output/engine2-kernel-state-linux-final-tests-20261005.xml), [earlier Linux504](../output/engine2-kernel-state-linux-tests-20261005.xml). Thirty-six additions; lint/format83files/dependency pass. Initial unused import corrected after first Linux run, original receipt not overwritten. No live state queried by tests.

[Protocol](KERNEL_CLOCK_STATE.md): separate zero-mode ordinary-user query/native-pair observer with complete offline reduction;36 targeted tests pass using injected state/backends only. INC-038 preserves initial two test-double failures. One sensor-free live observation pending after publication; no clock changes, causal/stability/ML evidence.

## Raw-versus-adjusted observation (2026-10-05)

[Receipt](../output/engine2-raw-clock-lineage-20261005.json), [offline review](../output/engine2-raw-clock-lineage-review-20261005.json), [protocol/result/provider context](CLOCK_PROVIDER_REVIEW.md). One sixteen-packet run: RAW-host15/15 compatible, adjusted11/15 discrepant, local RAW/MONO final gap~0.5674s and wall/BOOT change~0.3167s. Four sources/all sample/domain/gap/gate/summary checks reproduced; SHA70fff0419aa8bb6d42e9ab460bf0ae32162bcea3eb78102d85869c46f89dfe0a. INC-037, not attributed cause/absolute accuracy/stability/ML evidence. No changes/intervention/retry or source change since468 suites; old receipts unchanged.

## Clock-provider facts and raw protocol (2026-10-05)

[Minimized manually transcribed facts/commands](../output/engine2-clock-provider-facts-20261005.json), [review and raw protocol](CLOCK_PROVIDER_REVIEW.md). Sequential point-in-time tsc/alternatives, implicit/guest sync states, versions/minimized host hypervisor/services; no simultaneous attribution or authenticated clock accuracy. Frequency is cached in reviewed upstream source, not live timex. Raw trial pending at implementation checkpoint; old negative receipts unchanged.

Software [Windows](../output/engine2-raw-lineage-windows-tests-20261005.xml) / [Linux](../output/engine2-raw-lineage-linux-tests-20261005.xml):468 each, thirteen additions. Synthetic raw difference is not a reproduced runtime cause; no independent evaluation.

## Sensor-free Windows/WSL lineage observation (2026-10-05)

[Receipt](../output/engine2-clock-lineage-20261005.json), [offline review](../output/engine2-clock-lineage-review-20261005.json), [protocol/result](CLOCK_LINEAGE.md). One sixteen-packet run; four sources/all native+host samples/domains/gaps/gates/intervals checked. 13/15 elapsed comparisons and14/16 wall offsets exclude zero; native relative changes sampled zero-compatible. SHA179ebdfa0f8b26a27ba0ed83b2a921b865f4438077567fe3f2e503cb38722710; local consistency, not independent clock accuracy/attestation or explained historical cause. INC-036. No settings/service/sensor/clock action/retry; known-sensor absence/preflight/active time service checked externally; no source change since455-test suites.

## Clock-lineage implementation checks (2026-10-05)

[Protocol](CLOCK_LINEAGE.md), [Windows suite](../output/engine2-clock-lineage-windows-tests-20261005.xml) / [Linux suite](../output/engine2-clock-lineage-linux-tests-20261005.xml): 455 each OS, 27 additions. Native bounds, fixed bridge, interval/strict-data/refusal/privacy/partial-receipt and offline-binding behavior tested. No live observation at implementation checkpoint; synthetic jump is not a reproduced historical incident. Existing failed receipts unchanged.

## Recorded collector-on follow-up (2026-10-05)

[Receipt](../output/engine2-recorded-boot-clock-20261005.json), [offline review](../output/engine2-recorded-boot-review-20261005.json), [metrics](../output/engine2-recorded-boot-metrics-20261005.json), [protocol/result](RECORDED_BOOT_CLOCK_FOLLOWUP.md). Four measured events, eight TIME reads and 27 native samples compatible in one new run; seven source/raw/response hashes/summaries/namespace facts checked. Metrics zero drops, unknown coverage. Exploratory prelaunch relationship difference +123.10316 s against original receipt; no cause/change time or long-term stability established. Failed history intact; no clock adjustments/correction/independent evaluation. Raw data retained locally/ignored; last software suite 428 each OS.

## Recorded boot/TIME implementation checks (2026-10-05)

[Protocol](RECORDED_BOOT_CLOCK_FOLLOWUP.md), [Windows](../output/engine2-recorded-boot-windows-tests-20261005.xml) / [Linux](../output/engine2-recorded-boot-linux-tests-20261005.xml): 428 each. Native TIME endpoint recording/rejected-clock preservation and diagnostic exclusion software-tested; no v2 collector-on observation at this checkpoint. Historical receipts unchanged.

## Sensor-free TIME observation (2026-10-05)

[Receipt](../output/engine2-sensor-free-time-attempts-20261005.json), [offline review](../output/engine2-sensor-free-time-review-20261005.json), [protocol/result/reproduction](SENSOR_FREE_TIME_ATTEMPTS.md). One run six accepted reads/five gaps, all offset bounds include zero; six source/response hashes and available math reproduced offline. No sensors/retries/clock changes, identity unchanged. Later bounded observation cannot identify historical rejected-read cause or verify Falco alignment; no accuracy/overhead/independent evaluation claim. Software unchanged from 421 tests each OS.

## Sensor-free attempt-mode implementation (2026-10-05)

[Protocol](SENSOR_FREE_TIME_ATTEMPTS.md), software [Windows](../output/engine2-sensor-free-attempts-windows-tests-20261005.xml) / [Linux](../output/engine2-sensor-free-attempts-linux-tests-20261005.xml): 421 each. Shared sanitized recorder/fixed-count and refusal behavior tested; one live diagnostic planned but not executed at this checkpoint. Existing negative results remain unchanged.

## TIME failure-recording software checks (2026-10-05)

[Windows](../output/engine2-time-failure-windows-tests-20261005.xml) / [Linux](../output/engine2-time-failure-linux-tests-20261005.xml): 414 each. Seven failure regressions retain sanitized samples/stages/rejection flags without raw replies/error details. This is software verification, not a new live result or retrospective repair of E2-019. INC-033 / [diagnostic recording contract](CLOCK_DOMAINS.md).

## Incomplete boot-clock attempt (2026-10-05)

[Failed receipt](../output/engine2-boot-clock-20261005.json), [offline partial review](../output/engine2-boot-clock-partial-review-20261005.json), [protocol/result](BOOT_CLOCK_DIAGNOSTIC.md). One attempt, second TIME gate rejected; only first measured PING and five boot samples available. Seven source hashes/raw partial PID accounting checked. Missing failed bracket/post facts/metrics/full summaries prevent complete acceptance; compatible initial samples do not resolve INC-032. No retries/corrections. Software unchanged since 407-test implementation.

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
