# Exclusive receiver capture and one-observation protocol (E2-033 follow-up)

## Latest outcome — precheck failed, native observation not launched

Implementation published as `a9cc57d6e815ead96ec4e77acca32cf685a599a8`, GitHub main/local SHA matched and working tree was clean. The planned native observation was **not launched**: required known-sensor enumeration failed before capture. [Minimized precheck summary](../output/engine2-systemd-receiver-precheck-20261006.json) manually transcribes the actual tool outputs; it is not a native observation receipt or authenticated trace. INC-045 / WL-053.

Actual selected service query returned active/running/enabled; `/usr/bin/timeout --version` returned GNU coreutils9.4. Guest `docker ps -a --filter name=acg-falco- --format '{{.ID}}'` could not execute docker. Read-only diagnosis: `/usr/bin/docker` is a symlink to `/mnt/wsl/docker-desktop/cli-tools/usr/bin/docker`, but both Docker Desktop mount and target are absent (`ls` exit1). No installation/PATH/configuration was changed.

Windows `Get-Command docker` found `C:\Program Files\Docker\Docker\resources\bin\docker.exe`. Scoped Docker Desktop/backend process-name enumeration returned no entries. Current context is desktop-linux; context metadata identifies the **local** `npipe:////./pipe/dockerDesktopLinuxEngine` endpoint. A read-only known-sensor query against that verified local context exited1: named pipe not found. This establishes missing/unavailable expected local integration/API at inspection time, not an exhaustive process diagnosis or proof all containers/sensors are absent. No remote Docker context/API contacted.

The combined precheck shell's final exit0 belonged to successful timeout-version query; earlier Docker execution error was explicitly recognized, not treated as an all-passed preflight. Separate local API/path checks exited1. Per the predeclared protocol, failed inventory means **unknown** and prevents native launch. No capture directory, started/result record, native child, subscription, service/job/clock change, Docker startup, settings change, WSL restart or sensor/model workload. The one native observation remains pending; no retry/replacement observation occurred.

Restore local Docker Desktop availability/integration with operator direction, then recheck required read-only preflight before considering the still-pending single receiver observation. Do not silently relax the gate, manufacture sensor absence or describe this as an Engine2/clock fix. Production/ML/timing/durable job-fence gates remain open. The implementation/protocol checkpoint below is preserved as historical context.

Read-only diagnosis commands executed after the failed guest query:

```powershell
wsl -d ACG-Research -u acgresearch --exec /usr/bin/ls -ld /usr/bin/docker /mnt/wsl/docker-desktop /mnt/wsl/docker-desktop/cli-tools/usr/bin/docker
Get-Command docker -ErrorAction SilentlyContinue | Select-Object Name,Source
Get-Process -Name 'Docker Desktop','com.docker.backend' -ErrorAction SilentlyContinue | Select-Object ProcessName,Id
& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe' context show
& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe' context inspect desktop-linux --format '{{ .Endpoints.docker.Host }}'
& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe' --context desktop-linux ps -a --filter name=acg-falco- --format '{{.ID}}'
```

Final source hashes still match the published four selected sources; native observation directory absent. Full suites not rerun after read-only checks/document-only result recording: latest755Windows/5skips and760Linux remain implementation software evidence, not native receive validation.

## Implementation checkpoint — 6 October 2026

Launcher **implemented/software-tested**; native observation not yet executed at this checkpoint. Continue from f03a0f6a5befee194615c3e3d25cfde7ae374efc without changing the engine stack/controller/fence/native clocks or historical evidence. This follow-up adds failure-preserving storage and supervision for the [isolated receiver](SYSTEMD_RECEIVER.md); it is not service-control integration or timing/ML acceptance.

Acceptance: durable exclusive start record before a child can open a bus; one fixed ordinary-user Linux child; selected source/header/schema/no-authority validation; partial failures retained without raw error messages; bounded cleanup; no overwrite/retry. Publish implementation/protocol before **one** separately recorded native attempt. No live subscription has occurred while developing/testing this launcher.

## Files and execution flow

`scripts/systemd_receiver_capture.py` is a separate Linux CLI. Default imports have no bus connection/service action. Windows can test/read evidence; real capture refuses Windows/root. Explicit `--observe` required. No arbitrary target, command, output-directory or retry option in the CLI; injected Python API runner/directory are trusted test seams, not an adversarial sandbox.

```text
fresh fixed directory -> started.json (exclusive, flush/fsync)
  -> hash four selected sources -> ordinary-user Python child
  -> native receiver -> strict selected child receipt -> source postcheck
  -> result.json (exclusive, flush/fsync), including unknown/failure
```

Fixed directory: `output/engine2-systemd-receiver-observation-20261006`. `mkdir(exist_ok=False)` refuses an existing directory before child launch. Never remove/rename it to make a replacement observation. Separate `started.json` is never rewritten; a started-only directory after parent/storage failure means incomplete/unknown, not success. A result-file collision fails without replacing its bytes. Files are private-repository minimized research receipts, not raw bus logs or restoration-helper runtime secrets. Trusted local directories/OS are assumed; fsync of files does not establish parent-directory/power-loss durability or hostile inode/ancestor defenses.

Selected freeze: launcher, receiver, systemd_job and package initializer. Parent/child hashes must match before/after; receiver independently checks its three sources/library. No external interpreter/libc/runtime/loaded-memory attestation. The existing23-file comparison freeze is unchanged because the new launcher is not integrated with that controller.

The parent spawns only its own interpreter and fixed launcher child arguments with `shell=False`, stdin/stderr discarded, stdout captured and a new session. Parent communicate deadline20seconds; terminate then2seconds, kill then2seconds, no unbounded cleanup wait. Record whether child was actually reaped; timeout/interrupt/unreaped/nonzero/invalid output never becomes observed. Captured stdout capped65536bytes **after capture**, not a hard preallocation limit; rejected/partial raw output is not published, only hash/length. A parent launch error is saved by class, never private text. Unexpected IO errors are classified conservatively.

Native child arms default-action SIGALRM for18seconds **before** calling the receiver, cancels it afterward. It can terminate a stuck child even if the parent disappears; wiring is unit-tested, not a demonstrated crash-inside-FFI/parent-death guarantee. These guest timers and Python monotonic deadlines depend on the already-questioned adjusted kernel clock; no hard physical elapsed-time, host/WSL/power failure or disk-IO bound is claimed. A supervised outer30second GNU timeout is specified for the one attempt below. A child killed by a timer has no claimed graceful close/unsubscribe; OS process exit normally releases its socket, not an attested native cleanup receipt.

Child reports must have the exact capture envelope, selected native report fields, reviewed backend, valid epochs/hash strings/event buffer/counters/booleans and all five action/recovery-authority flags false. Only a complete native observation with acknowledgements/release/close and matching sources/epoch can be accepted as `observed`. Valid native `unknown` retains its selected partial report. Malformed/nonfinite/duplicate/private/unexpected fields fail; child exception messages/stderr/unrelated unit data are not stored. A bounded numeric `error_errno` is now retained for native OSError observation failures, and child-construction errno may be retained separately; no error text added. Historical receiver reports remain unchanged/revision-bound.

Zero notifications is not no jobs, full coverage or service quiescence. A native done cannot bind to our own job because **no job is submitted**. No recovery disarm, stop/start/cancel/disable, clock setter, Windows setting, WSL restart, model, sensor or workload in this protocol. Native fault/owner replacement/lost-job reply and durable gate recovery remain unvalidated.

## Observed software checks

34new cases:32Windows passes/2new Linux-only skips; Linux34passes as part of the full suite. Two actual Linux processes are **inert substituted children**: one prints `{}`, one ignores TERM/sleeps and is killed/reaped. No bus or service is opened by these tests. Other new cases use synthetic native report/C-level fixtures/process doubles. Alarm ordering/default action is mocked; do not claim an actual18second alarm or parent-death native test was run.

The initial combined targeted run had85passes/2skips and one lint F401 unused `copy` import. Removed that unused test import, added alarm-order test; final combined targeted receiver/capture86passes/2skips/0.26s. No native product failure or timing cause observed; this trivial lint issue does not warrant a new research incident. Earlier726test receipts preserved.

Commands executed from the repository root:

```powershell
.venv/Scripts/python.exe -m ruff check cloudguard scripts tests
.venv/Scripts/python.exe -m ruff format --check cloudguard scripts tests
.venv/Scripts/python.exe -m pip check
.venv/Scripts/python.exe -m pytest -q tests/test_systemd_receiver_capture.py tests/test_systemd_receiver.py --basetemp=tmp/systemd-capture-target-win-20261006-02 -o cache_dir=tmp/pytest-cache-20261006
.venv/Scripts/python.exe -m pytest -q --basetemp=tmp/systemd-capture-full-win-20261006-01 -o cache_dir=tmp/pytest-cache-20261006 --junitxml=output/engine2-systemd-capture-windows-tests-20261006.xml
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python -m pytest -q --basetemp=tmp/systemd-capture-full-linux-20261006-01 -o cache_dir=/home/acgresearch/.cache/acg-pytest --junitxml=output/engine2-systemd-capture-linux-tests-20261006.xml
```

Lint/format98files/pipcheck/working whitespace pass. [Windows XML](../output/engine2-systemd-capture-windows-tests-20261006.xml):760collected/755pass/5Linux-only skips/zero failures/errors, suite7.134s (console7.14s). [Linux XML](../output/engine2-systemd-capture-linux-tests-20261006.xml):760pass/zero failures/errors/skips, suite21.367s (console22.70s). Existing three Linux-only cases plus two new inert cases explain Windows skips. Full suites used approved host for inert helper/WSL execution; timing fields distinguished without diagnosing their difference. WL-052 records publication checks separately; these are local tests, not GitHub Actions or independent benchmarks.

## Predeclared one-attempt native protocol

After this implementation is committed/pushed and local/GitHub hashes match:

1. Confirm fresh capture directory absent and selected execution sources unchanged; record implementation commit/source hashes. Do not overwrite historical files.
2. Read ordinary-user selected timesyncd ActiveState/SubState/UnitFileState and list known research sensor containers before collection. Read installed timeout availability. No starting Docker/services/sensors to make a precheck pass; if checks fail, preserve failure and do not launch.
3. Execute the following command exactly once, ordinary acgresearch. Five nominal seconds of notification pumping,18second native alarm/20second parent/2+2cleanup/30+2outer bounds. No service job triggered to manufacture a notification:

```powershell
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /usr/bin/timeout --signal=TERM --kill-after=2s 30s /home/acgresearch/acg-venv/bin/python scripts/systemd_receiver_capture.py --observe
```

4. Preserve exit code and started/result receipts, including unknown/zero-event/crash/timeout; no retry, replacement or changing safeguards to turn the outcome green. If no result exists, started-only is incomplete; do not claim cleanup.
5. Re-read selected service state/known sensors and check no diagnostic child remains; record scope/limits of process enumeration. Never kill an unrelated process or control a service based on an empty/missing receipt.
6. Review saved JSON sizes/schema/sources/epoch/no-authority flags offline against the unchanged source, actual child exit/reap and callback buffer. Record hashes and exact observed result; successful setup/cleanup is not actual JobRemoved delivery, job fencing, loss-free coverage, stable clocks or an independent evaluation.
7. Add a **new** result section and WL-053/mandatory documentation/evidence in a separate descriptive commit, preserving this implementation checkpoint. Add a new incident only for an actual material failure. Continue durable job/fence design only after reporting the outcome; real time-service intervention still requires explicit approval and finalized recovery protocol.

Current one-attempt status at implementation publication: **pending**. Native receiver source changes only add bounded errno retention; no underlying engine/controller/fence/native-clock or architecture migration.
