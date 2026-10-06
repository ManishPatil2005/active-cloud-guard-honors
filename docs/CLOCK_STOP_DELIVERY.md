# Uncertain stop delivery and recovery cancellation (E2-030)

Later6October: [E2-031 inert guest fence](GUEST_FENCE_PROTOTYPE.md) implements isolated terminal admission/lock mechanics, with three actual inert Linux process cases. No systemd/native integration or complete job-drain proof; this page's610-test statements remain historical to E2-030.

## Status — 6 October 2026

**Partial safety milestone, software-tested only. Native comparison remains prohibited pending final safety design and specific approval.** We fixed premature recovery cancellation after an uncertain stop. We have not proved that a delayed guest request cannot arrive after the helper expires; this is not a complete guest-side fencing solution, clock fix or service-restoration validation.

Engine 1, the default Engine 2 path, the six native-observer files and all historical experimental receipts remain unchanged. No real time service was stopped/started, native clock observation performed, sensor workload launched or clock setting changed. Existing process integration tests are explicitly inert; service operations in this milestone's tests are simulated.

## Failure reproduced before the fix

Three deterministic controller regressions injected a delayed stop raising TimeoutError, ValueError or KeyboardInterrupt. The former controller attempted start, observed active/running/enabled, then disarmed the helper. All three new assertions failed before implementation (3 failed/62 deselected,0.38s). A delayed stop could still execute after that active snapshot. This is a reproduced **software-model flaw**, not an observed live WSL/systemd race. INC-043 preserves the negative test result.

## Changes and exact meaning

1. Controller records `stop_delivery_status=uncertain` before invoking stop. Only normal operation return advances it to `command_completed`. Error/interruption cancels all further measurements; cleanup still attempts start and reads state. If state is active but delivery remains uncertain, it reports `active_observed_stop_delivery_uncertain`, `operator_recovery_required=true`, `watchdog_status=not_disarmed`, and does not call disarm. Cleanup errors also require operator recovery.
2. Transport creates exclusive `stop-dispatch.json` containing the run nonce before sending the fixed blocking systemctl stop. After successful command return it creates exclusive `stop-ack.json`; only then clears its in-memory uncertainty. An error, interruption or acknowledgment-write failure leaves uncertainty. Failure to create the dispatch file sends no command. No marker is removed or overwritten, no new command/privilege introduced.
3. Both transport disarm and the normal helper check these markers. A pending dispatch forbids cancellation; malformed, mismatched or orphan acknowledgment refuses it too. The helper retains its one-shot deadline attempt instead of accepting an otherwise nonce-valid cancel. After a successful start/state observation with delivery still uncertain or invalid, it reports `active_observed_delivery_uncertain`, flags operator recovery and exits1. Inert mode does not read stop markers or call services.

Absent dispatch **and** acknowledgment means no recorded dispatch, not proof of an absence of outside writers. Valid matching markers are local parent-written continuity metadata, not authenticated systemd job receipts. `command_completed` is a transport contract result, not continuous service history. Existing successful blocking-command cases still require service-state checks and exact helper disarm/reap acknowledgment; stop failures remain conservatively uncertain even if they happened before actual dispatch.

The [systemd v255.4 manual](https://raw.githubusercontent.com/systemd/systemd-stable/v255.4/man/systemctl.xml) distinguishes blocking operation from `--no-block` enqueueing; this workflow does not request `--no-block`. [Python's subprocess documentation](https://docs.python.org/3/library/subprocess.html) bounds the local child on `run` timeout. **Inference:** neither an active service snapshot nor killing that local WSL client proves the guest request is quiesced. Documentation/source review is not attestation of the installed Ubuntu binary or actual WSL termination behavior.

## Verification performed

```powershell
.venv/Scripts/python.exe -m pytest -q tests/test_clock_comparison.py -k delayed_stop --basetemp=tmp/stop-delivery-negative-win-20261006-01 -o cache_dir=tmp/pytest-cache-20261006
```

Before-fix negative result:3failed/62deselected,0.38s. Initial post-fix targeted controller/transport run excluding real inert cases:93passed/2deselected,0.61s. After adding marker regressions:

```powershell
.venv/Scripts/python.exe -m pytest -q tests/test_clock_comparison.py tests/test_clock_comparison_transport.py -k 'not real_inert' --basetemp=tmp/stop-delivery-target-win-20261006-02 -o cache_dir=tmp/pytest-cache-20261006
.venv/Scripts/python.exe -m ruff check cloudguard scripts tests
.venv/Scripts/python.exe -m ruff format --check cloudguard scripts tests
.venv/Scripts/python.exe -m pip check
.venv/Scripts/python.exe -m pytest -q --basetemp=tmp/stop-delivery-full-win-20261006-01 -o cache_dir=tmp/pytest-cache-20261006 --junitxml=output/engine2-stop-delivery-windows-tests-20261006.xml
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python -m pytest -q --basetemp=tmp/stop-delivery-full-linux-20261006-01 -o cache_dir=/home/acgresearch/.cache/acg-pytest --junitxml=output/engine2-stop-delivery-linux-tests-20261006.xml
```

Targeted104passed/2deselected,0.63s; lint/format90files and pipcheck pass. Full Windows610passed/6.17s; Linux610passed/20.22s, each exit0. Full suites use approved host execution for WSL access and existing inert Windows breakaway tests. Two targeted deselections are included and pass in each full suite. [Windows XML](../output/engine2-stop-delivery-windows-tests-20261006.xml), [Linux XML](../output/engine2-stop-delivery-linux-tests-20261006.xml);14 additions, zero failures/errors/skips in both full reports. Earlier596 reports remain unchanged.

New cases cover three delayed controller errors, five helper marker states (pending/wrong/malformed/orphan/acknowledged), three transport errors, acknowledgment-write failure, dispatch-file failure and a shared pending marker after loss of the local uncertainty flag. Existing stop-error assertions were strengthened: uncertain stop no longer disarms, while a completed stop followed by collection failure still permits normal verified cleanup.

## Remaining gate and next step

The helper is still a finite one-shot recovery attempt, not persistent monitoring. A request delayed beyond its deadline can outlive it; host/WSL/process/power failure can defeat recovery. **Do not run the native batch just because these tests pass or a user approves a stop.** No claim of guaranteed restoration or verified job termination is made.

Next acceptance is a guest-side ordering/fencing design that rejects stale stop dispatch after recovery and handles already-submitted jobs without treating client death, PID absence, empty current job lists or active snapshots as sufficient proof. It needs deterministic queued-request/parent-death tests and inert integration before considering native use. Do not add retries, permanent service masks, kernel rate resets, Windows settings, WSL/Docker restarts or sensor workloads as a shortcut. Current fixed45s off-stage/60s helper operational budgets and one-batch proposal remain unchanged; final protocol/current prerequisite checks/explicit permission/native validation still open.
