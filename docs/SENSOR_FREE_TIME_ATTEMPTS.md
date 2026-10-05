# Sensor-free TIME bracket diagnosis

E2-021, declared 5 October 2026 before execution. User requested continuation, documentation and coherent named commits. INC-033's failed sensor read has no retained endpoints; that historical cause cannot be recovered. This is a **new sensor-free diagnostic**, not a replacement trial, overhead study, collector calibration or independent detection benchmark.

## Fixed method and acceptance

Extend the existing scripts/clock_bridge.py with opt-in `--record-attempts`; reuse E2-020's sanitized TIME recorder extracted to scripts/sensor_trial.read_time. Importing that module does not start a sensor. Existing mode/protocol and Engine 1 unchanged. New protocol redis_time_failure_evidence_v1: at most six sequential fixed Redis TIME commands, one-second sleep between accepted reads (five maximum), no PING. Stop immediately at any rejected bracket, command or sampling failure; no retry, replacement, grace-period extension or limit relaxation. Each TIME command timeout remains five seconds; accepted bracket <=500 ms, endpoint disagreement plus sampling uncertainty <=50 ms, individual sampler span <=5 ms. Preflight/identity commands retain their existing timeouts; fixed count/gaps are not a hard global wall-time guarantee under scheduling stalls.

Use only existing local Docker daemon and single running lab Redis. Verify known trial name/pinned-image sensor absence before/after and selected deployment identity continuity. Endpoint sensor absence is not proof no unrelated collector ran. No service restart, clock/NTP/Windows setting change, WSL reset, container creation, credentials/data access, software installation or added permissions. Redis TIME creates small process/network activity but no application-data write. No boot-clock reads or Falco event comparison in this diagnostic.

Freeze six execution-source hashes (bridge/shared recorder/absence check, clock arithmetic/sampler, deployment gate), require unchanged on successful completion. Export phases/status, available first/last clocks, computed comparison, separate clock/round-trip rejection flags, response hash and safe failure stage/class; never raw response/stderr/error message. Preserve partial receipt on failure, including accepted earlier reads; missing postflight fields stay missing. Do not synthesize offset bounds for rejected reads. Recompute every available compare value and accepted server bracket offline, check source hashes/attempt order/identity/absence fields before interpretation. Local consistency is not authentication or independent evaluation.

Acceptance: a complete, integrity-checked six-read observation or a preserved diagnostic failure with available inputs. `observed` does not mean clock drift or collector error fixed. Failure distinguishes clock incompatibility, sample width, >500 ms round trip or earlier command/sampling error **in this new attempt only**. A clock_outside_tolerance flag alone covers multiple clock-quality conditions; inspect its numeric fields. Endpoint-compatible results cannot exclude transient excursions or explain prior Falco lag. Keep INC-032/timing-stability gate open; no baseline/ML fitting follows automatically.

## Separate execution after implementation commit

One fresh path `output/engine2-sensor-free-time-attempts-20261005.json`. Commit/push implementation first, verify remote, then execute once after Linux preflight and read-only time-service/sensor enumeration:

```text
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python scripts/clock_bridge.py --record-attempts --output output/engine2-sensor-free-time-attempts-20261005.json
```

Explicitly inspect service/sensor/lab state afterward regardless of outcome. No software test suite or sensor running concurrently by this agent. Preserve result with a separate documentation/evidence commit, including failures. No automatic future experiments implied.

## Implementation checkpoint

Mode implemented; seven new tests cover shared recorder integration, six-read/five-gap behavior, first-rejection stop/no retry, sensor/preflight refusal, identity/source change, overwrite refusal and legacy protocol preservation. Existing E2-020 seven sanitized failure tests exercise extracted code. Final suites: 421 Windows (2.00 s) / Linux (2.66 s); [Windows](../output/engine2-sensor-free-attempts-windows-tests-20261005.xml), [Linux](../output/engine2-sensor-free-attempts-linux-tests-20261005.xml). Ruff lint/format (75 files), Windows pip check passed. No live observation claimed at this implementation checkpoint; real scheduler stalls/Docker timeout modes not exhaustively injected.

## One observed run, 5 October 2026

Implementation commit `14774dd824f11b7b26074db65ba71666d7966c13` pushed/remote verified before collection. Declared command ran once at 08:11:16 UTC, exit 0: [receipt](../output/engine2-sensor-free-time-attempts-20261005.json), [offline consistency review](../output/engine2-sensor-free-time-review-20261005.json). Six accepted reads, zero zero-excluding server/harness bounds; no retry or sensor started. Selected Redis identity (including start time/restarts) unchanged; known trial sensors absent at both endpoints. External pre/post lab preflight passed, timesyncd active/unchanged and sensor enumeration empty. No other services started/recreated, clock changes or tests intentionally run concurrently.

Round trips 53.716695–85.564442 ms; maximum absolute endpoint clock disagreement 343 ns, maximum sampling uncertainty 987 ns, maximum individual sampler span 1529 ns. Five measured endpoint gaps each >=1 second. Whole first-to-last endpoint comparison: 5,392,340,834 ns elapsed, 13 ns disagreement, 449 ns sampling uncertainty. This last comparison is an **offline descriptive reduction**, not a new protocol gate, boot-clock relationship measurement or full transient-change audit. All six response hashes reconstructed from accepted Redis scalars; six selected source hashes before/after/current source matched, compare and redis_bracket recomputed exactly, order/count/flags/identity verified. These are local consistency checks, not authenticated peer time or independent experimental labels.

This later sensor-free observation did not reproduce a rejected TIME bracket. It cannot identify whether INC-033's missing inputs showed clock disagreement, excessive duration or wide sampling, nor explain INC-032's early Falco events. Successful recording path live-observed; failure-recording paths remain software-tested, not live-validated by this all-accepted run. No Falco timestamp alignment, overhead, accuracy, stability-gate pass or baseline/ML acceptance follows. Original failed receipt remains byte-identical.

### Offline reproduction of executed checks

Run against this immutable receipt and implementation sources; a later source change requires the pinned implementation commit for the source check. No Docker/model/sensor access in this reduction:

```powershell
@'
import hashlib, json
from cloudguard.verification import read_json
from cloudguard.clock_check import compare
from cloudguard.clock_domains import redis_bracket
from scripts.clock_bridge import source_hashes
r,h = read_json('output/engine2-sensor-free-time-attempts-20261005.json')
assert r['protocol']=='redis_time_failure_evidence_v1' and r['status']=='observed'
assert r['source_sha256']==r['source_sha256_after']==source_hashes() and r['sources_unchanged'] is True
assert r['identity_before']==r['identity_after']
assert r['known_sensor_absent_before'] is True and r['known_sensor_absent_after'] is True
assert all(r[k] is False for k in ['clock_settings_modified','sensor_started','falco_alignment_verified','correction_applied','independent_evaluation'])
assert r['planned_reads']==6 and r['spacing_seconds']==1 and len(r['samples'])==len(r['time_read_attempts'])==6
for i,(a,s) in enumerate(zip(r['time_read_attempts'],r['samples']),1):
    assert a['phase']==f'time_{i}' and a['status']=='accepted' and a['clock_rejection_reasons']==[]
    assert a['first']==s['first'] and a['last']==s['last']
    assert a['clock_comparison']==compare(a['first'],a['last'])
    secs,nanos=divmod(s['redis_unix_ns'],10**9)
    reply=f'{secs}\n{nanos//1000}'
    assert hashlib.sha256(reply.encode()).hexdigest()==a['response_sha256']
    assert redis_bracket(s['first'],s['last'],reply)==s
assert r['zero_excluded_samples']==sum(not s['zero_within_bounds'] for s in r['samples'])==0
s=r['samples']
gaps=[b['first']['monotonic_mid_ns']-a['last']['monotonic_mid_ns'] for a,b in zip(s,s[1:])]
assert all(g>=10**9 for g in gaps)
print(json.dumps({'receipt_sha256':h,'source_hashes_verified':len(source_hashes()),
    'round_trip_ns_range':[min(x['elapsed_monotonic_ns'] for x in s),max(x['elapsed_monotonic_ns'] for x in s)],
    'max_absolute_clock_disagreement_ns':max(abs(x['clock_difference_ns']) for x in s),
    'inter_read_gaps_ns':gaps,
    'whole_observation_endpoint_comparison':compare(s[0]['first'],s[-1]['last'])},indent=2))
'@ | .\.venv\Scripts\python.exe -
```

Next: review/predeclare a separate collector-on diagnostic with the richer rejection records and boot-clock snapshots to investigate collector conversion under observed clocks. This result does not authorize clock changes, unbounded experiments, tolerance relaxation or promotion of prior/future development data into an independent benchmark.
