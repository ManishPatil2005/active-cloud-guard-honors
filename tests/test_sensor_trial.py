import sys
import json

import pytest

from scripts import sensor_trial


@pytest.mark.parametrize(
    "value", ["short", "a" * 63, "A" * 64, "a" * 64 + "\n", "x; command"]
)
def test_rules_reject_untrusted_identity(value):
    with pytest.raises(ValueError):
        sensor_trial.rules(value)


def test_rules_minimize_output():
    rule = sensor_trial.rules("a" * 64)
    assert "thread.cgroups contains " + "a" * 64 in rule
    assert "evt.rawres >= 0" in rule
    assert "proc.cmdline" not in rule and "fd.name" not in rule


def test_existing_report_never_runs_docker(tmp_path, monkeypatch):
    report = tmp_path / "report.json"
    report.write_text("preserve")
    monkeypatch.setattr(sys, "argv", ["sensor_trial", "--output", str(report)])
    monkeypatch.setattr(
        sensor_trial, "local_daemon", lambda: pytest.fail("unexpected Docker access")
    )
    with pytest.raises(FileExistsError):
        sensor_trial.main()
    assert report.read_text() == "preserve"


@pytest.mark.parametrize("change", ["container", "kind", "result", "boolean", "valid"])
def test_sensor_record_scope(change):
    fields = {
        "evt.type": "connect",
        "evt.rawres": 0,
        "thread.cgroups": "/docker/" + "a" * 64,
    }
    if change == "container":
        fields["thread.cgroups"] += "b"
    elif change == "kind":
        fields["evt.type"] = "write"
    elif change == "boolean":
        fields["evt.rawres"] = True
    elif change == "result":
        fields["evt.rawres"] = -1
    payload = json.dumps(
        {"rule": "ACG Redis selected syscall smoke", "output_fields": fields}
    )
    if change == "valid":
        assert sensor_trial.summarize_events("startup\n" + payload, "a" * 64) == {
            "connect": 1
        }
    else:
        with pytest.raises(ValueError):
            sensor_trial.summarize_events(payload, "a" * 64)
