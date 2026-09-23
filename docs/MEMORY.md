# Current project state

Updated 2026-09-23. This file describes the current state; history belongs in WORK_LOG, INCIDENTS, DECISIONS and Git.

## Implemented and observed

Python CLI/library with nine rule predicates, lexical and Chroma retrieval, local Ollama auditing, explicit TCP probes, provisional scoring and integration. Four target services plus Ollama were running at the last live observation. The 45-case development corpus matched expected rule sets. The previous implementation run passed 84 tests, lint and dependency checks. Saved evidence records four TCP accepts, two HTTP 200 responses, three semantic source checks and Trivy scans of 11 compatible fixtures.

Current smoke model: qwen2.5:3b. Latest saved three-case inference times are approximately 12.44, 12.30 and 12.83 seconds. Two supported candidates were retained; one unsupported password-placeholder/trust claim was rejected by a narrow guard. These are tuned development examples, not an accuracy benchmark.

## Current work

Strict documentation and private GitHub publication are complete. Remote: https://github.com/ManishPatil2005/active-cloud-guard-honors, visibility PRIVATE, default branch main. Initial publication was verified through both GitHub API and git ls-remote, matching the local commit; see WORK_LOG. Git history identifies subsequent documentation receipt commits. Preserve the existing architecture, setup and tech stack.

The documentation/publication checker adds three software tests. The refreshed local suite passes **87 tests**, with Ruff format/lint and dependency checks passing. The original 84-test report is preserved as output/test-results-initial-84.xml. Model and service experiments were not rerun for this documentation-only/application-unchanged publication task. A repository-local pre-commit hook runs the bounded publication check; this is not hosted CI.

## Known limitations

Model hallucinations remain possible; two guarded predicates do not cover all findings. The 3.5-second inference target is missed. There is no independently labeled held-out effectiveness study, calibrated TCI, general IaC evaluator, auth-aware probe or runtime engine. Some reference full texts were inaccessible. The bridge is not egress-isolated. Historical image versions are for reproduction, not production recommendations.

## Next scientific gate

Independent labels and grouped held-out data, followed by matched baseline/LLM/RAG/probe comparisons with abstentions, false negatives and uncertainty reported. Do not turn existing development cases into a purported untouched test set.

## Operational notes

Use the existing project `.venv` and README commands. Local credentials remain under ignored `testbed/secrets/`; generate them on a fresh clone. Rebuild the ignored vector index locally. Container recreation loses PostgreSQL/MinIO lab data; the model volume persists. Do not infer current uptime from this file: verify live state when it matters.
