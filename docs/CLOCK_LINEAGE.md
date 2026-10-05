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
