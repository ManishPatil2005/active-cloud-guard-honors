# Synthetic reconstruction autoencoder — software contract

E2-037 / E2-004 / RQ3, 6 October 2026. Implemented and software-tested on **declared synthetic development data only**. This is an optional comparator inside Engine 2, alongside the statistical baseline and Isolation Forest. It is not another engine, supervisor approval, independently evaluated threat detection or permission to fit real telemetry. [Current status](CURRENT_STATUS.md) and [work log](WORK_LOG.md) distinguish those gates.

## Method and architecture

`cloudguard/runtime_autoencoder.py` uses the existing optional pinned scikit-learn 1.9.1 backend: StandardScaler and MLPRegressor. No framework/dependency installation or lockfile change occurred in this milestone. The MLP learns input-to-input reconstruction, with a narrower hidden layer: four inputs → two tanh hidden units → four continuous outputs. This is an undercomplete reconstruction autoencoder implemented through a regression API, not a pretrained model or binary classifier. [Official MLP API](https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPRegressor.html), [official scaler API](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html).

The four existing features retain their order: event_count, process_start, network_connect, file_open. Total count is redundant with kind counts; these are a same-feature engineering comparison, not validated security features. Per asset, **only baseline windows** fit the scaler and network. Observations are transformed and reconstructed afterward, never fed into training, tuning or threshold calibration. Score is mean squared reconstruction error in standardized feature space, retained at computed floating-point precision. It is neither an attack probability nor directly comparable to Isolation Forest's raw score scale. A larger numerical score cannot establish that one method is better.

Shared helpers in `runtime_ml.py` now prepare synthetic inputs, apply baseline guards, recheck hashes and report dependency versions. They reuse existing runtime parsing/windows/analyze checks; no new window algorithm. Isolation Forest's calculated report is regression-compared to its saved final result, excluding selected implementation hashes and Python version. Its source hash legitimately changes with this refactor. Default runtime.py, runtime_intake.py and cli.py remain unchanged.

## Bounded input and training contract

`compare_synthetic(baseline_paths, observation_path, inventory, window_seconds=60, seed=42, latent_dim=2, max_iter=500)`:

- Existing normalized capture/inventory size/schema/identity/group/event-overlap checks apply. Every source must declare synthetic before backend fitting; declared sensor exports are refused. Source metadata is cooperative, not authenticated provenance: never relabel private/real telemetry as synthetic.
- One to twenty baseline paths; at most 4,096 baseline windows. At least eight baseline windows and two distinct rows per observed asset. Missing/constant baselines abstain. These are engineering guards, not research sample adequacy.
- Exact integer seed 0..2^32−1, latent dimension 1..3, max_iter 1..2,000 and seconds 1..3,600. Defaults: LBFGS, alpha 0.0001, tol 0.0001, max_fun = 20 × max_iter (10,000 by default), temporary numerical thread limit one, no warm start/early stopping. Bounds are not hard memory/deadline/power guarantees.
- Scaler/network fitting warnings are counted without exposing raw warning messages. Convergence warnings yield synthetic_optimizer_not_converged; other fitting warnings yield synthetic_training_warning. Both prevent reconstruction and abstain. Reconstruction warnings yield synthetic_reconstruction_warning and abstain. Invalid iteration/loss/shape/nonfinite/overflow diagnostics reject rather than invent scores.
- Capture/inventory hashes are checked initially, against the statistical comparator and after fitting/scoring. This is trusted local-filesystem consistency, not race-proof sandboxing or authenticated physical identity.

Protocol `runtime_synthetic_autoencoder_v1`, evidence level `synthetic_software_only`. Every observed window has reconstruction_error or null, binary_prediction=null and partial_or_unknown coverage. Scored plus abstained counts equal all observed units, including partially scored assets. Empty observations are no_observations, not invented benign windows; all abstentions are synthetic_scoring_abstained, not a clean verdict.

Actual fitting attempts are recorded even if convergence fails: synthetic_fitting_performed=true does not mean usable scoring or approved research. Training attempts include window count, iterations, loss, warning count/category flag and whether reconstruction was attempted. Synthetic scoring is true only for computed nonnull scores. Real-data fitting authority, supervisor approval, independent evaluation, labels, calibration, confirmed threat and live sensor flags remain false; actions empty. The unchanged statistical result, selected source hashes and dependency versions are retained. Selected hashes are not full environment attestation.

## Safe reproduction

From repository root, using the existing optional environment:

```powershell
.venv/Scripts/python.exe scripts/runtime_autoencoder_check.py --output output/my-fresh-autoencoder.json
.venv/Scripts/python.exe -m pytest -q tests/test_runtime_autoencoder.py tests/test_runtime_ml.py
```

Linux uses its Python equivalent; Docker, Ollama and a collector are not required. If the optional packages are absent, install the separately pinned `requirements-runtime-ml-20261006.txt` using the existing [ML installation procedure](SYNTHETIC_RUNTIME_ML.md). Do not change core dependencies or load supplied serialized models. Missing/wrong backend fails visibly, with optional-dependent tests skipped when unavailable; no fabricated fallback.

The smoke runner accepts only the fixed committed baseline/observation fixtures and creates its output exclusively before fitting. Choose a new filename each run; never replace a historical receipt. Its six checks cover three observed units, actual synthetic fitting, valid nonnegative scores, complete denominators, null binary predictions and no real authority/actions. A failure emits a failing receipt/exit 1, not a success disguised by nulls. Exceptions expose only an error class. Interrupted writes may be incomplete; no transactional/fsync guarantee.

Deliberate negative diagnostic, also use a fresh filename:

```powershell
.venv/Scripts/python.exe scripts/runtime_autoencoder_check.py --max-iter 1 --output output/my-fresh-autoencoder-negative.json
```

On the saved fixture/environment this actually produced one convergence warning, one training iteration, no reconstruction attempt, zero scored/three abstained units and exit 1. This tests abstention, not detection. Do not suppress warnings or increase iterations until a desired research metric appears.

## Evidence, privacy and limits

[Evidence index](EVIDENCE.md) retains final cross-platform demonstrations, five targeted XML checkpoints, full suites, the deliberately nonconverged receipt and the two-failure precision regression. Earlier successful smoke files used six-decimal rounding and are historical, not final precision verification; their source digests refer to uncommitted states whose complete source bytes were not separately archived. Final source-bound receipts and source are committed together. INC-053 records test fixture lint mistakes; INC-054 records actual precision loss and its fix. No negative evidence was replaced.

No network, subprocess, service, clock, collector or cloud response is performed by the library/runner. Models/scalers are ephemeral; no weights, pickle/joblib artifacts, vector databases or real reviewer records are saved. Reports contain synthetic IDs/epochs/count information, not anonymization of real data. Preserve approved private storage for any future genuine study.

Independent labels/grouped held-out real data, approved context/protocol, timing/coverage/identity, calibrated detection/false alarms/misses/delay, overhead/energy and Engine 1 integration remain open. Both optional model prototypes are implemented software; neither is independently evaluated security detection. Passing tests and synthetic scores do not establish production readiness.
