import hashlib
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from cloudguard.legacy_io import InputBudget
from cloudguard.process_runner import BoundedProcessError, ProcessResult
from cloudguard.evidence import evidence_main
from test_legacy_budget_regression import load_runner


def test_aggregate_budget_refuses_second_file(tmp_path):
    path = tmp_path / "data"
    path.write_bytes(b"123456")
    budget = InputBudget(total=10)
    assert budget.bytes(path) == b"123456"
    with pytest.raises(ValueError, match="byte budget"):
        budget.bytes(path)


def test_hash_budget_streams_same_digest_and_refuses_oversize(tmp_path):
    path = tmp_path / "data"
    raw = b"a" * 70000
    path.write_bytes(raw)
    assert InputBudget().digest(path) == hashlib.sha256(raw).hexdigest()
    with pytest.raises(ValueError, match="hash byte"):
        InputBudget(total=10).digest(path)


def test_file_count_deadline_and_newlines(tmp_path):
    path = tmp_path / "data"
    path.write_bytes(b"a\r\nb\r")
    budget = InputBudget(files=1)
    assert budget.text(path) == "a\nb\n"
    with pytest.raises(ValueError, match="file count"):
        budget.bytes(path)
    with patch("cloudguard.legacy_io.time.monotonic", side_effect=[0, 2]):
        expired = InputBudget(seconds=1)
        with pytest.raises(ValueError, match="deadline"):
            expired.check()


@pytest.mark.parametrize(
    "text",
    [
        '<!DOCTYPE x [<!ENTITY a "boom">]><x>&a;</x>',
        '<!ENTITY a "boom"><x/>',
        "<x>" * 66 + "</x>" * 66,
    ],
)
def test_bad_xml_refused(tmp_path, text):
    path = tmp_path / "report.xml"
    path.write_text(text)
    with pytest.raises(ValueError):
        InputBudget().xml(path)


@pytest.mark.parametrize("limit", [-1, 0, True, 8000001])
def test_read_limit_refused_before_file_open(limit):
    with pytest.raises(ValueError, match="limit"):
        InputBudget().bytes("missing", limit)


def test_trivy_keeps_prior_rows_and_marks_not_attempted(tmp_path):
    module = load_runner("trivy_baseline")
    (tmp_path / "data").mkdir()
    (tmp_path / "data/labels.json").write_text(
        '[{"id":"a.tf"},{"id":"b.tf"},{"id":"c.tf"},{"id":"redis.yaml"}]'
    )
    failure = BoundedProcessError(
        "timeout", b"prefix", b"stderr", reaped=True, pipes_closed=True
    )
    with (
        patch.object(module, "ROOT", tmp_path),
        patch.object(
            module,
            "run_bounded",
            side_effect=[ProcessResult(0, '{"Results":[]}', ""), failure],
        ) as run,
    ):
        outputs, code = module.collect(None)
    report = outputs["output"]
    assert code == 1 and run.call_count == 2
    assert report["cases"][0]["result"] == {"Results": []}
    assert report["cases"][1]["stdout_prefix"] == "prefix"
    assert report["not_attempted"] == ["c.tf"] and report["excluded"] == ["redis.yaml"]
    assert report["cases"][1]["process_diagnostic"]["direct_child_reaped"]
    assert not report["cases"][1]["process_diagnostic"][
        "external_job_completion_verified"
    ]


@pytest.mark.parametrize("name", ["../x.tf", "nested/x.tf", "a\\b.tf", "-x.tf"])
def test_trivy_bad_manifest_before_launch(tmp_path, name):
    import json

    module = load_runner("trivy_baseline")
    (tmp_path / "data").mkdir()
    (tmp_path / "data/labels.json").write_text(json.dumps([{"id": name}]))
    with (
        patch.object(module, "ROOT", tmp_path),
        patch.object(module, "run_bounded") as run,
        pytest.raises(ValueError),
    ):
        module.collect(None)
    run.assert_not_called()


def test_environment_failure_keeps_prior_digests_and_rejects_lock(tmp_path):
    module = load_runner("capture_environment")
    with (
        patch.object(module, "ROOT", tmp_path),
        patch.object(
            module,
            "run_bounded",
            side_effect=[
                ProcessResult(0, '["digest"]', ""),
                BoundedProcessError("timeout", reaped=True, pipes_closed=True),
            ],
        ),
    ):
        outputs, code = module.collect(None)
    assert code == 1 and len(outputs["output"]["image_digests"]) == 1
    assert outputs["output"]["status"] == "rejected"
    assert '"status": "rejected"' in outputs["lock-output"]


def test_environment_success_uses_bounded_commands_and_portable_source(tmp_path):
    module = load_runner("capture_environment")
    (tmp_path / "docs/source").mkdir(parents=True)
    (tmp_path / "docs/source/Honors_Research_1st_Monitoring_Deck.pdf").write_bytes(
        b"synthetic"
    )
    with (
        patch.object(module, "ROOT", tmp_path),
        patch.object(
            module, "run_bounded", return_value=ProcessResult(0, "[]", "")
        ) as run,
        patch.object(
            module.importlib.metadata,
            "distributions",
            return_value=[SimpleNamespace(metadata={"Name": "demo"}, version="1.0")],
        ),
        patch.object(module, "build_opener") as opener,
    ):
        opener.return_value.open.return_value.__enter__.return_value.read.return_value = b'{"models":[]}'
        outputs, code = module.collect(None)
    assert code == 0 and outputs["lock-output"] == "demo==1.0\n"
    assert (
        outputs["output"]["source_pdf_sha256"]
        == hashlib.sha256(b"synthetic").hexdigest()
    )
    assert run.call_count == 7 and all(
        c.kwargs["timeout"] <= 30 and c.kwargs["output_limit"] == 128000
        for c in run.call_args_list
    )


@pytest.mark.parametrize(
    "options",
    [
        {"total": True},
        {"total": 0},
        {"files": 0},
        {"files": 4097},
        {"seconds": float("nan")},
        {"seconds": 601},
    ],
)
def test_bad_input_budgets_refused(options):
    with pytest.raises(ValueError):
        InputBudget(**options)


def test_publication_limit_saves_rejected_receipt_not_huge_body(tmp_path):
    import json

    output = tmp_path / "report"

    def collect(args):
        return {"output": "x" * 8000001}, 0

    with patch("sys.argv", ["runner", "--output", str(output)]):
        assert evidence_main(collect, text_outputs=("output",)) == 1
    assert json.loads(output.read_text()) == {
        "status": "rejected",
        "error_type": "ValueError",
    }


def test_environment_oversized_selected_source_retains_partial_metadata(tmp_path):
    module = load_runner("capture_environment")
    (tmp_path / "cloudguard").mkdir()
    (tmp_path / "cloudguard/oversized.py").write_bytes(b"x" * 8000001)
    with (
        patch.object(module, "ROOT", tmp_path),
        patch.object(
            module, "run_bounded", return_value=ProcessResult(0, "[]", "")
        ) as run,
        patch.object(module.importlib.metadata, "distributions", return_value=[]),
        patch.object(module, "build_opener") as opener,
    ):
        opener.return_value.open.return_value.__enter__.return_value.read.return_value = b'{"models":[]}'
        outputs, code = module.collect(None)
    assert code == 1 and run.call_count == 6
    assert len(outputs["output"]["image_digests"]) == 6
    assert (
        outputs["output"]["file_hashes"] == {}
        and outputs["output"]["status"] == "rejected"
    )
