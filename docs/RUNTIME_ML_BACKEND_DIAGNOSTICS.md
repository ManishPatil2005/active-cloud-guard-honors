# Optional runtime-model backend diagnostics

E2-040 / E2-004 / RQ3,7October2026. Diagnostic refinement for the implemented synthetic-only model comparators, not another engine, model version, dependency migration or real-data evaluation. [INC-056](INCIDENTS.md) records an intermittent Windows import failure whose original cause remains **unknown**. This change fixes a separately reproduced error-reporting gap; it does not retroactively explain or fix that event.

## Observed problem and acceptance

Both model adapters previously caught every ImportError and emitted install the optional runtime-ml dependency, suppressing the original cause. A direct import currently succeeds for sklearn.ensemble/neural_network/preprocessing/threadpoolctl, installedscikit-learn1.9.1/pipcheck pass. Installing packages is therefore not a justified remedy for the old failure. Its raw XML retains a generic RuntimeError and source-code lines, not the underlying exception message/name needed for root-cause attribution. A literal search matching ImportError in that XML can match the printed source; it does not recover a chained exception.

Before the change, eight injected faults reproduced missing diagnostic categories (all eight tests failed); after the change, those cases and32total new diagnostic tests pass. These tests inject known exceptions, **not the historical intermittent fault**. Accept: stable safe categories in ordinary exception text and rejected CLI receipts, no raw paths/messages/private module/version names, no retries/fallback/package repair or changed model calculations/authority.

## Error contract

Shared runtime_ml.RuntimeMLBackendError subclasses RuntimeError, so existing RuntimeError catches still apply. A fresh diagnostic property returns code/cause_kind/dependency; CLI helper backend_failure_fields projects only recognized errors. Both fixed model runners add backend_diagnostic to rejected backend receipts and use error_type=RuntimeMLBackendError. Unrelated errors keep their existing class-only handling. Success report fields/calculated values/protocols remain unchanged; selected source digests legitimately change.

| Code | Evidence used | Interpretation, not a claimed root cause |
|---|---|---|
| optional_module_not_found | ModuleNotFoundError.name exactly sklearn or threadpoolctl | Named top-level module lookup failed; not proof reinstalling is necessary or sufficient |
| backend_dependency_not_found | Other ModuleNotFoundError, including nested module or absent name | Backend dependency/submodule lookup failed; only allowlisted root may be published |
| backend_import_failed | Other ImportError | Import failed; not automatically a missing package or proven DLL/resource problem |
| backend_metadata_missing | scikit-learn distribution PackageNotFoundError during pin lookup | Version metadata unavailable; import success alone does not establish pinned environment |
| backend_version_mismatch | Actual metadata does not equal required1.9.1 | Refuse unsupported backend; untrusted observed version string omitted |

Cause-kind vocabulary is limited to ModuleNotFoundError/ImportError/PackageNotFoundError/VersionMismatch. Dependency projection is only sklearn/scikit-learn/threadpoolctl/numpy/scipy/joblib/narwhals/cloudpickle or null. Unknown/private names, paths, messages and subclass names are not exported. Constructor rejects unowned code/cause/dependency values. Returning a copied diagnostic prevents mutation of the returned mapping from changing the original fields. This is not a Python object sandbox or authenticated dependency attestation.

Ordinary exception text includes owned code/cause literals for future traceback diagnosis. Raw exception text/name/path and unexpected metadata values are omitted; import/metadata chaining suppressed with from None. Python can still retain an original exception in in-process __context__; this is serialized-output/traceback redaction, not memory erasure or a promise that trusted code cannot inspect original objects. No pickle/untrusted exception object deserialization is introduced.

## Scope and compatibility

Helpers live in existing runtime_ml.py; autoencoder reuses the import classification/version check. Pinned version unchanged, no install/upgrade/runtime retry or imported-library cache cleanup. No collection/network/service/clock/response, core/default CLI/intake/capture/statistical/Engine1/native23-source closure change. Model features/scaling/fitting/parameters/threshold/abstention/authority boundaries unchanged. Synthetic actual fitting remains truthful when existing regression tests perform it; this helper creates no training/labels/predictions itself.

Existing Isolation Forest saved calculated-result regression and autoencoder backend-equivalence/determinism tests still run. Historical receipt/source bytes remain original; never edit old source digests to match this new revision. New failure receipt error class/additive category field is the deliberate externally visible diagnostic change, not a calibrated threat decision or approved dataset.

## Verification and reproduction

At repository root with existing environment:

```powershell
.venv/Scripts/python.exe -m pytest -q tests/test_runtime_backend_diagnostics.py tests/test_runtime_ml.py tests/test_runtime_autoencoder.py
```

Linux uses its environment's interpreter. New tests inject generic/missing/nested/private/nonstring import names, metadata absent/mismatched values, private exception subclasses and invalid diagnostic construction. In-process runner tests mock compare_synthetic to raise a known typed error and verify both exclusive rejected reports/redaction/no-actions/no overwrite. Those temporary receipts are synthetic fault cases, not native observed backend failures. No actual model fitting in those injected cases; existing model regression cases fit synthetic fixtures only.

Original8failure XML and subsequent105/129/verified129targets/full suites are retained in [EVIDENCE](EVIDENCE.md)/WL-066 [WORK_LOG](WORK_LOG.md); current result facts recorded there. Tests and owned diagnostic categories cannot establish INC-056's original cause, permanent environmental stability, detector accuracy or real-study approval. If a native backend failure recurs, retain its new safe category/selected version/source facts, stop that execution and diagnose within its authorization; do not silently retry or install packages to obtain success.
