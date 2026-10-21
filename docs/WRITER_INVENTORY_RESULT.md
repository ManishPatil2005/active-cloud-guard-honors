# Approved E0 writer-candidate inventory

19 October 2026 · QA-053 / WL-130 · E2-005/E2-025/RQ3.

**E0 completed once; no writer or clock cause is established.** The approved
read-only guest/system inventory finished in approximately 0.86 seconds, within
the 120-second outer ceiling. No tracing, inspected-binary execution, fresh clock
observation, service/clock/host changes, explicit startup/restart, download,
network or Docker/Redis/sensor operation was issued. No retries or fallback installs.

Execution checkout: `e85ec6716f651f8ace49f49491296c9ea03ff900`.
The existing guest was listed running before guest access and again before
system-context access. Both root metadata commands and both running-state reads
exited zero; no deadline expired. Those endpoint gates are not an atomic guarantee
against external WSL state changes between commands.

## What was found

| Observation | ACG-Research guest | WSL system view |
| --- | --- | --- |
| Enumerated PID entries |37 |78 |
| Exact approved-name candidates |1: systemd-timesyn |0 |
| Candidate PID / start ticks |6922 /6379794 |No matching candidate in observed list |
| Retained strace file |Present; expected hash matches |Same file/hash visible |
| ELF metadata |64-bit little-endian x86-64 |Same static header profile |
| Selected libc/loader paths |Debian-style libc/libunwind and loader present |Loader/lib64 libc present; selected libunwind paths not found |
| Runtime compatibility |**Not tested** |**Not tested** |
| Metadata stdout+stderr bytes |4,621 |2,092 |
| File-hash input bytes |4,636,624 |4,677,312 |

The name filter was exactly `systemd-timesyn`, `chronyd`, `ntpd`, `ntpsec`.
Zero matches in the system view means only that no such exact names matched
the enumerated entries. It does not exclude differently named, short-lived,
other-namespace, kernel or hypervisor writers. Nonmatching process details were
not retained. Missing selected library paths do not prove no library exists
elsewhere; the inventory was not an unrestricted filesystem search.

Guest unit metadata was active/running/enabled with MainPID6922. The selected
process was sleeping with TracerPid0 at both endpoints; start ticks, executable
and namespace/hash facts agreed before/after. Its executable was:

- Path: `/usr/lib/systemd/systemd-timesyncd`.
- SHA256: `5e87427803daf1dbe974cc62fba335c96ff24e37892f67d9095d6703d2c32009`.

This hash differs from QA-037's dated executable hash. The old PID176 and old
binary/source interpretation must not be reused as current identity. This is a
provenance difference, not evidence of tampering, an identified update, or the
cause of clock instability. No version/package/source attestation was performed.

The contexts reported equal boot identity/time namespace but different PID
namespace identities. These are observed metadata relationships, not a proof of
global process visibility or a collector clock-domain calibration. Ptrace policy
read1 in both contexts; no setting or permission was changed. Attachability and
required capabilities were not tested.

## Tool readiness is conditional

The retained tracer file was 2,087,432 bytes and matched the original hash:
`28f957c227012de0b18d1bd7fff2d396cb693ea60ed8013be68de071e84b5001`.
Guest selected loader/libc/libunwind hashes are in the receipt. The system-view
loader/libc differ. Neither `strace --version` nor any inspected daemon/library
was executed. Static ELF/file presence cannot establish loader resolution or
ptrace compatibility. No tool is promoted to newly verified native compatibility.

## Preservation and checks

[Minimized reviewed receipt](../output/writer-inventory-review-20261019-qa053.json)
binds the private manifest, terminal/controller/collector, reconstructed native
collector payload and imported bounded-runner source. Raw command intents,
exits, bytes, source and selected metadata remain under ignored
`output/runtime-raw/writer-inventory-20261019-qa053/`.

Offline review verified 20 manifest-listed files plus the separately bound
manifest, decoded the raw frames independently, recomputed counts/budgets,
compared candidate identity endpoints, and checked the imported runner against
the execution Git commit. Individual argv values retained its existing4,096
character ceiling. The reviewed collector source and actual command payload
are separately hashed: an additional harmless newline filled its unused chunk,
so the native argument payload is not falsely described as byte-identical to
the source file. No process environment, command line, memory, full process dump,
raw boot identifier or inspected binary is published.

All existing bounds stayed unchanged: <=256 PID entries/8 candidates per context,
5-second selected commands,1MiB metadata output,8MiB per hashed file/32MiB total
hash input per context, and the120-second total. No change needing restoration
was commanded; external changes were not ruled out. Offline reviewer/documentation
checks passed27tests. Product/core/native reader/reviewer source and dependencies
were unchanged; no full-suite or Linux package requalification is claimed.

## E1 attempt update — QA-054

The user subsequently approved one E1 attempt using the exact scope below.
Its first gate, `wsl.exe --list --running`, returned `Access is denied` /
`Wsl/E_ACCESSDENIED`; the exit code was not captured. The attempt stopped there.
No guest identity check, tracer version check, attachment, trace or retry ran.
See [QA-054 result](WRITER_TRACE_E1_RESULT.md). The cause of the WSL access
denial is unknown, and this attempt provides no new guest/process evidence.
The approval is consumed; another E1 attempt requires restored WSL access and
fresh approval.

## Proposed E1 guest-only trace — approval scope (consumed; attempt blocked)

E0 consent is consumed. The following is an optional next proposal grounded in
the observed guest identity, not authority to attach now. It would observe the
**current different guest binary**, not repeat a stale PID. It still would not
cover system-view/kernel writers or prove the cause of QA-051. No system target
was identified by E0, and no attachment to the system view is proposed here.

Before any trace, obtain fresh consent for the exact identity above. Recheck
MainPID6922, start ticks6379794, path/hash, namespace, active/running/enabled unit,
non-stopped process and TracerPid0. If anything changes or is unavailable, stop;
do not locate/attach a replacement PID. Recheck tool/loader/library hashes.

If approved later, one bounded retained-tool `--version` invocation would first
test minimal guest execution compatibility (5seconds, <=4,096 combined bytes),
without tracing. Only after it returns the expected strace6.8 identity and all
process/file checks pass would one selected45-second trace be eligible. No
download/install, library repair, privilege-policy change or retry on failure.
Version success would not itself prove attachability or unbiased timing.

Retain the original45-second SIGINT watchdog/+3-second kill grace,1MiB per-output
file ceiling, `-I2`, four syscall names, `-s128`, `-ttt -T` profile and single-PID
scope. No `-f`, other threads/processes, EXITKILL, syscall injection, kernel/global
tracing, concurrent clock sampling or service control. Ptrace can briefly pause
the process and adds overhead; this is not an efficiency benchmark. Only the
tracer's own job may receive watchdog signals, not the attached service.

Preserve raw evidence even for an empty/failed trace; verify same process, running
unit, TracerPid0 and non-stopped state afterward. An uncertain detach/state must
be reported for operator recovery, not fixed by signalling/restarting the service.
Use a120-second outer controller ceiling without extending the45-second trace.
No whole-writer coverage, causal timing join or clock stability claim follows.

### Exact E1 approval, if the user chooses this scope later

> I approve one guest-only E1 diagnostic in ACG-Research for timesyncd PID 6922,
> start ticks 6379794 and executable SHA256
> 5e87427803daf1dbe974cc62fba335c96ff24e37892f67d9095d6703d2c32009.
> Allow scoped root identity reads and one retained strace --version check under
> 5 seconds/4,096 bytes; only if compatibility and exact identity checks pass, attach
> once for 45 seconds to that PID for the four selected clock syscalls, with the
> original SIGINT/+3-second kill grace and 1 MiB per-output-file limits, within a
> 120-second outer ceiling. I understand attachment can briefly pause the process.
> Preserve failures and verify detachment/same running process afterward. No PID
> substitution, other-thread/process tracing, clock/service/host changes, downloads,
> network, sensor/workload, concurrent clock study or retry. Do not proceed further.

This proposal is not a promise the process still exists or will accept attachment.
Loaded timing, full-minute capacity/identity/coverage, independent evaluation,
novelty and production acceptance remain open. Exact execution/publication details:
[WL-130](WORK_LOG.md).
