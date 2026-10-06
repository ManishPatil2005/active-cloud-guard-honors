# Inert guest-side session fence (E2-031)

Later6October: [E2-032 systemd evidence contract](SYSTEMD_JOB_CONTRACT.md) adds source/actual read-only schema review and isolated decoded-event matching tests. Not connected to this fence or native service calls; guest job-binding safety still open. Historical643-test statements below remain checkpoint-specific.

## Status — 6 October 2026

Implemented and software-tested as an **isolated inert prototype**, not connected to the native comparison transport/helper. No real time service, clock setting, Docker or sensor command was selected. Engine 1, the existing comparison sources/native observer and historical receipts are unchanged. E2-030's native safety gate is still partial: this establishes admission/serialization mechanics for cooperating prototype workers, not elimination of already-submitted systemd jobs.

Acceptance: permanently close a session before recovery waits on its operation lock; reject late/duplicate/expired simulated stops; retain uncertainty after interruption/worker death; prove selected process mechanics with real Linux locks and inert processes; preserve a negative detached-job boundary. Do not add service commands or declare native execution safe.

## Implementation and meaning

`cloudguard/guest_fence.py` contains `InertGuestFence`. Initialization requires exact `inert=True`, an exclusive session directory, strict64hex nonce and fixed60s admission deadline. Reopening a session checks exact inert protocol/mode/request schema; native/restore mode is refused. There is no CLI, subprocess launch, service adapter or privileged path in this module. Its trusted caller supplies **simulation callbacks**; this is not a sandbox preventing a malicious Python caller from supplying a real action.

Stop holds an independently opened guest file lock while recording exclusive intent, checking terminal seal/deadline, running the simulation and writing exclusive completion. Recovery publishes `sealed.json` **before** waiting for that lock. A late cooperating worker that obtains the lock afterward sees the permanent seal and refuses dispatch. A seal that becomes visible after the holder's check does not revoke an operation already entering its callback; recovery waits rather than racing that holder. Stop duplicates fail at intent creation before callback; recovery duplicates fail before repeating a recovery callback. Failed effect acknowledgment preserves intent, not an invented successful completion. A lock-acquisition timeout leaves the session sealed and executes no recovery callback; callbacks themselves are not forcibly bounded by this library.

Linux locking uses `fcntl.flock(LOCK_EX|LOCK_NB)`, <=5s operational acquisition budget, independent opens, `O_NOFOLLOW|O_CLOEXEC`, and descriptor close on exit. It requires Linux; Windows unit cases inject a simulated lock instead. Small JSON reads are bounded4096bytes and duplicate keys refused. Records use exclusive creation/flush/fsync; no overwrites or deletion of the terminal seal. File fsync does not certify directory durability, host power-loss recovery, malicious filesystem behavior or clock accuracy.

If intent has no valid matching completion, recovery can observe a successful simulation but reports `submitted_stop_quiescence_known=false` and `operator_recovery_required=true`. A valid completion means the **simulation callback returned True**; it is not authenticated systemd job termination. An orphan/corrupt completion stays unknown. `native_service_validated` is always false. The detached-job test deliberately applies a simulated outside effect after recovery to show this fence cannot cancel a job beyond its cooperating lock.

[Python's fcntl documentation](https://docs.python.org/3/library/fcntl.html) describes its Unix interface; the [Linux flock manual](https://man7.org/linux/man-pages/man2/flock.2.html) describes advisory locking and shared open-file-description lifetime. **Inference/design limit:** all actual service dispatch paths must eventually cooperate with the same guest-local gate, and inherited descriptors/untracked submitted jobs must be handled separately. These references do not attest the prototype directory, mounted filesystem or native service behavior. Sessions assume trusted local directories; inode replacement, symlinked records, hostile writers, cross-boot identity and shared/network filesystem behavior are not hardened here.

## Executed tests

Thirty-three new cases: strict inert initialization/timeout/request refusals; terminal/expired/duplicate stops; failed recovery/duplicate effects; corrupt completion; unknown interrupted intent; detached-job limitation; native lock platform refusal; three actual Linux lock/process cases. The latter use Linux temporary directories and inert file markers only, not the shared-checkout lock or services; no filesystem type/production lock guarantee is claimed.

Actual Linux cases:

1. Lock holder remains alive: recovery times out after sealing; a second queued worker subsequently refuses its simulated stop, with no late effect marker.
2. Holder killed during simulation: close releases the participating lock; recovery observes incomplete intent and explicitly retains uncertainty. No job-drain inference from process death.
3. Completed inert child: completion metadata is readable across processes and subsequent recovery seals the session; still no native-service proof.

Initial Windows targeted25passed/2skipped,0.27s; after adding request checks and completed Linux case, Windows29passed/3skipped,0.36s and Linux32passed/1.57s. Then the detached-job boundary case was added before final full suites. During code review, duplicate recovery could have repeated its simulation before result-file refusal; an exclusive recovery-intent marker and pre-callback result check fixed this, and tests now forbid repeated callbacks after success/failure. A patch initially placed the result check in stop due to an ambiguous context; inspected and moved before validation. No failed test or native incident is fabricated from that edit.

```powershell
.venv/Scripts/python.exe -m ruff check cloudguard scripts tests
.venv/Scripts/python.exe -m ruff format --check cloudguard scripts tests
.venv/Scripts/python.exe -m pip check
.venv/Scripts/python.exe -m pytest -q --basetemp=tmp/guest-fence-full-win-20261006-01 -o cache_dir=tmp/pytest-cache-20261006 --junitxml=output/engine2-guest-fence-windows-tests-20261006.xml
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python -m pytest -q --basetemp=tmp/guest-fence-full-linux-20261006-01 -o cache_dir=/home/acgresearch/.cache/acg-pytest --junitxml=output/engine2-guest-fence-linux-tests-20261006.xml
```

Lint/format92files and dependency checks pass. [Windows XML](../output/engine2-guest-fence-windows-tests-20261006.xml):643collected,640passed/3skipped,6.41s, zero failures/errors; the three real flock integration cases are explicitly Linux-only. [Linux XML](../output/engine2-guest-fence-linux-tests-20261006.xml):643passed/22.74s, zero failures/errors/skips. Approved host execution allowed existing inert breakaway tests and WSL access; no real service operation. Earlier610 reports remain untouched. Staged/publication/commit/remote verification is separate in WL-049.

## Next required step, not a live-run instruction

Review a concrete systemd job-identity/completion binding and how every stop/restoration request would enter a trusted guest-local gate. Eliminate the old unfenced direct-dispatch path before any native use; expand its source freeze only when integration exists. Test lost submission replies, worker death after job enqueue, inherited descriptors and recovery timeout without treating active/PID-absent/empty-job snapshots as drain proof. Native binding, directory/boot/source/privilege hardening, final protocol/current preflight, specific human approval and real restoration validation remain open. Do not connect simulation callbacks to systemctl now or run the existing native batch.
