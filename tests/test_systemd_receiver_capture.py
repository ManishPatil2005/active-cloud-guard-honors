import json
import subprocess
import sys

import pytest

from scripts import systemd_receiver_capture as capture
from cloudguard import systemd_receiver as receiver
from tests.test_systemd_receiver import FakeBus


def native_report():
    bus = FakeBus()
    report = receiver._observe(bus, now=lambda: bus.time)
    report["backend"] = dict(
        library_path="/usr/lib/x86_64-linux-gnu/libsystemd.so.0.38.0",
        library_sha256=receiver.LIBRARY_SHA256,
        abi="linux-x86_64-lp64-little-glibc2.39",
        uid=1000,
    )
    hashes = capture.source_hashes()
    report["source_sha256"] = {name: hashes[name] for name in capture.SOURCES[1:]}
    report["source_sha256_after"] = dict(report["source_sha256"])
    report["library_sha256_after"] = receiver.LIBRARY_SHA256
    return report


def returned(report=None):
    return dict(
        protocol=capture.PROTOCOL,
        status="returned",
        source_sha256=capture.source_hashes(),
        source_sha256_after=capture.source_hashes(),
        receiver=native_report() if report is None else report,
    )


def outcome(value=None, **updates):
    result = dict(
        child_started=True,
        child_reaped=True,
        timed_out=False,
        cleanup_signal=None,
        exit_code=0,
        stdout=json.dumps(returned() if value is None else value).encode(),
    )
    result.update(updates)
    return result


def test_exclusive_start_before_child_and_separate_result_no_overwrite(tmp_path):
    directory = tmp_path / "session"

    def runner(expected):
        assert (
            json.loads((directory / "started.json").read_text())["status"] == "started"
        )
        assert not (directory / "result.json").exists()
        assert expected == capture.source_hashes()
        return outcome()

    report = capture.capture(directory, runner)
    assert report["status"] == "observed" and report["receiver"]["events"] == []
    before = (directory / "started.json").read_bytes()
    with pytest.raises(FileExistsError):
        capture.capture(directory, lambda value: pytest.fail("second child launched"))
    assert (directory / "started.json").read_bytes() == before
    assert (
        json.loads((directory / "result.json").read_text())["may_disarm_recovery"]
        is False
    )


@pytest.mark.parametrize(
    "mode",
    [
        "launch",
        "interrupt",
        "timeout",
        "unreaped",
        "exit",
        "empty",
        "oversized",
        "duplicate",
        "nonfinite",
        "source",
        "private_text",
    ],
)
def test_failure_receipt_preserved_without_raw_messages_or_retry(tmp_path, mode):
    calls = []

    def runner(expected):
        calls.append(True)
        if mode == "launch":
            raise OSError("private stderr must never be saved")
        if mode == "interrupt":
            raise KeyboardInterrupt()
        if mode == "timeout":
            return outcome(timed_out=True, error_type="TimeoutExpired")
        if mode == "unreaped":
            return outcome(child_reaped=False)
        if mode == "exit":
            return outcome(exit_code=9)
        if mode == "empty":
            return outcome(stdout=b"")
        if mode == "oversized":
            return outcome(stdout=b"private stderr" * 6000)
        if mode == "duplicate":
            return outcome(stdout=b'{"protocol":"one","protocol":"two"}')
        if mode == "nonfinite":
            return outcome(stdout=b'{"x":NaN}')
        value = returned()
        if mode == "source":
            value["source_sha256_after"][capture.SOURCES[0]] = "f" * 64
        if mode == "private_text":
            value["receiver"]["private stderr"] = "credential-like text"
        return outcome(value)

    report = capture.capture(tmp_path / "session", runner)
    assert report["status"] == "unknown" and len(calls) == 1
    saved = (tmp_path / "session" / "result.json").read_text()
    assert "private stderr" not in saved and "credential-like text" not in saved
    assert not report["may_disarm_recovery"]


def test_native_unknown_keeps_partial_report_and_errno(tmp_path):
    report = native_report()
    report.update(
        status="unknown",
        stage="subscribe",
        subscription_acknowledged=False,
        continuity_checks_passed=False,
        subscription_released=False,
        error_type="OSError",
        error_errno=13,
    )
    saved = capture.capture(
        tmp_path / "session", lambda expected: outcome(returned(report))
    )
    assert saved["status"] == "unknown" and saved["receiver"]["error_errno"] == 13
    assert saved["receiver"]["stage"] == "subscribe"


def test_child_backend_failure_sanitized_and_recorded(tmp_path, monkeypatch):
    def fail():
        raise OSError(13, "private native error text")

    monkeypatch.setattr(capture.receiver, "observe", fail)
    value = capture.child(json.dumps(capture.source_hashes()))
    assert value["status"] == "failed" and value["error_errno"] == 13
    assert "private native" not in str(value)
    report = capture.capture(
        tmp_path / "session", lambda expected: outcome(value, exit_code=1)
    )
    assert (
        report["child_error_type"] == "PermissionError"
        and report["child_error_errno"] == 13
    )


def test_changed_source_refused_before_native_observer(monkeypatch):
    values = capture.source_hashes()
    values[capture.SOURCES[0]] = "f" * 64
    monkeypatch.setattr(
        capture.receiver, "observe", lambda: pytest.fail("native observer called")
    )
    assert capture.child(json.dumps(values))["status"] == "failed"


@pytest.mark.parametrize(
    "mode",
    [
        "action",
        "authority",
        "incomplete",
        "epoch",
        "backend",
        "event",
        "errno",
        "counter",
        "bool_counter",
    ],
)
def test_positive_claims_and_schema_inconsistencies_refused(mode):
    value = native_report()
    if mode == "action":
        value["services_modified"] = True
    if mode == "authority":
        value["may_disarm_recovery"] = True
    if mode == "incomplete":
        value["subscription_released"] = False
    if mode == "epoch":
        value["epoch_after"] = dict(value["epoch_after"], manager_owner=":1.9")
    if mode == "backend":
        value["backend"]["library_sha256"] = "f" * 64
    if mode == "event":
        value["events"] = [{"unit": "private.service"}]
    if mode == "errno":
        value.update(error_type="OSError", error_errno=True)
    if mode == "counter":
        value["process_calls"] = 513
    if mode == "bool_counter":
        value["window_seconds"] = True
    with pytest.raises((ValueError, KeyError)):
        capture.checked_receiver(value, capture.source_hashes())


def test_start_write_failure_prevents_launch(tmp_path, monkeypatch):
    monkeypatch.setattr(
        capture, "write_exclusive", lambda *args: (_ for _ in ()).throw(OSError())
    )
    with pytest.raises(OSError):
        capture.capture(
            tmp_path / "session", lambda value: pytest.fail("child launched")
        )


def test_result_collision_preserved_not_replaced(tmp_path):
    directory = tmp_path / "session"

    def runner(expected):
        (directory / "result.json").write_text("existing evidence", encoding="utf-8")
        return outcome()

    with pytest.raises(FileExistsError):
        capture.capture(directory, runner)
    assert (directory / "result.json").read_text() == "existing evidence"


@pytest.mark.parametrize("mode", ["normal", "terminate", "kill", "unreaped"])
def test_fixed_child_command_deadlines_and_cleanup_with_process_double(
    monkeypatch, mode
):
    calls = []

    class Process:
        returncode = 0

        def communicate(self, timeout):
            calls.append(("communicate", timeout))
            number = sum(key == "communicate" for key, value in calls)
            if mode != "normal" and (
                number == 1 or mode == "unreaped" or (mode == "kill" and number == 2)
            ):
                raise subprocess.TimeoutExpired("inert-test", timeout)
            return b"{}", None

        def terminate(self):
            calls.append(("terminate", None))

        def kill(self):
            calls.append(("kill", None))

    def popen(vector, **options):
        assert vector[:3] == [
            sys.executable,
            str(capture.ROOT / capture.SOURCES[0]),
            "--native-child",
        ]
        assert vector[3] == "--sources"
        assert options["shell"] is False and options["start_new_session"] is True
        assert (
            options["stderr"] == subprocess.DEVNULL
            and options["stdin"] == subprocess.DEVNULL
        )
        return Process()

    monkeypatch.setattr(capture.sys, "platform", "linux")
    monkeypatch.setattr(capture.os, "geteuid", lambda: 1000, raising=False)
    monkeypatch.setattr(capture.subprocess, "Popen", popen)
    value = capture.run_child(capture.source_hashes())
    assert value["child_reaped"] == (mode != "unreaped")
    assert value["timed_out"] == (mode != "normal")
    assert calls[0] == ("communicate", 20)
    if mode in {"kill", "unreaped"}:
        assert ("kill", None) in calls


@pytest.mark.skipif(
    sys.platform != "linux", reason="actual inert Linux child lifecycle"
)
@pytest.mark.parametrize("hang", [False, True])
def test_real_inert_child_deadline_reaps_no_bus_or_service(monkeypatch, hang):
    real_popen = subprocess.Popen
    code = (
        "import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(5)"
        if hang
        else "print('{}')"
    )

    def inert_popen(vector, **options):
        return real_popen([sys.executable, "-c", code], **options)

    monkeypatch.setattr(capture.subprocess, "Popen", inert_popen)
    monkeypatch.setattr(capture, "CHILD_TIMEOUT", 0.2)
    monkeypatch.setattr(capture, "CLEANUP_TIMEOUT", 0.1)
    result = capture.run_child(capture.source_hashes())
    assert result["child_reaped"] and result["timed_out"] == hang
    if hang:
        assert result["cleanup_signal"] == "kill" and result["exit_code"] < 0
    else:
        assert result["stdout"] == b"{}\n" and result["exit_code"] == 0


def test_receiver_errno_retained_without_message():
    bus = FakeBus()

    def identity():
        raise OSError(5, "private native message")

    bus.identity = identity
    value = receiver._observe(bus, now=lambda: bus.time)
    assert value["error_errno"] == 5 and "private native" not in str(value)


def test_native_child_alarm_armed_before_observer_and_canceled_after(
    monkeypatch, capsys
):
    calls = []
    monkeypatch.setattr(capture.sys, "platform", "linux")
    monkeypatch.setattr(capture.os, "geteuid", lambda: 1000, raising=False)
    monkeypatch.setattr(
        capture.sys, "argv", ["capture", "--native-child", "--sources", "{}"]
    )
    monkeypatch.setattr(capture.signal, "SIGALRM", 14, raising=False)
    monkeypatch.setattr(
        capture.signal, "signal", lambda *args: calls.append("default_action")
    )
    monkeypatch.setattr(
        capture.signal, "alarm", lambda seconds: calls.append(seconds), raising=False
    )

    def child(value):
        assert calls == ["default_action", 18]
        return dict(
            protocol=capture.PROTOCOL, status="failed", error_type="RuntimeError"
        )

    monkeypatch.setattr(capture, "child", child)
    assert capture.main() == 1 and calls[-1] == 0
    assert json.loads(capsys.readouterr().out)["status"] == "failed"
