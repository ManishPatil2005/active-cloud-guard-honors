# Full-minute capacity and clock-admission refinement

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
