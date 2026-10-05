import copy
import sys

import pytest

from cloudguard import boot_clock as boot
from scripts import sensor_trial

BOOT_ID = "12345678-1234-1234-1234-123456789abc"


@pytest.mark.parametrize(
    "mode", ["valid", "namespace", "offset", "duplicate", "missing", "boot_id"]
)
def test_namespace_parser(mode):
    ns, offsets, identity = "time:[123]", "monotonic 0 0\nboottime 0 0", BOOT_ID
    if mode == "namespace":
        ns = "pid:[123]"
    elif mode == "offset":
        offsets = "monotonic x 0\nboottime 0 0"
    elif mode == "duplicate":
        offsets += "\nboottime 0 0"
    elif mode == "missing":
        offsets = "monotonic 0 0"
    elif mode == "boot_id":
        identity = "invalid"
    if mode == "valid":
        facts = boot.namespace_facts(ns, offsets, identity)
        assert len(facts["kernel_boot_sha256"]) == 64
        assert BOOT_ID not in str(facts)
    else:
        with pytest.raises(ValueError):
            boot.namespace_facts(ns, offsets, identity)


@pytest.mark.parametrize(
    "mode", ["valid", "offset", "kernel", "missing", "boolean", "children"]
)
def test_domains_gate(mode):
    domains = [
        boot.namespace_facts(f"time:[{n}]", "monotonic 0 0\nboottime 0 0", BOOT_ID)
        for n in range(3)
    ]
    for domain in domains:
        domain["time_namespace_for_children"] = domain["time_namespace"]
    if mode == "offset":
        domains[1]["offsets"]["boottime"] = [1, 0]
    elif mode == "kernel":
        domains[2]["kernel_boot_sha256"] = "x" * 64
    elif mode == "missing":
        domains.pop()
    elif mode == "boolean":
        domains[0]["offsets"]["monotonic"][0] = False
    elif mode == "children":
        domains[0]["time_namespace_for_children"] = "time:[99]"
    if mode == "valid":
        boot.checked_domains(domains)  # Namespace IDs need not be identical.
    else:
        with pytest.raises(ValueError):
            boot.checked_domains(domains)


@pytest.mark.parametrize(
    "values",
    [(100, 1000, 110), (110, 1000, 100), (0, 1000, 5_000_001), (True, 1000, 110)],
)
def test_bounds(values):
    if values == (100, 1000, 110):
        result = boot.bounds(*values)
        assert (result["offset_lower_ns"], result["offset_upper_ns"]) == (890, 900)
    else:
        with pytest.raises(ValueError):
            boot.bounds(*values)


def fixture(change=0):
    def reading(t):
        return boot.bounds(t, 10**9 + t + (change if t >= 300 else 0), t + 1)

    snapshots = [
        dict(phase=phase, sample=reading(t))
        for phase, t in zip(
            ["before_sensor_launch", "after_sensor_launch", "after_readiness"],
            [100, 200, 300],
        )
    ]
    observations, matches = [], []
    for pid in range(1, 5):
        t = 400 + pid * 100
        observations.append(
            dict(process_id=pid, boot_before=reading(t), boot_after=reading(t + 50))
        )
        matches.append(dict(process_id=pid, event_unix_ns=10**9 + t + 20))
    return snapshots, observations, dict(matches=matches)


@pytest.mark.parametrize("change", [0, 1_000_000_000])
def test_offset_change_without_correction(change):
    result = boot.summarize(*fixture(change))
    assert all(
        r["intersects_prelaunch_offset"] for r in result["event_implied_offsets"]
    )
    assert result["offset_changes_from_prelaunch"][-1]["lower_ns"] == change - 1
    assert result["collector_calibration_value_observed"] is False
    assert result["correction_applied"] is False


@pytest.mark.parametrize(
    "mode", ["shape", "phase", "scalar", "bounds", "order", "pid", "event"]
)
def test_saved_corruption_rejected(mode):
    snaps, obs, correlation = copy.deepcopy(fixture())
    if mode == "shape":
        obs.pop()
    elif mode == "phase":
        snaps[1]["phase"] = "wrong"
    elif mode == "scalar":
        obs[0]["boot_before"]["realtime_ns"] = True
    elif mode == "bounds":
        obs[0]["boot_before"]["offset_lower_ns"] += 1
    elif mode == "order":
        obs[0]["boot_after"] = obs[0]["boot_before"]
    elif mode == "pid":
        obs[0]["process_id"] = 99
    else:
        correlation["matches"][0]["event_unix_ns"] = True
    with pytest.raises(ValueError):
        boot.summarize(snaps, obs, correlation)


def test_no_monotonic_fallback(monkeypatch):
    monkeypatch.delattr(boot.time, "CLOCK_BOOTTIME", raising=False)
    with pytest.raises(ValueError, match="native CLOCK_BOOTTIME"):
        boot.sample()


def test_boot_option_requires_clock_domains(tmp_path, monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["sensor_trial", "--boot-clock", "--output", str(tmp_path / "new")]
    )
    with pytest.raises(SystemExit):
        sensor_trial.main()
    assert not (tmp_path / "new").exists()


def test_backend_domain_command_scope(monkeypatch):
    calls = []

    def command(*args):
        calls.append(args)
        return (
            "time:[123]"
            if args[-1].startswith("/proc/self/ns/time")
            else BOOT_ID
            if args[-1].endswith("boot_id")
            else "monotonic 0 0\nboottime 0 0"
        )

    monkeypatch.setattr(sensor_trial, "command", command)
    sensor_trial.time_domain("a" * 64)
    assert len(calls) == 4 and all(c[:2] == ("exec", "a" * 64) for c in calls)
    with pytest.raises(ValueError):
        sensor_trial.time_domain("untrusted;command")


def test_children_namespace_mismatch_rejected(monkeypatch):
    def command(*args):
        if args[-1] == "/proc/self/ns/time_for_children":
            return "time:[456]"
        if args[-1] == "/proc/self/ns/time":
            return "time:[123]"
        return (
            BOOT_ID if args[-1].endswith("boot_id") else "monotonic 0 0\nboottime 0 0"
        )

    monkeypatch.setattr(sensor_trial, "command", command)
    with pytest.raises(ValueError, match="offsets ambiguous"):
        sensor_trial.time_domain("a" * 64)
