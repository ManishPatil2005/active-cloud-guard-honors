import json
from pathlib import Path
import pytest
from scripts.repeat_readiness import accept
from scripts import repeat_readiness
import sys
import subprocess


@pytest.mark.parametrize(
    "mode", ["valid", "cleanup", "stale", "clock", "identity", "protocol"]
)
def test_acceptance_regression(mode):
    # Historical receipt exercises acceptance, not a newly executed experiment.
    root = Path(__file__).resolve().parents[1]
    run = json.loads(
        (root / "output/engine2-identified-readiness-20260930.json").read_text()
    )
    if mode == "cleanup":
        run["sensor_removed"] = False
    elif mode == "stale":
        run["readiness_attempts"][-1]["process_id"] = -1
    elif mode == "clock":
        run["correlation"]["matches"][0]["zero_within_bounds"] = False
    elif mode == "protocol":
        run["measurement"]["timing_protocol"] = "legacy_interval_brackets"
    identity = {"id": "wrong"} if mode == "identity" else None
    if mode == "valid":
        assert accept(run) == run["target_identity_before"]
    else:
        with pytest.raises(ValueError):
            accept(run, identity)


@pytest.mark.parametrize("mode", ["launch", "timeout"])
def test_failure_preserved_without_retry(tmp_path, monkeypatch, mode):
    destination = tmp_path / "new"
    monkeypatch.setattr(
        sys, "argv", ["repeat_readiness", "--output-dir", str(destination)]
    )
    monkeypatch.setattr(repeat_readiness, "preflight", lambda: None)
    monkeypatch.setattr(repeat_readiness, "hashes", lambda: {"fixture": "hash"})
    attempts = []

    def fail(*args, **kwargs):
        attempts.append(args)
        if mode == "timeout":
            raise subprocess.TimeoutExpired("fixture", 60)
        raise FileNotFoundError("synthetic launch failure")

    monkeypatch.setattr(repeat_readiness.subprocess, "run", fail)
    with pytest.raises((FileNotFoundError, subprocess.TimeoutExpired)):
        repeat_readiness.main()
    result = json.loads((destination / "manifest.json").read_text())
    assert len(attempts) == 1
    assert result["status"] == "failed"
    assert result["not_run_trials"] == (2 if mode == "timeout" else 3)
