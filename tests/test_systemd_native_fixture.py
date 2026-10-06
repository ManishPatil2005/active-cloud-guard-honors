"""Actual pinned Linux library with synthetic/private, never broker-routed data."""

import ast
import json
from pathlib import Path
import subprocess
import sys

import pytest

from scripts import systemd_native_fixture as fixture


@pytest.mark.skipif(sys.platform != "linux", reason="pinned native Linux fixture")
@pytest.mark.parametrize("case", fixture.CASES)
def test_native_selected_callback(case):
    completed = subprocess.run(
        [sys.executable, "scripts/systemd_native_fixture.py", "--case", case],
        cwd=Path(__file__).resolve().parents[1],
        shell=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        timeout=10,
        check=False,
    )
    assert completed.returncode == 0, (
        case,
        completed.returncode,
        completed.stdout[:512],
    )
    assert len(completed.stdout) <= 2048
    result = json.loads(completed.stdout)
    assert set(result) == {
        "case",
        "passed",
        "synthetic",
        "native_message_decoding",
        "broker_routing_tested",
        "jobs_submitted_or_canceled",
        "services_modified",
        "native_binding_verified",
        "may_disarm_recovery",
        "backend",
        "private_connection_closed",
    }
    assert result["case"] == case
    for key in (
        "passed",
        "synthetic",
        "native_message_decoding",
        "private_connection_closed",
    ):
        assert result[key] is True
    for key in (
        "broker_routing_tested",
        "jobs_submitted_or_canceled",
        "services_modified",
        "native_binding_verified",
        "may_disarm_recovery",
    ):
        assert result[key] is False
    assert result["backend"]["library_sha256"] == fixture.r.LIBRARY_SHA256


def test_fixture_native_call_surface_is_private_and_nonvariadic():
    tree = ast.parse(Path(fixture.__file__).read_text(encoding="utf-8"))
    calls = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr.startswith("sd_bus_")
    }
    assert calls == {
        "sd_bus_new",
        "sd_bus_set_fd",
        "sd_bus_start",
        "sd_bus_is_open",
        "sd_bus_is_ready",
        "sd_bus_message_new_method_call",
        "sd_bus_message_new_signal",
        "sd_bus_message_set_sender",
        "sd_bus_message_append_basic",
        "sd_bus_message_seal",
        "sd_bus_message_rewind",
        "sd_bus_message_get_member",
        "sd_bus_message_unref",
    }
    source = Path(fixture.__file__).read_text(encoding="utf-8")
    assert "socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)" in source
    assert "r._NativeBus.__new__(r._NativeBus)" in source
    assert "signal.alarm(8)" in source
    assert "signal.SIG_DFL" in source


def test_fixture_reader_proxy_refuses_nonreader_native_calls():
    reader = fixture._PrivateReader(object())
    for name in (
        "sd_bus_call",
        "sd_bus_send",
        "sd_bus_process",
        "sd_bus_flush",
        "sd_bus_set_address",
        "sd_bus_open_system",
    ):
        with pytest.raises(AssertionError):
            getattr(reader, name)


def test_unknown_fixture_case_refused_before_native_backend(monkeypatch):
    def forbidden():
        raise AssertionError("backend must not be called")

    monkeypatch.setattr(fixture.r, "_backend", forbidden)
    with pytest.raises(ValueError, match="unknown fixture"):
        fixture.run_case("unapproved-case")
