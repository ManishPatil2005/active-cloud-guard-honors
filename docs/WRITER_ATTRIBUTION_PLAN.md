# Writer-attribution preparation: inventory before attachment

19 October 2026 · QA-052 / WL-129 · E2-005/E2-025/RQ3.

**Prepared offline. No inventory, attachment, fresh clock observation or native
execution ran.** The latest native evidence is [QA-051](KERNEL_DOMAIN_BATCH_RESULT.md),
which observed large wall/boot and RAW/monotonic changes without identifying a
writer. D approval is consumed; the proposed scopes below need new consent.

## Why not repeat the old guest trace?

[QA-037](CLOCK_WRITER_TRACE.md) already captured two successful selected calls
from the then-identified guest timesyncd process. It did not cover other threads,
other processes, the WSL-system time agent or kernel/hypervisor paths. The old
PID176 is not a current target. A second uncorrelated trace of that PID would
neither identify all remaining paths nor explain QA-051 automatically.

Earlier source/context review identified WSL-system PHC synchronization as a
candidate path, not the proven current writer. Its current process identity,
namespace and tracer compatibility are unknown. Do not guess a PID, run the
Ubuntu tracer in another distro assuming compatible libraries, or attach to
everything to compensate. Establish the actual candidate and tool context first.

## Offline improvement completed

`scripts/clock_trace_review.py` consumes saved trace bytes only. It binds an
expected SHA256, preserves the existing 1,048,576-byte per-trace ceiling, and
applies finite analysis guards of 4,096 lines/4,096 characters per line. It
reserves a fresh output and never executes strace, reads native clocks or attaches.

The declared profile is the existing strace6.8 single-PID `-ttt -T -s128` output
for adjtimex, clock_adjtime, clock_settime and settimeofday. It distinguishes:

- decoded zero-mode queries and read-marker observations from named non-query
  modes, without declaring a process to be a verified writer;
- nonnegative returned time state from a failed syscall; neither proves stability;
- observed setter names from proof of an actual clock change, including NULL
  argument cases;
- unsupported, unfinished, multi-PID or unknown-mode lines, which remain explicitly
  uninterpreted instead of disappearing or yielding a clean verdict.

Mode recognition is lexical, not proof of a legal input-mask combination or the
original entry buffer. Returned timex values are never promoted to requested
tick/frequency/offset values. The strace6.8 decoder prints timex at exit; see its
[versioned implementation](https://raw.githubusercontent.com/strace/strace/v6.8/src/time.c).
Linux documents zero/read-only modes and returned states separately from parameter
adjustments in [adjtimex(2)](https://man7.org/linux/man-pages/man2/adjtimex.2.html).
The reviewer preserves original line order: `-ttt` wall timestamps can change and
are not a monotonic basis for sorting or causal alignment.

Every report keeps process identity, trace completeness, global coverage, entry
buffer verification and cause identification **false**. Even an empty trace is
not evidence of no writers. Identity/attachment/exit/namespace evidence requires
separate review; this helper intentionally cannot supply it.

### Actual offline re-analysis

[New saved-trace accounting](../output/clock-writer-saved-review-20261019-qa052.json)
processed QA-037's original848bytes/two lines: two completed clock_adjtime calls,
both with decoded non-query modes and return0. Nothing was re-executed or newly
attributed. No raw arguments, returned tick values, process identifiers or raw
timestamps were copied into that report. Its source hash binds this reviewer.

[Provenance check](../output/writer-preparation-provenance-20261019-qa052.json)
revalidated four original public-summary bindings to private evidence and the
locally retained extracted strace binary hash
`28f957c227012de0b18d1bd7fff2d396cb693ea60ed8013be68de071e84b5001`.
This is a Windows filesystem check only: not native availability, executable
compatibility, fresh package provenance or a vulnerability-free claim. Earlier
signed-package verification remains a dated QA-037 fact, not a new download.

This fills an offline evidence-accounting gap, not a reproduced production-clock
defect or repair of WSL time. Native readers, both engines, baseline, stack,
environments and all existing sampling/qualification/trace limits are unchanged.

## E0 — next proposed approval: bounded candidate/tool inventory

**Inventory is a prerequisite, not writer attribution.** One read-only pass over
the existing `ACG-Research` guest and WSL system distro is proposed, with a hard
120-second total ceiling. Read-only root access is requested only for selected
process identity and executable-file reads where required. No attachment or
execution of the inspected tracer, daemon or library is included; existing bounded
read-only inventory helper commands are permitted. If a prerequisite is unavailable, report
that fact; do not install, restart or change permissions/settings.

1. Reserve fresh private evidence under ignored `output/runtime-raw/`. Record
   consent, execution/controller hashes, context and exact commands before use.
   Do not reuse prior PID or execution directories.
   Check the guest's running-state listing first; if it is stopped, report
   unavailable rather than start it. Access the system context only through an
   already running WSL instance. No explicit startup, shutdown, terminate or update.
2. In each context enumerate at most256 `/proc` PID `comm` names, using bounded
   reads. Select at most8 exact candidates named `systemd-timesyn`, `chronyd`,
   `ntpd` or `ntpsec`; retain candidate metadata only, not a full process dump.
   If those bounds would be exceeded, stop/report incomplete, never truncate into
   a claim of complete coverage. Names are candidate filters, not writer identity.
3. For candidates read PID/start ticks, executable path/hash, state/TracerPid,
   PID/time namespace links and boot identity. Read the selected guest timesyncd
   unit's ActiveState/SubState/MainPID/UnitFileState only. Do not read environments,
   command lines, service configuration, memory, credentials or unrelated file contents.
4. Check before/after identity consistency. Read existing ptrace-policy value
   without changing it. Missing/denied facts stay unknown; no permission repair,
   forced detachment, process signal or automatic target substitution.
5. Inspect only the retained tracer file and required loader/library files for
   presence, ELF/architecture metadata and bounded digests in each context. No
   `strace --version`, loader invocation or new tool execution. Native execution
   compatibility remains unverified even if those files appear compatible.
6. Preserve raw inventory privately; publish a minimized candidate/tool readiness
   report. No clock observation, syscall query, trace, service action or trial.

Control budgets: selected commands at most5seconds each; metadata output at most
1MiB per context; comm reads64bytes, stat/status8KiB, links512bytes; executable
hashing at most8MiB per file/32MiB total per context. These inventory bounds do
not raise any existing trace, sensor, timing or research qualification budget.
The bounded one-off read-only controller must be inspected before execution.
No opaque shell-generated mutation, unbounded proc walk or fallback install.

### Exact approval E0 needed before running

> I approve one bounded read-only writer-candidate and tool-file inventory in
> ACG-Research and the WSL system distro, with a120-second total ceiling and the
> QA-052 per-command/process/file/output bounds. Allow root only for the specified
> read-only process identity and executable-file checks. Preserve private evidence.
> No process attachment, inspected-binary execution, clock observation or adjustment,
> service/host/WSL configuration change, explicit startup/restart, download, network,
> Docker/Redis/sensor operation or retry. Do not proceed automatically to tracing.
> Keep all existing qualification and trace limits unchanged.

No E0 operation is approved by preparing this document. No extra clock batch,
alignment run or guest-service trace is folded into an inventory approval.

## E1 — separate exact target trace, only after E0 review

This is **not ready for operational approval now** because the current target
PID/start time/namespace/executable and compatible tracer context are unknown.
Use E0 to propose one exact candidate and explain what remains unobserved.

The later proposal must name the actual context, PID/start ticks/executable hash,
tool/loader identity and support for the chosen flags. Revalidate immediately
before attachment; require no other tracer and a running, non-stopped target.
Permission for even a selected `strace --version` execution must be in that new
scope; E0 does not include it. A mismatch refuses rather than tracing a new PID.

Retain the earlier45second SIGINT/+3second kill and1MiB per-output-file limits,
four syscall names, finite string limit and fresh private outputs. Explicitly
describe ptrace's potential brief pauses/overhead, which thread(s) are covered,
allowed signals to the tracer only, and before/after same-process/detachment
checks. No `-f`, EXITKILL, syscall injection, global/kernel/eBPF tracing, service
control or automatic retries are implied. An export/cleanup ambiguity must be
reported, not repaired by restarting the service or signalling arbitrary tasks.

If temporal linkage to domain changes is proposed, obtain a separate precise
concurrent sampling scope and a reviewed clock-domain mapping. Do not subtract
wall timestamps from unrelated old observations or call coincidence causality.
Without that evidence, report only a selected process's captured syscalls and
decoded fields; no claim that it caused QA-051 or covers kernel/host writers.

E1 may remain blocked if a compatible retained tool or suitable target is absent.
That is a reason for a new explicit choice, not silent installation, broader
attachment, relaxed limits or service intervention. All A/D approvals are consumed;
B sensor qualification and E0/E1 are separate. Research/capacity/production gates
remain open. Final combined Windows checks: 323 passed, one existing Linux-only
skip; lint, 178-file formatting and dependency compatibility pass. No fresh Linux
suite or native invocation. Exact verification and publication: [WL-129](WORK_LOG.md).
