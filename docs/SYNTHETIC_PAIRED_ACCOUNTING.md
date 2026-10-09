# Matched synthetic decision comparison

E2-046 / RES-002 / E2-004, 9 October 2026. Software preparation for paired comparisons, not an executed ablation study, independent detector benchmark or approved protocol.

## What changed and why

The isolated `cloudguard/runtime_paired_accounting.py` compares two supplied synthetic accounting documents using the existing `runtime_accounting.summarize_synthetic` and `metrics.fp_reduction`. Existing Engine1/Engine2/scoring/model/intake/CLI algorithms and dependencies are unchanged. A fixed fresh-output runner and one four-unit invented fixture demonstrate the arithmetic without importing model backends, fitting, inference, collection or network operations.

Acceptance: exact paired population and context, complete transition/abstention/missing/unknown accounting, preserved undefined/negative quantities, no generated model predictions or evaluation authority. This supplies one calculation prerequisite of RES-002/E2-004; it does not complete matched experimental design, genuine humans/labels, grouped held-out comparisons or uncertainty estimates.

## Input and output contract

Exact outer keys: `schema_version=synthetic_paired_accounting_v1`, `origin=synthetic_fixture`, `baseline`, `variant`. Each child obeys the unchanged [synthetic accounting contract](SYNTHETIC_RUNTIME_ACCOUNTING.md): at most2,000unique units, strict schema/types/enums/IDs; missing/unusable must remain unknown+abstained. Thus at most2,000paired units/4,000child records, not independent samples. Both unit-ID sets must match exactly. For each unit, run ID, label and availability must match; only decision may differ. Different order is allowed, but dropping/adding units, changing labels/run membership/availability or duplicate units is refused. Declarations are not authenticated provenance; never relabel real/private inputs as synthetic.

Output retains both complete aggregate accounting reports, all declared3×3decision transitions, separately known-observed transitions, changed decision count, variant-minus-baseline metric/coverage differences, confusion-count/positive-negative abstention changes and FP **count** reduction. Unknown and unavailable units stay in declared totals, not binary confusion. A missing metric on either side gives a null difference, not a zero. Negative changes/reductions are preserved; FP reduction is null when baselineFP=0. Do not call count reduction rate reduction or infer quality from conditional precision alone.

Canonical input hashes reflect compact sorted-key JSON and preserve array order; aggregates can agree while hashes differ after reordering. No raw unit/run IDs or reasons are projected into the report. No model-score thresholds, score conversion, confidence intervals/bootstrap/significance, labels, fitting, latency, overhead or energy are produced. Approval/independent/real-evaluation/calibration/threat flags false, actions empty.

## Beginner example and interpretation

Activate the existing environment, open repository root, choose a new output name:

```powershell
python scripts/runtime_paired_accounting_check.py --output output/my-fresh-paired-accounting.json
python -m pytest -q tests/test_runtime_paired_accounting.py
```

Open JSON and check six true checks. The fixture has three observed units (one suspicious, one benign, one unknown) and one missing unit, with identical contexts on both sides. The variant changes the benign decision from flagged to abstained; everything else is unchanged.

| Quantity in this invented example | Baseline | Variant |
|---|---:|---:|
| Conditional TP / FP | 1 / 1 | 1 / 0 |
| Negative abstentions | 0 | 1 |
| Known decision coverage | 1 | 0.5 |
| Conditional precision | 0.5 | 1 |
| Conditional false-positive rate | 1 | null |

FP count reduction is1, but coverage fell and the variant decided **no benign unit**, so its conditional FPR is undefined. This is an arithmetic lesson, not engine improvement. Unknown decisions do not enter confusion; the missing slot is never silently removed. Three practice run IDs are not three independent experimental groups.

The runner has no arbitrary input/model/service command. Existing output is refused before reading inputs. It checks raw fixture and five selected source/launcher hashes before/after arithmetic and emits error class only on refusal. Bounds/hash checks are cooperative consistency, not complete import/host attestation or hostile filesystem-race defense. Interrupted/write failures can leave incomplete output; no atomic/fsync guarantee.

## Verification and remaining work

48 new cases cover all27label/decision transitions, strict schemas, exact pairing/context, availability/duplicate/missing refusals, null denominators, negative changes, order/nonmutation, absence of raw units/authority and actual exclusive runner. Paired+existing accounting target94pass on Windows1.11s/Linux1.80s. Both fixed six-check examples saved as `output/paired-accounting-synthetic-{windows,linux}-20261009.json`; full calculated results agree and raw input/five selected source+launcher hashes match current files. Full Windows1,362passed/38existing skips,1,400collected/zero failures/errors,96.59s (96.554s XML), `output/paired-accounting-full-windows-20261009.xml`. Docs18pass/0.40s (0.108s XML), `output/paired-accounting-docs-20261009.xml`. Ruff/129-file formatting and both pip checks passed. Initial lint caught an unused import in the new runner; removed before the passing target, not a runtime/model fault. Publication results/exact commands in WORK_LOG. The full Linux suite is not rerun for this isolated additive path; latest historical full Linux checkpoint remains1,352passes on8October, not1,400claimed passes today.

Next actual research still needs approved scope/protocol, comparable qualified capture timing/coverage/context, independent blinded labels/grouped data, calibration and matched ablations/uncertainty/overhead/energy. Uncalibrated runtime model scores must not be converted into these invented decisions without a separate reviewed protocol.
