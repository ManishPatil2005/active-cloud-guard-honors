# Journaled full-window development qualification

18October QA-042: the separately approved fixed-settling clock-only comparison
passes64post-settling samples narrowly (maximum47.943999ms/50ms). Baseline
unstable; guest service restored. This did NOT execute the coordinator or a sensor
workload. Combining that intervention with the integrated qualification requires
new scoped approval; original timing/identity/coverage/drop gates remain unchanged.
[Evidence](WSL_TIMING_REMEDIATION.md). No live UTC alignment or coverage acceptance.

18October QA-043: `utc_boundary_single_recheck_v2` repairs the wait deadline for
small accepted backward adjustments, with one additional wait<=50ms and both
samples retained. The original50ms clock and0..100ms boundary gates still apply
to the fresh final sample. Large changes remain rejected; no historical result
is corrected. [Tests and actual clock investigation](WSL_TIMING_REMEDIATION.md).
The first guest-NTP comparison failed and restored state; no new sensor trial or
full-window coverage acceptance. At that checkpoint the revised comparison still
needed fresh approval; its later limited result is recorded above.

## Latest observed outcome - QA-035 / WL-113

The owner explicitly approved one new trial after WL-112. It ran once at source
29cd9c470e4df90cc5200bbc9c0023d5350185e5, with the same pinned image and watchdog,
and rejected at UTC alignment before any of the 60 measured PINGs. Both readiness
PINGs returned PONG; the second PID had exactly one event within its command
clock bracket. The first PID had no matching connect event, as in the earlier
trial; readiness does not establish full capture.
[Minimized actual receipt](../output/window-trial-native-summary-20261011-qa035.json).

All 11 journal records passed structural review; both rejected alignment samples
are present. Recomputed wall-minus-monotonic elapsed difference: 5,473,448,109 ns
over 57,364,514,565 ns, sampling uncertainty 1,217 ns. UTC-boundary error:
5,473,528,008 ns. Unchanged 50 ms clock-disagreement and 0..100 ms boundary gates
both reject. No measured workload or full-window capture review was reached.

The selected 99 source hashes stayed unchanged. Exported 45,863-byte raw log and
101,954-byte metrics file hashes match; 59 metrics snapshots show 26,218
collector-wide events and zero selected reported drop deltas, not complete
telemetry or Redis coverage. Owned sensor cleanup verified; a separate
exact-nonce inventory found no remaining container. Redis restored to its
observed original stopped state, same loopback binding/restart policy. Earlier
QA-030 journal/raw hashes remain unchanged.

Timedatectl reports NTP=yes and NTPSynchronized=yes before/after this trial,
unlike QA-033's negative synchronization state. Timesyncd remains active/running/
enabled. No clock/time-service changes by this trial and no concurrent kernel
discipline trace: the flag transition's cause, timing writer and mechanism are
unknown. A positive synchronization flag did not establish stable elapsed
relationships. Neither a causal fix nor qualified UTC is claimed (INC-091).

This new one-trial authorization is consumed. No automatic retry, downloads,
production target or clock intervention. Next requires a separately scoped
timing investigation/qualified-host plan, not relaxed acceptance or repeated
success-seeking trials. Independent data/review/calibration and publication
claims still require actual research evidence. Original outcomes below remain
unchanged; source/test behavior was not edited for this evidence-only milestone.

## Earlier observed outcome - QA-031

The one approved native trial at e9cc775 rejected during UTC alignment before any
measured PING. Two readiness PINGs ran; second PID connection observed. Raw binary
export and owned cleanup passed; Redis restored to its original stopped state.
The initial recorder omitted the rejected alignment end sample; that gap is now
regression-tested and fixed. Rejected results are preserved, not repaired retroactively.

One sensor-free follow-up using the corrected recorder measured2.064462457seconds
wall-minus-monotonic difference over47.690497544seconds, and2.064615290seconds UTC
boundary error. Existing50ms/100ms thresholds reject. Clock writer/root cause and
full-window native qualification remain open. No new sensor trial or time-service
change. Actual data: [native summary](../output/window-trial-native-summary-20261011-qa030.json),
[clock summary](../output/window-alignment-native-summary-20261011-qa031.json).

Read-only clock observation (fresh directory; no sensor, workload or service operation):

```text
/var/tmp/acg-vector-candidate-linux-20261010-qa018/bin/python scripts/window_trial.py --directory output/runtime-raw/alignment-NEW --alignment-only
```

This command runs one wait to the next UTC minute and stores first/last samples,
comparison, boundary error and rejection reasons. A passing later observation
would not resolve historical cause or establish runtime stability. Do not poll
until green. No further observation is scheduled.

QA-030 / E2-003 / E2-005 / E2-004 / RQ3; 11 October 2026.

## Purpose and authority

`scripts/window_trial.py` connects the existing scheduler, Redis transport and
owned Falco lease. This is one development-family qualification, not an
independent benchmark, fitted detector, threat label or production rollout.
Python, Compose, Ollama, Chroma and both engines are unchanged in purpose.
The owner explicitly approved one trial in this chat: two readiness PINGs and
60 measured PINGs, the existing pinned Falco image, maximum150second watchdog,
retained evidence and only owned sensor cleanup. Separately approved starting
Docker Desktop without settings changes. Neither approval authorizes automatic
retries, time-service changes, arbitrary workloads or dataset collection.

## Implemented sequence and acceptance

1. Require Linux plus the explicit CLI flag, full target container ID and local
   Unix socket. Reserve a fresh journal directly below ignored
   `output/runtime-raw`; existing paths refuse before any external operation.
2. Freeze hashes of all top-level cloudguard/scripts Python files, collector
   config and inventory, with250file/8MB total caps. This is local source binding,
   not a signed runtime/import/dependency attestation.
3. Persist launch intent, selected target/socket and lease recovery name/nonce
   before calling the existing owned lifecycle. Same pinned no-pull image,
   capabilities,140second Falco duration and150second TERM/3second kill watchdog.
   Ownership checks, uncertain-launch refusal and export-before-remove remain.
4. Perform exactly two identified PINGs, each followed by one second wait.
   Require the second unique PID connection in the bounded readiness snapshot
   and within its command clock bracket; record snapshot hash. First-canary
   absence remains possible and is not silently converted into success.
   Reject readiness exceeding10seconds or existing clock tolerances.
5. Check the same selected Redis identity using a separate60call transport.
   Choose the next UTC-minute boundary; wait using monotonic time in at-most
   0.5second sleeps. Reject clock disagreement or starting more than100ms late.
6. Execute the unchanged60second scheduler:60PINGs, fixed one-second offsets,
   250ms dispatch lateness,750ms round trip,100ms end lateness,50ms clock
   disagreement and5ms sampling spans. Journal each intent/result. No catch-up,
   duplicate replacement or adaptive retry. Journal I/O is part of measured
   elapsed/round-trip overhead; these are not Redis-only or sensor-only costs.
7. Verify selected post-identity, wait a fixed two-second metric tail, then
   cleanup. Journal/storage failure never suppresses an owned cleanup attempt.
   Preserve bounded raw log and metrics files before removal, flush/fsync them.
   A stopped container remains if raw export fails. Never remove foreign assets.
8. Recheck source hashes and raw hashes. Require60distinct measured PIDs, one
   event each, all command clock bounds including zero and all selected events
   within the intended half-open UTC minute. Require second readiness event in
   final export. Reuse strict raw parser and metrics summarizer. Metrics must
   bracket the full minute, remain ordered/nonreset, have no interval larger
   than2.5seconds and zero selected reported drop deltas.
9. Only then emit `development_checks_passed`. Always keep independent evaluation,
   labels and full telemetry completeness false. Global metrics and observed
   command events do not prove all syscalls were delivered or clocks authenticated.

## Durable evidence and recovery

Journal: exclusive numbered JSON records, hash-linked predecessors, flush/fsync
per record and directory fsync on POSIX. Limits160records,300KB per record,
4MB total. Final `terminal` record seals the writer. Partial/torn files, altered
links, gaps and records after terminal fail the read-only reviewer. A valid
terminal record can describe a rejected experiment: structural completion is
not experimental acceptance. No automatic resumption, replay or cleanup by
the reviewer. Inspect incomplete intent and exact owned lease before operator
recovery. A hash chain is not an authenticated signature.

Windows directory fsync is unavailable in this implementation. Filesystem,
daemon, kernel scheduling and image watchdog behavior remain trusted assumptions;
fsync does not prove hardware durability on every filesystem. Hard parent death
cannot write a final record or guarantee remote-exec completion. A watchdog
stops the sensor process, not automatic container removal. Late/uncertain daemon
delivery remains unknown. Original systemd/time-service protocols are untouched.

Binary export correction: `run_bounded(..., binary=True)` retains bytes under the
same pipe, deadline, cleanup and combined-size controls. Default text mode still
strictly rejects invalid UTF-8. Only sensor `docker cp ... -` uses binary mode;
the bounded single regular fixed-name tar member is read without path extraction.
This removes the previous unnecessary UTF-8 restriction on tar headers.

## Operator commands

Use the existing qualified Linux interpreter, exact checked target and explicit
socket; replace NEW with a never-used directory. Do not run without separate
operational authorization. This command consumes one trial, including failure.

```text
/var/tmp/acg-vector-candidate-linux-20261010-qa018/bin/python scripts/window_trial.py --directory output/runtime-raw/window-trial-NEW --target FULL_CHECKED_CONTAINER_ID --endpoint unix:///var/run/docker.sock --approve-development-trial
```

Read-only recovery does not launch or remove anything:

```text
/var/tmp/acg-vector-candidate-linux-20261010-qa018/bin/python scripts/window_trial.py --directory output/runtime-raw/window-trial-NEW --review-only
```

The journal and raw paths stay private/ignored. Publish only reviewed minimized
summaries and hashes. Historical outputs and25second sensor scripts remain intact.

## Verification and remaining work

Virtual-clock/fake-daemon tests cover the complete selected success path and
launch, readiness, clock, PID, event offset, metrics drop/gap/bracketing, source
mutation, interruption, storage failure, cleanup failure and journal corruption.
Actual harmless Python children exercise binary/text process transport.
Exact executed commands/results and any native trial outcome are recorded in
[WORK_LOG](WORK_LOG.md), WL-107. Do not infer live success from these tests.

Next gates: actual native result and offline audit; separately designed
repeatability/representativeness and matched sensor-off controls; real independent
scenario/context definitions and reviewers; eligible real-data evaluation,
calibration/ablations/cost measurements; manuscript and replication review.
No independent data, labels, novelty or production acceptance is created here.
