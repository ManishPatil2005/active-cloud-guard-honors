# Active Cloud Guard: Engine 2 evaluation proposal

Version 0.1 — prepared 6 October 2026. **DRAFT — NOT APPROVED.** The user explicitly reported that supervisor approval has not yet been obtained and requested a properly prepared file. This document proposes the next study; it is not a supervisor decision, operational authorization, preregistration, executed experiment or publication-ready result. Actual decisions/identities/signatures must be recorded privately, not fabricated or committed here.

## 1. Research purpose and present status

Research question RQ3: what additional value and overhead does runtime evidence provide for cloud-hosted open-source security review? Engine 1's engineering baseline is frozen at engine1-v2.2; Engine 2's observation-only statistical replay and optional synthetic Isolation Forest/reconstruction-autoencoder implementations exist. Python/CLI, Docker Compose, Ollama and Chroma remain unchanged. No third engine or new framework is proposed.

Latest whole-suite software checkpoint: Linux1,148passed; Windows1,110passed/38skips, zero failures/errors. These are engineering tests, not attacks, independent samples or accuracy. The [data audit](RUNTIME_DATA_READINESS_AUDIT.md) identifies five synthetic and two sensor-development captures, a reused-event pair and unresolved historical timing/coverage. None is established as an independent benchmark. Current ML runners accept synthetic fixtures only; a real-data evaluation path, threshold/calibration and approved-data enforcement are future software work after human/protocol decisions. This proposal does not bypass those restrictions by relabeling real data.

## 2. Decision that must come first: what is a positive label?

Proposed narrow endpoint: **independent evidence warrants security investigation within the approved lab scope**, not confirmed attack/compromise. Supervisor must approve/revise/reject this endpoint and its relationship to the original research claim. Existing three event-kind counts omit destinations, paths, executable identity and authorization intent; they cannot by themselves justify broad attack labels. A legitimate high-activity scenario must not be called suspicious just because a model assigns a high score.

If the supervisor requires confirmed attack detection, stop this proposed narrow study and revise context/telemetry/scenario design and safety review before implementation; do not quietly rename count-change detection as attack detection. [Draft reviewer rubric](RUNTIME_LABELING_GUIDELINES.md) proposes benign/suspicious/unknown with evidence reasons; it remains unapproved. No seed label or model prediction is independent ground truth.

Required independent context: approved task/authorization records, intended policy, scope-bound scenario evidence and identity/time mapping, sourced separately from detector output. Document what each evidence item can and cannot establish. If those facts cannot support a label, retain unknown. Richer context must be minimized, hash-bound and reviewed; no new collector fields/schema are silently added by this proposal.

## 3. Proposed study boundary and controls

- Local, owner-authorized existing Compose lab only; initial Redis workload scope, with other OSS services excluded unless separately reviewed. No production/public endpoints, destructive payloads, data theft, automatic isolation, credential attacks or clock/service intervention implied.
- Use non-destructive routine and policy-review scenarios whose security relevance is established by independent approved context, not just unusual volume. Include routine high-activity cases to challenge the shortcut “more events means suspicious.” Scenario details/commands and ownership require separate scope review before execution.
- Collector acquisition/normalization and model scoring remain separate. Preserve pinned source/image/environment versions, bounded startup/shutdown, target identity before/after, canary readiness, accounting/rejections/drops and all planned/launched/failed/missing slots.
- Existing unresolved collector/harness alignment blocks timing-dependent evaluation. Prior within_tolerance=true at local endpoints does not establish collector-event alignment. No fitted offset correction or retrospective repair of the failed third repeat.
- No fixed runtime sample count is claimed sufficient here. A number of windows from one run is not that number of independent replications. Supervisor/statistical review must choose families/runs/calibration/test allocation and uncertainty/power rationale before evaluation; record rationale rather than invent a power calculation.

## 4. Proposed execution sequence and stop gates

| Stage | Work and acceptance | Stop / unresolved boundary |
|---|---|---|
| A: actual review | Approve label target/context/rubric, scope, units/grouping/sample/analysis/exclusion/privacy and responsible people; freeze document versions/hashes | All remain pending now; blank signatures/hashes are not approval |
| B: acquisition qualification | Separately reviewed bounded pilot demonstrates required target mapping, canary/coverage/accounting, collector-to-command timing and safe cleanup under selected conditions | No new pilot launched here; if identity/time/coverage is unknown or fails, retain failure and stop benchmark collection |
| C: independent data collection | Freeze authorized scenario families/order/repeats/hardware/software; record every planned slot and capture/context/receipt hash | Do not replace failed slots until a separately declared new version; do not pool old tuned exploratory data as held-out evidence |
| D: blind annotation | Neutral evidence packets, approved context and quality ledger, two real independent reviewers, immutable original votes/reasons then separate adjudication | No scores/seed key/other vote exposure; unknown and disagreements preserved; humans cannot be generated |
| E: protocol/software freeze | Freeze group-held-out partitions/features/hyperparameters/calibration/metrics; implement separately reviewed eligible-real-data evaluation path without weakening synthetic-only wrappers | Current library/intake grants no real-data fitting; this future path must be specified/tested before any actual fitting |
| F: comparison | Train/calibrate on approved training/development partitions only; test all three methods on the same untouched grouped units with complete score/abstention denominators | No tuning/fitting/scaling/threshold choice on test observations or labels; no raw-score magnitude ranking |
| G: extension/publication | Evaluate Engine1/runtime evidence integration and overhead under reviewed matched conditions; report reproducible results/negatives/limits | No integrated runtime TCI/energy/general-cloud claim unless separately measured and supported |

Every candidate must be reviewed against [G01..G16](RUNTIME_CAPTURE_ELIGIBILITY.md). A “not applicable” judgment needs written claim-specific supervisor rationale, not a shortcut around unfavorable evidence. Study approval and operational consent are separate. Any future time-service change requires its own explicitly authorized safe protocol; this proposal does not authorize it.

## 5. Units, grouping and leakage prevention

Proposed starting convention: nonempty per-asset60-second windows using current event_count/process_start/network_connect/file_open feature order. This is a proposal, not approval. Window/precision/mixed-window rules must be frozen before collection/labels; missing/empty intervals stay in a separate ledger, not fabricated benign/zero windows. Current timestamp parser's microsecond/floating-point limits must be disclosed where relevant to alignment. Aggregate count redundancy is a limitation, not proof of useful security features.

Group related scenario/template/deployment/run families together before splitting. Do not split one run's windows or minor variants across train/validation/test as independent observations. Audit exact byte/event overlap plus semantic/prior-use relationships. Both existing sensor captures belong to redis-ping-development; two different synthetic fixtures share two exact projections. Existing development files cannot become untouched test data through renaming.

The minimum eight baseline windows/two distinct feature rows in optional model code are engineering fit guards, **not sample sufficiency**. Reject/abstain when baseline guards or quality requirements fail. A future dataset must have reviewed family/run counts and class/context coverage; no balance or significance is asserted now.

## 6. Comparison methods and calibration

Compare the unchanged statistical count-deviation baseline, pinned scikit-learn Isolation Forest and baseline-scaled undercomplete reconstruction MLP. Existing prototype parameters are engineering defaults, not selected optimal research settings. List all allowed choices/search budget and freeze selection procedure before evaluation. StandardScaler/model fitting is training-only; no observation-driven normalization. MSE and IF scores have different scales, neither is an attack probability.

Current optional outputs have binary_prediction=null. A future reviewed calibration/decision layer must define a threshold on a training/validation partition only, preserving all abstentions. A prespecified operating point and paired comparison at matched conditions are required; do not pick a test threshold to achieve the deck's desired metric. Record optimizer warnings/nonfinite failures/training attempts; failure does not become a clean verdict. Do not interpret synthetic numerical reconstruction as real detection validation.

## 7. Proposed reporting and statistical analysis

7October software follow-up: [synthetic-only decision accounting](SYNTHETIC_RUNTIME_ACCOUNTING.md) now implements arithmetic/denominator tests on invented supplied decisions, not real model thresholds, human labels or approval of the estimands below. Optional models still have null binary_prediction. This does not make the proposal approved or permit real fitting/evaluation.

Primary runtime outcome and operating point require actual approval. Suggested reporting, not an executed analysis:

- Provide TP/FP/TN/FN on explicitly known, eligible, scored units; precision=TP/(TP+FP), recall=TP/(TP+FN), with undefined denominators reported as undefined. State these are conditional-on-scoring quantities, not performance over every planned unit.
- Separately report all eligible known positives, positives that abstained, negatives that abstained, unknown labels, missing/unusable windows and failed runs. Report fraction of all eligible known positives detected; abstentions cannot disappear from that denominator. Preserve exclusion reasons and effects on claims.
- Use paired method differences on the same groups; supervisor/statistical review must prespecify family/run-level resampling/uncertainty and number of genuinely independent groups. Do not treat correlated windows as independent evidence or claim a confidence interval from invented samples.
- Report agreement/disagreement/unknowns before adjudication. Existing intake known-agreement fraction is not kappa or human-independence proof; any additional reliability statistic requires reviewed definitions/implementation.
- Detection delay needs approved event onset/context mapping and reliable aligned clocks. Without it, report delay not estimable, not zero or inferred from a window number.
- For acquisition overhead, separate matched collector-off/on conditions and valid timing/resource measurements; for model costs, separate acquisition, preprocessing, training and inference. Record CPU/memory and end-to-end latency under declared hardware/load. Power/energy savings require actual suitable measurements; CPU percentage alone is not energy/sustainability evidence.
- Report all model/training warning rates and abstention mechanisms. Do not use synthetic test-suite duration as detector latency, collector overhead or a cross-OS performance benchmark.

## 8. Privacy, integrity and reproducibility

Actual approval/reviewer identity/consent/conflicts/exposure logs/seed keys/original submissions belong in private/runtime-labeling/ or approved access-controlled storage, not the public proposal. Git ignore/publication exclusion is not encryption or consent. Neutral IDs require private reversible mapping and a leakage audit; never claim complete anonymity from renaming.

Freeze and hash approved protocol/rubric/context/capture/receipt/software/environment versions. Keep originals and negative experiments; corrections create new versions with reasons. Publication contains only reviewed minimized data and applicable rights/permissions. Capture hashes are integrity, not signatures or authenticated provenance. Never load supplied serialized model artifacts or commit credentials, environments, weights/vector databases or raw private logs.

## 9. Pending supervisor decisions and handoff

All responses below are **pending**, not filled by an AI or the owner on behalf of a supervisor.

| Decision | Requested response |
|---|---|
| Target/claims | Approve/revise review-necessity endpoint, or require a different supported attack/context design |
| Scope/context | Define authorized scenarios, independent evidence, services and prohibited actions |
| Unit/group/sample | Choose window/precision/mixed rules, families/runs/splits, sample/uncertainty rationale |
| Qualification | Define necessary readiness/coverage/identity/alignment evidence and stop criteria |
| Humans | Assign two actual reviewers/adjudicator, consent/conflicts/blinding and private custody |
| Calibration/analysis | Freeze primary outcome/operating point/threshold selection/paired uncertainty and abstention/exclusion rules |
| Safety/privacy | Separate operational permissions, recovery/privacy/retention/publication conditions |

Share this file with the supervisor yourself. Record genuine responses using the [unfilled review sheet](templates/runtime-supervisor-review.md) in private approved storage; do not commit names/signatures without reviewed consent. No message has been sent automatically. Revision0.2 may incorporate actual decisions with provenance and change rationale; merely removing “draft” is not approval.

**Next actionable handoff:** obtain those decisions, then revise and freeze the qualification/collection protocol before new live evaluation. Offline documentation/guard validation can proceed now; accepting real research data, independent labels or a validated detector cannot be manufactured by continuing code generation.
