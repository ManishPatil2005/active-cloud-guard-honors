# Current project state

Updated 7 October 2026 (Asia/Calcutta). This file is the **single current working summary**, not a chronological log. Read [CURRENT_STATUS](CURRENT_STATUS.md), [TASKS](../TASKS.md) and relevant source/evidence before assigning acceptance. Keep this summary current in place; put dated execution history in [WORK_LOG](WORK_LOG.md). No background work or autonomous monitoring is scheduled.

## What exists now

| Layer | Implemented scope | Not established |
|---|---|---|
| Engine1 | Frozen engineering baseline engine1-v2.2 at6736a577f1ba08b4700daf8a86370ec3bbd1c019: configuration checks, retrieval/local-model transport, scoped observations, policy/candidate identity guards and bounded reuse | Independent effectiveness, broad hallucination reduction, general latency/TCI calibration or production readiness |
| Engine2 baseline | Saved normalized captures, strict parsing/identity/window/group guards, statistical count-deviation replay; separate bounded Falco acquisition/adapter/diagnostic tooling | Continuous default sensor integration, complete coverage/collector alignment, calibrated security detection or automatic response |
| Optional Engine2 ML | Synthetic-only per-asset Isolation Forest and undercomplete reconstruction autoencoder, baseline-only fit, continuous scores/null binary predictions and explicit abstentions | Approved real-data fitting, independent labels/held-out effectiveness or optimal model design |
| Evaluation preparation | Offline intake/typed receipt consistency, observed-unit index, existing-data audit, synthetic-only decision accounting, draft reviewer/eligibility/supervisor documents | Authentic supervisor approval, actual independent humans, newly eligible benchmark data or calibrated model decisions |
| Backend diagnostics | Safe typed import/module/metadata/version categories and both model CLI rejected receipts; reproduced reporting gap fixed | Original intermittent Windows import cause or guaranteed permanent environment stability |

Stack stays Python/CLI, Docker Compose, Ollama and Chroma. No third engine, web/SaaS migration, model/framework replacement or unapproved native/service/clock/cloud action. Software baseline commit faf60a707d8751dad7823684c3967e4d7dfc3961; the current documentation-only update changes no code/model/test algorithm.

## Verified software and latest observation

- Latest **full-suite** milestone remains E2-040: Linux **1,226 passed** (86.58 s console / 83.577 s XML); Windows **1,188 passed / 38 skips** (22.74 s / 22.736 s XML). Both collected 1,226, with zero failures/errors. Lint, 119-file formatting and both dependency checks passed. It was not rerun for this documentation-only update. Links: [Linux](../output/engine2-backend-diagnostic-linux-tests-20261007.xml), [Windows](../output/engine2-backend-diagnostic-windows-tests-20261007.xml).
- New bounded Windows import observation: exactly four fresh sequential Python processes, IF→AE and AE→IF twice each, 30-second per-child timeout/stop on first failure. All four imported both backends with Python 3.12.14 and pinned scikit-learn 1.9.1. No model instance/fitting, installation/cache purge/service/telemetry action. [Exact observation/reproduction](BACKEND_IMPORT_OBSERVATION_20261007.md), WL-067. Four passes are not old-fault reproduction, resolved cause, load/stress qualification or research effectiveness.
- INC-056 native intermittent import cause remains **unknown**; original failedXML unchanged. INC-057 diagnostic loss/misleading install advice is fixed/software-tested using injected faults. Do not conflate them or erase negative evidence. [Incidents](INCIDENTS.md).

## Research gates and next action

Actual supervisor approval has **not been obtained**. [ENGINE2_SUPERVISOR_REVIEW_PROPOSAL](ENGINE2_SUPERVISOR_REVIEW_PROPOSAL.md) remains DRAFT — NOT APPROVED. Next actual review must decide label target/claims, sufficient independent context, units/groups/sample/analysis, capture qualification, humans/privacy and separate operational permissions. Do not invent signatures, reviewer votes or a study result.

Existing7standalone normalized captures are5synthetic/2sensor-development; no independent benchmark is established. Known projection reuse/shared development family/timing-negative history remain in [data audit](RUNTIME_DATA_READINESS_AUDIT.md). Counts/synthetic decisions/declared IDs are not independent ground truth. Comparable timing/coverage/identity/context, genuine blinded humans, untouched grouped real-data evaluation/calibration, misses/false alarms/abstentions/delay/overhead/energy and bounded Engine1 integration remain open. Current synthetic wrappers must not be bypassed by relabeling real data.

Supporting native safety work remains partial and only resumes for a defined approved dependency. Generic proceed does not authorize clock/service stops, production scanning, automated response or new collection. No further success-seeking import reruns or unattended monitoring implied. Do not propose arbitrary model/engine versions to substitute for missing research evidence.

## Preserved historical memory

[MEMORY_HISTORY_20261007](MEMORY_HISTORY_20261007.md) is the **exact previous MEMORY.md byte snapshot**, not today's status. It retains older “Current update/Current work” headings and all checkpoint text unchanged; interpret those as historical. Original size: 56,968 bytes; SHA-256: `4e51af83e38e11bb9347eb3e1f27d59440d67397417a18e12096fcea2ba89c9a`. Same docs directory preserves relative link resolution. Do not overwrite the snapshot or backdate edits; chronological changes continue in WORK_LOG/CHANGELOG and Git.
