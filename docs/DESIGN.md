# CLI and evidence interface design

V2.2 adds `verify-service PATH --inventory FILE --service redis|postgres`. Its report contains the scan, deployment_before/after, service_observation and usable attribution flag. Identity mismatch does not become a clean verdict. See ENGINE1_BASELINE.md.

This project has no web interface. This document defines the current research interaction and output conventions; it does not introduce frontend technologies.

- Commands: scan, retrieve, audit, index, vector-retrieve, probe and run. See README for exact examples.
- Outputs: readable JSON with stable named fields; reports are Markdown and test results JUnit XML.
- Findings must retain origin, asset/rule identifiers where applicable, source references and configuration locations. Scores are provisional priorities, not probabilities.
- Probe states remain reachable, unreachable and inconclusive, scoped to an endpoint, vantage and timestamp. Not-tested and not-applicable score states remain explicit.
- Model output errors must not become empty successful scans. Rejected candidates remain visible; an abstention is not a clean verdict.
- Reports separate software checks, live observations, development metrics and independent scientific evidence.
- Prefer plain language and reproducible commands over screenshots of terminal output. Never display generated credential values.

Expected user journey: read scope -> set up local prerequisites -> reproduce fixtures/tests -> start declared lab -> perform audit/probes -> inspect raw outputs and rejected candidates -> review measured report and unresolved gates.

V2.1 adds optional run flags `--policy` and `--reviews`. Reports retain legacy findings while adding `verification`, `model_candidate_ids`, `model_verifications`, `configuration_bytes_sha256` and `verification_context`. Policy judgments are scoped observations, not security verdicts. Review documents use byte hashes rather than the scanner's normalized-text hash. See [refinement workflow](ENGINE1_REFINEMENT.md).
