# Experimental protocol v0.1

6October runtime follow-up: [current boundaries](CURRENT_STATUS.md), [staged grouped data-label plan](RUNTIME_EVALUATION_PLAN.md) and [implemented consistency subset](RUNTIME_INTAKE.md). Checks hashes/schema/group/split/observed windows/reviews/adjudication; receipts opaque and all eligibility/fitting flags false. No new real data/actual independent reviewers/models/evaluation. Next typed receipt-to-run/capture/protocol checks and genuine human/data gates; historical failed timing remains ineligible for performance claims unless separately resolved, never retroactively repaired.

## Questions and endpoints

RQ1: Does adding retrieved security context to a local LLM improve finding-level precision/recall relative to the same model without retrieval? RQ2: Does adding scoped verification improve prioritization while preserving recall? RQ3 (later): What additional value and overhead does runtime evidence provide?

Primary endpoint: paired difference in precision at a fixed minimum recall on independently labeled findings. Secondary endpoints: F1, raw TP/FP/FN, false-positive count reduction, abstention rate, p50/p95 latency, memory and CPU. Do not equate false-positive count reduction with false-positive rate reduction.

The PDF's numeric targets are hypotheses. The primary pass/fail criterion for this engineering milestone is repeatable behavior and faithful evidence, not reaching a target by altering labels or excluding difficult cases.

## Units and labels

Static finding identity: scenario + asset + vulnerability type + configuration location. Exposure identity adds protocol, destination, vantage, observation time and intended access policy. Runtime unit later: non-overlapping labeled run/window; overlapping windows from the same run must remain together.

For static cases record separately: `configuration_predicate`, `policy_violation`, `intended_audience`, `reachable_from_vantage`, `authentication_required`, `actionable`, `reviewer`, `adjudication_reason`. Existing fixtures label configuration predicates only; they do not establish full vulnerability or actionability labels.

Two human reviewers should independently annotate the future evaluation set without seeing system predictions. Resolve disagreements explicitly and preserve original labels. Compute agreement before adjudication. A generated label is a seed specification, not independent reviewer evidence.

## Data separation and leakage control

The 45 supplied files are development/regression cases. Do not relabel them as held-out test cases. Future target: at least 120 independently adjudicated scenarios balanced across applications and positive/negative/context-dependent cases; increase sample size if confidence intervals are too broad. This is a planning target, not a statistical power claim.

Group all variants of one base template, application deployment and attack run before splitting. Keep an untouched test partition; do not tune prompts, rules, retrieval, weights or thresholds using it. Freeze source hashes and dates, model digest, prompt hash, dependency versions and random seed. Record public repository commit hashes and licenses. Deduplicate exact and structurally similar templates before splitting. Avoid putting evaluation solutions or finding labels in the retrieval corpus.

## Comparisons

A: versioned established scanner on supported files (e.g. Checkov), with rule coverage recorded. B: this small explicit rule baseline. C: local LLM without retrieved context. D: identical local LLM with retrieval. E: D plus independently validated evidence. F: full runtime system in Months 5-7. B is a transparent implementation baseline, not a stand-in for an established state-of-the-art scanner.

Give comparisons identical files and threat scope. Match findings by canonical identity; have a blinded adjudicator resolve semantic matches. Never derive LLM ground truth from the custom scanner. Report malformed output, unsupported file types and timeouts as failures/abstentions; do not silently remove them from evaluation denominators. Include coverage and worst-case treatment of abstentions alongside covered-case metrics.

## Measurement

Precision=TP/(TP+FP); recall=TP/(TP+FN); F1=2TP/(2TP+FP+FN). Undefined denominators are null, not zero or perfect. FP reduction=(FP_baseline-FP_variant)/FP_baseline, undefined when baseline FP=0. Preserve negative reductions. Report recalls and FN changes alongside FP reduction.

Use paired bootstrap confidence intervals resampling scenario families for system differences; Wilson intervals are descriptive for simple independent proportions and do not solve template correlation. Use at least 1,000 bootstrap draws with a recorded seed once independent data exist. Current scripts provide Wilson intervals on development cases only; these are not population claims.

Separate cold model load, warm inference, retrieval, parsing and probe timing. Record hardware, OS, model quantization, input/output token counts, service image digests and concurrency. Five local scanner repeats are a timing smoke check, not five independent samples. Probe failure time belongs in latency statistics. Runtime overhead later requires matched baseline and instrumented workloads, identical load, repeated runs and stable sampling intervals.

## Gates and negative results

Gate 1: regression and schema tests pass. Gate 2: all four local services observed, with configuration and image identities recorded. Gate 3: actual model outputs saved with sources and timings, including invalid/unsupported outputs. Gate 4: independent labels and untouched test evaluation. Only Gate 4 supports research effectiveness claims.

Do not claim production safety, novelty, 90% improvement, .92 F1, .95 runtime AUC or <5% overhead from this development corpus. Failure to meet a hypothesis is a valid research result and should guide the discussion rather than be hidden.
