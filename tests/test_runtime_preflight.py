import json
from pathlib import Path
import subprocess
import sys

import pytest

from cloudguard import runtime_preflight as preflight

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("system", ["Windows", "Darwin"])
def test_non_linux_does_not_probe_linux_paths(monkeypatch, system):
    monkeypatch.setattr(preflight.platform, "system", lambda: system)

    def forbidden(*args):
        pytest.fail("non-Linux must not inspect Linux paths")

    monkeypatch.setattr(preflight, "path_fact", forbidden)
    report = preflight.collect()
    assert report["status"] == "linux_host_required"
    assert set(report["linux_markers"].values()) == {"not_applicable"}
    assert report["host"]["effective_uid"] is None


@pytest.mark.parametrize("fact", ["present", "absent", "unavailable"])
def test_linux_never_certifies_sensor(monkeypatch, fact):
    monkeypatch.setattr(preflight.platform, "system", lambda: "Linux")
    monkeypatch.setattr(preflight.os, "geteuid", lambda: 1000, raising=False)
    monkeypatch.setattr(preflight, "path_fact", lambda *args: fact)
    report = preflight.collect()
    assert report["status"] == "requires_sensor_specific_validation"
    assert not report["sensor_compatibility_verified"]
    assert not report["runtime_sensor_connected"]
    assert report["actions_executed"] == []
    assert set(report["linux_markers"].values()) == {fact}


def test_path_types_and_absence(tmp_path):
    file = tmp_path / "marker"
    file.write_text("fixture")
    assert preflight.path_fact(file, "file") == "present"
    assert preflight.path_fact(tmp_path, "directory") == "present"
    assert preflight.path_fact(file, "directory") == "unexpected_type"
    assert preflight.path_fact(tmp_path / "missing", "file") == "absent"


def test_permission_failure_is_not_absence(monkeypatch):
    def denied(*args):
        raise PermissionError("sensitive-path-not-to-be-printed")

    monkeypatch.setattr(Path, "stat", denied)
    assert preflight.path_fact("unused", "file") == "unavailable"


def test_script_saves_report_and_refuses_overwrite(tmp_path):
    output = tmp_path / "facts.json"
    command = [sys.executable, "scripts/runtime_preflight.py", "--output", str(output)]
    first = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    assert first.returncode == 0
    original = output.read_bytes()
    assert json.loads(original)["evidence_level"] == "local_host_facts"
    second = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    assert second.returncode != 0
    assert output.read_bytes() == original
