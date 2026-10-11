# Runtime study execution plan - proposed version0.1

QA-025/E2-004/RQ3/WL-102,11October2026. Owner requested a plan and implementation after [reported supervisor approval](SUPERVISOR_APPROVAL_RECORD.md). The broad investigation-necessity endpoint is approved by report; the new numeric schedule below is **proposed**, not attributed to the supervisor. No collection, labels, fitting or production deployment executed by this plan.

## Proposed scope and sample structure

Keep Python/Compose/Ollama/Chroma and the two engines. Initial owner-controlled Redis lab, internal Linux analyst tool and research demonstration only. Investigate incremental runtime-evidence value, not confirmed attacks. No public service, exploitation, destructive workload, clock/policy intervention or automatic remediation.

Proposed feasibility schedule:12distinct scenario-family placeholders,3runs each=36planned slots;6families/18slots train,3families/9slots validation,3families/9slots test. Fixed seed20261011orders slots before results. The three test families are a small exploratory set, not proof of adequate power or population coverage; three repeats from one family are correlated, not three independent families. A statistician/supervisor must accept or revise the size/analysis rationale before confirmatory use. Changes create a new plan version; never replace failed slots to improve results.

Family IDs are placeholders, not defined scenarios, independent evidence or preassigned security labels. Define genuinely distinct task/policy/context families privately, including ordinary high-activity cases and independently justified review-necessity cases. Every exact command, loopback asset, workload duration/rate, context sufficiency and safety/cleanup condition needs scope review before execution. Do not infer suspiciousness from event volume. Semantic family/prior-use audit is manual; grouped IDs alone do not prove independence.

Use60second nonempty observed windows in existing feature order. No synthetic zero/benign windows for missing intervals. Training needs adequate reviewed benign baseline support (existing8window/two-row guard is engineering-only); do not use validation/test data to meet training minima. Duration/sample sufficiency must be defined from the chosen observable scenarios and qualification pilot, not guessed from slot count.

## Sequence and stop conditions

1. Freeze exact scenario/context/rubric/analysis definitions and actual reviewers. Keep names/consent privately; no generated humans or labels. Withhold split map, scores and seed truth from reviewer packets.
2. Qualify identity, canary readiness, expected/observed coverage, raw accounting and collector-command timing using a separately reviewed bounded pilot. Local clock passes are insufficient. Failed/unknown qualification stops benchmark collection; no timestamp fitting/correction.
3. Collect the frozen schedule only after operational review. Preserve every attempted/unlaunched/failed/rejected slot and original receipts. A failed launch differs from a launched collection failure. No adaptive replacements.
4. Two independent reviewers label neutral eligible observed units using independent policy/task context; retain unknowns/original votes before separate adjudication. Existing development/synthetic data cannot become held-out by renaming.
5. Freeze real-data evaluation path/features/allowed tuning budget. Statistical baseline, IF and AE compare identical approved grouped units; scaler/model training on training only, threshold/operating-point selection on validation only, test once after freeze. Existing synthetic-only wrappers remain unchanged; this planner does not authorize fitting.
6. Report full planned/eligible/scored/unknown/abstained/excluded denominators, FP/FN/precision/recall and paired grouped uncertainty. With few test families, report limitations rather than unjustified significance. Detection delay only with aligned onset evidence. Separate acquisition and model CPU/memory/latency; energy requires actual power measurements.
7. Demo is observation-only with visible abstentions and scope limits. Production acceptance separately requires security/recovery/rollback and a supported runtime; Windows ML policy/hosted lifecycle and Chroma risks remain unresolved.

## Implemented now

QA-026 adds [offline scenario preflight](../scripts/runtime_scenario_preflight.py), not a new collector or study launch. [Actual receipt](../output/runtime-scenario-preflight-20261011-qa026.json) records existing ping_1/ping_4 schedules, exact PING argv inside the identity-checked Redis container, host inventory127.0.0.1:16379,4second measurements and2fixed-warmup PINGs. These are one previously used development family, not12independent scenarios;4seconds is not observed coverage of a60second study window. No padding missing time with zero events or renaming repeats into independent families. The preflight validates declared inventory/profile/plan scope and preserves eight selected local hashes; Compose bytes alone are not live/semantic deployment verification. Execution readiness remains false regardless of a successful offline CLI exit. No workloads/sensors/services/models/network launched; no labels created.

Reproduce with a fresh output: `tmp/dependency-candidate-windows-20261009/Scripts/python.exe scripts/runtime_scenario_preflight.py --output output/my-scenario-preflight-NEW.json`. Selected25newcases plus23planner cases pass on both Windows/Linux. This qualification catalogue intentionally does not fabricate the missing security scenario families. Next implement a reviewed full-window collection protocol and actual task/policy context definitions, then separately qualify live collector identity/timing/coverage before collection. Reviewer assignments/sample rationale/independent review remain human prerequisites; owner-reported broad approval is unchanged. Exact verification in WL-103.

[runtime_study_plan.py](../scripts/runtime_study_plan.py) generates the fixed proposed schedule after checking the exact approved-by-report proposal hash. Exclusive evidence publishing refuses an existing destination before plan activity. All36slots start not_launched with no receipt; collection/fitting/independent evaluation flags false. `validate_plan` checks fixed order/unique identity/group-held-out partition/counts, exact repeat types, supported negative/pending states and receipt-hash syntax for attempts. It preserves all36slots in the denominator. It does not open/hash-verify actual receipts, authenticate outcomes, prove scenario independence or grant eligibility. No external command/network/sensor/model call exists in this planner.

Repeat from repository root with the qualified interpreter and a **fresh filename**:

```powershell
tmp/dependency-candidate-windows-20261009/Scripts/python.exe scripts/runtime_study_plan.py --output output/my-study-plan-NEW.json
tmp/dependency-candidate-windows-20261009/Scripts/python.exe -m pytest -q tests/test_runtime_study_plan.py tests/test_repeat_readiness.py
```

Actually generated [proposed coordinator schedule](../output/runtime-study-schedule-proposed-20261011.json); it is not a blinded reviewer packet.23newcases/42targeted passes; full verification in WORK_LOG. Do not distribute the schedule/splits to blinded reviewers. Future execution records must remain exclusive/versioned; syntactically valid hashes/statuses are supplied declarations, not measured proof.
