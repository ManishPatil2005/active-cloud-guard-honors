import sys
import json

import pytest

from scripts import sensor_trial


def test_fixed_canaries_use_identity_callback(monkeypatch):
    ids = []

    def ping():
        ids.append(len(ids) + 100)
        return "PONG"

    monkeypatch.setattr(
        sensor_trial, "command", lambda *args: "true" if args[0] == "inspect" else "log"
    )
    monkeypatch.setattr(sensor_trial.time, "sleep", lambda _: None)
    monkeypatch.setattr(
        sensor_trial, "summarize_events", lambda *args: {"execve": 1, "connect": 1}
    )
    sensor_trial.await_canary("sensor", "a" * 64, fixed_two=True, ping=ping)
    assert ids == [100, 101]


@pytest.mark.parametrize("ready", [True, False])
def test_fixed_warmup_always_two_or_reject(monkeypatch, ready):
    calls = []

    def command(*args):
        calls.append(args[0])
        return (
            "true" if args[0] == "inspect" else "PONG" if args[0] == "exec" else "log"
        )

    monkeypatch.setattr(sensor_trial, "command", command)
    monkeypatch.setattr(sensor_trial.time, "sleep", lambda _: None)
    monkeypatch.setattr(
        sensor_trial,
        "summarize_events",
        lambda *a: {"execve": 1, "connect": 1} if ready else {},
    )
    if ready:
        assert (
            sensor_trial.await_canary("sensor", "a" * 64, fixed_two=True)[
                "canary_attempts"
            ]
            == 2
        )
    else:
        with pytest.raises(ValueError):
            sensor_trial.await_canary("sensor", "a" * 64, fixed_two=True)
    assert calls.count("exec") == 2
    if ready:
        monkeypatch.setattr(
            sensor_trial, "command", lambda *a: "true" if a[0] == "inspect" else "bad"
        )
        with pytest.raises(ValueError, match="fixed warmup"):
            sensor_trial.await_canary("sensor", "a" * 64, fixed_two=True)


@pytest.mark.parametrize(
    "change", ["none", "running", "id", "project", "service", "restarts"]
)
def test_target_identity_scope(monkeypatch, change):
    fields = dict(
        id="a" * 64,
        image="sha256:" + "b" * 64,
        started_at="2026-09-28T00:00:00Z",
        running=True,
        restarts=0,
        project="honors-cloud-guard",
        service="redis",
    )
    if change != "none":
        fields[change] = False if change in {"running", "restarts"} else "wrong"
    monkeypatch.setattr(sensor_trial, "command", lambda *a: json.dumps(fields))
    if change == "none":
        assert sensor_trial.target_identity("a" * 64) == fields
    else:
        with pytest.raises(ValueError):
            sensor_trial.target_identity("a" * 64)


@pytest.mark.parametrize("mode", ["ready", "stopped", "no_events"])
def test_readiness_requires_events(monkeypatch, mode):
    calls = []

    def command(*args):
        calls.append(args)
        if args[0] == "inspect":
            return "false" if mode == "stopped" else "true"
        if args[0] == "exec":
            return "PONG"
        return "log"

    monkeypatch.setattr(sensor_trial, "command", command)
    monkeypatch.setattr(sensor_trial.time, "sleep", lambda _: None)
    monkeypatch.setattr(
        sensor_trial,
        "summarize_events",
        lambda *a: {"execve": 1, "connect": 1} if mode == "ready" else {},
    )
    if mode == "ready":
        assert sensor_trial.await_canary("sensor", "a" * 64)["canary_attempts"] == 1
    else:
        with pytest.raises(ValueError):
            sensor_trial.await_canary("sensor", "a" * 64)
    assert len([c for c in calls if c[0] == "exec"]) <= 3


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
