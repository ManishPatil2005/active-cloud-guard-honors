# Three-trial readiness repeatability study

## QA-023 - Saved event-offset consistency strengthened

10October2026/WL-099: repeat_readiness.accept now requires exact integer event_unix_ns/offset bounds and supported event range; recomputes bounds using checked per-call first/last wall samples and abs(clock difference)+sampling uncertainty. Saved bounds/zero flag must agree exactly; changing the event while retaining favorable bounds cannot pass.11newcases/62selected passes each OS. Historical October5 trials1/2accept and3reject unchanged; pre-fix8fail9pass preserved. This checks saved arithmetic, not raw-export provenance, authenticated asset identity, full coverage, physical time alignment or supervisor eligibility. No new repeat/sensor/workload/clock correction. Future frozen runner hash is different; never retrofit historical receipts. Earlier study results below remain historical.

## Separately declared follow-up: 5 October 2026

Before execution, declare a new batch at `output/engine2-readiness-repeats-20261005` using the hardened runner and the unchanged acceptance/protocol below. Exactly three planned slots, no replacements or adaptive waits, abort on the first failed gate. The September batch is not overwritten or pooled with this batch. Restore availability only by starting the existing Docker Desktop and existing lab Redis, without container recreation, clock changes or added permissions; record changed startup conditions. Perform a read-only preflight before collection and explicit sensor enumeration afterward. Review hash-matched correlation and collector metrics offline before drawing any conclusion. Even three accepted runs would establish only bounded same-host development repeatability, not general coverage, accuracy or production readiness.

Planned invocation: `wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python scripts/repeat_readiness.py --output-dir output/engine2-readiness-repeats-20261005`.

### Follow-up results: all three launched, acceptance gate failed

The declared command executed once. [Manifest](../output/engine2-readiness-repeats-20261005/manifest.json): three launched, zero unlaunched, two accepted, third rejected by `accept()` with `measured timestamp mismatch`. Status remains failed, not completed validation. No replacement run or timing adjustment. All sensor children returned zero, but that means collection completed, not that correlation timing was acceptable.

| Trial | Acceptance | Selected records | First warmup connect | All six unique connects | Measured bounds excluding zero | Collector event delta |
|---|---|---|---|---|---|---|
| [1](../output/engine2-readiness-repeats-20261005/trial-1.json) | Accepted | 205 | Absent | False | 0/4 | 13,967 |
| [2](../output/engine2-readiness-repeats-20261005/trial-2.json) | Accepted | 246 | Present | True | 0/4 | 13,713 |
| [3](../output/engine2-readiness-repeats-20261005/trial-3.json) | Rejected | 246 | Present | True | 4/4 | 14,093 |

Third-trial PID associations are unique, with zero unassigned connects, four PONGs and acceptable harness wall/monotonic brackets. Nevertheless event-minus-command offset bounds are entirely negative: PID 105 [-886752175, -821050741] ns; 111 [-882148666, -811625239]; 117 [-881460343, -824289165]; 123 [-882431334, -826296079]. These are bounds, not a fitted clock correction. Successful command identity matching and harness clock checks did not establish cross-clock alignment. Cause remains unproven (INC-032); neither historical timing issue nor general stability is declared fixed.

Each hash-bound metrics reduction has 16 snapshots and zero reported kernel/output-queue drop deltas. These counters are collector-wide, not proof of target-specific completeness. The selected Docker identity is unchanged across this batch; Redis's recorded start changed during availability recovery before the batch. No sensors remained at explicit final enumeration; timesyncd active, no clock-service changes. Existing Redis remains running; other lab services were not started. September evidence remains untouched.

Offline review checked manifest receipt hashes and all six frozen source hashes, selected exactly one local raw log by its SHA256 for each trial, reran `correlate(raw, container_id, correlation_process_ids, measurement.calls, warmup_pids=warmup_process_ids)` and compared the complete object with saved correlation, checked identical pre/post/cross-trial identity, and reran `accept()` to reproduce the manifest statuses. For each selected raw directory, executed `python scripts/sensor_metrics_report.py --metrics <hash-matched-raw-directory>/metrics.jsonl --trial output/engine2-readiness-repeats-20261005/trial-N.json --output output/engine2-readiness-repeats-20261005/trial-N-metrics.json` using Windows .venv Python. All three reductions and review assertions passed; raw files remain local/ignored. Hashes establish byte consistency, not authenticated provenance.

Fresh software checks after sensor cleanup: 351 passed on Windows (2.05 s) and Linux (3.38 s), with new `output/engine2-repeat-followup-{windows,linux}-tests-20261005.xml`; Ruff check/format (68 files) and Windows pip check passed. No executable implementation changed in this increment. Next is a reviewed simultaneous collector/backend/harness clock diagnostic design, not another unchanged success-seeking batch, baseline fitting or ML training. Do not broaden host permissions or change clock services without separate approval.

Predeclared 30 September 2026 before execution. Freeze the current identified_second_canary_v1 / container_pid_connect_v2 / per_call_brackets_v1 diagnostic with source hashes. Exactly three sequential planned trials on the same selected Redis identity. No replacement runs or adaptive waits. Stop remaining trials on preflight, collection, acceptance, identity, source-change or cleanup failure; retain failed receipts and count unexecuted trials explicitly. Output directory must be new.

Acceptance: successful bounded sensor, identified second-canary readiness, four PONGs and unique measured PID matches, per-call/interval timing checks, all four correlation offset intervals include zero, unchanged target identity across all runs, and sensor removed. First-warmup absence is reported separately, not silently discarded or an automatic failure of measured readiness. All-six flags and collector counters are descriptive; neither proves all-syscall completeness. No clock-service changes, environment reset, extra permissions, control comparison, ML training or accuracy claim. Default existing watchdog/resource/privacy boundaries apply.

This is a small same-host development repeatability check, not independent trials from a population or sufficient statistical power. Do not pool it with earlier changed protocols to claim one success rate. No tests or unrelated compute are deliberately run concurrently with sensor trials. Runner timeout is 60 seconds per child; independent sensor watchdog remains active, and final explicit cleanup inspection is required after any timeout.

Command, using existing WSL acgresearch Python from the repository root:

```text
python scripts/repeat_readiness.py --output-dir output/engine2-readiness-repeats-20260930
```

Review hash-bound raw correlation and collector metrics offline after the batch, before accepting the evidence package. Aggregate all planned outcomes, including missing first warmups; do not generate a survivor-only accuracy or overhead estimate. Next decision: if all measured gates pass, advance to scoped workload-family design; if not, diagnose the recorded failed gate without a favorable rerun.

## Execution: incomplete batch, preserved

[Manifest](../output/engine2-readiness-repeats-20260930/manifest.json): trial 1 accepted, then FileNotFoundError while resolving the next output path before trial 2 child creation. Trial 3 skipped; no replacement or retry. Correct accounting is **one launched/accepted, two not launched**, not a completed three-run study. The original manifest's not_run_trials=1 counted unentered slots, and its trial-2 failed entry represents orchestration failure, not a sensor run. This reporting defect is preserved rather than edited retrospectively; future manifests track child_started and count unlaunched children, including launch failures and timeouts distinctly.

[Trial 1](../output/engine2-readiness-repeats-20260930/trial-1.json): identified second-canary readiness passed; four measured matches with zero-compatible bounds, first warmup not observed, second observed, zero unassigned connects. [Metrics](../output/engine2-readiness-repeats-20260930/trial-1-metrics.json): 16 snapshots, collector event delta 13,909; kernel/output-queue drop deltas zero. Coverage remains unknown. Offline SHA256-matched raw log was reparsed with correlate and exactly reproduced the saved correlation. No survivor-only success rate or overhead estimate.

Follow-up: no acg-falco containers, timesyncd active, WSL pwd and ls both resolved /mnt/d/research f1. The traceback establishes an output-path resolution failure; transient WSL working-directory behavior is plausible but not proven. Mitigation resolves destination once before collection and uses absolute paths thereafter. The executed manifest source hash intentionally differs from the final hardened runner. No sensor source/protocol change and no new experiment after mitigation. INC-031 records the uncertainty.

Final regression: 351 tests each OS, Windows 2.13 s / Linux 3.18 s; output/engine2-repeat-{windows,linux}-tests-20260930.xml. Eight new cases include historical receipt acceptance/rejections and mocked launch/timeout failure preservation, with no retry. Ruff lint/format 68 files and Windows dependencies pass. Orchestration failures are not exhaustively injected. A new separately named repeatability study is still needed before advancing the measurement-stability gate.
