# CLI and evidence interface design

Integrated-replay now supports opt-in --engine1-pipeline with required --kb and existing --model/--vector-index/--cache-dir/--timeout/--max-tokens/--policy/--reviews. Options require explicit mode; output labels actual pipeline execution/requested model/distinct probed assets, preserves full reports and adds reviewed model-verification references to contexts. Existing rule mode remains offline; pipeline mode may use requested local services. Stable distinct pipeline protocol, null combined priority/false joint authority. [Contract/examples](PIPELINE_RUNTIME_INTEGRATION.md).

Engine 2 adds `runtime-replay CAPTURE --baseline BASELINE --inventory INVENTORY` with optional window size and threshold. Output explicitly identifies observation_only_replay, source provenance, unknown coverage, insufficient baseline/deviation states and an empty actions_executed list. It is not a live monitor. Full contract: ENGINE2_FOUNDATION.md.

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
