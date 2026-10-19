# Bounded clock-writer observation — QA-037

QA-053 actual E0 metadata: [current inventory](WRITER_INVENTORY_RESULT.md) found
guestPID6922 with a different executable hash from QA-037; old PID/source identity
is not reusable as current. No new attachment or tool execution, cause unknown.
E0 consumed and conditional E1 remains unapproved; QA-037 trace below unchanged.

QA-052 offline preparation: [next writer-attribution plan](WRITER_ATTRIBUTION_PLAN.md)
separates unapproved candidate/tool inventory from later exact-target tracing.
Original QA-037 bytes/tool hashes rechecked locally and saved trace accounted by
new offline helper; no new native operation or stronger causal claim. Historical
single-process result and consumed approval below remain unchanged.

## Outcome, 12 October 2026

The one expressly authorized trace completed. PID176, the existing
systemd-timesyncd main process, made two successful
`clock_adjtime(CLOCK_REALTIME, ...)` calls. This establishes an active guest
clock-adjusting process during this observation, **not the cause or repair of
QA-035's failed alignment**. Engine2's live timing/coverage gate remains open.

[Minimized receipt](../output/clock-writer-trace-summary-20261012-qa037.json).
Raw trace, stderr, before/after identity and execution records remain private in
the Git-ignored `output/runtime-raw/clock-writer-trace-20261012-qa037` directory.
No raw trace or tool binary is included in the publication commit.

## Approved scope and execution

Owner explicitly approved one isolated official Ubuntu package download and
one 45-second trace of the existing process, with detachment and service checks.
No system-wide installation, clock-setting by the diagnostic, service changes,
sensor, workload, automatic retry, or persistent configuration was authorized
or performed. Normal autonomous timesyncd adjustments continued and were observed.

Acceptance: verify signed package provenance before execution; fresh private
outputs; exact executable/PID/start-time identity; no pre-existing tracer;
finite timeout and output limits; preserve even a negative trace; verify the
same service is running and detached afterward. No stability acceptance follows
from meeting these diagnostic criteria.

Ubuntu noble/main amd64 strace6.8-0ubuntu2 was downloaded once over HTTPS from
the exact URL in the receipt. `gpgv` verified the cached noble InRelease with
the installed Ubuntu archive keyring (2018 signing key, fingerprint in receipt).
The signed release's uncompressed Packages SHA256 and size matched the local
index; the exact strace stanza matched version, architecture, filename, size and
SHA256. Download:584172bytes, SHA256
`d588810ae26b06fee6678dc81e5b54f6efcde8e718e4589adb4d11d254b9820b`.
This is integrity/provenance against the cached April2024 signed baseline, not
a freshness or vulnerability-free claim. Existing libc6/libunwind8 dependencies
were reused; no dependency installation or apt refresh occurred.

`dpkg-deb --extract` unpacked into ignored
`tmp/research-tools-qa037/extracted`; it does not run package maintainer scripts.
`strace --version` reported6.8 and local help confirmed the chosen flags.
Downloaded/extracted artifacts remain there, outside the system PATH.

Immediately before attachment, root read systemctl and `/proc/176` to require
active/running, no tracer, non-stopped process, expected executable SHA256 and
start_ticks164. A fresh output directory prevented overwrite/repeat. The exact
trace command, with absolute paths represented below by ROOT=`/mnt/d/research f1`:

```text
/usr/bin/timeout --signal=INT --kill-after=3s 45s ROOT/tmp/research-tools-qa037/extracted/usr/bin/strace -I 2 -p 176 -e trace=adjtimex,clock_adjtime,clock_settime,settimeofday -e signal=none -ttt -T -s 128 -o ROOT/output/runtime-raw/clock-writer-trace-20261012-qa037/clock-calls.log
```

One-shot private launcher `tmp/qa037_trace.py` applied a1MiB RLIMIT_FSIZE to its
tracer/timeout child outputs, not the service; recorded exclusive fsynced JSON
before/after; and checked identity/detachment in `finally`. Its SHA256 is in the
receipt. No `-f`, syscall injection, EXITKILL, seccomp filter, service stop or
restart was used. The timeout sent SIGINT to its own command process group;
service PID176 was an attached process, not a launched child. Exit124 is the
expected duration limit, not an unreported trial failure. Launcher exit0;
guest-monotonic elapsed45.018289348s. That duration is not independent physical
time, and ptrace overhead makes this unsuitable as an efficiency benchmark.

Stderr records one attach and one detach. Afterward, PID176/start_ticks164 and
the executable hash were unchanged, service active/running/enabled, TracerPid0,
process sleeping rather than stopped. A separate systemctl read confirmed the
service state again. These endpoint checks do not prove uninterrupted execution
or exclude external concurrent actors.

## Interpretation

Both decoded mode masks were
`ADJ_OFFSET|ADJ_MAXERROR|ADJ_ESTERROR|ADJ_STATUS|ADJ_TIMECONST|ADJ_NANO`;
both returned0/TIME_OK. No other selected syscall line was captured. Neither
mask contained ADJ_TICK, ADJ_FREQUENCY or ADJ_SETOFFSET. Absence applies only to
these observed calls, not all processes, threads, kernel paths or past activity.

Returned tick fields were10791 and9983microseconds; frequency fields -1763827
and -742349scaledppm; offset fields -58645962 and -44702767nanoseconds.
Critically, [strace6.8's decoder](https://raw.githubusercontent.com/strace/strace/v6.8/src/time.c)
prints the timex structure **at syscall exit**. These fields are not a preserved
entry buffer or proof that timesyncd requested those tick/frequency values.
The [Linux interface contract](https://man7.org/linux/man-pages/man2/adjtimex.2.html)
distinguishes selected modes from returned kernel state; offset discipline can
also influence frequency without an explicit ADJ_FREQUENCY request.

The tick-field difference needs further attribution. This process-only trace
does not observe Hyper-V/kernel writers, other processes/threads, or an exact
historical failure. No causal exclusion, accurate external clock reference,
successful full-window collection, detector improvement or stable-clock claim.
Original QA-035/036 negative evidence remains unchanged.

## Next decision

Do not repeat the sensor trial or relax gates. A separately scoped investigation
of the remaining clock-writing paths, or an explicitly approved controlled
synchronization comparison with reliable restoration, is needed before another
live qualification. This approval is consumed; it does not authorize disabling
NTP/Hyper-V, restarting WSL, kernel-wide tracing or another attachment. Real-data
training, independent supervisor/reviewer labels, held-out comparisons, novelty
and production acceptance remain separate pending milestones.

Verification commands and publication closure: WL-115 in [WORK_LOG](WORK_LOG.md).
