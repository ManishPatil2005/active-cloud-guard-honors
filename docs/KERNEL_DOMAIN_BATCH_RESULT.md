# Approved four-block clock-domain observation

19 October 2026 · QA-051 / WL-128 · E2-005/E2-025/RQ3.

**The diagnostic completed; clock stability was not established.** All four
predefined blocks completed once, with 64 packets and 128 zero-mode kernel state
queries. Substantial wall/boot and RAW/monotonic changes were observed. No retry,
replacement block, clock/service/host change, tracing, network, Docker/Redis or
sensor operation was issued. This is diagnostic evidence, not qualified workload
data, a clock cure, an identified writer or native capacity validation.

## Approval and actual execution

The user expressly approved [QA-050's scope D](CLOCK_CAUSE_DIAGNOSTIC_PLAN.md).
It ran in one continuous `ACG-Research` WSL controller session as ordinary user
`acgresearch`, at commit `07ea13f8b3e60a09d7429ef7d4ff5d93bf6c4be8`.

Each existing kernel diagnostic retained 16 packets, 32 zero-mode `adjtimex`
queries, 15 fixed one-second sleeps and its 45-second SIGINT watchdog/+3-second
kill grace. A hard 240-second outer ceiling bounded the one-off controller.
All block, controller and outer-wrapper exit codes were zero; no watchdog expired.
The controller's monotonic elapsed time was approximately 63.814 seconds.
First-to-last sampled monotonic elapsed bounds were
[63.325564446,63.325571223] seconds. These are guest-clock observations, not an
independently calibrated physical duration or gap-free acquisition claim.

Each block was reviewed before the next was launched. Supported ABI/libc metadata,
native/source hashes, zero modes, complete packets and sampled-domain ordering
passed. Cross-block backend and domain identity/order remained consistent.
All sampling, query, byte and qualification limits stayed unchanged. No existing
native-reader, reviewer, core module, environment or package source was modified.

## Observed domain changes

The table reports conservative changes from the first to the last sample; it
does not compare unrelated clock epochs as elapsed counters.

| Relationship | Final change bounds | Interpretation limited to this batch |
| --- | --- | --- |
| Wall minus MONOTONIC |[+1.899952678,+1.899959455] s | Large disagreement; not stable under the existing 50 ms criterion |
| Wall minus BOOTTIME |[+1.899956122,+1.899956592] s | The sampled wall/boot offset changed substantially |
| BOOTTIME minus MONOTONIC |[-3.914,+3.333] microseconds | Endpoint interval includes zero; maximum cumulative absolute bound across all samples was 9.096 microseconds |
| RAW minus MONOTONIC |[+2.043345372,+2.043362939] s | Large adjusted/unadjusted elapsed disagreement |

Large adjacent wall-minus-BOOT changes were localized to these **sample intervals**:

| Zero-based block / sample | Adjacent change bounds, ms |
| --- | --- |
|1 /8 |[+988.040947,+988.041771] |
|3 /6 |[+405.496122,+405.496900] |
|3 /7 |[+506.418032,+506.418999] |

These are differences between sampled bounds, not timestamps of specific writes
or proof of instantaneous steps. Sampled tick values were 9676,9678,9688,9689,
9691,9693,9696 microseconds. Frequency values also varied; all returned time states
were 0/status8192. Such state is not proof of UTC accuracy or writer identity.
All recorded query modes were zero; the diagnostic requested no adjustment.

A constant boot-to-wall mapping would not track the measured changing offset
through this batch. That mathematical observation is relevant to the collector
timestamp investigation, but **no Falco timestamp behavior was measured here**.
Do not attribute these changes to timesyncd, a host agent or a hypervisor without
new direct evidence. The pattern does not uniquely separate steps from slewing,
identify all actors or explain every earlier failure.

## Preservation and verification

Raw context, block receipts/commands/exits/stdout/stderr, controller source,
per-block reviews, full 64-sample domain timeline, terminal record and manifest
remain private under ignored
`output/runtime-raw/kernel-domain-batch-20261019-qa051/`.
No state-changing command was issued, so no restoration was needed; this does
not assert that external time writers were inactive during observation.

The [minimized reviewed receipt](../output/kernel-domain-batch-review-20261019-qa051.json)
binds four raw block hashes, the raw manifest/terminal/controller and seven source
hashes. Offline Windows review rechecked 28 manifest-listed files, the separately
bound manifest, all seven sources against both the execution Git commit and
current source, all four native reviews and cross-block continuity. Per-block
native checks rehashed their own libc bytes; the Windows reviewer did not query
the native clock or reload/re-attest the Linux library.

A separately written [integer endpoint check](../output/kernel-domain-batch-endpoint-check-20261019-qa051.json)
recomputed all 508 first/adjacent interval results from raw endpoints and matched
the full timeline. This is an additional arithmetic cross-check, not independent
human research evaluation. The offline source/documentation target passed 58 tests.
Earlier QA-041/044/049 observations remain byte-unchanged.

## Next boundary

Scope D is consumed. No additional clock observation, writer trace, service
intervention, sensor trial or automatic continuation is authorized. Next prepare
a tightly scoped attribution proposal offline using this domain evidence. Loaded
timing, native producer/export, full-minute capacity, PID/identity/coverage,
independent evaluation, novelty and production acceptance remain open.

Exact commands, verification and publication: [WL-128](WORK_LOG.md).
