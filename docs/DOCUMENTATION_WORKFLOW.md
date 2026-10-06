# Documentation maintenance contract

The user explicitly requested strict ongoing documentation. This contract applies whenever project work occurs; it is not a promise of unattended background monitoring.

Current status source: CURRENT_STATUS.md, linked first from INDEX/MEMORY/README. Maintain it whenever capability, priority or evidence changes; keep implementation snapshots visibly historical. Each status update must distinguish implemented baseline/refinement/open capabilities/scientific gates. Any supporting helper must map to an original task/research requirement and a specific dependency; no generic continued safety work or whole-engine completion claim from test counts. The task ledger controls planned versus implemented; code/artifacts still determine facts.

## Per-change loop

1. Read the index, current state, rules, task ledger and relevant architecture/protocol sections.
2. Identify task ID, scope, expected behavior and acceptance criteria before modifying code.
3. Implement the smallest coherent change without changing the stack as a side effect.
4. Verify relevant behavior. Log exact commands, results, evidence paths and checks not run.
5. Update WORK_LOG, MEMORY, TASKS and CHANGELOG in the same commit. Update specialized documents when their claims change.
6. Record a decision when alternatives/tradeoffs affect future work. Record an incident when a failure is worth preserving.
7. Check documentation links and publication exclusions, review the staged diff, commit coherently and verify the remote when pushing is authorized.

## Update matrix

| Change | Additional documents to review |
|---|---|
| Feature/scope | PRD, ARCHITECTURE, DESIGN, TEST_PLAN |
| Parser, probe or model behavior | ARCHITECTURE, SECURITY, TEST_PLAN, relevant incident/decision |
| Dependency or image/model version | README, DECISIONS, reproducibility metadata for NEW runs |
| Research experiment | EXPERIMENT_PROTOCOL, EVIDENCE, measured report; preserve prior observations |
| Defect fix | INCIDENTS and regression evidence |
| Operational setup | README, SECURITY, MEMORY |
| Publication | Source provenance, exclusions, WORK_LOG and remote verification |

## Work-entry template

```text
ID / date / task:
Request and acceptance criteria:
Files and behavior changed:
Why and how:
Commands run and observed results:
Evidence paths:
Failures / limitations / checks not run:
Decisions or incidents:
Commit and remote verification:
Next action:
```

## Decision template

```text
ADR ID / date / status:
Context and alternatives:
Decision and rationale:
Consequences and risks:
Verification:
Supersedes / superseded by:
```

## Evidence language

Use **planned**, **implemented**, **software-tested**, **live-observed**, **independently evaluated**, **partial**, **blocked** or **deferred** precisely. Do not say 'complete research', 'no errors' or 'production ready' from a passing regression suite. Record unknowns instead of inventing causes, timestamps or measurements.

## Enforcement and limits

`scripts/repository_check.py` verifies required documents, Markdown file links, forbidden tracked paths, common credential patterns and matches to actual local lab credential bytes without printing their values. It also checks for workflow-document updates alongside staged code changes after the initial commit. Run it before committing. This is a bounded local check, not a full secret scanner or automated proof that prose is accurate. Reviewer judgment remains necessary.

The versioned `.githooks/pre-commit` runs this check locally. Enable it in a clone with `git config core.hooksPath .githooks`; this setting is repository-local and is not automatically inherited by a fresh clone. It is enabled in the current workspace. The hook does not run experiments or contact the network. GitHub-hosted CI is not configured; do not claim a local passing run is a GitHub Actions run.
