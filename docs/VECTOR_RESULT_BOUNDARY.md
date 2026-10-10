# Vector retrieval corpus boundary

QA-020/R7/WL-095, 10 October 2026. Python/Compose/Ollama/Chroma and both engines preserved. This is source-level provenance validation, not an upstream vulnerability fix.

## Implemented acceptance

Before collection/network activity, k must be an exact integer1..256. One query must return exactly one list of IDs, metadata and distances, each with min(k, corpus size) rows. Reject unknown/duplicate IDs, non-dictionary metadata, non-string source_json and boolean/nonfinite/over1e100 distance magnitudes. No zip truncation or partial result fallback.

Stored source strings have a total UTF-8 budget of1MB and a pre-encoding character bound; existing strict JSON reader rejects duplicate fields, nonfinite constants and excessive structure. Canonical JSON representations must match the corresponding current corpus document. Return corpus-owned fields plus distance/current corpus hash, not decoded stored metadata. Whitespace/key-order differences are permitted, type/content differences are not. Chroma materializes its result before this validation: this is not a native allocation sandbox.

These checks cannot authenticate the filesystem, vector ranking, model digest, trusted corpus, dependency internals or adversarial library objects. Poisoned embeddings with matching metadata may still alter ranking. Existing trusted private embedded store and model assumptions remain. Index creation/repair and malicious-store import are not qualified here.

## Advisory review

Rechecked official GitHub records10October2026: [creation code injection](https://github.com/advisories/GHSA-f4j7-r4q5-qw2c), [tenant authorization](https://github.com/advisories/GHSA-2wm9-hf6c-p5cr), [update code injection](https://github.com/advisories/GHSA-36p7-vc44-83pf), [RBAC scope](https://github.com/advisories/GHSA-xph7-9rjv-w5fr). Each still lists no patched version; pinned Chroma1.0.20 matches affected ranges. Inspected project uses PersistentClient, telemetry disabled and embedding_function=None with explicit local vectors, not the described server/provider endpoints. This distinction does not clear the package or all deployment paths. No upgrade/exploit/server launch/source upload; server exposure remains prohibited and upstream remediation open.

## Verification and next gates

Pre-fix24cases:21fail/3pass; initial implementation127selected passes. Final32newcases and135selected passes each OS, including actual ephemeral explicit-vector accepted/forged metadata queries. Exact commands/results and fresh receipts in WORK_LOG. Preserve negative XML without whitespace normalization. Actual valid Chroma shape confirmed, not merely mocked.

No new full suite/installed-wheel/hosted run: vector.py changed, so prior built wheel source equality is no longer current qualification. Next engineering checks include fresh package/full regressions, native ext4 storage and supported Windows lifecycle review; dependency/native risks remain open. Genuine supervisor approval, qualified runtime timing/identity/coverage, independent labels/data, calibration/ablations/cost/novelty and production review remain separate gates.
