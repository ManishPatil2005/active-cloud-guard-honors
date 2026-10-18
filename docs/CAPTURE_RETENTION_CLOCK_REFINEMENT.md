# Capture retention and cumulative-clock refinement

Historical QA-045 checkpoint below. Latest [QA-046 refinement](CAPACITY_TIMING_OFFLINE_REFINEMENT.md)
versions a fields-only producer/parser and recomputes final clock admission;
same caps, no native trial or physical-clock cure. Both QA-045configs remain unchanged.

18 October 2026 · QA-045 · E2-003/E2-005/E2-025/RQ3 · WL-122.

The user requested diagnosis and fixes without another live trial or larger limits.
Two software defects are addressed. **The underlying WSL timing problem and full
live coverage are not resolved or newly validated.** Engine 1 and the two-engine
Python/Compose/Ollama/Chroma architecture remain unchanged.

## What the saved evidence establishes

The QA-044 trial completed all 60 PINGs, but rejected the minute's clock difference
of -129.242680 ms against the existing 50 ms limit. Its final export retains only
21 measured connections. The original evidence is not repaired or relabelled.

[Offline diagnosis](../output/retention-clock-saved-diagnosis-20261018-qa045.json)
rechecks all 99 source hashes against the **original Git commit**, not today's
modified source. It also verifies the 132-record journal, raw/metrics hashes and
clock arithmetic. Before command index 19 (the 20th scheduled PING), the recorded
cumulative difference was already -68.213871 ms, with 2,198 ns sampling uncertainty.
This is a counterfactual stopping point from saved samples, not a new execution.

The final raw file contains 832 events/902,464 bytes. Repeated formatted `output`
strings alone account for 354,991 bytes. Removing that property hypothetically
would leave 537,199 bytes **for this retained suffix only**; it neither recovers
the lost prefix nor proves a full minute would fit. No field projection, sampling,
timestamp shift, filtering of event kinds or relaxed gate was used for admission.

## Fix 1: do not use rotating stdout as authoritative evidence

The earlier lease exported `docker logs` only at the end, while retaining just one
rotating log file. [Docker's logging contract](https://docs.docker.com/engine/logging/drivers/json-file/)
permits old files to be removed when the configured count is exceeded. QA-044's
missing prefix is consistent with rotation, but the removed container's rotation
history was not preserved, so that historical cause remains unverified.

The new, separately hash-bound [window configuration](../testbed/falco-window.yaml)
uses Falco's append-only file output at `/tmp/acg-events.jsonl`, disables duplicate
alert stdout and explicitly disables output buffering. The same JSON fields,
selection rule and all selected syscall kinds remain. Falco documents that this
file channel does not rotate alerts; see the version-matched
[0.45.0 configuration](https://raw.githubusercontent.com/falcosecurity/falco/0.45.0/falco.yaml).
The historical `falco-trial.yaml` and old 25-second workflow are byte-unchanged.

[SensorLease](../scripts/window_sensor.py) declares `sensor_window_lease_v2` /
`nonrotating_file_fsize_v1`. The container receives
`--ulimit fsize=1000000:1000000`; no larger capture budget is introduced. Docker
[documents this setting](https://docs.docker.com/reference/cli/docker/container/run/#set-ulimits-in-container---ulimit)
as a direct OS file-size limit. Linux can terminate a writer with SIGXFSZ or return
EFBIG when it exceeds the limit; [kernel API contract](https://www.man7.org/linux/man-pages/man2/getrlimit.2.html).
An inert Linux child test verifies the cap and unchanged prefix, not Falco's
actual signal/error behavior in the pinned container.

Readiness and final capture now read the fixed event file, not Docker's rotating
diagnostic log. Final export still follows stop-and-own verification. The bounded
tar reader permits exactly one regular, fixed-name file; it never extracts paths.
No fallback to stdout, changed image, new capability, network access or retry.

### Limits and failure behavior

| Constraint | Remains |
| --- | --- |
| Event file ceiling / export pipe | 1,000,000 bytes each |
| Metrics payload | 900,000 bytes; original 1,000,000-byte tar pipe |
| Sensor / Falco duration | 150 s TERM + 3 s kill / 140 s |
| Sensor resources | 512 MiB, 1 CPU, 64 PIDs; existing capabilities |
| Timing | 50 ms disagreement, 5 ms samples, 250 ms dispatch, 750 ms round trip, 100 ms end/alignment lateness |
| Workload | Two readiness PINGs; at most 60 measured calls, no replacements |

This is **prefix preservation, not unlimited retention**. The existing byte cap
may still prevent a full minute at this event rate. Tar headers/padding also count
toward the unchanged pipe cap: a near-cap file can refuse export even if its
payload alone fits. Saturated/unexportable evidence never earns a completed
capture; the owned stopped container is retained for operator recovery instead
of deleting the only copy or widening the bound. A capped file can end with a
partial JSON record; strict parsing still rejects it. No native container run has
validated this new path. File-size limits are per-file, not an aggregate disk
quota or a guarantee against a malicious privileged image/host.

## Fix 2: reject cumulative clock drift when it is sampled

Previously the scheduler checked each short command and the final minute. Small
changes could accumulate beyond 50 ms while every individual command passed.
A transient between-command fault could even disappear before the final check.
Four virtual regressions reproduced these gaps (both drift directions).

[window_workload.py](../scripts/window_workload.py) now declares
`cumulative_window_samples_v2`. It reuses the existing initial/before/after samples
and unchanged `compare` predicate before later commands and after each command.
The first observed failure stores `clock_stop` with phase, index, both endpoint
samples and arithmetic. It stops without another PING or compensating delay;
per-call failures retain their more specific reason. The original final-minute
gate also remains. This does not continuously observe clocks or detect every
transient between samples. New coordinator receipts declare `redis_window_trial_v2`;
source manifests bind both old and new collector configurations.

The previously reviewed pinned collector computes event epoch timestamps using
a stored boot-to-epoch offset plus kernel boot time; see
[immutable source review and its limits](COLLECTOR_TIMESTAMP_REVIEW.md).
That mechanism is a plausible contributor when the realtime/boot relationship
changes, not a proven unique cause of QA-044. Fresh browser retrieval of two old
immutable source URLs failed this turn; no new binary attestation is claimed.
No clock setter, service change, source patch to Falco, fitted offset or revised
historical timestamp was applied. A scheduler guard cannot repair host discipline.

## Verification and remaining gates

- [Before-fix regressions](../output/retention-clock-before-20261018-qa045.xml): six failures retained.
- [First corrected targets](../output/retention-clock-first-20261018-qa045.xml): 136 passed before eight additional cases.
- [Final Windows targets](../output/retention-clock-windows-20261018-qa045.xml): 143 passed, one explicit Linux-only primitive skip.
- [Final Linux targets](../output/retention-clock-linux-20261018-qa045.xml): 144 passed, including actual inert-child file-cap enforcement.
- [Full Linux regression](../output/retention-clock-full-linux-20261018-qa045.xml): 2,124 passed, zero failures/errors/skips; matching unchanged 43-module QA-040 package artifacts supplied.

Lint, 174-file format and Windows/Linux dependency checks pass. No new full
Windows/hosted qualification, package rebuild, sensor, Redis workload, service
intervention, clock diagnostic or production deployment. Full live timing and
coverage, adequate bounded capacity, real-data eligibility, independent reviews,
calibration and research effectiveness remain open. Native validation requires
separate live approval, which was explicitly not used here. Exact commands,
incidents, decisions and publication verification: WL-122 / INC-100 / ADR-095.
