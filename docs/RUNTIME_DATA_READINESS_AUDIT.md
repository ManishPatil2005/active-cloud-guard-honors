# Runtime data readiness audit — 6 October 2026

E2-035 / E2-004 / RQ3. **Offline source/receipt audit, not an independent evaluation or eligibility approval.** Starting revision dd8518d5b291f1b4d515ce81d30ddda0c7fb6779. User requested complete status and the next step after both synthetic ML implementations. This audit addresses the current plan's first dependency: establish what existing data actually represent before defining an independent benchmark. No code/algorithm, collection, fitting, service/clock setting, labels, timestamp, data role or historical evidence was changed.

## Result

Seven tracked standalone normalized captures were found within data/runtime/ and output/engine2-*.json paths: five synthetic software fixtures and two sensor-development captures. All seven pass the existing capture parser with current lab inventory; current bytes match HEAD. There are 380 stored event rows and 45 **per-file nonempty 60-second window records**: synthetic260events/43windows, sensor120events/2windows. These sums include reused observations, not unique observations or independent replications. No independent benchmark or newly eligible capture was established.

Scope excludes nested trial event objects, arbitrary/untracked files, ignored raw exports, private records, external datasets and other directory prefixes. Receipts are evidence about earlier experiments, not additional standalone normalized captures. Seven is not the number of all historical runs. Parsing/hashes establish selected consistency, not provenance authentication, real-time deployment identity, complete sensor delivery or semantic validity.

## Capture inventory

Counts in the kinds column are process_start / network_connect / file_open. Window size here is an audit convention (60seconds), not approval of a future annotation unit.

| Capture | Declared source / role retained | Events; kinds | Nonempty windows | Independent-use boundary |
|---|---|---|---|---|
| [Replay baseline](../data/runtime/baseline-synthetic.json) | Synthetic software fixture | 9; 3/3/3 | 3 | Authored counts, no real benign recording |
| [Replay observation](../data/runtime/observation-synthetic.json) | Synthetic software fixture | 12; 1/10/1 | 2 | Authored count changes, no attack ground truth |
| [Intake example](../data/runtime/intake-example/captures/synthetic.json) | Synthetic intake fixture | 3; 1/1/1 | 3 | Supplied votes/IDs are fixture data, not actual independent humans |
| [ML baseline](../data/runtime/ml-baseline-synthetic.json) | Synthetic ML development | 206; 48/63/95 | 32 | Already used to develop both optional models; not held-out evaluation |
| [ML observation](../data/runtime/ml-observation-synthetic.json) | Synthetic ML development | 30; 4/19/7 | 3 | Already scored during development; not untouched test data |
| [Instrumented capture](../output/engine2-instrumented-normalized-20260928/capture.json) | Normalized sensor export / development | 80; 4/2/74 | 1 | Canary/workload activity and partial coverage; no independent labels |
| [Earlier smoke capture](../output/engine2-normalized-20260928/capture.json) | Normalized sensor export / development | 40; 2/1/37 | 1 | Same development scenario family as instrumented capture; not an independent split |

Exact current SHA256:

| Capture | SHA256 |
|---|---|
| Replay baseline | 80c027feb962da021071cb04c4779f22af63606e040df2a50d0e04c25d832389 |
| Replay observation | c1e188afed2ee56a5467d6984114f3fb8a480614c86093d9c86589134f791c83 |
| Intake example | b240bfcb239a1beca18a30288c9f16389ed1fb5f8612b7a45cd6e62cff08f837 |
| ML baseline | 2bc41637da6621a43f31eb761ea2f927593c8b99d805565800b5cd5031d5b18b |
| ML observation | a752468776d6b60f0feacf81bb9c6e3a215d65b93615eeea525ede536dfc5509 |
| Instrumented capture | 948aecb953f522ee49521a871b9179d263a21aebb238bda15a8ba9ee582ffebc |
| Earlier smoke capture | 5dc76e982fec7258ebebeeb96f2021271a1d8b8d8acedc83f1871d1ddb6fb2ae |

Lab inventory SHA256: 80cba29b5afd5fc8ec6d217d19bc3b2002a90f43ecec514219803e2cb9e2930a. Using that inventory for parsing does not change the intake example's own bound inventory or attest either deployment.

## Reuse and grouping findings

All seven capture byte hashes and capture IDs are distinct. That does **not** establish independent data:

- Replay observation and intake example share two exact runtime event projections `(asset_id, container_id, epoch, kind)` despite different capture IDs/scenario-group strings. An actual call to existing runtime.analyze with these as baseline/observation rejects with baseline/observation event overlap. No production guard change required. These are examples for different software workflows, not a demonstrated contamination of an executed research split. INC-055 preserves this audit finding.
- Both sensor captures declare scenario_group=redis-ping-development. They must not be separated into nominally independent train/test families merely by different filenames/capture IDs. No split was assigned here.
- No other cross-file intersections were found under that **exact** projection. This is not semantic deduplication, independence proof or exhaustive detection of related workloads. Synthetic data remain development even with disjoint hashes/groups.
- Synthetic labels/fixture reviewer IDs/adjudication must never be promoted into real blinded annotation. Already examined ML observations cannot become an untouched test set.

## Selected historical receipt review

The [40-event accounting](../output/engine2-normalized-20260928/accounting.json) and [80-event accounting](../output/engine2-instrumented-normalized-20260928/accounting.json) both record normalized/receipt_counts_match=true/rejected_record_count=0, but collection_coverage=partial_or_unknown, binding_verified=false and sensor_dropped_events=null. Those accounting fields are saved facts, not a current raw-export re-normalization or proof that every expected target event was captured. Existing typed-receipt tests separately check the 80-event saved agreement. [Instrumentation](ENGINE2_INSTRUMENTATION.md) retains its readiness and attribution limits.

The [5October readiness manifest](../output/engine2-readiness-repeats-20261005/manifest.json) records three planned/launched trials, zero unlaunched, accepted/accepted/failed and overall failed. All three receipt SHA references match current files. [Trial3](../output/engine2-readiness-repeats-20261005/trial-3.json) retains local harness clock within_tolerance=true **and** correlation.zero_excluded_samples=4. Local clock compatibility does not erase all four collector alignment failures. No retry, pooling, offset repair or retrospective acceptance here; [original review](READINESS_REPEATS.md)/INC-032 remain authoritative for that experiment.

Selected exact receipt hashes: 40accounting6739693e30af106d697c9036605f39f47f9fea73f025f9094b49b5a4afe426ae; 80accountingba81f26db9ceea18714d5d80edd755ae096a59e5eb72729ed64cc5406abf8a13; repeatmanifestca0366b8e579cf37c3da2014c9f28ab2220d700d48d921353e611983661013cc; trial3f5d55687535f85eb47e7b4a497e057203fdd0012d09344069824de124cf8f1c0. Hash consistency is not independently authenticated experiment history.

## What must happen next

No gate is approved by this audit. Use the [draft16-gate checklist](RUNTIME_CAPTURE_ELIGIBILITY.md) and [actual supervisor decision sheet](templates/runtime-supervisor-review.md), not a generated approval.

| Order | Required next outcome | Why it is needed / current state |
|---|---|---|
| 1 | Actual approved threat/label target, sufficient independent context, units/groups/sample and analysis plan | G01/G09/G11; pack is draft. Count deviation alone cannot mean confirmed attack |
| 2 | Separately reviewed authorized comparable capture protocol with timing/identity/readiness/coverage/exclusion evidence | G02..G08/G15/G16; current sensor data exploratory, alignment/coverage unresolved; generic proceed does not approve a clock/service intervention |
| 3 | Neutral evidence packets and two genuinely independent human submissions, original votes/unknowns/adjudication retained | G12/G13/G14; fixture IDs/votes are not human work |
| 4 | Freeze grouped held-out data, training/calibration/features/hyperparameters and statistical analysis before evaluation | G10/G11; keep development data out, audit semantic as well as exact duplication |
| 5 | Measure all three Engine2 methods on the same approved untouched groups, including abstention/FN/FP/delay/uncertainty/overhead | Existing software prototypes make this possible, but no research fitting/effectiveness result exists yet |
| 6 | Evaluate bounded Engine1/runtime integration and prepare reproducible paper/thesis artifacts with limitations | Do not claim production readiness, validated TCI, energy savings or general cloud accuracy from synthetic tests |

Work that needs actual people or new operational authority is not silently performed. Share genuine supervisor decisions before accepting data/creating annotation packets or designing a new live study. No invented percentage, completion date, sample-size approval or third engine is implied.

## Read-only reproduction and verification

The following exact PowerShell stdin command was executed from repository root with the existing Python environment. It prints selected hashes/counts and asserts known outcomes. It writes no audit file, changes no input and fits no model. On Linux the Python body can be executed using its environment's interpreter. Assertions are a checkpoint against these current fixtures, not a universal dataset validator; intentional later data changes require a new versioned audit, not editing this history.

```powershell
@'
import hashlib
import itertools
import json
import subprocess
from collections import Counter
from pathlib import Path
from cloudguard import runtime
from cloudguard.verification import load_inventory

tracked = subprocess.check_output(['git', 'ls-files', '-z']).decode().split('\0')
assets, inventory_hash = load_inventory('testbed/inventory.json')
records = []
for name in tracked:
    if not name.endswith('.json') or not name.startswith(('data/runtime/', 'output/engine2-')):
        continue
    value = json.loads(Path(name).read_text(encoding='utf-8'))
    if not isinstance(value, dict) or not all(key in value for key in runtime.CAPTURE_SCHEMA['required']):
        continue
    capture = runtime.load_capture(name, assets)
    records.append((name, capture))
assert len(records) == 7
assert Counter(c['source'] for _, c in records) == {'synthetic': 5, 'normalized_sensor_export': 2}
assert sum(len(c['events']) for _, c in records) == 380
assert sum(len(runtime.windows(c, 60)) for _, c in records) == 45
assert len({c['sha256'] for _, c in records}) == 7
assert len({c['capture_id'] for _, c in records}) == 7
for name, capture in records:
    assert hashlib.sha256(subprocess.check_output(['git', 'show', 'HEAD:' + name])).hexdigest() == capture['sha256']
    print(name, capture['sha256'], len(capture['events']), len(runtime.windows(capture, 60)))
pairs = [(a, b, len(runtime.event_keys(x) & runtime.event_keys(y))) for (a, x), (b, y) in itertools.combinations(records, 2) if runtime.event_keys(x) & runtime.event_keys(y)]
assert pairs == [('data/runtime/intake-example/captures/synthetic.json', 'data/runtime/observation-synthetic.json', 2)]
try:
    runtime.analyze(['data/runtime/observation-synthetic.json'], 'data/runtime/intake-example/captures/synthetic.json', 'testbed/inventory.json')
except ValueError as error:
    assert str(error) == 'baseline/observation event overlap'
else:
    raise AssertionError('overlapping fixtures were not refused')
manifest_path = Path('output/engine2-readiness-repeats-20261005/manifest.json')
manifest = json.loads(manifest_path.read_text())
assert manifest['status'] == 'failed' and manifest['planned_trials'] == 3 and manifest['not_run_trials'] == 0
assert [row['status'] for row in manifest['trials']] == ['accepted', 'accepted', 'failed']
for row in manifest['trials']:
    name = 'output/engine2-readiness-repeats-20261005/trial-' + str(row['trial']) + '.json'
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == row['receipt_sha256']
trial = json.loads(Path('output/engine2-readiness-repeats-20261005/trial-3.json').read_text())
assert trial['measurement']['clock_sampling']['within_tolerance'] is True
assert trial['correlation']['zero_excluded_samples'] == 4
print('PASS: seven current captures match HEAD; overlap rejected; failed batch and all three receipt hashes preserved')
print('Inventory SHA256:', inventory_hash)
print('No collection, model fitting, labels, eligibility approval or source changes')
'@ | .venv/Scripts/python.exe -
```

Fresh existing test subsets/receipt paths/outcomes are in [EVIDENCE](EVIDENCE.md) and WL-064 [WORK_LOG](WORK_LOG.md). No new executable source or tests were added; prior full-suite1,148collected checkpoint remains the latest full suite, not a newly executed run. Audited original capture/receipt bytes remain unchanged.
