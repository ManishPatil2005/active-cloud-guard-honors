# Research and engineering task ledger

Status as of 2026-09-23. Completed means the stated acceptance criterion was met, not that the entire research hypothesis is proven.

| ID | Task | Status | Acceptance/evidence |
|---|---|---|---|
| M1-001 | Review original deck and pasted context | Complete | 15-page audit; docs/DECK_AUDIT.md |
| M1-002 | Define scope, threat model and evaluation protocol | Complete draft | docs/EXPERIMENT_PROTOCOL.md; professor approval remains open |
| M1-003 | Audit cited literature | Partial | docs/LITERATURE.md; blocked full texts and expanded search remain |
| M1-004 | Resolve TCI direction and missing-data semantics | Implemented/tested | scoring.py; monotonicity/bounds tests; calibration pending |
| M2-001 | Four-service Docker research testbed | Live-observed | output/live-testbed.json; four TCP accepts, two HTTP 200s |
| M2-002 | Labeled development corpus | Complete | 45 fixtures and hashes; not held-out data |
| M2-003 | Lexical and vector retrieval | Implemented/live-observed | nine source summaries; three semantic source checks |
| M2-004 | Established-tool baseline execution | Complete smoke run | Trivy: 11 fixtures, 34 excluded; policy alignment pending |
| M3-001 | Local model adapter and structured output validation | Implemented/tested | llm.py; retained schema failures and model outputs |
| M3-002 | Model location and limited evidence guards | Implemented/tested | grounding.py; known unsupported auth claim rejected |
| M3-003 | Controlled TCP probe and integrated pipeline | Implemented/live-observed | output/integrated-demo.json |
| M3-004 | Regression tests and reproducibility metadata | Complete baseline | 84 tests; lock, image/model digests and raw results |
| DOC-001 | Strict documentation and maintenance process | Complete | Documentation index, incident/decision ledgers, checked local commit guard |
| DOC-002 | Research-oriented GitHub README | Complete | Formal abstract, questions, architecture, linked evidence, reproduction and validity limits; no new research claims |
| VCS-001 | Private GitHub repository and initial publication | Complete | Private main verified on GitHub; local/remote commit match; see WORK_LOG |
| RES-001 | Independent labels and untouched grouped test set | Open | Two-reviewer workflow; adjudicated labels; no leakage |
| V2-001 | Exact-request audit reuse with bounded local retention | Implemented/tested/live-observed | Miss then two hits; context invalidation and corruption/expiry tests |
| V2-002 | Idempotent vector indexing and explicit generation controls | Implemented/tested/live-observed | Reuse embedded zero documents; forced rebuild nine; truncation/budget unit tests |
| V2-003 | Stage timing and fresh verification across reuse | Implemented/tested/live-observed | Four distinct TCP timestamps; cache hits 0.084/0.072 s on one development fixture |
| V2-004 | Resource/accuracy evaluation beyond repeat-work smoke | Open | Unseen-input distribution, matched conditions, independent labels and power measurement needed |
| RES-002 | Matched scanner/LLM/RAG/probe ablation study | Open | Comparable rule scope; paired confidence intervals; abstentions |
| RES-003 | Reduce and evaluate model hallucinations | Open | Broader held-out measurement, not only two guarded predicates |
| RES-004 | Meet or revise model latency target | Open | Current approximately 12-second smoke cases miss 3.5 seconds |
| RES-005 | Calibrate TCI and enrich verification | Open | Development-only calibration; authentication/multiple vantages |
| LATER-001 | Runtime telemetry and anomaly models | Deferred to M5-6 | Original roadmap; no implementation claim |
| LATER-002 | Full-system evaluation, thesis and defense | Deferred to M7-9 | Original roadmap; measured results required |
