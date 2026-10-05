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
