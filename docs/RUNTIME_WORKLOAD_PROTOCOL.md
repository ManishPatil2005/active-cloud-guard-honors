# Runtime workload protocol v0.1

## Separate full-window scheduler proposal - 11 October 2026

QA-029/WL-106 implements [SensorLease](../scripts/window_sensor.py), a separate explicit-approval-gated lifecycle library, not an end-to-end live collector CLI. Same pinned Falco image/caps/mounts, no-pull/networknone, proposed140second Falco duration plus150second TERM/3second kill watchdog. Fresh unique nonce rules directory/exact config hash, selected Redis precheck. Launch/cleanup commands bounded and audited; full-ID/name/nonce/image ownership before stop/removal. Stop and re-inspect, then exclusive bounded raw logs and single regular-file metrics tar export/hash before removal. Never extract archive paths. NonUTF8/unsupported tar/oversize/partial export preserves stopped container and marks cleanup unverified. Unknown launch delivery remains unknown despite later removal/absence; sealed one-attempt lease, no retries.26new mocked cases/final86selected passes each OS; no actual collector/native tar/deadline compatibility proven.

Old25second sensor remains unchanged. Library caller must obtain reviewed operational authority, enforce durable intent/result/source binding and integrate canary readiness/UTC boundary/full observed coverage; literal approved=True is not a signed supervisor decision. No raw metrics eligibility/clock calibration/authenticated coverage or independent labels inferred from cleanup. Caller death/late Docker work/kernel scheduling are not solved. Next durable coordinator and separately reviewed native qualification; no unattended monitoring or live collection implied.

QA-028/WL-105 implements [RedisWindowTransport](../scripts/window_transport.py), the callback/selected identity piece only. Caller supplies a reviewed full container ID and explicit local Unix socket, calls check_identity before scheduling, then uses client.ping with window_workload.run and checks identity after. Fixed PID+PING shell text only;128byte combined response/0.5second direct-client deadline/60attempt cap, safe sticky rejection and original attempt/PID snapshot. Any Docker host/context environment override rejects before a client call. No standalone live CLI or sensor launch added.39newcases/83selected passes each OS use mocked Docker plus actual harmless process-supervisor regressions.

This does not complete collector integration: selected daemon identity is trusted, not full deployment attestation; client reap can take an additional5seconds plus1second pipe join, and remote exec completion remains unverified after client timeout. Stop without retry/launch replacement; preserve uncertainty. The existing25second sensor remains incompatible. Next versioned sensor lifetime/cleanup/source-bound durable receipts/readiness and complete UTC-window coverage, followed by separately approved live qualification. No historical scheduler/specification receipt overwritten or real telemetry claim.

QA-027/WL-104 implements [window_workload.py](../scripts/window_workload.py) as a separate qualification scheduler, not an amendment to the historical four-second live protocol below. Fixed60PINGs at offsets0..59seconds over60seconds;250ms maximum dispatch lateness,750ms measured round-trip and100ms end lateness. Existing clock bracket/tolerance checks retained. Stop at failure without catch-up/retry; retain attempted/completed/unattempted counts and missing clock records. Callback exception text/reply contents are not stored. Engineering thresholds are proposed, not calibrated security operating points. PING frequency has no threat label; this remains the existing development family.

CLI `tmp/dependency-candidate-windows-20261009/Scripts/python.exe scripts/window_workload.py --output output/window-definition-NEW.json` publishes definition only. [Actual definition](../output/window-workload-definition-20261011-qa027.json) explicitly marks collection unauthorized/live transport unintegrated/watchdog incompatible. The library callback needs separately bounded deadline enforcement; post-return timing checks cannot kill a stuck callback. No sensor or Redis launched in21new virtual-clock tests. Existing sensor_trial25second watchdog/32second wait and four-second choices remain unchanged. Do not wire this scheduler into that old sensor command.

Next integration requires separately versioned collector lifespan/cleanup, identity/canary readiness, metrics and raw evidence bracketing, source binding and partial-failure preservation. Sixty seconds elapsed can straddle two UTC feature bins: align/review continuous observed boundaries before accepting a full60second feature window. Timing acceptance alone never verifies collector coverage or independent benchmark eligibility. Live qualification and actual task/policy context/reviewers remain open.

Defined 29 September 2026 before the measured-profile pilot. Scope: engineering validation of measurement boundaries, not independent effectiveness evaluation. Preserve all earlier captures unchanged. Engine 1 and existing stack remain fixed.

## Pilot acceptance

Use only existing Redis, credential-free loopback PING, current pinned Falco image and unchanged collection capabilities/watchdog. After matching-event readiness, wait one second, then measure four seconds. Profile ping_1 dispatches at offset 0; ping_4 dispatches at offsets 0, 1, 2 and 3 seconds. All commands must return PONG. Record actual dispatch offsets and Docker-exec round-trip times using a monotonic clock, plus wall-clock nanosecond interval boundaries for joining events.

Reject completed-run designation on a command failure, scheduled work exceeding four seconds, dispatch lateness above 250 ms, elapsed interval outside 4.0..4.1 seconds or wall/monotonic elapsed disagreement above 50 ms. These are engineering tolerances, not scientifically calibrated thresholds. The sensor has the existing independent 25-second watchdog. A failure stays in the denominator and saved artifacts; do not silently rerun until a favorable result appears.

Pilot order is declared in advance: one ping_1 run then one ping_4 run. These are related development samples, both scenario_group=redis-ping-development, not independent train/test groups. Fixed order and one repetition cannot establish statistical significance. Each interval report revalidates raw bytes through the strict adapter and selects exact nanosecond timestamps in half-open [start,end). Record excluded-event counts, never relabel all events as workload-owned. Time filtering does not prove causal attribution, eliminate delayed canary events or establish complete coverage. Preserve separate collector metrics; global drop counters are not target-specific loss.

## Gates after the pilot

1. Verify measured intervals are bracketed by valid collector metrics, handle partial/missing intervals and preserve uncertainty. Boundary clocks share an assumed host clock; their agreement is not external clock authentication.
2. Add matched sensor-off controls with identical workload and host conditions, order balancing, repetitions, CPU/memory sampling and explicit measurement overhead. Docker-exec latency includes process launch/transport: it is not Redis-only latency or sensor overhead. Do not assert a <5% overhead target from these pilots.
3. Predeclare repeat counts and stopping rules for workload families before collection; group related deployment/template variants. Independently review labels and keep an untouched evaluation partition. Increased benign PING frequency is not an attack label.
4. Fit statistical/ML baselines only once comparable, adequately sampled runs exist. The existing comparator's minimum three windows is a software guard, not a valid sample-size calculation. Do not rename related PING groups to bypass leakage checks.

Pilot execution/results, when available, belong in WORK_LOG and separate output files. No results were predeclared as successful here.

## Pilot execution receipt (added after the runs)

Both runs occurred on 29 September local time (Asia/Calcutta), 28 September UTC; receipts retain UTC timestamps. The predefined order was followed with no retries or relaxed tolerances.

- [ping_1 receipt](../output/engine2-ping1-measured-20260929.json): PONG, but rejected for timing_outside_tolerance. Monotonic elapsed 4,000,085,791 ns; wall-minus-monotonic difference 1,117,025,466 ns. Sensor removed. The rejection occurs before post-identity/metrics collection, so those final fields are not established for this attempt; raw log hash is retained. No interval summary or score generated.
- [ping_4 receipt](../output/engine2-ping4-measured-20260929.json): accepted measured schedule, four PONGs, 4,000,150,373 ns monotonic elapsed and 6,738 ns clock difference. Before/after identity stable; sensor removed. Full capture 200 records. [Interval report](../output/engine2-ping4-interval-20260929.json): 160 records inside (8 process_start, 148 file_open, 4 network_connect), 40 outside. Temporal selection does not prove ownership of each event.
- [Metrics](../output/engine2-ping4-metrics-20260929.json): 16 snapshots with timestamps spanning the selected interval, collector event delta 10,681 and reported drop deltas zero. This manual bracket observation is not an automated completeness guarantee.

The four recorded Docker-exec round trips were approximately 63.879, 62.602, 56.936 and 60.969 ms. These are not Redis-only latency or a sensor-overhead estimate. A separate sensor-free four-second clock diagnostic observed monotonic 4,000,081,177 ns, wall 4,000,083,054 ns, difference 1,877 ns. The first discrepancy did not reproduce in that check; cause remains unknown (clock adjustment and sampling/scheduling effects are possibilities, not established diagnoses). No host clock settings changed. See INC-026.

Result: one accepted / one rejected development pilot. No valid paired baseline comparison, fit, accuracy or overhead estimate exists. The timing gate detected an unsuitable interval instead of silently incorporating it. The earlier 40/80-event smoke captures cannot be retroactively assigned measured boundaries.

## Commands and regression evidence

Executed from the repository root, using the existing environments:

```text
wsl -d ACG-Research --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python scripts/sensor_trial.py --profile ping_1 --output output/engine2-ping1-measured-20260929.json
wsl -d ACG-Research --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python scripts/sensor_trial.py --profile ping_4 --output output/engine2-ping4-measured-20260929.json
python scripts/workload_report.py --raw output/runtime-raw/acg-falco-200333ad9220495481bb941aff9b240f/sensor.log --trial output/engine2-ping4-measured-20260929.json --inventory testbed/inventory.json --output output/engine2-ping4-interval-20260929.json
python scripts/sensor_metrics_report.py --metrics output/runtime-raw/acg-falco-200333ad9220495481bb941aff9b240f/metrics.jsonl --trial output/engine2-ping4-measured-20260929.json --output output/engine2-ping4-metrics-20260929.json
python -m pytest -q --junitxml=output/engine2-workload-windows-tests-20260929.xml
wsl -d ACG-Research --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python -m pytest -q -o cache_dir=/home/acgresearch/.cache/acg-pytest --junitxml=output/engine2-workload-linux-tests-20260929.xml
```

Unqualified Python above was `.venv\Scripts\python.exe` on Windows. Use new output names for reproduction; raw paths remain private/local. Windows 279 tests passed in 2.11 s; Linux 279 in 2.56 s. Eleven new tests cover both fixed schedules, overrun, clock disagreement, bad PONG, unknown profile, exact nanosecond half-open boundaries and invalid interval rejection. Software tests do not certify host clocks or exhaustive process-failure behavior.
