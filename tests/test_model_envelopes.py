import io
import json
from unittest.mock import patch, MagicMock
from types import SimpleNamespace

import pytest

from cloudguard import llm, vector

TEXT = "services: {a: {image: redis}}"
SOURCES = [dict(id="s", title="t", url="https://example.invalid", text="evidence")]


@pytest.mark.parametrize(
    "payload",
    [None, [], {}, {"message": None}, {"message": {}}, {"message": {"content": 3}}],
)
def test_malformed_chat_is_owned_rejection(payload):
    with patch.object(llm, "build_opener") as opener:
        opener.return_value.open.return_value = io.BytesIO(json.dumps(payload).encode())
        with pytest.raises(llm.InvalidModelOutput):
            llm.audit(TEXT, SOURCES, "m")


@pytest.mark.parametrize(
    "fields",
    [
        {"done": "false"},
        {"done": 1},
        {"done_reason": None},
        {"done_reason": []},
        {"done_reason": "x" * 65},
        {"total_duration": -1},
        {"eval_count": True},
        {"prompt_eval_count": 1.2},
        {"load_duration": "PRIVATE"},
        {"eval_duration": 2**63},
    ],
)
def test_invalid_metadata_refused_and_not_cached(tmp_path, fields):
    content = '{"findings":[]}'
    with (
        patch.object(llm, "model_identity", return_value="d"),
        patch.object(llm, "build_opener") as opener,
        patch.object(llm.AuditCache, "put") as save,
    ):
        opener.return_value.open.return_value = io.BytesIO(
            json.dumps(dict(message={"content": content}, **fields)).encode()
        )
        with pytest.raises(llm.InvalidModelEnvelope) as error:
            llm.audit(TEXT, SOURCES, "m", cache_dir=tmp_path)
    assert error.value.raw_output == content
    assert error.value.code in {"completion_metadata", "inference_metadata"}
    assert "PRIVATE" not in str(error.value) and content not in str(error.value)
    save.assert_not_called()


@pytest.mark.parametrize("content", [None, {}, [], 3, True, ""])
def test_unusable_content_never_retained_as_model_string(content):
    with pytest.raises(llm.InvalidModelEnvelope) as error:
        llm.chat_content({"message": {"content": content}})
    assert error.value.raw_output is None and error.value.code == "content_required"


@pytest.mark.parametrize(
    "raw",
    [b"PRIVATE invalid json", b'{"message":NaN}', b"{}" + b" " * 2000000],
    ids=["invalid-json", "nonfinite-json", "oversized-json"],
)
def test_bad_json_or_budget_owned_rejection(raw):
    with patch.object(llm, "build_opener") as opener:
        opener.return_value.open.return_value = io.BytesIO(raw)
        with pytest.raises(llm.InvalidModelEnvelope) as error:
            llm.audit(TEXT, SOURCES, "m")
    assert error.value.code == "invalid_json_or_budget"
    assert error.value.raw_output is None and "PRIVATE" not in str(error.value)


@pytest.mark.parametrize(
    "cached",
    [
        [],
        {},
        {"message": None},
        {"message": {"content": "{}"}},
        {"message": {"content": '{"findings":[]}'}, "done": "false"},
    ],
)
def test_malformed_cache_requests_fresh_model_instead_of_clean_fallback(
    tmp_path, cached
):
    with (
        patch.object(llm, "model_identity", return_value="d"),
        patch.object(llm.AuditCache, "get", return_value=cached),
        patch.object(llm.AuditCache, "put") as save,
        patch.object(llm, "build_opener") as opener,
    ):
        opener.return_value.open.return_value = io.BytesIO(
            b'{"message":{"content":"{\\"findings\\":[]}"}}'
        )
        result = llm.audit(TEXT, SOURCES, "m", cache_dir=tmp_path)
    assert result["inference_performed"] and result["cache_status"] == "miss"
    assert opener.return_value.open.call_count == 1
    save.assert_called_once()


def test_owned_diagnostic_rejects_unknown_codes():
    with pytest.raises(ValueError):
        llm.InvalidModelEnvelope(None, "PRIVATE unknown")


def test_valid_optional_completion_and_counts_retained():
    payload = {
        "message": {"content": '{"findings":[]}'},
        "done": True,
        "done_reason": "stop",
        "total_duration": 123,
        "eval_count": 0,
        "prompt_eval_count": 2,
    }
    with patch.object(llm, "build_opener") as opener:
        opener.return_value.open.return_value = io.BytesIO(json.dumps(payload).encode())
        result = llm.audit(TEXT, SOURCES, "m")
    assert result["total_duration_ns"] == 123 and result["generation_tokens"] == 0
    assert result["prompt_eval_count"] == 2 and result["output"] == {"findings": []}


@pytest.mark.parametrize("fields", [{"done": False}, {"done_reason": "length"}])
def test_incomplete_generation_preserves_content(fields):
    content = "PRIVATE incomplete"
    with pytest.raises(llm.InvalidModelOutput) as error:
        llm.chat_content(dict(message={"content": content}, **fields))
    assert error.value.raw_output == content
    assert "PRIVATE" not in str(error.value)


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        {},
        {"models": None},
        {"models": {}},
        {"models": [None]},
        {"models": [{"name": "m:latest"}]},
        {"models": [{"name": "m:latest", "digest": []}]},
        {"models": [{"name": "m:latest", "digest": ""}]},
    ],
)
def test_bad_metadata_envelopes_are_explicit_value_error(payload):
    with pytest.raises(ValueError, match="invalid model metadata"):
        llm.identity_from_models(payload, "m")


@pytest.mark.parametrize(
    "models",
    [[], [{"name": "other", "digest": "d"}], [{"name": "m:latest", "digest": "d"}] * 2],
)
def test_missing_or_ambiguous_metadata_not_identity(models):
    with pytest.raises(ValueError, match="identity unavailable"):
        llm.identity_from_models({"models": models}, "m")


def test_valid_metadata_keeps_original_model_digest():
    assert (
        llm.identity_from_models(
            {"models": [{"name": "m:latest", "digest": "d", "size": 1}]}, "m"
        )
        == "d"
    )


def test_vector_metadata_refuses_before_persistent_client():
    client = MagicMock()
    with (
        patch.dict(
            "sys.modules",
            {
                "chromadb": SimpleNamespace(PersistentClient=client),
                "chromadb.config": SimpleNamespace(Settings=MagicMock()),
            },
        ),
        patch.object(vector, "knowledge", return_value=(b"[]", [])),
        patch.object(vector, "build_opener") as opener,
    ):
        opener.return_value.open.return_value = io.BytesIO(b'{"models":null}')
        with pytest.raises(ValueError, match="metadata"):
            vector.collection("kb", "index", "m")
    client.assert_not_called()


@pytest.mark.parametrize("payload", [None, [], {}, {"error": "PRIVATE"}])
def test_embedding_envelope_is_explicit_rejection(payload):
    with patch.object(vector, "build_opener") as opener:
        opener.return_value.open.return_value = io.BytesIO(json.dumps(payload).encode())
        with pytest.raises(ValueError, match="embedding response envelope") as error:
            vector.embed(["one"])
    assert "PRIVATE" not in str(error.value)
