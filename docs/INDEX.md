# Documentation index

Start here when reviewing or continuing the project. The owner is Manish Patil; repository: [active-cloud-guard-honors](https://github.com/ManishPatil2005/active-cloud-guard-honors), private.

| Document | Purpose |
|---|---|
| [PRD](PRD.md) | What the research prototype must do and why |
| [Architecture](ARCHITECTURE.md) | Existing stack, modules, flow and boundaries |
| [Engine 1 v2](ENGINE1_V2.md) | Repeat-work efficiency, budgets, cache contracts and reproduction |
| [Engine 1 refinement](ENGINE1_REFINEMENT.md) | V2.1 reviewed verification, operator templates, results and remaining gates |
| [Engine 1 baseline](ENGINE1_BASELINE.md) | V2.2 local deployment identity and bounded Redis/PostgreSQL checks |
| [Engine 2 foundation](ENGINE2_FOUNDATION.md) | Observation-only replay contract, statistical baseline, evidence and sensor prerequisites |
| [Engine 2 sensor trial](ENGINE2_SENSOR_TRIAL.md) | Bounded live Falco observation, failed attempts, privileges, tests and remaining integration gates |
| [Engine 2 adapter](ENGINE2_ADAPTER.md) | Offline raw-event validation, minimized normalized capture, accounting and remaining coverage gates |
| [Engine 2 instrumentation](ENGINE2_INSTRUMENTATION.md) | Event-observed readiness, selected identity continuity and collector-wide loss counters |
| [Runtime workload protocol](RUNTIME_WORKLOAD_PROTOCOL.md) | Fixed measured profiles, timing gates, preserved pilot failure and next control experiments |
| [Clock and controls](CLOCK_AND_CONTROLS.md) | Bracketed diagnostics, reproduced timing failure and deferred sensor-off controls |
| [Windows/Linux setup](WINDOWS_LINUX_SETUP.md) | Installed research WSL distribution, actual Linux preflight, Docker integration handoff and sensor gates |
| [Interface design](DESIGN.md) | CLI/output contracts; no proposed web redesign |
| [Rules](../RULES.md) | Implementation, evidence and Git rules |
| [Working agreement](../AGENTS.md) | Required context and maintenance for future work |
| [Tasks](../TASKS.md) | Completed, partial, open and deferred work |
| [Decisions](DECISIONS.md) | Durable decisions and consequences |
| [Current state](MEMORY.md) | Current capabilities, limits and next steps |
| [Test plan](TEST_PLAN.md) | Checks, commands, evidence and interpretation |
| [Security](SECURITY.md) | Probe limits, secrets, model trust and publication policy |
| [Work log](WORK_LOG.md) | What changed, how, verification and unresolved work |
| [Incident ledger](INCIDENTS.md) | Symptoms, diagnoses, fixes and remaining limits |
| [Evidence index](EVIDENCE.md) | Saved observations and what each can establish |
| [Documentation workflow](DOCUMENTATION_WORKFLOW.md) | Required updates per change and reusable templates |
| [Changelog](../CHANGELOG.md) | Human-readable change history |
| [Run instructions](../README.md) | Setup, operation and reproducibility |
| [Deck audit](DECK_AUDIT.md) | Slide-by-slide interpretation and corrections |
| [Experiment protocol](EXPERIMENT_PROTOCOL.md) | Independent scientific evaluation plan |
| [Literature audit](LITERATURE.md) | Source verification levels and uncertainties |
| [M1-3 acceptance ledger](MONTHS_1_TO_3.md) | Engineering milestone versus research gates |
| [Measured status](../output/RESEARCH_STATUS.md) | Generated summary of saved experimental evidence |
| [Source provenance](source/README.md) | Original deck and content hash |

Authority: explicit user requests govern scope; actual source code and saved observations determine implementation status. A plan is not evidence of execution. `MEMORY.md` describes current state; `WORK_LOG.md`, `INCIDENTS.md`, `DECISIONS.md` and Git preserve history. Do not rewrite old observations to match a later implementation.
