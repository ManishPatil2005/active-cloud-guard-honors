"""Synthetic vector envelopes must not replace the authoritative corpus."""

import copy
import json
from unittest.mock import MagicMock, patch

import pytest

from cloudguard.vector import retrieve_vector


DOCS = [dict(id="s1", title="Source", text="Trusted text", url="https://example.org")]


def envelope():
    return dict(
        ids=[["s1"]],
        metadatas=[[dict(source_json=json.dumps(DOCS[0]))]],
        distances=[[0.2]],
    )


def retrieve(result, k=3):
    col = MagicMock()
    col.count.return_value = 1
    col.query.return_value = result
    with (
        patch(
            "cloudguard.vector.collection",
            return_value=(col, copy.deepcopy(DOCS), "digest"),
        ),
        patch("cloudguard.vector.embed", return_value=[[1.0]]),
    ):
        return retrieve_vector("q", "kb", "index", k=k)


def test_valid_vector_result_retains_corpus_and_distance():
    assert retrieve(envelope()) == [
        dict(**DOCS[0], distance=0.2, corpus_sha256="digest")
    ]


@pytest.mark.parametrize(
    "field,value",
    [
        ("text", "Injected instruction"),
        ("url", "https://attacker.invalid"),
        ("id", "s2"),
        ("title", "Forged title"),
    ],
)
def test_changed_stored_source_rejected(field, value):
    result = envelope()
    source = dict(DOCS[0], **{field: value})
    result["metadatas"][0][0]["source_json"] = json.dumps(source)
    with pytest.raises(ValueError):
        retrieve(result)


@pytest.mark.parametrize(
    "field,value",
    [
        ("ids", [["unknown"]]),
        ("ids", [[]]),
        ("distances", [[]]),
        ("metadatas", [[]]),
        ("ids", [None]),
        ("distances", [[True]]),
        ("distances", [[float("nan")]]),
        ("distances", [[float("inf")]]),
        ("metadatas", [[{}]]),
        ("metadatas", [[dict(source_json=42)]]),
        ("metadatas", [[dict(source_json="{")]]),
    ],
)
def test_malformed_vector_rows_fail_closed(field, value):
    result = envelope()
    result[field] = value
    with pytest.raises(ValueError):
        retrieve(result)


@pytest.mark.parametrize("k", [True, 0, -1, 1.5, "3", 257])
def test_invalid_result_count_rejected_before_activity(k):
    with patch("cloudguard.vector.collection") as collection:
        with pytest.raises(ValueError):
            retrieve_vector("q", "kb", "index", k=k)
    collection.assert_not_called()


def test_oversize_stored_source_rejected():
    result = envelope()
    result["metadatas"][0][0]["source_json"] = " " * 1_000_001
    with pytest.raises(ValueError):
        retrieve(result)


def test_duplicate_json_fields_rejected():
    result = envelope()
    result["metadatas"][0][0]["source_json"] = (
        json.dumps(DOCS[0])[:-1] + ', "id": "s1"}'
    )
    with pytest.raises(ValueError):
        retrieve(result)


@pytest.mark.parametrize(
    "result",
    [
        None,
        [],
        {},
        {"ids": [["s1"], ["s1"]]},
        dict(ids=[["s1"]], metadatas=[[{}]], distances=[[10**1000]]),
    ],
)
def test_invalid_envelope_or_extreme_distance(result):
    with pytest.raises(ValueError):
        retrieve(result)


def test_duplicate_result_ids_rejected():
    docs = DOCS + [dict(DOCS[0], id="s2")]
    result = envelope()
    for values in result.values():
        values[0] *= 2
    col = MagicMock()
    col.count.return_value = 2
    col.query.return_value = result
    with (
        patch("cloudguard.vector.collection", return_value=(col, docs, "digest")),
        patch("cloudguard.vector.embed", return_value=[[1.0]]),
    ):
        with pytest.raises(ValueError):
            retrieve_vector("q", "kb", "index", k=2)


@pytest.mark.parametrize("poison", [False, True])
def test_actual_embedded_query_corpus_boundary(poison):
    chromadb = pytest.importorskip("chromadb")
    from chromadb.config import Settings
    from uuid import uuid4

    client = chromadb.EphemeralClient(settings=Settings(anonymized_telemetry=False))
    col = client.create_collection("boundary-" + uuid4().hex, embedding_function=None)
    try:
        source = dict(DOCS[0], text="Injected") if poison else DOCS[0]
        col.add(
            ids=["s1"],
            embeddings=[[1.0, 0.0]],
            metadatas=[dict(source_json=json.dumps(source))],
        )
        with (
            patch("cloudguard.vector.collection", return_value=(col, DOCS, "digest")),
            patch("cloudguard.vector.embed", return_value=[[1.0, 0.0]]),
        ):
            if poison:
                with pytest.raises(ValueError, match="differs from current corpus"):
                    retrieve_vector("q", "kb", "index")
            else:
                assert retrieve_vector("q", "kb", "index")[0]["text"] == "Trusted text"
    finally:
        client.delete_collection(col.name)
