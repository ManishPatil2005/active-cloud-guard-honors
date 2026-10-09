# Preserve every development-evaluation report

QA-003 / M3-004 / R7, 9 October 2026. Fixes report publication in the existing Engine1 development evaluator, not detector algorithms or independent research acceptance.

## Defect, fix and compatibility

Previously `scripts/evaluate.py` always wrote `output/baseline-development.json`, replacing prior evidence after scanning. The corrected script requires `--output FRESH_FILENAME` and opens it exclusively **before reading/scanning inputs**. Existing files are refused without changing their bytes. Omitting the argument exits2 before scanning; a missing output directory is refused rather than implicitly created. `scripts/summarize.py` still reads the historical baseline; it is not redirected automatically to a new run.

The existing45development fixtures, five scanner repeats, exact-rule mismatch checks, binary case metrics/Wilson calculations, timings and limitations remain. Fresh reports retain original fields and add status, manifest raw-byte SHA and four selected source hashes (evaluator/scanner/metrics/verification). Manifest/fixture/source consistency is checked before and after evaluation. A valid mismatch saves full raw findings/timings as `development_regression_failed` and returns1; a schema/IO/checksum/input/source error saves a rejected fresh receipt with error class only. No clean result is fabricated from a failed evaluation. Successful CLI stdout now gives the status; inspect the saved JSON for metrics/raw results.

This is an intentional safer invocation/output contract, not an engine version, architecture change, data replacement or benchmark redesign. Corpus membership/path/label definitions remain trusted repository inputs; checks do not authenticate ground truth, enforce independent splits or attest complete imports/host state. Hash checks are not hostile filesystem-race protection. Existing-file refusal is not an atomic/fsync completion guarantee: interruption/write errors can leave partial new reports. No old report or negative evidence was modified by this change.

## Beginner reproduction

Activate the existing Python environment, open repository root, choose a new filename:

```powershell
python scripts/evaluate.py --output output/my-fresh-development-evaluation.json
python -m pytest -q tests/test_evaluate_output.py
```

Open JSON and check status, metrics.n=45, raw45rows, repetitions5 and rule_set_mismatches empty. Repeating the command with the same filename must return1/output_refused_or_failed while preserving the report. Pick another filename for another run; never delete evidence merely to make a command succeed. Failed/mismatched reports are valid evidence, not files to hide. Five timing repeats are a smoke measurement, not independent samples or proof of generalization.

## Observations and negative evidence

- Initial new test used an empty corpus and passed because median calculation failed before writing; it did **not** reproduce the overwrite. Preserved `output/evaluator-output-before-windows-20261009.xml`,1pass. Test setup corrected, not hidden.
- Corrected valid one-case tests reproduced both five scans before refusal and replaced bytes in isolated temporary test roots: `output/evaluator-output-reproduced-windows-20261009.xml`,2failed/1.06s. Actual historical repository evidence was never used as a destructive test target. INC-067.
- Fix first passed both regressions, then ten expanded cases passed Windows0.35s/Linux1.20s. Cases cover historical bytes/no scans on refusal, fresh success/unchanged metrics/five repeats, saved mismatch, pre-scan checksum rejection, fixture/manifest/source mutation, empty refusal and required argument. Receipts: `output/evaluator-output-fixed-windows-20261009.xml`, `output/evaluator-output-target-{windows,linux}-20261009.xml`.
- Actual fresh45-case evaluations passed on both OS: `output/evaluator-preserved-development-{windows,linux}-20261009.json`. Historical `output/baseline-development.json` SHA before/after both executions: `0df82eca188b274936d2273c7059191f59f739b9d2a677744d421b46f0e5f50f`, unchanged. These remain seeded development regression results, not an independent benchmark.
- Full Windows1,372passed/38existing skips,1,410collected/zero failures/errors,55.43s (55.410s XML), `output/evaluator-output-full-windows-20261009.xml`. Docs18pass/0.33s (0.147s XML), `output/evaluator-output-docs-20261009.xml`; lint/130-file formatting and both pip checks pass. Both fresh45-case reports match historical calculated metrics and id/expected/predicted/sha rows (timings excluded) and bind current raw manifest/four selected source hashes. Exact commands/publication checks WORK_LOG/current MEMORY. Full Linux not rerun for evaluator-only change; relevant tests and actual45-case evaluation run there. No model inference/fitting, probes, sensor/clock/service/cloud operation or deployment performed by the evaluator.

Remaining original research work: genuine approved protocol and independent labels/held-out groups, fair actual ablations, calibration and qualified runtime timing/coverage/overhead. Preserving reports enables trustworthy audit history; it does not establish those results.
