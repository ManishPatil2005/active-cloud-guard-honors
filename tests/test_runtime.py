import json
from pathlib import Path
import subprocess
import sys

import pytest
from cloudguard.runtime import analyze, load_capture, windows

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "data/runtime/baseline-synthetic.json"
OBSERVATION = ROOT / "data/runtime/observation-synthetic.json"
INVENTORY = ROOT / "testbed/inventory.json"


def altered(tmp_path, original, edit, name="capture.json"):
    data = json.loads(original.read_text())
    edit(data)
    path = tmp_path / name
    path.write_text(json.dumps(data))
    return path


def test_synthetic_replay_and_provenance():
    result = analyze([BASELINE], OBSERVATION, INVENTORY)
    assert [w["status"] for w in result["windows"]] == [
        "no_threshold_exceedance",
        "deviation_for_review",
    ]
    assert result["windows"][1]["deviation_score"] == 8.0
    assert result["mode"] == "observation_only_replay"
    assert not result["runtime_sensor_connected"] and not result["threat_confirmed"]
    assert result["actions_executed"] == []
    assert len(result["observation"]["sha256"]) == 64


@pytest.mark.parametrize(
    "change",
    [
        "unknown_asset",
        "unknown_container",
        "duplicate_event",
        "duplicate_binding",
        "bad_time",
        "naive_time",
        "bad_kind",
        "extra_field",
        "bad_container",
        "too_many_events",
    ],
)
def test_invalid_capture_rejected(tmp_path, change):
    def edit(data):
        if change == "unknown_asset":
            data["bindings"][0]["asset_id"] = "unknown"
        elif change == "unknown_container":
            data["events"][0]["container_id"] = "a" * 64
        elif change == "duplicate_event":
            data["events"].append(data["events"][0])
        elif change == "duplicate_binding":
            data["bindings"] *= 2
        elif change == "bad_time":
            data["events"][0]["timestamp"] = "not-a-timestamp-at-all"
        elif change == "naive_time":
            data["events"][0]["timestamp"] = "2026-01-01T00:00:00.000"
        elif change == "bad_kind":
            data["events"][0]["kind"] = "execute_shell"
        elif change == "extra_field":
            data["events"][0]["command"] = "do-not-execute"
        elif change == "bad_container":
            data["bindings"][0]["container_id"] = "short"
        else:
            data["events"] = [data["events"][0]] * 2001

    path = altered(tmp_path, OBSERVATION, edit)
    with pytest.raises(ValueError):
        analyze([BASELINE], path, INVENTORY)


@pytest.mark.parametrize(
    "change", ["same_id", "same_group", "same_events", "mixed_source"]
)
def test_leakage_and_source_guards(tmp_path, change):
    baseline = json.loads(BASELINE.read_text())

    def edit(data):
        if change == "same_id":
            data["capture_id"] = baseline["capture_id"]
        elif change == "same_group":
            data["scenario_group"] = baseline["scenario_group"]
        elif change == "same_events":
            data["events"] = baseline["events"]
        else:
            data["source"] = "normalized_sensor_export"

    path = altered(tmp_path, OBSERVATION, edit)
    with pytest.raises(ValueError):
        analyze([BASELINE], path, INVENTORY)


def test_duplicate_baseline_rejected():
    with pytest.raises(ValueError):
        analyze([BASELINE, BASELINE], OBSERVATION, INVENTORY)


def test_baseline_never_learns_from_observation(tmp_path):
    def edit(data):
        for index, event in enumerate(data["events"]):
            event["timestamp"] = f"2026-01-02T00:00:{index:02d}Z"

    path = altered(tmp_path, OBSERVATION, edit)
    assert (
        analyze([BASELINE], path, INVENTORY)["baseline_parameters"]
        == analyze([BASELINE], OBSERVATION, INVENTORY)["baseline_parameters"]
    )


def test_empty_capture_is_unknown_not_clean(tmp_path):
    path = altered(tmp_path, OBSERVATION, lambda data: data.update(events=[]))
    result = analyze([BASELINE], path, INVENTORY)
    assert result["status"] == "no_observations" and result["windows"] == []


def test_insufficient_baseline_abstains(tmp_path):
    path = altered(
        tmp_path, BASELINE, lambda data: data.update(events=data["events"][:3])
    )
    result = analyze([path], OBSERVATION, INVENTORY)
    assert all(
        w["status"] == "insufficient_baseline" and w["deviation_score"] is None
        for w in result["windows"]
    )


def test_gap_is_not_zero_filled_and_order_independent(tmp_path):
    def edit(data):
        data["events"] = [data["events"][0], data["events"][-1]]
        data["events"][1]["timestamp"] = "2026-01-02T05:00:00Z"
        data["events"].reverse()

    path = altered(tmp_path, OBSERVATION, edit)
    result = analyze([BASELINE], path, INVENTORY)
    assert len(result["windows"]) == 2
    assert all(
        w["observation_coverage"] == "partial_or_unknown" for w in result["windows"]
    )


def test_window_boundary_and_offset():
    capture = load_capture(BASELINE, {"compose/redis"})
    capture["events"] = [
        dict(capture["events"][0], epoch=59.999),
        dict(capture["events"][1], epoch=60.0),
    ]
    assert [w["start_epoch"] for w in windows(capture, 60)] == [0, 60]


@pytest.mark.parametrize(
    "options",
    [
        {"window_seconds": 0},
        {"window_seconds": True},
        {"window_seconds": 1.5},
        {"threshold": float("nan")},
        {"threshold": -1},
        {"threshold": True},
    ],
)
def test_invalid_parameters(options):
    with pytest.raises(ValueError):
        analyze([BASELINE], OBSERVATION, INVENTORY, **options)


def test_cli_replay():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "cloudguard.cli",
            "runtime-replay",
            str(OBSERVATION),
            "--baseline",
            str(BASELINE),
            "--inventory",
            str(INVENTORY),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert json.loads(result.stdout)["actions_executed"] == []
