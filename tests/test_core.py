import json
import socket
from pathlib import Path
from unittest.mock import patch
import pytest
from cloudguard.scanner import scan
from cloudguard.probe import probe
from cloudguard.scoring import score
from cloudguard.metrics import metrics, fp_reduction
from cloudguard.retrieval import retrieve
from cloudguard.llm import validate_output

ROOT = Path(__file__).resolve().parents[1]


def write(tmp_path, text, name="compose.yaml"):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


@pytest.mark.parametrize(
    "record", json.loads((ROOT / "data/labels.json").read_text()), ids=lambda r: r["id"]
)
def test_corpus(record):
    result = scan(ROOT / record["path"])
    assert (
        sorted(set(f["rule_id"] for f in result["findings"]))
        == record["expected_rules"]
    )


def test_duplicate_yaml_rejected(tmp_path):
    with pytest.raises(ValueError):
        scan(write(tmp_path, "services: {}\nservices: {}"))


def test_unsafe_yaml_rejected(tmp_path):
    with pytest.raises(Exception):
        scan(write(tmp_path, "!!python/object/apply:os.system [echo forbidden]"))


def test_multidocument_and_init_container(tmp_path):
    p = write(
        tmp_path,
        "kind: Pod\nmetadata: {name: x}\nspec:\n  initContainers:\n  - name: setup\n    securityContext: {privileged: true}\n---\nkind: Service\nspec: {type: NodePort}\n",
    )
    assert {f["rule_id"] for f in scan(p)["findings"]} == {"PRIV001", "NET002"}


def test_secrets_not_echoed(tmp_path):
    result = scan(
        write(
            tmp_path,
            "services:\n  app:\n    environment: {PASSWORD: never-print-this-value}",
        )
    )
    assert "never-print-this-value" not in json.dumps(result)


def test_unknown_yaml_warns(tmp_path):
    assert scan(write(tmp_path, "unknown: format"))["warnings"]


def test_unresolved_binding_rejected(tmp_path):
    with pytest.raises(ValueError):
        scan(write(tmp_path, 'services:\n  app:\n    ports: ["${BIND}:8000:80"]'))


def test_probe_local_live():
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        port = listener.getsockname()[1]
        assert (
            probe("127.0.0.1", port, allowlist={("127.0.0.1", port)})["outcome"]
            == "reachable"
        )


@pytest.mark.parametrize(
    "host,port,allow",
    [
        ("8.8.8.8", 80, {("8.8.8.8", 80)}),
        ("localhost", 80, {("localhost", 80)}),
        ("127.0.0.1", 80, set()),
    ],
)
def test_probe_scope(host, port, allow):
    with pytest.raises(ValueError):
        probe(host, port, allowlist=allow)


@pytest.mark.parametrize(
    "error,state",
    [
        (ConnectionRefusedError(), "unreachable"),
        (TimeoutError(), "inconclusive"),
        (OSError(), "inconclusive"),
    ],
)
def test_probe_errors(error, state):
    with patch("socket.create_connection", side_effect=error):
        assert (
            probe("127.0.0.1", 12345, allowlist={("127.0.0.1", 12345)})["outcome"]
            == state
        )


def test_score_monotonic():
    for i in range(101):
        baseline = score(i / 100, 0.5)["value"]
        assert score(i / 100, 0.5, "reachable")["value"] >= baseline
        assert score(i / 100, 0.5, "inconclusive")["value"] == baseline
        assert score(i / 100, 0.5, "unreachable")["value"] == baseline
        assert 0 <= baseline <= 1


@pytest.mark.parametrize("value", [-1, 2, float("nan"), float("inf"), True])
def test_bad_score(value):
    with pytest.raises(ValueError):
        score(value, 0.5)


def test_missing_runtime_is_distinct():
    assert not score(0.7, 0.5)["runtime_observed"]
    assert score(0.7, 0.5, anomaly=0)["runtime_observed"]


def test_metrics_and_empty_denominators():
    m = metrics(
        {"a": True, "b": True, "c": False, "d": False},
        {"a": True, "b": False, "c": True, "d": False},
    )
    assert (m["tp"], m["fp"], m["fn"], m["tn"], m["f1"]) == (1, 1, 1, 1, 0.5)
    assert metrics({}, {})["f1"] is None
    assert fp_reduction(0, 0) is None
    assert fp_reduction(10, 1) == 0.9
    with pytest.raises(ValueError):
        metrics({"a": True}, {})


def test_retrieval_citation_provenance():
    docs = retrieve("PostgreSQL trust authentication", ROOT / "knowledge/sources.json")
    assert docs[0]["id"] == "postgres-trust"
    assert len(docs[0]["corpus_sha256"]) == 64
    assert retrieve("zzzzunmatched", ROOT / "knowledge/sources.json") == []


def test_llm_unknown_citation_rejected():
    value = {
        "findings": [
            {
                "asset_id": "x",
                "title": "x",
                "location": "x",
                "score": 0.5,
                "source_ids": ["invented"],
            }
        ]
    }
    with pytest.raises(ValueError):
        validate_output(value, [{"id": "real"}])


def test_llm_invalid_shape_rejected():
    with pytest.raises(Exception):
        validate_output({"all_safe": True}, [])


def test_llm_empty_candidates_valid():
    assert validate_output({"findings": []}, []) == {"findings": []}
