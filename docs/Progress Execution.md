# Progress Execution

## New step — compare two invented results fairly

Activate the existing Python environment, open repository root and run `python scripts/runtime_paired_accounting_check.py --output output/my-fresh-paired-accounting.json` with a new filename. Open JSON and check six true checks. Both sides contain the same four invented units; one benign flag becomes an abstention. Precision looks better, but coverage falls and the variant's conditional false-positive rate becomes null because it decided no benign unit. The report retains all of this rather than calling it an improvement. No engine/model predictions or real research labels are produced. [Detailed schema/example/limits](SYNTHETIC_PAIRED_ACCOUNTING.md).

## New refinement — avoid repeatedly searching the same windows

The combined workflow now groups each comparator's window positions once, then looks up each asset. Previously it searched the entire list for every asset—even assets without data. Outputs/scores/abstentions stay the same; this is fewer processing steps, not a new engine or proven energy saving. Run the existing fresh-file example `python scripts/integration_check.py --engine1-pipeline --runtime-ml both --measure-stages --output output/my-fresh-index-check.json`, open JSON and check ten true checks. For simple proof of fewer list passes and unchanged reports, run `python -m pytest -q tests/test_integration_window_index.py`. [Explanation/evidence/limits](INTEGRATION_WINDOW_INDEX.md).

## New step — see how much local execution time each part uses

Activate the existing Python environment, open repository root, and run `python scripts/integration_check.py --engine1-pipeline --runtime-ml both --measure-stages --output output/my-fresh-cost.json`. Use a new filename. Open JSON, check ten true checks, then read result.execution_cost: divide wall_ns/process_cpu_ns by1,000,000 for milliseconds. Each selected component and total are measured separately; CPU can exceed wall time when threads work concurrently, and zero short CPU intervals do not mean free work. These are invented-data development observations, not attack accuracy/sensor overhead/energy savings. [Full step-by-step scope/results](INTEGRATION_EXECUTION_COST.md).

## New step — compare the two existing synthetic models together

The workflow now connects Engine1 and saved Engine2 windows with optional existing Isolation Forest/autoencoder reports. It is not a third engine or proof of real attack detection. Follow [simple reproduction](SYNTHETIC_ML_INTEGRATION.md): activate the existing Python environment, open repository root, run `python scripts/integration_check.py --engine1-pipeline --runtime-ml both --output output/my-fresh-ml-integration.json`, then open the file. Use a new filename. Nine true checks confirm this software example; compare each model's separate numeric/null values and scored/abstained counts. Null means it abstained, not safe. Actual local retrieval/synthetic fits were demonstrated on both systems, no inference/network probes. Supervisor/real data/independent evaluation remain pending.

## Latest development — existing Engine1 pipeline connected to runtime context

The combined command can now use the existing Engine1 pipeline, so its retrieved sources, model output, probe observations, policy review and existing priority stay alongside Engine2's saved runtime windows. This is new Python/CLI integration; the default rule-only command still works.

[Baby steps and commands](PIPELINE_RUNTIME_INTEGRATION.md) provide a fixed example that actually performs local retrieval/scoring without a model or network call. It passes8checks on Windows/Linux; fullsuiteLinux1306pass/Windows1268pass38skip. Model/probe/review paths are tested with synthetic mocks. Runtime does not change priority or establish an attack; real qualified data/timing/coverage/independent labels/calibration remain research work.

## Latest development — see both engines in one offline report

The new integrated-replay command scans a configuration and reads separate baseline/observation captures, then presents their findings and runtime windows by asset. You can now see a configuration issue beside runtime context in one report. Missing windows stay unknown; findings are preserved even when a runtime score is low. [Baby steps, example and exact commands](INTEGRATED_REPLAY.md).

The fixed synthetic example passes on Windows/Linux: Redis has one configuration finding and two runtime windows; the other three inventory assets show no observed windows. Whole-suiteLinux1278pass/Windows1240pass38skip. The report has no combined threat score or action; actual deployment/timing/coverage and research evaluation still need evidence. The earlier pending scanner change is now committed/pushed asa555b32. This milestone includes new Python implementation/CLI/tests, alongside the documentation you requested.

## Latest maintenance — clearer rejection of ambiguous configuration

Engine1 now rejects an environment list that declares the same variable twice, instead of silently keeping its last value. It also rejects malformed entries. Valid configurations keep their existing findings and locations. The new tests caught a mistake in the first fix; its failed evidence is saved and the correction is verified before commit. [Explanation, commands and checking steps](COMPOSE_ENVIRONMENT_VALIDATION.md). Engine2's research status is unchanged; supervisor/data/evaluation work remains open.

## Latest maintenance — cache safety and full regression checks

We found and reproduced three problems in Engine 1's optional saved-response cache: rejected writes or replacement could delete good saved entries. These are now fixed and tested; they are not newly discovered cloud vulnerabilities. Windows: 1,191 tests passed/38 skipped; Linux: 1,229 passed. Style/dependency checks passed. The restricted Windows run failed because host-dependent assumptions were not available; its evidence is preserved rather than deleted. [Readable report, exact commands and beginner check steps](REFINEMENT_AUDIT_20261007.md).

Both engines keep the existing Python architecture. The old Engine1 baseline remains preserved; current code has this maintenance refinement. Engine2's statistical and synthetic ML comparators are implemented, not independently proven detectors. Supervisor approval and qualified data/independent labels/timing/coverage/calibration are still needed. No live service, sensor, cloud or clock action was taken.

## Current maintenance step — clearer status and bounded import check

Four fresh Windows Python processes imported both optional model backends successfully, in both orders twice. No model was fitted and no package/service/clock/sensor setting changed. This did **not** reproduce or explain the earlier intermittent failure. [Observed facts and exact command](BACKEND_IMPORT_OBSERVATION_20261007.md).

For an accurate quick handoff, open [MEMORY.md](MEMORY.md) first: it now contains one current summary. The earlier long document is preserved unchanged in [MEMORY_HISTORY_20261007.md](MEMORY_HISTORY_20261007.md); old “Current” headings there are historical. Nothing was deleted or rewritten into success, and the latest full test totals are unchanged—not a newly executed suite.

The next real research action remains sharing [ENGINE2_SUPERVISOR_REVIEW_PROPOSAL.md](ENGINE2_SUPERVISOR_REVIEW_PROPOSAL.md) for actual target/context/sample/qualification/human/analysis decisions. It stays DRAFT NOT APPROVED. A working prototype and healthy imports cannot replace qualified data or independent labels; do not start a production deployment or infer permission to change services.

## Current refinement — better optional-model failure reports, 7 October

The previous Windows import failure's cause is still unknown. Imports work now, so we did not reinstall packages or blame another process. We fixed a different, demonstrated problem: every import error used to say “install the dependency,” which could be misleading.

Future model-backend failures now retain safe categories in the error/JSON: module lookup, other import, missing version metadata or wrong pinned version. Unknown/private names and raw paths/messages stay hidden. Both model runners still stop with exit1 and no fabricated score/action—no automatic retry. Details: [diagnostic guide](RUNTIME_ML_BACKEND_DIAGNOSTICS.md).

To check the software without a sensor or service change, run from project root:

```powershell
.venv/Scripts/python.exe -m pytest -q tests/test_runtime_backend_diagnostics.py tests/test_runtime_ml.py tests/test_runtime_autoencoder.py
```

Existing environment verified129cases;32new diagnostic cases deliberately inject faults, not real Windows instability. Initial8failure report stays preserved; fullLinux1226pass/Windows1188pass38skips, nofailures/errors in current runs. This fixes future reporting, not a proven historical fault cause or security benchmark. Supervisor-ready proposal remains unapproved and real data/labels/calibration/evaluation gates pending. WL-066 records exactly what happened.

## New software step — honest decision accounting, 7 October

There is now an optional arithmetic example that keeps missed, unknown, missing/unusable and abstained cases visible. It does not run a detector or create human labels. In the invented example, one positive is flagged, one is not flagged and one has no decision: recall among decided positives is1/2, but only1/3of all known positives is flagged. Neither is actual Engine2 accuracy; hiding the abstention would hide a limitation.

From project root, choose a new output filename:

```powershell
.venv/Scripts/python.exe scripts/runtime_accounting_check.py --output output/my-first-accounting-check.json
.venv/Scripts/python.exe -m pytest -q tests/test_runtime_accounting.py
```

Linux uses its environment's Python. Open the JSON: declared11/observed9/missing1/unusable1, positive/negative abstention counts, unknown cells and separate conditional/inclusive ratios. Null means the denominator is undefined, not perfect performance. Empty or missing evidence never becomes a safe/benign conclusion. Existing filenames cannot be overwritten. [Contract](SYNTHETIC_RUNTIME_ACCOUNTING.md) explains every input/output field.

46newtarget cases passed; both fixed examples agree. An initial fullWindowscheck had one existing optional-model import failure; preserved in INC-056/WL-065, subsequent direct/isolated checks passed without a known cause/fix. Final complete verification in EVIDENCE, not inferred from older test totals. Default two-engine architecture and the unapproved supervisor proposal remain unchanged; this is an offline arithmetic aid, not an accepted benchmark or real-data calibration.

## Current next step — data audit and a file for your supervisor

The models' software is built, but the research needs defensible data and real human decisions. We inspected seven saved normalized files: five invented practice files and two earlier sensor-development files. Their380stored events/45per-fileone-minute windows are not380independent observations or45independent experiments. Two practice files reuse two events; both sensor files come from the same development family. The existing leakage guard rejects the reused pair. Earlier failed collector alignment remains failed; files/times were not edited into success. [Full audit](RUNTIME_DATA_READINESS_AUDIT.md).

You said supervisor approval has not yet been obtained. The requested file is **docs/ENGINE2_SUPERVISOR_REVIEW_PROPOSAL.md**: [open proposal](ENGINE2_SUPERVISOR_REVIEW_PROPOSAL.md). It is DRAFT — NOT APPROVED, not a signed permission or results report.

1. Open the proposal and read sections2/3/9: what the positive label means, allowed lab scope and pending decisions.
2. Share the file yourself with your supervisor. No message was sent automatically. Ask them to approve/revise the target, required independent context, units/families/sample design, collection-quality gates, reviewers and analysis/privacy/safety conditions.
3. Record their actual response privately using the [review sheet](templates/runtime-supervisor-review.md). Do not invent a signature or commit personal names/consent records. Keep revisions and why decisions changed.
4. Only after genuine decisions, revise/freeze the qualification/collection plan and obtain any separate operational permission. The draft does not permit stopping time services or collecting production data.
5. Then establish comparable data, obtain two real independent reviews, freeze grouped training/calibration/test data and run a reviewed evaluation. Synthetic votes or repeatedly viewed practice observations cannot be independent test evidence.

Fresh existing offline checks: Windows208passed/1skip and Linux209passed, zero failures/errors. No new model code, collection or real-data training in this step. The latest full suite remains1148collected from the earlier model milestone; it was not rerun for this documentation-only audit. Commands/outcomes: WL-064 [WORK_LOG](WORK_LOG.md). Earlier entries below are historical progress.

## Current addition — Engine 2 reconstruction model, 6 October 2026

Engine 2 now has three **comparison methods**, not three engines: the original statistical baseline, an optional Isolation Forest, and an optional reconstruction autoencoder. Engine 1 still checks configurations; Engine 2 studies runtime evidence. Both optional models are implemented software using invented examples. They are not independently proven attack detectors, and no real-study approval or labels have been invented. The existing architecture remains unchanged.

The autoencoder learns to rebuild four baseline activity counts through a smaller hidden layer. A separate observation is scaled using **only the baseline's** learned scale, then rebuilt. We record how different that reconstruction is. A small difference does not prove safety; a large difference does not prove an attack. Its numbers are on a different scale from Isolation Forest, so comparing their raw magnitudes cannot tell which is better. [Technical contract](SYNTHETIC_RUNTIME_AUTOENCODER.md).

### Baby steps: run the safe example

1. Open a terminal in your project folder (`D:\research f1` on this machine). Use the existing virtual environment; do not change Docker, services, system time or cloud settings.
2. If setting up a new machine, follow the environment setup sections below first, then the optional package steps in [synthetic ML setup](SYNTHETIC_RUNTIME_ML.md). This milestone installed no new package here. Use your Linux environment's `python` instead of the Windows interpreter path below.
3. Pick a filename that does not exist and run:

   ```powershell
   .venv/Scripts/python.exe scripts/runtime_autoencoder_check.py --output output/my-autoencoder-first-check.json
   ```

4. Open that JSON file in a text editor. Expected normal example: status synthetic_check_passed; all six checks true; result.scored_window_count=3 and abstained_window_count=0. Each binary_prediction is null, actions_executed is empty and real_data_fitting_authorized is false. Training attempts show baseline window count, actual iterations, loss and warnings. These are software checks, not accuracy percentages.
5. Very small positive errors are written in scientific notation, for example `4.34e-10` means roughly 0.000000000434, **not zero**. We fixed earlier rounding that hid these values and kept the original failing test report. Do not manually round/edit the saved evidence into a different result.
6. Check implementation regressions:

   ```powershell
   .venv/Scripts/python.exe -m pytest -q tests/test_runtime_autoencoder.py tests/test_runtime_ml.py
   ```

   In these configured environments the final combined run passed97tests. Without optional packages, dependent tests skip; skips are not verified model execution.
7. To see explicit failure handling, choose another new filename:

   ```powershell
   .venv/Scripts/python.exe scripts/runtime_autoencoder_check.py --max-iter 1 --output output/my-autoencoder-expected-negative.json
   ```

   Our actual diagnostic stopped after one iteration with a convergence warning: exit1/synthetic_check_failed,0scored/3abstained, training attempted but reconstruction not attempted. This is the expected negative example, not “three safe observations.” Preserve it; never overwrite or force it into a pass.

### What is finished, and what comes next?

Fifty new autoencoder test cases; final full Linux1,148passed, Windows1,110passed/38platform-related skips, zero failures/errors. Lint,115-file formatting and dependency checks passed. Both final synthetic demonstrations passed; failed lint/precision/nonconvergence evidence is retained in [EVIDENCE](EVIDENCE.md), with problems/fixes in [INCIDENTS](INCIDENTS.md) and commands in WL-063 [WORK_LOG](WORK_LOG.md). These counts are software tests, not tested attacks or publication-ready accuracy.

Next real-research prerequisites: actual supervisor-approved scope/guidelines, comparable captures with known timing/coverage/identity/context, independent human labels, grouped held-out evaluation, calibration, false alarms/misses/delay, measured overhead/energy and integration with Engine1 evidence. Software prototypes reduce implementation work but do not close those scientific gates. Earlier additions below are historical progress checkpoints, not a claim that today's autoencoder is missing.

## Current addition — synthetic-only machine-learning prototype, 6 October

Engine2 now has an optional Isolation Forest software prototype alongside its unchanged default statistical baseline. We **did fit temporary models**, but only on invented development counts. No real telemetry, attacks, independent reviewers or approved study results were used. This is not Engine3, a production detector or confirmed threat detection.

The prototype learns from synthetic baseline windows, then scores separate synthetic observation windows. It does not feed those observations back into fitting or choose a threat threshold from them. High score is not an attack probability; no binary ML “safe/attack” verdict is produced. Too little/constant baseline data produces an abstention, not a clean verdict.

### Baby steps — reproduce the software demonstration

1. Read [the ML prototype guide](SYNTHETIC_RUNTIME_ML.md). It requires an optional Python library; Docker/Ollama/Linux sensors are not needed for this example.
2. In your existing Python environment, install the optional pinned packages if absent: Windows `.venv/Scripts/python.exe -m pip install --only-binary=:all: --index-url https://pypi.org/simple -r requirements-runtime-ml-20261006.txt`; Linux uses its environment's `python`. This is package setup, not research-data collection. Core/vector lockfiles are not replaced.
3. Find data/runtime/ml-baseline-synthetic.json (32invented one-minute windows) and ml-observation-synthetic.json (3invented windows). January timestamps and placeholder container IDs are test coordinates, not old measured captures or labels.
4. Run `.venv/Scripts/python.exe scripts/runtime_ml_check.py --output output/my-fresh-synthetic-ml.json` (Linux: environment's `python`). Choose a new filename; existing output is refused. No model file is saved.
5. Open the report: all6checks should be true. result shows synthetic_fitting_performed=true,3scored/0abstained windows, null binary_prediction. Real-data fitting, supervisor approval, independent evaluation and threat confirmation remain false; actions empty. The nested statistical_comparator is the unchanged older baseline, not a second new model.
6. Run `.venv/Scripts/python.exe -m pytest -q tests/test_runtime_ml.py`. Current47cases pass in both installed environments; without optional libraries the relevant tests explicitly skip. Software checks are not47attack scenarios.
7. Testing found two test-only mistakes, then review found a real reporting mistake: all abstentions still said scores computed. We reproduced it, fixed summary/status/counts, and preserved every negative/preliminary report. Final whole-project Linux1,098pass/Windows1,060pass38skips; no independent accuracy claim.
8. Next still requires actual supervisor protocol decisions, eligible comparable real data/timing/coverage/identity, approved independent context and real blinded labels. Autoencoder, calibration, real evaluation and measured overhead remain unfinished. Do not rename the invented fixtures into an independent benchmark.

Work and failure history: WL-062, INC-051/052; [current status](CURRENT_STATUS.md). Earlier additions below are historical.

## Current addition — list the windows without inventing labels, 6 October

Engine2's baseline remains built. We added an optional list of the exact observed time windows a coordinator would later allocate to reviewers. It creates **no labels**, chooses no “good/bad” answer and trains nothing. Empty or missing data does not become a fake benign window. Review approval and genuinely independent people are still required.

This is **not a blinded handout**: run names and times may reveal scenarios. Keep actual private indices with the coordinator, audit neutral names/context separately, and do not distribute model answers or other reviewers' votes.

### Baby steps — harmless synthetic example

1. Open [the index guide](RUNTIME_ANNOTATION_INDEX.md). This is an optional output of existing intake, not another engine or Engine2 model version.
2. At your configured repository root, Windows: `.venv/Scripts/python.exe scripts/runtime_intake.py --manifest data/runtime/intake-example/manifest-typed-counted.json --annotation-index --output output/my-fresh-annotation-index.json`. Linux: use `python` in the existing environment. No Docker, Ollama or services needed. Choose a new filename outside the example folder; its parent must exist.
3. Open your report. Expect status observed_units_indexed and three units with run_id, asset_id and start_epoch. Labels, approval, blinding, independent evaluation, fitting and predictions stay false; actions empty. These are existing invented demonstration windows, not new data.
4. Without --annotation-index, the old intake report is unchanged. Do not hand its agreement/reviewer metadata to blinded reviewers. Real indices should be private/runtime-labeling/ or approved secure storage; Git protection is not encryption.
5. Run `.venv/Scripts/python.exe -m pytest -q tests/test_runtime_annotation_index.py tests/test_runtime_intake.py tests/test_runtime_receipts.py` (Linux: existing environment's `python`). Current182cases; here Windows181pass1symlink-privilege skip. Practice files/software contracts, not research subjects or cloud scans.
6. Initial testing revealed a helper editing the wrong capture reference after changing run order. The hash checker correctly rejected it. We fixed only test setup and kept the failed XML. Final whole-project Linux1,051passed/Windows1,013passed38skips; software checks, not security accuracy.
7. Next obtain actual supervisor decisions using the [draft sheet](templates/runtime-supervisor-review.md), then adequate approved context, comparable capture/timing/coverage evidence and real independent reviews. Do not fill approvals or generate votes to move forward.

Detailed commands/results/problem/fix: WL-061 and INC-050. Earlier additions below are historical.

## Current addition — preparing honest human review, 6 October

Engine2's basic engine is built; this step prepares how people could evaluate it responsibly. We wrote a draft reviewer guide, supervisor decision sheet, capture checklist and blank label templates. **Nobody has approved the draft or submitted real independent labels.** Three event counts do not tell us whether activity was authorized or malicious. When context is insufficient, the draft says “unknown,” not “safe.”

Whole-project software checks passed: Linux1,029; Windows991with38platform/privilege skips. Eighteen targeted checks passed, including15new checks. These numbers measure software regression checks, not security accuracy. No collector, cloud scan, model training or time-service operation was started.

### Baby steps — inspect the draft without running an experiment

1. Open [current status](CURRENT_STATUS.md); see the distinction between implemented software and research proof.
2. Read [coordinator pack](RUNTIME_LABELING_PROTOCOL.md), then [reviewer guidelines](RUNTIME_LABELING_GUIDELINES.md). The proposed narrow “needs security review” target requires supervisor decisions; it is not proof of confirmed attacks or a replacement for the original aim.
3. Open [supervisor sheet](templates/runtime-supervisor-review.md). It is intentionally pending. Ask your supervisor: “Can we approve or revise the target, independent evidence/context, windows/groups/sample design, blinding/unknown rules, timing/coverage requirements and permitted claims?” Record actual answers privately; do not fill names/signatures merely to move forward.
4. Read [capture checklist](RUNTIME_CAPTURE_ELIGIBILITY.md). Each of16gates requires evidence or remains unknown/not satisfied. Old development captures and rejected timing trials cannot become new independent evaluation data by renaming them.
5. Inspect [case ledger](templates/runtime-case-ledger.md) and [review](templates/runtime-review.json.example)/[adjudication](templates/runtime-adjudication.json.example) templates. Null/UNFILLED fields deliberately fail validation. Do not submit these as actual votes or generate votes for reviewers.
6. At your configured repository root, Windows: `.venv/Scripts/python.exe -m pytest -q tests/test_runtime_research_pack.py tests/test_repository_check.py`; Linux: use `python` from the existing environment. Expected18checks; these use synthetic/static material and Git-ignore checks, not real reviewers. No Docker/Ollama needed.
7. Run `.venv/Scripts/python.exe scripts/repository_check.py` (Linux: environment's `python`) for documentation/publication checks. Future actual private records belong in private/runtime-labeling/ or approved secure storage. Git ignore/publication refusal is not encryption; do not force-stage/copy those records elsewhere.
8. After actual approval and eligible authorized comparable data, two real people independently review neutral packets without model scores/answer keys/other votes. Preserve originals/unknowns before adjudication. Existing intake checks file consistency only; it does not authorize fitting.
9. Next research milestone is actual protocol approval and evidence-bearing comparable captures, then independent labels/frozen grouped evaluation. Stable timing/coverage, ML comparisons and effectiveness remain open. We cannot honestly mark those complete from templates or test counts.

Earlier additions below are historical steps, not current approval/status.

## Current addition — checking what receipts actually say, 6 October

Engine2's replay baseline is still the same engine. We added an optional second **input format**, not a second detector version. It checks recorded counts against the capture and trial, compares saved before/after identity, and recomputes local clock calculations. This helps catch inconsistent research records. It does not prove that all events were captured, that the collector clock aligns, or that two reviewer names represent independent people. No model was trained and no live collector/service/clock operation was run.

We added 77 checks, including two reads of already saved historical evidence. Final whole-project results: Linux 1,014 passed; Windows 976 passed with 38 skips. These are software checks, not threat accuracy. Review found a missing comparison of trial counts; three tests reproduced it, then we fixed it and kept the failed report. Both the earlier uncounted input and corrected counted input remain available, so the problem is not hidden. [Current status](CURRENT_STATUS.md), [detailed report](RUNTIME_RECEIPTS.md).

### Baby steps — typed receipt example

1. Open a terminal at your configured repository root. No need to start Docker, Ollama or any services.
2. Find data/runtime/intake-example/manifest-typed-counted.json. It connects the existing invented capture to three *wrappers*. Each wrapper names the run, capture hash, inventory hash and source file. receipts/accounting-fixture-counted.json contains invented counts; receipts/trial-fixture-counted.json contains invented identity/clock/count facts. These are not actual human or collector observations.
3. Windows: `.venv/Scripts/python.exe scripts/runtime_intake.py --manifest data/runtime/intake-example/manifest-typed-counted.json --output output/my-fresh-typed-report.json`. Linux: replace the Windows executable with `python` from the existing environment. Pick a new output filename outside the example folder; the output parent must exist.
4. Open the report and expand runs -> selected_receipt_checks. Accounting checks that numbers add up; identity checks saved snapshots; timing checks local endpoints. Each selected_consistency_checked=true is limited to the named scope. **Do not mistake it for full receipt_semantics_verified or evaluation_eligible**, which stay false. Collector alignment, complete coverage, authenticated identity, independent evaluation and model fitting remain unverified; actions_executed empty.
5. The example has three windows and no reviewer submissions. Its invented event times are not matched to the practice measurement interval. That is deliberately not collector-alignment proof. A stable snapshot or acceptable local calculation cannot authorize training.
6. Run `.venv/Scripts/python.exe -m pytest -q tests/test_runtime_receipts.py tests/test_runtime_intake.py` (Linux: existing environment's `python`). Current combined cases total 160; here Windows has one symlink-privilege skip. Tests use practice files, plus two read-only checks of old evidence; no new collection or cloud scanning.
7. Earlier manifest-typed.json is now a **negative example**: it lacks trial counts and is rejected. Its earlier passing report is kept as a pre-fix checkpoint, not current success. Original v1 manifest.json still works unchanged. Never overwrite reports or casually reformat hash-bound files.
8. The current addition above now provides a draft labeling pack/checklist; these are NOT APPROVED. Next obtain actual supervisor decisions, real independently completed blinded reviews and comparable data under reviewed protocols. Software cannot invent these prerequisites. We are preparing evaluation, not claiming a publication-ready security detector.

Sections below describe earlier checkpoints; this section and CURRENT_STATUS take precedence.

## Current addition — checking research data before models, 6 October

Engine2's basic replay engine is already built. We added an offline checker to help prepare its evaluation. It checks file hashes, related declared groups across partitions, and reviewer labels for each observed time window. It keeps disagreements and unknowns. It does not collect data, contact models or train anything. Independence is **not** proven by two names or a file saying “passed.” Receipt meanings and human identities still need verification; all evaluation/training flags remain false. We added 83 practice tests. Full suite: Linux 937 passed; Windows 899 passed with 38 skips. These are software tests, not attack accuracy. [Current summary](CURRENT_STATUS.md), [detailed contract](RUNTIME_INTAKE.md).

### Baby steps — try the harmless example

1. Open a terminal at your configured repository root. No need to start Docker, Ollama or any services for this example.
2. Find data/runtime/intake-example. inventory/assets.json lists the example asset. captures/synthetic.json contains three invented events. guidelines/synthetic.md explains fixture labels. labels/fixture-a.json and fixture-b.json are **invented submissions**, not real people. labels/adjudication.json keeps one agreed vote and two unknowns. manifest.json connects their exact hashes.
3. Windows: `.venv/Scripts/python.exe scripts/runtime_intake.py --manifest data/runtime/intake-example/manifest.json --output output/my-fresh-intake-report.json`. Linux: replace the Windows executable with `python` from the existing environment. Output parent must exist; pick a new filename outside the example directory.
4. Open your report. Expect status artifact_consistency_checked, three observed windows, one known agreement, one disagreement and one unknown pair; known fraction 0.5. This is fixture agreement, **not detection accuracy**. Three missing receipts stay listed. Independence/evaluation/model-fitting/prediction flags remain false; actions_executed empty.
5. Windows: `.venv/Scripts/python.exe -m pytest -q tests/test_runtime_intake.py`. Linux: existing environment's `python -m pytest -q tests/test_runtime_intake.py`. Here Windows 82 passed with one symlink-privilege skip; Linux's 83 cases pass in the whole suite. Temporary practice files, not cloud scans or time-service commands.
6. Existing output is refused, never overwritten. Bad hashes/inconsistent labels give a fresh redacted rejection/exit1, never “clean.” Keep earlier results and create a new corrected input version; never edit a saved report into success. Hashes include exact bytes/line endings; fixture files use repository LF rules, do not casually reformat them.
7. For real research obtain approved guidelines and independent blinded human submissions, without showing predictions. Store real private submissions securely, not automatically in GitHub. Next check what collection/timing/identity receipts actually prove. Stable comparable captures and an untouched grouped test set are prerequisites to model/effectiveness claims. [Full plan](RUNTIME_EVALUATION_PLAN.md).

Two testing problems were recorded: sandbox path permissions and a test changing a constant after its default had been bound. Host execution and an actual oversized-file test resolved test issues; production limits unchanged/failed XML kept. [INC-048](INCIDENTS.md). Paragraphs below are earlier snapshots, not today's task list.

**Read this current-status clarification first,6October:** you were right that Engine2 already has an implemented baseline. We are not rebuilding it. It can read saved event captures, group them into time windows and report statistical deviations for review. Separate Linux/Falco capture and normalization tools also exist. Recent receiver/job/fence tests improve experiment reliability and safety; they are not extra engines or threat-detection proof. Planned ML models, independent labels, reliable timing and measured effectiveness/overhead remain open. [One current summary](CURRENT_STATUS.md) takes precedence over the dated snapshots below.

**What changed now/how to check:** replay output now includes implementation_scope: component runtime_replay_baseline/status implemented, saved sensor exports supported, live input/trained ML/independent evaluation/automatic response false. A misleading old statement that the repository had no eBPF collector was corrected; calculations/guards unchanged. Windows full817pass37Linux-only skips/Linux854pass; these are software checks across the whole repository, not attack accuracy. (1) Run `.venv/Scripts/python.exe -m pytest -q tests/test_runtime.py` in the configured Windows project environment (31passes). (2) Open the fresh [synthetic report](../output/engine2-status-clarification-replay-20261006.json), read evidence_level/scope/false flags before scores. (3) Read [next data/label plan](RUNTIME_EVALUATION_PLAN.md); it is planned, not new independent data or implemented intake software. Do not rerun old fixed-output reports, label development examples as untouched tests, or stop services. For a new replay use the existing script with a fresh output filename; it refuses replacement. Next default is grouped data/label intake, not more safety helpers by default.

**Saving simulated job evidence safely,6October:** the new inert gate writes “about to try” before a practice callback, then keeps the returned job number/path and copied completion messages separately. It can reload these records after a worker exits. A missing reply, interrupted worker or invalid record stays unknown—even if a recovery simulation looks successful. Recovery closes the session before waiting so later cooperating workers cannot dispatch.60new tests were added, including four real Linux dummy-worker checks; Linux851pass/Windows814pass37Linux-only skips. We found/fixed one rule that accepted number1instead of true, and kept the failed test report. Engine1 and real services/clocks were not changed. [Detailed report and file meanings](DURABLE_JOB_GATE.md).

**Baby steps to check it:** (1) use the existing Python environment at the project root. (2) Windows: run `.venv/Scripts/python.exe -m pytest -q tests/test_inert_job_gate.py`; expect56passes/4Linux-only skips. (3) In configured ACG-Research Linux, use `/home/acgresearch/acg-venv/bin/python -m pytest -q tests/test_inert_job_gate.py`; expect60passes. These tests use practice data, temporary files and dummy processes—not service commands. (4) Read the new passing XML reports linked in the detailed report; also read the separately retained failing report as a historical defect reproduction, not the current result. (5) Follow the file-meaning table: intent means an attempt may have happened, reply alone is not completion, and no completed window after worker death means unknown. (6) Confirm native_binding_verified/service_quiesced_verified/may_disarm_recovery are false and operator_recovery_required is true even for successful simulations. Do not delete seals/faults/reports, connect callbacks to systemctl, or repeat the reserved live observation. Next is a concrete native integration/recovery safety protocol tested inertly; real intervention still needs separate explicit approval.

**Harmless native message tests completed,6October:** after the real listener saw0selected events, we tested how it reads messages using the actual Linux library and invented practice data. No practice message went to the real service manager and no service was stopped.28native cases checked correct data, copied-data lifetime, wrong data, repeats, too many events and error handling;3extra checks restrict the fixture. Linux791tests pass; Windows758pass/33Linux-only skips. No receiver defect was found in these cases; this is not proof that Engine2 detects threats or can recover real service jobs. Engine1 remains unchanged. [Detailed report](NATIVE_CALLBACK_VALIDATION.md).

**Baby-step check:** (1) open a terminal in your project clone. (2) On Windows run `.venv/Scripts/python.exe -m pytest -q tests/test_systemd_native_fixture.py`; expect3passes/28Linux-only skips. (3) In the configured ACG-Research Linux environment, activate the existing research Python environment or use `/home/acgresearch/acg-venv/bin/python -m pytest -q tests/test_systemd_native_fixture.py`; expect31passes. Do not run as root or weaken the pinned-library checks if your environment differs. (4) Read the two new XML reports linked in the detailed report: failures/errors should be0, Windows skips are explicit. (5) Read the limitations: practice data is synthetic, so real job completion and recovery remain unproven. Do not delete/repeat the old live observation folder or run a service-stop command. Next we will design/test durable job records and the safe guest gate inertly before any separately approved intervention.

**Real listener check completed,6October:** you approved starting Docker Desktop. The local Windows and Linux command tools now reached the engine, and the required known-sensor check passed. We ran the planned read-only listener once: its connection, notification registration, identity checks and cleanup passed. It saw0selected completion events; that does not mean no jobs exist or that Engine2's protection is finished. The time service remained active/running/enabled, and no time-service/clock setting changed. The earlier blocked check was kept, not replaced. [Real evidence and meaning](SYSTEMD_RECEIVER_CAPTURE.md).

**How to inspect safely, in baby steps:** (1) open `output/engine2-systemd-receiver-observation-20261006/started.json` in a text editor; it records one planned attempt and the limits. (2) Open `result.json`; look for outer/receiver `status: observed`, child `exit_code: 0` and `child_reaped: true`. (3) Look at `events: []` and read this as no selected event delivered—not a clean security result. (4) Confirm `jobs_submitted_or_canceled`, `native_binding_verified`, `service_quiesced_verified` and `may_disarm_recovery` are false. (5) Read the report's remaining gates. Do not delete the directory to repeat the one-attempt command. Earlier755Windows/5skips and760Linux tests verify software; no new full suite was run for this unchanged-source observation. Next: harmless native callback/fault fixtures, then safe durable job/gate integration; Engine1 and research stack are unchanged.

**Why the real listening check has not run:** the launcher and protocol are committed on GitHub, but the required lab check could not reach Docker Desktop. The Windows command tool exists; its local engine pipe and the Linux integration mount are unavailable. We cannot assume the sensors are absent when the check fails, so we stopped before launching the listener. No service, clock, Docker setting or WSL restart was changed. We saved this problem and its read-only diagnosis as INC-045. [Evidence and explanation](SYSTEMD_RECEIVER_CAPTURE.md).

**What is needed next:** restore Docker Desktop/local Linux integration with operator direction, then repeat the readiness check—not a receiver observation. If readiness passes, the one planned read-only listening attempt can begin. Do not delete any evidence folder or stop the time service. Engine1 is unchanged; Engine2 still needs actual notification validation, safe job/fence integration, reliable timing and independent ML evaluation. Latest755Windows/5skips and760Linux tests verify software, not the currently unavailable lab engine.

**Saving a listening attempt, 6 October:** we added a launcher that first saves “started,” then saves the result separately. It refuses to replace an earlier attempt. A stuck listener gets a time limit; if completion/cleanup cannot be checked, the result stays unknown.34new checks were added; Windows755tests pass/5Linux-only skips, Linux760pass. Two real Linux tests ran harmless dummy children, not service commands. We have not yet performed the one declared real notification check at this implementation checkpoint. [How it works and limits](SYSTEMD_RECEIVER_CAPTURE.md).

**Simple check for this addition:** at the configured project root run `.venv/Scripts/python.exe -m pytest -q tests/test_systemd_receiver_capture.py` on Windows, or `python -m pytest -q tests/test_systemd_receiver_capture.py` in the Linux research environment. Windows expects32passes/2Linux-only skips, Linux34passes. These tests cannot start/stop the time service. The real `--observe` command is a one-attempt supervised research check: read the report first and do not delete its result folder to repeat it. It listens only; an empty list does not mean the service is safe or Engine2 is finished.

**Listening safely, 6 October:** we added a separate listener that can stay connected to the Linux service manager briefly and check where notifications came from. It cannot start, stop or cancel service jobs, and an empty event list never means everything is safe.54new simulated tests pass; full Windows723pass/3Linux-only skips, Linux726pass. The real library's identity/functions were checked, but real notification reception has not run yet. One Windows test simulated the wrong native number size; the test was corrected and the safety rule kept. [Detailed report and commands](SYSTEMD_RECEIVER.md).

**How you can check this step:** open a terminal at the cloned project folder and use the existing Python environment. Run `.venv/Scripts/python.exe -m pytest -q tests/test_systemd_receiver.py` on Windows, or `python -m pytest -q tests/test_systemd_receiver.py` inside the configured Linux research environment. Expect54passes; these tests simulate messages and cannot change services. Follow the report for fresh temporary/report names if retaining evidence. There is no finished native receipt launcher yet; do not wire this listener into the service-stop experiment. Next we will preserve a separate real read-only observation before considering service-control integration. Engine1 remains unchanged; Engine2 timing and ML validation are still unfinished.

**Job-completion evidence, 6 October:** we checked the real Linux service manager's interface without changing services. Sending a request is not proof it finished; canceling a job does not necessarily cancel its operation. New test-only logic matches a specific returned job to its completion and treats lost replies/connection changes as unknown. Windows669tests pass/3Linux-only skips; Linux672pass. This logic is not yet connected to real control or recovery. [What this establishes](SYSTEMD_JOB_CONTRACT.md).

**Guest-side safety prototype, 6 October:** we built a separate test-only gate that permanently closes a session before recovery waits for another operation. Real Linux file/process tests show that a queued test worker cannot start afterward. A killed worker is still treated as uncertain; an already-submitted job outside the gate is not magically canceled. Windows640tests pass with3Linux-only skips; Linux643pass. No actual time service changed, and this gate is not yet connected to the real runner. [Explanation and limits](GUEST_FENCE_PROTOTYPE.md).

**Recovery cancellation fix, 6 October:** our simulated tests found that an error while stopping the time service could cancel recovery too early. We fixed this: the system now keeps the helper uncancelled, saves whether the stop command was acknowledged, and says a person must check recovery instead of claiming it is safely restored.610software tests pass on each OS. No real service was changed. A very late guest command could still outlive the helper, so the live experiment remains blocked until that ordering problem is resolved. [Plainly bounded result](CLOCK_STOP_DELIVERY.md).

**Safer source checking, 6 October:** we now check23project files, including the files loaded by the lab readiness check, before starting that check. If those files change, the diagnostic refuses to collect or stop the service. All596 software tests pass on Windows and Linux. No real time service was changed. A delayed stop command could still arrive after recovery, so that safety issue must be resolved before the live experiment; the clock problem and ML evaluation remain open. [Explanation and results](CLOCK_COMPARISON_PREFLIGHT.md).

**Transport/helper progress, 6 October:** we implemented the Windows-to-research-Linux command adapter and a separate recovery helper. All581 software tests pass on both OS. We tested a real helper after killing its parent and tested cancellation, but those helpers were explicitly inert: they wrote temporary markers and could not touch time services. Actual service commands were simulated. The earlier PID mismatch and sandbox access issues are documented with the fixes. [Report](CLOCK_COMPARISON_TRANSPORT.md).

**Still not done:** we have not stopped the real time service or run the proposed comparison. Your explicit approval and a finalized protocol are required; recovery cannot be guaranteed during host/WSL failure. Engine1 is unchanged, and Engine2 still needs timing reliability, independent labels and ML/effectiveness evaluation. Do not run the live launcher yet; a code flag is not approval.

**Safer comparison logic, 5 October:** we built and tested the logic that would stop a comparison after an error, still attempt service restoration, verify the service is running and only then continue. All551 software tests pass on both operating systems. Service and watchdog behavior in the new tests is simulated: no real time service was stopped and no real recovery helper exists yet. We also added an offline reader that checks three saved receipts and refuses copied or incompatible results. [Details](CLOCK_COMPARISON_CONTROLLER.md).

**What still needs doing:** your explicit temporary-stop approval, a tested real service transport/independent recovery helper and a final one-attempt protocol. We are not claiming timing is fixed or Engine2 ML is ready. Existing Engine1 and old research evidence remain unchanged. Do not run a service-changing command from these planning documents yourself.

**Writer review, 5 October:** we checked the running time service, its WSL-specific setup and official source code. The guest service can adjust time, but the reviewed file does not directly request tick changes. Kernel rate settings can remain after a clock reset; stopping one service does not necessarily remove all adjustment effects. No additional named NTP daemon appeared in the inspected process lists, but that does not prove there are no other writers. We changed nothing and preserved the findings. Engine2 timing/ML remain unfinished. [Detailed review](SYNC_WRITER_REVIEW.md).

**Proposed next experiment:** one reading block with the service running, one briefly stopped, then restoration and a final block. It needs your specific approval and tested automatic restoration before execution. No Windows setting, permanent disable, clock reset, WSL restart or sensor workload is proposed. It may narrow the cause; it cannot guarantee a fix or long-term reliability.

**Real result, 5 October:** the planned check completed all16 timer readings and32 read-only kernel-setting readings. Time-adjustment settings changed during the observation. Linux's normal elapsed clock advanced about0.463 seconds less than its unadjusted timer; its wall-time relationship to time since boot changed by about0.867 seconds. We changed no settings/services and saved the result without retrying. This is stronger diagnostic evidence, not a proven cause or fix. Engine1 remains unchanged; Engine2 still needs reliable timing, independent labels and ML evaluation. [Detailed evidence](KERNEL_CLOCK_STATE.md).

**Next safe step:** inspect which synchronization components can write these settings and prepare a supervised comparison with clear restoration steps. Do not stop services yourself or reuse the earlier one-time permission. A changed kernel setting does not identify who changed it; a successful software test does not make the clocks stable.

**Software check:** all504 tests pass on both operating systems. We kept the early Linux test result and saved a separate final one after correcting an unused test import. Tests confirm the tool's rules, not that the machine's clocks are reliable; the one real observation is still pending at this implementation checkpoint.

**Next read-only check, 5 October:** we added a small Linux-only tool that reads the kernel's current time-adjustment settings without changing them. It will pair32 setting readings with16 timer readings, once, after tests and publication. This helps distinguish an observed clock difference from a guess about its cause. Engine1 remains unchanged; Engine2 timing and ML evaluation are not complete. [Protocol and copyable steps](KERNEL_CLOCK_STATE.md). Windows can review its saved result, but live collection requires the research Linux environment. Do not run it again to seek a nicer result.

**Raw-clock result, 5 October:** the one planned check completed sixteen readings. Linux's unadjusted timer was compatible with Windows within command-delay bounds, but its normal elapsed clocks differed in eleven of fifteen comparisons. Inside Linux, unadjusted time advanced about 0.567 seconds more than normal monotonic time; wall-time's relationship to time since boot also changed. This tells us which measurements to investigate next—not who caused the problem. We saved the evidence and changed no settings or services. All 468 software tests pass on each OS; Engine 1 is unchanged, and Engine 2 timing/ML validation is unfinished. Next: read the live kernel adjustment state without modifying it. [Report and reproduction](CLOCK_PROVIDER_REVIEW.md).

**Next read-only step, 5 October:** Windows' time service is now running; Linux uses the tsc timer and has both host synchronization and its own NTP service enabled. These snapshots do not tell us what caused earlier failures. We added an optional check using Linux's unadjusted clock alongside its normal clocks, without changing any settings. It can help separate clock-adjustment effects from a provider/reference difference. One new short observation is planned after tests/publication; Engine 2 is still under validation. [Provider facts and simple commands](CLOCK_PROVIDER_REVIEW.md).

**Clock investigation result, 5 October:** the one planned read-only check completed sixteen readings. Linux's clocks stayed consistent with each other, but advanced less than Windows' timer across the observation, even after allowing for command delays. This was visible in thirteen of fifteen elapsed-time comparisons. It gives us useful sensor-free evidence; we still do not know which clock mechanism caused it or whether it explains the earlier sensor issue. We kept the result, changed no time settings/services and did not retry. Engine 1 unchanged; Engine 2 timing reliability and machine-learning evaluation remain unfinished. Next: inspect clock-provider facts before choosing a separately planned stability test. [Evidence and reproduction](CLOCK_LINEAGE.md).

**Next clock investigation, 5 October:** a new read-only tool will watch Windows time and three Linux clocks together, up to sixteen times. It keeps the uncertainty caused by command delays instead of assuming the computers share one clock. No time settings, services or sensors are changed. All 455 software tests pass on each OS. One short observation is planned after publishing the tool; even a successful result cannot explain a past clock change or prove long-term reliability. This remains Engine 2 groundwork, not Engine 3. [Simple protocol and commands](CLOCK_LINEAGE.md).

## A beginner's guide to Active Cloud Guard

**Collector follow-up result, 5 October:** the one new sensor-on check completed, matched all four measured test connections and passed the recorded timing checks. We checked 27 boot/wall-time samples and the saved event summaries; sensor removed, no clock changes. However, comparing the earlier and current startup readings shows the boot/wall relationship differs by about 123 seconds between runs. We do not know when or why it changed, and missing service/power logs do not prove nothing happened. This is an exploratory finding, not proof of a cause. Engine 2 still needs trustworthy long-term timing and independent evaluation; the latest software suite passes 428 tests per OS. [Evidence and limits](RECORDED_BOOT_CLOCK_FOLLOWUP.md).

**Collector-specific follow-up preparation, 5 October:** we are adding time-since-boot/wall-time readings around each server-time check, saving them before a check can reject the result. This will provide more information if a future sensor-on run fails. It does not change clocks, loosen safety limits or recover earlier lost data. One new bounded follow-up is planned after tests and commit. [Protocol](RECORDED_BOOT_CLOCK_FOLLOWUP.md).

**Sensor-free result, 5 October:** all six time reads passed in the one planned run. Commands took about 54–86 milliseconds; clock readings agreed within the tested bounds, and the service stayed unchanged. We checked the saved numbers and hashes independently of the live command (offline consistency, not independent scientific evaluation). No sensor, retry or clock adjustment. This is useful evidence that the later sensor-free check worked, not proof the earlier problem is fixed. Next is a carefully planned collector-specific check using the improved failure recording. Engine 1 unchanged; Engine 2 timing/ML evaluation still unfinished. [Results](SENSOR_FREE_TIME_ATTEMPTS.md).

**Next diagnostic, 5 October:** we are preparing a check that asks the existing Redis service for time up to six times, with a one-second pause between successful reads. It runs without a sensor and stops at the first failed check, saving the available timing details. This can tell us whether a new failure is due to a slow command or incompatible clock readings; it cannot recover the earlier lost details or prove Engine 2 is finished. One new attempt is planned after testing/commit. [Method](SENSOR_FREE_TIME_ATTEMPTS.md).

**Failure-recording improvement, 5 October:** future failed time reads now save the available timing details and failure stage without exposing raw error messages. Tests cover seven different failure paths; 414 pass on both operating systems. This improves our ability to diagnose a future failure, but cannot recover details lost in the earlier attempt. We did not run another sensor trial or change clocks. The research timing problem is still open; next is a separately planned check without a sensor. [Recording details](CLOCK_DOMAINS.md).

**Single live attempt, 5 October:** the new tool verified initial clock comparability and recorded the first test connection correctly. It stopped during the second time read because a safety check failed; we did not repeat it to get a better result. Unfortunately the failed read's timing details were not saved, so we cannot yet say why it failed. The sensor was removed and clock settings stayed unchanged. Next we will improve failure recording, with tests, before another separately planned experiment. Engine 2 is not complete; Engine 1 stays unchanged. [Partial result](BOOT_CLOCK_DIAGNOSTIC.md).

**Boot-clock tool, 5 October:** we added a read-only tool to compare wall time with time since boot around sensor startup and each test command. It checks whether the measuring program and containers have comparable clocks before interpreting numbers. 407 tests pass on each OS. This is implementation progress, not proof the timing problem is fixed; the one planned live diagnostic has not run at this checkpoint. No clock settings or Engine 1 changes. [Protocol and limits](BOOT_CLOCK_DIAGNOSTIC.md).

**Collector review, 5 October:** we inspected the exact installed collector version and its corresponding release code. It builds event time using a boot-time offset set during initialization. If the relationship between wall time and boot time changes later, this could explain early event timestamps—but we have not directly proven that happened. We added a small reproducible version/source checker and preserved source hashes; 378 tests pass on each OS. No new sensor trial or clock changes. Next is careful read-only clock-relationship measurement, not declaring the engine fixed. [Review and limits](COLLECTOR_TIMESTAMP_REVIEW.md).

**Next 5 October step:** a new diagnostic now asks the Redis server for its time immediately before and after each measured PING. In one trial, all eight server readings were compatible with the measuring program, but the four matching sensor event times were about a second earlier than both. This narrows where to investigate; it does not prove the cause or fix the problem. We preserved the finding, removed the sensor and adjusted no clocks. 368 software tests pass on each OS. These extra time reads change the workload, so we do not call this an overhead benchmark or a successful repeatability study. [Clock-domain report](CLOCK_DOMAINS.md).

**5 October update:** we ran a separately declared three-trial check using the improved runner. All three started; the first two passed, but the third failed because its recorded event times were about 0.8 seconds earlier than the measuring program's command times. The commands themselves succeeded and their connections were recorded. This shows why collecting events is not the same as measuring them reliably. We preserved the failure, removed every trial sensor and changed no clocks; we did not repeat runs to obtain a favorable result. Fresh software suites still pass 351 tests on each OS. Next is careful clock-domain diagnosis, not a claim that Engine 2 is finished. [Detailed study](READINESS_REPEATS.md). Older updates below are historical snapshots.

Latest repeatability check: **351 software tests pass on each OS**. We planned three identical trials, but a path-handling error stopped the batch after the first passed. The other two never started. We preserved the incomplete study and improved the runner; we did not rerun until obtaining a favorable result. One successful run is not proof of repeatability. See [study record](READINESS_REPEATS.md).

Latest readiness improvement: **343 tests pass on both operating systems**. Measurement now waits for evidence belonging specifically to the second preparation PING, rather than accepting any earlier activity. One new trial observed both preparation PINGs and all four measured PINGs. This is a successful six-command check, not proof of complete monitoring. Earlier misses remain documented; next is a fixed repeated evaluation rather than declaring the problem permanently solved.

Latest progress: **338 tests pass on both operating systems**. We now track the two preparation PINGs separately. The new trial found no connection record for the first preparation command, but found the second and all four measured commands. This identifies where the gap occurred in this trial, not its cause; overall completeness is still unproven. Docker/Redis needed restarting before the test; nothing was recreated or deleted. Next is stricter sensor-readiness checking. See [detailed diagnostic](PID_CORRELATION.md).

Latest sensor step: **332 tests pass on each OS**. In one new supervised trial we identified each of four measured PING processes and found exactly one matching sensor connection for each. Their timestamps were compatible with the command timings. This is useful progress, but the earlier clock issue is not proven fixed and total warmup coverage is still uncertain. The sensor was removed and no time settings changed. See [PID correlation](PID_CORRELATION.md). Older totals below are historical snapshots.

Latest clock investigation: **318 tests now pass on each OS**. We asked the existing Redis lab for its time six times and compared it with the measuring program, allowing for command delay. None of these samples demonstrated a clock difference. This was a later check with no sensor running, so the earlier sensor-timing problem remains open. No clocks or database data were changed. See [clock diagnostic and limits](CLOCK_BRIDGE.md). Older test totals below describe earlier snapshots.

Latest follow-up: **308 software tests pass on each OS**. Comparison reports now double-check the saved clock readings and refuse to compare different timing methods. The old pilot was rechecked without changing its results. This protects reporting; it does not fix the sensor-clock discrepancy. The 301-test counts later in this guide identify the earlier timing-guard snapshot; a current checkout should report 308. Latest test records: [Windows](../output/engine2-report-guards-windows-tests-20260930.xml), [Linux](../output/engine2-report-guards-linux-tests-20260930.xml).

Researcher: **Manish Patil**. Updated **30 September 2026**. This document explains the research, its actual progress, and how to try the implemented parts. It is written for students, supervisors and reviewers who do not work with software every day.

Read sections 1–5 first. Sections 6–10 are practical steps. The safe demonstrations need no cloud account, paid API, AI model or running server. Advanced experiments are separate because they require additional permissions and careful measurement.

## 1. What problem are we studying?

Software can be installed with unsafe settings: for example, a database may be configured to trust a connection without checking a password. Finding such a setting is useful, but it does not automatically prove that an attacker can reach or exploit the system.

Active Cloud Guard investigates whether three kinds of evidence can support a better security review:

1. Read the settings and check clearly defined rules.
2. Retrieve relevant security guidance and ask a local AI model to suggest concerns.
3. Make limited, authorized observations to check what is actually reachable or happening.

The aim is evidence-supported review, not automatic declarations that a system is safe or compromised. The research hypothesis still needs independent evaluation.

## 2. The two engines, without jargon

**Engine 1 is the configuration reviewer.** Think of it as inspecting a building's plan. It reads supported configuration files, applies nine defined checks, can retrieve supporting guidance, and can ask a locally running AI model for suggestions. Some verification checks can contact explicitly listed services on this computer. AI suggestions require human review.

**Engine 2 is the activity observer.** Think of it as examining a building's activity log. It can read saved events, count activity in time intervals and flag a difference from a supplied baseline for review. A limited Linux sensor has also recorded real activity from the local Redis lab. The live sensor is a separate bounded research tool, not a continuously deployed protection system.

The engines do not automatically block users, shut down services or repair a deployment. An activity difference is not automatically an attack. A reachable port is not automatically a vulnerability.

## 3. Small dictionary

| Term | Plain meaning |
|---|---|
| Repository / GitHub | The versioned project folder / its online copy |
| Commit | A named saved revision; use its identifier when citing results |
| Terminal | A window where you type commands |
| Python | The language used to implement the project |
| Virtual environment | A separate folder holding this project's Python packages |
| Docker / container | A way to run the disposable lab services in separate software environments |
| Compose | The file that describes the lab services |
| Ollama | The local program that runs the AI model |
| Chroma | A local store used to retrieve related guidance by meaning |
| Fixture | A deliberately prepared example used during development |
| JSON | Structured text containing fields and results; open it in a text editor |
| Regression test | An automatic check that a known behavior still works |
| Baseline | Reference behavior used for comparison |
| PING / PONG | A small Redis availability request / its successful reply |
| Hash / SHA256 | A fingerprint used to detect changed file bytes, not proof of trustworthy authorship |
| WSL | A Linux environment hosted on Windows |
| eBPF / Falco | Linux observation technology / the sensor used in the bounded trials |
| Latency | How long an operation takes |
| Abstention | The system does not accept a claim; this is not a clean safety verdict |

## 4. What has actually been completed?

| Area | Implemented and checked | Still limited or unfinished |
|---|---|---|
| Research planning | Original proposal reviewed; architecture, rules, tasks and evidence documented | Literature review and supervisor-approved independent evaluation remain open |
| Configuration checks | Nine rules; 45 prepared development examples | These examples are not an untouched test set; broader security coverage is not claimed |
| Retrieval and AI | Local retrieval, structured model output, source/location checks and narrow rejection guards | AI can still make unsupported claims; general accuracy is unmeasured |
| Engine 1 verification | Restricted local network checks and selected Redis/PostgreSQL identity/protocol observations | No general exploit verification or full deployment attestation |
| Efficiency | Reuse of identical AI requests and unchanged vector indexes | General speed, energy and sustainability improvement is not established |
| Engine 1 preservation | Baseline frozen under tag engine1-v2.2 | Frozen means preserved, not scientifically complete |
| Engine 2 replay | Saved-event validation, interval counts, simple deviation comparison | No independently evaluated runtime ML model |
| Live observation | Bounded Linux sensor trials and offline conversion of saved logs | Coverage and sensor-to-harness timing alignment remain uncertain |
| Comparison pilot | Two sensor-off and two sensor-on runs completed | Results are too limited and inconsistent for a general overhead claim |
| Latest timing safeguards | Clock readings around each measured PING; rejection of large per-call clock disagreement | Software-tested, not yet exercised in a new live sensor experiment |
| Software quality | 301 tests pass on Windows and Linux at this revision | Passing tests do not prove detection accuracy or production safety |

The Python, Docker Compose, Ollama and Chroma architecture has been preserved. The supplied web-app workflow was used as a documentation reference, not as a request to change the technology stack.

## 5. Results, problems and honest interpretation

### Engine 1

The 45 development examples matched their expected rule sets. This demonstrates behavior on the examples used during development, not real-world detection accuracy.

One earlier repeat-work experiment observed approximately 0.084 and 0.072 seconds for cached runs, while still making fresh network observations. This does not mean every new configuration is checked that quickly. Separate uncached AI examples took roughly 12 seconds and missed the 3.5-second target. Earlier malformed AI responses and unsupported suggestions remain saved in the repository.

### Engine 2

A completed four-run experiment measured average Docker-exec round trips:

| Run | Sensor | Mean time |
|---|---|---:|
| OFF-1 | Off | 59.423 ms |
| ON-1 | On | 91.887 ms |
| ON-2 | On | 66.066 ms |
| OFF-2 | Off | 72.592 ms |

The paired changes were +54.63% and -8.99%. They point in opposite directions. These measurements include Docker's command-launch work; they are not pure Redis response times or a reliable estimate of sensor overhead.

The second sensor run returned four measured PONGs, but only three connect events had timestamps inside the selected interval. Offline inspection found six connect events in the entire capture, including warm-up activity. One was timestamped 65.4 ms before the measured start. A clock-alignment problem is plausible, but the events cannot yet be confidently linked to individual commands. We did not move the boundaries to make the counts look better.

Earlier clock checks also failed. Temporarily stopping a guest time-synchronization service for explicitly approved experiments improved those checks; the service was restored afterward. This is not a permanent clock fix. **Do not disable time services by following this beginner guide.**

Latest improvement: every new measured PING now gets its own before/after clock readings. A test confirms that a temporary clock jump can be rejected even when the overall experiment's endpoint clocks agree. This does not align the sensor clock or retrospectively repair old results.

Detailed records: [Engine 1 baseline](ENGINE1_BASELINE.md), [paired results](PAIRED_PILOT_RESULTS.md), [event alignment](EVENT_ALIGNMENT.md), [incidents](INCIDENTS.md).

## 6. Before typing commands

Use a personal or explicitly approved research computer. Do not point the project at your college, employer or anyone else's servers. Do not deploy the deliberately weak example configurations.

Choose one route:

- **Existing research computer:** use the current project folder and environment; do not create another clone or replace the environment.
- **New Windows computer:** follow 6A, then 7.
- **New Linux computer:** follow 6B, then use the same demonstration commands with the Linux Python path.

The repository is private. Ask Manish for access before cloning. Permission to view it is not permission to redistribute it. Have Git and Python 3.11 or newer available before starting; an administrator can help install them. Docker is unnecessary for the first demonstrations. The project does not promise a universal minimum RAM/disk requirement; AI models and lab images can require several GB of downloads and additional memory.

Commands in code boxes should be copied without the surrounding backticks. Run each separately; stop at an error instead of continuing blindly. A command finishing normally usually returns you to the prompt. Never publish credentials or raw telemetry when asking for help.

### 6A. Windows PowerShell

Open PowerShell. Check installed tools:

```powershell
git --version
python --version
```

On a new checkout only, choose your parent folder using File Explorer, open PowerShell there, then:

```powershell
git clone https://github.com/ManishPatil2005/active-cloud-guard-honors.git
cd active-cloud-guard-honors
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
```

If you already use this research computer instead:

```powershell
Set-Location 'D:\research f1'
.\.venv\Scripts\python.exe --version
```

Do not recreate its existing .venv. This guide uses the environment's full Python path, so you do not need to activate it or loosen PowerShell execution policy. Installation requires network access; the offline demos do not download a model.

### 6B. Linux shell

For a new Linux checkout with Git, Python and venv support installed:

```bash
git clone https://github.com/ManishPatil2005/active-cloud-guard-honors.git
cd active-cloud-guard-honors
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
```

In all later Python commands, replace `.\.venv\Scripts\python.exe` with `.venv/bin/python`. Never copy a Windows virtual environment into Linux; create a Linux environment separately. Core/tests are verified on the recorded Ubuntu WSL setup; arbitrary Linux machines and full AI/vector installations are not all validated. For the existing ACG-Research environment, use [the recorded paths and setup](WINDOWS_LINUX_SETUP.md), not a fresh installation over it.

## 7. Safe demonstration: check installation

From the project root on Windows:

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest -q
```

Expected: no broken requirements; at this revision, **301 passed**. Newer revisions may have more tests. A failure means stop and inspect it; do not delete the test or change its expected answer merely to obtain a green result. Tests use controlled examples and mocks where appropriate; they do not prove that Docker or the AI model is currently working.

Record your checkout identity:

```powershell
git rev-parse HEAD
git status --short
```

The first command prints a revision fingerprint. The second prints changed/untracked files; empty output means a clean working tree. A different revision or environment can produce different results.

## 8. Safe demonstration: Engine 1 without AI

### Step 1 — Scan one prepared configuration

```powershell
.\.venv\Scripts\python.exe -m cloudguard.cli scan data/development/postgres-trust.yaml
```

Expected: JSON containing rule_id `AUTH001` and title `PostgreSQL trust authentication enabled`. The location explains where the setting was found. `origin: rule_baseline` means a defined rule, not an AI guess. This command reads the example; it does not deploy PostgreSQL or exploit a database. A score of 0.9 is a provisional score, not a measured 90% attack probability.

### Step 2 — Retrieve supporting guidance

```powershell
.\.venv\Scripts\python.exe -m cloudguard.cli retrieve "PostgreSQL trust authentication"
```

Expected: a list containing the `postgres-trust` source summary, its source URL and provenance fields. It retrieves local summaries; it is not a fresh internet search or proof that a model's conclusion is correct.

### Step 3 — Understand what you have shown

You have demonstrated a known rule and retrieval on a prepared example. You have not measured AI accuracy, independently validated a vulnerability, or proven that a real server is exposed. These two commands were rerun successfully when this guide was written.

## 9. Safe demonstration: Engine 2 without a live sensor

Run this one-line command:

```powershell
.\.venv\Scripts\python.exe -m cloudguard.cli runtime-replay data/runtime/observation-synthetic.json --baseline data/runtime/baseline-synthetic.json --inventory testbed/inventory.json
```

Expected: `status: observations_processed`, one window with `no_threshold_exceedance`, another with `deviation_for_review`, and `actions_executed: []`. At this revision, the constructed changed window has deviation_score 8.0. `source: synthetic` means the event data was deliberately invented for demonstration. `runtime_sensor_connected: false` means this replay command is not collecting live events. It does not mean the separate sensor-trial tools have never existed.

`threat_confirmed: false` is important: a count difference is not an attack diagnosis. `partial_or_unknown` means observation completeness is not established. No network connection, container launch or automatic response is performed by this replay command. It was rerun successfully for this guide.

### Save a separate replay-check report

```powershell
.\.venv\Scripts\python.exe scripts/runtime_check.py --output output/my-first-replay.json
```

Use that name only if it does not exist. On a second run use a new name, such as `my-second-replay.json`. The script refuses to replace an existing report. Open the file in your editor to inspect it. This optional saving command is supported by the repository; this guide did not create a file with that suggested name.

## 10. Read the real research evidence

You do not need Docker to open these existing files:

1. [Paired experiment summary](../output/engine2-paired-audited-20260929/summary.json): inspect `runs`, `pairs`, `independent_evaluation` and `sensor_cpu_memory_overhead`.
2. [Second-run alignment report](../output/engine2-on-2-alignment-20260930.json): inspect `event_regions` and `network_connect_offsets`. Negative offsets mean before the recorded start, not negative processing time.
3. [Windows timing-guard tests](../output/engine2-call-clocks-windows-tests-20260930.xml) and [Linux tests](../output/engine2-call-clocks-linux-tests-20260930.xml): machine-readable software-test records.
4. [Work log](WORK_LOG.md): what was done, why, commands, failures and limitations.
5. [Task ledger](../TASKS.md): what is complete, partial or still open.

The saved results came from the recorded research machine and specific dates. Reading them is evidence review, not rerunning their experiments. Raw sensor logs are intentionally not in GitHub; a fresh clone cannot reconstruct those logs from hashes. The minimized summaries are available for review.

## 11. Optional advanced route: AI and local lab

Do this only after sections 7–9 pass, on a disposable approved lab computer, with Docker Linux-container support available. Have a technical supervisor help if Docker or model setup is unfamiliar. These steps can download large images/models and start local services. They are not required to understand the research.

On a **new lab**, install vector support and create local credentials (values are not printed):

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[vector,test]"
.\.venv\Scripts\python.exe scripts/init_secrets.py
docker version
docker compose -f testbed/compose.yaml --profile ai up -d
docker compose -f testbed/compose.yaml ps
```

If the server section of `docker version` fails, stop: Docker is not ready. On an existing research lab, ask the owner before `up -d` because it can recreate containers if their definitions changed. Do not delete volumes or reset Docker to fix an unexplained error.

Download the local models and build the retrieval index:

```powershell
docker compose -f testbed/compose.yaml exec -T ollama ollama pull qwen2.5:3b
docker compose -f testbed/compose.yaml exec -T ollama ollama pull nomic-embed-text
.\.venv\Scripts\python.exe -m cloudguard.cli index
```

Run the restricted demonstration:

```powershell
.\.venv\Scripts\python.exe -m cloudguard.cli run data/development/redis-all.yaml --inventory testbed/inventory.json --model qwen2.5:3b --cache-dir output/audit-cache --max-tokens 512 --timeout 180
```

Read every warning and distinguish rule findings, AI candidates and network observations. The model may abstain or return rejected candidates. That is not proof that the input is safe. Repeating the exact request may reuse cached model work; network observations are still fresh. The command above uses default lexical retrieval; add `--vector-index output/chroma` to explicitly use the built semantic index. Model tags can change; compare recorded digests before claiming identical reproduction.

Stop this lab when finished, without deleting volumes:

```powershell
docker compose -f testbed/compose.yaml --profile ai stop
```

Only stop it when no other authorized experiment needs it. Keep credentials, .venv, caches, model weights and vector databases out of Git. The lab binds published ports to this computer's loopback interface, but is not fully isolated from outbound networking. Do not use real personal or institutional data.

These AI/lab commands follow the implemented workflow; they were **not rerun for this document**. Earlier live results are historical. See [README](../README.md) and [security boundaries](SECURITY.md) for details.

## 12. Live Engine 2 collection: supervised work only

Windows can be used for development and replay; the tested live sensor route uses Linux through ACG-Research WSL and Docker integration. A Python-only Windows replay is not the same as a Linux kernel sensor. Separate Linux installation details are in [Windows/Linux setup](WINDOWS_LINUX_SETUP.md).

Do not run sensor_trial.py or paired_pilot.py as a beginner shortcut. A supervisor must first verify the approved target, image digest, permissions, time-service policy, bounded duration, output location, resource limits and cleanup. The time-service stop/restore used in earlier tests was explicitly scoped; it is not general permission to disable synchronization. New per-call timing fields still need live validation and collector-clock alignment remains open.

The next supervised sequence is: review measurement design; verify prerequisites; collect a separately named bounded diagnostic if authorized; inspect all failures and cleanup; compare clocks without inventing event associations; only then plan repeated baselines. Do not fit an ML model to uncertain measurements or rename related samples to pretend they are independent.

## 13. If something goes wrong

| Symptom | First safe action |
|---|---|
| GitHub asks for access | Ask the owner to grant access; never share tokens in chat |
| Python or Git not found | Ask the computer administrator to install the missing prerequisite |
| Module not found | Check you are in the repository root and using its environment's Python |
| PowerShell activation blocked | Use the full Python path in this guide; do not weaken system policy |
| Tests fail | Save the command and error; record Git revision; stop before live work |
| Output file already exists | Choose a new filename; preserve the old observation |
| Docker unavailable | Start/check Docker through the approved setup; do not reset data |
| Model missing or slow | Check model/service availability; allow download time; do not call a timeout a clean verdict |
| Counts or clocks disagree | Keep the result, mark it uncertain and investigate; do not shift timestamps to force agreement |
| No findings / rejected candidate | Interpret it as limited coverage or abstention, not proof of security |

When asking for help, give: the step number, exact command, expected result, actual error, operating system and Git revision. Redact secrets and do not upload raw telemetry without review.

## 14. How to maintain a trustworthy research record

For each new change or experiment, write what you intended, what changed, the exact command, what actually happened, failures, limitations and next action. Keep old failed reports. Use a new filename for each run. Update WORK_LOG, MEMORY, TASKS and CHANGELOG together; update test/security/architecture documents when relevant.

Before publishing, run the repository checker, inspect the staged files and exclude secrets/raw telemetry. Commit only the intended work with a descriptive message. After pushing, compare local and remote revision IDs; a local commit alone is not a GitHub backup. This project's checks run locally; do not present them as hosted CI or peer review.

For a presentation, a defensible summary is: **“We have a tested configuration-review prototype and a bounded runtime-observation pipeline. We preserve evidence and failures. Independent detection accuracy, reliable sensor timing, general overhead and production readiness remain under evaluation.”**

## 15. What comes next?

1. Validate the new per-call timing measurements and establish collector-to-harness clock/correlation evidence.
2. Strengthen automated experiment/report validation and predeclare repeat counts and stopping rules.
3. Collect comparable, resource-instrumented samples with honest coverage accounting.
4. Obtain independent labels and a genuinely untouched grouped evaluation set.
5. Evaluate runtime models and compare Engine 1 alternatives fairly; report errors and abstentions.
6. Assess general latency, resource cost and sustainability before claiming improvements.

The project has made measurable engineering progress. It is not appropriate to claim “zero errors,” “all vulnerabilities detected,” or “research completed” from the current evidence.
