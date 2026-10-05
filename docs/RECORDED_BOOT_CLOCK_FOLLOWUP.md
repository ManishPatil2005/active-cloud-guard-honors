# Collector-on boot/TIME evidence follow-up

E2-022, predeclared 5 October 2026. The original E2-019 attempt is incomplete, with rejected TIME inputs lost; E2-021's later sensor-free six-read observation passed but cannot diagnose the earlier failure or verify Falco. This follow-up tests improved instrumentation under the collector, not a replacement run chosen for success.

## Change and fixed protocol

In boot-clock mode only, shared read_time now saves native boot/realtime sandwiches immediately before the first TIME clock sample and after the last TIME clock sample, **before redis_bracket validation**. Both endpoints survive a normal rejected clock bracket. Early command/sampling failures may still lack later fields; preserve safe stage/class and never synthesize missing readings. Default sensor/bridge/nonboot paths do not call native boot clocks. New receipt label container_pid_connect_boot_v2 prevents confusion with earlier instrumentation and is excluded from repeated-readiness acceptance/latency baselines.

One new bounded sensor trial with existing ping_4/fixed two identified canaries/correlation/clock-domains/boot-clock options. Same pinned Falco image, 15-second sensor run/25-second watchdog, permissions/resources, namespace gates, five-second TIME command timeout and unchanged <=500 ms/50 ms/5 ms clock criteria. No adaptive extension, second trial, retry, fitted offset, sampling tolerance relaxation or clock/NTP/WSL/Windows intervention. Abort and preserve partial receipt/raw log on first rejection; cleanup only its unique trial container. Existing Redis identity must remain stable; only existing lab Redis used.

Complete run has 27 native sandwiches: original 3 launch/readiness + 8 PING endpoints (11), plus 16 TIME endpoints. Existing boot_clock_summary remains the original 11-sample PING/launch reduction; the additional 16 are nested in time_read_attempts and checked separately offline. No claim of direct collector calibration-value measurement or exact binary-source attestation. The small extra clock reads change instrumentation; source hashes freeze seven execution files. Do not retrofit old observations or compare this diagnostic as matched latency overhead.

Native namespace checks still require active/children agreement, zero boot/monotonic offsets and shared boot hash across harness/Redis/sensor, unchanged at endpoints when reached. Endpoint readings cannot exclude between-sample transients, other collectors or unreported loss. Preserve unassigned connects and negative experimental findings. Actual collector offset/time-service causality and independent accuracy/stability remain unproven even if this attempt passes.

## Separate execution boundary

Implementation/test/docs commit pushed and remote verified first. Then Linux read-only preflight, known-sensor enumeration and time-service state. Execute **once** into a new destination:

```text
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python scripts/sensor_trial.py --profile ping_4 --fixed-warmup --correlate --clock-domains --boot-clock --output output/engine2-recorded-boot-clock-20261005.json
```

No agent-initiated tests/model/workloads during collection. Always verify cleanup/service/lab state afterward. For success, hash-match raw correlation and metrics, recompute full correlation/server/PING boot summaries and all 27 ordered native bounds; reconstruct TIME response hashes and compare fields. For failure, verify only available data, classify numeric rejection fields when present and explicitly retain missing postflight/correlation/metrics. No full summary fabricated from partial data. Record result separately, whether positive or negative.

Acceptance is an integrity-checked diagnostic outcome, not a causal fix, general clock stability or permission to fit ML. Retain INC-032; INC-033 original missing inputs cannot be repaired. Decide the next scientific experiment from the actual result, without automatically continuing until a favorable observation.

## Implementation validation before execution

428 Windows tests (2.20 s) / Linux (5.62 s): [Windows](../output/engine2-recorded-boot-windows-tests-20261005.xml), [Linux](../output/engine2-recorded-boot-linux-tests-20261005.xml). Five new boot-recording cases plus two added protocol-exclusion variants; existing nonboot/failure/privacy tests pass. Ruff lint/format (76 files), Windows pip check pass. Collector-on v2 not executed at this implementation checkpoint; actual sampler/command failure timing and lifecycle paths not exhaustively injected.

## Observed v2 diagnostic, 5 October

Implementation `82e2a5a092e546454553c707c16c03ea2ea87280` pushed/remote verified before one command at 08:26:18 UTC. Exit 0, sensor removed, no retry or clock changes. [Receipt](../output/engine2-recorded-boot-clock-20261005.json), [offline review](../output/engine2-recorded-boot-review-20261005.json), [collector metrics](../output/engine2-recorded-boot-metrics-20261005.json). Pre/post lab preflight passed, timesyncd active/unchanged, sensor enumeration empty. No tests/other agent workloads during collection; selected identity and three clock-domain facts unchanged.

708 records/14 connects. Two own-PID warmups and four measured PINGs each uniquely observed; eight unassigned connects retained (count compatible with eight TIME reads, ownership not individually proven). All four event/harness and event/server brackets include zero/contain event; all eight server/harness bounds include zero. TIME round trips 52.400758–65.822963 ms, max endpoint disagreement 231 ns. All 27 ordered native samples valid and changes relative to this run's prelaunch include zero; interval union -1380 to +1826 ns. Four event-implied collector offsets intersect prelaunch, **which is not an observed calibration value**. This is one compatible diagnostic, not repeatability or independently evaluated accuracy.

Offline checks reproduced seven source hashes, sole SHA-matched ignored raw log, full PID correlation, server and original 11-sample boot summaries. Reconstructed eight TIME response hashes, compared saved clock fields, checked all 27 native bounds/order and namespace endpoints. Metrics reducer on SHA-matched raw metrics: 16 snapshots, collector event delta 33927, kernel/output-queue drop deltas zero; collector-wide counters do not prove target delivery/full coverage. Metrics/report hashes bind this receipt. No old evidence changed or fitted time correction.

### Exploratory cross-receipt finding, not predeclared confirmation

Comparing prelaunch native offsets against original E2-019 (07:43:31 UTC) yields **+123,103,159,572 to +123,103,161,432 ns**, approximately +123.10316 s. Both samples revalidate; boot_sampler source hash and harness namespace/zero offsets/shared boot hash are equal. The relationship differs at these two endpoints despite stable within-run readings. This comparison was noticed after the new run: it is explicitly exploratory, not a confirmatory predeclared result or matched-protocol performance comparison. It does not locate the change, distinguish wall vs boot behavior, establish host/guest suspension/NTP causality, attest kernel state or prove the earlier ~1 s event-lag mechanism.

Read-only history query for 07:40–08:28 UTC: ordinary-user timesyncd journal visibility limited; sufficient-permission repeat returned no matching unit entries. Windows Kernel-Power IDs 42/107/506/507 query returned NoMatchingEventsFound. Missing logs do **not** prove no adjustment, VM pause/suspend or other synchronization mechanism. No Windows setting, time service, kernel or WSL reset changed. INC-034 preserves the new relationship-change observation; INC-032 and original INC-033 cause remain unresolved. Do not certify long-term stability from today's passing trial.

### Offline check arithmetic and reproducibility

Using Windows here-string Python, strict read_json/hash selection followed by existing correlate, summarize_clocks, boot_clock.summarize, checked_domains, checked and redis_bracket. All successful TIME response hashes use canonical `seconds + '\n' + microseconds`. Ordered 27 samples: three launch/readiness, then each observation's before-TIME pair, PING pair and after-TIME pair. Every next boot_before >= previous boot_after. For sample s relative to prelaunch p, change bounds are `[s.offset_lower - p.offset_upper, s.offset_upper - p.offset_lower]`. Cross-receipt bounds use the same formula with new/old prelaunch samples. No midpoint or symmetry assumed; review JSON binds both original receipt digests. Raw log/metrics must be retained privately to reproduce raw checks; numeric receipts alone are not authenticated execution provenance.

Metrics command actually executed:

```text
.venv/Scripts/python.exe scripts/sensor_metrics_report.py --metrics output/runtime-raw/acg-falco-9cb27baedfab498880874be8e6c3a66c/metrics.jsonl --trial output/engine2-recorded-boot-clock-20261005.json --output output/engine2-recorded-boot-metrics-20261005.json
```

Next is reviewed host/WSL/native-clock lineage diagnosis that can record changes between observations. No automatic extra sensor runs, clock adjustment, correction, baseline fitting or independent detection claim. Stable measurement across a predeclared study and separately labeled evaluation remain required.
