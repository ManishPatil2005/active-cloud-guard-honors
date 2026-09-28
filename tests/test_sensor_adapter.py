import hashlib
import json
import subprocess
import sys

import pytest

from cloudguard.runtime import load_capture, windows
from cloudguard.sensor_adapter import IMAGE, RULE, normalize


@pytest.fixture
def sample(tmp_path):
    event = dict(
        hostname="sensor",
        output="sensitive text never exported",
        priority="Informational",
        rule=RULE,
        source="syscall",
        tags=[],
        time="2026-09-28T13:32:22.698426591Z",
        output_fields={
            "evt.rawres": 0,
            "evt.rawtime": 1790602342698426591,
            "evt.time": 1790602342698426591,
            "evt.type": "execve",
            "thread.cgroups": "/docker/" + "a" * 64,
        },
    )
    inventory = tmp_path / "inventory.json"
    inventory.write_text(
        json.dumps([dict(asset_id="compose/redis", host="127.0.0.1", port=16379)])
    )

    def run(events=None, raw=None, receipt=None, **kwargs):
        data = (
            raw
            if raw is not None
            else "\n".join(json.dumps(e) for e in (events or [event]))
        )
        payload = data.encode()
        raw_path = tmp_path / "raw.log"
        raw_path.write_bytes(payload)
        trial = dict(
            image=IMAGE,
            status="events_observed",
            exit_code=0,
            sensor_removed=True,
            workload_result="PONG",
            container_id="a" * 64,
            raw_log_sha256=hashlib.sha256(payload).hexdigest(),
            matched_event_count=1,
            event_type_counts={"execve": 1},
        )
        trial.update(receipt or {})
        trial_path = tmp_path / "trial.json"
        trial_path.write_text(json.dumps(trial))
        return normalize(
            raw_path,
            trial_path,
            inventory,
            asset_id=kwargs.get("asset_id", "compose/redis"),
            capture_id="capture",
            scenario_group="group",
        )

    return event, run, tmp_path


def test_valid_capture_loads_and_minimizes(sample):
    event, run, path = sample
    bundle = run(raw=json.dumps(event) + "\nstartup diagnostic\n")
    assert bundle["accounting"]["status"] == "normalized"
    assert bundle["accounting"]["diagnostic_line_count"] == 1
    assert bundle["accounting"]["sensor_dropped_events"] is None
    assert "sensitive" not in json.dumps(bundle)
    assert bundle["capture"]["events"][0]["timestamp"] == event["time"]
    output = path / "capture.json"
    output.write_text(json.dumps(bundle["capture"]))
    capture = load_capture(output, {"compose/redis": {}})
    assert not capture["binding_verified"]
    assert windows(capture, 60)[0]["counts"]["process_start"] == 1


@pytest.mark.parametrize(
    "change",
    [
        "scope",
        "type",
        "negative",
        "boolean",
        "time",
        "fraction",
        "epoch",
        "extra",
        "source",
        "rule",
        "fields",
    ],
)
def test_invalid_record_rejects_entire_capture(sample, change):
    event, run, _ = sample
    fields = event["output_fields"]
    if change == "scope":
        fields["thread.cgroups"] += "a"
    elif change == "type":
        fields["evt.type"] = "write"
    elif change == "negative":
        fields["evt.rawres"] = -1
    elif change == "boolean":
        fields["evt.rawres"] = True
    elif change == "time":
        event["time"] = "2026-09-28T13:32:22Z"
    elif change == "fraction":
        fields["evt.time"] += 1
    elif change == "epoch":
        fields["evt.rawtime"] = True
    elif change == "extra":
        event["command"] = "do not execute"
    elif change == "source":
        event["source"] = "other"
    elif change == "rule":
        event["rule"] = "other"
    elif change == "fields":
        event["output_fields"] = []
    bundle = run()
    assert bundle["capture"] is None
    assert bundle["accounting"]["rejected_record_count"] == 1


@pytest.mark.parametrize("raw", ['{"rule":', '{"a":1,"a":2}', "[]", '{"a":NaN}'])
def test_bad_json_is_counted(sample, raw):
    _, run, _ = sample
    bundle = run(raw=raw)
    assert bundle["capture"] is None
    assert bundle["accounting"]["rejected_record_count"] == 1


def test_duplicate_projection_fails_closed(sample):
    event, run, _ = sample
    bundle = run(events=[event, event])
    assert bundle["capture"] is None
    assert bundle["accounting"]["rejection_reasons"] == {"duplicate_projection": 1}


@pytest.mark.parametrize(
    "receipt",
    [
        {"raw_log_sha256": "wrong"},
        {"exit_code": True},
        {"image": "other"},
        {"sensor_removed": False},
    ],
)
def test_receipt_gate(sample, receipt):
    _, run, _ = sample
    with pytest.raises(ValueError):
        run(receipt=receipt)


def test_count_mismatch_no_capture(sample):
    _, run, _ = sample
    bundle = run(receipt={"matched_event_count": 2})
    assert bundle["capture"] is None
    assert not bundle["accounting"]["receipt_counts_match"]


def test_unknown_asset(sample):
    _, run, _ = sample
    with pytest.raises(ValueError):
        run(asset_id="other")


def test_input_bound(sample):
    _, run, _ = sample
    with pytest.raises(ValueError, match="1 MB"):
        run(raw="x" * 1_000_001)


def test_cli_preserves_existing_directory(sample):
    _, run, path = sample
    run()
    args = [
        sys.executable,
        "scripts/normalize_sensor.py",
        "--raw",
        str(path / "raw.log"),
        "--trial",
        str(path / "trial.json"),
        "--inventory",
        str(path / "inventory.json"),
        "--asset-id",
        "compose/redis",
        "--capture-id",
        "capture",
        "--scenario-group",
        "group",
        "--output-dir",
        str(path / "result"),
    ]
    first = subprocess.run(args, capture_output=True, text=True)
    assert first.returncode == 0, first.stderr
    saved = (path / "result/capture.json").read_bytes()
    assert subprocess.run(args, capture_output=True).returncode != 0
    assert (path / "result/capture.json").read_bytes() == saved


@pytest.mark.parametrize(
    "kind,normalized",
    [
        ("execve", "process_start"),
        ("execveat", "process_start"),
        ("open", "file_open"),
        ("openat", "file_open"),
        ("openat2", "file_open"),
        ("connect", "network_connect"),
    ],
)
def test_syscall_mapping(sample, kind, normalized):
    event, run, _ = sample
    event["output_fields"]["evt.type"] = kind
    bundle = run(receipt={"event_type_counts": {kind: 1}})
    assert bundle["capture"]["events"][0]["kind"] == normalized


def test_empty_is_not_normal(sample):
    _, run, _ = sample
    bundle = run(raw="", receipt={"matched_event_count": 0, "event_type_counts": {}})
    assert bundle["capture"] is None
    assert bundle["accounting"]["status"] == "rejected"


def test_boolean_count_rejected(sample):
    _, run, _ = sample
    assert run(receipt={"event_type_counts": {"execve": True}})["capture"] is None


def test_identity_stable_despite_diagnostics(sample):
    event, run, _ = sample
    first = run()["capture"]
    second = run(raw="diagnostic\n" + json.dumps(event))["capture"]
    assert first == second
