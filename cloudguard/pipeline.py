"""Link configuration findings to explicitly mapped staging endpoints."""

import hashlib
import json
from pathlib import Path
from .scanner import scan
from .retrieval import retrieve
from .llm import audit
from .probe import probe
from .scoring import score

NETWORK_RULES = {"NET001", "NET002", "NET003"}


def run(path, kb, inventory=None, model=None, vector_index=None):
    report = scan(path)
    text = Path(path).read_text(encoding="utf-8")
    if vector_index:
        from .vector import retrieve_vector

        report["retrieved_sources"] = retrieve_vector(text, kb, vector_index)
    else:
        report["retrieved_sources"] = retrieve(text, kb)
    report["retrieval_mode"] = "chroma_ollama" if vector_index else "lexical"
    report["rag"] = None
    if model:
        # Model candidates remain separately identified; never silently replace rule findings.
        report["rag"] = audit(text, report["retrieved_sources"], model)
    endpoints = json.loads(Path(inventory).read_text()) if inventory else []
    if len({e["asset_id"] for e in endpoints}) != len(endpoints):
        raise ValueError("duplicate inventory asset")
    by_asset = {e["asset_id"]: e for e in endpoints}
    probe_cache = {}
    for finding in report["findings"]:
        state = (
            "not_applicable"
            if finding["rule_id"] not in NETWORK_RULES
            else "not_tested"
        )
        evidence = None
        if finding["rule_id"] in NETWORK_RULES and finding["asset_id"] in by_asset:
            asset = finding["asset_id"]
            endpoint = by_asset[asset]
            if asset not in probe_cache:
                probe_cache[asset] = probe(
                    endpoint["host"],
                    endpoint["port"],
                    allowlist={(endpoint["host"], endpoint["port"])},
                    asset_id=asset,
                )
            evidence = probe_cache[asset]
            state = evidence["outcome"]
        finding["probe"] = evidence
        finding["priority"] = score(
            finding["static_score"], criticality=0.5, exposure=state
        )
    report["inventory_sha256"] = (
        hashlib.sha256(Path(inventory).read_bytes()).hexdigest() if inventory else None
    )
    report["policy_notes"] = [
        "Inventory maps candidate assets to staging endpoints; it does not establish Internet reachability.",
        "Only network findings receive TCP evidence. Secrets and authorization findings cannot be refuted by TCP refusal.",
        "Asset criticality 0.5 and weights are illustrative, not calibrated.",
        "LLM candidates require human location/asset/entailment review before verification or scoring.",
    ]
    return report
