# Synthetic runtime comparator integration

E2-043 / RQ3 / E2-004, 7 October 2026. Implemented/software-tested, not an independent detection benchmark or new engine version.

## Change and boundaries

`integration.replay(..., runtime_ml="both")` and `integrated-replay --runtime-ml` connect the existing Isolation Forest and autoencoder to both integrated modes. Choices: `isolation-forest`, `autoencoder`, `both`. Omission preserves the old modes. No algorithm, dependency, architecture, frozen tag or research authorization change.

Saved runtime/input identity is validated first. Non-synthetic declarations are refused before fitting or optional active Engine1 stages. The wrapper checks frozen inputs/sources, calls bounded baseline-only comparators, validates input/source hashes, exact asset/start-window identities and scored/abstained accounting, then optionally runs Engine1. Original model reports remain under `runtime_comparators`; asset contexts contain window indices for each model. Missing observations/abstentions remain visible. Declarations are not authenticated provenance; hash checks are not hostile filesystem-race protection.

Different-scale scores remain separate. No fusion, calibrated threshold, binary prediction, automatic response, confirmed threat or real-data fitting authority. Parent statistical threshold does not alter nested comparators' existing threshold 3. Model failure rejects the operation, without clean fallback. Selected implementation hashes include chosen model files. No serialized models are accepted or written.

## Simple safe reproduction

From repository root with the existing Python environment activated:

```powershell
python scripts/integration_check.py --engine1-pipeline --runtime-ml both --output output/my-fresh-ml-integration.json
```

Use a fresh filename: overwrite is refused. This example reads invented captures, performs actual local lexical retrieval/scoring and synthetic fits, and calls no Ollama inference or TCP probe. Open the JSON and check nine boolean checks, then inspect each model's scored/abstained counts/windows. Explicit abstention is valid, not a clean verdict. Rejected ML receipts retain owned safe backend diagnostic fields when available.

Direct CLI:

```powershell
python -m cloudguard.cli integrated-replay data/integration/redis-auth-only.yaml data/runtime/ml-observation-synthetic.json --baseline data/runtime/ml-baseline-synthetic.json --inventory testbed/inventory.json --engine1-pipeline --kb knowledge/sources.json --runtime-ml both
```

Do not substitute sensor/real-study captures. Existing pipeline model/probe options still require their separate operational permissions.

## Actual evidence

- Full suites before the final launcher/CLI test addition: Windows1284passed38skipped/27.42s, Linux1322passed/106.83s; both1322collected/zero failures/errors. `output/ml-join-full-{windows,linux}-20261007.xml`.
- Final corrected integration target79passed/8.35s: `output/ml-join-corrected-target-windows-20261007.xml`. Seventeen new cases: actual direct-model equality, invalid selection, separate counts/identities, default no-fit, failure-before-pipeline, sensor declaration refusal, component mismatch rejection, actual CLI/runner/no overwrite. The final added case was not in the earlier full suites.
- Initial target73pass; later target78pass/one incorrect test-entry-point failure. Failure receipt `output/ml-join-final-target-windows-20261007.xml` preserved; INC-065. Corrected to `cloudguard.cli` without application changes.
- Both fixed demos nine checks passed: `output/ml-join-synthetic-{windows,linux}-20261007.json`. Actual synthetic fits/local retrieval, no inference/TCP. Cross-platform execution is not independent evaluation.
- Ruff/124-file formatting and both environments' pip checks passed. Documentation/publication checks recorded separately in WORK_LOG.

Next: genuine protocol/supervisor decisions, qualified capture timing/coverage/context and independent labels/data before real calibration/evaluation. Continuous acquisition and calibrated joint prioritization remain open.
