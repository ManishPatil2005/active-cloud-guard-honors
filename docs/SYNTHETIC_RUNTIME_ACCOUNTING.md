# Synthetic runtime decision accounting

E2-039 / E2-004 / RQ3, prepared7October2026 (Asia/Calcutta). **Software arithmetic only, not independent detector evaluation.** This addresses the proposed evaluation's denominator/abstention requirement while real supervisor/context/data/labels/calibration remain pending. It does not approve that proposed protocol or convert model scores into binary predictions. [Current status](CURRENT_STATUS.md), [unapproved proposal](ENGINE2_SUPERVISOR_REVIEW_PROPOSAL.md).

## Scope and architecture

New isolated cloudguard/runtime_accounting.py, pure summarize_synthetic(document), plus fixed scripts/runtime_accounting_check.py and one developer-authored arithmetic fixture. No dependencies, default CLI/Engine1/Engine2 algorithm, capture/intake schema, native23-source closure or Python/Compose/Ollama/Chroma change. Existing metrics.py stays unchanged: it requires booleans and includes per-case Wilson intervals, which cannot simply be transferred to correlated runtime windows. The new path cross-checks its decided-known arithmetic against existing metrics without emitting confidence intervals or claiming independent groups.

No actual runtime windows, model reports or human review files are ingested. The supplied decisions are invented **accounting examples**, not predictions from statistical replay/IF/autoencoder; those ML binary_prediction fields remain null. No fitting, calibration, thresholds, detector scores, network/subprocess/service/clock/collection or automatic response in the new library/runner. Full regression tests still exercise earlier implemented synthetic-model/inert software paths; those tests are not a new research experiment.

## Input contract

Exact document fields: schema_version=synthetic_runtime_accounting_v1, origin=synthetic_fixture, units=list of0..2000records. Exact record fields: unit_id, run_id, label, decision, availability. IDs reuse the runtime ASCII1..128identifier pattern; unit_id globally unique. Enum values:

- label: benign / suspicious / unknown;
- decision: flagged / not_flagged / abstained;
- availability: observed / missing / unusable.

Missing/unusable declared slots **must** have unknown label and abstained decision; never manufacture benign or not_flagged for unavailable evidence. Observed unknown labels may retain an explicit declared decision, but cannot enter TP/FP/TN/FN. Exact fields/types/bounds/duplicates invalid enums refuse. Source/origin metadata is cooperative, not authenticated provenance: never relabel real or private decisions as synthetic. The fixed runner has no arbitrary input/model argument.

These are supplied planned-unit placeholders, not fabricated events or additions to runtime.windows. They do not establish complete planned-run coverage or authenticate window/run mapping. represented_run_count counts declared IDs only, not independent families or an actual failed-run ledger. A future real study must separately retain all planned/launched/failed/missing runs and adjudicated context using approved protocols.

## Output and denominators

Protocol synthetic_runtime_accounting_report_v1/evidence synthetic_software_only. Count every declared unit by availability. For observed units retain all3×3label/decision cells, label totals and decision totals. No unit IDs/reasons/body projected into the aggregate report. Conditional confusion includes only observed known labels with flagged/not_flagged decisions:

| Label | flagged | not_flagged | abstained |
|---|---|---|---|
| suspicious | TP | FN | positive_abstentions, not silently discarded |
| benign | FP | TN | negative_abstentions, not silently discarded |
| unknown | Retained unknown cell, not FP/TP | Retained unknown cell, not TN/FN | Retained unknown cell |

Conditional precision=TP/(TP+FP); recall=TP/(TP+FN); false_positive_rate=FP/(FP+TN); F1=2TP/(2TP+FP+FN). These describe the **decided-known subset**, not every declared case. Every undefined denominator yields null, not0/1. Inclusive fields explicitly distinguish:

- all_known_positive_detection_fraction=TP/all observed suspicious units, including positive abstentions;
- all_known_negative_flag_fraction=FP/all observed benign units, including negative abstentions (not renamed conditional FPR);
- known_decision_coverage=known decided / known observed;
- observed_decision_coverage=all explicit observed decisions / observed units, including unknown-label decisions.

No treatment of unknown/unavailable units as benign, no confidence intervals, sample adequacy, attack accuracy, delay, overhead or energy estimate. Empty input is no_declared_units; otherwise accounting_computed, not “safe.” Output approval/independence/real-evaluation/labels-created/model-fitting/predictions/calibration/threat flags false and actions empty. These are boundaries, not proof input metadata is genuine.

Input canonical SHA256 hashes validated JSON with sorted keys/compact separators; it is **not original-file SHA256**, preserves unit-array order and changes when order changes even though aggregate counts do not. Runner separately records exact input file SHA and selected library source SHA (not full runner/environment attestation), checks fixture hash after summary and uses exclusive output creation. Malformed/changed inputs reject with error class only; interrupted/write failures may leave incomplete reports, no transactional/fsync guarantee.

## Fixed arithmetic example and safe reproduction

[Fixture](../data/runtime/accounting-synthetic.json) has11invented slots:9observed covering every label/decision cell once,1missing,1unusable. No humans/scenarios/attacks/model outcomes represented. ConditionalTP/FP/TN/FN each1; positive/negative abstention each1. Conditionalrecall1/2 while inclusive positive detection1/3; neither number is measured engine effectiveness. Four practice run IDs do not mean four independent experimental replications.

At repository root using existing environment, choose a fresh filename:

```powershell
.venv/Scripts/python.exe scripts/runtime_accounting_check.py --output output/my-fresh-accounting.json
.venv/Scripts/python.exe -m pytest -q tests/test_runtime_accounting.py
```

Linux uses its environment's interpreter; no collector/Docker/Ollama setup required. Check all six smoke checks true, declared11/observed9/missing1/unusable1, separate abstentions/unknown cells and no real authority/actions. Existing output is refused before fixture reads; do not overwrite historical artifacts or interpret invented decisions as independent labels. Raw input is bounded by existing read_json; in-memory library applies record/type limits, not a hard memory/deadline sandbox.

## Verification and next boundary

46new tests cover all observed cells, undefined/all-unknown/all-abstained/unavailable cases, strict document/unit types/IDs/enums/origin/extra fields/duplicates/2000record boundary, known decided equivalence to unchanged metrics, nonmutation/order-independent aggregates with changed canonical hash, no unit-ID projection, unknown flag not FP and exclusive CLI/no other artifact. Initial34target and final46target XMLs preserved separately; actual full-suite/demo results in [EVIDENCE](EVIDENCE.md)/WL-065 [WORK_LOG](WORK_LOG.md). No new failure is claimed if checks pass; earlier incidents remain preserved.

Next real acceptance still requires genuine approved target/context/sampling/qualification/independent labels, reviewed eligible-real-data evaluation/calibration path and grouped untouched evaluation. This implementation supplies arithmetic for software tests only; it does not satisfy those gates or approve a statistical estimand. Never connect raw uncalibrated model scores to these decision labels without a separately reviewed protocol.
