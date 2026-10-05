# Windows/WSL clock-lineage diagnostic (E2-023)

## Purpose and acceptance

INC-034 records an exploratory +123.10316-second difference between two realtime-minus-native-boot relationships under equal saved harness namespace/kernel facts. It does not identify a cause. This separate, read-only diagnostic observes Windows wall/performance-counter and WSL native REALTIME/MONOTONIC/BOOTTIME together. It is not Engine 3, a timestamp correction, runtime baseline, or ML evaluation.

Acceptance: strict native/domain/source validation; interval arithmetic with no shared-epoch or symmetric-delay assumption; fixed maximum count/gaps/timeout; stop on first failure with sanitized available inputs; never overwrite evidence; tested on both OSes; commit protocol before one observation and commit its result separately. No clock setting, NTP service, host power policy, sensor, Redis, model or vector-index changes.

## Frozen single-observation protocol

After implementation commit/push/remote verification, check lab access, known trial sensors absent and timesyncd active. Run exactly one Windows-host observation to a new path:

```powershell
.venv\Scripts\python.exe scripts/clock_lineage.py --output output/engine2-clock-lineage-20261005.json
```

Sixteen snapshots maximum, fifteen fixed one-second sleeps following successful packets, no replacement/retry. Each fixed WSL command has a five-second subprocess timeout. Scheduling/launch overhead can extend elapsed time; this is a count/timeout protocol, not an absolute 16-second wall deadline. Refuse host packet round trip above two seconds, clock-check disagreement plus uncertainty above 50 ms, or host/native sampling span above 5 ms. These are diagnostic-only gates, not changes to the existing 500-ms Redis bridge or collector protocol.

Fixed child: `wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python scripts/clock_lineage.py --guest-snapshot`. Child performs only native clock reads, four allowlisted proc reads (namespace symlinks, offsets, hashed boot identity) and hashes four source files. No shell interpolation, external network, Docker or privileged service actions. Active/children namespace equality, zero offsets and stable domain facts required. `boot_clock.checked_domain` is extracted from the existing three-domain validator without changing its count/shared-boot/offset gates; old receipts remain bound to historical source hashes.

Guest clock order: MONOTONIC / BOOTTIME / REALTIME / BOOTTIME / MONOTONIC, all native integer nanoseconds; no fallback. Host wall reads use `time.time_ns`, bracketed by explicit `time.perf_counter_ns`. Record actual host `get_clock_info` facts. Host counter epoch is never equated with either Linux epoch.

## Reduction and interpretation

For guest sample `(before, wall, after)`, wall-minus-clock range is `[wall-after, wall-before]`. Relative change against initial range is `[later_low-initial_high, later_high-initial_low]`. All readings and derived fields are retained/recomputed.

Host counter endpoints conservatively use midpoint +/- ceil(sample span / 2). The guest instant lies between host dispatch/receive brackets. Host elapsed range across packets is `[later_dispatch_low-initial_receive_high, later_receive_high-initial_dispatch_low]`. Subtract guest elapsed interval using lower-minus-upper / upper-minus-lower. Never use half round-trip as assumed one-way delay.

Guest-minus-host wall range uses the full dispatch/receive wall interval plus measured endpoint disagreement/uncertainty allowance. It assumes no unobserved transient wall jump inside a packet; endpoint sampling cannot establish this. An interval excluding zero is a recorded discrepancy, not an automatic fix or attributed cause. Compatible intervals establish only this bounded observation; no long-term stability or past-event explanation.

Offline command (no WSL launch):

```powershell
.venv\Scripts\python.exe scripts/clock_lineage.py --review output/engine2-clock-lineage-20261005.json --output output/engine2-clock-lineage-review-20261005.json
```

Review recomputes count/order/gaps, samples, domain continuity, source hashes, host gates and every summary range; binds input bytes with SHA256. Run from the matching execution revision if sources later change. Local hash consistency is not authenticated attestation or independent evaluation. Partial failed receipts are preserved but refused by the complete-review path. Error classes/stages only; unknown/malformed guest payloads and raw stderr/messages never saved. Exclusive output creation protects historical evidence.

## Scientific boundaries and API sources

The [Python time API](https://docs.python.org/3.12/library/time.html) documents an undefined performance-counter reference point and integer nanosecond/native Unix APIs; [Microsoft QPC guidance](https://learn.microsoft.com/en-us/windows/win32/sysinfo/acquiring-high-resolution-time-stamps) documents elapsed-time use including machine sleep. These semantics do not prove what caused this WSL incident. No induced sleep/pause, service intervention, actual Falco calibration-value read or historical correction is included. Endpoint facts do not exclude between-sample changes, unrelated collectors, or host/guest instrumentation perturbation. INC-032/INC-034, repeatability, matched baselines, independent labels and runtime ML remain open even if all sixteen snapshots complete.

Implementation checkpoint: live observation pending. Test outcomes are recorded in WORK_LOG/TEST_PLAN after execution, not inferred from this protocol.

## One declared observation: 5 October 2026

Executed once after implementation `1f2e4d4d359a0e181195d35278ceb16fe129592f` was pushed/remote verified. Start 08:57:45 UTC (14:27:45 IST). [Receipt](../output/engine2-clock-lineage-20261005.json) SHA256 `179ebdfa0f8b26a27ba0ed83b2a921b865f4438077567fe3f2e503cb38722710`; [offline review](../output/engine2-clock-lineage-review-20261005.json). Sixteen accepted packets/fifteen gaps, exit 0; observed means collection completed, **not clock agreement**. All source/domain/sample/order/gate/summary checks passed offline. No replacement or retry.

| Comparison | Observed result | Interpretation |
|---|---|---|
| WSL wall-minus-boot change from initial | 16 ranges include zero; union [-288,365] ns | Stable within these sampled native bounds only |
| WSL wall-minus-monotonic change | 16 ranges include zero; union [-3742,4034] ns | Same local sample limitation |
| Windows counter minus WSL boot elapsed | 13/15 ranges exclude zero positively; final [701218210,1023840119] ns | Host counter advanced more across guest sample instants, beyond dispatch/receive bounds |
| Windows counter minus WSL monotonic elapsed | 13/15 ranges exclude zero positively; final [701215040,1023843702] ns | Similar discrepancy for both native elapsed clocks |
| Guest-minus-host wall | 14/16 ranges exclude zero positively; initial [789558868,944589668] ns, final [-79923416,88219184] ns | Relationship moved toward overlap; compatible endpoint does not cancel earlier discrepancy |

Final guest boot elapsed [16505688681,16505689290] ns versus bounded host elapsed [17206907500,17529528800] ns. Whole host first-dispatch to last-receive wall elapsed 17529650000 ns/performance-counter elapsed 17529528350 ns, difference 121650 ns; descriptive whole-window reduction, not an extra predeclared gate. Host implementation reports QueryPerformanceCounter(), monotonic true/adjustable false/resolution 100 ns; this is API metadata, not hardware accuracy attestation. Packet round trips 119691000–433885600 ns; endpoint wall/counter disagreement -941250..3200 ns. Maximum native boot/mono sampling spans 373/3956 ns, host sample span 2500 ns.

All guest domain facts equal: namespace/children time:[4026531834], zero offsets and kernel boot hash e69ba2ab8be4a58844aaa9f0b93d2ee394b083834d4c53f8035056b48df15c61. Pre/post known-sensor absence/Redis preflight passed, time service active; no clock/service/power change. Original rejected receipt still SHA754c29d9e63b9a13ab455b0bcb829a5ed340b0c1c8f70d1bdfe024c25fbecddb.

INC-036 preserves this **sensor-free cross-host/guest advance discrepancy**, not a proven cause or absolute clock-accuracy verdict. INC-034's between-run 123-second difference and earlier collector lag are not causally explained by this short run. Next review read-only guest clocksource/kernel/time-discipline and host timer/virtualization facts, then choose a separately declared stability protocol. No automatic clock fix, repeated-until-pass sensor trials or ML/baseline acceptance.
