# Bounded process-ID correlation diagnostic

Predeclared 30 September 2026, before live execution. E2-012. One new sensor trial only, fixed two-PING warmup and ping_4 schedule, existing digest/capabilities/mounts/network isolation/watchdog/resource limits. No time-service or Redis configuration changes. Prerequisite: normal local Docker/Redis/known-sensor preflight. Abort on failed timing, missing or ambiguous correlation; preserve output, no retries.

## Correlation and privacy contract

An opt-in --correlate mode adds proc.vpid to the existing selected syscall output. A fixed shell prints its PID and execs redis-cli PING; the PID is retained across that exec. Require four distinct positive PIDs and exactly one successful connect record per measured PID within the full target-cgroup capture. Do not select matches by nearest timestamp. Strict diagnostic fields, types, timestamp agreement and target cgroup are required. PID reuse or ambiguous/missing matches refuses a result. No command-line, environment, file-path or packet payload field is exported.

Falco defines proc.vpid as the process ID in its current PID namespace ([official field reference](https://falco.org/docs/reference/rules/supported-fields/), consulted 30 September). Runtime support of the pinned image must be demonstrated by the trial, not assumed from current documentation. Container identity and PIDs are local-daemon evidence, not authenticated adversarial attribution; PID reuse or unobserved unrelated activity remain limits.

The fixed shell changes workload instrumentation and produces extra process/file events. Therefore this is a diagnostic, not a comparable latency pilot. Paired reports reject diagnostic receipts. Default sensor output is unchanged, and the normal offline adapter deliberately rejects the extra field; diagnostic captures must not enter baseline fitting.

Compare the unique connect timestamp with its per-call wall/monotonic bracket, expanded by sampling uncertainty and measured endpoint disagreement. A range excluding zero indicates recorded timestamp disagreement under the bracket/correlation assumptions; zero inclusion is compatibility at this resolution, not clock synchronization or completeness. Endpoint checks cannot detect all transient excursions. Never apply inferred offsets to historical records.

## Planned bounded invocation

Run preflight before the sensor command, as acgresearch with the existing Linux environment:

```text
python scripts/paired_pilot.py --preflight-only
python scripts/sensor_trial.py --profile ping_4 --fixed-warmup --correlate --output output/engine2-pid-correlation-20260930.json
```

Use the full WSL invocation recorded in WORK_LOG. Finally verify no trial container remains. If the trial fails, inspect saved failure evidence before considering another separately authorized increment. No tolerance relaxation, clock-service stop or automatic favorable retry.

## Actual execution and limits

[Receipt](../output/engine2-pid-correlation-20260930.json): one trial succeeded with PIDs 213, 219, 225, 231, four distinct matched connect records, four PONGs and all per-call timing checks passing. All four offset ranges include zero: approximately [-8.50,+70.69], [-9.44,+63.20], [-11.33,+61.43], [-10.93,+61.61] ms. This shows compatibility within command-duration uncertainty for this trial, not exact synchronization, long-term stability or the historical cause. No correction applied.

Full capture: 204 selected records, including five connects. Six PING commands were issued including warmup, so total coverage is not demonstrated even though all four measured process connections matched. Warmup identities were not recorded; do not assign the unmatched warmup or invent its event. Unknown coverage remains. Selected Redis identity stayed unchanged; sensor exit zero and removed. Follow-up enumeration found no acg-falco containers; systemd-timesyncd remained active. No clock/service changes, no retries, no old evidence overwritten. Diagnostic raw logs remain ignored; ordinary normalization/paired latency analysis must not import this changed instrumentation.

Validation: 332 tests each OS, output/engine2-correlation-{windows,linux}-tests-20260930.xml; Windows 2.19 s, Linux 3.33 s. Fourteen additional test cases cover strict/minimized correlation, missing/duplicate matches, wrong scope, timestamps, helper parsing, opt-in fields and paired-report exclusion. Ruff lint/format (66 files) and Windows dependencies passed. Existing software tests remain largely synthetic; lifecycle fault injection is not exhaustive. Next: explicitly account for readiness/warmup identity and capture coverage, then predeclare repeated correlation checks rather than treating this one success as a general clock solution. INC-029 remains historically unresolved.
