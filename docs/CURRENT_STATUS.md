# Active Cloud Guard — current capability and research status

## Latest step — existing-data audit and supervisor proposal

E2-038/E2-035/RQ3: [offline readiness audit](RUNTIME_DATA_READINESS_AUDIT.md) completed for seven tracked standalone normalized captures in selected data/runtime/output prefixes:5synthetic/2sensor-development,380stored rows/45per-file60second nonempty window records, not independent replications. All seven parse/current hashes match HEAD; two synthetic fixtures share two exact projections and existing baseline/observation guard refuses them. Both sensor captures share redis-ping-development. Historical failed repeat/three receipt hashes retained, including4collector exclusions despite local clock compatibility. No independent benchmark/new eligible data established; no code/model/data/service/clock changes.

User explicitly confirmed supervisor approval is **not obtained** and requested a proper file: [ENGINE2_SUPERVISOR_REVIEW_PROPOSAL.md](ENGINE2_SUPERVISOR_REVIEW_PROPOSAL.md), prepared **DRAFT — NOT APPROVED**, proposed target/context/safety/units/groups/annotation/calibration/evaluation/overhead/publication and pending decisions. Not a changed research question or approved/executed study. No supervisor messages sent, humans/labels fabricated, new collection/fitting or operational consent inferred.

Fresh existing offline subsets: Windows208pass1symlink-privilege skip6.69s/XML6.549; Linux209pass43.77s/XML42.210, zero failures/errors,209collected each. This documentation/source audit adds no tests/algorithms; prior1,148-case full suite below remains latest full suite, not rerun. WL-064/ADR-054/INC-055. Next actual review/approved context and claim-appropriate collection qualification, not Engine3 or more arbitrary model versions.

## Latest milestone — synthetic-only reconstruction autoencoder

Final whole-suite verification: [Linux XML](../output/engine2-autoencoder-linux-tests-20261006.xml) **1,148 passed**, 245.99 s console / 241.721 s XML; [Windows XML](../output/engine2-autoencoder-windows-tests-20261006.xml) **1,110 passed / 38 skips**, 66.63 s console / 66.602 s XML. Both 1,148 collected, zero failures/errors; 37 Linux-only and one host symlink-privilege skip on Windows. Lint/format 115 files and both dependency checks pass. Suite duration is not detector latency/overhead or clock-accuracy evidence.

[Autoencoder comparator](SYNTHETIC_RUNTIME_AUTOENCODER.md), E2-037/E2-004/RQ3, implemented/software-tested with the existing optional scikit-learn backend. Engine 2 now has statistical, Isolation Forest and reconstruction comparators; these are **not three engines**. Per-asset baseline-only scaler/network, narrower 4→2→4 reconstruction, continuous uncalibrated MSE, null binary predictions, explicit warning abstention and actual fitting diagnostics. No default/runtime-intake/Engine 1/stack change, dependency installation, real-data authority or production deployment.

Final source-bound Windows/Linux synthetic demonstrations pass six checks, three scored/zero abstained windows, no training warnings. Deliberate one-iteration run records one convergence warning, zero scored/three abstained windows and exit 1. INC-053 records test fixture lint failures; INC-054 preserves a two-failure precision regression and the fix to retain computed errors instead of six-decimal rounding. Fifty new autoencoder cases; combined final target 97 passed. [Evidence](EVIDENCE.md)/WL-063/ADR-053 distinguish historical/pre-fix receipts from final verification.

Both optional model prototypes are implemented software, **not independently evaluated security detectors**. Genuine supervisor/context/protocol decisions, comparable timing/coverage/identity/data, independent labels/grouped held-out evaluation, calibration/false alarms/misses/delay, overhead/energy and Engine 1 integration remain open. No new sensor/native/service/clock/cloud-response action or future monitoring. Earlier milestones below are historical checkpoints; references to an unimplemented autoencoder describe their earlier state.

## Latest milestone — isolated synthetic Isolation Forest software

[Optional comparator](SYNTHETIC_RUNTIME_ML.md) implemented/software-tested for **declared synthetic development data only**. This is an additional Engine2 experiment path, not a third engine or default replacement. It fits temporary per-asset Isolation Forests on baseline windows, emits continuous uncalibrated scores/null binary predictions, and explicitly counts scored/abstained units. Actual synthetic fitting occurred; real-data approval/fitting/independent evaluation remain false. Default statistical replay/intake/Engine1 unchanged. Autoencoder, calibrated real-data comparison, timing/coverage, independent labels, overhead/energy and integration remain open.

Final [Linux XML](../output/engine2-synthetic-iforest-linux-final-tests-20261006.xml): **1,098 passed**,93.06s console/XML89.757; [Windows XML](../output/engine2-synthetic-iforest-windows-final-tests-20261006.xml): **1,060 passed / 38 skips**,20.80s/XML20.792. Both1,098collected/zero failures/errors. [Final targeted XML](../output/engine2-synthetic-iforest-target-final-fixed-tests-20261006.xml):47passed3.27s/XML3.270; lint/format112files, both pipchecks pass. [Final Windows](../output/engine2-synthetic-iforest-windows-final-20261006.json)/[Linux](../output/engine2-synthetic-iforest-linux-final-20261006.json) fixed demos: all6checks pass, same3scores,3scored/0abstained, no labels/binary threat predictions/actions. Software receipts, not independent threat/clock/performance evidence.

Optional scikit-learn1.9.1/packages installed in existing environments with no existing package upgrades; Python/Compose/Ollama/Chroma/core deps preserved. INC-051 retains two test failures; INC-052 reproduces/fixes misleading all-abstention summary, with raw negative/preliminary positive artifacts kept. WL-062/ADR-052. User authorized offered synthetic-development branch, **not supervisor approval**; actual human/context/comparable-data gates still next for real research. No real telemetry/native/service/clock/model deployment or response action. Earlier checkpoints below historical.

## Earlier refinement — coordinator annotation-unit index (historical checkpoint)

[Offline unit index](RUNTIME_ANNOTATION_INDEX.md) implemented: opt-in --annotation-index/annotation_index projects sorted observed run/asset/epoch keys using existing intake checks. No votes/reasons/features/splits, labels, approval, blinding or model/action authority created. Default v1/typed reports exactly match saved results. This is a coordinator allocation aid, not a blinded packet: identifiers/epochs/hashes may reveal scenarios. E2-035 remains partial; actual supervisor decisions/comparable data/humans still next.

Latest whole-repository software verification: [Linux XML](../output/engine2-annotation-index-linux-tests-20261006.xml) **1,051 passed**,100.10s console/XML96.595; [Windows XML](../output/engine2-annotation-index-windows-tests-20261006.xml) **1,013 passed / 38 skips**,19.00s console/XML18.994. Both1,051collected,zero failures/errors. [Final target XML](../output/engine2-annotation-index-target-final-tests-20261006.xml):181pass/1symlink skip,8.15s/XML8.107;22new cases; lint/format109files/pipcheck pass. Whole-suite checks not detector effectiveness/clock/performance measurements. [Synthetic index](../output/engine2-annotation-index-synthetic-20261006.json)3units/no labels/false gates. INC-050 preserved [initial test-setup failure](../output/engine2-annotation-index-target-tests-20261006.xml); production hash guard unchanged. WL-061 commands and limits.

No newly eligible captures/independent labels, live collector/native/service/clock/model action or research approval. Python/Compose/Ollama/Chroma, Engine1 freeze, Engine2 algorithms, historical evidence and native comparison gates unchanged. Prior refinement/test sections below are historical.

## Earlier refinement — draft annotation and capture review pack (historical checkpoint)

The [coordinator pack](RUNTIME_LABELING_PROTOCOL.md), [reviewer guidelines](RUNTIME_LABELING_GUIDELINES.md), [16-gate capture checklist](RUNTIME_CAPTURE_ELIGIBILITY.md) and four blank [templates](templates/runtime-supervisor-review.md) are prepared: **DRAFT — NOT APPROVED**. E2-035 remains partial. No supervisor decision, actual reviewers, independent labels, newly eligible captures or model fitting resulted. Proposed security-review necessity is not confirmed-attack detection and needs human approval without silently replacing the research question. Current normalized counts alone lack authorization/intent context.

Latest whole-repository verification: [Linux XML](../output/engine2-research-pack-linux-tests-20261006.xml) **1,029 passed**, 77.81 s console / 75.533 s XML; [Windows XML](../output/engine2-research-pack-windows-tests-20261006.xml) **991 passed / 38 skips**, 15.30 s console / 15.290 s XML. Both 1,029 collected, zero failures/errors. [Target XML](../output/engine2-research-pack-target-tests-20261006.xml):18 passed, 0.43 s console / 0.178 s XML. Fifteen new contract tests; lint/format108files/pipcheck pass. These are software checks, not attack scenarios or clock/efficiency/effectiveness measurements.

Reserved private/runtime-labeling/ is ignored and publication-excluded even if force-staged, including case variants. No private reviewer records created; this is not encryption/access control/content DLP. Next obtain actual scope/guideline/context/group/sample/blinding decisions and establish comparable evidence-bearing captures; unknown gates do not become passed. Details/commands: WL-060. Subsequent dated verification paragraphs are historical checkpoints.

Updated 6 October 2026. This is the current status summary; dated implementation checkpoints in other documents are historical evidence, not additional engines or today's task list. Actual code, saved artifacts and their limitations take precedence over prose. Preserve Python/CLI, Docker Compose, Ollama and Chroma; no web/SaaS or cloud-account mutation is implied.

## What “complete” means here

**Engine 2's observation-only replay baseline is implemented. We are refining its experimental infrastructure; several planned capabilities and scientific validation gates remain unfinished.** Do not describe it simply as “not built,” “fully complete,” “production ready” or “validated threat detection.” A working baseline, a refinement and an independently evaluated research result are different milestones.

| Layer | Current capability | Evidence and remaining boundary |
|---|---|---|
| Engine 1 engineering baseline | Configuration checks, retrieval/local-model transport, scoped probes, bounded reuse and reviewed service observations | Frozen engine1-v2.2 at commit 6736a577f1ba08b4700daf8a86370ec3bbd1c019; [baseline](ENGINE1_BASELINE.md). Independent effectiveness/latency/hallucination/TCI calibration remain open |
| Engine 2 runtime baseline | Saved normalized captures, identity/schema validation, nonempty time windows, statistical count-deviation comparator | cloudguard/runtime.py; [foundation](ENGINE2_FOUNDATION.md). Model is statistical, uncalibrated, observation-only; low score is not safety |
| Optional runtime ML software | Synthetic-only per-asset Isolation Forest and undercomplete reconstruction autoencoder, continuous scores/abstentions, unchanged statistical comparator side by side | [Isolation Forest](SYNTHETIC_RUNTIME_ML.md), E2-036; [autoencoder](SYNTHETIC_RUNTIME_AUTOENCODER.md), E2-037. Both implemented/software-tested with actual synthetic fitting, not approved real-data models, binary threat classifiers or independent evaluation |
| Engine 2 telemetry tooling | Separate bounded Falco capture, saved-data normalization, selected readiness/identity/drop metrics and correlation diagnostics | [Instrumentation](ENGINE2_INSTRUMENTATION.md), [adapter](ENGINE2_ADAPTER.md). Not a continuously integrated sensor or independent threat benchmark; coverage/clock stability unresolved |
| Supporting refinements | Timing diagnosis, receiver, private native callback tests and inert durable job/fence records | [Receiver](SYSTEMD_RECEIVER_CAPTURE.md), [native fixtures](NATIVE_CALLBACK_VALIDATION.md), [inert gate](DURABLE_JOB_GATE.md). Experimental-safety mechanisms, not additional engines or anomaly-detection models |
| Full runtime research objectives | Not yet independently established | Runtime labels/grouped held-out data, planned ML comparisons, calibrated detection/false alarms/misses/delay/overhead and Engine1/runtime evidence integration remain open |
| Runtime research intake | Offline bounded schema/hash/group/split/window/review/adjudication and selected typed-source consistency | [Intake formats](RUNTIME_INTAKE.md), [typed receipts](RUNTIME_RECEIPTS.md), E2-035 partial. v1 opaque; v2 selected count/identity/local-endpoint checks, not full protocols/coverage/alignment/human authenticity; eligibility/fitting false |

The current replay output now includes implementation_scope for **runtime_replay_baseline** only: status implemented; saved sensor exports supported; live input/trained ML/independent detection evaluation/automatic response false. It no longer claims the entire repository has no eBPF collector. Acquisition/normalization are separate experimental paths. Added metadata/text do not change scores, thresholds, windows or leakage guards.

The isolated synthetic Isolation Forest software path is now implemented above; no real-data validated Isolation Forest/autoencoder, runtime threat classifier, automated cloud isolation, integrated runtime TCI contribution or production deployment is claimed. Original first-three-month engineering scope principally concerned Engine1; later runtime objectives are not retrospectively declared completed. See [deck audit](DECK_AUDIT.md), [requirements](PRD.md), [tasks](../TASKS.md).

## Current verification, not effectiveness

The latest draft-pack verification is above. The following implementation checkpoints are historical, with their original test counts and receipts preserved.

### Historical typed receipt verification (same date, earlier change)

Typed receipt refinement:77new software cases, including two checks of saved historical artifacts (not new observations). Full [Windows final XML](../output/engine2-typed-intake-windows-final-tests-20261006.xml):976passed/38skips (37Linux-only/one symlink privilege),15.31s console/XML15.304; [Linux final XML](../output/engine2-typed-intake-linux-final-tests-20261006.xml):1,014passed/no skips,90.48s console/XML87.088. Both1,014collected/zero failures/errors, lint/format107files/pipcheck pass. Not detector accuracy/clock/performance evidence. INC-049 reproduced three missing trial-count-check failures and fixed them; original negative XML and preliminary passing receipts/example/source bytes preserved, not presented as current validation. [Final synthetic typed example](../output/engine2-typed-intake-counted-synthetic-20261006.json) checks selected roles; [uncounted input rejected](../output/engine2-typed-intake-uncounted-rejected-20261006.json). No fitting/independence/coverage/alignment/actions; original v1 report exactly unchanged. [Contract](RUNTIME_RECEIPTS.md)/WL-059.

### Historical initial intake verification (same date, earlier change)

E2-035 intake83new synthetic software cases; targetedWindows82pass/1symlink-privilege skip2.40s. Full [Windows XML](../output/engine2-intake-windows-tests-20261006.xml)899pass/38skips (37existing Linux-only/1symlink privilege),12.13s console/XML12.126; [Linux XML](../output/engine2-intake-linux-tests-20261006.xml)937pass/no skips57.78s console/XML54.962. Both937collected/zero failures/errors, lint/format105files/pipcheck pass. Whole-repository tests, not threat accuracy/clock/performance evidence. [Synthetic intake result](../output/engine2-intake-synthetic-20261006.json)3windows/1known agreement/1disagreement/1unknown pair/no eligibility/predictions/fitting/actions. INC-048/WL-058 preserve initial sandbox and test-default-binding failures; no production path/byte guard weakened. [Contract/commands](RUNTIME_INTAKE.md).

### Historical status-clarification verification (same date, earlier change)

Status-clarification change: three new scope regressions; targeted runtime tests: 31 passed in 0.69 s. Full [Windows XML](../output/engine2-status-windows-tests-20261006.xml): 854 collected, 817 passed / 37 Linux-only skips, zero failures/errors, console 8.34 s / XML 8.343 s. Full [Linux XML](../output/engine2-status-linux-tests-20261006.xml): 854 passed, zero failures/errors/skips, console 39.56 s / XML 37.570 s. These are **whole-repository software tests**, not 854 attack scenarios or independent accuracy observations. Console/XML timing difference undiagnosed, no clock-accuracy/engine-performance claim. Ruff lint/format (102 files) and pip check pass.

[Fresh synthetic replay](../output/engine2-status-clarification-replay-20261006.json) passed all four checks: expected states, no actions, no sensor claim, declared synthetic. Compared every result field against the [historical baseline](../output/engine2-replay-smoke.json), excluding only new scope metadata/clarified limitation text: all other calculated fields/provenance identical. Original artifacts untouched, no real collector/clock/service/model action. Recorded executed_at2026-10-06T11:05:16.527834+00:00 is reported walltime, not clock-accuracy evidence. Commands/checks/staged review/publication in WL-057.

### Executed checks and reproduction

At the configured repository root, using the existing environments:

```powershell
.venv/Scripts/python.exe -m ruff format cloudguard/runtime.py tests/test_runtime.py
.venv/Scripts/python.exe -m pytest -q tests/test_runtime.py --basetemp=tmp/engine-status-target-win-20261006-01 -o cache_dir=tmp/pytest-cache-20261006
.venv/Scripts/python.exe scripts/runtime_check.py --output output/engine2-status-clarification-replay-20261006.json
.venv/Scripts/python.exe -m pytest -q --basetemp=tmp/engine-status-full-win-20261006-01 -o cache_dir=tmp/pytest-cache-20261006 --junitxml=output/engine2-status-windows-tests-20261006.xml
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python -m pytest -q --basetemp=tmp/engine-status-full-linux-20261006-01 -o cache_dir=/home/acgresearch/.cache/acg-pytest --junitxml=output/engine2-status-linux-tests-20261006.xml
.venv/Scripts/python.exe -m ruff check cloudguard scripts tests
.venv/Scripts/python.exe -m ruff format --check cloudguard scripts tests
.venv/Scripts/python.exe -m pip check
```

Use fresh temporary/report filenames when reproducing; do not replace these saved artifacts or old fixed-output evidence. Whole-suite host execution was approved for existing inert process tests and ordinary-user WSL; no native service intervention. The existing synthetic runner refuses an existing output file. Scope metadata is an implementation declaration supported by tests/source review, not runtime attestation or independent evaluation.

## Work direction and acceptance gates

Current priority remains **E2-035: grouped runtime dataset and independent-label intake**, mapped to E2-004/RQ3. [Typed receipts](RUNTIME_RECEIPTS.md) implement selected consistency, not complete protocol/coverage/alignment/eligibility. The [draft labeling pack](RUNTIME_LABELING_PROTOCOL.md) and [capture checklist](RUNTIME_CAPTURE_ELIGIBILITY.md) are prepared, not approved; next obtain actual supervisor decisions. Genuine blinded human labels and comparable captures remain prerequisites, not generated evidence. Existing failures and no-action/fitting boundaries preserved. [Evaluation plan](RUNTIME_EVALUATION_PLAN.md) retains wider gates; no new collection/intervention implied by proceeding.

1. Audit existing captures/receipts, retain development and timing-rejected data as such; do not promote them into untouched/independently labeled test data.
2. Prepare a bounded offline run/window manifest and separate blinded reviewer submissions; guard template/deployment/run grouping, duplicate captures and event leakage before assigning splits. No prediction-visible/generated “independent” labels.
3. Establish eligible comparable captures, timing/coverage/identity evidence and actual human adjudication before fitting a research model or claiming a benchmark. Existing clock failures remain open; do not relax/retrofit their gates.
4. Implement/test planned model comparisons under that frozen protocol; software tests with synthetic data may validate code but cannot establish effectiveness.
5. Evaluate misses/false alarms/abstentions, grouped uncertainty, delay/overhead and carefully scoped Engine1/runtime integration. Publication readiness requires actual research evidence, not a test count.

Existing E2-034/native restoration work stays partial. Expand/resume it only for a defined dependency of a reviewed diagnostic/intervention; do not mistake such progress for detection progress. Generic proceed never authorizes time-service stops, clock changes, production scanning or response. Any real service intervention still needs the safe native job-owner/recovery protocol, old unfenced-path elimination, current preflight, explicit fresh human consent and restoration validation. This page schedules no unattended work.

## Maintenance rule

Every substantive change must update this current summary when capabilities/priority/evidence change, plus MEMORY/TASKS/WORK_LOG/CHANGELOG and relevant contracts. Record separately: implemented baseline, completed refinements, missing planned capabilities and scientific gates. Say “complete” only for named acceptance criteria. Keep dated snapshots visibly historical; never rewrite negative experiment bytes or infer execution from documentation. [Maintenance contract](DOCUMENTATION_WORKFLOW.md).
