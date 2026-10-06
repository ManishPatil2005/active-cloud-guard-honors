"""Coordinator unit indices, never independent reviews or blinded packets."""

import copy
import json
import subprocess
import sys

import pytest

from cloudguard import runtime_intake as intake
from test_runtime_intake import (
    ROOT,
    add_run,
    adjudication,
    edit_capture,
    make_bundle,
    review,
    save,
)


@pytest.fixture
def bundle(tmp_path):
    return make_bundle(tmp_path)


def index(bundle):
    root, manifest = bundle
    save(root, "manifest.json", manifest)
    return intake.annotation_index(root / "manifest.json")


def command(manifest, output):
    return subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/runtime_intake.py"),
            "--manifest",
            str(manifest),
            "--output",
            str(output),
            "--annotation-index",
        ],
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize(
    "manifest,report",
    [
        ("manifest.json", "engine2-intake-synthetic-20261006.json"),
        (
            "manifest-typed-counted.json",
            "engine2-typed-intake-counted-synthetic-20261006.json",
        ),
    ],
)
def test_default_reports_still_match_historical_bytes_as_json(manifest, report):
    result = intake.inspect(ROOT / "data/runtime/intake-example" / manifest)
    assert result == json.loads((ROOT / "output" / report).read_text())
    assert "observed_window_index" not in result


@pytest.mark.parametrize("option", [0, 1, None, "true", [], {}])
def test_index_option_requires_exact_boolean(bundle, option):
    with pytest.raises(ValueError, match="exact boolean"):
        intake.inspect(bundle[0] / "manifest.json", include_window_index=option)


def test_minimized_index_retains_no_votes_reasons_answers_or_splits(bundle):
    first = review(bundle, "private-reviewer-a", ("benign", "suspicious"))
    review(bundle, "private-reviewer-b", ("benign", "unknown"))
    adjudication(bundle, first)
    result = index(bundle)
    assert set(result) == {
        "protocol",
        "status",
        "manifest_sha256",
        "inventory_sha256",
        "guidelines_sha256",
        "window_seconds",
        "observed_window_count",
        "empty_capture_count",
        "missing_windows_not_materialized",
        "units",
        "labels_created",
        "supervisor_approval_verified",
        "blinding_verified",
        "independent_evaluation_verified",
        "model_fitting_authorized",
        "predictions_computed",
        "actions_executed",
        "limitations",
    }
    assert result["protocol"] == intake.ANNOTATION_PROTOCOL
    assert result["status"] == "observed_units_indexed"
    assert result["observed_window_count"] == len(result["units"]) == 2
    assert result["empty_capture_count"] == 0
    for row in result["units"]:
        assert set(row) == {"run_id", "asset_id", "start_epoch"}
        assert type(row["start_epoch"]) is int
    for field in (
        "labels_created",
        "supervisor_approval_verified",
        "blinding_verified",
        "independent_evaluation_verified",
        "model_fitting_authorized",
        "predictions_computed",
    ):
        assert result[field] is False
    assert result["actions_executed"] == []
    rendered = json.dumps(result)
    for private in (
        "private-reviewer",
        "private synthetic rationale",
        "benign",
        "suspicious",
        "template-a",
        "deployment-a",
        "family-a",
    ):
        assert private not in rendered


def test_unit_order_independent_of_manifest_and_event_order(bundle):
    add_run(bundle)
    before = index(bundle)
    edit_capture(bundle, lambda value: value["events"].reverse())
    bundle[1]["runs"].reverse()
    after = index(bundle)
    assert before["units"] == after["units"]
    assert len(after["units"]) == 4
    assert after["units"] == sorted(
        after["units"],
        key=lambda row: (row["run_id"], row["asset_id"], row["start_epoch"]),
    )
    assert before["manifest_sha256"] != after["manifest_sha256"]


def test_empty_capture_never_becomes_a_zero_or_benign_unit(bundle):
    edit_capture(bundle, lambda value: value.update(events=[]))
    result = index(bundle)
    assert result["units"] == []
    assert result["observed_window_count"] == 0
    assert result["empty_capture_count"] == 1
    assert result["missing_windows_not_materialized"] is True


@pytest.mark.parametrize("seconds", [1, 60, 3600])
def test_index_reuses_frozen_existing_window_keys(bundle, seconds):
    root, manifest = bundle
    manifest["window_seconds"] = seconds
    result = index(bundle)
    report = intake.inspect(root / "manifest.json", include_window_index=True)
    assert result["units"] == report["observed_window_index"]
    assert result["window_seconds"] == seconds
    assert all(row["start_epoch"] % seconds == 0 for row in result["units"])


@pytest.mark.parametrize(
    "failure", ["hash", "cross_group", "promoted_synthetic", "unbound_label"]
)
def test_index_cannot_bypass_intake_rejections(bundle, failure):
    root, manifest = bundle
    if failure == "hash":
        manifest["runs"][0]["capture"]["sha256"] = "0" * 64
    elif failure == "cross_group":
        add_run(bundle, sensor=True)
        manifest["runs"][1]["groups"] = copy.deepcopy(manifest["runs"][0]["groups"])
    elif failure == "promoted_synthetic":
        manifest["runs"][0].update(data_role="candidate_evaluation", split="test")
    else:
        submission = review(bundle, "synthetic-fixture")
        submission["labels"][0]["start_epoch"] = 0
        manifest["reviews"][0] = save(root, "labels/synthetic-fixture.json", submission)
    with pytest.raises(ValueError):
        index(bundle)


def test_index_rejects_postflight_capture_mutation(bundle, monkeypatch):
    original = intake.runtime.windows

    def changing(*args):
        result = original(*args)
        target = bundle[0] / "captures/a.json"
        target.write_bytes(target.read_bytes() + b" ")
        return result

    monkeypatch.setattr(intake.runtime, "windows", changing)
    with pytest.raises(ValueError, match="changed"):
        index(bundle)


def test_committed_typed_index_inherits_missing_count_rejection():
    with pytest.raises(ValueError):
        intake.annotation_index(
            ROOT / "data/runtime/intake-example/manifest-typed.json"
        )
    result = intake.annotation_index(
        ROOT / "data/runtime/intake-example/manifest-typed-counted.json"
    )
    assert len(result["units"]) == 3
    assert result["model_fitting_authorized"] is False


def test_cli_index_fresh_no_overwrite_and_redacted_failure(bundle, tmp_path):
    root, manifest = bundle
    output = tmp_path / "index.json"
    result = command(root / "manifest.json", output)
    assert result.returncode == 0 and not result.stderr
    before = output.read_bytes()
    assert json.loads(before) == intake.annotation_index(root / "manifest.json")
    (root / "manifest.json").unlink()
    result = command(root / "manifest.json", output)
    assert result.returncode == 1
    assert output.read_bytes() == before
    assert json.loads(result.stdout)["error_type"] == "FileExistsError"
    manifest["dataset_id"] = "private invalid value must not leak"
    save(root, "manifest.json", manifest)
    rejected = tmp_path / "rejected.json"
    result = command(root / "manifest.json", rejected)
    assert result.returncode == 1 and not result.stderr
    report = json.loads(rejected.read_text())
    assert report["protocol"] == intake.ANNOTATION_PROTOCOL
    assert report["status"] == "rejected"
    assert report["labels_created"] is False
    assert report["model_fitting_authorized"] is False
    assert report["actions_executed"] == []
    assert "units" not in report
    assert "private invalid" not in result.stdout + rejected.read_text()
    assert str(root) not in result.stdout + rejected.read_text()


def test_cli_index_output_inside_bundle_refused(bundle):
    root, _ = bundle
    output = root / "index.json"
    assert command(root / "manifest.json", output).returncode == 1
    assert not output.exists()
