# Offline event alignment investigation

Follow-up: per-call wall/monotonic brackets now implemented in workload.py (timing_protocol=per_call_brackets_v1). Each call retains first/last samples and comparison; >50 ms disagreement including uncertainty, or >5 ms sampling span, rejects the run as call_clock_outside_tolerance. Round-trip measurement remains the monotonic interval around ping(); bracket collection adds surrounding work. A synthetic transient-jump regression passes even though whole-interval difference is zero. Full suites 301 each OS. No new live run, no collector alignment or causal mapping established. Historical receipts lack these fields and are not upgraded retrospectively; no assumption of identical measurement overhead across protocols. Inter-call-only changes and callback exception partial evidence remain limitations.

30 September 2026, E2-009 / INC-029. This is analysis of the unchanged 29 September raw logs, not new sensor collection or a corrected benchmark.

## Acceptance and implementation

Retain exact half-open measurement boundaries, raw/receipt/inventory hash validation and unknown coverage. Add before/inside/after counts, connect offsets relative to the recorded start, and timestamp regressions in original export order. Do not sort away regressions, pair events causally with PINGs, repair clocks, infer dropped events or change a baseline. The existing strict adapter bounds input size and rejects invalid logs before reporting. Correct the generic no-control sentence to say this individual report does not join controls.

Implemented in scripts/workload_report.py. No collector, workload, Engine 1 or architecture change. Existing saved reports remain byte-for-byte unchanged; new analysis is in [ON-1 alignment](../output/engine2-on-1-alignment-20260930.json) and [ON-2 alignment](../output/engine2-on-2-alignment-20260930.json).

## Findings

| Observation | ON-1 | ON-2 |
|---|---:|---:|
| Before / inside / after connect records | 2 / 4 / 0 | 3 / 3 / 0 |
| Before / inside / after all events | 80 / 160 / 0 | 86 / 120 / 0 |
| Export-order timestamp regressions | 0 | 0 |

ON-2 connect offsets in seconds: -3.274947709, -2.158947420, -0.065428194, +0.936139707, +1.935020974, +2.937555580. Thus the six records exist in the saved capture; one is 65.428194 ms before the measured start. This explains how the timestamp filter yields three rather than four connections without proving which PING produced any record.

The last four form an approximately one-second sequence. If provisionally aligned in order with the four measured dispatches, all would precede those dispatch offsets by roughly 63–66 ms. That is an exploratory pattern consistent with cross-clock misalignment, NOT a verified event-to-command association or measured correction. The minimized capture lacks process/command correlation IDs. No fixed offset is applied. Endpoint wall/monotonic agreement in the harness only compares its own clock samples; it does not establish alignment with collector timestamps. No regressions in exported timestamps and zero collector-reported drops do not resolve that distinction.

Status: INC-029 narrowed, not fixed. The earlier 120-event interval count is retained; no completeness, threat, sensor-speedup or independent accuracy claim follows. The inconsistent two-pair latency result also remains unchanged.

## Commands and verification

For each on-1/on-2, PowerShell read the receipt and selected exactly one output/runtime-raw/**/sensor.log whose SHA256 equaled raw_log_sha256, then ran:

```text
.venv/Scripts/python.exe scripts/workload_report.py --raw <hash-matched-private-log> --trial output/engine2-paired-audited-20260929/<name>.json --inventory testbed/inventory.json --output output/engine2-<name>-alignment-20260930.json
.venv/Scripts/python.exe -m pytest tests/test_workload.py -q
.venv/Scripts/python.exe -m pytest -q --junitxml=output/engine2-alignment-windows-tests-20260930.xml
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python -m pytest -q -o cache_dir=/home/acgresearch/.cache/acg-pytest --junitxml=output/engine2-alignment-linux-tests-20260930.xml
.venv/Scripts/python.exe -m ruff check cloudguard scripts tests
.venv/Scripts/python.exe -m ruff format --check cloudguard scripts tests
.venv/Scripts/python.exe -m pip check
```

Both offline reports succeeded; targeted suite 13 passed; full suites Windows 300 in 2.08 s / Linux 300 in 3.45 s. Ruff lint/format passed (62 files), Windows dependencies passed. Two new tests cover original-order boundary diagnostics and rejection of failed normalization; existing boundary test also checks region accounting. Tests are synthetic software checks, not clock calibration. Raw logs remain excluded. No workload, Docker mutation or time-service operation was performed this increment.

## Next acceptance gate

Design explicit per-call clock bracketing and a reviewed collector-to-harness clock/correlation diagnostic. Keep old captures unmodified and predeclare failure criteria before any new collection. Automated paired-report provenance validation also remains incomplete. Only after alignment is demonstrated should repeated resource-instrumented baseline collection begin; independent labels and ML still remain later gates.
