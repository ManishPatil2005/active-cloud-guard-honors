# Approved sensor-free clock screen — rejected at alignment

18 October 2026 · QA-049 / WL-126 · E2-005/E2-025/RQ3.

The user approved **step A only** of [QA-048](NATIVE_VALIDATION_PLAN.md).
It ran once in `ACG-Research` as ordinary user `acgresearch`, in one continuous
WSL controller session at commit `b0e9a114ef2c8005fdd51460194de5206bf25335`.
No Docker, Redis, sensor, service-control, clock-setting, network or download
command was issued. No repeat or step B followed the rejection.

## Observed result

| Observation | Result | Unchanged gate |
| --- | --- | --- |
| Six fixed four-second comparisons | All six passed | Disagreement magnitude + sampling uncertainty <=50 ms; span <=5 ms |
| Worst four-second bound |48.768863 ms; margin1.231137 ms |50 ms |
| Conditional alignment elapsed |45.003052868 seconds | One next-minute observation, not a full loaded minute |
| Alignment wall-minus-monotonic difference |+71.061457 ms | Magnitude + uncertainty <=50 ms |
| Alignment uncertainty / combined bound |0.001221 /71.062678 ms | **Rejected**,21.062678 ms over gate |
| UTC boundary error |+72.273769 ms |0..100 ms — passed separately |
| Overall step A |**Rejected: clock_disagreement** | Both clock and boundary gates must pass |

The worst four-second interval's signed difference was+48.767794 ms, with
0.001069 ms uncertainty. Short passing intervals do not override the later
longer disagreement. The existing bounded UTC recheck was not used: its
conditions did not apply. No timestamp correction or tolerance change.

## Execution and preserved evidence

The approved existing programs ran exactly once each:

1. `scripts/clock_diagnostic.py --output FRESH_CLOCK_JSON` under GNU timeout
   TERM45seconds/+5second kill grace: exit0, six complete comparisons.
2. Because those comparisons passed, `scripts/window_trial.py --directory
   FRESH_ALIGNMENT_DIR --alignment-only` under TERM75seconds/+5second kill grace:
   exit1, complete three-record hash-linked journal, rejected terminal record.

The one-off controller returned exit1 to report the rejection, not a watchdog
expiry. Both programs finished before their deadlines. Fresh raw paths were
reserved exclusively under ignored
`output/runtime-raw/sensor-free-step-a-20261018-qa049/`. Raw endpoints, command
intents/exits/stdout/stderr, controller source, approval/context, terminal record
and manifest remain private there. A partial result would also have been retained.
No changes were made that require restoration; no assertion is made that an
external time writer was absent while this read-only observation ran.

[Reviewed minimized receipt](../output/sensor-free-step-a-review-20261018-qa049.json)
binds the raw manifest, clock/terminal/controller hashes and six comparisons.
Offline review recomputed timing/boundary arithmetic, validated the three-record
journal and checked17manifest-listed files. All101execution source/config hashes
match both their original Git commit and current unchanged executable files.
The manifest itself is separately hash-bound in the receipt; it is not counted
among its own17entries. Historical QA-042/044 and prior failures remain unchanged.

## Meaning and next boundary

This is fresh evidence that the current WSL session did **not** meet the unchanged
alignment consistency gate. It does not identify the writer, distinguish a step
from rate adjustment, authenticate UTC, measure boot-domain alignment or establish
the historical failure's unique cause. The short screen was allowed to pass; the
longer observation correctly prevented progression.

Full-minute loaded timing, native fields-only producer/export behavior, capacity,
PID/event correspondence, identity and coverage remain unqualified. No Falco image
or Redis state was inspected or altered in this step. Step B remains unapproved
and must not run based on the consumed step-A consent. An idle screen pass would
not have proved capacity or repeatability either.

Next: review this evidence and prepare any proposed clock-domain/writer diagnostic
offline with an exact fresh scope. No automatic native observation, service
intervention or sensor retry. The separate no-clock-change restoration controller
can still be prepared offline, but its readiness cannot cure this failed clock gate.
Independent labels, real-data fitting/evaluation, novelty and production acceptance
are unaffected. Exact commands/checks/publication details: [WL-126](WORK_LOG.md).
