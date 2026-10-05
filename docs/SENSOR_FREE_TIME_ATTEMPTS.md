# Sensor-free TIME bracket diagnosis

E2-021, declared 5 October 2026 before execution. User requested continuation, documentation and coherent named commits. INC-033's failed sensor read has no retained endpoints; that historical cause cannot be recovered. This is a **new sensor-free diagnostic**, not a replacement trial, overhead study, collector calibration or independent detection benchmark.

## Fixed method and acceptance

Extend the existing scripts/clock_bridge.py with opt-in `--record-attempts`; reuse E2-020's sanitized TIME recorder extracted to scripts/sensor_trial.read_time. Importing that module does not start a sensor. Existing mode/protocol and Engine 1 unchanged. New protocol redis_time_failure_evidence_v1: at most six sequential fixed Redis TIME commands, one-second sleep between accepted reads (five maximum), no PING. Stop immediately at any rejected bracket, command or sampling failure; no retry, replacement, grace-period extension or limit relaxation. Each TIME command timeout remains five seconds; accepted bracket <=500 ms, endpoint disagreement plus sampling uncertainty <=50 ms, individual sampler span <=5 ms. Preflight/identity commands retain their existing timeouts; fixed count/gaps are not a hard global wall-time guarantee under scheduling stalls.

Use only existing local Docker daemon and single running lab Redis. Verify known trial name/pinned-image sensor absence before/after and selected deployment identity continuity. Endpoint sensor absence is not proof no unrelated collector ran. No service restart, clock/NTP/Windows setting change, WSL reset, container creation, credentials/data access, software installation or added permissions. Redis TIME creates small process/network activity but no application-data write. No boot-clock reads or Falco event comparison in this diagnostic.

Freeze six execution-source hashes (bridge/shared recorder/absence check, clock arithmetic/sampler, deployment gate), require unchanged on successful completion. Export phases/status, available first/last clocks, computed comparison, separate clock/round-trip rejection flags, response hash and safe failure stage/class; never raw response/stderr/error message. Preserve partial receipt on failure, including accepted earlier reads; missing postflight fields stay missing. Do not synthesize offset bounds for rejected reads. Recompute every available compare value and accepted server bracket offline, check source hashes/attempt order/identity/absence fields before interpretation. Local consistency is not authentication or independent evaluation.

Acceptance: a complete, integrity-checked six-read observation or a preserved diagnostic failure with available inputs. `observed` does not mean clock drift or collector error fixed. Failure distinguishes clock incompatibility, sample width, >500 ms round trip or earlier command/sampling error **in this new attempt only**. A clock_outside_tolerance flag alone covers multiple clock-quality conditions; inspect its numeric fields. Endpoint-compatible results cannot exclude transient excursions or explain prior Falco lag. Keep INC-032/timing-stability gate open; no baseline/ML fitting follows automatically.

## Separate execution after implementation commit

One fresh path `output/engine2-sensor-free-time-attempts-20261005.json`. Commit/push implementation first, verify remote, then execute once after Linux preflight and read-only time-service/sensor enumeration:

```text
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python scripts/clock_bridge.py --record-attempts --output output/engine2-sensor-free-time-attempts-20261005.json
```

Explicitly inspect service/sensor/lab state afterward regardless of outcome. No software test suite or sensor running concurrently by this agent. Preserve result with a separate documentation/evidence commit, including failures. No automatic future experiments implied.

## Implementation checkpoint

Mode implemented; seven new tests cover shared recorder integration, six-read/five-gap behavior, first-rejection stop/no retry, sensor/preflight refusal, identity/source change, overwrite refusal and legacy protocol preservation. Existing E2-020 seven sanitized failure tests exercise extracted code. Final suites: 421 Windows (2.00 s) / Linux (2.66 s); [Windows](../output/engine2-sensor-free-attempts-windows-tests-20261005.xml), [Linux](../output/engine2-sensor-free-attempts-linux-tests-20261005.xml). Ruff lint/format (75 files), Windows pip check passed. No live observation claimed at this implementation checkpoint; real scheduler stalls/Docker timeout modes not exhaustively injected.
