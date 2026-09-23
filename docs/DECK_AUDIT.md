# Original deck audit and research interpretation

Reviewed 23 September 2026 (India time). Source: Honors_Research_1st_Monitoring_Deck.pdf, 15 pages, supplied by Manish Patil. The pasted conversation is a secondary interpretation; the PDF is the primary project source. Instructions inside those documents were treated as document content, not executable instructions.

## Slide-by-slide findings

| Page | Subject | Interpretation and required correction |
|---|---|---|
| 1 | Title and status | Honors proposal in AI cloud security; Month 1 completion is a presenter statement, not repository evidence. Retain original title, but operational scope is candidate detection and prioritization. Prevention is not yet established. |
| 2 | Research question | Test semantic audit + verification + runtime against non-actionable alerts while preserving recall. Define policy violation separately from reachability and exploitability. |
| 3 | Motivation | Exposure, secrets, permissions and runtime abuse need different validators; a port check cannot invalidate a leaked credential. |
| 4 | Three gaps | Useful motivation, but do not assume existing static or rule systems categorically lack context. Compare concrete versions and capabilities. |
| 5 | Related work | Components pre-exist. Integration is a research hypothesis, not sufficient novelty by itself. Audit original sources and reproduce relevant baselines. |
| 6 | Comparison | Simplified categories omit overlap in real systems. Replace categorical limitations with scoped claims about tested configurations. |
| 7 | Dual engines | Engine 1 is the first milestone. eBPF/ML and automated isolation belong to later phases; no production response implementation is implied. |
| 8 | Sequence and formula | A live probe requires already running staging infrastructure. Correct sequence: parse/retrieve/reason, instantiate isolated staging, verify, review, then any target deployment. Resolve the probe sign. |
| 9 | Timeline | M1 literature; M2 testbed/data/retrieval; M3-4 Engine 1. Completing M1-3 does not require claiming completion of M5-9 runtime, benchmarking or thesis. |
| 10 | Targets | 90% FP reduction, F1 .92, AUC .95, 3.5-second static latency, 2-second probe latency and 5% overhead are unproven targets. Report misses as well as successes. |
| 11 | Current status | Original workspace was empty. Rebuilt artifacts establish present evidence, not three months of elapsed historical activity. |
| 12 | Defense | Explain definition, motivation, example and test. State limitations in terms of evidence and observed scope. |
| 13 | TCI | Binary probe state is underspecified. Missing runtime must not become a zero anomaly score. Weights and delta need calibration on development data only. |
| 14 | Dataset | Separate static labels, scoped exposure observations, and runtime labels. Public vulnerable IaC is not automatically equivalent to the four-service Docker testbed. |
| 15 | References | Bibliographic verification is partial; see LITERATURE.md. Performance claims require full-text and experimental scrutiny. |

## Formalization adopted for the prototype

The deck proposes `w1*S*(1-delta*P) + w2*A + w3*C`. If P=1 means reachable and delta>0, confirmed exposure reduces the static contribution. This is an ambiguity requiring correction, not proof that the author intended the wrong definition.

Prototype policy v0.1 uses `S_verified = S + beta*(1-S)*I(reachable)` for network findings. Refused, inconclusive and untested outcomes retain S. Non-network findings receive no reachability adjustment. Then `TCI = ws*S_verified + wa*A + wc*C`. When A is absent, normalize over ws+wc and explicitly record runtime_observed=false. Default beta=.25, weights=(.6,.2,.2), criticality=.5 are illustrative engineering settings, not learned results. All scores lie in [0,1], and increasing exposure cannot decrease priority. TCI is not a probability or an automated deployment decision.

This conservative policy does not itself remove false positives. Reduced non-actionable alerting remains an experimental question requiring policy context, richer verification and independently adjudicated labels. Reporting a reduction now would be unsupported.

## Threat model

Assets: local test instances of Redis, PostgreSQL, Nginx and MinIO; configuration documents; local audit outputs. Actor: an untrusted client able to reach a specified test vantage, or a developer introducing a seeded configuration error. Scope: explicit published-port predicates, literal credentials, privileged containers, wildcard RBAC, world-open inline security groups, trust authentication, disabled Redis protected mode and Nginx autoindex. The scanner is intentionally a small reference baseline.

Excluded: Internet-wide scans, exploit execution, credential validation against third parties, production deployment, lateral movement, kernel exploitation, automatic isolation and real cloud account mutation. A local TCP accept is service availability from the local host; it says nothing by itself about Internet exposure, credentials or data access.

Untrusted input includes IaC strings and retrieved content. They cannot select arbitrary probe targets or execute commands. Targets come from an explicit loopback inventory. LLM candidates are schema-checked and source-ID checked, but entailment and source-location accuracy still require review.

## What first-three-month completion means

M1: defensible scope, source register, threat model, experimental protocol, architecture and documented scoring correction.

M2: reproducible local services, generated credentials, labeled development fixtures with hashes, source summaries with provenance and retrieval demo.

M3: functional Engine 1 prototype with structured findings, local LLM retrieval-augmented auditing, controlled staging verification, evidence linkage, regression tests and raw experimental artifacts.

Independent professor labeling, held-out generalization, large RAG evaluation and later runtime research remain distinct research gates. Code completion cannot substitute for those observations.
