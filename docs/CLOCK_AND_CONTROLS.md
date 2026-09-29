# Clock diagnostics and sensor-off controls

29 September 2026. Planned before execution: six four-second clock checks, then (only if all pass) one ping_1 control and one ping_4 control, in that order. No retries or clock setting changes. Earlier failed evidence remains unchanged.

## Implementation and acceptance

`clock_check.sample` brackets each wall-clock read with monotonic readings. Midpoint coordinates and bracket widths expose sampling uncertainty. Accept only positive elapsed time, at most 5 ms per bracket, and absolute elapsed disagreement plus combined half-width uncertainty at most 50 ms. This conservatively rejects ambiguity; it cannot explain an earlier unbracketed reading or certify future clock stability. Workload scheduling now uses these samples with the previous four-second duration and dispatch tolerances unchanged.

`scripts/clock_diagnostic.py` performs six predeclared four-second checks, saves every result to a new file, and starts no sensor or network activity. `scripts/workload_control.py` rejects a running known trial name or pinned-image container before/after execution; checks existing Redis identity; performs two fixed PING warm-ups, a one-second guard, then the exact shared ping_1/ping_4 measured schedule. No collector is started, stopped or installed. Endpoint checks do not detect every host collector or a sensor appearing between checks.

Controls use mode=sensor_off_control, never normalized_sensor_export. No fake telemetry is generated. Same measured schedule is necessary but insufficient for causal overhead estimates: warm-up differs from variable sensor readiness, runs are not concurrent/paired, host conditions and CPU/memory are not controlled, and sample size is tiny. No subtraction from historical sensor-on latencies or overhead percentage is authorized by this protocol. Future order-balanced matched runs need an explicit protocol and uniform warm-up.

The control CLI requires `--clock-report` with status checks_passed and records that file's hash before Docker access. This is an operator-supplied gate, not an authenticated or fresh certificate; each actual workload also applies the new clock bracket checks. Full control-process lifecycle tests and live control execution remain pending.

Outputs refuse overwriting. Exceptions preserve control failure summaries. No secrets, arbitrary workload commands, new destinations, host settings, privileges or persistent monitoring. Engine 1 remains frozen.

## Actual result and retained blocker

[Diagnostic](../output/engine2-clock-diagnostic-20260929.json): six samples; five within tolerance, fourth rejected. Difference 1,129,990,064 ns, estimated sampling uncertainty 1,094 ns; endpoint bracket widths 94 and 2,093 ns. The sensor-free reproduction with narrow endpoint brackets makes endpoint sampling delay an unlikely explanation for this new observation. It does not identify which host/virtualization/time-service mechanism caused it. Historical INC-026 remains unresolved.

The predeclared gate failed, so neither control workload was run. No new kernel sensor was launched. Final Docker enumeration found no trial sensor and only existing Redis running. No performance comparison, fit, clock fix or overhead estimate is claimed.

Read-only follow-up: `timedatectl show --property=NTP --property=NTPSynchronized --property=TimeUSec` in ACG-Research returned NTP=yes, NTPSynchronized=yes, time 2026-09-28 18:47:20 UTC. Windows `w32tm /query /status` returned service-not-started error 0x80070426. These snapshots are not proof of the clock-jump cause. No clock/service setting, WSL restart or forced resynchronization was performed. Next investigation should identify the active Windows/WSL clock synchronization path before any separately approved disruptive correction. Do not relax tolerances or repeatedly retry until a passing sample appears.

## Commands and tests

Executed:

```text
wsl -d ACG-Research --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python scripts/clock_diagnostic.py --output output/engine2-clock-diagnostic-20260929.json
python -m pytest -q --junitxml=output/engine2-control-final-windows-tests-20260929.xml
wsl -d ACG-Research --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python -m pytest -q -o cache_dir=/home/acgresearch/.cache/acg-pytest --junitxml=output/engine2-control-final-linux-tests-20260929.xml
```

Windows Python was `.venv\Scripts\python.exe`. Initial suite 287 passed on each OS; preserved output/engine2-control-{windows,linux}-tests-20260929.xml. Added failed-clock-gate regression: final 288 passed on Windows (2.02 s) and Linux (3.75 s). Nine new tests cover bracketing, backward monotonic samples, disagreement/uncertainty rejection, known-sensor refusal and no Docker access after a failed diagnostic. Ruff lint/format and Windows pip check passed. These tests establish software behavior, not live control success or host-clock reliability.

Example control command, **not executed** because the prerequisite failed:

```text
python scripts/workload_control.py --profile ping_1 --clock-report PATH_TO_PASSING_DIAGNOSTIC --output NEW_CONTROL_REPORT.json
```

All diagnostic/check filenames are historical; use new names on deliberate future runs. Reports retain UTC; date labels use local 29 September.
