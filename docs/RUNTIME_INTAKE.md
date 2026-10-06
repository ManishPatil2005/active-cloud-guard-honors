# Offline runtime research intake formats (E2-035)

6 October 2026: **implemented/software-tested artifact-consistency subset** of E2-035/RQ3/E2-004. Isolated offline tooling, not a new engine, detector, collector, trained model or independent benchmark. Engine2's saved-capture statistical baseline already exists. [Current status](CURRENT_STATUS.md), [evaluation plan](RUNTIME_EVALUATION_PLAN.md).

Latest refinement: opt-in runtime_intake_v2 adds [selected typed-source checks](RUNTIME_RECEIPTS.md); v1 report/API and opaque-receipt behavior preserved. Full final Linux1,014passed/Windows976passed38skips;77new cases, including two saved-artifact checks, not new captures. INC-049 trial/accounting count gap reproduced/fixed with negative evidence retained. This format version is not a new runtime model/Engine2 release. Sections below retain the v1 baseline contract unless explicitly extended.

## Capability and research boundaries

cloudguard/runtime_intake.py checks a dedicated bundle; scripts/runtime_intake.py exclusively creates a minimized report outside it. No network, subprocess, model, service, clock or sensor operations in the library/CLI. Tests launch the CLI and the existing whole suite has separately documented inert process cases.

Bind exact hashes, reuse normalized-capture/inventory validation, reject duplicate IDs/captures/event projections and declared cross-partition groups, require complete labels for observed windows, retain disagreement before optional adjudication. Empty/missing windows are not manufactured or called benign. Original votes/reasons stay in supplied files, postflight rechecks artifact hashes. Reports omit reasons, receipt/event bodies and input paths.

**Consistency is not eligibility.** Always false: independent_evaluation_verified, model_fitting_authorized, predictions_computed, per-run evaluation_eligible, binding_verified and receipt_semantics_verified; actions_executed empty. Two names/successful-looking receipts/candidate splits cannot change this. v1 receipts opaque, strict JSON/hash only; v2 selected source/count/snapshot/local-endpoint checks do not validate full protocol/coverage/collector alignment/native identity/human authenticity. E2-035 partial; no real captures/reviewer study obtained.

## Exact contract and limits

Use a dedicated trusted local directory, not the repository root. [Committed example](../data/runtime/intake-example/README.md) is entirely synthetic. Module constants define schemas; all listed object fields required, no extra fields except opaque receipt contents. Optional references explicitly null, not omitted.

| Artifact | Fields |
|---|---|
| Manifest | schema_version=runtime_intake_v1 or runtime_intake_v2; dataset_id; inventory reference; guidelines reference; window_seconds integer1..3600; runs1..20; reviews0..2; adjudication reference/null |
| Reference | path, lowercase64hex sha256 of exact raw bytes |
| Run | run_id; capture reference; data_role development/candidate_evaluation; split development/train/validation/test; groups; receipts |
| Groups | template_family, deployment_id, run_family; capture scenario_group also checked. Each (kind, ID) in only one split; within-split sharing allowed |
| Receipts | accounting, identity, timing references/null; v1 opaque objects, v2 typed wrappers/source bindings per RUNTIME_RECEIPTS.md. Missing roles visible; full validity never inferred |
| Review | schema_version=runtime_review_v1; reviewer_id; origin synthetic_fixture/human_submission; guidelines_sha256; blinded exact true; labels |
| Adjudication | schema_version=runtime_adjudication_v1; adjudicator_id; guidelines_sha256; review_sha256 exactly two distinct original review hashes; labels |
| Label | run_id, asset_id, start_epoch integer0..4134067200; label benign/suspicious/unknown; reason nonempty string up to500characters |

IDs contain 1–128 ASCII letters/digits/underscore/dot/slash/colon/hyphen, no whitespace. Nonempty reason is not scientific adequacy. Reviewer IDs must differ but are not authenticated; adjudicator need not have a third distinct ID. Actual independent annotation and professor-approved guidelines remain prerequisites.

Paths: forward-slash relative ASCII components, exact role directory, matching extension: inventory/*.json, captures/*.json, receipts/*.json, labels/*.json, guidelines/*.md. Nested nonhidden directories allowed; absolute/drive/backslash/parent/dot/hidden/double-slash/wrong-role paths refused. Regular files only; symlink components refused; resolved paths inside root. Trusted filesystem/root/output parent: not hostile inode/reparse/race/OS sandbox guarantees.

Limits: manifest 100,000 bytes; each referenced artifact 1,000,000 bytes; aggregate unique referenced bytes 8,000,000; 2,000 observed windows and 2,000 labels per submission. Aggregate excludes manifest/repeated parser/postflight IO, not a total IO/CPU/time/memory sandbox bound. Duplicate JSON keys/nonfinite constants/overflow floats refused. Existing capture/inventory schemas apply (2,000 events/capture); guidelines nonblank strict UTF-8.

Development role iff development split; synthetic cannot be candidate. Exact historical exploratory hashes guarded against promotion even after copying/renaming: output/engine2-normalized-20260928/capture.json SHA5dc76e982fec7258ebebeeb96f2021271a1d8b8d8acedc83f1871d1ddb6fb2ae; output/engine2-instrumented-normalized-20260928/capture.json SHA948aecb953f522ee49521a871b9179d263a21aebb238bda15a8ba9ee582ffebc. List bounded/nonexhaustive; reserialization/changed provenance/structural variants may evade it. All candidates remain ineligible regardless. Historical bytes unchanged.

Overlap uses runtime.event_keys (asset, container, float epoch, kind), ignores event IDs, is lossy/conservative, not semantic similarity detection. Run/capture IDs and capture hashes unique per bundle. Declared groups do not prove unseen data.

Labels key (run_id, asset_id, start_epoch), computed only for nonempty runtime.windows. Each submission/adjudication covers exactly that set once. With two reviews, any unknown vote contributes to unknown_pairs, excluded from known_agreement_fraction. Fraction agreements/known_pairs or null: not accuracy, kappa or independent reliability. Adjudication cannot flip agreed known votes; disagreements/unknowns can resolve or remain unknown. Original review hashes and pre-adjudication statistics preserved.

## Reproduction and report interpretation

From the configured repository root:

```powershell
.venv/Scripts/python.exe scripts/runtime_intake.py --manifest data/runtime/intake-example/manifest.json --output output/my-fresh-intake-report.json
.venv/Scripts/python.exe -m pytest -q tests/test_runtime_intake.py
```

Linux uses existing environment's Python. No Docker/Ollama needed. Fresh output outside bundle; parent must exist. Existing output refused before reading inputs, never replaced. Consistency exits0, not eligibility. Rejection exits1 with only status/error class/false gates/no actions, not exception text/input contents. Output-creation/refusal errors sanitized stdout. Interrupted/write-failed report may be incomplete; no fsync/durable transaction/hard deadline guarantee. Incomplete output failed, never edited into success.

Executed once: [synthetic report](../output/engine2-intake-synthetic-20261006.json), three observed windows/three invented events; one known agreement, one disagreement, one unknown pair; known fraction 0.5. Adjudication: one benign/two unknown. Six unique artifacts, 3,596 bytes, three missing receipts; all research/action gates false. Fixture votes/IDs authored by software development, not independent people/attack observations.

## Historical v1 verification and preserved negatives

83new synthetic cases: valid/empty/no-review/human-declaration inputs; hashes/groups/duplicates/development promotion/historical guards; paths/strict JSON/schema/reviewer/adjudication/window/resource/nonregular/symlink/postflight checks; actual CLI no-overwrite/redaction and example. TargetWindows82pass/1symlink-privilege skip2.40s. Full [Windows XML](../output/engine2-intake-windows-tests-20261006.xml)899pass/38skips (37existing Linux-only/1symlink privilege),12.13s console/XML12.126; [Linux XML](../output/engine2-intake-linux-tests-20261006.xml)937pass/no skips57.78s console/XML54.962. Both937collected/zero failures/errors. Timing difference undiagnosed, no clock/performance claim. Ruff105files/pipcheck pass.

Initial sandbox60fail13pass1skip3.25s, Path.resolve(strict=True) WinError5; host rerun removed permission failures. [Manual context](../output/engine2-intake-sandbox-attempt-20261006.json), explicitly not raw output. Initial host72pass1fail1skip2.53s/XML2.321: test monkeypatched FILE_LIMIT but Python default already bound. [Original failing XML](../output/engine2-intake-initial-host-tests-20261006.xml), SHA c457628fb1078177626e2e17324828602bdd3918cc3af3091317eaaf1272f959. Fix test using actual oversized artifact, no production safeguard changes. INC-048/WL-058 exact commands.

## Next acceptance

Within E2-035, selected typed source bindings are now implemented; full receipt compatibility/coverage/collector correlation remains open. Next prepare supervisor-reviewed threats/guidelines/reviewer pack and eligible-capture checklist. Obtain genuine blinded human submissions/comparable captures, not generated labels or promoted development data. Frozen held-out groups, planned models, misses/false alarms/uncertainty/delay/overhead/integration remain separate gates. No automatic real collection/native intervention/response/benchmark/publication readiness implied.
