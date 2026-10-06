# Persistent read-only systemd receiver (E2-033)

Later E2-034 checkpoint: [private native callback validation](NATIVE_CALLBACK_VALIDATION.md) executes28actual pinned-library message/reader/C-trampoline cases with synthetic data plus3portable guards. No broker routing/real jobs; no production-source change or receiver bug observed. This extends callback software evidence, not real delivery/job binding; original milestone statements below remain historical. Prior real setup/cleanup observation remains separately documented in SYSTEMD_RECEIVER_CAPTURE.md.

Later implementation checkpoint: [exclusive launcher and one-attempt protocol](SYSTEMD_RECEIVER_CAPTURE.md) adds durable start/outcome storage, parent/native child deadlines and selected validation. Native observation pending at that publication checkpoint; statements below remain the original receiver milestone, not retroactively executed evidence. The isolated receiver now retains bounded numeric errno on native OSError observation failures, with no raw error message.

## Status — 6 October 2026

The isolated native adapter is **implemented and software-tested**, not yet live receive-validated or connected to the service controller. Actual installed library identity/ABI/export availability was checked without opening a connection. No native `Subscribe`, `Unsubscribe`, job submission/cancellation or service control was executed in this milestone. Engine1, the comparison runner, inert guest fence, native clock observers and historical receipts remain unchanged.

Acceptance for this implementation checkpoint: persistent fixed-address ordinary-user connection, typed nonvariadic API, acknowledged selected matches/subscription before observation, selected envelope/reply validation, bounded buffering/pumping, sticky unknown on identity/stream faults, cleanup and no service-control method. Live validation is a separate gate. This is safety instrumentation for Engine2's unresolved timing investigation, not anomaly-model progress or a clock fix.

## Choice and reviewed native environment

Read-only availability check found no `dbus_next` or Python `dbus` module; installed `libsystemd.so.0` exists. Rather than install a package or hand-code D-Bus wire messages, use Python stdlib `ctypes` with a small fixed sd-bus binding. Native FFI adds ABI/lifetime risk and review burden; it is not a security sandbox or evidence that Python memory-safety applies inside C. ADR-043.

Actual ordinary-user ACG-Research reads:

- `libsystemd0` reports `255.4-1ubuntu8.17`.
- Reviewed path resolves to `/usr/lib/x86_64-linux-gnu/libsystemd.so.0.38.0`.
- SHA256 `bdf59c828b547bcdbe7b3576c0810d9d9d2e982d8b61b365812542da6a4c4a99`.
- Linux x86_64, little-endian LP64 (pointer/long8bytes), glibc2.39, UID1000; fixed system-bus path is a socket.
- `_backend()` and `_bind(ctypes.CDLL(...))` succeeded for the selected symbols only. No connection opened or method invoked by that check.

These are current local observations, not a signed build attestation or proof of service readiness. Production refuses root, unsupported ABI/libc/platform and any library hash change; a package update needs fresh review, not fallback. Loading uses the resolved fixed library, never a user/model-selected name. Trusted local OS/library/socket are assumed; same-host hostile filesystem replacement and in-memory/binary attestation remain outside this prototype.

## Primary API review

The [tagged v255.4 header](https://raw.githubusercontent.com/systemd/systemd-stable/v255.4/src/systemd/sd-bus.h) supplies exact opaque-pointer/integer/function-pointer declarations. No variadic `call_method`, `read` or `append` is bound; messages are constructed with fixed fields and `append_basic`, then passed to typed `sd_bus_call`. Setter declarations are not service-control operations.

The [match manual](https://raw.githubusercontent.com/systemd/systemd-stable/v255.4/man/sd_bus_add_match.xml) establishes synchronous broker acknowledgement for `sd_bus_add_match` on a bus-client connection. Callbacks borrow messages: our callback never unrefs that message, copies selected basic values, retains the C callback objects until connection closure, and catches Python exceptions before returning through C.

The [append-basic manual](https://raw.githubusercontent.com/systemd/systemd-stable/v255.4/man/sd_bus_message_append_basic.xml) distinguishes a string argument's `char[]` from a pointer-to-pointer. The [read-basic manual](https://raw.githubusercontent.com/systemd/systemd-stable/v255.4/man/sd_bus_message_read_basic.xml) requires `const char **` for returned strings and `uint32_t *` for unsigned IDs; borrowed strings are copied while the message is valid. Tests explicitly exercise these different pointer shapes.

The [call manual](https://raw.githubusercontent.com/systemd/systemd-stable/v255.4/man/sd_bus_call.xml) describes call/reply error and timeout handling. Our caller checks method-return type, expected sender, complete signature, nonzero request cookie/exact reply cookie and argument exhaustion before accepting the reply. Reviewed upstream APIs do not prove installed binary behavior; runtime exports only establish availability. Initial rendered-manual URLs were inaccessible, so the review used official version-tagged XML/header files instead.

## What the code does

`cloudguard/systemd_receiver.py` is separate from `systemd_job.py` and `guest_fence.py`; nothing imports it from the default engines/controller. Public `observe()` always constructs the native backend, with no fake-mode fallback. It is Linux-only; Windows can run the tests, not collect native bus evidence.

1. Hash the receiver, job validator and package initializer. Check fixed reviewed backend/library.
2. Create a bus client at `unix:path=/run/dbus/system_bus_socket`; ignore environment-selected session/system addresses. Disable interactive authorization, disconnect-triggered process exit and message auto-activation; set one-second method timeout.
3. Read boot-ID hash, broker `GetId` and `GetNameOwner(org.freedesktop.systemd1)` on that connection. Validate the epoch. The manager's unique owner is used as destination/sender, not nearest-time/PID/name-only association.
4. Install synchronous matches for selected manager `NameOwnerChanged`, local disconnection, and exact manager path/interface/JobRemoved/selected timesyncd unit. Validate type, sender, path, interface, member, `uoss` signature, bounded copied fields and argument exhaustion for selected job notifications.
5. Request `Subscribe` on the same connection and recheck epoch/readiness before pumping. This is a transient request for notification delivery, not a start/stop/disable or clock setting change. Broker AddMatch/subscription change connection-local notification state; "read-only" here refers to service/job/clock state, not zero bus traffic/state.
6. Pump for five nominal `time.monotonic()` seconds, at most512process calls, with waits at most100000usec and at most32distinct selected events. Duplicate/malformed/overflow, owner change, disconnect, failed call/wait, interruption, identity change or callback error rejects the observation. No retry or replacement observation.
7. Recheck epoch/readiness, acknowledge `Unsubscribe`, close slots/connection, compare source/library file hashes. Connection closure also drops subscription when explicit unsubscribe was not acknowledged. The report distinguishes subscription release acknowledgement from connection close.

Internal method allowlist is exactly `GetId`, `GetNameOwner`, `Subscribe`, `Unsubscribe`. StopUnit/StartUnit/CancelJob/SetTime/Reload are refused before message creation. No subprocess, privilege escalation, sensor/model/workload or service-state property setter is used.

## Result meaning and limits

Report `status=observed` means only the listed receiver checks passed. `continuity_checks_passed` is not loss-free coverage, authenticity against a hostile host, long-term continuity or timing stability. Zero events means no selected completion was delivered to this diagnostic; it is **not** proof of no jobs, safe service state or a clean verdict. Setup/final-call queues can contain notifications outside the nominal pump window, and message timestamps are not used to make a causal temporal association. Do not count these as independent runtime detection data.

There is no submitted/tracked job, so even a native received `done` would not prove our own stop completed. `native_binding_verified`, `service_quiesced_verified`, `may_disarm_recovery`, `jobs_submitted_or_canceled` and `services_modified` stay false. `unknown` reports retain selected partial events and exception class/stage, not raw messages, error text, unrelated units or packet captures. Backend-construction/source-prefreeze failures raise before a report exists; caller must record the failed attempt, not silently retry.

Bounds cover Python pump iterations, selected copies, wait slices and sd-bus method timeout. They are **not** a hard process deadline for socket setup, library calls, disk IO or hostile/unbounded broker message allocation. The underlying adjusted monotonic clock is already under investigation. A separately supervised outer timeout and exclusive receipt launcher are required for the upcoming observation. ctypes crashes/native allocation failures cannot be reliably converted into Python cleanup evidence. No future monitor/background daemon is started.

No durable job intent/reply/completion storage, cross-worker fencing, death-after-enqueue resolution, privilege-separated control path, real disconnect/owner-replacement observation or recovery proof yet. The23-file comparison freeze is unchanged because the new isolated module is not integrated; expand it if/when that integration is implemented. E2-030, E2-032 and E2-033 remain partial safety gates; explicit stop consent, final intervention protocol/current preflight/restoration validation and timing/ML/independent evaluation remain open.

## Executed tests and reproduction

From the repository root, using the existing environments:

```powershell
.venv/Scripts/python.exe -m ruff check cloudguard scripts tests
.venv/Scripts/python.exe -m ruff format --check cloudguard scripts tests
.venv/Scripts/python.exe -m pip check
.venv/Scripts/python.exe -m pytest -q tests/test_systemd_receiver.py --basetemp=tmp/systemd-receive-target-win-20261006-03 -o cache_dir=tmp/pytest-cache-20261006
.venv/Scripts/python.exe -m pytest -q --basetemp=tmp/systemd-receive-full-win-20261006-01 -o cache_dir=tmp/pytest-cache-20261006 --junitxml=output/engine2-systemd-receiver-windows-tests-20261006.xml
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python -m pytest -q --basetemp=tmp/systemd-receive-full-linux-20261006-01 -o cache_dir=/home/acgresearch/.cache/acg-pytest --junitxml=output/engine2-systemd-receiver-linux-tests-20261006.xml
```

Use fresh temporary/report names when reproducing; do not overwrite these historical XML receipts. Lint/format96files/pipcheck pass. Final targeted54pass/0.07s. [Windows XML](../output/engine2-systemd-receiver-windows-tests-20261006.xml):726collected,723passed/3existing Linux-only skips, suite time6.452s (pytest console6.46s). [Linux XML](../output/engine2-systemd-receiver-linux-tests-20261006.xml):726passed, suite time21.216s (pytest console24.34s), zero failures/errors/skips. These two timing fields are reported separately; their difference was not diagnosed. Full suites used approved host execution for existing inert process tests/WSL. The54new tests use supplied C-level fixtures/synthetic events and fake operations, **no native connection**; existing actual process tests are explicitly inert.

Cases cover finite empty/event observation, setup/final epoch replacement, match/subscription/wait/callback/interruption/close failure, processing flood, bounded copied/replayed/malformed events, typed reply cookies/types/senders/signatures/exhaustion, string pointer shapes, callback ownership/lifetime, fixed constructor address/settings, root/changed-library/platform refusal and no silent simulation. INC-044 preserves the actual intermediate53pass/1failure due to a Windows test double's LLP64 C-long width. Correcting that fixture did not weaken the production LP64 guard. An earlier49-case subset passed before the five backend/constructor additions.

Read-only actual symbol check (no connection/method calls):

```powershell
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python -c "from cloudguard import systemd_receiver as r; import ctypes,json; m=r._backend(); r._bind(ctypes.CDLL(m['library_path'])); print(json.dumps({'metadata':m,'selected_symbols_bound':True,'connection_opened':False,'subscription_invoked':False,'jobs_controlled':False}))"
```

This succeeded with the metadata above. Export binding does not execute those exported functions or validate their callback behavior. No native live receipt is claimed. Publication/staged/commit/remote verification is recorded in WL-051 separately.

## Next step

First add an exclusive, failure-preserving receipt launcher and supervised process timeout, then declare and execute exactly one five-second read-only receiver observation after implementation publication. Never trigger a timesyncd job just to make an event appear. Preserve a zero-event/unknown/failure result without retry. Only after native connection/subscription/cleanup validation should durable guest-gate/job binding be considered; it requires additional design/tests, not direct wiring into the existing unfenced service path. A new real service intervention still requires explicit human approval and a finalized recovery protocol.
