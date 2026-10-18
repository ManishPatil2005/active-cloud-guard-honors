# Preserve every development-evaluation report

## QA-038 — exact case/rule accounting, 12 October 2026

RQ1/RQ2/RES-002 require meaningful precision/recall accounting. The original
binary case metrics answer only whether a file has any finding. A wrong rule
can count as a binary true positive, although the existing mismatch guard
correctly fails that report. Also, duplicate manifest case IDs previously
collapsed in metric dictionaries while both rows were scanned. Two preserved
before-fix regressions reproduce missing exact accounting and duplicate admission.

`cloudguard.metrics.rule_metrics` now computes exact **(case_id, rule_id)**
micro TP/FP/FN, precision/recall/F1, expected/predicted counts, exact case matches
and sorted per-rule counts. Wrong rules produce both FP and FN; the same rule
in the wrong case cannot match. Empty denominators return null. No declared
negative-rule universe exists, so TN and false-positive rate stay null. No
Wilson interval or independence assumption is attached to the new counts.

Inputs require matching nonempty case inventories, unique nonblank string rule
lists, at most10000cases/1000rules per case,1024character case IDs and256character
rule IDs. Evaluator manifests reject duplicate IDs and malformed labels before
the first scan. Expected order is irrelevant; original label order is retained
in raw rows. Repeated predicted occurrences at different locations still count
once per case/rule: this is **not full asset/location finding-level evaluation**.

The fresh report adds `rule_metrics`; historical `metrics` and output refusal,
source/input hashes, five-repeat scanning and negative-evidence behavior remain.
No scanner, model, scoring, fixture, threshold, runtime or architecture change.
Independent actionability labels and location-aware matching remain necessary
for the final paper's primary endpoint. This closes a development-accounting
gap, not the entire independent evaluation milestone.

Final Windows/Linux selected tests:104passed each (48new cases in this change).
Actual fresh45fixture runs on both hosts agree:26expected/predicted case-rule
instances,26TP/0FP/0FN,45exact cases. These are deliberately seeded development
fixtures, **not 100% real-world accuracy or established novelty**. Historical
binary metrics match, and original baseline SHA remains
`0df82eca188b274936d2273c7059191f59f739b9d2a677744d421b46f0e5f50f`.

Receipts: `output/rule-accounting-before-20261012-qa038.xml` (2failures),
`output/rule-accounting-final-{windows,linux}-20261012-qa038.xml`, and
`output/rule-accounting-development-{windows,linux}-20261012-qa038.json`.
Intermediate48-pass receipts are retained separately. Commands and limitations:
WL-116 in [WORK_LOG](WORK_LOG.md); INC-093 and ADR-090.

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
