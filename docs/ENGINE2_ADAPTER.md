# Engine 2 offline sensor adapter

Implemented and exercised 28 September 2026. E2-003 remains partial. This increment connects the **saved** bounded Falco trial to the existing normalized capture contract; it does not install/restart a collector, build an anomaly model or change Engine 1.

## Acceptance and scope

- Consume only the documented ACG Falco 0.45.0 smoke envelope with the pinned image receipt, successful exit/PONG and cleanup receipt.
- Check raw bytes against the trial's saved SHA-256 before parsing. Bind an explicitly supplied asset to a full container ID from the receipt and an existing loopback inventory.
- Validate timestamps, selected successful syscalls, cgroup scope and duplicates; export only normalized event identity/time/container/kind.
- Account for every input line, reject incomplete/invalid event sets, retain unknown collection loss and never infer benign behavior or threat probability.
- Load the output using unchanged runtime.load_capture/windows, and preserve all previous evidence.

## Data flow and trust

`cloudguard/sensor_adapter.py` exposes `normalize`; `scripts/normalize_sensor.py` is an offline CLI. Neither executes raw content, Docker commands, network requests or security actions. The CLI creates a new directory containing `capture.json` and `accounting.json`. Existing directories are refused; invalid record sets produce accounting only and exit 1. Precondition errors (wrong hash/receipt, unknown asset, invalid UTF-8, oversized input) raise before creating output. Filesystem failures can leave a partial new directory; do not treat directory existence as success.

Maximum input is 1,000,000 bytes, 10,000 lines and 2,000 accepted events, aligned with the existing capture contract. Duplicate JSON keys, non-finite JSON constants, unknown envelope/field names and invalid selected records are rejected. This adapter is intentionally narrow, not a general-purpose Falco importer. Diagnostic stderr lines are counted but not interpreted; JSON-looking lines beginning with `{` or `[` must validate. A truncated event reclassified as diagnostic still cannot silently reduce the capture because accepted syscall counts must equal the receipt. A modified/forged receipt can defeat that consistency check: hashes are not signatures or authenticated identity.

Supported mappings:

| Raw successful syscall | Normalized kind |
|---|---|
| execve, execveat | process_start |
| open, openat, openat2 | file_open |
| connect | network_connect |

These count selected successful calls, not unique processes/files/requests. The adapter requires agreement among integer evt.rawtime, evt.time and the nanosecond UTC envelope timestamp. Nanoseconds remain in the capture; the existing runtime parser truncates to microseconds before floating-point windowing. Supported timestamps are 1970 through 2100. IDs hash container/time/syscall/result, independent of file order and diagnostic text. Identical projections are rejected because the minimal collector lacks a unique sequence number; this can reject two indistinguishable legitimate records rather than silently deduplicating them.

The receipt image digest identifies the intended collector build but does not authenticate its execution. Cgroup membership and inventory mapping remain declarations (`binding_verified=false`). No pre/post deployment attestation or readiness handshake is added here.

## Accounting is not sensor completeness

`validated_event_count`, `rejected_record_count`, diagnostic-line count and rejection categories describe parser inputs. They do **not** measure kernel/ring-buffer loss, log rotation or unselected syscalls. `sensor_dropped_events=null` and `collection_coverage=partial_or_unknown` are deliberate. Falco's zero drop-action occurrences are not converted into zero dropped events. Zero valid events or any rejected event prevents capture publication. No empty windows are manufactured.

## Actual saved-data result

Input: local raw log from the verified 28 September trial, SHA-256 `1a9d553988542359a36bc23dffc5b697427ed410ce1f2701c7b6889d5bdb396b`; original receipt unchanged. This is offline processing of earlier live data, not a new live collection.

[Accounting](../output/engine2-normalized-20260928/accounting.json): 61 lines, 21 diagnostic lines, 40 validated events, zero rejected records, receipt counts match. [Capture](../output/engine2-normalized-20260928/capture.json): real prior syscall timestamps, not synthetic timestamps. Raw output strings/cgroups/hostnames are excluded; container IDs/timestamps still require privacy review. The private repository publication was reviewed for this lab capture only.

Existing runtime.load_capture and windows(capture, 60) accepted the capture, producing one window at epoch 1790602320 for compose/redis: total 40, process_start 2, network_connect 1, file_open 37; coverage partial_or_unknown. This is a partial minute, not a measured full minute of activity. No comparator score was calculated because no separate matched real baseline exists.

## Reproduction and checks

From the repository root, using the local environment (raw logs are intentionally not in Git):

```text
python scripts/normalize_sensor.py --raw output/runtime-raw/acg-falco-633d3b4bb218411a83b1605addb52e26/sensor.log --trial output/engine2-sensor-trial-verified-20260928.json --inventory testbed/inventory.json --asset-id compose/redis --capture-id redis-smoke-20260928 --scenario-group redis-ping-development --output-dir output/engine2-normalized-20260928
python -m pytest -q --junitxml=output/engine2-adapter-windows-tests-20260928.xml
```

These paths record the executed run; use fresh output names when reproducing. No fresh collector run is required to test the adapter. In WSL the executed test command was:

```text
wsl -d ACG-Research --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python -m pytest -q -o cache_dir=/home/acgresearch/.cache/acg-pytest --junitxml=output/engine2-adapter-linux-tests-20260928.xml
```

Results: 250 passed on Windows (2.10 s), 250 on Linux (2.34 s). Thirty-four new tests cover valid runtime ingestion, six syscall mappings, sensitive-field removal, invalid envelope/fields/scope/time/results, duplicate records/keys, malformed/non-finite JSON, receipt/hash/count gates, unknown assets, size bounds, empty input, deterministic IDs and CLI non-overwrite. Windows Ruff lint/format (49 files) and pip check passed. These are software regression results, not independent detection accuracy or exhaustive fuzzing.

## Next gates

Collector readiness, pre/post container identity checks and actual loss/coverage instrumentation come next. Then collect separately grouped, labeled baseline and observation workloads with comparable exposure/duration and record CPU/memory overhead. Do not train and evaluate on this same 40-event development sample. Isolation Forest, autoencoder, threat confirmation, calibrated TCI and autonomous response remain outside this increment.
