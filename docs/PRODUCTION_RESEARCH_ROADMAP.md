# Sequenced production and research readiness roadmap

9 October 2026. User asks to finish remaining work one by one, preserving the architecture. This is an execution/acceptance roadmap, not a claim of production readiness, novelty, supervisor approval or deployment authorization. Engineering and scientific gates can proceed in parallel where dependencies allow.

| Sequence | Work and acceptance | Current disposition / dependency |
|---|---|---|
| 1 / QA-007 | Malformed model envelopes/metadata explicitly reject; bad cache requires fresh inference; no invalid cache/index publication; regression evidence preserved | Implemented, verification in [contract](MODEL_ENVELOPE_VALIDATION.md)/WORK_LOG |
| 2 / QA-008 | Selected legacy inputs/client stdout/stderr and aggregate/checkpoint budgets; direct-child timeout/interruption cleanup, negative/partial receipts and publication cap | Implemented; [contract](LEGACY_RUNNER_BUDGETS.md)/WORK_LOG. Not all-process sandbox, descendant/remote-container cleanup, hard blocked-IO/native deadlines or qualified research |
| 3 / QA-009/QA-010/QA-011 | Local dependency/advisory review, focused parser/resource fuzzing, cache/artifact access/race review and native boundary audit | Partial: stream/cache fixes, installed advisory triage and [isolated patched portable candidates](DEPENDENCY_CANDIDATE_QUALIFICATION.md). Active/default promotion/full optional Windows-vector qualification/Chroma remediation/OS-image/ancestor/native audit open; no blind historical lock replacement/cloud provisioning |
| 4 / QA-012/QA-013/QA-014/QA-016 | Fresh-host reproducibility, automated cross-platform regression pipeline and operator runbook | Partial: portable setup/pin verifier/local package qualification and authorized manual fixed-host CI definition. Actual hosted run acceptance requires recorded run/head/job receipts; local tests/structural workflow checks are not GitHub Actions passes. No production host selected/provisioned |
| 5 | Supervisor approves label/claim/context/unit/group/sample/privacy/analysis and acquisition qualification | Human gate; [proposal](ENGINE2_SUPERVISOR_REVIEW_PROPOSAL.md) remains DRAFT—NOT APPROVED |
| 6 | Qualify identity, readiness, coverage/accounting, event/clock bounds and matched workload conditions; preserve rejected runs | Open experimental gate. Native fence/restoration work only if needed for an approved intervention, with separate permission |
| 7 | New independent grouped captures/static cases and two actual blinded reviewers; original votes/adjudication/unknowns | Open. Prior synthetic/development data not promoted into held-out evidence |
| 8 | Freeze protocol/splits/prompt/model/corpus/rules; implement reviewed eligible-real-data fitting/calibration/evaluation without bypassing synthetic wrappers | Open; approved scope/context/data required before claiming executed independent study |
| 9 | Fair matched scanner/LLM/RAG/probe and runtime statistical/IF/AE comparisons; complete denominators/grouped uncertainty; TCI calibration | Open empirical phase, not solved by synthetic utilities |
| 10 | Matched acquisition/model costs and recall/FP/latency/overhead/energy tradeoffs | Open; actual qualified timing/resources/power evidence, not test-suite durations |
| 11 | Full-text literature/closest baseline reproduction and contribution-versus-evidence matrix | Related-work work can proceed earlier. Novelty remains a hypothesis until fair measured contribution and reviewer scrutiny |
| 12 | Thesis/paper/results/negative findings/threats/reproducibility, supervisor/external review and defense | Open; no guaranteed venue acceptance or claim all targets met |
| 13 | Production scope review, independent security assessment, least privilege/isolation, monitoring/recovery/rollback/retention and authorized staging acceptance | Separate operational gate; production release only after reviewed target/use-case/claims and relevant assurance, no automatic cloud response |

## Completion definitions

An engineering task is complete only for its named supported behavior and executed acceptance checks. Record failures, scope and limits in the same commit. Passing tests do not authenticate saved declarations or establish security detection accuracy.

Research-ready means a defensible question/contribution, genuine approved protocol and independent data/review, frozen fair experiments with uncertainty and traceable negative results. Targets may be missed and still produce valid research; fabricated labels, hidden failures and unsupported novelty claims cannot.

Production-ready means ready for a specifically reviewed operational deployment—not generically safe for every cloud account. Current loopback research prototype cannot silently become an Internet scanner, production remediation service or autonomous isolation system. Hosting/deployment/access controls need separate scope and authority; no stack migration is implied.

No arbitrary third engine, engine version or framework migration substitutes for those missing gates. The current Python/Compose/Ollama/Chroma two-engine design is retained. Record actual progress in [MEMORY](MEMORY.md), [TASKS](../TASKS.md) and [WORK_LOG](WORK_LOG.md); [complete outstanding research list](RESEARCH_COMPLETION_STATUS_20261009.md) remains applicable.
