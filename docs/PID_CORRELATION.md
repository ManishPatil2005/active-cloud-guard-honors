# Bounded process-ID correlation diagnostic

## Predeclared identified-readiness follow-up

One new trial after preflight, output/engine2-identified-readiness-20260930.json. Diagnostic mode retains exactly two warmup commands with one-second waits. The second canary's own PID must have exactly one successful connect in a strict validated log snapshot; an unrelated or earlier canary event cannot satisfy readiness. Duplicate current matches abort immediately; absent second match aborts before measured dispatch. The first missing match remains recorded, not retried away. Record each attempt's PID/count and snapshot hash in the receipt, including failures. Default noncorrelated readiness unchanged. No privileges/tolerance/time-service change. This proves a selected readiness event was observed, not complete collection or future uptime.

### Identified-readiness execution

[Receipt](../output/engine2-identified-readiness-20260930.json): preflight passed without environment recovery; one trial only. Warmup PIDs 57/63 each had exactly one connect in their readiness snapshots. Only after second-canary validation did measured PIDs 69/75/81/87 run; all four uniquely matched and had zero-compatible clock ranges. Final capture 246 selected records, all six command connects uniquely observed, zero unassigned. Selected Redis identity stable; sensor removed; follow-up no acg-falco containers and timesyncd active, unchanged.

This successful selected-command accounting does not establish full syscall completeness, eliminate startup variability, prove authentication or solve the historical clock discrepancy. Previous first-warmup misses remain preserved. Snapshot hashes identify the bytes read but snapshots are not separately retained, so they are not independently replayable artifacts; the final raw log is kept privately. Changes were to readiness validation, not longer waits, extra commands or retries.

Tests: Windows 343/2.07 s, Linux 343/2.82 s, separate output/engine2-readiness-{windows,linux}-tests-20260930.xml. Five new readiness cases cover own-PID success, stale-only events, ambiguity, first-canary absence retained and missing callback IDs. Shared strict parser retains previous scope/schema rejection coverage. Ruff lint/format (66 files) and Windows pip check pass. Next: freeze this diagnostic protocol and predeclare a small repeated readiness/correlation evaluation, including missing/failed runs and collector counters; do not extrapolate one success into a completeness or performance claim.

## Predeclared follow-up: warmup accounting v2

Next bounded run uses container_pid_connect_v2: the same fixed PID-print/exec helper also identifies each of the two warmup commands. No extra commands, privileges or raw fields; helper processing now affects warmup as well, so do not compare timing as unchanged instrumentation. Four measured commands retain the strict unique-match gate. Warmup results separately report unique_match, not_observed or ambiguous; absence does not automatically mean kernel drop or startup cause. All six IDs must be distinct; unknown PID connects counted separately. Even all six observed does not certify every syscall or full coverage. One fresh trial after preflight, no retries, no time-service changes. New path output/engine2-warmup-correlation-20260930.json; historical v1 evidence unchanged.

### Follow-up execution

[V2 receipt](../output/engine2-warmup-correlation-20260930.json): first warmup PID 21 had zero connect records; second PID 27 had one. Measured PIDs 33/39/45/51 each had one, all four clock bounds include zero. No unassigned connects. Total 205 selected records, five connects. all_six_commands_uniquely_observed=false and coverage remains partial_or_unknown. This localizes the missing command association to warmup attempt 1 in this run; it does not establish startup loss as the cause or retrospectively identify earlier gaps.

Before execution, preflight failed because Docker Desktop was unavailable; Windows Linux-engine pipe absent and WSL docker executable unavailable. Started existing Docker Desktop, then observed existing Redis stopped exit 255. Started only Redis with compose start, then preflight passed. No container recreation/deletion. Redis start time changed to 2026-09-30T16:39:50.097383311Z; identity stable within the new trial, not identical across historical runs. No sensor launched before preflight passed; one trial only. Sensor removed, no acg-falco containers at follow-up, timesyncd active with no time-service changes.

Full tests: Windows 338/2.53 s, Linux 338/3.96 s; output/engine2-warmup-{windows,linux}-tests-20260930.xml. Six new cases cover missing/ambiguous/complete warmup, overlapping/boolean IDs and two fixed callback invocations. Ruff lint/format (66 files) and Windows dependency checks pass. Next: make readiness explicitly require a uniquely observed identified canary before measured dispatch, retaining startup misses and fixed attempt limits. No longer waits or retries chosen merely to hide missing evidence; predeclare any revised readiness protocol before collection.

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
