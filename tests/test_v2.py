import io
import json
from unittest.mock import MagicMock, patch

import pytest
from cloudguard.cache import AuditCache, fingerprint
from cloudguard.llm import audit, InvalidModelOutput
from cloudguard.pipeline import run
from cloudguard.vector import index
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    dict(
        id="postgres-trust",
        title="Trust",
        url="https://example.org",
        text="Trust requires no password",
        corpus_sha256="a",
    )
]
TEXT = "services: {app: {environment: {POSTGRES_HOST_AUTH_METHOD: trust}}}"


def response(content=None, **fields):
    return io.BytesIO(
        json.dumps(
            dict(message={"content": json.dumps(content or {"findings": []})}, **fields)
        ).encode()
    )


def test_cache_reuse_and_changed_input(tmp_path):
    with (
        patch("cloudguard.llm.model_identity", return_value="digest"),
        patch("cloudguard.llm.build_opener") as opener,
    ):
        opener.return_value.open.side_effect = [response(), response()]
        first = audit(TEXT, SOURCES, "model", cache_dir=tmp_path)
        second = audit(TEXT, SOURCES, "model", cache_dir=tmp_path)
        third = audit(TEXT + "\n", SOURCES, "model", cache_dir=tmp_path)
    assert [x["cache_status"] for x in (first, second, third)] == [
        "miss",
        "hit",
        "miss",
    ]
    assert not second["inference_performed"]
    assert opener.return_value.open.call_count == 2


@pytest.mark.parametrize("change", ["digest", "sources", "budget", "policy", "corpus"])
def test_context_changes_invalidate_cache(tmp_path, change):
    with (
        patch("cloudguard.llm.model_identity", return_value="first") as identity,
        patch("cloudguard.llm.build_opener") as opener,
    ):
        opener.return_value.open.side_effect = [response(), response()]
        audit(TEXT, SOURCES, "model", cache_dir=tmp_path)
        sources = [dict(SOURCES[0])]
        budget = 512
        if change == "digest":
            identity.return_value = "new"
        if change == "sources":
            sources[0]["text"] = "changed guidance"
        if change == "corpus":
            sources[0]["corpus_sha256"] = "b"
        if change == "budget":
            budget = 256
        with patch(
            "cloudguard.llm.POLICY_VERSION",
            "new" if change == "policy" else "engine1-v2-auth-guard-1",
        ):
            result = audit(
                TEXT, sources, "model", cache_dir=tmp_path, max_tokens=budget
            )
    assert result["cache_status"] == "miss"


def test_cache_expiry_integrity_and_capacity(tmp_path):
    cache = AuditCache(tmp_path, ttl=10, max_entries=2)
    keys = [fingerprint(i) for i in range(3)]
    with patch("cloudguard.cache.time.time", return_value=100):
        cache.put(keys[0], {"value": 1})
    with patch("cloudguard.cache.time.time", return_value=111):
        assert cache.get(keys[0]) is None
    cache.put(keys[1], {"value": 2})
    cache.put(keys[2], {"value": 3})
    assert len(list(tmp_path.glob("*.json"))) == 2
    entry = json.loads(cache.path(keys[2]).read_text())
    entry["response"] = {"value": 999}
    cache.path(keys[2]).write_text(json.dumps(entry))
    assert cache.get(keys[2]) is None
    with pytest.raises(ValueError):
        cache.path("../escape")


def test_cached_response_revalidated(tmp_path):
    with (
        patch("cloudguard.llm.model_identity", return_value="digest"),
        patch("cloudguard.llm.build_opener") as opener,
    ):
        opener.return_value.open.side_effect = [response(), response()]
        first = audit(TEXT, SOURCES, "model", cache_dir=tmp_path)
        AuditCache(tmp_path).put(
            first["request_sha256"], {"message": {"content": "{}"}}
        )
        second = audit(TEXT, SOURCES, "model", cache_dir=tmp_path)
    assert second["cache_status"] == "miss"


def test_rejected_candidate_remains_rejected_on_hit(tmp_path):
    finding = dict(
        asset_id="app",
        title="trust",
        location="/services/app/environment/POSTGRES_PASSWORD",
        score=0.6,
        source_ids=["postgres-trust"],
    )
    text = "services: {app: {environment: {POSTGRES_PASSWORD: '${PG_PASSWORD}'}}}"
    with (
        patch("cloudguard.llm.model_identity", return_value="digest"),
        patch("cloudguard.llm.build_opener") as opener,
    ):
        opener.return_value.open.return_value = response({"findings": [finding]})
        first = audit(text, SOURCES, "model", cache_dir=tmp_path)
        second = audit(text, SOURCES, "model", cache_dir=tmp_path)
    assert first["rejected_findings"] == second["rejected_findings"]
    assert second["abstained"] and not second["output"]["findings"]


@pytest.mark.parametrize("fields", [{"done_reason": "length"}, {"done": False}])
def test_truncated_response_not_cached(tmp_path, fields):
    with (
        patch("cloudguard.llm.model_identity", return_value="digest"),
        patch("cloudguard.llm.build_opener") as opener,
    ):
        opener.return_value.open.return_value = response(**fields)
        with pytest.raises(InvalidModelOutput):
            audit(TEXT, SOURCES, "model", cache_dir=tmp_path)
    assert not list(tmp_path.glob("*.json"))


@pytest.mark.parametrize(
    "kwargs",
    [
        {"max_tokens": 0},
        {"max_tokens": True},
        {"timeout": 0},
        {"timeout": float("nan")},
    ],
)
def test_invalid_budgets_fail_without_io(kwargs):
    with patch("cloudguard.llm.build_opener") as opener:
        with pytest.raises(ValueError):
            audit(TEXT, SOURCES, "model", **kwargs)
    opener.assert_not_called()


def test_model_change_mid_request_not_cached(tmp_path):
    with (
        patch("cloudguard.llm.model_identity", side_effect=["old", "new"]),
        patch("cloudguard.llm.build_opener") as opener,
    ):
        opener.return_value.open.return_value = response()
        with pytest.raises(InvalidModelOutput):
            audit(TEXT, SOURCES, "model", cache_dir=tmp_path)
    assert not list(tmp_path.glob("*.json"))


def test_cache_write_failure_keeps_valid_result(tmp_path):
    with (
        patch("cloudguard.llm.model_identity", return_value="digest"),
        patch("cloudguard.llm.build_opener") as opener,
        patch("cloudguard.llm.AuditCache.put", side_effect=OSError),
    ):
        opener.return_value.open.return_value = response()
        result = audit(TEXT, SOURCES, "model", cache_dir=tmp_path)
    assert result["cache_warning"] and result["output"] == {"findings": []}


def test_index_reuses_only_matching_ids():
    col = MagicMock()
    col.count.return_value = 1
    col.get.return_value = {"ids": ["a"]}
    col.metadata = {"embedding_digest": "d"}
    with (
        patch(
            "cloudguard.vector.collection",
            return_value=(col, [{"id": "a", "title": "t", "text": "x"}], "h"),
        ),
        patch("cloudguard.vector.embed", return_value=[[1, 0]]) as embed,
    ):
        assert index("kb", "db")["embedded_documents"] == 0
        embed.assert_not_called()
        assert index("kb", "db", force=True)["embedded_documents"] == 1
        col.get.return_value = {"ids": ["wrong"]}
        assert not index("kb", "db")["reused"]
        col.delete.assert_called_once_with(ids=["wrong"])


def test_probes_repeat_across_runs_even_if_audit_cached(tmp_path):
    inventory = tmp_path / "inventory.json"
    inventory.write_text(
        json.dumps([dict(asset_id="compose/redis", host="127.0.0.1", port=16379)])
    )
    with (
        patch("cloudguard.pipeline.audit", return_value={"cache_status": "hit"}),
        patch(
            "cloudguard.pipeline.probe", return_value={"outcome": "reachable"}
        ) as probe,
    ):
        for _ in range(2):
            report = run(
                ROOT / "data/development/redis-all.yaml",
                ROOT / "knowledge/sources.json",
                inventory,
                model="model",
                cache_dir=tmp_path,
            )
    assert probe.call_count == 2
    assert report["engine_version"] == "2.0" and report["timings_ms"]["total_ms"] >= 0
