# Synthetic runtime ML comparator — software prototype

7October E2-040: [optional backend diagnostics](RUNTIME_ML_BACKEND_DIAGNOSTICS.md) distinguish import/module/metadata/version categories without raw private details or automatic package repair. RuntimeMLBackendError remains a RuntimeError subclass; fixed CLI rejected receipts gain backend_diagnostic. Success calculated fields/default model behavior unchanged, selected source hashes change. Original intermittent Windows cause remains unknown (INC-056); only diagnostic loss/misleading install advice reproduced/fixed (INC-057). Older checkpoints below historical.

Current E2-037 follow-up: a separate [synthetic reconstruction autoencoder](SYNTHETIC_RUNTIME_AUTOENCODER.md) is now implemented/software-tested, using the same optional backend and four features. Shared synthetic preparation/guards/postflight/version helpers were extracted here; Isolation Forest calculated fields still match its saved final result, excluding legitimately changed selected source hashes/Python version. Default runtime/intake unchanged. The original E2-036 checkpoint below remains historical; its “no autoencoder”/“unimplemented” wording describes that earlier milestone, not current software status. Real-data evaluation of both models remains open.

E2-036/E2-004/RQ3: isolated optional Isolation Forest implementation for **synthetic software development only**, 6 October 2026. User proceeded with the offered offline/synthetic branch; this is not supervisor approval, real-data fitting authority or an independent security evaluation. Engine2's existing statistical replay remains the default. No third engine, stack migration, autoencoder, calibrated threat detector, TCI integration or automatic response.

## Implementation and source basis

`cloudguard/runtime_ml.py` uses the pinned scikit-learn1.9.1 IsolationForest implementation through a lazy optional import. Isolation Forest uses random partitions and path lengths; this wrapper negates score_samples so higher positive scores indicate relatively shorter isolation paths. Scores are **not attack probabilities**. It does not call predict/decision_function or use the library's contamination-derived binary threshold. [Official API and score convention](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html), [package provenance](https://pypi.org/project/scikit-learn/1.9.1/).

Reusing the established implementation avoids introducing a custom forest algorithm whose correctness would need separate review. `runtime-ml` is a new optional extra, not a core/vector replacement. The original lockfiles remain historical environment snapshots; [optional package snapshot](../requirements-runtime-ml-20261006.txt) records the installed Windows/Linux package versions. No existing package upgraded: Windows already had NumPy2.5.3; Linux added it with the other absent ML dependencies. Python versions differ and are recorded in actual outputs.

## Input, separation and output contract

`compare_synthetic(baseline_paths, observation_path, inventory, window_seconds=60, seed=42, n_estimators=64, max_samples=256)` accepts1..20baseline files and one observation. Existing normalized schema/inventory/file limits apply. **Every capture must declare source=synthetic**; declared sensor exports are rejected before backend import/fitting. A caller can forge source metadata; this is a cooperative software contract, not authentication or a guarantee against relabeling real data. The published smoke CLI accepts only the fixed committed fixtures, not arbitrary input paths.

Reuse existing runtime.analyze checks for capture IDs, scenario-group separation and event projection overlap. Compare initial and statistical-comparator hashes, then re-read capture/inventory hashes after fitting/scoring. Trusted local filesystem only: not an inode-race/reparse/durable sandbox guarantee. Default runtime.py and intake schemas/report behavior unchanged; no new collector/clock/native-job integration.

Reuse exact nonempty windows and four existing features, in order: event_count, process_start, network_connect, file_open. Total count is redundant/correlated with kind counts; preserving it gives an explicit same-feature software comparison, not proof of good feature design. Future features/grouping/sample design require actual protocol decisions. Canonical training order is asset/capture_id/start_epoch. Fit **per asset, on baseline windows only**. Observations never enter fitting, normalization, threshold selection or calibration. No labels/reviewer data are ingested or generated.

Engineering budgets: exact integer seed0..2^32-1, trees1..128, subsample2..256, seconds1..3600, at most4,096total baseline windows. Default64trees, at most256rows/tree, n_jobs=1 and temporary threadpool limit1; the context restores prior process limits. Not a hard CPU/deadline/memory/power bound. At least8baseline windows and2distinct feature rows required per observed asset; these are software guards, **not research sample adequacy**. Insufficient/constant baselines yield null scores and explicit abstentions. Empty observations are not synthetic benign windows. Missing intervals/coverage stay unknown.

Protocol runtime_synthetic_iforest_v1, evidence_level synthetic_software_only. Output records parameters, dependency versions, selected implementation hashes, fitted asset/window counts, observed unit scores/status/null binary_prediction and the unchanged statistical comparison. No model object, pickle/joblib model, weights, executable payload or cached training artifact is saved. Actual synthetic_fitting_performed/synthetic_scoring_performed are distinct from real_data_fitting_authorized=false. Approval/independent evaluation/labels/calibration/threat confirmation/live sensor remain false; actions empty. This does not modify intake's always-false fitting/eligibility gates.

Summary status: no_observations when there are no observed units; synthetic_scoring_abstained when all units have null scores; synthetic_scores_computed when at least one is scored. scored_window_count and abstained_window_count sum to all observed units, including partially scored assets. INC-052 preserves the initial misleading all-abstention status and its two reproduced failures; do not interpret the preliminary passing suites as coverage of this gap.

No false-positive/false-negative/accuracy/ROC/F1/attack-delay/overhead/energy claim follows from invented feature counts or passing tests. Demonstration scores and engineering parameters must not be tuned on future held-out real data or treated as independent labels. Do not promote these fixtures into the research test set.

## Reproduction, optional installation and privacy

At the configured repository root, existing environment:

```powershell
.venv/Scripts/python.exe -m pip install --only-binary=:all: --index-url https://pypi.org/simple -r requirements-runtime-ml-20261006.txt
.venv/Scripts/python.exe scripts/runtime_ml_check.py --output output/my-fresh-synthetic-ml.json
.venv/Scripts/python.exe -m pytest -q tests/test_runtime_ml.py
```

Linux uses its environment's Python; no Docker/Ollama/collector/service required. The optional extra can also be installed with the project's normal packaging workflow. Without it, default/core code remains usable; backend-dependent tests explicitly skip and fitting requests fail visibly, never fall back to fabricated scores. A wrong scikit-learn version fails rather than silently changing the experiment.

The fixed runner creates output exclusively before reading/fitting. Existing output is refused. Use fresh report/temp paths and preserve earlier reports. Rejected checks emit an error class, not exception text; interrupted/failed writes may be incomplete and cannot be edited into success. No fsync/transaction/hard deadline guarantee. Reports contain synthetic IDs/time/count features; actual private information must never be disguised as synthetic or committed. Never load a user-supplied serialized model. No library/runner network, subprocess, service, clock or sensor operation; package installation is the separately observed setup step.

## Evidence and remaining work

Two fixed smoke receipts and software regression XMLs are linked in EVIDENCE/WL-062, including preserved initial test failures and final verification. Tests compare scores to the established backend and test input/fitting/abstention/identity/mutation/resource/optional-dependency/default-compatibility boundaries. This is implemented/software-tested synthetic ML, **not independently evaluated detection**. Actual supervisor decisions, sufficient independent context, comparable timing/coverage/identity, genuine reviewers, frozen grouped real-data partitions and approved analysis remain open. Autoencoder and real-data model comparisons are separate unimplemented work.
