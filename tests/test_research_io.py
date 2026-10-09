import importlib.util
import io
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from cloudguard.evidence import evidence_main
from cloudguard import limits, llm, vector
from cloudguard.cache import AuditCache
from cloudguard.scanner import scan

ROOT = Path(__file__).resolve().parents[1]
RUNNERS = [
    "live_check",
    "integrated_check",
    "rag_check",
    "vector_check",
    "trivy_baseline",
    "capture_environment",
    "summarize",
]


def runner(name):
    spec = importlib.util.spec_from_file_location(
        name, ROOT / "scripts" / (name + ".py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("name", RUNNERS)
def test_legacy_runner_refuses_existing_before_collection(tmp_path, name):
    module = runner(name)
    original = tmp_path / "report"
    original.write_bytes(b"preserved negative")
    argv = [name, "--output", str(original)]
    if name == "live_check":
        argv += ["--pipeline-output", str(tmp_path / "new")]
    if name == "capture_environment":
        argv += ["--lock-output", str(tmp_path / "lock")]
    with patch("sys.argv", argv), patch.object(module, "collect") as collect:
        assert module.main() == 1
    collect.assert_not_called()
    assert original.read_bytes() == b"preserved negative"


@pytest.mark.parametrize("name", RUNNERS)
def test_legacy_runner_requires_outputs(tmp_path, name):
    module = runner(name)
    with patch("sys.argv", [name]), patch.object(module, "collect") as collect:
        with pytest.raises(SystemExit) as error:
            module.main()
    assert error.value.code == 2
    collect.assert_not_called()


@pytest.mark.parametrize("name", RUNNERS)
def test_legacy_runner_writes_fresh_report(tmp_path, name):
    module = runner(name)
    output = tmp_path / "report"
    argv = [name, "--output", str(output)]
    report = {
        "output": "historical summary" if name == "summarize" else {"observations": [1]}
    }
    if name == "live_check":
        argv += ["--pipeline-output", str(tmp_path / "pipeline")]
        report["pipeline-output"] = {"stage": "test"}
    if name == "capture_environment":
        argv += ["--lock-output", str(tmp_path / "lock")]
        report["lock-output"] = "pinned==1\n"
    with (
        patch("sys.argv", argv),
        patch.object(module, "collect", return_value=(report, 0)),
    ):
        assert module.main() == 0
    assert (
        output.read_text() == "historical summary"
        if name == "summarize"
        else json.loads(output.read_text()) == report["output"]
    )
    if name == "capture_environment":
        assert (tmp_path / "lock").read_text() == "pinned==1\n"


@pytest.mark.parametrize("failure", [RuntimeError, KeyboardInterrupt])
def test_failed_collection_retains_sanitized_fresh_receipt(tmp_path, failure):
    target = tmp_path / "report"

    def collect(args):
        raise failure("PRIVATE detail")

    with patch("sys.argv", ["runner", "--output", str(target)]):
        assert evidence_main(collect) == 1
    report = json.loads(target.read_text())
    assert report == {"status": "rejected", "error_type": failure.__name__}
    assert "PRIVATE" not in target.read_text()
    assert "actions_executed" not in report


def test_second_output_refusal_is_before_any_actions(tmp_path):
    original = tmp_path / "lock"
    original.write_bytes(b"keep")
    with patch(
        "sys.argv",
        ["r", "--output", str(tmp_path / "new"), "--lock-output", str(original)],
    ):
        with patch("builtins.print"), patch("cloudguard.evidence.json.dumps"):

            def collect(args):
                pytest.fail("must not collect")

            assert evidence_main(collect, outputs=("output", "lock-output")) == 1
    assert original.read_bytes() == b"keep"
    assert (tmp_path / "new").read_bytes() == b""


@pytest.mark.parametrize(
    "raw",
    [
        b'{"a":1,"a":2}',
        b'{"x":NaN}',
        b'{"x":Infinity}',
        b'{"x":1e999}',
        b"[" * 65 + b"0" + b"]" * 65,
    ],
)
def test_ambiguous_nonfinite_deep_json_refused(raw):
    with pytest.raises(ValueError):
        limits.json_value(raw)


def test_json_quoted_brackets_do_not_count_as_nesting():
    assert limits.json_value(json.dumps({"text": "[" * 100 + '\\"'})) == {
        "text": "[" * 100 + '\\"'
    }


def test_read_never_requests_unbounded_bytes():
    class Recorded(io.BytesIO):
        def read(self, count=-1):
            assert 1 <= count <= 11
            return super().read(count)

    with pytest.raises(ValueError):
        limits.read_stream(Recorded(b"x" * 100), 10)
    assert limits.read_stream(Recorded(b"x" * 10), 10) == b"x" * 10


def test_scanner_rejects_multibyte_byte_limit(tmp_path):
    path = tmp_path / "a.yaml"
    path.write_bytes(("#" + "é" * 500000).encode())
    with pytest.raises(ValueError, match="byte budget"):
        scan(path)


@pytest.mark.parametrize(
    "text", ["a: &a [*a]", "a: &a [1]\nb: *a", "a: " + "[" * 65 + "1" + "]" * 65]
)
def test_yaml_cycles_aliases_depth_rejected_before_model(tmp_path, text):
    path = tmp_path / "a.yaml"
    path.write_text(text)
    with pytest.raises(ValueError):
        scan(path)
    with patch.object(llm, "build_opener") as opener, pytest.raises(ValueError):
        llm.audit(text, [{"id": "s", "title": "t", "url": "u", "text": "x"}], "m")
    opener.assert_not_called()


@pytest.mark.parametrize("raw", [b"[]", b"{}", b'[{"id":"s"}]'])
def test_knowledge_schema_refused(tmp_path, raw):
    path = tmp_path / "kb"
    path.write_bytes(raw)
    with pytest.raises(ValueError):
        limits.knowledge(path)


@pytest.mark.parametrize(
    "vectors", [[], [[True]], [[float("nan")]], [[1], [1, 2]], [[1]]]
)
def test_invalid_embedding_vectors_refused(vectors):
    with patch.object(vector, "build_opener") as opener:
        opener.return_value.open.return_value = io.BytesIO(
            json.dumps({"embeddings": vectors}).encode()
        )
        with pytest.raises(ValueError):
            vector.embed(["first", "second"])


@pytest.mark.parametrize("texts", [[], [1], ["x" * 1000001], ["x"] * 257])
def test_bad_embedding_inputs_refuse_before_request(texts):
    with patch.object(vector, "build_opener") as opener, pytest.raises(ValueError):
        vector.embed(texts)
    opener.assert_not_called()


def test_oversized_identity_response_refused():
    with patch.object(llm, "build_opener") as opener:
        opener.return_value.open.return_value = io.BytesIO(b" " * 2000001)
        with pytest.raises(ValueError, match="byte budget"):
            llm.model_identity("m", 11434)


def test_nonfinite_cache_response_is_a_miss(tmp_path):
    key = "a" * 64
    (tmp_path / (key + ".json")).write_text('{"created_at":NaN}')
    assert AuditCache(tmp_path).get(key) is None


def test_universal_newlines_preserved(tmp_path):
    path = tmp_path / "text"
    path.write_bytes(b"a\r\nb\rc\n")
    assert limits.read_text(path) == "a\nb\nc\n"


def test_live_collector_retains_early_observations_on_pipeline_failure(tmp_path):
    module = runner("live_check")
    (tmp_path / "testbed").mkdir()
    (tmp_path / "testbed/inventory.json").write_text(
        '[{"host":"127.0.0.1","port":1234,"asset_id":"a"}]'
    )
    with (
        patch.object(module, "ROOT", tmp_path),
        patch.object(module, "probe", return_value={"outcome": "reachable"}),
        patch.object(module, "build_opener") as opener,
        patch.object(module, "run", side_effect=RuntimeError("PRIVATE")),
    ):
        opener.return_value.open.return_value.__enter__.return_value.status = 200
        reports, code = module.collect(None)
    assert code == 1
    assert reports["output"]["tcp"] == [{"outcome": "reachable"}]
    assert len(reports["output"]["http"]) == 2
    assert reports["pipeline-output"] == {
        "status": "rejected",
        "error_type": "RuntimeError",
    }


def test_integrated_collector_preserves_unsuccessful_report():
    module = runner("integrated_check")
    raw = {
        "retrieval_mode": "chroma_ollama",
        "rag": {"origin": "ollama_rag"},
        "findings": [],
    }
    with patch.object(module, "run", return_value=raw):
        reports, code = module.collect(None)
    assert code == 1 and reports["output"] is raw


def test_embedding_huge_integer_refused_with_value_error():
    with patch.object(vector, "build_opener") as opener:
        opener.return_value.open.return_value = io.BytesIO(
            json.dumps({"embeddings": [[10**500]]}).encode()
        )
        with pytest.raises(ValueError, match="numeric"):
            vector.embed(["one"])
