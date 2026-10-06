# Runtime annotation-unit index — coordinator-only

E2-035/RQ3/E2-004 offline preparation. **Implemented software, not an approved reviewer packet, actual labels or independent evaluation.** The [human-review pack](RUNTIME_LABELING_PROTOCOL.md) remains DRAFT — NOT APPROVED. Engine2's replay baseline already exists; this is an optional intake export, not an engine/model release. No stack/dependency change.

## Purpose and exact behavior

A coordinator needs to know which observed units a review must cover exactly. `cloudguard.runtime_intake.annotation_index(manifest_path)` reuses the existing intake validator and its postflight checks, then projects a sorted list of `(run_id, asset_id, start_epoch)` keys. This avoids manually reimplementing window boundaries or accidentally adding missing/empty windows as benign labels.

All existing manifest, role/path/hash/schema/byte/window/group/duplicate/development/review/adjudication and selected v2 source checks still apply, including rejection of the uncounted synthetic typed fixture. Invalid supplied reviews or changed artifacts cannot be bypassed to create an index. The tool validates existing submissions if supplied, but never exports votes or creates new submissions.

The existing `inspect(manifest_path)` and default CLI retain the original output. New keyword-only `include_window_index` requires an exact boolean and defaults false; true appends only observed_window_index to that consistency report. **That full report is not the minimized index and may contain reviewer declarations/agreement.** Use annotation_index/the CLI flag for the separate projection, not the full report as a reviewer handout.

## Index contract

Protocol `runtime_annotation_index_v1`, status `observed_units_indexed`. It contains exact manifest/inventory/guideline SHA256s, window_seconds, observed_window_count, empty_capture_count, missing_windows_not_materialized=true, units and explicit limitations. Each unit contains only run_id, asset_id and integer start_epoch, sorted lexically by run/asset then numerically by start. Bounds inherited: at most20runs/2,000units, existing file/aggregate byte limits.

No labels/reasons/reviewer names/adjudication/receipt bodies/events/count features/model scores/groups/split assignments/seed answers or input paths are exported. No label file, neutral alias, independent context or synthetic human vote is generated. Always false: labels_created, supervisor_approval_verified, blinding_verified, independent_evaluation_verified, model_fitting_authorized, predictions_computed; actions_executed empty. Hashing a draft is not its approval.

**Not a blinded packet:** run/asset IDs, epochs and hashes can reveal/link scenarios. This is a coordinator-only allocation aid, not anonymity, de-identification or a guarantee against prediction leakage. Audit neutral aliases and provide actual approved independent context separately before real reviewers receive anything. Related runs still need approved grouping/sample decisions; an index is not sample adequacy or ground truth. Missing intervals/coverage are not inferred; preserve them in the [private ledger](templates/runtime-case-ledger.md).

## Safe reproduction

At the configured repository root, existing Windows environment:

```powershell
.venv/Scripts/python.exe scripts/runtime_intake.py --manifest data/runtime/intake-example/manifest-typed-counted.json --annotation-index --output output/my-fresh-annotation-index.json
.venv/Scripts/python.exe -m pytest -q tests/test_runtime_annotation_index.py tests/test_runtime_intake.py tests/test_runtime_receipts.py
```

Linux uses the existing environment's Python. No Docker/Ollama/collector/services needed. Output parent must exist and be outside the input bundle. Use a new output/temp/report name; existing output is refused before input reading. Do not overwrite saved evidence. Actual private outputs belong in private/runtime-labeling/ or approved access-controlled storage, not public output/. Ignore/publication policy is not encryption or protection after copying elsewhere.

Success exits0 for indexing consistency only. Input rejection exits1, saves no units, only a sanitized rejection envelope/error class/false gates; exception text/input paths are omitted. Output refusal/failure uses the existing sanitized stdout envelope. Incomplete write/interruption is not a valid index; no fsync/transaction/hard deadline or hostile-filesystem guarantee is added. No network, sensor, model, service, clock or subprocess in the library/CLI; tests invoke the CLI locally.

## Executed example and evidence limits

[Synthetic index](../output/engine2-annotation-index-synthetic-20261006.json) was generated once from the unchanged counted fixture:3observed units/0empty captures, no labels or enabled research/action gates. It lists demo-run/compose/redis and three existing 60-second units. Its underlying guidelines/capture/receipts are development fixtures, not approved study evidence or real reviewer work. WL-061 records exact verification, preserved initial test failure and final suite receipts.

Next still requires actual supervisor decisions, claim-appropriate comparable data/timing/coverage/identity, genuinely independent humans and frozen grouped evaluation before model fitting/effectiveness claims. This exporter does not satisfy those gates or authorize operational experiments.
