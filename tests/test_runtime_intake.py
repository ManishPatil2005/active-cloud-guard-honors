"""Synthetic offline consistency tests, never independent reviewers or attacks."""

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from cloudguard import runtime, runtime_intake as intake
from cloudguard.verification import load_inventory

ROOT = Path(__file__).resolve().parents[1]


def save(root, name, value):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")
    return dict(path=name, sha256=hashlib.sha256(path.read_bytes()).hexdigest())


@pytest.fixture
def bundle(tmp_path):
    root = tmp_path / "bundle"
    root.mkdir()
    inventory = save(
        root,
        "inventory/assets.json",
        [{"asset_id": "compose/redis", "host": "127.0.0.1", "port": 16379}],
    )
    guide = root / "guidelines/guide.md"
    guide.parent.mkdir()
    guide.write_text("Synthetic guidelines; unknown is not benign.\n", encoding="utf-8")
    capture = json.loads((ROOT / "data/runtime/observation-synthetic.json").read_text())
    ref = save(root, "captures/a.json", capture)
    manifest = dict(
        schema_version=intake.PROTOCOL,
        dataset_id="synthetic-fixture",
        inventory=inventory,
        guidelines=dict(
            path="guidelines/guide.md",
            sha256=hashlib.sha256(guide.read_bytes()).hexdigest(),
        ),
        window_seconds=60,
        runs=[
            dict(
                run_id="run-a",
                capture=ref,
                data_role="development",
                split="development",
                groups=dict(
                    template_family="template-a",
                    deployment_id="deployment-a",
                    run_family="family-a",
                ),
                receipts=dict(accounting=None, identity=None, timing=None),
            )
        ],
        reviews=[],
        adjudication=None,
    )
    save(root, "manifest.json", manifest)
    return root, manifest


def execute(bundle):
    root, manifest = bundle
    save(root, "manifest.json", manifest)
    return intake.inspect(root / "manifest.json")


def edit_capture(bundle, edit):
    root, manifest = bundle
    value = json.loads((root / "captures/a.json").read_text())
    edit(value)
    manifest["runs"][0]["capture"] = save(root, "captures/a.json", value)


def add_run(bundle, *, sensor=False):
    root, manifest = bundle
    capture = json.loads((root / "captures/a.json").read_text())
    capture.update(capture_id="capture-b", scenario_group="scenario-b")
    for entry in capture["events"]:
        entry["timestamp"] = entry["timestamp"].replace("01-02", "01-03")
    if sensor:
        edit_capture(
            bundle, lambda value: value.update(source="normalized_sensor_export")
        )
        capture["source"] = "normalized_sensor_export"
        manifest["runs"][0].update(data_role="candidate_evaluation", split="train")
    run = copy.deepcopy(manifest["runs"][0])
    run.update(
        run_id="run-b",
        capture=save(root, "captures/b.json", capture),
        groups=dict(
            template_family="template-b",
            deployment_id="deployment-b",
            run_family="family-b",
        ),
    )
    if sensor:
        run["split"] = "test"
    manifest["runs"].append(run)
    return capture


def review(bundle, identifier, labels=("benign", "unknown")):
    root, manifest = bundle
    assets, _ = load_inventory(root / manifest["inventory"]["path"])
    entries = []
    for run in manifest["runs"]:
        rows = runtime.windows(
            runtime.load_capture(root / run["capture"]["path"], assets),
            manifest["window_seconds"],
        )
        entries.extend(
            dict(
                run_id=run["run_id"],
                asset_id=row["asset_id"],
                start_epoch=row["start_epoch"],
                label=labels[index % len(labels)],
                reason="private synthetic rationale",
            )
            for index, row in enumerate(rows)
        )
    value = dict(
        schema_version="runtime_review_v1",
        reviewer_id=identifier,
        origin="synthetic_fixture",
        guidelines_sha256=manifest["guidelines"]["sha256"],
        blinded=True,
        labels=entries,
    )
    manifest["reviews"].append(save(root, f"labels/{identifier}.json", value))
    return value


def edit_review(bundle, index, value):
    root, manifest = bundle
    ref = manifest["reviews"][index]
    manifest["reviews"][index] = save(root, ref["path"], value)


def adjudication(bundle, labels):
    root, manifest = bundle
    value = copy.deepcopy(labels)
    value.pop("reviewer_id")
    value.pop("origin")
    value.pop("blinded")
    value.update(
        schema_version="runtime_adjudication_v1",
        adjudicator_id="synthetic-adjudicator",
        review_sha256=[ref["sha256"] for ref in manifest["reviews"]],
    )
    manifest["adjudication"] = save(root, "labels/adjudication.json", value)
    return value


def test_minimized_consistency_is_never_eligibility(bundle):
    root, manifest = bundle
    ref = save(
        root, "receipts/opaque.json", {"claimed_pass": True, "private": "must not leak"}
    )
    manifest["runs"][0]["receipts"] = dict.fromkeys(
        ("accounting", "identity", "timing"), ref
    )
    review(bundle, "fixture-a", ("benign", "suspicious"))
    second = review(bundle, "fixture-b", ("benign", "unknown"))
    adjudication(bundle, second)
    report = execute(bundle)
    assert report["status"] == "artifact_consistency_checked"
    assert report["observed_window_count"] == 2
    assert report["pre_adjudication_agreement"] == dict(
        known_pairs=1,
        known_agreements=1,
        known_disagreements=0,
        unknown_pairs=1,
        known_agreement_fraction=1.0,
    )
    assert report["adjudication"]["label_counts"] == dict(
        benign=1, suspicious=0, unknown=1
    )
    for field in (
        "independent_evaluation_verified",
        "model_fitting_authorized",
        "predictions_computed",
    ):
        assert report[field] is False
    assert report["actions_executed"] == []
    assert report["runs"][0]["evaluation_eligible"] is False
    assert report["runs"][0]["receipt_semantics_verified"] is False
    assert report["runs"][0]["collection_coverage"] == "partial_or_unknown"
    assert report["unique_artifact_count"] == 7
    assert "private synthetic rationale" not in json.dumps(report)
    assert "must not leak" not in json.dumps(report)


@pytest.mark.parametrize(
    "labels,expected",
    [
        (("unknown", "unknown"), (0, 0, 2, None)),
        (("suspicious", "benign"), (1, 1, 0, 0.5)),
    ],
)
def test_pre_adjudication_agreement_preserved(bundle, labels, expected):
    review(bundle, "a", ("benign", "benign"))
    second = review(bundle, "b", labels)
    adjudication(bundle, second)
    report = execute(bundle)
    agreement = report["pre_adjudication_agreement"]
    assert (
        tuple(
            agreement[key]
            for key in (
                "known_agreements",
                "known_disagreements",
                "unknown_pairs",
                "known_agreement_fraction",
            )
        )
        == expected
    )


def test_empty_capture_is_not_zero_or_benign(bundle):
    edit_capture(bundle, lambda value: value.update(events=[]))
    review(bundle, "a")
    review(bundle, "b")
    report = execute(bundle)
    assert report["empty_capture_count"] == 1
    assert report["observed_window_count"] == 0
    assert report["missing_windows_not_materialized"] is True
    assert report["pre_adjudication_agreement"]["known_agreement_fraction"] is None


@pytest.mark.parametrize("count", [0, 1, 2])
def test_optional_reviews_and_missing_receipts(bundle, count):
    for index in range(count):
        review(bundle, f"review-{index}")
    report = execute(bundle)
    assert len(report["review_submissions"]) == count
    assert set(report["runs"][0]["missing_receipts"]) == {
        "accounting",
        "identity",
        "timing",
    }


@pytest.mark.parametrize(
    "role", ["inventory", "guidelines", "capture", "review", "adjudication", "receipt"]
)
def test_hash_mismatch_rejected(bundle, role):
    root, manifest = bundle
    first = review(bundle, "a")
    review(bundle, "b")
    adjudication(bundle, first)
    manifest["runs"][0]["receipts"]["timing"] = save(root, "receipts/timing.json", {})
    refs = dict(
        inventory=manifest["inventory"],
        guidelines=manifest["guidelines"],
        capture=manifest["runs"][0]["capture"],
        review=manifest["reviews"][0],
        adjudication=manifest["adjudication"],
        receipt=manifest["runs"][0]["receipts"]["timing"],
    )
    refs[role]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="hash mismatch"):
        execute(bundle)


@pytest.mark.parametrize(
    "kind", ["template_family", "deployment_id", "run_family", "scenario_group"]
)
def test_cross_partition_group_rejected(bundle, kind):
    root, manifest = bundle
    capture = add_run(bundle, sensor=True)
    if kind == "scenario_group":
        capture[kind] = json.loads((root / "captures/a.json").read_text())[kind]
        manifest["runs"][1]["capture"] = save(root, "captures/b.json", capture)
    else:
        manifest["runs"][1]["groups"][kind] = manifest["runs"][0]["groups"][kind]
    with pytest.raises(ValueError, match="crosses"):
        execute(bundle)


def test_candidate_sensor_declaration_never_authorizes_fit(bundle):
    add_run(bundle, sensor=True)
    report = execute(bundle)
    assert [row["split_declared"] for row in report["runs"]] == ["train", "test"]
    assert all(row["evaluation_eligible"] is False for row in report["runs"])
    assert report["model_fitting_authorized"] is False


@pytest.mark.parametrize("change", ["run", "capture", "hash", "event"])
def test_duplicates_rejected(bundle, change):
    root, manifest = bundle
    capture = add_run(bundle)
    if change == "run":
        manifest["runs"][1]["run_id"] = "run-a"
    elif change == "hash":
        manifest["runs"][1]["capture"] = manifest["runs"][0]["capture"]
    else:
        original = json.loads((root / "captures/a.json").read_text())
        if change == "capture":
            capture["capture_id"] = original["capture_id"]
        else:
            capture["events"] = original["events"]
        manifest["runs"][1]["capture"] = save(root, "captures/b.json", capture)
    with pytest.raises(ValueError, match="duplicate|overlapping"):
        execute(bundle)


@pytest.mark.parametrize("change", ["synthetic", "split", "role", "known"])
def test_development_promotion_rejected(bundle, monkeypatch, change):
    _, manifest = bundle
    run = manifest["runs"][0]
    if change == "split":
        run["split"] = "test"
    elif change == "role":
        run["data_role"] = "candidate_evaluation"
    else:
        run.update(data_role="candidate_evaluation", split="test")
        if change == "known":
            edit_capture(
                bundle, lambda value: value.update(source="normalized_sensor_export")
            )
            monkeypatch.setattr(
                intake, "KNOWN_DEVELOPMENT_CAPTURES", {run["capture"]["sha256"]}
            )
    with pytest.raises(ValueError, match="development only|cannot enter"):
        execute(bundle)


def test_known_historical_hashes_match_unchanged_artifacts():
    hashes = {
        hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        for path in (
            "output/engine2-normalized-20260928/capture.json",
            "output/engine2-instrumented-normalized-20260928/capture.json",
        )
    }
    assert hashes == intake.KNOWN_DEVELOPMENT_CAPTURES


@pytest.mark.parametrize(
    "name",
    [
        "../outside.json",
        "C:/outside.json",
        "/captures/a.json",
        "captures\\a.json",
        "captures/../a.json",
        "captures/.hidden.json",
        "labels/a.json",
        "captures/a.txt",
        "captures//a.json",
    ],
)
def test_role_and_escape_paths_rejected(bundle, name):
    bundle[1]["runs"][0]["capture"]["path"] = name
    with pytest.raises(ValueError, match="path"):
        execute(bundle)


@pytest.mark.parametrize(
    "raw", [b'{"a":1,"a":2}', b'{"a":NaN}', b'{"a":Infinity}', b'{"a":1e999}']
)
def test_strict_json(raw):
    with pytest.raises(ValueError):
        intake._json(raw)


@pytest.mark.parametrize(
    "change",
    [
        "extra",
        "boolean_window",
        "float_window",
        "zero_window",
        "newline_id",
        "empty_runs",
        "too_many_reviews",
    ],
)
def test_manifest_schema_rejected(bundle, change):
    _, manifest = bundle
    if change == "extra":
        manifest["execute"] = "never"
    elif change == "newline_id":
        manifest["dataset_id"] = "name\n"
    elif change == "empty_runs":
        manifest["runs"] = []
    elif change == "too_many_reviews":
        manifest["reviews"] = [manifest["inventory"]] * 3
    else:
        manifest["window_seconds"] = dict(
            boolean_window=True, float_window=60.0, zero_window=0
        )[change]
    with pytest.raises(ValueError):
        execute(bundle)


@pytest.mark.parametrize(
    "change",
    [
        "duplicate",
        "missing",
        "extra",
        "boolean_epoch",
        "off_window",
        "blinded_false",
        "blinded_one",
        "guidelines",
        "same_reviewer",
        "bad_label",
    ],
)
def test_reviews_rejected(bundle, change):
    first = review(bundle, "a")
    value = review(bundle, "b")
    if change == "duplicate":
        value["labels"].append(value["labels"][0])
    elif change == "missing":
        value["labels"].pop()
    elif change == "extra":
        value["labels"][0]["run_id"] = "unbound"
    elif change == "boolean_epoch":
        value["labels"][0]["start_epoch"] = True
    elif change == "off_window":
        value["labels"][0]["start_epoch"] += 1
    elif change.startswith("blinded"):
        value["blinded"] = False if change.endswith("false") else 1
    elif change == "guidelines":
        value["guidelines_sha256"] = "0" * 64
    elif change == "same_reviewer":
        value["reviewer_id"] = first["reviewer_id"]
    else:
        value["labels"][0]["label"] = "confirmed_attack"
    edit_review(bundle, 1, value)
    with pytest.raises(ValueError):
        execute(bundle)


@pytest.mark.parametrize(
    "change",
    ["one_review", "review_binding", "guidelines", "flip_agreement", "missing"],
)
def test_adjudication_rejected(bundle, change):
    first = review(bundle, "a")
    review(bundle, "b")
    value = adjudication(bundle, first)
    if change == "one_review":
        bundle[1]["reviews"].pop()
    elif change == "review_binding":
        value["review_sha256"][0] = "0" * 64
    elif change == "guidelines":
        value["guidelines_sha256"] = "0" * 64
    elif change == "flip_agreement":
        value["labels"][0]["label"] = "suspicious"
    else:
        value["labels"].pop()
    bundle[1]["adjudication"] = save(bundle[0], "labels/adjudication.json", value)
    with pytest.raises(ValueError):
        execute(bundle)


@pytest.mark.parametrize("value", [[], None, "receipt"])
def test_receipt_requires_object(bundle, value):
    bundle[1]["runs"][0]["receipts"]["timing"] = save(
        bundle[0], "receipts/timing.json", value
    )
    with pytest.raises(ValueError, match="JSON object"):
        execute(bundle)


@pytest.mark.parametrize("limit", ["FILE_LIMIT", "TOTAL_LIMIT", "WINDOW_LIMIT"])
def test_resource_limits(bundle, monkeypatch, limit):
    if limit == "FILE_LIMIT":
        bundle[1]["runs"][0]["receipts"]["timing"] = save(
            bundle[0], "receipts/oversize.json", {"fixture": "x" * intake.FILE_LIMIT}
        )
    else:
        monkeypatch.setattr(intake, limit, 1)
    with pytest.raises(ValueError, match="limit"):
        execute(bundle)


def test_nonregular_artifact_refused(bundle):
    bundle[1]["runs"][0]["capture"]["path"] = "captures/directory.json"
    (bundle[0] / "captures/directory.json").mkdir()
    with pytest.raises(ValueError, match="regular"):
        execute(bundle)


def test_symlink_artifact_refused(bundle):
    root, manifest = bundle
    link = root / "captures/link.json"
    try:
        link.symlink_to(root / "captures/a.json")
    except OSError:
        pytest.skip("host symlink privilege unavailable")
    manifest["runs"][0]["capture"]["path"] = "captures/link.json"
    with pytest.raises(ValueError, match="symlink"):
        execute(bundle)


@pytest.mark.parametrize("which", ["manifest", "capture"])
def test_postflight_change_rejected(bundle, monkeypatch, which):
    original = runtime.windows

    def changing(*args):
        result = original(*args)
        target = bundle[0] / (
            "manifest.json" if which == "manifest" else "captures/a.json"
        )
        target.write_bytes(target.read_bytes() + b" ")
        return result

    monkeypatch.setattr(runtime, "windows", changing)
    with pytest.raises(ValueError, match="changed"):
        execute(bundle)


def command(manifest, output):
    return subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/runtime_intake.py"),
            "--manifest",
            str(manifest),
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
    )


def test_cli_fresh_report_no_overwrite_and_redacted_rejection(bundle, tmp_path):
    root, manifest = bundle
    output = tmp_path / "report.json"
    result = command(root / "manifest.json", output)
    assert result.returncode == 0 and not result.stderr
    before = output.read_bytes()
    assert json.loads(before)["model_fitting_authorized"] is False
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
    report = json.loads(rejected.read_bytes())
    assert report["status"] == "rejected" and report["actions_executed"] == []
    assert "private invalid" not in rejected.read_text() + result.stdout
    assert str(root) not in rejected.read_text() + result.stdout


def test_cli_output_inside_bundle_refused(bundle):
    root, _ = bundle
    output = root / "report.json"
    assert command(root / "manifest.json", output).returncode == 1
    assert not output.exists()


def test_committed_example_is_explicitly_synthetic():
    report = intake.inspect(ROOT / "data/runtime/intake-example/manifest.json")
    assert report["observed_window_count"] == 3
    assert report["pre_adjudication_agreement"] == dict(
        known_pairs=2,
        known_agreements=1,
        known_disagreements=1,
        unknown_pairs=1,
        known_agreement_fraction=0.5,
    )
    assert all(
        row["origin_declared"] == "synthetic_fixture"
        for row in report["review_submissions"]
    )
    assert report["adjudication"]["label_counts"] == dict(
        benign=1, suspicious=0, unknown=2
    )
    assert report["independent_evaluation_verified"] is False


def test_human_metadata_is_not_human_authentication(bundle):
    for identifier in ("a", "b"):
        value = review(bundle, identifier)
        value["origin"] = "human_submission"
        edit_review(bundle, len(bundle[1]["reviews"]) - 1, value)
    report = execute(bundle)
    assert report["independent_evaluation_verified"] is False
    assert report["model_fitting_authorized"] is False


@pytest.mark.parametrize(
    "change",
    ["asset", "container", "duplicate_event", "time", "field", "newline_capture_id"],
)
def test_existing_capture_schema_and_identity_reused(bundle, change):
    def edit(value):
        if change == "asset":
            value["bindings"][0]["asset_id"] = "unbound"
        elif change == "container":
            value["events"][0]["container_id"] = "a" * 64
        elif change == "duplicate_event":
            value["events"].append(value["events"][0])
        elif change == "time":
            value["events"][0]["timestamp"] = "2026-01-02T00:00:00.000"
        elif change == "field":
            value["events"][0]["command"] = "never execute"
        else:
            value["capture_id"] = "bad\n"

    edit_capture(bundle, edit)
    with pytest.raises(ValueError):
        execute(bundle)


def test_empty_guidelines_and_top_manifest_bound(bundle):
    root, manifest = bundle
    guide = root / manifest["guidelines"]["path"]
    guide.write_bytes(b" \n")
    manifest["guidelines"]["sha256"] = hashlib.sha256(guide.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="nonempty"):
        execute(bundle)
    (root / "manifest.json").write_bytes(b" " * 100_001)
    with pytest.raises(ValueError, match="byte limit"):
        intake.inspect(root / "manifest.json")
