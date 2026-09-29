import json
import pytest
from scripts import paired_pilot, paired_report


@pytest.mark.parametrize("ids", ["", "a\nb"])
def test_preflight_requires_single_target(monkeypatch, ids):
    monkeypatch.setattr(paired_pilot, "local_daemon", lambda: None)
    monkeypatch.setattr(paired_pilot, "check_sensor_absent", lambda: None)
    monkeypatch.setattr(paired_pilot, "command", lambda *a: ids)
    monkeypatch.setattr(
        paired_pilot,
        "target_identity",
        lambda _: pytest.fail("must not inspect ambiguous target"),
    )
    with pytest.raises(ValueError):
        paired_pilot.preflight()


@pytest.mark.parametrize(
    "mode",
    ["valid", "failed_manifest", "warmup", "identity", "cleanup", "boolean_latency"],
)
def test_paired_summary(tmp_path, mode):
    manifest = dict(
        status="completed",
        sequence=[
            dict(name=n, exit_code=0)
            for n in ["clock", "off-1", "on-1", "on-2", "off-2"]
        ],
    )
    if mode == "failed_manifest":
        manifest["status"] = "failed"
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    for name in ["off-1", "on-1", "on-2", "off-2"]:
        on = name.startswith("on")
        row = dict(
            status="events_observed" if on else "completed",
            warmup_protocol="two_pings_v1",
            mode="sensor_off_control",
            sensor_started=False,
            sensor_removed=True,
            measurement=dict(
                status="completed",
                profile="ping_4",
                scenario_group="redis-ping-development",
                calls=[
                    dict(
                        pong=True,
                        docker_exec_round_trip_ns=20_000_000 if on else 10_000_000,
                    )
                ]
                * 4,
            ),
        )
        before, after = (
            ("target_identity_before", "target_identity_after")
            if on
            else ("identity_before", "identity_after")
        )
        row[before] = row[after] = dict(id="a" * 64)
        if name == "on-1":
            if mode == "warmup":
                row["warmup_protocol"] = "adaptive_v1"
            elif mode == "identity":
                row[after] = dict(id="b" * 64)
            elif mode == "cleanup":
                row["sensor_removed"] = False
            elif mode == "boolean_latency":
                row["measurement"]["calls"][0]["docker_exec_round_trip_ns"] = True
        (tmp_path / (name + ".json")).write_text(json.dumps(row))
    if mode == "valid":
        result = paired_report.summarize(tmp_path)
        assert result["pairs"][0]["on_minus_off_ms"] == 10
        assert result["sensor_cpu_memory_overhead"] is None
    else:
        with pytest.raises(ValueError):
            paired_report.summarize(tmp_path)
