import hashlib
import json
from unittest.mock import patch

import pytest

from cloudguard.process_runner import BoundedProcessError, ProcessResult
from scripts import vector_storage_check as module


def child(expected_phase, **changes):
    payload = {
        "phase": expected_phase,
        "stored_count": 2,
        "nearest_id": "synthetic-one",
        "deleted_collection": expected_phase == "read",
    }
    payload.update(changes)
    return ProcessResult(0, json.dumps(payload), "")


def run(tmp_path, results):
    with (
        patch.object(module, "ROOT", tmp_path),
        patch.object(module.importlib.metadata, "version", return_value="1.0.20"),
        patch.object(module, "run_bounded", side_effect=results) as process,
    ):
        reports, code = module.collect(None)
    return reports["output"], code, process


def test_two_separate_bounded_processes_and_no_security_authority(tmp_path):
    report, code, process = run(tmp_path, [child("write"), child("read")])
    assert code == 0 and report["cold_process_reopen_verified"] is True
    assert [row["status"] for row in report["steps"]] == ["passed", "passed"]
    assert process.call_count == 2
    for call, phase in zip(process.call_args_list, ["write", "read"], strict=True):
        args = call.args[0]
        assert args[1:4] == ["-I", "-c", module.CHILD] and args[4] == phase
        assert call.kwargs == {"timeout": 60, "output_limit": 100_000}
    assert (
        report["child_source_sha256"]
        == hashlib.sha256(module.CHILD.encode()).hexdigest()
    )
    assert report["store_directory"].startswith("tmp/vector-storage-")
    assert report["external_storage_parent_selected"] is False
    assert "ignored tmp" in report["limits"][-1]
    assert (tmp_path / report["store_directory"]).is_dir()
    for key in (
        "production_ready",
        "independent_evaluation",
        "server_security_verified",
        "network_isolation_verified",
    ):
        assert report[key] is False


@pytest.mark.parametrize(
    "changes",
    [
        {"stored_count": True},
        {"stored_count": 2.0},
        {"stored_count": 1},
        {"phase": "read"},
        {"nearest_id": "other"},
        {"deleted_collection": 0},
        {"deleted_collection": True},
        {"extra": "untrusted"},
    ],
)
def test_bad_first_report_refuses_reopen_and_preserves_state(tmp_path, changes):
    report, code, process = run(tmp_path, [child("write", **changes)])
    assert code == 1 and process.call_count == 1
    assert report["cold_process_reopen_verified"] is False
    assert [row["status"] for row in report["steps"]] == ["rejected", "not_attempted"]


@pytest.mark.parametrize(
    "result",
    [
        ProcessResult(1, "private details", "private failure"),
        ProcessResult(0, "{broken", ""),
        ProcessResult(0, '{"phase":"write","phase":"read"}', ""),
    ],
)
def test_nonzero_malformed_duplicate_reports_are_not_success(tmp_path, result):
    report, code, _ = run(tmp_path, [result])
    assert code == 1 and "private" not in json.dumps(report)
    assert report["steps"][1]["status"] == "not_attempted"


def test_second_process_timeout_preserves_first_phase_and_cleanup_diagnostic(tmp_path):
    fault = BoundedProcessError(
        "timeout", b"private stdout", b"private stderr", reaped=True, pipes_closed=True
    )
    report, code, _ = run(tmp_path, [child("write"), fault])
    assert code == 1
    assert report["steps"][0]["status"] == "passed"
    assert report["steps"][1]["diagnostic"] == fault.diagnostic
    assert report["cold_process_reopen_verified"] is False
    assert "private" not in json.dumps(report)


def test_wrong_version_refused_before_directory_or_child(tmp_path):
    with (
        patch.object(module, "ROOT", tmp_path),
        patch.object(module.importlib.metadata, "version", return_value="other"),
        patch.object(module, "run_bounded") as process,
    ):
        with pytest.raises(ValueError, match="unexpected"):
            module.collect(None)
    assert list(tmp_path.iterdir()) == []
    process.assert_not_called()


def test_existing_output_refused_before_version_or_directory(tmp_path):
    output = tmp_path / "negative.json"
    output.write_bytes(b"historical failed result")
    with (
        patch("sys.argv", ["storage", "--output", str(output)]),
        patch.object(module.importlib.metadata, "version") as version,
    ):
        assert module.evidence_main(module.collect) == 1
    version.assert_not_called()
    assert output.read_bytes() == b"historical failed result"


def test_explicit_native_parent_used_without_touching_repository(tmp_path):
    parent = tmp_path / "native"
    parent.mkdir()
    root = tmp_path / "repository"
    with (
        patch.object(module, "ROOT", root),
        patch.object(module.importlib.metadata, "version", return_value="1.0.20"),
        patch.object(
            module, "run_bounded", side_effect=[child("write"), child("read")]
        ) as process,
    ):
        reports, code = module.collect(None, storage_parent=parent)
    report = reports["output"]
    store = module.Path(report["store_directory"])
    assert code == 0 and store.parent == parent and store.is_dir()
    assert report["external_storage_parent_selected"] is True
    assert "external parent" in report["limits"][-1]
    assert not root.exists()
    assert all(call.args[0][-1] == str(store) for call in process.call_args_list)


@pytest.mark.parametrize("kind", ["missing", "file", "relative"])
def test_invalid_storage_parent_refused_before_child(tmp_path, kind):
    parent = tmp_path / "parent"
    if kind == "file":
        parent.write_text("not a directory")
    elif kind == "relative":
        parent = module.Path("relative-parent")
    with (
        patch.object(module.importlib.metadata, "version", return_value="1.0.20"),
        patch.object(module, "run_bounded") as process,
    ):
        with pytest.raises(ValueError, match="storage parent"):
            module.collect(None, storage_parent=parent)
    process.assert_not_called()


def test_external_parent_existing_output_refused_before_activity(tmp_path):
    output = tmp_path / "existing.json"
    output.write_bytes(b"negative result")
    with (
        patch("sys.argv", ["storage", "--output", str(output)]),
        patch.object(module, "collect") as collect,
    ):
        assert (
            module.evidence_main(lambda args: collect(args, storage_parent=tmp_path))
            == 1
        )
    collect.assert_not_called()
    assert output.read_bytes() == b"negative result"


def test_symlink_storage_parent_refused(tmp_path):
    target = tmp_path / "real"
    target.mkdir()
    link = tmp_path / "link"
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError:
        pytest.skip("symlink privilege unavailable")
    with (
        patch.object(module.importlib.metadata, "version", return_value="1.0.20"),
        patch.object(module, "run_bounded") as process,
    ):
        with pytest.raises(ValueError, match="storage parent"):
            module.collect(None, storage_parent=link)
    process.assert_not_called()
