# First-three-month deliverables and acceptance ledger

This work implements the initial research milestone now. It does not fabricate three months of historical activities or experiments. The status ledger separates engineering completion from scientific validation.

| Month | Deliverable | Evidence | Remaining scientific gate |
|---|---|---|---|
| 1 | Problem definition and bounded threat model | DECK_AUDIT.md | Professor scope review |
| 1 | Related-work and claim audit | LITERATURE.md | Full-text verification of blocked sources and expanded systematic search |
| 1 | Architecture and TCI correction | cloudguard modules; DECK_AUDIT.md | Calibration and comparative validation |
| 1 | Evaluation protocol | EXPERIMENT_PROTOCOL.md | Independent labels and frozen evaluation set |
| 2 | Redis/PostgreSQL/Nginx/MinIO testbed | testbed/compose.yaml; output/live-testbed.json | Additional network vantages and policy contexts |
| 2 | Labeled development data | 45 fixtures; data/labels.json | Independent, larger, realistic dataset |
| 2 | Source register and retrieval | knowledge/sources.json; retrieval.py; vector.py | Broader licensed corpus; retrieval quality evaluation |
| 2 | Baseline observations | output/baseline-development.json; Trivy script | Rule alignment and fair paired comparison |
| 3 | Structured local LLM audit | llm.py; output/rag-smoke.json | Generalization and hallucination evaluation |
| 3 | Explicit endpoint verification | probe.py; output/live-testbed.json | Authentication-aware checks and multiple vantages |
| 3 | Evidence-linked Engine 1 | pipeline.py; CLI | Reviewed LLM asset matching before automatic verification |
| 3 | Tests and reproducibility | tests; output/test-results.xml; environment capture | Cross-host rerun and external code review |

## Professor-facing statement

I have implemented an early, reproducible configuration-audit and staging-verification prototype for the first three months of the proposed research. It includes a bounded rule baseline, local retrieval-augmented model inference, structured outputs, explicit probe evidence and a corrected provisional risk policy. Development and live service tests are recorded separately from claims about research effectiveness. The next scientific step is an independently labeled, frozen evaluation set and a fair comparison with established tools. The later runtime engine has not been claimed as complete.

## Expected later work from the original schedule

Month 4: broaden and validate Engine 1, add policy-aware/authentication-aware verification, freeze prompts and matched baselines. Months 5-6: Linux/k3s telemetry, benign-run feature collection and anomaly baselines. Month 7: paired ablations and controlled evaluation. Months 8-9: thesis, paper and defense based on measured results, including negative results.

No emails, professor submissions, cloud deployments or external publications were performed.
