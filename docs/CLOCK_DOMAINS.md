# Concurrent-trial clock-domain diagnostic

E2-017, declared 5 October 2026 before live execution. INC-032 showed unique PID matches with event timestamps outside harness brackets despite stable harness clocks. Design a different diagnostic, not a replacement repeatability run or corrected baseline.

## Fixed method and acceptance

One bounded Falco trial, existing fixed two-canary readiness and four-second ping_4 schedule. Opt-in `--clock-domains` requires correlation/fixed warmup. For each measured dispatch perform sequential Redis TIME / identified PING / Redis TIME, eight TIME reads total. Each TIME has a five-second command timeout and a valid <=500 ms harness bracket; preserve partial rows on failure. Keep precise nested PING brackets separate from the full three-command workload round trip. Whole-workload timing limits, existing sensor privileges/resource limits/watchdog and cleanup are unchanged. New label `container_pid_connect_clock_v1` is refused by repeat acceptance and existing latency-pair reporting. No historical evidence edited, retries, host/clock-service changes, correction factors or ML fitting.

Read-only local preflight before collection; one selected running Redis identity must match before/after. Save frozen source hashes and check unchanged after collection. New receipt path `output/engine2-clock-domains-20261005.json`; do not overwrite. Execute at most once after software checks. Explicitly enumerate sensors afterward; on failure preserve receipt and stop, not rerun for success.

Redis TIME returns server seconds and microseconds ([official documentation](https://redis.io/docs/latest/commands/time/), checked 5 October). The server time is a backend realtime observation, not an independent authenticated clock. Bound server-minus-harness offsets using full command endpoints/uncertainty, never half round trips. Compare each Falco event with its identified PING's precise harness bracket and with the two server readings (+999 ns quantization). Sequential server bracketing assumes adequate stability between those reads; endpoint compatibility cannot exclude transient excursions. All combinations of server/harness and event/server compatibility are reported without automatic causal verdict or alignment certification.

The extra TIME calls create process/network events and eight expected auxiliary Redis connections; do not classify unassigned connects as attackers, erase them, or claim their ownership from counts alone. Correlate measured PINGs only by unique PID/cgroup; preserve unassigned counts. No extra exported command-line, path or environment fields. Raw logs/metrics remain local/ignored. Published summaries contain bounded selected IDs/timestamps/counters. Eight auxiliary reads change the workload, so no direct comparison with earlier latency or baseline studies.

Planned command:

```text
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python scripts/sensor_trial.py --profile ping_4 --fixed-warmup --correlate --clock-domains --output output/engine2-clock-domains-20261005.json
```

Implementation: `cloudguard/clock_domains.py` shares the unchanged Redis bracket computation previously in `scripts/clock_bridge.py`, validates new per-call reports and computes separate diagnostic bounds. `clocked_ping()` retains partial observations. Default sensor and Engine 1 paths unchanged. Next scientific decision must follow results, not assume this diagnostic resolves INC-032.

## Executed once: collector-time incompatibility reproduced

The declared command returned 0, meaning collection/diagnostic reduction completed, **not alignment accepted**. [Receipt](../output/engine2-clock-domains-20261005.json): 566 selected records, 14 connects; both warmups and four measured PINGs uniquely matched. Eight connects remain unassigned to those six PIDs, consistent in count with the eight auxiliary TIME calls but not individually attributed. Identity stable, sensor removed. All eight server-minus-harness bounds include zero, whereas all four event-minus-harness bounds exclude zero and all four events precede their server-time brackets. No clocks changed, retries or correction.

| PING PID | Event-minus-server lower ns | Upper ns | Inside server bracket |
|---|---|---|---|
| 147 | -1135882820 | -1032288821 | No |
| 165 | -1135206064 | -1033020065 | No |
| 183 | -1135784420 | -1033861421 | No |
| 201 | -1136767999 | -1027732000 | No |

Event-minus-harness bounds likewise exclude zero, with lower limits around -1.091 s and upper limits around -1.035 to -1.039 s. This later observation narrows the discrepancy toward the collector timestamp/clock-conversion path rather than a demonstrated Redis/harness difference. It does not establish root cause, authenticate PID ownership, certify complete capture, correct September/earlier October evidence or justify a constant offset. Investigate the exact pinned Falco/libs timestamp-generation path and backend clock behavior before choosing another experiment or code change. INC-032 remains open; stability gate not passed.

Offline review selected exactly one local raw log by SHA256, checked all six saved source hashes and selected identity, recomputed `correlate()` using **nested PING brackets**, then recomputed `summarize()` and compared both complete objects with the receipt. All assertions passed. Invoked `.venv/Scripts/python.exe scripts/sensor_metrics_report.py --metrics <hash-matched-raw-directory>/metrics.jsonl --trial output/engine2-clock-domains-20261005.json --output output/engine2-clock-domains-metrics-20261005.json`: [metrics](../output/engine2-clock-domains-metrics-20261005.json) has 16 snapshots, event delta 24,604, reported kernel/output-queue drops zero; still collector-wide/unknown coverage. Explicit sensor enumeration empty; timesyncd active and postflight passed.

Software checks **before collection**: 368 tests Windows (2.01 s) / Linux (2.63 s), [Windows](../output/engine2-clock-domains-windows-tests-20261005.xml) / [Linux](../output/engine2-clock-domains-linux-tests-20261005.xml). Seventeen new cases cover clock-domain combinations, invalid receipts/order/IDs, partial failure, flag prerequisites and repeat-study exclusion. Existing pairing refuses any diagnostic_protocol. After collection, Ruff check/format (70 files) and Windows pip check passed; no concurrent software tests during collection, no model/Engine 1 live reruns. No claim of exhaustive Docker lifecycle fault injection or independently evaluated detection.
