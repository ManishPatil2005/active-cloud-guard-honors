import copy
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

import pytest

from cloudguard import integration, pipeline
from cloudguard.cache import fingerprint
from cloudguard.runtime import analyze
from cloudguard.verification import file_hash

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "data/integration/redis-auth-only.yaml"
NETWORK_CONFIG = ROOT / "data/development/redis-all.yaml"
BASELINE = ROOT / "data/runtime/baseline-synthetic.json"
OBSERVATION = ROOT / "data/runtime/observation-synthetic.json"
INVENTORY = ROOT / "testbed/inventory.json"
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
    model_digest="synthetic-test-model",
    rejected_findings=[{"reason": "synthetic-rejection"}],
)


def replay(config=CONFIG, **options):
    return integration.replay(
        config,
        [BASELINE],
        OBSERVATION,
        INVENTORY,
        engine1_pipeline=True,
        kb=KB,
        **options,
    )


def redis(result):
    return next(a for a in result["asset_contexts"] if a["asset_id"] == "compose/redis")


def test_actual_pipeline_retrieval_and_priority_with_saved_runtime():
    with (
        patch("cloudguard.pipeline.probe") as probe,
        patch("cloudguard.pipeline.audit") as audit,
    ):
        result = replay()
    probe.assert_not_called()
    audit.assert_not_called()
    assert result["protocol"] == "integrated_engine1_pipeline_runtime_replay_v1"
    assert result["engine1"]["retrieval_mode"] == "lexical"
    assert result["engine1"]["retrieved_sources"]
    assert result["engine1"]["findings"][0]["rule_id"] == "AUTH002"
    assert result["engine1"]["findings"][0]["priority"]["runtime_observed"] is False
    assert result["engine1"]["findings"][0]["probe"] is None
    assert (
        result["engine1"]["findings"][0]["verification"]["status"] == "not_applicable"
    )
    assert result["engine2"] == analyze([BASELINE], OBSERVATION, INVENTORY)
    assert result["engine1"]["rag"] is None
    assert result["active_verification_asset_count"] == 0
    assert redis(result)["model_verification_indices"] == []
    assert redis(result)["combined_priority"] is None
    assert set(result["selected_implementation_sha256"]) == set(
        integration.SELECTED_SOURCES + integration.PIPELINE_SOURCES
    )
    assert result["input_sha256"]["knowledge"] == file_hash(KB)


def test_pipeline_default_preserves_historical_rule_report():
    result = integration.replay(NETWORK_CONFIG, [BASELINE], OBSERVATION, INVENTORY)
    historical = json.loads(
        (ROOT / "output/integration-synthetic-windows-20261007.json").read_text()
    )["result"]
    for report in (result, historical):
        report.pop("selected_implementation_sha256")
        report["engine1"].pop("file")
    assert result == historical


def test_model_and_probe_evidence_preserved_without_automatic_alias_mapping():
    with (
        patch("cloudguard.pipeline.audit", return_value=copy.deepcopy(RAG)) as model,
        patch(
            "cloudguard.pipeline.probe",
            return_value={"outcome": "unreachable", "observed_at": "synthetic-test"},
        ) as probe,
    ):
        result = replay(
            NETWORK_CONFIG,
            model="synthetic-model",
            cache_dir="unused-synthetic-cache",
            timeout=30,
            max_tokens=256,
        )
    assert model.call_args.kwargs == dict(
        cache_dir="unused-synthetic-cache", timeout=30, max_tokens=256
    )
    probe.assert_called_once()
    assert result["engine1"]["rag"] == RAG
    assert result["engine1"]["model_verifications"] == []
    assert result["engine1"]["model_candidate_ids"] == [fingerprint(CANDIDATE)]
    assert redis(result)["model_verification_indices"] == []
    assert result["engine1"]["findings"][0]["probe"]["outcome"] == "unreachable"
    assert (
        result["engine1"]["findings"][0]["verification"]["finding_suppressed"] is False
    )
    assert result["active_verification_asset_count"] == 1
    assert not any(a["asset_id"] == "model-alias" for a in result["asset_contexts"])


def contexts(tmp_path):
    binding = dict(
        version="1.0",
        configuration_sha256=file_hash(NETWORK_CONFIG),
        inventory_sha256=file_hash(INVENTORY),
        reviewed_by="synthetic-test-reviewer",
    )
    policy = dict(
        **binding,
        rationale="synthetic-test-only",
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
                rationale="synthetic-test-only",
            )
        ],
    )
    paths = tmp_path / "policy.json", tmp_path / "review.json"
    for path, document in zip(paths, (policy, review)):
        path.write_text(json.dumps(document), encoding="utf-8")
    return paths


def test_reviewed_candidate_joins_only_operator_inventory_mapping(tmp_path):
    policy, reviews = contexts(tmp_path)
    with (
        patch("cloudguard.pipeline.audit", return_value=copy.deepcopy(RAG)),
        patch(
            "cloudguard.pipeline.probe", return_value={"outcome": "reachable"}
        ) as probe,
    ):
        result = replay(
            NETWORK_CONFIG, model="synthetic-model", policy=policy, reviews=reviews
        )
    probe.assert_called_once()  # One asset's observation serves two evidence references.
    assert result["active_verification_asset_count"] == 1
    assert redis(result)["model_verification_indices"] == [0]
    verification = result["engine1"]["model_verifications"][0]
    assert verification["candidate"] == CANDIDATE
    assert verification["verification"]["status"] == "unexpected_reachability"
    assert verification["priority"] is None
    assert verification["review_required"] is True
    assert result["deployment_binding_verified"] is False
    assert result["joint_priority_calculated"] is False
    assert result["actions_executed"] == []
    assert result["input_sha256"]["policy"] == file_hash(policy)
    assert result["input_sha256"]["reviews"] == file_hash(reviews)


@pytest.mark.parametrize("field", ["configuration_sha256", "inventory_sha256"])
def test_stale_policy_stops_model_and_probes(tmp_path, field):
    policy, _ = contexts(tmp_path)
    document = json.loads(policy.read_text())
    document[field] = "0" * 64
    policy.write_text(json.dumps(document))
    with (
        patch("cloudguard.pipeline.audit") as model,
        patch("cloudguard.pipeline.probe") as probe,
    ):
        with pytest.raises(ValueError, match="stale"):
            replay(NETWORK_CONFIG, model="synthetic-model", policy=policy)
    model.assert_not_called()
    probe.assert_not_called()


def test_rejected_candidate_cannot_receive_operator_probe(tmp_path):
    policy, reviews = contexts(tmp_path)
    rag = copy.deepcopy(RAG)
    rag["output"]["findings"] = []
    with (
        patch("cloudguard.pipeline.audit", return_value=rag),
        patch("cloudguard.pipeline.probe") as probe,
    ):
        with pytest.raises(ValueError, match="rejected"):
            replay(
                NETWORK_CONFIG, model="synthetic-model", policy=policy, reviews=reviews
            )
    probe.assert_not_called()


def test_model_failure_propagates_without_clean_result_or_probe():
    with (
        patch(
            "cloudguard.pipeline.audit",
            side_effect=RuntimeError("synthetic-test-error"),
        ),
        patch("cloudguard.pipeline.probe") as probe,
    ):
        with pytest.raises(RuntimeError):
            replay(NETWORK_CONFIG, model="synthetic-model")
    probe.assert_not_called()


def test_invalid_runtime_is_rejected_before_pipeline(tmp_path):
    observation = tmp_path / "observation.json"
    document = json.loads(OBSERVATION.read_text())
    document["scenario_group"] = json.loads(BASELINE.read_text())["scenario_group"]
    observation.write_text(json.dumps(document))
    with patch("cloudguard.pipeline.run") as run:
        with pytest.raises(ValueError):
            integration.replay(
                CONFIG, [BASELINE], observation, INVENTORY, engine1_pipeline=True, kb=KB
            )
    run.assert_not_called()


@pytest.mark.parametrize("value", [None, 0, 1, "true"])
def test_pipeline_mode_requires_exact_boolean(value):
    with pytest.raises(ValueError, match="boolean"):
        integration.replay(
            CONFIG, [BASELINE], OBSERVATION, INVENTORY, engine1_pipeline=value
        )


@pytest.mark.parametrize(
    "options",
    [
        {"kb": KB},
        {"model": "x"},
        {"vector_index": "x"},
        {"cache_dir": "x"},
        {"policy": "x"},
        {"reviews": "x"},
        {"timeout": 30},
        {"max_tokens": 256},
    ],
)
def test_pipeline_options_cannot_be_silently_ignored(options):
    with pytest.raises(ValueError, match="explicit pipeline"):
        integration.replay(CONFIG, [BASELINE], OBSERVATION, INVENTORY, **options)


def test_pipeline_requires_corpus():
    with pytest.raises(ValueError, match="knowledge corpus"):
        integration.replay(
            CONFIG, [BASELINE], OBSERVATION, INVENTORY, engine1_pipeline=True
        )


def test_vector_path_is_delegated_to_existing_pipeline():
    with patch("cloudguard.vector.retrieve_vector", return_value=[]) as retrieve:
        result = replay(vector_index="synthetic-test-index")
    assert retrieve.call_args.args[1:] == (KB, "synthetic-test-index")
    assert result["engine1"]["retrieval_mode"] == "chroma_ollama"


@pytest.mark.parametrize("when", ["before", "after"])
def test_corpus_mutation_is_rejected(tmp_path, monkeypatch, when):
    kb = tmp_path / "sources.json"
    kb.write_bytes(KB.read_bytes())
    original = integration.analyze_runtime if when == "before" else pipeline.run

    def mutation(*args, **kwargs):
        result = original(*args, **kwargs)
        with kb.open("ab") as stream:
            stream.write(b"\n")
        return result

    monkeypatch.setattr(
        integration if when == "before" else pipeline,
        "analyze_runtime" if when == "before" else "run",
        mutation,
    )
    with pytest.raises(ValueError, match="input changed"):
        integration.replay(
            CONFIG, [BASELINE], OBSERVATION, INVENTORY, engine1_pipeline=True, kb=kb
        )


def test_selected_source_change_stops_pipeline_before_active_stages(monkeypatch):
    original = integration._digest
    calls = 0

    def digest(path):
        nonlocal calls
        value = original(path)
        if Path(path).name == "pipeline.py":
            calls += 1
            if calls == 2:
                return "0" * 64
        return value

    monkeypatch.setattr(integration, "_digest", digest)
    with patch("cloudguard.pipeline.run") as run:
        with pytest.raises(ValueError, match="implementation changed before"):
            replay()
    run.assert_not_called()


def test_pipeline_component_hash_mismatch_rejected(monkeypatch):
    original = pipeline.run

    def mismatch(*args, **kwargs):
        result = original(*args, **kwargs)
        result["configuration_bytes_sha256"] = "0" * 64
        return result

    monkeypatch.setattr(pipeline, "run", mismatch)
    with pytest.raises(ValueError, match="pipeline input mismatch"):
        replay()


def test_real_pipeline_cli_and_fixed_exclusive_example(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "cloudguard.cli",
            "integrated-replay",
            str(CONFIG),
            str(OBSERVATION),
            "--baseline",
            str(BASELINE),
            "--inventory",
            str(INVENTORY),
            "--engine1-pipeline",
            "--kb",
            str(KB),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0 and not result.stderr
    report = json.loads(result.stdout)
    assert report["engine1_pipeline_executed"] is True
    assert report["active_verification_asset_count"] == 0
    output = tmp_path / "demo.json"
    args = [
        sys.executable,
        str(ROOT / "scripts/integration_check.py"),
        "--engine1-pipeline",
        "--output",
        str(output),
    ]
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0 and not result.stderr
    original = output.read_bytes()
    assert all(json.loads(original)["checks"].values())
    assert len(json.loads(original)["checks"]) == 8
    assert (
        subprocess.run(args, cwd=ROOT, capture_output=True, timeout=30).returncode == 1
    )
    assert output.read_bytes() == original
    assert list(tmp_path.iterdir()) == [output]
