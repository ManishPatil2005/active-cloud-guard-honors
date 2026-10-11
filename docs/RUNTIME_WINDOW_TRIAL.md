# Journaled full-window development qualification

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
