# Comparison controller contract and offline reviewer (E2-027)

This page records the5October controller milestone. [6October transport/helper follow-up](CLOCK_COMPARISON_TRANSPORT.md) implements the previously absent backend and limited inert process integration; native service intervention remains unapproved/unexecuted. Historical test/results statements below remain checkpoint-specific.

## Current milestone — not a live launcher

Implements the fail-stop decision logic from [writer review](SYNC_WRITER_REVIEW.md), plus offline comparison of three complete E2-025-format receipts. Engine 1, existing native observer and all historical experiment sources/receipts remain unchanged. No live service command, clock reading, native backend, real watchdog process, sensor or workload was run or added by this milestone.

`cloudguard/clock_comparison.py` is a dependency-injected controller. Its operations are simulated in tests; there is **no concrete service transport or watchdog launcher**. `scripts/clock_comparison_review.py` is offline-only and cannot stop/start services. A future transport still needs implementation, bounded command/process integration tests, specific human approval and a finalized published one-attempt protocol before execution. Software acceptance here is not intervention or clock-stability acceptance.

## Controller behavior tested

- Requires `approved is True` before any operation. This is an API refusal guard, not authenticated proof of human approval; the operator must obtain it separately.
- Requires original active/running/enabled service, known sensors absent and lab ready; freezes exactly eight allowlisted execution-source hashes, detaching the returned dictionary to detect later in-place changes.
- Before/stopped/restored labels only, at most three collection calls. Each complete block passes the unchanged native observer's full offline review; receipt six-source hashes must match the larger controller freeze.
- Requires an acknowledged **independent restore watchdog** before requesting service stop. The contract specifies60s watchdog deadline and a45s off-stage budget on the controller's monotonic clock. Each injected operation receives a bounded remaining timeout (normally <=5s, collection <=45s).
- Marks stop *attempted before the call*, so a command that changes state and then errors still enters cleanup. First failure/KeyboardInterrupt cancels later measurement, not cleanup.
- Cleanup requests service start after any stop attempt and verifies active/running/enabled. Disarm/reap acknowledgement is required only after active verification. Failed restoration leaves the watchdog undisarmed; failed disarm prevents restored measurement. Restored collection happens only after successful cleanup.
- Preserves phase, per-block stage/status, attempted/completed/failed operations, bounded receipt SHA before parsing, safe error classes, and cleanup status. No raw reply, exception message or service command output in controller report. Synthetic tests assert private sentinel messages absent.

**Boundaries:** Python cannot enforce a timeout on an injected operation that ignores it. The45s budget is checked between calls; the future transport must actually enforce command/child deadlines and persist exclusive raw/partial receipts. An acknowledged simulated watchdog is not a running independent process. Controller kill, host sleep/power loss, WSL failure or a failed restore can defeat recovery even with a future helper. Future source freeze must include any added transport/watchdog dependencies; the current eight-file list is not permission to omit future code. The real off-stage/watchdog/restoration safety gate remains open.

Kernel tick/frequency are never reset. Underlying receipt `clock_settings_modified=false` describes that read-only child, not an enclosing intervention; the controller separately reports `environment_service_stop_attempted`. Do not call guest-client removal “single authority.”

## Offline comparison and limits

Reviewer accepts bounded <=100000-byte inputs, uses strict native receipt parser/full source/backend/domain/bounds/state/summary re-reduction, then requires three distinct receipt digests, identical backend/source identities and ordered same-domain native endpoints across blocks. Refuses recycled receipt, wrong order, namespace/backend/source change, stale or float/bool summaries and invalid native state. Output creation is exclusive, never overwrites evidence.

The comparison reports per-block final native intervals and sampled state sets, not a fitted rate correction or general overhead/accuracy score. Labels are operator-supplied: offline receipt review **does not verify or authenticate service history**. `stable_clock_accepted=false`, `causal_attribution=not_proven`, `independent_evaluation=false` remain explicit. No real comparison result exists yet; tests use synthetic receipts.

Only after a separately authorized batch produces three compatible receipts, run this template (not executed here):

```powershell
.venv\Scripts\python.exe scripts/clock_comparison_review.py --before PATH_TO_BEFORE.json --stopped PATH_TO_STOPPED.json --restored PATH_TO_RESTORED.json --output NEW_COMPARISON.json
```

Do not copy one old receipt into three files or infer stopped-service evidence from filenames. Existing E2-025 single receipt remains an independent diagnostic, not this proposed batch.

## Observed software checks, 5 October

Targeted suite initially41 passed/0.35s; expanded47 passed/0.35s and after tightening the eight-source freeze47/0.38s. Tests include complete simulated sequence, strict approval/no operations, preflight/watchdog/source refusals, ValueError and KeyboardInterrupt across seven stages, stop-side-effect-then-error cleanup, failed start/inactive-after-start, failed disarm, exhausted off-stage budget, malformed/oversized receipt digest retention, full three-block identity/order/math checks and exclusive offline output. No real subprocess/native/service backend invoked in these cases.

Full checks:551 Windows/4.90s and Linux/9.59s, lint/format86files/dependency/working whitespace pass. [Windows receipt](../output/engine2-comparison-controller-windows-tests-20261005.xml), [Linux receipt](../output/engine2-comparison-controller-linux-tests-20261005.xml). Full suites include existing engine regressions, not a rerun of live model/sensor experiments. All historical sources unchanged; exact commands in WORK_LOG. Scheduling, process-kill, transport and independent-watchdog integration remain untested/unimplemented; no production safety or publication-ready effectiveness claim.

## Next gate

Get explicit permission for a one-batch before/stopped/restored comparison that briefly stops only ACG-Research systemd-timesyncd and restores/verifies it. No Windows/persistent-disable/kernel-reset/WSL/Docker lifecycle changes or sensor workloads. Before action, implement/test a concrete transport and independent restore helper, finalize counts/paths/source freeze/timeouts/cleanup protocol, commit/push/verify, and only then execute the specifically approved batch once. A generic “continue” is not inferred as permission to change synchronization state.
