# Current project state

Updated 2026-09-25. This file describes the current state; history belongs in WORK_LOG, INCIDENTS, DECISIONS and Git.

## Implemented and observed

Python CLI/library with nine rule predicates, lexical and Chroma retrieval, local Ollama auditing, explicit TCP probes, provisional scoring and integration. Four target services plus Ollama were running at the last live observation. The 45-case development corpus matched expected rule sets. The previous implementation run passed 84 tests, lint and dependency checks. Saved evidence records four TCP accepts, two HTTP 200 responses, three semantic source checks and Trivy scans of 11 compatible fixtures.

Current smoke model: qwen2.5:3b. Latest saved three-case inference times are approximately 12.44, 12.30 and 12.83 seconds. Two supported candidates were retained; one unsupported password-placeholder/trust claim was rejected by a narrow guard. These are tuned development examples, not an accuracy benchmark.

## Current work

Engine 1 baseline is frozen and published at `6736a577f1ba08b4700daf8a86370ec3bbd1c019`, tag `engine1-v2.2`; both remote references were verified on 25 September. Engine 2 now has an initial observation-only replay implementation (engine 0.1, package 0.5.0): normalized capture/asset validation, time-window counts, separate-baseline statistical comparison, explicit missing-data/insufficient-baseline states, no actions. Full suite: 196 tests passed; four synthetic replay checks passed. No sensor is connected and no ML threat model or real runtime accuracy/overhead result exists. ENGINE2_FOUNDATION.md explains the contract and next Linux/sensor steps. Earlier version snapshots below are historical.

Engine 1 v2.2 / package 0.4.0 adds actual-Compose local Docker identity checks and credential-free Redis/PostgreSQL observations. 168 software tests passed. Real lab: identities stable before/after, Redis protected-mode denial, PostgreSQL SASL challenge; reports in output/service-identity-v22*. No settings or data modified. This establishes selected local identity/protocol evidence, not full application-state equivalence. Freeze this baseline before an observation-only Engine 2. See ENGINE1_BASELINE.md; older refinement entries below are historical.

Latest refinement is Engine 1 v2.1 / package 0.3.0: strict inventory validation, exact-byte policy binding, digest/request/candidate-bound operator approvals, conservative policy judgments and reviewed model TCP evidence. Saved suite: 136 passing tests. Real loopback/synthetic-policy smoke passed five checks; no live model or human-reviewed deployment evaluation was performed. See ENGINE1_REFINEMENT.md and output/verification-v21-*. Model candidates remain unscored/review-required; deployment equivalence is explicitly not verified. Historical v2 efficiency observations below were not rerun for this change.

The README now serves as a formal research entry point: abstract, questions, architecture, evidence-linked results, reproduction, safety and roadmap. This documentation-only revision changes no implementation or measurements. Linux/macOS setup guidance is explicitly unvalidated; old fixed-output experiment scripts are excluded from the first-run sequence to protect saved evidence.

Engine 1 v2 efficiency implementation (package 0.2.0) is now implemented and live-smoke-observed: opt-in exact-request caching, index reuse, generation ceilings/socket timeout and stage timing. The suite passes 106 tests. See ENGINE1_V2.md and output/v2-efficiency-smoke.json. First uncached pipeline: 17.424 s; warm cache miss: 5.256 s; hits: 0.084/0.072 s with fresh TCP observations. Index rebuild/reuse: 5.804/0.084 s, nine/zero embedded documents. These are one-fixture repeat-work observations, not an independent speed/accuracy/energy benchmark. Uncached latency and general hallucination research remain open. Git history identifies the v2 snapshot; verify the remote commit rather than inferring publication from this file.

Strict documentation and private GitHub publication are complete. Remote: https://github.com/ManishPatil2005/active-cloud-guard-honors, visibility PRIVATE, default branch main. Initial publication was verified through both GitHub API and git ls-remote, matching the local commit; see WORK_LOG. Git history identifies subsequent documentation receipt commits. Preserve the existing architecture, setup and tech stack.

The earlier documentation/publication task passed 87 tests; that report and the original output/test-results-initial-84.xml remain preserved. Its model/service evidence was not rerun at publication. V2 now has separate software/live reports; do not interpret output/RESEARCH_STATUS.md as a v2 summary. A repository-local pre-commit hook runs the bounded publication check; this is not hosted CI.

## Known limitations

Model hallucinations remain possible; two guarded predicates do not cover all findings. The 3.5-second inference target is missed. There is no independently labeled held-out effectiveness study, calibrated TCI or general IaC evaluator. Authentication-boundary checks are limited to the documented Redis/PostgreSQL exchanges. Some reference full texts were inaccessible. The bridge is not egress-isolated. Historical image versions are for reproduction, not production recommendations.

## Next scientific gate

Independent labels and grouped held-out data, followed by matched baseline/LLM/RAG/probe comparisons with abstentions, false negatives and uncertainty reported. Do not turn existing development cases into a purported untouched test set.

## Operational notes

Use the existing project `.venv` and README commands. Local credentials remain under ignored `testbed/secrets/`; generate them on a fresh clone. Rebuild the ignored vector index locally. Container recreation loses PostgreSQL/MinIO lab data; the model volume persists. Do not infer current uptime from this file: verify live state when it matters.
