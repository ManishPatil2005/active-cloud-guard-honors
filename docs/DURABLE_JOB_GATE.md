# Inert durable job gate (E2-034 follow-up)

## Status — 6 October 2026

Implemented and software-tested: `cloudguard/inert_job_gate.py` combines the existing guest lock/terminal seal with exclusive supplied-job evidence records. It is an **inert prototype**, not native service integration.60new tests, including four actual Linux file/lock/process cases, pass in the complete suites. INC-046 preserves a reproduced strict-boolean defect and its correction. No time-service/D-Bus/clock/sensor/model workload was run, and Engine1/previous sources/history are unchanged.

Acceptance: intent persisted before a simulation callback; reply/path and copied completion evidence retained in either arrival order; reconstructed results after reopening; interrupted/lost/replayed/malformed/non-success evidence never promoted; recovery seals before waiting, no duplicate effect after failure; native/quiescence/disarm authority always false. E2-034 remains partial because native submitted-job binding, real recovery integration and stale native request elimination are unfinished.

## Implementation and file meaning

InertJobGate initialization requires exact `inert=True`, validated nonce/declared epoch and a fresh exclusive directory. It reuses InertGuestFence initialization,60second admission deadline and Linux advisory lock, but **does not call its bare-True stop/recovery methods**. No CLI, subprocess, ctypes, bus/network/service command or privileged path is added to the library. Windows tests inject an inert lock; native locking remains Linux-only.

| File in an inert session | Meaning |
|---|---|
| request.json / session.lock | Existing inert request, deadline and shared cooperating-worker lock |
| job-context.json | Fixed new protocol/inert mode/nonce/selected unit/declared boot-bus-owner epoch/deadline |
| job-intent.json | Exclusive simulated-stop intent, saved before invoking callback |
| job-reply.json | Valid supplied returned job path; one reply only |
| event-01.json … event-32.json | Copied selected decoded events, contiguous bounded sequence; duplicates/overflow refused |
| window-complete.json | Callback returned exactTrue without a writer fault; supplied continuity marker, not broker proof |
| fault.json | Sticky evidence/storage-fault presence; never removed/reset or overwritten |
| sealed.json | Existing terminal seal, published before recovery waits for operation lock |
| job-recovery-intent.json / job-recovery.json | Exclusive recovery attempt before callback, then separate successful simulation report |

All new journal records bind nonce and declared epoch. Existing exclusive UTF-8 JSON creation/flush/file-fsync and4096byte duplicate-rejecting reads are reused; no record is overwritten. Request/context deadline binding rechecked on replay; event/reply/window/recovery envelopes and selected schemas validated. Unknown/legacy entries, gaps, orphans, wrong nonce/epoch/unit, malformed records, wrong exact booleans and nonregular/symlink journal artifacts reject consistency. File-count/schema/copy bounds are not a hostile-filesystem sandbox.

Stop owns the shared lock for the complete supplied simulation. A scope-bound writer records reply/events, supports fast completion before reply, checks declared epoch and latches supplied disconnection. Exceptions—including KeyboardInterrupt/SystemExit at the callback boundary—retain intent and prevent a completion-window record. If a callback catches a writer error and returnsTrue anyway, the writer fault still rejects completion. Retaining the writer does not authorize post-scope writes. Subsequent stop attempts refuse the existing intent before another callback.

Replay reconstructs JobEvidence from records; it never guesses a job path from unit/time/PID/active state. A normal callback returningTrue is not enough: missing reply/event, unrelated completion, missing final window or any fault remains unknown. A matching done becomes **simulated_tracked_job_done**; canceled/skipped/failed/timeout becomes **simulated_job_not_successful**, not safe cancellation. No-event/no-intent becomes **not_dispatched** only within this trusted inert record model; it does not exclude external jobs.

`inspect` takes the shared lock and **may write a sticky fault marker on invalid evidence**; it is not a non-mutating reader. Validation errors remain unknown even when the original epoch is later supplied or a new object reopens the session. `_poison` attempts exclusive minimal fault storage without replacing the original exception. If storage itself cannot write that marker, durable publication of the latch cannot be guaranteed; incomplete intent/window and in-process invalidity still deny success in tested stop failures. Do not repair/remove evidence to make a session usable again.

Recovery publishes the terminal seal before waiting for the lock. Timeout therefore closes admission without racing the lock holder. Once acquired, an exclusive recovery intent precedes the simulation callback, preventing its repetition after either success or failure. It reports reconstructed stop-evidence consistency separately from `simulated_recovery_observed`; observing a successful simulation never repairs unknown stop evidence. Every report keeps operator_recovery_required=True and native_binding_verified/service_quiesced_verified/may_disarm_recovery=False, including matching done or no prior dispatch. No report is permission to cancel a real watchdog.

## Actual inert process checks and limits

Four Linux-only cases run ordinary-user children on Linux-local temporary directories, not production/shared-checkout locks:

- Three interruption stages: exclusive intent only, supplied reply recorded, and reply plus supplied done event recorded. The holder waits inside its simulation; another child queues a stop. Parent recovery times out after sealing, then explicitly kills/reaps the fixture holder. Recovery retains unknown—even with reply/done present, because no completed window. Queued worker rejects on seal; no late-effect file appears.
- One completed child writes fast supplied event before reply and finishes the window. Parent reconstructs matching simulated evidence and seals recovery; all native authority remains false.

Children use close_fds, no stdin/stdout/stderr/private service text retained, bounded marker waits/parent cleanup, no descendants. These tests prove selected cooperating lock/record/death mechanics, **not actual job enqueue/drain**, inherited-fd malicious bypass, native restoration, shutdown/power failure or real D-Bus disconnect. Simulation callbacks are trusted Python, not forcibly time-bounded or sandboxed; never pass systemctl/native actions to them. Local storage/OS/caller identity is trusted; record authenticity, root protection, directory fsync/inode replacement/races, mount/network filesystem, cross-boot/native epoch acquisition and privilege separation are unresolved. Fsync here means files were flushed, not crash-consistent whole-session durability. Guest timers/clocks remain under investigation.

This library imports only guest_fence and systemd_job. Existing receiver/clock/controller/transport/helper/default-engine sources and the23-file comparison freeze remain unchanged. It is not wired into the currently unfenced native service path. The previous one-attempt receiver observation is not rerun and its zero-event result remains unchanged. See [original fence boundaries](GUEST_FENCE_PROTOTYPE.md), [job contract](SYSTEMD_JOB_CONTRACT.md), [native callback tests](NATIVE_CALLBACK_VALIDATION.md).

## Defect preserved and exact verification

Initial targeted Windows run:51pass/4Linux-only skips/2.11s. During schema review, a new regression changed `continuous: true` to integer1 in a valid fixture window. Before fix:1failed/59deselected/0.58s, saved [negative XML](../output/engine2-durable-job-window-regression-20261006.xml), suite0.323s. Python dict equality treats1equal toTrue; fix requires exact value schema and `is True`. INC-046; no real service/production authority was exercised, all native flags were false even in the faulty inert status. Failure evidence is not replaced.

After fix and additional binding/duplicate/false-ack regressions: targeted Windows56pass/4skips/2.12s, Linux60pass/9.45s. Full [Windows XML](../output/engine2-durable-job-windows-tests-20261006.xml):851collected,814pass/37Linux-only skips,0failures/errors, console8.39s/XML8.388s. Full [Linux XML](../output/engine2-durable-job-linux-tests-20261006.xml):851pass/0failures/errors/skips, console31.81s/XML29.832s. Durations are software-suite timing, not engine latency/clock accuracy; console/XML difference undiagnosed. Ruff lint/format102files, pip check and working whitespace pass. Existing inert breakaway tests/WSL used approved host execution. Prior native callback/full suites and historical receipts are preserved.

Executed at project root with existing environments:

```powershell
.venv/Scripts/python.exe -m ruff format cloudguard/inert_job_gate.py tests/test_inert_job_gate.py
.venv/Scripts/python.exe -m pytest -q tests/test_inert_job_gate.py --basetemp=tmp/durable-job-target-win-20261006-01 -o cache_dir=tmp/pytest-cache-20261006
.venv/Scripts/python.exe -m pytest -q tests/test_inert_job_gate.py -k integer_window_acknowledgment --basetemp=tmp/durable-job-bool-regression-win-20261006-01 -o cache_dir=tmp/pytest-cache-20261006 --junitxml=output/engine2-durable-job-window-regression-20261006.xml
.venv/Scripts/python.exe -m pytest -q tests/test_inert_job_gate.py --basetemp=tmp/durable-job-target-win-20261006-02 -o cache_dir=tmp/pytest-cache-20261006
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python -m pytest -q tests/test_inert_job_gate.py --basetemp=tmp/durable-job-target-linux-20261006-01 -o cache_dir=/home/acgresearch/.cache/acg-pytest
.venv/Scripts/python.exe -m pytest -q --basetemp=tmp/durable-job-full-win-20261006-01 -o cache_dir=tmp/pytest-cache-20261006 --junitxml=output/engine2-durable-job-windows-tests-20261006.xml
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python -m pytest -q --basetemp=tmp/durable-job-full-linux-20261006-01 -o cache_dir=/home/acgresearch/.cache/acg-pytest --junitxml=output/engine2-durable-job-linux-tests-20261006.xml
.venv/Scripts/python.exe -m ruff check cloudguard scripts tests
.venv/Scripts/python.exe -m ruff format --check cloudguard scripts tests
.venv/Scripts/python.exe -m pip check
git diff --check
```

The -k command is the recorded before-fix execution, not an expected current failure. Reproduction must use fresh temp/report names, never overwrite the retained failed/passing XML or historical live folder. Publication/staged review/commit/remote receipt is separate in WL-056. ADR-046 explains why the native path remains blocked.

Publication review: unrestricted `git diff --cached --check` reported trailing whitespace on line12of the generated negative XML (`E` traceback blank line). Preserve those original failure bytes instead of sanitizing the receipt or relaxing source rules. Executed `git diff --cached --check -- . ':(exclude)output/engine2-durable-job-window-regression-20261006.xml'` passed for every other staged file. Raw negative SHA256 b6434bb5ca1e8831020d84ff003d25430c558a831cab5899066f51bcf3b77f76; `git hash-object --no-filters` equals staged blob3c7c6ff8b361f6b63419d3e9d91198c93a096fb0. No artifact-byte or .gitattributes change. This is a documented raw-report whitespace exception, not a passing unrestricted staged whitespace check or suppression of the actual regression.

## Next gate

Design the concrete native guest job-owner/recovery protocol and test it inertly against lost submission replies, crash after enqueue, epoch/stream loss, delayed queued requests and all admission paths. Reusing this journal with unverified callbacks is not native binding; old unfenced dispatch must be eliminated before native use. Add source/boot/storage/privilege controls and an independently supervised recovery design that cannot infer quiescence from active/empty-job snapshots. Actual native service validation requires finalized protocol/current preflight and fresh explicit human intervention consent; generic proceed does not authorize stopping clocks/services. Timing stability, ML, independent labels and research evaluation remain open; no production/publication-ready claim.
