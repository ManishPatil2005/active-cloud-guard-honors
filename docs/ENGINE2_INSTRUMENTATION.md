# Engine 2 readiness, identity continuity and metrics

28 September 2026, E2-003 increment. Engine 1 and the Python/Docker/Ollama/Chroma architecture remain unchanged. This is a bounded development smoke, not an accuracy, benign-baseline or overhead benchmark.

## What changed and why

The earlier harness slept then checked container liveness; liveness did not establish event visibility. It now attempts at most three fixed Redis PING canaries, checking for successful process-start and network-connect records from the target cgroup after each. A matching event observation is required before the final PING workload. Other activity can satisfy those counts: causal attribution to the canary is not proven. Canary activity is included in the capture and must not be treated as undisturbed idle behavior.

Before and after collection, the harness reads only selected Docker fields: full ID, image ID, start time, running status, restart count and Compose project/service labels. Both observations must identify running lab Redis and agree exactly. This checks selected local-daemon identity continuity; it does not authenticate the daemon, attest mounted files/application state or eliminate changes between samples. `deployment_binding_authenticated` remains false. No extra credentials or environment fields are exported.

Falco configuration now emits metrics every second to the sensor-local `/tmp/acg-metrics.jsonl`, copied to the trial's unique ignored raw directory before cleanup. No host writable mount, metrics webserver, network output, additional capability, host PID namespace or kernel tuning was added. Resource/state/plugin/libbpf metrics are disabled; kernel counters and empty values are enabled. Default metric metadata can still expose host/network details: raw metrics remain local and publication-blocked. Existing 15-second Falco/25-second watchdog, resource ceilings and unique-container cleanup remain.

`cloudguard/sensor_metrics.py` validates a raw metrics hash, 1 MB size, 2..1000 snapshots, duplicate JSON keys, integer nonnegative required counters, increasing timestamps and nondecreasing counters/duration. It exports only first/last selected counters and their differences. Missing counters, resets or reordering fail instead of being interpreted as zero. `scripts/sensor_metrics_report.py` binds this summary to the saved successful instrumented receipt and refuses output overwrite. Extra metadata is discarded, not republished.

## Actual observed trial

[Trial receipt](../output/engine2-instrumented-trial-20260928.json): started 14:53:33 UTC. Matching-event readiness on attempt 2, final PONG, exit 0, identical before/after selected identity fields, sensor removed. Captured 80 selected successful calls: execve 4, openat 50, openat2 16, open 8, connect 2. Three PING attempts were issued (two canaries and final workload); only two sets of matching records are present. This illustrates why attempted workload count and captured events must not be equated, and why readiness is a gate rather than complete coverage. No causal proof identifies which attempted call was absent.

[Minimized metrics](../output/engine2-metrics-20260928.json): 16 snapshots, duration field 0 through 15 seconds. First/final scap.n_evts: 25/7646; observed delta 7621. First/final scap.n_drops: 0/0; output-queue drops: 0/0. These counters are **collector-wide, not Redis-specific**. They do not measure all kernel activity, the exact target's missing records, log rotation or the unsampled interval boundaries. Zero reported drops does not prove complete delivery. Coverage stays partial_or_unknown.

[Normalized capture](../output/engine2-instrumented-normalized-20260928/capture.json) and [accounting](../output/engine2-instrumented-normalized-20260928/accounting.json): 80 validated records, zero rejected, 22 diagnostic lines. The existing event adapter intentionally retains sensor_dropped_events=null; the separate collector-wide metrics report must not be promoted to a target-specific drop count. No comparator fit or anomaly score was computed. This capture uses the same development scenario group as the earlier PING sample to avoid pretending it is an independent evaluation group.

Final live check found no acg-falco containers and only the existing lab Redis running. No lab recreation, persistent monitor or security action occurred. Raw logs and metrics remain excluded from Git; reviewed minimized reports are published in the private repository.

## Executed commands

From repository root, with fresh filenames on repetition:

```text
wsl -d ACG-Research --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python scripts/sensor_trial.py --output output/engine2-instrumented-trial-20260928.json
python scripts/sensor_metrics_report.py --metrics output/runtime-raw/acg-falco-c2eb502b26b5497d81245aa0aeacde3e/metrics.jsonl --trial output/engine2-instrumented-trial-20260928.json --output output/engine2-metrics-20260928.json
python scripts/normalize_sensor.py --raw output/runtime-raw/acg-falco-c2eb502b26b5497d81245aa0aeacde3e/sensor.log --trial output/engine2-instrumented-trial-20260928.json --inventory testbed/inventory.json --asset-id compose/redis --capture-id redis-instrumented-20260928 --scenario-group redis-ping-development --output-dir output/engine2-instrumented-normalized-20260928
python -m pytest -q --junitxml=output/engine2-instrumented-windows-tests-20260928.xml
wsl -d ACG-Research --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python -m pytest -q -o cache_dir=/home/acgresearch/.cache/acg-pytest --junitxml=output/engine2-instrumented-linux-tests-20260928.xml
```

Windows Python commands used `.venv\Scripts\python.exe`. Both OS suites passed 268 tests; Windows Ruff lint/format passed (52 files), pip check passed. Eighteen new tests cover identity scope, bounded readiness, counter summaries, missing/boolean counters, resets, timestamp order, hashes, empty metrics, duplicate JSON keys and metadata minimization. Full launcher lifecycle/fault injection is still not exhaustive. The explicit final PONG failure guard was added after the live run (which returned PONG); no negative live workload was injected.

## Research limits and next gate

Readiness observations and selected identity continuity are now live-observed, and actual collector-drop counter snapshots are available. Full authenticated deployment mapping, complete coverage, matched workload duration, overhead, independent labels and detection accuracy remain open. Next: design repeatable separated baseline/observation runs with readiness/canary intervals distinguished, retain failure/partial samples and measure collection overhead before fitting a model. Do not train/test on these two related PING smokes as independent groups.

Configuration and interpretation follow the [official Falco metrics documentation](https://falco.org/docs/concepts/metrics/) and [drop troubleshooting guidance](https://falco.org/docs/troubleshooting/dropping/); compatibility was verified against the already pinned Falco 0.45.0 image, not assumed from current docs alone.
