# Private native callback validation (E2-034)

Later follow-up: [inert durable job gate](DURABLE_JOB_GATE.md) combines existing decoded-event evidence with exclusive journal/guest lock/terminal seal,60additional tests/four actual inert Linux process cases; Linux851pass/Windows814pass37Linux-only skips. This native fixture/helper is unchanged, no real broker jobs or native control integration. INC-046 applies to the new inert journal schema, not a receiver-native bug; original results below remain historical.

## Status — 6 October 2026

The callback decoding/lifetime/fault prerequisite is **implemented and software-tested with the actual pinned Linux library and synthetic messages**. It is not broker-delivered JobRemoved evidence, an independent benchmark or durable job/fence integration. E2-034 remains partial. Engine1, production sources, the receiver capture launcher, comparison source list, native clock observers and historical evidence are unchanged.

Acceptance: construct native messages without a real broker/service job; invoke the existing receiver's C callback trampoline; check copied values after fixture-owner message release, strict selected envelopes/body/cursor handling, bounded replay/overflow, continuity faults, contained consumer exceptions and cleanup. Reject non-reader operations in the test proxy. Run relevant checks and both full suites, preserving new reports separately.

## How the fixture works

`scripts/systemd_native_fixture.py` is a test-only helper, not a new engine or public service-control command. `tests/test_systemd_native_fixture.py` runs each of28fixed native cases in a separate ordinary-user Linux child. Three additional portable checks cover the fixture's direct native call surface, proxy refusal and unknown-case rejection before backend access.

1. Reuse the production ABI/ordinary-user/library-hash guard. This stats the fixed system-bus socket but does not connect it. Load the resolved reviewed library; no installation or dynamic user-selected library.
2. Allocate an unnamed AF_UNIX stream socketpair. Transfer one FD to a new sd-bus object, keep the peer local, start the private connection. Assert open but **not ready**: no completed peer authentication, broker or named socket. Starting may send authentication bytes to the private peer; this is not zero local IO.
3. Allocate `_NativeBus` without running its real-system-bus constructor. Use a test proxy: intercept AddMatch and retain rule text only, leaving native slot output NULL. Forward only selected real getters/readers/unref-close operations; refuse call/send/process/flush/address/open operations. Actual broker AddMatch acknowledgement, selection and routing are therefore **not tested** here.
4. Call the production `install` to retain its CFUNCTYPE callbacks; collect Python garbage before retrieving the retained callback. Construct typed native signal (or wrong-type method-call) objects with reviewed nonvariadic APIs, append basic values, optionally seal/rewind. All identity/header/unit/job/result values are synthetic, including the selected timesyncd name.
5. Invoke the retained production callback directly through the ctypes C trampoline, not through `sd_bus_process` or a broker. Real libsystemd getters and basic-body reads execute. Check return1, bus fault and receive-state invalid latches. A later valid message cannot clear a recorded fault.
6. Before the fixture owner unrefs each message, a native member getter still succeeds: the callback did not release its borrowed message in these cases. After all owner releases and Python GC, retained event values are plain Python int/str copies with exact expected content. This is selected lifetime evidence, not exhaustive memory-safety proof or allocation-stress testing.
7. Close the private bus/peer and check cleared receiver pointer/slots/callbacks. No native slot was allocated, so real broker slot lifetime is outside this fixture. No real service/job/clock/sensor/model workload occurs.

The helper binds only five additional fixed signatures: set_fd, new_signal, set_sender, seal, rewind. The [tagged header](https://raw.githubusercontent.com/systemd/systemd-stable/v255.4/src/systemd/sd-bus.h) was reviewed for types; [set_fd ownership documentation](https://raw.githubusercontent.com/systemd/systemd-stable/v255.4/man/sd_bus_set_fd.xml) establishes transfer/close behavior. The [tagged message implementation](https://raw.githubusercontent.com/systemd/systemd-stable/v255.4/src/libsystemd/sd-bus/bus-message.c) was reviewed for non-unset bus requirement, seal and body/cursor behavior. Dedicated raw manual URLs for seal/new_signal were unavailable; header/implementation review was used, without treating source as installed-binary attestation. ADR-045.

## Cases and result meaning

| Cases | Selected assertion |
|---|---|
| copied-lifetime, uint32-max | Exact uoss fields, uint32 maximum, Python copies survive owner release |
| canceled, skipped | Preserve non-success result, do not convert to completion/recovery authority |
| sender, missing-sender, path, interface, member, method-type | Wrong/missing selected native envelope poisons callback |
| short-signature, trailing-signature, wrong-basic-type | Reject non-uoss signature before body acceptance |
| consumed-first, consumed-all, unsealed | Real negative/zero native read paths reject incompatible cursor/message state |
| job-id-mismatch, zero-job-id, wrong-unit | Strict decoded job/unit contract invalidates receive state |
| oversized-result, invalid-result, unicode-result | Copy-size, result-format and ASCII rules reject data |
| replay, overflow | Duplicate rejected; retain32events and reject33rd, latch unknown |
| owner-change, disconnect | Synthetic continuity notification invalidates state permanently |
| consumer-error, consumer-interrupt | ValueError/KeyboardInterrupt contained before returning through C, bus fault remains |

Short/trailing signatures are **well-formed native messages with incompatible schemas**, not truncated/corrupt D-Bus wire bytes. Exhausted cursor cases are manually advanced valid objects. There is no incoming wire parser fuzzing, authenticated sender, receive loss/coverage study, native disconnect or actual owner replacement. The fixture's synthetic epoch is deliberately not the live observation's epoch.

Even a synthetic done/canceled/skipped event is passed to JobEvidence without a submitted-job reply: status stays unknown and native_binding_verified/service_quiesced_verified/may_disarm_recovery remain false. Other fixture success flags mean assertions passed, not Engine2 detection or restoration success.

Each child installs an8second SIGALRM/default OS termination before native work; parent uses subprocess timeout10seconds, shellFalse, STDIN/STDERR discarded, selected JSON stdout. No child creates a descendant. Success runs exercised alarm setup, not actual alarm-expiry/FFI-hang or parent-death behavior. Kernel timers, process/storage/native failures, captured-output memory and trust in the local OS/library remain limits. The helper uses test assertions; it is not a security sandbox or supported `python -O` control path. Windows skips the28actual native cases rather than reporting simulated native success; unsupported Linux backends fail, not silently skip/fall back.

## Executed commands and saved evidence

From `D:\research f1`, existing environments only:

```powershell
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python scripts/systemd_native_fixture.py --case copied-lifetime
.venv/Scripts/python.exe -m pytest -q tests/test_systemd_native_fixture.py --basetemp=tmp/native-callback-target-win-20261006-01 -o cache_dir=tmp/pytest-cache-20261006
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python -m pytest -q tests/test_systemd_native_fixture.py --basetemp=tmp/native-callback-target-linux-20261006-01 -o cache_dir=/home/acgresearch/.cache/acg-pytest
.venv/Scripts/python.exe -m pytest -q --basetemp=tmp/native-callback-full-win-20261006-01 -o cache_dir=tmp/pytest-cache-20261006 --junitxml=output/engine2-native-callback-windows-tests-20261006.xml
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python -m pytest -q --basetemp=tmp/native-callback-full-linux-20261006-01 -o cache_dir=/home/acgresearch/.cache/acg-pytest --junitxml=output/engine2-native-callback-linux-tests-20261006.xml
.venv/Scripts/python.exe -m ruff check cloudguard scripts tests
.venv/Scripts/python.exe -m ruff format --check cloudguard scripts tests
.venv/Scripts/python.exe -m pip check
git diff --check
```

Standalone first native case exit0: pinned library SHA bdf59c828b547bcdbe7b3576c0810d9d9d2e982d8b61b365812542da6a4c4a99, resolved libsystemd.so.0.38.0, reviewed Linux/glibc2.39/LP64, UID1000, synthetic/private success; no authority flags. Then targeted Windows3pass/28skips/0.07s, Linux31pass/2.44s. No substantive test failure or receiver bug was observed; no invented incident/fix.

Full [Windows XML](../output/engine2-native-callback-windows-tests-20261006.xml):791collected,758pass/33Linux-only skips, zero failures/errors, pytest console7.04s/XML suite7.025s. Full [Linux XML](../output/engine2-native-callback-linux-tests-20261006.xml):791pass, zero failures/errors/skips, console29.81s/XML suite27.524s. These are software-run durations, not clock accuracy or engine performance benchmarks; difference not diagnosed. Existing inert process tests ran under approved host execution. Lint passes,100files formatted, pip check/working whitespace pass.31new tests;28native child fixtures plus3portable checks. Every prior XML and the one-attempt live receiver folder remain unchanged.

Use fresh temporary/report names on reproduction, never replace saved XML. Run targeted pytest to execute the cases; do not use the historical `systemd_receiver_capture.py --observe` directory as a fixture/retry target. Publication/staged checks and Git receipt are recorded in WL-055.

## Next prerequisite

Design/test durable guest-side intent/reply/completion binding under the inert fence: lost reply, completion before reply, crash after enqueue, sealed queued worker, owner/boot replacement, replay and non-success must remain unknown/operator-recovery when unresolved. Do not wire the current unfenced systemctl path into a supposedly safe new gate, or infer all jobs drained from a snapshot. Privilege separation, stale-request elimination, native restoration validation, final intervention protocol and fresh explicit human stop consent remain required before any real time-service experiment. Timing stability/ML/independent evaluation are still open; Engine1 stays frozen at engine1-v2.2.
