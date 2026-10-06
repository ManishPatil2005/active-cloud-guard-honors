# Systemd job evidence review and offline contract (E2-032)

## Status — 6 October 2026

Source/interface review completed; an **isolated offline completion-evidence contract** is implemented/software-tested. Native D-Bus client, guest fence integration and recovery safety remain unfinished. No job was submitted, canceled, started or stopped; `Subscribe` was not invoked. No native clock comparison, service setting, sensor or model workload. Existing comparison/guest-fence/native-observer/default-engine sources and historical receipts are unchanged.

Acceptance: review actual job/subscription semantics, verify selected installed interface signatures read-only, and test path-bound completion including signal-before-reply, lost replies, malformed/replayed events and identity/connection loss. Do not turn an offline record into service-quiescence proof or recovery authority.

## Primary-source findings and design consequences

The [systemd-stable v255.4 D-Bus manual](https://raw.githubusercontent.com/systemd/systemd-stable/v255.4/man/org.freedesktop.systemd1.xml), method discussion around1204–1229 and signals1469–1487, explains asynchronous job-return semantics and subscription-before-submission tracking. StopUnit follows the analogous start mechanism. JobRemoved carries job ID/path/unit/result. Crucially, cancellation of a job need not cancel the operation itself. Therefore neither a submission reply nor a canceled result is treated as a safe completed stop.

The [v255.4 bus-wait-for-jobs implementation](https://raw.githubusercontent.com/systemd/systemd-stable/v255.4/src/shared/bus-wait-for-jobs.c) parses `uoss` and filters pending object paths, handles disconnection, and treats done/skipped as successful command exits. **Our stricter diagnostic choice:** only an exact tracked `done` can be labeled successful evidence; skipped and other results are not promoted to stop success. This is a research safety contract, not a claim that upstream skipped handling is a defect. Version-tagged source is not installed-Ubuntu binary attestation.

Design inference: retain completion arriving before the submission reply; bind later by the returned path. Lost reply cannot be repaired by a nearest-time event, unit name alone, canceled result, empty job list, PID disappearance or active snapshot. The future native client must install/acknowledge its signal match and subscription before submitting; enforce sender/header/signature/serial validation; maintain boot/bus/manager identity and receive continuity; durably record intent/reply/result through the same guest admission gate. Worker death after enqueue/lost replies still require a recovery design, not an invented job ID.

## Actual read-only interface check

Executed as ordinary acgresearch via approved host WSL access:

```powershell
wsl -d ACG-Research -u acgresearch --exec /usr/bin/busctl --system introspect org.freedesktop.systemd1 /org/freedesktop/systemd1 org.freedesktop.systemd1.Manager --xml-interface
```

Query succeeded; first displayed XML was truncated by output budget, not a service/query failure. Repeated the same introspection, parsed XML in PowerShell and printed only selected signatures:

| Name | Input | Output/signal arguments |
|---|---|---|
| StopUnit | ss | o |
| StartUnit | ss | o |
| Subscribe | empty | empty |
| CancelJob | u | empty |
| JobRemoved | signal | uoss |

[Minimized manual summary](../output/engine2-systemd-interface-review-20261006.json) is transcribed from that output, not an authenticated trace or a native job-completion receipt. This establishes selected schema presence only; no actual connection-epoch IDs, subscription/event continuity, permission to control jobs or current service/lab readiness was verified. Introspection was the only method invoked.

## Offline implementation

`cloudguard/systemd_job.py` contains JobEvidence, no bus/subprocess/network/filesystem/service calls or native adapter. Strict caller-declared boot SHA256/bus GUID/unique manager owner, exact subscription/match booleans before begin, one submission/reply, bounded uint32 job/path validation, copied decoded events and32selected-event buffer. Valid other-unit events are ignored; different jobs for the fixed timesyncd unit cannot satisfy the returned path. A completion may be buffered before reply. Duplicate/malformed/overflow events, invalid/repeated reply/submission, disconnect, lost continuity or epoch change poison evidence permanently, even if a caller ignores the exception or the old identity returns.

Outcomes: `tracked_job_done`, `job_not_successful`, or `unknown`. A decoded matching done means consistency of **supplied evidence only**. All outcomes retain `native_binding_verified=false`, `service_quiesced_verified=false`, and `may_disarm_recovery=false`. The epoch and readiness booleans are not authenticated. The class expects decoded selected messages; it does not parse/validate raw D-Bus envelopes, observe method serials or persist records across worker death. This is deliberately not integrated into the inert callback acknowledgment or live transport;23-file comparison source freeze is unchanged.

## Executed checks

```powershell
.venv/Scripts/python.exe -m ruff check cloudguard scripts tests
.venv/Scripts/python.exe -m ruff format --check cloudguard scripts tests
.venv/Scripts/python.exe -m pip check
.venv/Scripts/python.exe -m pytest -q tests/test_systemd_job.py --basetemp=tmp/systemd-job-target-win-20261006-01 -o cache_dir=tmp/pytest-cache-20261006
.venv/Scripts/python.exe -m pytest -q --basetemp=tmp/systemd-job-full-win-20261006-01 -o cache_dir=tmp/pytest-cache-20261006 --junitxml=output/engine2-systemd-job-windows-tests-20261006.xml
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python -m pytest -q --basetemp=tmp/systemd-job-full-linux-20261006-01 -o cache_dir=/home/acgresearch/.cache/acg-pytest --junitxml=output/engine2-systemd-job-linux-tests-20261006.xml
```

Targeted29passed/0.04s; lint/format94files/pipcheck pass. [Windows XML](../output/engine2-systemd-job-windows-tests-20261006.xml):672collected,669passed/3existing Linux-only skips,6.53s, zero failures/errors. [Linux XML](../output/engine2-systemd-job-linux-tests-20261006.xml):672passed/21.28s, zero failures/errors/skips. Full suites used approved host execution for existing inert helpers/WSL.29additions, synthetic decoded events only; prior real process tests remain inert, prior643reports unchanged. Repository/publication/staged/commit/remote checks separate in WL-050.

## Next gate

Select and review a persistent native D-Bus receive adapter with read-only subscription/identity/continuity tests first. No package or native library was installed/selected by this milestone. Then bind durable job evidence to the trusted guest gate and test worker death after enqueue/lost replies/inherited handles, eliminating the old unfenced dispatch. Native-storage/boot/source/privilege controls, final protocol/current preflight, explicit human intervention approval and actual restoration validation remain mandatory. E2-032 is partial; E2-030 not closed. Passing this contract does not permit the native comparison or prove stable clocks, detection quality, ML or production readiness.
