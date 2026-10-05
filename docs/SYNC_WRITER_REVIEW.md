# Synchronization writer review and proposed comparison (E2-026)

## Outcome and acceptance

Read-only follow-up to [E2-025](KERNEL_CLOCK_STATE.md), not another clock trial or engine change. Acceptance: inspect actual selected service/executable/drop-in facts, review versioned writer paths, distinguish plausible mechanisms from observed calls, preserve negative limits, propose a bounded comparison with restoration and request new approval before intervention.

Engine 1 stays frozen; Engine 2 timing, independent labels and ML are still unfinished. No new native state sampling, sensor, workload, package install, service change, host setting, WSL restart or clock correction in this review. [Minimized manually transcribed facts/source hashes](../output/engine2-sync-writer-review-20261005.json) are sequential context, not simultaneous E2-025 evidence, process attestation or a complete writer inventory.

## Actual environment observations

- ACG-Research timesyncd active/running/enabled, PID176, reported start06:18:43 UTC, version255.4-1ubuntu8.17. ExecStart points to `/usr/lib/systemd/systemd-timesyncd`; capability bounding set includes cap_sys_time (not proof of a particular privileged syscall).
- WSL drop-in `/usr/lib/systemd/system/systemd-timesyncd.service.d/wsl.conf` clears the base virtualization condition and allows noncontainer or WSL. ConditionResult=yes. It enables the service in WSL, not a special tick-adjustment implementation. Three executable/unit/drop-in hashes retained; no signed package/binary-source equivalence verified.
- Hyper-V implicit parameter Y; guest kernel6.6.114.1-microsoft-standard-WSL2, getconf CLK_TCK100. Selected guest chrony/chronyd/ntp/ntpsec units not-found/inactive. This is not exclusion of an arbitrary privileged program.
- W32Time Running/Manual, vmictimesync Stopped/Manual. WSL list shows ACG-Research and docker-desktop already Running/version2. Read only process-name snapshots in each, no additional named NTP daemon seen. Names can be truncated and PID namespaces incomplete; no historical/continuous absence or Docker bootstrap exclusion established. No other distro was started.

Commands executed (each separately checked for exit status):

```text
Get-Service W32Time,vmictimesync | Select-Object Name,Status,StartType | ConvertTo-Json
wsl --list --verbose
wsl -d ACG-Research -u acgresearch --exec /usr/bin/systemctl show systemd-timesyncd --property=ActiveState --property=SubState --property=UnitFileState --property=MainPID --property=ExecMainStartTimestamp --property=FragmentPath --property=DropInPaths --property=CapabilityBoundingSet
wsl -d ACG-Research -u acgresearch --exec /usr/bin/dpkg-query -W '-f=${Package} ${Version}\n' systemd systemd-timesyncd
wsl -d ACG-Research -u acgresearch --exec /bin/cat /sys/module/hv_utils/parameters/timesync_implicit
wsl -d ACG-Research -u acgresearch --exec /bin/cat /proc/sys/kernel/osrelease
wsl -d ACG-Research -u acgresearch --exec /bin/cat /usr/lib/systemd/system/systemd-timesyncd.service.d/wsl.conf
wsl -d ACG-Research -u acgresearch --exec /usr/bin/systemctl show systemd-timesyncd --property=ExecStart --property=ConditionResult
wsl -d ACG-Research -u acgresearch --exec /usr/bin/sha256sum /usr/lib/systemd/systemd-timesyncd /usr/lib/systemd/system/systemd-timesyncd.service /usr/lib/systemd/system/systemd-timesyncd.service.d/wsl.conf
wsl -d ACG-Research -u acgresearch --exec /usr/bin/systemctl show chrony.service chronyd.service ntp.service ntpsec.service --property=Id --property=LoadState --property=ActiveState --property=SubState
wsl -d ACG-Research -u acgresearch --exec /bin/ps -eo pid,comm
wsl -d docker-desktop --exec /bin/ps -eo pid,comm
wsl -d ACG-Research -u acgresearch --exec /usr/bin/getconf CLK_TCK
```

PowerShell serialized service enums as numbers1/4 and3; manually mapped to Stopped/Running and Manual. WSL list display included UTF-16/NUL characters, names/states minimized faithfully; raw process/unit output not committed.

## Versioned source paths, not syscall observations

| Candidate/path | Source-backed behavior | What it cannot establish |
|---|---|---|
| Guest timesyncd | v255.4 manager_adjust_clock calls clock_adjtime REALTIME: small offsets slew, larger offsets jump; cached drift_freq updated after call | No ADJ_TICK token/request in this file; Ubuntu patches/loaded binary not fully reviewed; not attribution of observed tick changes |
| Hyper-V kernel path | Version-matched WSL tag hv_util: explicit SYNC or enabled implicit guest-behind>=5s condition schedules work calling do_settimeofday64 | No live message flags/work trace; Y does not prove every sample steps time or identify the ~0.867s jump |
| Kernel discipline | Version-matched ntp.c handles ADJ_TICK assigning tick_usec; frequency calculation uses tick_usec, time_freq and boot-time tick adjustment | Endpoint fields do not identify caller or continuously reconstruct total rate |
| Kernel clock reset | timekeeping.c invokes TK_CLEAR_NTP for do_settimeofday64/injected offsets; reviewed ntp_clear clears phase/adjtime state, not tick_usec/time_freq | Guest-service stop or a wall-time step is not proof that residual rate state is reset |

[systemd-stable v255.4 manager](https://raw.githubusercontent.com/systemd/systemd-stable/v255.4/src/timesync/timesyncd-manager.c), [WSL6.6.114.1 hv_util](https://raw.githubusercontent.com/microsoft/WSL2-Linux-Kernel/linux-msft-wsl-6.6.114.1/drivers/hv/hv_util.c), [WSL ntp.c](https://raw.githubusercontent.com/microsoft/WSL2-Linux-Kernel/linux-msft-wsl-6.6.114.1/kernel/time/ntp.c), [WSL timekeeping.c](https://raw.githubusercontent.com/microsoft/WSL2-Linux-Kernel/linux-msft-wsl-6.6.114.1/kernel/time/timekeeping.c). Files fetched as data only using Python urllib with10s timeout/150000-byte limit; hashes/byte counts in artifact, no saving/executing downloaded source. Tag match is stronger than generic upstream review but not running-binary attestation. Token counts corroborate inspected functions, not whole-package semantic proof.

Canonical [WSL synchronization guidance](https://ubuntu.com/wsl/docs/stable/explanation/time-sync/) warns that guest NTP may conflict with implicit host sync and discusses the Ubuntu24.04 default. It is general guidance, not permission to disable services or proof of this incident's writer. [Ubuntu package listing](https://packages.ubuntu.com/noble-updates/systemd-timesyncd) agrees with observed package version; archive patchset/signatures/rebuild equivalence not audited.

**Inference:** do not label a guest-NTP-stopped condition “single authority.” It removes one active client, not unknown writers, accumulated tick/frequency state, or explicit Hyper-V sync requests. Reviewing mechanisms has narrowed the question but has not fixed or attributed INC-039. A small positive frequency field alone cannot explain the complete sampled rate; tick and other terms matter. No fitted correction or retrospective acceptance.

## Proposed one-batch comparison — NOT executed or authorized

Ask fresh approval for temporarily stopping **only ACG-Research systemd-timesyncd** during one diagnostic block, always restoring original active state. Not persistent disable, host service changes, manual time setting, kernel/provider changes, Docker/WSL restart, sensor/Redis workload or reset of tick/frequency state.

1. Implement/test a fail-stop controller before live action; source-freeze and exclusive new directory for a single batch manifest and separate before/stopped/restored receipts. Name/manifest/count finalized in a published protocol before execution, not fabricated here.
2. Require original service active/running/enabled, unchanged selected backend/domain facts, known sensors absent and lab preflight pass. Run one existing sixteen-packet kernel-state block with service active.
3. If complete, temporarily stop guest timesyncd, confirm inactive, run one same sixteen-packet block. Existing45s timeout bounds the child; total off-stage operation timeout and cleanup watchdog must be tested before execution. No retry or adaptive settling until passing.
4. A finally/cleanup path restores active state even on failure/interrupt. Verify running/enabled; if restoration fails, abort everything, report immediately and do not launch further measurement. A killed controller/WSL lifecycle interruption can defeat finally; approval must acknowledge and tested recovery/watchdog handling is required.
5. Only after restoration succeeds and prior blocks complete, run one restored sixteen-packet block. Maximum three blocks/48packets/96zero-mode queries; first failure cancels remaining measurement, never cleanup. Exact kernel gates unchanged, no sensor, before/after bytes preserved.
6. Compare interval discrepancies and state sequences descriptively, with service states and all aborts recorded. Kernel residual state is measured, not reset. A cleaner stopped block supports a limited hypothesis, not causal isolation, independent accuracy, long-term stability, general overhead or ML acceptance. Persistent discrepancy motivates separately reviewed writer tracing/native-Linux environment evaluation; neither is authorized here.

No management code or intervention in this commit. This proposal needs approval and tested orchestration/protocol completion before execution. The September one-time approval is spent; do not reuse it. Production/research publication readiness remains gated on stable repeatability, independent labels/evaluation and measured overhead, not this review alone.
