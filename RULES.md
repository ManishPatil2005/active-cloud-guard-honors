# Development and research rules

## Scope

This project investigates cloud OSS configuration audit, retrieval-assisted reasoning and controlled staging verification. Maintain the current CLI/library architecture. There is no requested web UI, authentication platform, hosted SaaS or production deployment.

## Implementation

- Keep parsing, retrieval, model transport/validation, probing, scoring and evaluation separate.
- Use safe YAML loading, explicit supported predicates and visible warnings/errors for recognized unsupported inputs.
- Preserve candidate provenance: source content/hash, model identity, file identity, location and origin.
- Probe only explicit loopback inventory destinations. Configuration or model text must never choose arbitrary targets or execute commands.
- Missing telemetry is not a zero anomaly observation. A failed/inconclusive TCP check cannot cancel a secret or authorization issue.
- Do not silently fall back from failed model inference to a fabricated result or clean verdict.

## Documentation and evidence

Read docs/CURRENT_STATUS.md through the index before assigning current engine status. Every substantive change must maintain its capability/priority/evidence distinctions when affected. Do not say an engine is simply complete/incomplete without named acceptance scope: implemented baseline, completed refinements, missing planned capabilities and scientific gates are separate. Historical checkpoint text and whole-repository test counts are not current effectiveness proof. Every new helper/refinement must name its original research requirement/task and reason for priority; do not expand supporting safety work by default.

Follow `docs/DOCUMENTATION_WORKFLOW.md`. Do not describe a proposed capability as implemented, or a test as run without execution evidence. Keep failed model outputs alongside subsequent observations. Record limitations and negative findings as first-class research evidence.

## Validation and Git

Run lint, formatting checks, relevant tests and dependency checks for code changes. Run documentation checks for documentation changes. Record which live checks were or were not rerun; do not rerun model experiments merely to make results look better.

Stage explicit project directories/files, inspect the index and verify exclusions. Commit all reproducible source, documentation, fixtures and reviewed evidence. Exclude runtime credentials, `.venv`, caches, vector databases and model weights. Use a private repository unless the owner explicitly changes visibility. Do not select an open-source license on the owner's behalf.
