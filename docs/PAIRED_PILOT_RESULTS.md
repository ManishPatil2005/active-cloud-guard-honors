# Audited paired pilot: results and remaining gates

Review completed 30 September 2026; execution occurred 29 September, starting 14:16:18 UTC. Dates in the unchanged receipts are execution dates, not this review date. Scope: E2-008, one fresh predeclared OFF/ON/ON/OFF batch after prerequisite audit, not a repeat-until-success experiment.

## Audit and acceptance

Before execution, Windows and Linux full suites passed 298 tests each (2.03 s / 2.97 s). Ruff check and format check passed (62 files); Windows pip check and publication checker passed (220 existing publication files). Local main and GitHub main matched 0af760bd666e11c4a36e04a2244b6b9519697edb; the Engine 1 freeze tag matched 6736a577f1ba08b4700daf8a86370ec3bbd1c019. Read-only Docker/Redis/known-sensor preflight passed. This audit did not rerun Ollama, Chroma, Trivy, independent labels or all historical live experiments; their prior results remain historical.

Acceptance: fresh six-interval clock check; four successful fixed ping_4 runs in declared order; same selected Redis identity; sensor cleanup; no retries, tolerance relaxation, architecture change or modification of historical evidence. The approved PowerShell try/finally temporarily stopped guest systemd-timesyncd and restored it. The batch exited zero and printed restored state active. Follow-up on 30 September confirmed active/enabled, Redis running and no remaining acg-falco containers. No Windows time setting or permanent service configuration changed.

## Observations

[Manifest](../output/engine2-paired-audited-20260929/manifest.json), [clock gate](../output/engine2-paired-audited-20260929/clock.json), and [descriptive summary](../output/engine2-paired-audited-20260929/summary.json) preserve the results. All five jobs exited zero. All four measurements returned four PONGs and passed existing timing guards. Both sensors observed readiness after two canaries and were removed.

| Run | Mean Docker-exec round trip | Measured events | Outside interval |
|---|---:|---:|---:|
| OFF-1 | 59.423 ms | Not collected | Not collected |
| ON-1 | 91.887 ms | 160 | 80 |
| ON-2 | 66.066 ms | 120 | 86 |
| OFF-2 | 72.592 ms | Not collected | Not collected |

Pair 1 difference: +32.465 ms (+54.63%). Pair 2: -6.526 ms (-8.99%). ON-1 contains a 168.492 ms first round trip, retained without exclusion. Opposite signs and two pairs do not establish a reliable overhead effect. This is Docker-exec latency, not Redis-only response time, CPU/memory overhead, statistical significance or meeting the <5% target.

Strict hash-bound normalization accepted both entire raw captures: 240 and 206 records. Interval selection yielded ON-1: 8 process_start, 148 file_open, 4 network_connect; ON-2: 6 process_start, 111 file_open, 3 network_connect. Four measured PONGs but only three interval connect events in ON-2 is an unresolved alignment/coverage discrepancy (INC-029), not proof that a specific event was dropped. The full second capture contains six connect events including warm-up. Do not move interval boundaries or relabel outside events to manufacture four measured connections.

Both metrics summaries contain 16 snapshots, bracketing the measurement by their recorded wall timestamps. Collector-wide event deltas: 15,245 / 13,865; kernel and output-queue drop deltas: zero. These counters do not prove target completeness, cross-clock alignment or causal attribution. Raw logs remain local/ignored; reviewed minimized receipts and summaries are published.

The generated interval reports retain the existing script's generic sentence "no sensor-off comparison exists." In this context it means that the individual interval-report operation does not join a control; it is not an accurate project-wide statement after this batch. The separate paired summary above is the control comparison. Reports are preserved as generated; correcting that wording in the report generator is a remaining documentation-code task.

## Commands actually executed

From the repository root; python below denotes .venv/Scripts/python.exe for offline operations:

```text
python -m pytest -q
python -m ruff check cloudguard scripts tests
python -m ruff format --check cloudguard scripts tests
python -m pip check
python scripts/repository_check.py
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python -m pytest -q -o cache_dir=/home/acgresearch/.cache/acg-pytest
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python scripts/paired_pilot.py --preflight-only
git ls-remote origin refs/heads/main refs/tags/engine1-v2.2
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python scripts/paired_pilot.py --output-dir output/engine2-paired-audited-20260929
python scripts/paired_report.py --directory output/engine2-paired-audited-20260929 --output output/engine2-paired-audited-20260929/summary.json
```

The pilot command was inside the approved initial-active check / systemctl stop / try-finally systemctl start / verify-active wrapper, not run with ordinary restored NTP state. Offline for each on-1/on-2 receipt: matched exactly one private sensor.log by SHA256, ran scripts/workload_report.py with --raw, --trial, --inventory testbed/inventory.json, --output <batch>/<name>-interval.json; ran scripts/sensor_metrics_report.py with sibling metrics.jsonl, --trial and --output <batch>/<name>-metrics.json. Both succeeded. No extra workload was executed during offline analysis. Source manifest hashes describe the executed code; no source change in this increment.

## Next gate

Investigate saved ON-2 event timestamps against the declared measurement and canary boundaries, plus collector timestamp behavior, before expanding collection or fitting a baseline. Retain unknown coverage. Harden automated report/provenance validation and wording; current report generation trusts successful local receipts and is not authenticated evidence. Then predeclare an adequately repeated, resource-instrumented protocol. Independent grouped labels, ML evaluation, calibrated TCI and long-term synchronization policy remain open. Neither engine is certified production-ready or scientifically complete.
