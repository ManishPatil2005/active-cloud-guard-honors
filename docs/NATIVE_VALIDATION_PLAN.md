# Native validation plan: WSL clock and full-minute capacity

QA-048 / WL-125 · 18 October 2026 · E2-003/E2-005/E2-025/RQ3.

**Prepared, not executed or approved.** This document authorizes nothing. It
defines the next bounded decisions, not a new engine, stack, dataset or benchmark.
Software basis: QA-047 commit `15597b77785a7b4ce284d3bd489e3fb4b46c7e23`;
record the actual execution commit and source hashes again before any future run.

## Why this is next

The latest actual trial, QA-044, completed 60 PINGs but rejected at 129.243 ms
wall/monotonic disagreement; only 21 measured connections survived in its export.
QA-045/046/047 repaired retention and admission software offline. The retained
suffix became 40.474% smaller, but that does not prove a complete minute fits.
See [current evidence and checklist](CAPACITY_TIMING_OFFLINE_REFINEMENT.md) and
[actual failed trial](RUNTIME_WINDOW_TRIAL.md). Nothing below relabels that failure.

## Approval boundaries

| Step | Native effects | Approval required |
| --- | --- | --- |
| A: sensor-free screen | Existing WSL clock reads and fresh private evidence files only | A wording below; does not approve B |
| B: one integrated trial | Inspect/start/restore the exact owner-controlled Redis container; one pinned privileged-capability sensor | Separate B approval after A review and controller readiness |
| C: native saturation/fault tests | Deliberate failure/saturation or extra sensor launches | Not included in A/B; propose exact separate scope if still needed |

No approval here includes service stop/restart, clock setting, Windows/host-agent
changes, WSL restart/update, downloads, image pulls, Docker Desktop startup,
production targets, scans or automatic retries. If an unavailable prerequisite
requires one of these actions, stop and ask separately. Prior one-off approvals
were consumed by earlier trials and are not reusable.

## A — next recommended approval: sensor-free screen

Use the existing `ACG-Research` distro and ordinary `acgresearch` user, current
checkout and existing Python environment. No root, Docker invocation, Redis
command, sensor, kernel attachment, service change or network query.

1. Reserve fresh children of ignored `output/runtime-raw/`; never reuse QA-044
   or any other old output. Record source hashes, interpreter and execution context.
2. Invoke existing `scripts/clock_diagnostic.py --output FRESH_CLOCK_JSON`
   once: six fixed four-second local clock comparisons, approximately 24 seconds,
   under an outer 45-second TERM watchdog with five-second kill grace.
3. Review its exit status, all endpoints and recomputed comparisons. If rejected,
   interrupted, malformed or incomplete, preserve it and stop; do not run alignment.
4. Only if that screen passes, invoke existing `scripts/window_trial.py
   --directory FRESH_ALIGNMENT_DIR --alignment-only` once under a 75-second
   TERM watchdog with five-second kill grace. It waits for the next UTC minute
   boundary, up to roughly 60 seconds, and journals alignment/endpoints/source hashes.
5. Review the terminal journal and recompute its unchanged clock/alignment gates.
   Record exit statuses and any missing terminal record. Hash raw evidence privately;
   publish only reviewed minimized findings. No configuration was changed to restore.

Each pathname must be replaced with a newly reserved absolute path before execution;
the placeholders above are an operator recipe, not a runnable batch. These outer
diagnostic deadlines do not alter sensor, workload or acceptance limits. Keep this
as one continuous WSL execution session; record interruption/restart rather than
silently resuming or treating separate sessions as the same clock history.

**A is a screen, not a full-minute or load qualification.** The first utility
checks separate four-second intervals; it does not prove cumulative 60-second
stability. Alignment-only brackets a variable wait, not 60 PINGs. No boot-domain
writer attribution, Falco calibration, capacity or repeatability follows from A.

### Exact approval A

> I approve one sensor-free screen in ACG-Research as user acgresearch: six fixed
> four-second clock comparisons under a 45-second watchdog plus five-second kill
> grace; only if those pass, one UTC-alignment observation under a 75-second
> watchdog plus five-second kill grace. Preserve fresh private evidence and failures.
> No Docker/Redis/sensor operations, clock or service changes, downloads, host/WSL
> changes or automatic retries. Keep all existing acceptance limits unchanged.

Approval A permits only these two conditional observations. A failure ends this
scope; a pass produces a review and a **new request**, not automatic step B.

## B — conditional integrated validation, not approved now

Before requesting B, review A's actual result and freeze the exact execution
commit/controller. The old ignored `tmp/qa044_integrated.py` stops guest timesyncd
and must **not** be reused. Current `scripts/window_trial.py` cleans up its sensor
but does not start/restore Redis; a separately reviewed no-clock-change outer
controller with `finally` restoration and bounded commands is required before B.
Do not claim that new controller is implemented by this plan. Prepare/test it
offline before executing B; retain the existing 180-second coordinator deadline
and 360-second outer-controller ceiling, not an expanded acquisition window.

### Fixed target and preconditions

- WSL distro `ACG-Research`; Docker endpoint `unix:///var/run/docker.sock`.
- Historical owner-controlled target ID:
  `2ac27fc25de6e18cb453cc3ced26b0405f97477af7c3584c5950b69272e91f9b`.
  Recheck exact ID, image, Compose labels, running state, restart policy, bindings
  and immutable image identity. Expected prior state is stopped, restart `no`,
  `127.0.0.1:16379` mapped to Redis 6379. A mismatch stops before mutation; no
  automatic replacement container. Do not dump unrelated container environments.
- Existing pinned sensor image, no pull:
  `falcosecurity/falco@sha256:788f1129c542171813083d4afc61b16730a47dde8c23d9c39370acef996349b6`.
- Hash-bound `testbed/falco-window-fields.yaml`, SHA256
  `0777b22af20748394a8f403e1a8e6c4c6452452a4de77f015723e463c0d2e54a`.
  Current seven-property fields-only profile; no rules/event-selection changes.
- Docker already available, no competing study/sensor, fresh private evidence
  destinations and writable storage. Record selected service/Redis state read-only;
  do not stop guest synchronization or assume its historical PID still applies.

### Limits frozen from current implementation

| Gate/resource | Unchanged requirement |
| --- | --- |
| Workload | Two readiness PINGs; 60 measured PINGs, offsets 0..59 seconds; no retry |
| Timing | 60-second minute; end lateness <=100 ms; cumulative/local disagreement plus uncertainty <=50 ms; sampling span <=5 ms |
| Commands | Dispatch lateness <=250 ms; positive RTT <=750 ms; actual transport subprocess <=0.5 seconds, combined output <=128 bytes |
| Alignment | Original clock gate and boundary error 0..100 ms; existing single bounded recheck only |
| Sensor | Falco duration140 seconds; watchdog150 seconds TERM +3-second kill;512 MiB,1 CPU,64 PIDs |
| Privileges | Network none; drop ALL then only BPF, PERFMON, SYS_RESOURCE, SYS_PTRACE; existing read-only mounts |
| Evidence | Nonrotating event file/fsize1,000,000 bytes; export pipe1,000,000 bytes including tar overhead; metrics payload900,000 bytes |
| Metrics |1-second configured interval; gaps <=2.5 seconds; bracket whole minute; zero selected drop deltas |
| Tail/identity | Existing fixed2-second metrics tail only after successful workload; exact running pre/post target identity |

The coordinator's stricter sampled fail-fast checks remain enabled. A sampled
fault stops further commands; it is not repaired by later apparent recovery.

### One-run sequence and evidence

1. Reserve journal/controller/raw directories exclusively; record consent text,
   all source/config/rule hashes, prior target/service state and timeout intent.
2. Start only the verified stopped Redis target. Launch exactly one owned sensor
   through the existing lease; record ID/name/nonce/image and command outcomes.
3. Run existing readiness, alignment and full-window coordinator once. Never bypass
   readiness to obtain data, extend sensor lifetime or pad a rejected minute.
4. On success, keep fixed tail and running identity evidence. On any failure,
   preserve the first fault and only perform bounded evidence export/owned cleanup
   and restoration. Report phases not reached; do not manufacture their receipts.
5. Export authoritative event file/metrics, record exact payload/pipe sizes and
   hashes. Validate format, complete PID matches/event time, prefix preservation,
   clock samples and metrics. Saturation, partial JSON or archive overflow rejects.
6. Remove only the exactly owned sensor after successful evidence export. If export
   fails, stop/preserve that sensor for operator recovery; do not delete the only
   raw copy. Restore Redis to its recorded prior stopped state. Verify selected
   service state unchanged; report external changes, never force a service reset.

Recovery is not allowed to erase evidence: a leftover stopped sensor is explicitly
**operator recovery required**, not verified cleanup. A process timeout cannot by
itself prove remote jobs stopped; perform bounded exact-ownership postchecks and
report uncertainty. No blanket Docker cleanup or removal of other containers.

**Success means selected development checks only:** all60measured matches, required
readiness retained, valid full-minute timing and identities, bounded complete export,
bracketed metrics and cleanup/restoration. Current code requires the second readiness
match in final export; inspect/report both readiness PIDs without silently changing
that predicate. Do not claim complete host telemetry, calibrated detection, independent
evaluation, novelty or production readiness. A single pass does not prove repeatability.

### Exact approval B, to request later

> I approve one integrated development validation in ACG-Research against only the
> exact verified existing Redis target in QA-048: start and restore its prior stopped
> state; two readiness PINGs then up to60measured PINGs over one minute; one installed
> pinned Falco sensor with the current fields-only profile,150-second TERM watchdog
> and3-second kill grace. Keep every existing byte/resource/timing/coverage limit,
> the180-second coordinator deadline and360-second outer ceiling unchanged. No
> clock/service/host changes, downloads, Docker startup, production targets or retries.
> Preserve failures privately; remove only the trial sensor after successful export,
> or preserve it stopped if export fails and report recovery needed. Verify Redis
> restoration and report any unverified cleanup. Do not proceed automatically to
> further trials or research-data admission.

The no-clock-change controller must be reviewed first; B consent never implicitly
approves the older stop/settle procedure. If service remediation is later proposed,
obtain fresh approval for the exact service, duration, rollback and comparison.

## Decision after results

- A fails: stop; review clock/session evidence offline. No sensor trial follows.
- A passes: review and prepare controller offline, then request B separately.
- B clock fails: retain partial capture; investigate writer/domain provenance.
- B capacity fails: quantify original payload/overhead and preserve stopped sensor
  if needed. Do not increase caps, omit events or substitute a shorter workload.
- B passes: report this bounded development result; design repeatability and any
  missing native saturation/fault tests under separate consent. Only qualified,
  independently reviewed observations can enter later fitting/evaluation.

No native validation ran while preparing this plan. Documentation verification
and publication receipts are in [WL-125](WORK_LOG.md).
