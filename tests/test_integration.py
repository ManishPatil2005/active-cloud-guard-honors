import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from cloudguard import integration
from cloudguard.runtime import analyze
from cloudguard.scanner import scan

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "data/development/redis-all.yaml"
BASELINE = ROOT / "data/runtime/baseline-synthetic.json"
OBSERVATION = ROOT / "data/runtime/observation-synthetic.json"
INVENTORY = ROOT / "testbed/inventory.json"


def replay(**options):
    return integration.replay(CONFIG, [BASELINE], OBSERVATION, INVENTORY, **options)


def altered(tmp_path, original, edit, name):
    document = json.loads(original.read_text())
    edit(document)
    path = tmp_path / name
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def asset(result, name="compose/redis"):
    return next(a for a in result["asset_contexts"] if a["asset_id"] == name)


def test_combined_components_and_declared_context():
    result = replay()
    assert result["engine1"] == scan(CONFIG)
    assert result["engine2"] == analyze([BASELINE], OBSERVATION, INVENTORY)
    assert result["configuration_finding_count"] == 1
    assert result["runtime_window_count"] == 2
    redis = asset(result)
    assert redis["configuration_finding_ids"] == [
        result["engine1"]["findings"][0]["id"]
    ]
    assert redis["runtime_window_indices"] == [0, 1]
    assert redis["runtime_evidence_state"] == "observations_available"
    assert redis["runtime_review_required"] is True
    assert redis["association"] == "declared_asset_id_only"
    assert (
        result["input_sha256"]["configuration"]
        == hashlib.sha256(CONFIG.read_bytes()).hexdigest()
    )
    assert set(result["selected_implementation_sha256"]) == set(
        integration.SELECTED_SOURCES
    )


def test_inventory_assets_with_no_runtime_remain_unknown():
    result = replay()
    for name in ("compose/postgres", "compose/nginx", "compose/minio"):
        row = asset(result, name)
        assert row["runtime_evidence_state"] == "no_observed_window"
        assert row["runtime_review_required"] is None
        assert row["runtime_window_indices"] == []
        assert row["combined_priority"] is None
        assert row["review_required"] is True


@pytest.mark.parametrize("mode", ["empty", "insufficient", "below_threshold"])
def test_runtime_states_do_not_erase_static_findings(tmp_path, mode):
    baseline, observation = BASELINE, OBSERVATION
    if mode == "empty":
        observation = altered(
            tmp_path, OBSERVATION, lambda d: d.update(events=[]), "o.json"
        )
    elif mode == "insufficient":
        baseline = altered(
            tmp_path, BASELINE, lambda d: d.update(events=d["events"][:3]), "b.json"
        )
    else:
        observation = altered(
            tmp_path, OBSERVATION, lambda d: d.update(events=d["events"][:2]), "o.json"
        )
    result = integration.replay(CONFIG, [baseline], observation, INVENTORY)
    assert result["engine1"] == scan(CONFIG)
    row = asset(result)
    assert row["configuration_finding_ids"]
    assert row["combined_priority"] is None
    assert row["review_required"] is True
    if mode == "empty":
        assert row["runtime_evidence_state"] == "no_observed_window"
        assert row["runtime_review_required"] is None
        assert result["runtime_window_count"] == 0
    elif mode == "insufficient":
        assert row["runtime_evidence_state"] == "insufficient_baseline"
        assert all(w["deviation_score"] is None for w in result["engine2"]["windows"])
    else:
        assert row["runtime_review_required"] is False
        assert all(
            w["status"] == "no_threshold_exceedance"
            for w in result["engine2"]["windows"]
        )


def test_unmapped_static_asset_and_nonnetwork_findings_retained(tmp_path):
    config = tmp_path / "compose.yaml"
    config.write_text(
        'services: {other: {environment: {PASSWORD: "fixture-only"}}}', encoding="utf-8"
    )
    result = integration.replay(config, [BASELINE], OBSERVATION, INVENTORY)
    other = asset(result, "compose/other")
    assert other["inventory_asset_present"] is False
    assert other["association"] == "unmapped_static_asset"
    assert other["runtime_evidence_state"] == "no_observed_window"
    assert result["engine1"]["findings"][0]["rule_id"] == "SEC001"
    assert other["configuration_finding_ids"]
    assert asset(result)["configuration_finding_ids"] == []
    assert "fixture-only" not in json.dumps(result)


def test_no_findings_does_not_create_clean_verdict(tmp_path):
    config = tmp_path / "compose.yaml"
    config.write_text("services: {}", encoding="utf-8")
    result = integration.replay(config, [BASELINE], OBSERVATION, INVENTORY)
    assert result["configuration_finding_count"] == 0
    assert result["engine2"]["windows"][1]["status"] == "deviation_for_review"
    assert all(
        a["review_required"] and a["combined_priority"] is None
        for a in result["asset_contexts"]
    )
    assert result["threat_confirmed"] is False


def test_library_has_no_network_process_or_model_activity(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("integration attempted an external operation")

    monkeypatch.setattr("socket.create_connection", forbidden)
    monkeypatch.setattr("subprocess.Popen", forbidden)
    monkeypatch.setattr("cloudguard.llm.audit", forbidden)
    result = replay()
    for name in (
        "joint_priority_calculated",
        "deployment_binding_verified",
        "independent_evaluation_verified",
        "real_data_evaluation_authorized",
        "runtime_sensor_connected",
        "calibrated",
        "threat_confirmed",
    ):
        assert result[name] is False
    assert result["actions_executed"] == []
    assert all(
        a["deployment_binding_verified"] is False for a in result["asset_contexts"]
    )


@pytest.mark.parametrize(
    "guard", ["same_id", "same_group", "overlap", "mixed_source", "invalid_event"]
)
def test_existing_runtime_guards_apply_to_integration(tmp_path, guard):
    baseline = json.loads(BASELINE.read_text())

    def edit(document):
        if guard == "same_id":
            document["capture_id"] = baseline["capture_id"]
        elif guard == "same_group":
            document["scenario_group"] = baseline["scenario_group"]
        elif guard == "overlap":
            document["events"] = baseline["events"]
        elif guard == "mixed_source":
            document["source"] = "normalized_sensor_export"
        else:
            document["events"][0]["command"] = "forbidden-payload"

    observation = altered(tmp_path, OBSERVATION, edit, "observation.json")
    with pytest.raises(ValueError):
        integration.replay(CONFIG, [BASELINE], observation, INVENTORY)


@pytest.mark.parametrize(
    "options",
    [
        {"threshold": True},
        {"threshold": float("nan")},
        {"window_seconds": 0},
        {"window_seconds": True},
    ],
)
def test_invalid_comparator_parameters(options):
    with pytest.raises(ValueError):
        replay(**options)


@pytest.mark.parametrize("baselines", [[], [BASELINE] * 21, "capture", None])
def test_baseline_bounds(baselines):
    with pytest.raises(ValueError, match="1..20"):
        integration.replay(CONFIG, baselines, OBSERVATION, INVENTORY)


def test_inventory_required_and_invalid_inventory_rejected(tmp_path):
    with pytest.raises(ValueError):
        integration.replay(CONFIG, [BASELINE], OBSERVATION, None)
    bad = tmp_path / "inventory.json"
    bad.write_text('[{"asset_id":"compose/redis","host":"8.8.8.8","port":80}]')
    with pytest.raises(ValueError):
        integration.replay(CONFIG, [BASELINE], OBSERVATION, bad)


def test_ambiguous_configuration_rejected_before_runtime(tmp_path, monkeypatch):
    config = tmp_path / "compose.yaml"
    config.write_text("services: {app: {environment: [MODE=a, MODE=b]}}")
    monkeypatch.setattr(
        integration, "analyze_runtime", lambda *a, **k: pytest.fail("runtime ran")
    )
    with pytest.raises(ValueError, match="duplicate environment"):
        integration.replay(config, [BASELINE], OBSERVATION, INVENTORY)


def test_wrapper_bounds_before_component_work(tmp_path, monkeypatch):
    config = tmp_path / "large.yaml"
    config.write_bytes(b"x" * (integration.INPUT_LIMIT + 1))
    monkeypatch.setattr(integration, "scan", lambda *a: pytest.fail("scanner ran"))
    with pytest.raises(ValueError, match="1 MB"):
        integration.replay(config, [BASELINE], OBSERVATION, INVENTORY)


def test_finding_bound(tmp_path, monkeypatch):
    static = copy.deepcopy(scan(CONFIG))
    static["findings"] *= 1001
    monkeypatch.setattr(integration, "scan", lambda *a: static)
    monkeypatch.setattr(
        integration, "analyze_runtime", lambda *a, **k: pytest.fail("runtime ran")
    )
    with pytest.raises(ValueError, match="1000"):
        replay()


@pytest.mark.parametrize(
    "role", ["configuration", "baseline", "observation", "inventory"]
)
def test_postflight_input_mutation_rejected(tmp_path, monkeypatch, role):
    originals = dict(
        configuration=CONFIG,
        baseline=BASELINE,
        observation=OBSERVATION,
        inventory=INVENTORY,
    )
    paths = {}
    for name, original in originals.items():
        paths[name] = tmp_path / original.name
        paths[name].write_bytes(original.read_bytes())
    original_analyze = integration.analyze_runtime

    def mutation(*args, **options):
        result = original_analyze(*args, **options)
        with paths[role].open("ab") as stream:
            stream.write(b"\n")
        return result

    monkeypatch.setattr(integration, "analyze_runtime", mutation)
    with pytest.raises(ValueError, match="input changed"):
        integration.replay(
            paths["configuration"],
            [paths["baseline"]],
            paths["observation"],
            paths["inventory"],
        )


def test_selected_source_change_rejected(monkeypatch):
    original_digest = integration._digest
    calls = 0

    def digest(path):
        nonlocal calls
        value = original_digest(path)
        if Path(path).name == "integration.py":
            calls += 1
            if calls == 2:
                return "0" * 64
        return value

    monkeypatch.setattr(integration, "_digest", digest)
    with pytest.raises(ValueError, match="implementation changed"):
        replay()


def test_component_inventory_mismatch_rejected(monkeypatch):
    original = integration.analyze_runtime

    def mismatched(*args, **kwargs):
        result = original(*args, **kwargs)
        result["inventory_sha256"] = "0" * 64
        return result

    monkeypatch.setattr(integration, "analyze_runtime", mismatched)
    with pytest.raises(ValueError, match="component input mismatch"):
        replay()


def test_sensor_declaration_does_not_grant_eligibility(tmp_path):
    paths = [
        altered(
            tmp_path,
            original,
            lambda d: d.update(source="normalized_sensor_export"),
            name,
        )
        for original, name in ((BASELINE, "b.json"), (OBSERVATION, "o.json"))
    ]
    result = integration.replay(CONFIG, [paths[0]], paths[1], INVENTORY)
    assert result["engine2"]["observation"]["source"] == "normalized_sensor_export"
    assert result["deployment_binding_verified"] is False
    assert result["independent_evaluation_verified"] is False
    assert result["real_data_evaluation_authorized"] is False


def test_real_cli_and_exclusive_example(tmp_path):
    args = [
        sys.executable,
        "-m",
        "cloudguard.cli",
        "integrated-replay",
        str(CONFIG),
        str(OBSERVATION),
        "--baseline",
        str(BASELINE),
        "--inventory",
        str(INVENTORY),
    ]
    completed = subprocess.run(
        args, cwd=ROOT, capture_output=True, text=True, timeout=30
    )
    assert completed.returncode == 0 and not completed.stderr
    assert json.loads(completed.stdout)["configuration_finding_count"] == 1
    output = tmp_path / "example.json"
    example_args = [
        sys.executable,
        str(ROOT / "scripts/integration_check.py"),
        "--output",
        str(output),
    ]
    completed = subprocess.run(
        example_args, cwd=ROOT, capture_output=True, text=True, timeout=30
    )
    assert completed.returncode == 0 and not completed.stderr
    before = output.read_bytes()
    assert all(json.loads(before)["checks"].values())
    assert (
        subprocess.run(
            example_args, cwd=ROOT, capture_output=True, timeout=30
        ).returncode
        == 1
    )
    assert output.read_bytes() == before
    assert list(tmp_path.iterdir()) == [output]


def test_cli_rejection_redacts_invalid_input(tmp_path):
    config = tmp_path / "compose.yaml"
    config.write_text(
        "services: {app: {environment: [PASSWORD=synthetic-marker, PASSWORD]}}"
    )
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "cloudguard.cli",
            "integrated-replay",
            str(config),
            str(OBSERVATION),
            "--baseline",
            str(BASELINE),
            "--inventory",
            str(INVENTORY),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert completed.returncode == 2 and not completed.stdout
    assert "no clean verdict" in completed.stderr
    assert "synthetic-marker" not in completed.stderr
