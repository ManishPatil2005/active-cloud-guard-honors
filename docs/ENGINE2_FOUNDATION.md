# Engine 2 initial foundation: observation-only replay

**Current interpretation6October:** [CURRENT_STATUS](CURRENT_STATUS.md) separates this implemented observation-only baseline from refinements and full research gates. A separate bounded Falco harness/offline adapter exists; no continuously connected replay sensor or independently evaluated ML detector. Current replay output exposes implementation_scope and says live acquisition/normalization are separate paths, replacing stale broad no-eBPF-collector wording. Scores/guards unchanged; historical result files below remain byte-preserved. Next default research task [grouped data/label intake](RUNTIME_EVALUATION_PLAN.md), planned only.

## Historical foundation checkpoint

Latest extension (28 September): bounded live trial and offline adapter now exist; see ENGINE2_SENSOR_TRIAL.md and ENGINE2_ADAPTER.md. The prior real log normalizes to 40 events accepted by this runtime loader/windowing. No matched real baseline or detection evaluation exists. Earlier no-collector/no-adapter statements below describe the original foundation snapshot.

Implemented 2026-09-25. Engine 2 report version 0.1; package 0.5.0. Engine 1 remains v2.2, frozen at commit `6736a577f1ba08b4700daf8a86370ec3bbd1c019`, Git tag `engine1-v2.2`. Both baseline references were verified on the remote before runtime work began.

## Purpose and acceptance

Establish a small, testable data path for runtime observations before installing sensors, training ML models or connecting scores to response decisions. This is a real implementation of ingestion/windowing/statistical comparison, but **its saved demonstration uses synthetic replay data, not real telemetry**.

| Requirement | Implemented behavior |
|---|---|
| Explicit identity | Full container ID mapped to an inventory asset by the capture's declared bindings |
| Bounded input | 1 MB/capture, at most 2,000 events, at most 20 baseline captures |
| Strict validation | Duplicate keys/events/bindings, unknown fields/assets/containers/types and invalid timestamps rejected |
| Reproducible features | UTC-aligned non-overlapping windows; four explicit count features |
| Separate baseline | Distinct capture IDs/groups and no overlapping event records between fitting and observation |
| Missing evidence | Empty input yields no_observations; gaps are not filled with zero/normal windows |
| Conservative output | Count deviations for review; no threat label, action, probability or TCI update |
| Reproduction | Versioned synthetic fixtures, CLI, tests and non-overwriting smoke script |

No new external dependency or service is introduced. This does not replace the planned Linux eBPF/Kubernetes telemetry or Isolation Forest/autoencoder study. It provides the data contract and a simple statistical comparator those later experiments can use.

## Data contract

Each normalized capture is a JSON document with exactly:

- `schema_version`: `1.0`.
- `capture_id`: unique recording identity.
- `scenario_group`: grouping of related workload/template runs; do not split related variants across fitting and evaluation.
- `source`: `synthetic` or `normalized_sensor_export`.
- `bindings`: container_id/asset_id pairs. Container IDs are 64 lowercase hex characters; assets must exist in the supplied inventory.
- `events`: event_id, timezone-aware ISO 8601 timestamp, container_id and kind.

Kinds: `process_start`, `network_connect`, `file_open`. Raw command arguments, paths, environment, secrets and payloads are deliberately outside this minimal schema. The capture does not instruct code execution or network requests.

See [baseline fixture](../data/runtime/baseline-synthetic.json), [observation fixture](../data/runtime/observation-synthetic.json) and [fixture provenance](../data/runtime/README.md) for complete valid examples. Their January timestamps are invented test coordinates, not backdated capture claims.

Imported provenance is a **declaration**, not an authenticated sensor identity. `binding_verified: false` remains explicit even for sensor exports. The initial implementation cannot prove that an asset/container mapping corresponds to a live deployment, nor normalize raw Falco/Kubernetes output. Do not simply rename an alert-only file into this schema and call it representative benign telemetry. Collector selection, event selection, loss counters and coverage must be documented when real ingestion is added.

## Windowing and comparator

Default window: 60 seconds, configurable integer 1..3600. Event timestamps normalize to UTC; half-open windows use floor(epoch/window_size). Records are sorted, so input order does not change counts. Windows are grouped by asset and capture. Features:

1. Total event count.
2. Process-start count.
3. Network-connect count.
4. File-open count.

Fit per-asset mean and population standard deviation on supplied baseline windows only. Scale has a floor of 1.0 to avoid divide-by-zero on a constant synthetic baseline. Require at least three nonempty baseline windows for an asset; otherwise abstain with `insufficient_baseline` and null score. Three windows is a software guard, **not a scientifically sufficient sample size**.

For each observation window, compute the maximum absolute standardized count difference across those four features. Above the default threshold 3.0 yields `deviation_for_review`; otherwise `no_threshold_exceedance`. Threshold and scale floor are uncalibrated engineering choices. The features are correlated and no probabilistic significance is claimed. A low score does not imply safety; a high score does not imply an attack. This is not Isolation Forest or an autoencoder.

Only nonempty windows exist. Every window reports `observation_coverage: partial_or_unknown`; no heartbeat or sensor-completeness guarantee exists yet. Missing, zero-activity and partially captured intervals cannot currently be distinguished. Consequently this baseline cannot detect silence reliably, and count comparisons may be distorted by partial capture.

The source type must agree across baseline and observation. Exact event reuse and same declared scenario group are rejected; this reduces accidental contamination but cannot detect renamed templates, forged metadata, all temporal correlations or structurally similar workloads. The operator's baseline designation is not independently established benign ground truth.

## Commands

From the repository root with the existing Python environment:

```text
python -m cloudguard.cli runtime-replay data/runtime/observation-synthetic.json --baseline data/runtime/baseline-synthetic.json --inventory testbed/inventory.json
python scripts/runtime_check.py --output output/engine2-new-replay.json
```

Repeat `--baseline` to use additional distinct captures. `--window-seconds` and `--threshold` control the comparator. This command opens no sockets, executes no commands from telemetry, starts no background monitor and performs no isolation. The smoke script refuses to overwrite an existing report. The library returns a JSON-serializable report, not a serialized executable model.

Real raw telemetry should remain in ignored `output/runtime-raw/` until redacted/reviewed; do not publish production logs. The normalized schema minimizes sensitive payloads but IDs/timestamps can still be sensitive. Adding data to a repository always requires review.

## Observed result and tests

Saved [synthetic replay report](../output/engine2-replay-smoke.json): all four smoke checks passed (expected statuses, no actions, no sensor claim and explicit synthetic source). The first observation window matches the baseline counts; the second has nine connect events, giving maximum standardized difference 8.0 and a review flag at threshold 3.0. These are deliberately constructed examples, not accuracy measurements.

The [software test report](../output/engine2-foundation-tests.xml) records the complete suite. Tests cover schema/identity rejection, duplicates, source mismatch, event/group leakage, fitting independence, missing data, insufficient baseline, window boundaries, invalid parameters and the actual CLI subprocess. Tests and replay do not require Docker or Ollama. Earlier real service observations remain historical Engine 1 evidence, not Engine 2 telemetry.

## Next acceptance gates

Latest setup update (28 September): ACG-Research Docker integration is enabled and verified; Windows/WSL see the same running lab Redis container ID. Full Linux suite: 204 passed; synthetic replay passed. See [setup record](WINDOWS_LINUX_SETUP.md). No live sensor installed or kernel event visibility verified. Earlier host-preflight findings below remain historical.

### Host preflight increment (25 September)

Run `python scripts/runtime_preflight.py --output output/engine2-host-new.json` on the intended research host with a new filename. This standard-library script saves OS/release/architecture, effective UID on Linux, and present/absent/unavailable/unexpected-type facts for `/sys/kernel/btf/vmlinux`, `/sys/kernel/tracing` and `/sys/fs/cgroup/cgroup.controllers`. Other systems report not_applicable. No installs, subprocesses, socket connections or privilege changes. Exit zero means the report was saved, not sensor readiness.

These are diagnostic hints, not universal prerequisites or a compatibility test. Paths may exist without usable mounts/capabilities; absent markers do not rule out every collector. Facts describe the Python process's host/namespace, not another WSL distribution or remote Docker host. Linux always returns requires_sensor_specific_validation. Do not run as root merely to obtain this report.

Actual [Windows report](../output/engine2-windows-preflight.json) returned linux_host_required. Approved `wsl --list --verbose` listed only docker-desktop, Stopped, version 2. Docker server query failed with an unavailable engine pipe. No general-purpose research Linux distribution was listed; no services were started. The [204-test report](../output/engine2-preflight-tests.xml) covers mocked Linux branches and local script execution/overwrite refusal, not live Linux compatibility.

Next setup decision: supply a Linux research host/VM/WSL distribution (or explicitly approve provisioning one), then run preflight there. Select a sensor against official version-specific requirements and agree privileges, capture scope, retention and stop procedure before installation. Starting Docker alone does not establish eBPF compatibility. Do not treat the Docker-managed distribution as an approved general-purpose sensor host.

1. Validate a supported Linux host and select/configure one sensor with bounded privileges; record its version and event-selection rules.
2. Build the raw-sensor adapter, derive trustworthy container/deployment mappings and add coverage/loss accounting.
3. Record actual benign workloads and safe labeled simulations with grouped train/validation/test separation.
4. Compare this simple baseline with Isolation Forest, measuring false alarms, misses, drift, p50/p95 delay and sensor CPU/memory overhead.
5. Integrate reviewed runtime evidence with Engine 1 only after identity/time semantics and calibration are evaluated. Keep response observation-only until an explicit safety review authorizes more.

No live collector, Kubernetes adapter, trained ML accuracy, independent benchmark, overhead target or automated response is complete in this increment.
