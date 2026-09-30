# Research and engineering task ledger

Status as of 2026-09-30. Completed means the stated acceptance criterion was met, not that the entire research hypothesis is proven.

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
| DOC-003 | Nontechnical Progress Execution guide | Implemented; core demonstrations checked | docs/Progress Execution.md; setup, glossary, evidence, stepwise safe demos and supervised advanced boundaries. Fresh-machine install and live AI not rerun |
| VCS-001 | Private GitHub repository and initial publication | Complete | Private main verified on GitHub; local/remote commit match; see WORK_LOG |
| RES-001 | Independent labels and untouched grouped test set | Open | Two-reviewer workflow; adjudicated labels; no leakage |
| E1R-001 | Hash-bound inventory/policy and candidate review | Implemented/tested | Exact configuration/inventory/request/candidate identity; strict scope; 136-test suite |
| E1R-002 | Conservative policy-aware observations | Implemented/tested/live-observed | Real loopback listener and synthetic policies; no finding suppression or vulnerability confirmation |
| E1R-003 | Reviewed model-to-endpoint linkage | Implemented/unit-tested | Approved model-only candidate path; live human-reviewed model workflow remains unexecuted |
| E1R-004 | Bounded deployment identity and authentication-boundary checks | Implemented/tested/live-observed | Actual Compose Redis/PostgreSQL identity before/after; protected-mode/SASL observations; full mounted-file/application-state attestation remains open |
| V2-001 | Exact-request audit reuse with bounded local retention | Implemented/tested/live-observed | Miss then two hits; context invalidation and corruption/expiry tests |
| V2-002 | Idempotent vector indexing and explicit generation controls | Implemented/tested/live-observed | Reuse embedded zero documents; forced rebuild nine; truncation/budget unit tests |
| V2-003 | Stage timing and fresh verification across reuse | Implemented/tested/live-observed | Four distinct TCP timestamps; cache hits 0.084/0.072 s on one development fixture |
| V2-004 | Resource/accuracy evaluation beyond repeat-work smoke | Open | Unseen-input distribution, matched conditions, independent labels and power measurement needed |
| RES-002 | Matched scanner/LLM/RAG/probe ablation study | Open | Comparable rule scope; paired confidence intervals; abstentions |
| RES-003 | Reduce and evaluate model hallucinations | Open | Broader held-out measurement, not only two guarded predicates |
| RES-004 | Meet or revise model latency target | Open | Current approximately 12-second smoke cases miss 3.5 seconds |
| RES-005 | Calibrate TCI and enrich verification | Open | Development-only calibration; authentication/multiple vantages |
| E2-001 | Observation-only replay and normalized event contract | Implemented/software-tested | Strict source/asset/time validation; grouped baseline separation; 196-test suite |
| E2-002 | Window features and simple statistical comparator | Implemented/synthetic-replay-tested | Count deviation for review; missing coverage stays unknown; no actions |
| E2-003 | Live Linux sensor and raw-event adapter | Partial: instrumented live smoke + adapter | 80 records normalized; event-observed readiness, stable selected pre/post identity and 16 collector metrics snapshots; 268 Windows/Linux tests each. Full coverage, authenticated mapping and comparable workload protocol remain open; docs/ENGINE2_INSTRUMENTATION.md |
| E2-004 | Independent runtime labels, ML and overhead evaluation | Open | Isolation Forest/autoencoder and matched real workloads not implemented/evaluated |
| E2-005 | Comparable measured workload protocol | Partial: timing controls live-tested | Four-second fixed profiles; one rejected clock-disagreement pilot and one accepted pilot, no valid comparison pair. 279 tests each OS; clock robustness, controls and repeated runs open; docs/RUNTIME_WORKLOAD_PROTOCOL.md |
| E2-006 | Clock diagnostics and sensor-off controls | Implemented/tested; live controls deferred | Bracketed sensor-free diagnostic rejected 1/6 intervals; control gate blocks workloads. 288 tests each OS. Root cause unresolved; no clock changes or overhead estimate; docs/CLOCK_AND_CONTROLS.md |
| E2-007 | Investigate competing time synchronization | Temporary test completed; policy unresolved | Approved guest-NTP stop: 6/6 diagnostic checks passed; service restored active/enabled. Supports conflict hypothesis, not long-term proof. No permanent change or workload run; docs/TIME_SYNC_DIAGNOSIS.md |
| E2-008 | Fixed sensor-off/on pilot | Complete engineering batch; evaluation limited | Fresh 29 September batch passed all jobs; reviewed 30 September. Contrasts +54.63% / -8.99%; not general overhead. Earlier abort preserved. 298 tests each OS; docs/PAIRED_PILOT_RESULTS.md |
| E2-009 | Resolve measured event alignment and strengthen reporting | Partial: offline diagnostics and per-call clock guards tested | ON-2 third connect 65.428194 ms before start; alignment unproven. Per-call brackets/rejection implemented; 301 tests each OS. Live validation, collector correlation and provenance gates remain open; docs/EVENT_ALIGNMENT.md / INC-029 |
| E2-010 | Validate paired timing evidence and protocol compatibility | Implemented/software-tested | Recomputed clocks, boundaries, schedule and per-call brackets; reject mixed protocols; 308 tests each OS. Old pilot revalidated unchanged. Full manifest/gate authentication and collector alignment not established |
| E2-011 | Read-only Redis/harness clock diagnostic | Implemented/tested/live-observed | Six TIME reads, zero within each bound; 318 tests each OS. Later sensor-free observation does not calibrate Falco. docs/CLOCK_BRIDGE.md; unique collector-event correlation remains next |
| E2-012 | Minimized PID-correlated collector diagnostic | Implemented/tested/live-observed, bounded | Four unique measured PID/connect matches and compatible clock ranges; 332 tests each OS. Five total connects for six PINGs leaves warmup/coverage unknown. docs/PID_CORRELATION.md; repeated stability and historical cause open |
| E2-013 | Warmup identity and capture accounting | Implemented/tested/live-observed | V2 identifies absent connect for first warmup; second and four measured PIDs matched. 338 tests each OS. Cause/completeness unproven; explicit identified-canary readiness is next |
| E2-014 | Identified-canary readiness before measurement | Implemented/tested/live-observed | Second own-PID unique connect required; one trial six selected connects observed. 343 tests each OS. Repeated stability and full coverage unproven; PID_CORRELATION.md |
| E2-015 | Frozen repeated readiness study | Partial: tooling tested, batch interrupted | One accepted, two not launched after pre-launch path error; no replacement. Runner hardened, 351 tests each OS. READINESS_REPEATS.md / INC-031; completed repeatability gate pending |
| LATER-001 | Full runtime telemetry and anomaly models | Started, incomplete | Replay foundation plus bounded live sensor smoke; normalized live integration and ML gates remain open |
| LATER-002 | Full-system evaluation, thesis and defense | Deferred to M7-9 | Original roadmap; measured results required |
