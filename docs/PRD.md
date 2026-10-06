# Research prototype requirements

Current6October interpretation: [CURRENT_STATUS](CURRENT_STATUS.md). First-three-month scope below historical, not a claim later Engine2 is unbuilt. Engine1 frozen; Engine2 baseline/bounded telemetry implemented, ML/independent validation open. [Intake](RUNTIME_INTAKE.md)/[selected typed receipts](RUNTIME_RECEIPTS.md) refine RQ3/E2-004 evaluation preparation; full coverage/alignment/protocol/authenticity/independent-human/eligible-data gates remain. Next approved labeling pack/eligible-capture checklist, no scope/stack/response permission change.

## Problem and users

Cloud-hosted open-source software can have configuration mistakes, exposed services and excessive permissions. A candidate configuration issue, observed network reachability and an actionable vulnerability are different facts. The research asks whether linking semantic auditing and controlled verification, and later runtime evidence, improves prioritization without losing coverage.

Primary users: Manish Patil as researcher/developer, the supervising professor/review panel, and reviewers reproducing experiments. The immediate outcome is an inspectable Engine 1 prototype and evidence package, not a production security service.

## First-three-month deliverables

| Requirement | Acceptance criterion | Present evidence |
|---|---|---|
| R1: Explain scope and related work | Traceable deck audit, source register, threat model and protocol | Existing research documents; some full texts unverified |
| R2: Reproduce a local testbed | Redis, PostgreSQL, Nginx and MinIO with explicit local endpoints | Compose and live observations |
| R3: Baseline configuration checks | Structured findings with asset/rule/location/provenance | Nine predicates, 45 development cases |
| R4: Grounded local model invocation | Retrieved sources, structured output checks, visible failures | Ollama adapter, Chroma and lexical smoke runs |
| R5: Scoped active verification | Explicit inventory, bounded TCP checks, distinct outcomes | Probe tests and live run |
| R6: Evidence-linked prioritization | Reachability cannot lower priority; missing runtime explicit | Provisional score and integration evidence |
| R7: Reproducibility and honest reporting | Versions, hashes, commands, test outputs, negative results | Lockfile, environment snapshot and reports |
| R8: Maintainable audit history | Document updates and meaningful version-control history | Documentation workflow and private GitHub repository |

## Exclusions

No production deployment, cloud-account mutation, Internet scanning, arbitrary attack execution, frontend/dashboard, user-authentication application, automated isolation or eBPF runtime engine in this milestone. Helm and general Terraform evaluation are not implemented. The supplied workflow example does not change these boundaries.

## Success and limits

Engineering success means repeatable supported behavior with documented errors and limitations. The deck's effectiveness and latency numbers remain research targets. Generalization requires independent labels, an untouched grouped test set and fair ablations. Passing development fixtures does not establish novelty, prevention efficacy or publication readiness.
