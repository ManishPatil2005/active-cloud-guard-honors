# Preflight source coverage and execution gate (E2-029)

6October follow-up: [E2-030 uncertain-delivery guards](CLOCK_STOP_DELIVERY.md) fix premature cancellation after stop errors,610tests each OS. Guest-side fencing remains unresolved; this page's596-test/23-source statements preserve the preceding checkpoint.

## Status — 6 October 2026

Implemented and software-tested; **no real service intervention or native comparison was run**. Engine 1, the default Engine 2 path, native observer sources and historical evidence are unchanged. This follows the [transport milestone](CLOCK_COMPARISON_TRANSPORT.md), not a clock fix or a completed live-experiment protocol.

Acceptance: include the repository-local static import closure of the comparison and its existing lab preflight, freeze it before preflight, retain the frozen mapping on later failure, and reject changed preflight dependencies before collection/stop. Preserve explicit approval, restoration limits and prior evidence.

## What changed and why

The former 11-file list omitted modules imported by `paired_pilot.py --preflight-only`. That command imports the sensor/workload modules even though the preflight-only branch does not execute their workload functions. The source freeze also followed preflight, so it could not describe the files before that first operation. INC-042 records this reviewed coverage gap; it is not evidence of tampering or a past failed restoration.

`cloudguard/clock_comparison.py` now freezes 23 files before lab preflight and stores a detached `source_sha256` mapping immediately. Existing pre/post block checks compare this mapping, so a dependency change during preflight refuses the first collection and service stop. An unreadable/missing file or invalid freeze refuses preflight entirely. No new runtime dependency, import of sensor code by the controller, command, privilege or service setting was added.

The 12 added paths are:

- `scripts/paired_pilot.py`, `scripts/sensor_trial.py`, `scripts/workload_control.py`;
- `cloudguard/__init__.py`, `deployment.py`, `verification.py`, `workload.py`, `correlation.py`, `clock_domains.py`, `cache.py`, `sensor_adapter.py`, `runtime.py` (all under `cloudguard/`).

The new AST regression parses ordinary `import`/`from` statements recursively without importing or executing those modules. It checks the reachable local files against the list, including the package initializer, and will fail if a normal local import introduces another unlisted dependency. Twelve parameterized change tests cover each added file; three additional tests cover static closure, freeze-before-preflight/failure retention and missing-source refusal. The existing helper request automatically uses the enlarged mapping through the shared hashing function.

This is local source-byte continuity, **not attestation**: dynamic imports, external jsonschema/dependencies, interpreter/stdlib, schema/data files, binaries, loaded memory and concurrent changes between hash checks are not authenticated. Static import coverage does not prove that every imported function is safe or that all host collectors are absent. The unchanged native observer still binds its six files; previous saved source maps remain historical and are not rewritten.

## Executed verification

Windows commands, from the repository root:

```powershell
.venv/Scripts/python.exe -m ruff check cloudguard scripts tests
.venv/Scripts/python.exe -m ruff format --check cloudguard scripts tests
.venv/Scripts/python.exe -m pytest -q tests/test_clock_comparison.py --basetemp=tmp/source-freeze-target-win-20261006-01 -o cache_dir=tmp/pytest-cache-20261006
.venv/Scripts/python.exe -m pytest -q --basetemp=tmp/source-freeze-full-win-20261006-01 -o cache_dir=tmp/pytest-cache-20261006 --junitxml=output/engine2-preflight-freeze-windows-tests-20261006.xml
.venv/Scripts/python.exe -m pip check
```

Lint/format passed (90 files); targeted62 passed/0.50s; full596 passed/6.13s; dependency check passed. Full Windows tests used approved host execution for the existing explicitly inert breakaway-helper tests, without a weaker flag fallback. No live service operations were selected.

```powershell
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python -m pytest -q --basetemp=tmp/source-freeze-full-linux-20261006-01 -o cache_dir=/home/acgresearch/.cache/acg-pytest --junitxml=output/engine2-preflight-freeze-linux-tests-20261006.xml
```

Initial sandbox launch returned `Wsl/E_ACCESSDENIED`, exit1, before pytest produced a report. The approved host invocation then passed596/20.69s, exit0. This is an execution-environment permission failure, not an application test failure or a clock experiment. Fresh scoped basetemp directories were used; no broad deletion or ACL change. A PowerShell inspection of the spaced progress-document path initially used incorrect shell escaping; the quoted-path inspection succeeded, without a file modification.

[Windows XML](../output/engine2-preflight-freeze-windows-tests-20261006.xml) and [Linux XML](../output/engine2-preflight-freeze-linux-tests-20261006.xml) each record zero failures/errors/skips. Fifteen new regressions, historical581 reports preserved. Existing service calls remain simulated and real helper lifecycle tests remain explicitly inert. Publication checker, staged inspection and push/remote verification are recorded in WL-047 separately from test execution.

## Before any native batch — still do not execute

| Gate | Current outcome / required action |
|---|---|
| Source scope | Local static Python import closure covered; external/runtime/binary/data attestation not claimed |
| Specific authority | Fresh explicit permission for exactly one temporary guest-timesyncd stop is still absent; generic “proceed” is not consent |
| Late service requests | WSL client timeout does not prove guest command or queued systemd job termination. A delayed stop after restoration/disarm is a remaining safety hazard. Resolve and test ordering/termination handling before native execution; an active snapshot alone is insufficient |
| Actual prerequisites | Current lab, known-sensor absence, service state and helper launch capability must be checked read-only after the safety design is resolved; not rechecked by this milestone |
| Frozen protocol | Publish final command/receipt scope, abort/recovery handling and operator recovery procedure before intervention; do not call this page final approval |
| Bounded candidate | Existing proposal: one before/stopped/restored batch, at most48 packets/96 zero-mode queries,45s off-stage budget,60s helper deadline. Budgets are operational, not guaranteed physical-time bounds |
| Outcome interpretation | Preserve first failure/partial receipts; no retry, reset or settling-until-pass. Restoration failure needs immediate operator attention. A successful diagnostic is not stability, causality, general overhead or ML acceptance |

Do not change Windows time settings, persistently disable synchronization, reset kernel rates, restart WSL/Docker or run sensor workloads as part of this step. Helper recovery remains fallible under process/job, host, WSL and power failures. The next implementation priority is the late-request/restoration ordering hazard, before requesting or exercising native intervention authority.
