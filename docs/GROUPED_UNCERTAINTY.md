# Paired scenario-family uncertainty: software preparation

QA-034 / RES-002 / E2-004 / RQ3 / WL-111, 11 October 2026.

## Why this is necessary

The experimental protocol requires paired bootstrap intervals over scenario
families. Repeated windows from the same scenario are correlated; treating every
window as an independent experimental unit would overstate the evidence.
This implementation closes an analysis-software gap. It does not produce an
independent benchmark, human labels, model predictions or novelty results.

## Implementation and scope

`cloudguard/runtime_uncertainty.py:grouped_synthetic` consumes the unchanged
synthetic paired-accounting document plus an exact unit-to-family mapping.
Both systems must contain the same units, runs, labels and availability states.
Every declared run belongs to exactly one family. Multiple runs may share one
family; manual template/deployment/semantic grouping remains necessary.

The existing 2,000-unit limit applies. At most 100 families, 1,000–10,000 draws
and a true integer seed in [0, 2^32) are allowed. Fewer than two families produces
no interval or draws; two families is only an arithmetic prerequisite, not an
adequate sample-size claim. The fixed example uses four invented families and
32 invented units, not the proposed independent study.

For each draw, sample G family indices with replacement from the G families.
The same multiplicity applies to both systems. Keep every unit of each selected
family, including missing/unusable/unknown/abstained entries. Aggregate integer
counts before computing ratios: the estimand is the variant-minus-baseline
difference in pooled, unit-weighted metrics, not a mean of family metrics.
Large families therefore contribute more units when selected; this choice must
be reviewed for the actual study rather than silently treated as equal-family
weighting. Original paired reports and all denominators remain intact.

Report precision, recall, false-positive rate, F1, inclusive known-positive
detection/known-negative flag fractions, and known/observed decision coverage.
For each metric retain the original estimate and counts of defined/undefined
draws. If the original ratio or ANY draw is undefined, withhold its interval.
Never drop/redraw difficult samples, impute zero or call abstention a clean result.
Negative differences and degenerate distributions remain visible.

This first implementation uses two-sided nominal 95% percentile intervals,
linear quantiles at (n-1)*p and Python's local seeded MT19937 generator. The
default is 2,000 draws; global random state is untouched. Stable sorted family
and unit order makes numerical results independent of input record ordering.
Record source/runtime/seed when reproducing; future runtime changes need rechecking.

The [SciPy bootstrap documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html)
describes paired resampling with shared indices and percentile intervals, while
noting alternatives such as basic and BCa methods. Our implementation applies
shared indices to whole declared families, not individual windows. It uses no
new dependency. Percentile is a transparent exploratory preparation choice,
not proof of nominal coverage or superiority to BCa; final method, group size,
sample adequacy and operating-point selection still require study review.
There is no p-value, significance verdict or multiple-comparison adjustment.

## Reproduce without collecting data

From the repository root, use the qualified Python interpreter and a fresh path:

```text
python scripts/runtime_uncertainty_check.py --output output/grouped-check-NEW.json
python -m pytest -q tests/test_runtime_uncertainty.py tests/test_runtime_accounting.py tests/test_runtime_paired_accounting.py
```

The CLI has no arbitrary input or model argument. It evaluates only the versioned
`data/runtime/grouped-uncertainty-synthetic.json`, reserves output before reading,
checks input/selected implementation hashes before and after, and preserves a
safe rejection receipt on failure. Existing output is refused. It neither starts
services nor collects telemetry, changes clocks, fits models or generates votes.
Hashes/origin flags are consistency declarations, not authenticated provenance.

Tests compare every label/decision cell and mixed counts against existing
accounting; a separate row-expansion oracle enumerates all four paired draws
for two unequal-size families. Other tests cover exact pairing, reproducibility,
reversed signs, unknowns, undefined draws, small groups, strict budgets, run
splitting, nonmutation, no global RNG change and exclusive evidence output.

Actual Windows/Linux targeted suites: 140 passed each, including 46 new cases.
Both fixed demonstrations pass five checks and their full numerical results
match exactly; these invented numerical differences must not be quoted as
Engine 1/Engine 2 performance. Full-suite/package verification is recorded in
WORK_LOG and EVIDENCE after execution.

## Still required for publication

Qualified captures, independently justified scenario groups, two actual reviewers
(or an approved protocol revision), eligible train/validation/test data, frozen
real-data fitting and calibration, fair component comparisons and the paper.
The existing synthetic-only wrappers are unchanged. This helper is not a route
around the acquisition/independence gates and does not establish a fixed-recall
operating point, TCI calibration, detection delay, overhead or energy results.
