"""Link configuration findings to explicitly mapped staging endpoints."""

import time
from .scanner import scan
from .retrieval import retrieve
from .llm import audit
from .probe import probe
from .scoring import score
from .cache import fingerprint
from .verification import (
    file_hash,
    load_inventory,
    load_context,
    policy_assets,
    approved_candidates,
    assess,
    POLICY_SCHEMA,
    REVIEW_SCHEMA,
)

NETWORK_RULES = {"NET001", "NET002", "NET003"}


def run(
    path,
    kb,
    inventory=None,
    model=None,
    vector_index=None,
    *,
    cache_dir=None,
    timeout=180,
    max_tokens=512,
    policy=None,
    reviews=None,
):
    started = time.perf_counter()
    configuration_hash = file_hash(path)
    by_asset, inventory_hash = load_inventory(inventory)
    policy_context = load_context(
        policy, POLICY_SCHEMA, configuration_hash, inventory_hash
    )
    policies = policy_assets(policy_context, by_asset)
    review_context = load_context(
        reviews, REVIEW_SCHEMA, configuration_hash, inventory_hash
    )
    if reviews and not model:
        raise ValueError("reviewed verification requires a current model audit")
    report = scan(path)
    timings = {"scan_ms": (time.perf_counter() - started) * 1000}
    stage = time.perf_counter()
    from .limits import read_text

    text = read_text(path)
    if vector_index:
        from .vector import retrieve_vector

        report["retrieved_sources"] = retrieve_vector(text, kb, vector_index)
    else:
        report["retrieved_sources"] = retrieve(text, kb)
    report["retrieval_mode"] = "chroma_ollama" if vector_index else "lexical"
    timings["retrieval_ms"] = (time.perf_counter() - stage) * 1000
    stage = time.perf_counter()
    report["rag"] = None
    if model:
        # Model candidates remain separately identified; never silently replace rule findings.
        report["rag"] = audit(
            text,
            report["retrieved_sources"],
            model,
            cache_dir=cache_dir,
            timeout=timeout,
            max_tokens=max_tokens,
        )
    timings["audit_ms"] = (time.perf_counter() - stage) * 1000
    stage = time.perf_counter()
    approvals = approved_candidates(review_context, report["rag"], by_asset, policies)
    if file_hash(path) != configuration_hash:
        raise ValueError("configuration changed during audit")
    probe_cache = {}

    def observe(asset):
        endpoint = by_asset[asset]
        if asset not in probe_cache:
            probe_cache[asset] = probe(
                endpoint["host"],
                endpoint["port"],
                allowlist={(endpoint["host"], endpoint["port"])},
                asset_id=asset,
            )
        return probe_cache[asset]

    for finding in report["findings"]:
        state = (
            "not_applicable"
            if finding["rule_id"] not in NETWORK_RULES
            else "not_tested"
        )
        evidence = None
        if finding["rule_id"] in NETWORK_RULES and finding["asset_id"] in by_asset:
            asset = finding["asset_id"]
            evidence = observe(asset)
            state = evidence["outcome"]
        finding["probe"] = evidence
        finding["verification"] = assess(
            policies.get(finding["asset_id"]),
            evidence,
            finding["rule_id"] in NETWORK_RULES,
        )
        finding["priority"] = score(
            finding["static_score"], criticality=0.5, exposure=state
        )
    report["model_verifications"] = []
    for approval, candidate in approvals:
        asset = approval["inventory_asset_id"]
        evidence = observe(asset)
        report["model_verifications"].append(
            dict(
                candidate_sha256=fingerprint(candidate),
                candidate=candidate,
                approval=approval,
                reviewed_by=review_context["document"]["reviewed_by"],
                probe=evidence,
                verification=assess(policies[asset], evidence),
                review_required=True,
                priority=None,
            )
        )
    if report["rag"]:
        report["model_candidate_ids"] = [
            fingerprint(c) for c in report["rag"]["output"]["findings"]
        ]
    report["configuration_bytes_sha256"] = configuration_hash
    report["inventory_sha256"] = inventory_hash
    report["verification_context"] = dict(policy=policy_context, review=review_context)
    report["policy_notes"] = [
        "Inventory maps candidate assets to staging endpoints; it does not establish Internet reachability.",
        "Only network rules and explicitly reviewed model candidates receive TCP evidence; no finding is refuted by TCP refusal.",
        "Asset criticality 0.5 and weights are illustrative, not calibrated.",
        "Model approval authorizes TCP evidence only, not correctness, vulnerability confirmation or automatic scoring.",
        "Hash-bound operator policy is not proof of deployment equivalence; legacy inventory mappings remain unverified.",
    ]
    timings["verification_and_score_ms"] = (time.perf_counter() - stage) * 1000
    timings["total_ms"] = (time.perf_counter() - started) * 1000
    report["timings_ms"] = {k: round(v, 3) for k, v in timings.items()}
    report["engine_version"] = "2.2"
    return report
