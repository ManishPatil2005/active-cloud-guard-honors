# Three-trial readiness repeatability study

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
