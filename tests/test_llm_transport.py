import io
import json
from unittest.mock import patch
import pytest
from cloudguard.llm import audit, InvalidModelOutput, input_locations

SOURCES = [
    dict(
        id="s1",
        title="Source",
        url="https://example.org",
        text="Evidence",
        relevance=7.4,
    )
]


def test_real_adapter_body_does_not_expose_retrieval_score():
    response = io.BytesIO(
        json.dumps({"message": {"content": '{"findings":[]}'}}).encode()
    )
    with patch("cloudguard.llm.build_opener") as opener:
        opener.return_value.open.return_value = response
        result = audit("services: {app: {image: redis}}", SOURCES, "test-model")
        request = opener.return_value.open.call_args.args[0]
        body = json.loads(request.data)
    evidence = json.loads(body["messages"][1]["content"])["evidence"]
    assert "relevance" not in evidence[0]
    assert result["output"] == {"findings": []}
    assert body["options"]["temperature"] == 0


def test_invalid_model_output_is_preserved_and_rejected():
    raw = '{"findings":[{"asset_id":"a","title":"t","location":"x","score":7,"source_ids":["s1"]}]}'
    response = io.BytesIO(json.dumps({"message": {"content": raw}}).encode())
    with patch("cloudguard.llm.build_opener") as opener:
        opener.return_value.open.return_value = response
        with pytest.raises(InvalidModelOutput) as caught:
            audit("services: {app: {image: redis}}", SOURCES, "test-model")
    assert caught.value.raw_output == raw


def test_no_evidence_fails_before_network():
    with patch("cloudguard.llm.build_opener") as opener:
        with pytest.raises(ValueError):
            audit("services: {}", [], "test-model")
    opener.assert_not_called()


def test_input_paths_are_exact_and_escape_keys():
    assert input_locations('services: {app: {image: redis, ports: ["80:80"]}}') == {
        "/services/app/image": "redis",
        "/services/app/ports/0": "80:80",
    }
    assert input_locations('"a/b": 1') == {"/a~1b": 1}


def test_hallucinated_location_is_not_accepted():
    value = {
        "findings": [
            dict(
                asset_id="app",
                title="Invented field",
                location="/services/app/security_groups",
                score=0.7,
                source_ids=["s1"],
            )
        ]
    }
    response = io.BytesIO(
        json.dumps({"message": {"content": json.dumps(value)}}).encode()
    )
    with patch("cloudguard.llm.build_opener") as opener:
        opener.return_value.open.return_value = response
        result = audit("services: {app: {image: redis}}", SOURCES, "test-model")
    assert result["output"]["findings"] == []
    assert result["abstained"] and len(result["rejected_findings"]) == 1
