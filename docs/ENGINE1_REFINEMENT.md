# Engine 1 refinement report: reviewed verification

Date: 2026-09-23. Engine report **2.1**, package **0.3.0**. This is a bounded refinement of Engine 1 v2, not completion of all Engine 1 research gates or implementation of Engine 2.

## Objective and result

Add explicit policy context and a trusted review boundary between model candidates and existing loopback TCP verification. Preserve Python, Docker Compose, Ollama, Chroma, the rule baseline and historical evidence.

| Acceptance | Result |
|---|---|
| Bind context to exact configuration and inventory | SHA-256 identities checked; mismatches fail before probing |
| Bind model approval to exact request and candidate | Request hash plus full candidate fingerprint; digest-bound audit required |
| No autonomous model-chosen destination | Reviewer maps to a prevalidated literal-loopback inventory asset |
| Policy-aware interpretation | Expected/unexpected reachability, inconclusive, not observed, not tested, missing policy or not applicable |
| Preserve uncertainty | No vulnerability confirmation, deployment attestation, suppression or automatic model scoring |
| Preserve freshness | Within-run asset deduplication only; probes repeat on subsequent runs |
| Regression and real network checks | 136 software tests passed; five controlled loopback smoke checks passed |

## What changed

`verification.py` validates bounded JSON documents, rejects duplicate JSON keys, unknown fields, duplicate assets and non-loopback endpoints. Inventory validation now runs before inference and before any probe. A run parses one inventory snapshot and records its byte hash. Policy/review documents also retain hashes and parsed contents in the report.

`pipeline.py` adds policy assessments to rule findings and a separate `model_verifications` list for explicitly approved model candidates. Candidate IDs are canonical SHA-256 fingerprints, exposed as `model_candidate_ids` in the same order as retained RAG findings. Rejected candidates cannot be approved. The unchanged scoring policy still handles rule findings; approved model evidence has `priority: null` and `review_required: true`.

`run --policy ... --reviews ...` enables the workflow. Both switches are optional. Existing inventory-only commands still work, but now explicitly report missing policy and unverified deployment equivalence. Inventory entries are strictly limited to asset_id/host/port; extra metadata must not be silently ignored.

## Trust and evidence semantics

Policy/review files are **trusted operator inputs**, not model-generated authority. A reviewer name is an audit annotation, not an authenticated identity or digital signature. The program does not verify that a human actually reviewed the file. Do not load these files from untrusted sources or automatically produce approvals from model output.

Hash agreement means the declared documents refer to these exact bytes. It does **not** prove a running service was deployed from that configuration. `relationship` distinguishes an analogue from an operator assertion of equivalence, but **deployment_equivalence_verified remains false for both**. Independent container/configuration attestation is still needed.

`unexpected_reachability` means an endpoint accepted TCP from the local host despite a declared forbidden-reachability policy. It does not mean the source configuration caused that condition, authentication was bypassed, or the service is publicly exposed. `expected_reachability` does not clear other findings. A refusal remains scoped non-observation; it never suppresses a candidate. Non-network rule findings do not acquire network judgments.

The review authorizes only TCP evidence collection, not a claim that the candidate is correct. The pipeline deliberately does not translate the model's score into a calibrated priority. Auth-aware service checks, deployment attestation and independent effectiveness remain open.

## Operator workflow

1. Run the normal pipeline against an approved inventory. For model review, enable `--cache-dir output/audit-cache` so the audit includes actual model identity. Save its JSON to a new report file.
2. Read the retained candidates and source evidence. Review asset identity, location, claim and intended access. Do not approve a candidate merely because it passes schema validation.
3. Create a policy document using `configuration_bytes_sha256` and `inventory_sha256` from the report. The scanner's older `sha256` is a normalized-text hash; it is **not** the policy byte hash on files with different line endings.
4. For each candidate that merits a TCP observation, create an approval using `rag.request_sha256`, its corresponding `model_candidate_ids` entry, and the inventory asset. Record a reviewer and rationale. Do not approve rejected candidates.
5. Rerun with both documents. Any changed request/candidate or stale configuration/inventory requires renewed review. A cache hit helps preserve the exact candidate; a newly generated different candidate invalidates its approval. Policies/reviews do not suppress fresh probe execution.

Policy template (replace every angle-bracket placeholder; these are deliberately not usable approvals):

```json
{
  "version": "1.0",
  "configuration_sha256": "<configuration_bytes_sha256 from report>",
  "inventory_sha256": "<inventory_sha256 from report>",
  "reviewed_by": "<actual reviewer>",
  "rationale": "<intended access and experimental scope>",
  "assets": [{
    "asset_id": "compose/redis",
    "expected_reachability": "forbidden",
    "relationship": "analogue"
  }]
}
```

Allowed expectations: `allowed`, `forbidden`. Allowed relationships: `analogue`, `operator_asserted_same_configuration`. Neither relationship is machine attestation. Policy coverage can be partial; missing assets remain `policy_missing` and cannot receive reviewed model verification.

Review template:

```json
{
  "version": "1.0",
  "configuration_sha256": "<configuration_bytes_sha256 from report>",
  "inventory_sha256": "<inventory_sha256 from report>",
  "audit_request_sha256": "<rag.request_sha256 from report>",
  "reviewed_by": "<actual reviewer>",
  "approvals": [{
    "candidate_sha256": "<corresponding model_candidate_ids entry>",
    "inventory_asset_id": "compose/redis",
    "verification_scope": "tcp_reachability_only",
    "rationale": "<why this candidate maps to this endpoint and merits a TCP check>"
  }]
}
```

After creating and reviewing real documents:

```text
python -m cloudguard.cli run data/development/redis-all.yaml --inventory testbed/inventory.json --model qwen2.5:3b --cache-dir output/audit-cache --policy output/operator-policy.json --reviews output/operator-review.json
```

Those operator filenames are examples, not files supplied by this change. No real review has been fabricated. Protect reviewer/context files like other sensitive project records and review them before publication. Model identity lookups are required even on cache hits. Review records have no automatic expiration; re-review them when intended policy or deployment changes even if file hashes do not.

## Verification performed

- `python -m ruff check cloudguard scripts tests`: passed.
- `python -m pytest -q --junitxml=output/verification-v21-tests.xml`: 136 passed.
- `python -m pip check`: no broken requirements.
- `python -m cloudguard.cli run --help`: new options displayed.
- `python scripts/verification_check.py --output output/verification-v21-smoke.json`: five checks passed: real connections, expected/unexpected distinction, no suppression, fresh timestamps, stale binding rejection.

The smoke starts a temporary **accept-only loopback TCP listener**, not Redis or a deployed manifest. It uses explicitly synthetic policy records, makes real connections, and shuts down its server. It does not call Ollama. Model approval integration is unit-tested using mocked audit output; no live human-approved model-to-service study is claimed. Failed/stale runs are not clean verdicts.

Evidence: [software report](../output/verification-v21-tests.xml), [loopback observation](../output/verification-v21-smoke.json). Old v1/v2 reports remain unchanged; their latency measurements are historical and must not be presented as v2.1 timings.

## Remaining work, in order

1. Supervisor agreement on policy/actionability definitions and provisional scoring semantics.
2. Attest actual lab deployment/configuration identity; then add scoped authentication-aware checks.
3. Obtain independent annotations and freeze matched evaluation data; compare baseline, LLM, RAG and verified variants without excluding abstentions.
4. Measure unseen-input latency and resource consumption. No new speed/energy claim follows from this refinement.
5. Start a minimal observation-only Engine 2 after stable evidence/asset contracts are agreed.

This closes an implementation gap in reviewed evidence linkage. It does not prove false-positive reduction, general detection accuracy, novelty, production readiness or completion of the full proposal.
