# Collector-on boot/TIME evidence follow-up

E2-022, predeclared 5 October 2026. The original E2-019 attempt is incomplete, with rejected TIME inputs lost; E2-021's later sensor-free six-read observation passed but cannot diagnose the earlier failure or verify Falco. This follow-up tests improved instrumentation under the collector, not a replacement run chosen for success.

## Change and fixed protocol

In boot-clock mode only, shared read_time now saves native boot/realtime sandwiches immediately before the first TIME clock sample and after the last TIME clock sample, **before redis_bracket validation**. Both endpoints survive a normal rejected clock bracket. Early command/sampling failures may still lack later fields; preserve safe stage/class and never synthesize missing readings. Default sensor/bridge/nonboot paths do not call native boot clocks. New receipt label container_pid_connect_boot_v2 prevents confusion with earlier instrumentation and is excluded from repeated-readiness acceptance/latency baselines.

One new bounded sensor trial with existing ping_4/fixed two identified canaries/correlation/clock-domains/boot-clock options. Same pinned Falco image, 15-second sensor run/25-second watchdog, permissions/resources, namespace gates, five-second TIME command timeout and unchanged <=500 ms/50 ms/5 ms clock criteria. No adaptive extension, second trial, retry, fitted offset, sampling tolerance relaxation or clock/NTP/WSL/Windows intervention. Abort and preserve partial receipt/raw log on first rejection; cleanup only its unique trial container. Existing Redis identity must remain stable; only existing lab Redis used.

Complete run has 27 native sandwiches: original 3 launch/readiness + 8 PING endpoints (11), plus 16 TIME endpoints. Existing boot_clock_summary remains the original 11-sample PING/launch reduction; the additional 16 are nested in time_read_attempts and checked separately offline. No claim of direct collector calibration-value measurement or exact binary-source attestation. The small extra clock reads change instrumentation; source hashes freeze seven execution files. Do not retrofit old observations or compare this diagnostic as matched latency overhead.

Native namespace checks still require active/children agreement, zero boot/monotonic offsets and shared boot hash across harness/Redis/sensor, unchanged at endpoints when reached. Endpoint readings cannot exclude between-sample transients, other collectors or unreported loss. Preserve unassigned connects and negative experimental findings. Actual collector offset/time-service causality and independent accuracy/stability remain unproven even if this attempt passes.

## Separate execution boundary

Implementation/test/docs commit pushed and remote verified first. Then Linux read-only preflight, known-sensor enumeration and time-service state. Execute **once** into a new destination:

```text
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python scripts/sensor_trial.py --profile ping_4 --fixed-warmup --correlate --clock-domains --boot-clock --output output/engine2-recorded-boot-clock-20261005.json
```

No agent-initiated tests/model/workloads during collection. Always verify cleanup/service/lab state afterward. For success, hash-match raw correlation and metrics, recompute full correlation/server/PING boot summaries and all 27 ordered native bounds; reconstruct TIME response hashes and compare fields. For failure, verify only available data, classify numeric rejection fields when present and explicitly retain missing postflight/correlation/metrics. No full summary fabricated from partial data. Record result separately, whether positive or negative.

Acceptance is an integrity-checked diagnostic outcome, not a causal fix, general clock stability or permission to fit ML. Retain INC-032; INC-033 original missing inputs cannot be repaired. Decide the next scientific experiment from the actual result, without automatically continuing until a favorable observation.

## Implementation validation before execution

428 Windows tests (2.20 s) / Linux (5.62 s): [Windows](../output/engine2-recorded-boot-windows-tests-20261005.xml), [Linux](../output/engine2-recorded-boot-linux-tests-20261005.xml). Five new boot-recording cases plus two added protocol-exclusion variants; existing nonboot/failure/privacy tests pass. Ruff lint/format (76 files), Windows pip check pass. Collector-on v2 not executed at this implementation checkpoint; actual sampler/command failure timing and lifecycle paths not exhaustively injected.
