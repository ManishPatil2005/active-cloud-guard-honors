# Single-pass comparator window indexing

E2-045 / V2-004 / E2-004, 8 October 2026. A narrow efficiency refinement of the existing integrated workflow; no new engine or detection model.

## Problem, implementation and acceptance

The previous asset-context loop filtered each comparator's complete window list for every asset, including assets without observations. For A contexts and W comparator windows, that mapping work inspected A×W rows per comparator. This is source-level work accounting, not a measured latency/energy result.

`cloudguard/integration.py` now builds a local comparator-name → asset-ID → original-window-indices map in one traversal per comparator. Context lookup reuses those lists and supplies a fresh empty list when no windows exist. Original order/positions, separate comparator names, abstention/status/score fields, missing states and complete component reports stay unchanged. No persisted cache, model reuse, score fusion, source/identity guard relaxation, dependency or architecture change.

Index construction inspects W rows and stores W index entries per comparator; subsequent per-asset lookups avoid re-filtering W rows. This uses additional temporary index dictionaries, not a guarantee of lower peak memory. The existing validation pass remains. Total model parsing/fitting/scoring costs are not eliminated; there is no measured speedup or energy-saving claim.

## Evidence and failures preserved

- Before-change traversal test failed with **5 passes instead of 2** for four inventory contexts and three observation windows: one existing identity-validation pass plus four full-list mapping passes. Actual synthetic model fit, not an injected model score. `output/window-index-before-windows-20261008.xml`, 1failed/7.56s; INC-066 preserves the negative.
- Initial post-change integration target: **106 passed / zero failures**, 10.87s, `output/window-index-target-windows-20261008.xml`. Includes the first four new cases. Two final complete-report comparison cases were added afterward and included in the full suites, not retroactively claimed in this target.
- Six new cases cover two-pass actual replay accounting, ordered/interleaved multi-asset/model mapping, missing/empty reports, no component mutation/list aliasing, one traversal of a 1,000-row/50-asset invented list, and complete report equality against legacy mapping in rule and Engine1 pipeline modes. Only the existing pipeline measured timings are excluded from equality; scores/abstentions/provenance/context fields remain compared.
- Both fresh fixed demonstrations passed ten checks: `output/window-index-synthetic-{windows,linux}-20261008.json`. Existing launcher, actual synthetic IF/autoencoder fits and local lexical retrieval/scoring, no Ollama inference/TCP/sensor operations. Measurements collected under concurrent regression activity are not a before/after benchmark.
- Final whole suites: Linux1,352passed/397.21s console (379.825s XML); Windows1,314passed38skipped/49.47s (49.452s XML), both1,352collected/zero failures/errors/final six new cases included. `output/window-index-full-{windows,linux}-20261008.xml`. Docs18pass/0.17s (0.115s XML), `output/window-index-docs-20261008.xml`. Ruff/126-file formatting and both environments' pip checks passed. Both demos' source/input/launcher bindings match current files; historical MEMORY/original negative import unchanged. Exact commands/publication review in WORK_LOG/current MEMORY. No independent efficiency acceptance.

## Beginner reproduction

Activate the existing Python environment, open the repository root, and choose a fresh output filename:

```powershell
python scripts/integration_check.py --engine1-pipeline --runtime-ml both --measure-stages --output output/my-fresh-index-check.json
```

Open JSON: ten true checks confirm this example. `result.asset_contexts` still links Redis to each comparator's windows `[0,1,2]`; the other inventory assets retain empty indices/unknown observation state. Scores remain separate, null combined priority unchanged. Missing/abstained observations are not a clean verdict. Existing output is refused.

For the deterministic work-count and equivalence tests:

```powershell
python -m pytest -q tests/test_integration_window_index.py
```

The first test counts actual list traversals instead of asserting timing thresholds. Passing tests support software equivalence/work reduction, not detector generalization or independent efficiency evaluation. Real protocol approval, comparable capture timing/coverage, independent labels, calibration, matched overhead and energy work remain pending.
