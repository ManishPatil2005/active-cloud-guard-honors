# Namespace-gated realtime/boot-clock diagnostic

E2-019, predeclared 5 October 2026. User requested status/proceed and named commits for each completed change. Implement/test this diagnostic first and commit separately from its eventual observed result. No promise of a clock fix or automatic research acceptance.

## Question and fixed protocol

E2-018 found the collector's stored offset + kernel boot time mechanism. Record bracketed **CLOCK_BOOTTIME / CLOCK_REALTIME / CLOCK_BOOTTIME** readings to bound the current realtime-minus-boot relationship. Never substitute CLOCK_MONOTONIC. Each sandwich must be forward, <=5 ms wide and use nonnegative integer nanoseconds. Source semantics: [Linux v6.6 helper documentation](https://github.com/torvalds/linux/blob/v6.6/include/uapi/linux/bpf.h) describes boot-time helper behavior; [Linux man-pages time namespaces](https://man7.org/linux/man-pages/man7/time_namespaces.7.html) describes boot/monotonic offsets and nonvirtualized realtime. These are semantic references, not exact WSL kernel-build attestation.

One new bounded trial, only opt-in `--boot-clock --clock-domains --correlate --fixed-warmup --profile ping_4`. The previous clock-domain protocol retains eight TIME reads and precise PING clocks. Boot snapshots: before sensor creation, immediately after docker run returns, after identified readiness, plus before/after each of four measured PINGs (11 total sandwiches). Initialization is bracketed by launch/readiness, **not directly observed**: actual calibration time and stored BPF offset remain unknown. Do not call prelaunch reading the collector's calibration value.

Read harness/Redis/sensor `/proc/self/ns/time`, `/proc/self/ns/time_for_children`, `/proc/self/timens_offsets` and kernel boot ID before/after; export the boot ID as SHA256 only. Namespace IDs may differ across domains, but each domain's active/children namespaces must match: [Linux v6.6 proc offset implementation](https://github.com/torvalds/linux/blob/v6.6/kernel/time/namespace.c) reads the children namespace. Require exactly three declared domains, unchanged facts across endpoints, same boot-ID hash, zero monotonic/boottime offsets and valid fields. These checks support a same-kernel/unshifted-clock comparison, not cryptographic attestation. Refuse missing/nonzero/changed/ambiguous facts rather than assuming namespaces match or installing a backend helper. No proc writes, arbitrary host path reads, additional mounts/capabilities, time-service changes, WSL reset or new language/runtime.

Compute offset-change intervals relative to prelaunch, and the event-implied offset range from each precise PING's boot-clock bracket. Report intersections descriptively; do not fit/apply an offset, certify Falco alignment or promote the run into runtime baselines. Endpoint readings can miss transient changes. Additional proc commands perturb collection; this distinct `container_pid_connect_boot_v1` receipt is excluded from existing repeat acceptance/latency pairing. Keep extra/unassigned events visible.

## Execution boundaries

Existing lab/local-daemon preflight first; exactly one new receipt at `output/engine2-boot-clock-20261005.json`. Source hashes include the new module; default sensor, Engine 1 and prior protocols unchanged. Existing 15-second sensor duration/watchdog/resources remain; extra checks must finish within those limits, no adaptive extensions. Abort/preserve evidence on failure, no replacement run. Explicit sensor enumeration and time-service state after completion. Independently reparse SHA-matched raw correlation, server-clock summary, boot-clock summary and collector counters offline before interpretation.

Planned command after passing software checks and committing implementation:

```text
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python scripts/sensor_trial.py --profile ping_4 --fixed-warmup --correlate --clock-domains --boot-clock --output output/engine2-boot-clock-20261005.json
```

Acceptance means collection and validated diagnostic accounting, **not stable clocks**. A changed relationship is a lead; no observed change does not disprove earlier drift. Retain INC-032 until causal mechanism and repeatability gates are independently addressed.

## Implementation validation, before live execution

407 tests passed on Windows (2.13 s) and Linux (3.50 s); [Windows receipt](../output/engine2-boot-clock-implementation-windows-tests-20261005.xml), [Linux receipt](../output/engine2-boot-clock-implementation-linux-tests-20261005.xml). Twenty-nine additions exercise namespace/boot identity parsing and gates, children-namespace ambiguity, bracket widths/order/types, synthetic offset change, saved-summary corruption, option prerequisites, fixed backend commands and absence of monotonic fallback. Ruff lint/format (74 files) and Windows pip check pass. Actual boot-clock collection has **not run at this implementation checkpoint**; lifecycle/resource timing and transient-change coverage are not exhaustively tested. No independent detection evaluation or Engine 1 live rerun.

## Observed single attempt, 5 October 2026

Implementation commit `ac6767adece8b231830d98fc0b42019a32899b82` pushed and remote hash matched before collection. Declared command above ran once at 07:43:31 UTC, exit 1: second iteration's before-TIME bracket raised `unstable or excessively wide clock bracket`. [Failed receipt](../output/engine2-boot-clock-20261005.json), [offline partial review](../output/engine2-boot-clock-partial-review-20261005.json). No retry, clock change or extension. Pre/post lab preflight passed, sensor enumeration empty afterward, timesyncd active/unchanged.

All three initial domain facts passed: shared boot hash, zero offsets, active/children equality despite distinct namespace IDs. Both identified warmups and first measured PING succeeded/uniquely observed. Only one of four measured PINGs completed; `workload_executed=true` means dispatch began, **not completed protocol**. Second row is empty: command/bounds inputs are not retained when redis_bracket raises. Existing gate combines clock disagreement, sample width and command duration (>500 ms); missing inputs prevent deciding which condition triggered. Post-domain facts, full measurement, metrics and four-PING summaries are absent. Do not reconstruct them or claim full stability.

SHA-matched failure raw log: 243 records, six connects; tracked warmup PIDs 249/255 and measured 267 each exactly one, three unassigned auxiliary connects. Five valid boot sandwiches (3 launch/readiness, 2 first PING), widths 319–975 ns; change intervals relative to prelaunch all include zero, union -801 to +971 ns. The single event includes zero in harness (-6,593,326 to +46,985,563 ns) and server (-52,603,562 to +55,614,437 ns) bounds; implied offset intersects prelaunch. This bounded partial observation does **not** resolve earlier failed runs, measure actual collector calibration or pass repeatability. Raw bytes remain ignored/local; source hashes (seven), available bracket recomputation and strict raw PID accounting verified offline. Receipt hash bound in partial review; consistency checking is not independent/authenticated evaluation. INC-033 records aborted attempt/evidence gap; INC-032 remains open.

Offline review used Windows Python and existing functions, not sensor execution. Reproduction core (after checking saved receipt/source/raw SHA256 hashes and selecting its sole SHA-matched ignored sensor.log):

```python
from cloudguard import boot_clock
from cloudguard.clock_domains import redis_bracket
from cloudguard.clock_check import compare
from cloudguard.correlation import connection_counts
boot_clock.checked_domains(receipt["time_domains_before"])
matches, extra = connection_counts(raw, receipt["container_id"],
    receipt["warmup_process_ids"] + receipt["correlation_process_ids"])
o = receipt["clock_domain_samples"][0]
for remote in (o["before"], o["after"]):
    seconds, nanos = divmod(remote["redis_unix_ns"], 10**9)
    assert redis_bracket(remote["first"], remote["last"],
        f"{seconds}\n{nanos // 1000}") == remote
samples = [boot_clock.checked(s["sample"])
    for s in receipt["boot_clock_snapshots"]]
samples += [boot_clock.checked(o["boot_before"]), boot_clock.checked(o["boot_after"])]
initial = samples[0]
changes = [(s["offset_lower_ns"] - initial["offset_upper_ns"],
    s["offset_upper_ns"] - initial["offset_lower_ns"]) for s in samples]
clock = o["ping_clock"]
timing = compare(clock["first"], clock["last"])
event = matches[o["process_id"]][0]
allowance = abs(timing["clock_difference_ns"]) + timing["sampling_uncertainty_ns"]
harness = (event - clock["last"]["wall_ns"] - allowance,
    event - clock["first"]["wall_ns"] + allowance)
server = (event - o["after"]["redis_unix_ns"] - 999,
    event - o["before"]["redis_unix_ns"])
```

Next: preserve sanitized failed TIME sample/comparison fields before validation, with regression tests. Do not weaken the gate or rerun the failed slot; a further live experiment needs a separately declared protocol after this evidence gap is fixed.

**Later software checkpoint (E2-020):** that retention improvement is now implemented with 414 tests each OS; see [recording contract](CLOCK_DOMAINS.md). No additional live attempt. The source hash review above was performed before this later code change; rechecking historical execution hashes requires implementation commit ac6767a, not assuming latest source matches. Original receipt/hash/empty row unchanged. Next is separately predeclared sensor-free bracket diagnosis, not replacement of this failed slot.
