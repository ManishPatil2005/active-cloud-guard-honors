# Next clock-cause diagnostic: domain-localization batch

19 October 2026 · QA-050 / WL-127 · E2-005/E2-025/RQ3.

**Prepared offline; native batch not approved or executed.** The latest actual
clock observation remains [QA-049's rejected step A](SENSOR_FREE_CLOCK_SCREEN.md).
Its consent is consumed. No sensor trial, time setter, clock/service intervention,
WSL/host change, download, tracing or new native clock read ran in QA-050.

## Question and limits of inference

QA-049 observed wall-minus-MONOTONIC disagreement over45seconds but did not sample
RAW, BOOTTIME and kernel timing state simultaneously. The next observation asks
which domain relationships change, and whether sampled tick/frequency/phase/status
changes coincide. It does **not** identify a writer or uniquely distinguish a step
from accumulated rate adjustment: changes can occur between reads, multiple actors
can act together and a guest snapshot cannot expose every host/hypervisor path.
No regression, fitted offset or timestamp correction will qualify failed data.

The existing kernel reader already supplies these measurements. Reuse it, rather
than add a new clock backend or invoke the service-changing comparison controller.
Native writer tracing or intervention would require a distinct future proposal.

## Offline improvement implemented

`scripts/kernel_domain_review.py` reads **saved files only**. It first uses the
existing kernel receipt reviewer:100,000-byte per-receipt budget, strict JSON,
16complete packets/32zero-mode state queries, supported ABI metadata, unchanged
execution sources, original summary, ordered clocks and same-domain checks.

It accepts one saved block or exactly four complete blocks. Four-block review
also requires common backend metadata and continuous ordered domain observations
across block boundaries; it rejects mixed boots, reordered/repeated blocks and
changed backends. It neither treats separately sampled clock epochs as comparable
elapsed counters nor fabricates observations in gaps between processes.

For every sample, it computes conservative **changes in offset bounds** from the
first sample and from the preceding sample, for:

| Relationship | Diagnostic value, not causal proof |
| --- | --- |
| Wall minus MONOTONIC | Directly exposes the relationship that rejected QA-049 |
| Wall minus BOOTTIME | Localizes wall/boot-offset changes relevant to collector timestamps |
| BOOTTIME minus MONOTONIC | Separates this relationship from a wall-only interpretation |
| RAW minus MONOTONIC | Exposes sampled adjusted/unadjusted elapsed disagreement |

The report preserves before/after kernel state per packet: tick, scaled frequency,
phase/units, synchronization/status fields. These are returned state, not proof of
the identity or request flags of the writer. Negative results and intervals including
zero remain visible. Output binds original input hashes, execution-source hashes
and reviewer-source hash; no input path, boot identifier or raw trace is copied.
The CLI reserves a fresh output before reading and retains a minimized rejection
on parse/review failure; it never overwrites historical reports.

### Actual saved-data review, not a new observation

The new reviewer processed the existing QA-041 file
`output/kernel-clock-current-20261018-qa041.json` without changing it. New
[derived report](../output/kernel-domain-saved-review-20261019-qa050.json):16samples,
final cumulative RAW-minus-MONOTONIC change[89,384,485,89,450,212]ns, while the
wall-minus-MONOTONIC[-9,228,19,981]ns, wall-minus-BOOT[-664,486]ns and
BOOT-minus-MONOTONIC[-9,714,20,645]ns intervals all include zero. Sampled tick
values are10000,10121,10146usec. This confirms arithmetic/observability on an older
capture, not the mechanism of QA-049, stability today or a clock cure.

No old protocol/schema, native reader, query mode, sample count, environment,
package/core module or qualification threshold changed. New tests explicitly
forbid calling the native backend. The gap filled is offline diagnostic accounting;
no production clock defect was reproduced or repaired by this feature.

## Proposed one-time native scope D

After fresh explicit consent, run a **fixed four-block** sensor-free batch in one
continuous `ACG-Research` WSL session as ordinary user `acgresearch` using the existing
`/var/tmp/acg-vector-candidate-linux-20261010-qa018/bin/python` environment.

1. Reserve a fresh ignored `output/runtime-raw/` child. Record approval, execution
   commit, controller/reviewer/native source hashes, interpreter and domain context.
2. Run the existing `scripts/kernel_clock_diagnostic.py --output FRESH_BLOCK_JSON`
   four times sequentially at most, as four predefined blocks, **not retries**.
   Each retains its original16packets,32zero-mode `adjtimex` queries and15fixed
   one-second sleeps. Total planned64packets/128state queries, roughly60seconds
   plus launch/hash overhead; this is not guaranteed gap-free or a qualified minute.
3. Keep the established per-block `/usr/bin/timeout --signal=INT --kill-after=3s
   45s` guard. Use a240second outer batch ceiling solely to bound orchestration;
   it does not extend any block or existing sensor/workload budget. These
   guest-clock deadlines are operational, not independent physical-time attestation.
4. After each block require exit0, complete receipt/source/backend checks and
   cross-block domain/order continuity before starting the next planned block.
   A failed, interrupted, incomplete, oversized or incompatible block ends the
   batch; preserve all prior/partial files. No replacement block, resume or retry.
   A measured domain difference alone is evidence to retain, not a structural
   failure to erase or a reason to repeat until it disappears.
5. Review all four saved blocks offline with the new reviewer; if fewer completed,
   report the incomplete batch and review individual complete blocks only. Preserve
   raw endpoints/states/commands privately, publish reviewed minimized findings
   and hashes. No changed state needs restoration; do not issue service resets.

The existing backend refuses root, unsupported Linux/ABI/glibc, missing native
clock support and nonzero query input. Do not install/update anything to bypass
a refusal. Fixed LP64/glibc2.39 layout checks and5ms sampling-width bounds remain.
No call with nonzero adjustment modes, process attachment, syscall injection,
system-wide tracing, Docker/Redis invocation or network query is in this scope.

Execution command shapes are templates requiring newly reserved absolute paths;
none ran while preparing this document. The one-off bounded sequential controller
must be inspected against this scope before its sole execution; old
`clock_comparison_batch.py` or QA-044's stop/settle wrapper must not be substituted.

## Exact approval needed before running D

> I approve one fixed four-block sensor-free kernel clock-domain batch in
> ACG-Research as acgresearch: each block has 16 packets and 32 zero-mode state queries,
> one-second spacing, the original 45-second SIGINT watchdog plus 3-second kill grace,
> with a 240-second outer batch ceiling. Stop on the first incomplete or invalid
> block; do not retry or replace it. Preserve private raw evidence and review
> domain changes offline. No clock/service/host/WSL changes, root, process tracing,
> downloads, network, Docker/Redis/sensor operations or automatic next trial.
> Keep every existing sampling and qualification limit unchanged.

This authorizes only D if explicitly approved later. It does not approve B's
integrated sensor trial, a new A screen, independent labels/evaluation, training
on failed observations or future service intervention.

## Decision after D

Report observed domain changes and kernel-state co-occurrences with uncertainty,
not a guessed writer. A repeatable domain pattern may guide a narrowly scoped
later attribution experiment. If no change appears, absence in that bounded
sample does not resolve earlier failures. Either result remains separate from
loaded timing, native producer/export, full-minute capacity/identity/coverage,
independent research evaluation and production acceptance. Limits stay unchanged.

Verification: final Windows targets passed 299 tests with one existing Linux-only
skip, including documentation checks. Lint, 176-file formatting and dependency
compatibility checks passed. No fresh Linux suite or native diagnostic ran.
Intermediate test failures were preserved, not replaced by the passing report.
Exact commands and publication: [WL-127](WORK_LOG.md).
