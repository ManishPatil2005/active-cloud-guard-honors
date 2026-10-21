# E1 preflight result — blocked before guest access

21 October 2026 · QA-054 / WL-131 · E2-005/E2-025/RQ3.

The user approved the exact, single-attempt E1 scope from
[QA-053](WRITER_INVENTORY_RESULT.md). The first required gate,
`wsl.exe --list --running`, returned `Access is denied` and
`Wsl/E_ACCESSDENIED`. The exit code was not captured. No guest command ran, so
there is no new evidence about whether the guest is running or whether the old
PID/executable identity still exists.

The attempt stopped at that gate. It did not read guest `/proc` or service
metadata, invoke `strace --version`, attach, or trace. There was no retry, clock
or service change, download, network action, sensor, or workload. The cause of
the Windows WSL access denial is unknown. The approved trace duration, signal
grace, output caps, syscall selection, and 120-second outer ceiling were not
changed or consumed by a trace.

Receipt: [minimized preflight record](../output/writer-trace-e1-preflight-20261021-qa054.json).
No private guest data was obtained. The prior QA-037 trace and QA-053 E0
inventory remain unchanged. This attempt establishes neither a current writer
identity nor clock cause, clock stability, coverage, or research acceptance.

## To resume

Restore WSL access in the intended execution context, then request a new
approval for a fresh, one-attempt E1 preflight/trace. The earlier approval was
for this single attempt and is consumed. The new attempt must recheck the exact
PID, start ticks, executable hash, service state and tracer compatibility; any
mismatch or access failure stops without PID substitution or retry. Do not infer
that fixing WSL access itself requires changing clock or service settings.
