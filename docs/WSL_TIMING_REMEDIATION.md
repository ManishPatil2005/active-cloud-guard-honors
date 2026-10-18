# Live timing investigation and bounded UTC wait repair

QA-045 adds earlier cumulative sampled refusal, not a physical clock correction.
SavedQA-044breach beforeindex19 verified; no live/service/clock action. Nonrotating
capture refinement and unresolved capacity/native/discipline gates are recorded
in [the offline refinement report](CAPTURE_RETENTION_CLOCK_REFINEMENT.md).

QA-044 integrated follow-up is now executed once with fresh approval: initial
alignment/all60PINGs pass, but minute clock difference-129.242680ms rejects50ms.
Final retention/command-time correspondence also fail; clock-only QA-042 is not a
cure. Service/Redis restored and sensor removed. [Actual integrated result](RUNTIME_WINDOW_TRIAL.md),
WL-121/INC-098; no retry, relaxed limits, real-data qualification or host changes.

18 October 2026; QA-041/QA-042/QA-043, E2-005/E2-025/RQ3. The user explicitly requested
fixing live timing and coverage. **Live qualification remains open.** A scheduler
defect is repaired and software-tested; the first service correction was rejected
and restored. After fresh exact approval the revised service comparison ran once:
its post-settling segment passed narrowly. No new sensor workload or real-data
study occurred; the underlying clock cause is not resolved.

## Current observations and correction attempt

One unchanged ordinary-user kernel diagnostic collected16packets/32zero-mode
queries. [Receipt](../output/kernel-clock-current-20261018-qa041.json) and
[offline review](../output/kernel-clock-current-review-20261018-qa041.json).
Final RAW-minus-monotonic bounds[89384485,89450212]ns; wall/BOOT change
[-664,486]ns. Tick10000/10121/10146, kernel TIME_OK. This records continuing
rate disagreement in that short sample, without a wall/BOOT step there.

Read-only WSL inventory reports2.7.3.0/kernel6.6.114.1. Separate distro commands
initially showed changing service PIDs and WSL reported stopped between commands;
one bounded ordinary-user sleep process kept a session open for subsequent work.
The comparison additionally checks identical clock-domain evidence across its
blocks. Session lifetime and clock convergence cannot be assumed from separate
shell invocations.

`wsl --system --exec /bin/sh -c 'chronyc tracking'` responds with PHC0 tracking,
while ACG-Research timesyncd is active. The agent is not visible in that guest's
ordinary process inventory. Microsoft's version-matched
[WSL2.7.3 init source](https://raw.githubusercontent.com/microsoft/WSL/2.7.3/src/linux/init/main.cpp)
contains StartTimeSyncAgent launching chronyd with a PHC source. This is source
and local socket-response evidence, not an authenticated identity/syscall trace
of every writer. [Canonical guidance](https://ubuntu.com/wsl/docs/stable/explanation/time-sync/)
warns of guest-NTP/host synchronization conflicts in Ubuntu24.04 on WSL. It
motivates testing removal of the guest writer; it does not establish a fix here.

The existing Docker Desktop was started under the owner's lab-start authority,
with settings untouched. Exact Redis remained stopped, restart=no, published
only127.0.0.1:16379. No research sensor launched. An inert transient timer running
`/usr/bin/true` verified timer execution before any time-service action.

One correction attempt used a fresh private directory and fixed sequence:
one16-packet baseline; arm240second systemd rollback to enable/start the original
guest service; stop only systemd-timesyncd; four16-packet post-stop blocks.
Source/backend/domain continuity and cross-block RAW/MONO and wall/BOOT bounds
were checked against50ms. Rollback was armed before stop; no setters, Windows
time settings or host-agent changes. Timer time is guest time; host suspend or
manager failure can defeat operational deadlines, so it is not a physical-time
guarantee.

**Rejected:** final post-stop RAW/MONO bound[-118369934,-118348908]ns and wall/BOOT
bound[-52337372,-52336746]ns. Tick changes continued after removing this guest
writer. This disproves accepting guest removal alone as sufficient in this test;
it does not identify all causes. The original enabled/running service was
restored (newPID720), then its rollback timer cancelled. No persistent service
configuration change, fitted timestamp correction or accepted collection.
[Minimized comparison](../output/guest-ntp-correction-summary-20261018-qa041.json)
binds24private file hashes and5observation receipts. Raw evidence/helper stays
under ignored output/runtime-raw and tmp, with selected commands in WORK_LOG.

## Repaired scheduler defect — QA-043

The old wait derived a monotonic deadline from the first realtime sample. A
small backward realtime adjustment could leave it early, even though the
original50ms clock-consistency predicate passed. Regression offsets -1ns,-1ms,
-49ms,-50ms reproduce four avoidable rejections.

New `utc_boundary_single_recheck_v2` records the initial sample/timing/error and
allows one additional wait, capped at50ms, only when the first clock predicate
already passes and the boundary is slightly early. It then takes a fresh actual
sample and reapplies the original50ms clock and0..100ms UTC boundary gates.
No fabricated timestamp, changed tolerance, repeated workload or retry-until-pass.
A new clock fault during the one additional wait still rejects. Existing large
clock failures do not invoke this path. Wait version is explicit in new receipts;
old records and generic workload counts remain unchanged.

This repairs scheduling under an already acceptable small adjustment; it cannot
repair the observed large rate/step behavior, certify event coverage, or qualify
historical failures. New tests preserve both initial and final evidence.

## Executed revised comparison — QA-042, limited candidate pass

Revised private helper tmp/qa042_clock_settle.py: one baseline, arm480second
rollback, stop only guest timesyncd, fixed120second settling period, then four
fixed16-packet observations;260second controller timeout. Restore after the
comparison whether it passes or fails; no automatic repeat, no sensor/workload,
no Windows or host-agent changes.
The purpose is to test convergence of the remaining controller after the first
attempt showed continuing correction, not to select a favorable trial.

Automatic approval review initially rejected this longer intervention without
fresh approval. The user subsequently explicitly approved the exact revised
comparison, which ran once at source4a4384c. This does not alter the earlier
QA-041 failure or its historical pending proposal. No automatic repeat.

[Minimized result](../output/guest-ntp-settle-summary-20261018-qa042.json) binds
26private JSON files, the helper digest and5native block receipts. Baseline
wall/BOOT change[-297815116,-297814202]ns remains outside50ms. After the fixed
twelve10second sleeps, all64post-settling bounds passed the unchanged50ms limit.
Maximum endpoint47,943,999ns leaves only2,056,001ns margin; finalRAW/MONO
[-47772347,-47740756]ns and wall/BOOT[-35838831,-35838003]ns. Settling measured
119,798,299,536ns against RAW, not proof of120physical seconds. Clock-domain,
source/backend and summary arithmetic were checked offline; that is not signed
attestation, independent human evaluation or a repeatability study.

Original service restored enabled/active/running/PID1990 and only then rollback
cancelled; separate read-only verification confirmed exact timer inactive and
not-found, no pending jobs. No permanent service/host setting changed. The
candidate condition was deliberately not left active for another workload.

At this checkpoint the next step was a separately scoped integrated qualification
under the candidate condition (subsequently approved/executed as QA-044), with unchanged UTC alignment/readiness/identity/
coverage/drop gates and unconditional restoration. This clock-only permission
does not authorize a sensor trial or changes to host PHC synchronization. A
passing post-settling segment does not prove full-window capture or explain the
baseline/earlier failures. Actual context, reviewer labels, grouped splits and
calibration remain prerequisites for independent research evaluation.

Exact commands, failures, verification and named publication: WL-119/WL-120.
