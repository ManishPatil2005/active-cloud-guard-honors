# CLI and evidence interface design

This project has no web interface. This document defines the current research interaction and output conventions; it does not introduce frontend technologies.

- Commands: scan, retrieve, audit, index, vector-retrieve, probe and run. See README for exact examples.
- Outputs: readable JSON with stable named fields; reports are Markdown and test results JUnit XML.
- Findings must retain origin, asset/rule identifiers where applicable, source references and configuration locations. Scores are provisional priorities, not probabilities.
- Probe states remain reachable, unreachable and inconclusive, scoped to an endpoint, vantage and timestamp. Not-tested and not-applicable score states remain explicit.
- Model output errors must not become empty successful scans. Rejected candidates remain visible; an abstention is not a clean verdict.
- Reports separate software checks, live observations, development metrics and independent scientific evidence.
- Prefer plain language and reproducible commands over screenshots of terminal output. Never display generated credential values.

Expected user journey: read scope -> set up local prerequisites -> reproduce fixtures/tests -> start declared lab -> perform audit/probes -> inspect raw outputs and rejected candidates -> review measured report and unresolved gates.
