# Full-minute capacity and clock-admission refinement

## QA-047 follow-up: receipt consistency and native validation

18 October 2026 · E2-003/E2-005/E2-025/RQ3 · WL-124.

Three additional offline regressions were reproduced: a boolean sampling width
was accepted as zero, and altered dispatch/round-trip values passed their limits
while contradicting the command's saved clock brackets. `validate_timing` now
requires nonnegative integer nanoseconds, excluding booleans/floats, in every
sample and transport measurement. It reconstructs monotonic brackets exactly
from midpoint and width (including odd widths), requiring dispatch after the
pre-call sample ends and completion before the post-call sample begins.
No timing limit changes. These checks do not authenticate receipts or continuously
monitor clocks. The scheduler and underlying clock source are unchanged.

[Before-fix results](../output/clock-receipt-before-20261018-qa047.xml) preserve
three failures/31 passes and two cache-permission warnings. Negative-span rejection
already passed and is not a newly reproduced defect. Fresh local caches avoid
those warnings in the [final Windows targets](../output/clock-receipt-final-windows-20261018-qa047.xml):
201 passed, one existing Linux-only skip. The [full offline Linux suite](../output/clock-receipt-full-linux-20261018-qa047.xml)
passed 2,164 tests with zero skips. Eighteen new cases include odd sampling widths
and valid virtual receipts. No core package source changed; the existing QA-046
Linux wheel/installation passed the full suite's package identity checks.
Separate Windows installed-package checks passed eight tests; documentation
checker tests passed three. Lint, 174-file formatting and both pip checks passed.

### Capacity remains an empirical blocker

The fields-only profile and nonrotating capped file remain unchanged. Saved suffix
reduction does not establish the byte rate of the missing prefix. Archive headers
and padding consume the fixed 1,000,000-byte export budget: a file below its ceiling
can still be unexportable. That path must reject and retain the owned stopped
container. Increasing caps, retaining more files, filtering events or shortening
the minute would change the protocol and cannot manufacture a pass.

No offline patch establishes the historical clock writer, stable WSL timing or a
future minute's capacity. QA-044 remains rejected at 129.243 ms disagreement with
21 of 60 measured connections retained. Missing events are not reconstructed.
No new sensor, workload, clock observation, clock setter or service change ran.

### Native acceptance checklist before real-data testing

This is **not authorization or a claim these checks ran**. Validation can start
in existing WSL; a dedicated native Linux host/VM is the fallback if WSL cannot
satisfy the same gates.

1. Establish repeatable full-window wall/monotonic consistency under intended
   load, not just an NTP flag or short idle pass. Preserve simultaneous clock-domain
   and collector timestamp evidence to investigate divergence. Do not fit/subtract
   offsets to admit failed data. Service/host-agent changes need separate approval.
2. Verify the pinned Falco image actually emits the seven-property profile and
   every selected structured field. Validate append/no-rotation, flush/stop,
   file-size saturation and bounded binary archive export. Verify export failure
   preserves evidence. YAML parsing/inert-child fsize tests are not producer tests.
3. Measure the complete two-readiness plus 60-call workload and capture tail,
   including all selected process/file events and archive overhead, under unchanged
   byte, metrics, resource and watchdog limits. Overflow must reject; extrapolating
   missing prefixes cannot qualify capacity.
4. Pass all PID/container/event-time brackets, pre/post running identity, whole
   UTC minute, metrics brackets/gaps and selected drop deltas together. Zero drops
   alone do not prove coverage. Preserve first failures without automatic retries.
5. Verify removal of only the trial sensor and restoration of prior Redis/any
   explicitly authorized temporary service state. Qualified development data still
   does not supply independent labels, evaluation, novelty or production acceptance.

Exact commands and verification closure are recorded in WL-124.

18 October 2026 · QA-046 · E2-003/E2-005/E2-025/RQ3 · WL-123.

The changes below are implemented and software-tested. **No live trial, Docker
invocation, Redis workload, time-service intervention or fresh clock observation
was performed.** The underlying WSL timing cause and complete full-minute capture
remain unqualified. This is runtime plumbing, not another engine or stack change.

## Capacity: remove duplicate presentation, not events

The earlier no-overwrite fix preserved evidence prefixes but could not guarantee
that a verbose minute fits the unchanged 1,000,000-byte cap. The new producer
profile omits only Falco's optional human-readable `output` string. It retains
every structured `output_fields` value (including raw timestamp, event time, PID,
successful result, syscall type and full cgroup string), plus the other envelope
metadata. It does not sample, aggregate, narrow syscall kinds or omit connections.

Falco documents the switch in its version-matched
[0.45.0 configuration](https://raw.githubusercontent.com/falcosecurity/falco/0.45.0/falco.yaml).
The new [falco-window-fields.yaml](../testbed/falco-window-fields.yaml) explicitly
keeps structured fields enabled and the alternate duplicate `message` disabled.
Both older collector configurations remain byte-unchanged. Native behavior of this
new configuration is **not** tested by parsing YAML or consulting upstream source.

New lease/coordinator receipts declare version 3 and `falco_fields_only_v1`.
`connection_counts(..., fields_only=True)` requires the exact seven-property
envelope; its default still requires the original eight-property envelope.
Neither profile silently accepts the other. All prior strict scope, PID, numeric,
timestamp, event-kind and byte checks remain. The normalizer for historical smoke
captures is unchanged. The new format is not lossless byte compression: a duplicate
display string is deliberately omitted, and original historical bytes are retained.

### Measured offline result and its limits

[Saved-data and package receipt](../output/capacity-timing-saved-review-20261018-qa046.json)
binds QA-044's raw hash, 132-record journal, 99 source hashes rechecked against its
original Git commit, both new wheels and all 43 current core-module digests.

| Saved suffix accounting | Bytes |
| --- | ---: |
| Original final export | 902,464 |
| Fields-only serialization of the same 832 events | 537,199 |
| Reduction | 365,265 (40.474%) |
| Two-copy serialization stress input | 1,074,398 — rejected |

Every retained structured field and remaining envelope value compares equal,
and connection accounting is identical. Only 21 of the original 60 measured
connections are available; the missing 39 are not reconstructed. The two-copy
stress repeats records deliberately: it is not a new minute, independent sample
or admissible dataset. It proves the unchanged byte gate still rejects overflow,
not that a future full minute will fit. Actual producer spacing/encoding and event
rate still need native qualification. Tar overhead further reduces usable payload
under the unchanged export-pipe cap.

All QA-045 no-overwrite safeguards remain: nonrotating file, fsize ceiling,
bounded regular-file archive export and retention of a stopped owned container
on saturated/unexportable evidence. No buffer, file count, byte budget, resource,
watchdog, event-count limit or workload allowance was increased.

## Timing: recompute admission instead of trusting status

Two additional software defects were reproduced, independently of the unresolved
host issue:

1. The initial scheduled offset skipped the cumulative pre-command check, so a
   known clock fault could allow one PING before rejection. Both signed failures
   now stop before the first callback. An identical initial zero-elapsed sample
   remains permitted for virtual/coarse clocks; sampling-width limits still apply.
2. Final capture admission trusted `workload_timing_accepted=True` plus local
   command checks without recomputing the minute. Virtual reports with changed
   minute endpoints and an unchanged acceptance flag were wrongly accepted.

`validate_timing` now recomputes minute duration/disagreement, all command-local
and cumulative endpoints, ordering, dispatch/round-trip limits and stored summary
agreement before capture acceptance. New scheduling metadata declares
`cumulative_window_samples_v3`. Tests retain the exact signed 50 ms boundary and
reject inconsistent status/summary, a short minute and sampled transient drift.
No timestamp correction, fitted offset, clock setter or tolerance change.

These checks prevent invalid admission; they do **not** make WSL stable, authenticate
UTC or prove every transient was sampled. The retained collector source review
describes a boot-offset timestamp mechanism, but QA-044 lacks the simultaneous
calibration/clock-writer history needed to identify a unique cause. No patched
clock source, new provider or alternative client/workload was introduced.

## Verification and delivery

- [Five before-fix failures](../output/capacity-timing-before-20261018-qa046.xml), including both initial-call and both flag-trust regressions.
- [First target](../output/capacity-timing-first-20261018-qa046.xml): 127 passed, one Linux-only skip, before 17 further cases/transport targets.
- [Final Windows targets](../output/capacity-timing-windows-20261018-qa046.xml): 183 passed, one Linux-only skip.
- [Windows installed-package checks](../output/capacity-package-windows-20261018-qa046.xml): eight passed.
- [Full Linux suite](../output/capacity-timing-full-linux-20261018-qa046.xml): 2,146 passed, zero failures/errors/skips, including matching fresh package checks.

Lint, 174-file formatting and both dependency checks pass. Fresh Windows/Linux
wheels were built and installed offline because the shared correlation module
changed; all 43 archived/installed modules match current source. Distinct wheel
hashes are retained, not a byte-reproducible-build claim. Original environments,
weights, vector stores, baseline and historical evidence were not replaced.

Remaining: actual WSL clock cause/remediation, native v3 producer/export validation,
adequate full-minute capacity and timing/identity/coverage qualification. Independent
labels, fitting/calibration, held-out comparisons, novelty and production acceptance
are not supplied by these tests. Any native trial or service change requires a new
scope/approval. Exact commands and publication closure: WL-123 / INC-101 / ADR-096.
