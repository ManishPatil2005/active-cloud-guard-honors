import json
from pathlib import Path
from unittest.mock import patch

import pytest
from cloudguard.cache import fingerprint
from cloudguard.pipeline import run
from cloudguard.verification import assess, file_hash, load_inventory, read_json

ROOT = Path(__file__).resolve().parents[1]
KB = ROOT / "knowledge/sources.json"
CANDIDATE = dict(
    asset_id="model-alias",
    title="Published service",
    location="/services/redis/ports/0",
    score=0.6,
    source_ids=["docker-ports"],
    grounding_status="requires_human_entailment_review",
)
RAG = dict(
    output={"findings": [CANDIDATE]},
    request_sha256="a" * 64,
    model_digest="model-identity",
)


def setup_context(tmp_path):
    source = tmp_path / "input.yaml"
    source.write_bytes((ROOT / "data/development/redis-all.yaml").read_bytes())
    inventory = tmp_path / "inventory.json"
    inventory.write_text(
        json.dumps([dict(asset_id="compose/redis", host="127.0.0.1", port=16379)])
    )
    binding = dict(
        version="1.0",
        configuration_sha256=file_hash(source),
        inventory_sha256=file_hash(inventory),
        reviewed_by="synthetic-test-reviewer",
    )
    policy = dict(
        **binding,
        rationale="test only",
        assets=[
            dict(
                asset_id="compose/redis",
                expected_reachability="forbidden",
                relationship="analogue",
            )
        ],
    )
    review = dict(
        **binding,
        audit_request_sha256=RAG["request_sha256"],
        approvals=[
            dict(
                candidate_sha256=fingerprint(CANDIDATE),
                inventory_asset_id="compose/redis",
                verification_scope="tcp_reachability_only",
                rationale="test only",
            )
        ],
    )
    pp, rp = tmp_path / "policy.json", tmp_path / "review.json"
    pp.write_text(json.dumps(policy))
    rp.write_text(json.dumps(review))
    return source, inventory, pp, rp


@pytest.mark.parametrize(
    "expected,outcome,status",
    [
        ("allowed", "reachable", "expected_reachability"),
        ("forbidden", "reachable", "unexpected_reachability"),
        ("allowed", "unreachable", "not_observed_from_this_vantage"),
        ("forbidden", "unreachable", "not_observed_from_this_vantage"),
        ("forbidden", "inconclusive", "inconclusive"),
        ("allowed", None, "not_tested"),
    ],
)
def test_policy_matrix(expected, outcome, status):
    result = assess(dict(expected_reachability=expected), dict(outcome=outcome))
    assert result["status"] == status
    assert not result["vulnerability_confirmed"] and not result["finding_suppressed"]
    assert not result["deployment_equivalence_verified"]


def test_reviewed_candidate_receives_evidence_not_score(tmp_path):
    source, inventory, policy, review = setup_context(tmp_path)
    with (
        patch("cloudguard.pipeline.audit", return_value=RAG),
        patch(
            "cloudguard.pipeline.probe", return_value={"outcome": "reachable"}
        ) as probe,
    ):
        for _ in range(2):
            report = run(
                source, KB, inventory, model="test", policy=policy, reviews=review
            )
    assert probe.call_count == 2  # Dedup within run, never across runs.
    result = report["model_verifications"][0]
    assert result["verification"]["status"] == "unexpected_reachability"
    assert result["priority"] is None and result["review_required"]
    assert result["candidate_sha256"] == report["model_candidate_ids"][0]


@pytest.mark.parametrize(
    "change",
    [
        "configuration",
        "inventory",
        "request",
        "candidate",
        "rejected",
        "duplicate",
        "asset",
        "scope",
        "digest",
    ],
)
def test_changed_review_fails_before_probes(tmp_path, change):
    source, inventory, policy, review = setup_context(tmp_path)
    document = json.loads(review.read_text())
    rag = json.loads(json.dumps(RAG))
    if change == "configuration":
        source.write_text(source.read_text() + "\n")
    elif change == "inventory":
        inventory.write_text(inventory.read_text() + "\n")
    elif change == "request":
        document["audit_request_sha256"] = "b" * 64
    elif change == "candidate":
        rag["output"]["findings"][0]["title"] = "Changed claim"
    elif change == "rejected":
        rag["output"]["findings"] = []
    elif change == "duplicate":
        document["approvals"] *= 2
    elif change == "asset":
        document["approvals"][0]["inventory_asset_id"] = "unknown"
    elif change == "scope":
        document["approvals"][0]["verification_scope"] = "execute_command"
    elif change == "digest":
        rag["model_digest"] = None
    review.write_text(json.dumps(document))
    with (
        patch("cloudguard.pipeline.audit", return_value=rag),
        patch("cloudguard.pipeline.probe") as probe,
    ):
        with pytest.raises(ValueError):
            run(source, KB, inventory, model="test", policy=policy, reviews=review)
    probe.assert_not_called()


def test_model_without_approval_cannot_select_endpoint(tmp_path):
    source, inventory, policy, _ = setup_context(tmp_path)
    # Use a model-only candidate: no rule finding exists in this input.
    source.write_text("services: {redis: {image: 'redis:7'}}")
    with (
        patch("cloudguard.pipeline.audit", return_value=RAG),
        patch("cloudguard.pipeline.probe") as probe,
    ):
        result = run(source, KB, inventory, model="test")
    probe.assert_not_called()
    assert result["model_verifications"] == []


@pytest.mark.parametrize(
    "host,port",
    [("example.com", 80), ("8.8.8.8", 53), ("127.0.0.1", True), ("127.0.0.1", 0)],
)
def test_inventory_scope_validated_before_inference(tmp_path, host, port):
    source, inventory, _, _ = setup_context(tmp_path)
    inventory.write_text(json.dumps([dict(asset_id="a", host=host, port=port)]))
    with patch("cloudguard.pipeline.audit") as audit:
        with pytest.raises(ValueError):
            run(source, KB, inventory, model="test")
    audit.assert_not_called()


def test_duplicate_json_keys_rejected(tmp_path):
    path = tmp_path / "duplicate.json"
    path.write_text('{"assets": [], "assets": []}')
    with pytest.raises(ValueError):
        read_json(path)


def test_legacy_mapping_explicitly_unverified(tmp_path):
    source, inventory, _, _ = setup_context(tmp_path)
    with patch("cloudguard.pipeline.probe", return_value={"outcome": "reachable"}):
        result = run(source, KB, inventory)
    assert result["findings"][0]["verification"]["status"] == "policy_missing"
    assert not result["findings"][0]["verification"]["deployment_equivalence_verified"]


def test_secret_not_cleared_by_policy(tmp_path):
    source, inventory, policy, _ = setup_context(tmp_path)
    source.write_bytes((ROOT / "data/development/postgres-secret.yaml").read_bytes())
    doc = json.loads(policy.read_text())
    doc["configuration_sha256"] = file_hash(source)
    policy.write_text(json.dumps(doc))
    with patch("cloudguard.pipeline.probe") as probe:
        result = run(source, KB, inventory, policy=policy)
    probe.assert_not_called()
    assert result["findings"][0]["verification"]["status"] == "not_applicable"


def test_unknown_policy_asset_rejected(tmp_path):
    source, inventory, policy, _ = setup_context(tmp_path)
    doc = json.loads(policy.read_text())
    doc["assets"][0]["asset_id"] = "unknown"
    policy.write_text(json.dumps(doc))
    with pytest.raises(ValueError):
        run(source, KB, inventory, policy=policy)


def test_missing_inventory_is_empty(tmp_path):
    assert load_inventory(None) == ({}, None)
    path = tmp_path / "float-port.json"
    path.write_text(json.dumps([dict(asset_id="a", host="127.0.0.1", port=16379.0)]))
    with pytest.raises(ValueError):
        load_inventory(path)


def test_approved_model_only_candidate_gets_probe(tmp_path):
    source, inventory, policy, review = setup_context(tmp_path)
    source.write_text('services: {redis: {ports: ["127.0.0.1:123:123"]}}')
    for path in (policy, review):
        doc = json.loads(path.read_text())
        doc["configuration_sha256"] = file_hash(source)
        path.write_text(json.dumps(doc))
    with (
        patch("cloudguard.pipeline.audit", return_value=RAG),
        patch(
            "cloudguard.pipeline.probe", return_value={"outcome": "reachable"}
        ) as probe,
    ):
        result = run(source, KB, inventory, model="test", policy=policy, reviews=review)
    assert result["findings"] == []
    assert len(result["model_verifications"]) == 1
    probe.assert_called_once()


def test_review_requires_policy(tmp_path):
    source, inventory, _, review = setup_context(tmp_path)
    with (
        patch("cloudguard.pipeline.audit", return_value=RAG),
        patch("cloudguard.pipeline.probe") as probe,
    ):
        with pytest.raises(ValueError):
            run(source, KB, inventory, model="test", reviews=review)
    probe.assert_not_called()


def test_source_changed_during_inference_fails_before_probe(tmp_path):
    source, inventory, policy, review = setup_context(tmp_path)

    def changed(*args, **kwargs):
        source.write_text(source.read_text() + "\n")
        return RAG

    with (
        patch("cloudguard.pipeline.audit", side_effect=changed),
        patch("cloudguard.pipeline.probe") as probe,
    ):
        with pytest.raises(ValueError, match="configuration changed"):
            run(source, KB, inventory, model="test", policy=policy, reviews=review)
    probe.assert_not_called()


def test_duplicate_policy_asset_rejected(tmp_path):
    source, inventory, policy, _ = setup_context(tmp_path)
    doc = json.loads(policy.read_text())
    doc["assets"] *= 2
    policy.write_text(json.dumps(doc))
    with pytest.raises(ValueError):
        run(source, KB, inventory, policy=policy)
