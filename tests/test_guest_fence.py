from contextlib import contextmanager
from pathlib import Path
import subprocess
import sys
import tempfile
import time

import pytest

from cloudguard import guest_fence as fence

NONCE = "a" * 64


@contextmanager
def simulated_lock(path, timeout):
    yield


def session(tmp_path, **kwargs):
    return fence.InertGuestFence.initialize(
        tmp_path / "session", NONCE, inert=True, lock=simulated_lock, **kwargs
    )


@pytest.mark.parametrize("value", [False, 0, -1, 6, float("nan"), float("inf"), "5"])
def test_invalid_lock_budget(value):
    with pytest.raises(ValueError):
        fence.bounded_timeout(value)


@pytest.mark.parametrize("value", [False, 1, "yes", None])
def test_no_native_initialization_or_directory(tmp_path, value):
    path = tmp_path / "session"
    with pytest.raises(ValueError, match="inert"):
        fence.InertGuestFence.initialize(path, NONCE, inert=value)
    assert not path.exists()


def test_normal_stop_recovery_then_late_stop_refused(tmp_path):
    s = session(tmp_path)
    calls = []
    assert s.stop(lambda: calls.append("stop") or True)["mode"] == "inert"
    result = s.recover(lambda: calls.append("recover") or True)
    assert result["submitted_stop_quiescence_known"]
    with pytest.raises(ValueError, match="sealed"):
        s.stop(lambda: calls.append("late") or True)
    assert calls == ["stop", "recover"]
    assert result["native_service_validated"] is False


def test_recovery_before_delivery_fences_all_new_requests(tmp_path):
    s = session(tmp_path)
    result = s.recover(lambda: True)
    assert result["new_stop_requests_fenced"]
    with pytest.raises(ValueError, match="sealed"):
        s.stop(lambda: pytest.fail("late dispatch"))


@pytest.mark.parametrize("error", [ValueError, TimeoutError, KeyboardInterrupt])
def test_interrupted_intent_never_becomes_quiescence_proof(tmp_path, error):
    s = session(tmp_path)

    def fail():
        raise error("simulation error")

    with pytest.raises(error):
        s.stop(fail)
    result = s.recover(lambda: True)
    assert result["operator_recovery_required"]
    assert result["submitted_stop_quiescence_known"] is False


def test_fence_cannot_claim_to_cancel_an_already_detached_job(tmp_path):
    s = session(tmp_path)

    def submitted_then_lost():
        raise TimeoutError("simulated detached request")

    with pytest.raises(TimeoutError):
        s.stop(submitted_then_lost)
    result = s.recover(lambda: True)
    # Model a job outside this cooperating file lock executing afterward.
    (s.directory / "detached-late-effect").touch()
    assert result["new_stop_requests_fenced"]
    assert result["submitted_stop_quiescence_known"] is False
    assert result["operator_recovery_required"]


def test_no_duplicate_stop_or_overwritten_recovery(tmp_path):
    s = session(tmp_path)
    s.stop(lambda: True)
    with pytest.raises(FileExistsError):
        s.stop(lambda: pytest.fail("duplicate stop"))
    s.recover(lambda: True)
    before = (s.directory / "recovery.json").read_bytes()
    with pytest.raises(FileExistsError):
        s.recover(lambda: pytest.fail("duplicate recovery callback"))
    assert (s.directory / "recovery.json").read_bytes() == before


def test_expired_stop_never_dispatches(tmp_path):
    now = [1]
    s = session(tmp_path, clock=lambda: now[0])
    now[0] = s.deadline_ns
    with pytest.raises(TimeoutError):
        s.stop(lambda: pytest.fail("expired dispatch"))
    assert not (s.directory / "stop-intent.json").exists()
    assert s.recover(lambda: True)["new_stop_requests_fenced"]


def test_lock_timeout_still_seals_without_racing_recovery_callback(tmp_path):
    s = session(tmp_path)

    @contextmanager
    def unavailable(path, timeout):
        raise TimeoutError("busy")
        yield

    s.lock = unavailable
    with pytest.raises(TimeoutError):
        s.recover(lambda: pytest.fail("restore raced lock holder"))
    assert (s.directory / "sealed.json").exists()
    s.lock = simulated_lock
    with pytest.raises(ValueError, match="sealed"):
        s.stop(lambda: pytest.fail("late dispatch"))


@pytest.mark.parametrize("record", [b'{"nonce":"bad"}', b"{broken", b"x" * 4097])
def test_corrupt_completion_keeps_unknown(tmp_path, record):
    s = session(tmp_path)
    fence.exclusive(s.directory / "stop-intent.json", dict(nonce=NONCE))
    (s.directory / "stop-complete.json").write_bytes(record)
    assert s.recover(lambda: True)["operator_recovery_required"]


def test_wrong_request_mode_and_duplicate_fields_refused(tmp_path):
    s = session(tmp_path)
    path = s.directory / "request.json"
    path.write_text('{"mode":"inert","mode":"restore"}', encoding="utf-8")
    with pytest.raises(ValueError):
        fence.InertGuestFence(s.directory, NONCE, lock=simulated_lock)


@pytest.mark.parametrize("field", ["mode", "nonce", "deadline_ns", "extra"])
def test_request_shape_refused_without_simulated_effect(tmp_path, field):
    s = session(tmp_path)
    value = fence.read(s.directory / "request.json")
    value[field] = {
        "mode": "restore",
        "nonce": "b" * 64,
        "deadline_ns": True,
        "extra": True,
    }[field]
    (s.directory / "request.json").write_text(fence.json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError):
        fence.InertGuestFence(s.directory, NONCE, lock=simulated_lock)


def test_recovery_failure_still_prevents_new_stop(tmp_path):
    s = session(tmp_path)
    with pytest.raises(ValueError):
        s.recover(lambda: False)
    with pytest.raises(ValueError, match="sealed"):
        s.stop(lambda: pytest.fail("late stop"))
    with pytest.raises(FileExistsError):
        s.recover(lambda: pytest.fail("recovery effect repeated"))


def test_native_lock_refuses_windows_before_open(tmp_path, monkeypatch):
    monkeypatch.setattr(fence.sys, "platform", "win32")
    with pytest.raises(ValueError, match="Linux"):
        with fence.linux_lock(tmp_path / "missing", 1):
            pytest.fail("non-Linux lock entered")


def wait_path(path, process):
    deadline = time.monotonic() + 5
    while not path.exists():
        if process.poll() is not None or time.monotonic() >= deadline:
            pytest.fail("inert worker did not reach marker")
        time.sleep(0.01)


@pytest.mark.skipif(
    sys.platform != "linux", reason="real guest flock integration is Linux-only"
)
@pytest.mark.parametrize("kill_holder", [False, True])
def test_real_inert_linux_lock_holder_and_terminal_fence(kill_holder):
    # Linux-local temporary filesystem, not the Windows /mnt/d shared checkout.
    with tempfile.TemporaryDirectory(prefix="acg-inert-fence-") as scratch:
        directory = Path(scratch) / "session"
        s = fence.InertGuestFence.initialize(directory, NONCE, inert=True)
        code = (
            "import sys,time;from pathlib import Path;"
            "from cloudguard.guest_fence import InertGuestFence;"
            "s=InertGuestFence(sys.argv[1],sys.argv[2]);"
            "s.stop(lambda:(Path(sys.argv[1]+'/entered').touch(),time.sleep(20),True)[-1])"
        )
        process = subprocess.Popen(
            [sys.executable, "-c", code, str(directory), NONCE],
            cwd=Path(__file__).resolve().parents[1],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
        )
        queued = None
        try:
            wait_path(directory / "entered", process)
            if not kill_holder:
                queued_code = (
                    "import sys;from pathlib import Path;"
                    "from cloudguard.guest_fence import InertGuestFence;"
                    "s=InertGuestFence(sys.argv[1],sys.argv[2]);"
                    "Path(sys.argv[1]+'/waiting').touch()\n"
                    "try:\n s.stop(lambda:Path(sys.argv[1]+'/late-effect').touch() or True)\n"
                    "except ValueError as e:\n"
                    " if 'sealed' not in str(e):raise\n"
                    " Path(sys.argv[1]+'/rejected').touch()\n"
                    "else:\n raise SystemExit(2)\n"
                )
                queued = subprocess.Popen(
                    [sys.executable, "-c", queued_code, str(directory), NONCE],
                    cwd=Path(__file__).resolve().parents[1],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    close_fds=True,
                )
                wait_path(directory / "waiting", queued)
                with pytest.raises(TimeoutError):
                    s.recover(lambda: pytest.fail("must not race worker"), timeout=0.1)
                assert (directory / "sealed.json").exists()
            process.kill()
            process.wait(timeout=3)
            result = s.recover(lambda: True)
            if queued is not None:
                assert queued.wait(timeout=3) == 0
                assert (directory / "rejected").exists()
                assert not (directory / "late-effect").exists()
            assert result["operator_recovery_required"]
            with pytest.raises(ValueError, match="sealed"):
                s.stop(lambda: pytest.fail("late worker dispatched"))
            assert result["native_service_validated"] is False
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=3)
            if queued is not None and queued.poll() is None:
                queued.kill()
                queued.wait(timeout=3)


@pytest.mark.skipif(
    sys.platform != "linux", reason="real guest flock integration is Linux-only"
)
def test_real_inert_linux_completed_dispatch_and_recovery():
    with tempfile.TemporaryDirectory(prefix="acg-inert-fence-") as scratch:
        directory = Path(scratch) / "session"
        s = fence.InertGuestFence.initialize(directory, NONCE, inert=True)
        code = (
            "import sys;from pathlib import Path;"
            "from cloudguard.guest_fence import InertGuestFence;"
            "s=InertGuestFence(sys.argv[1],sys.argv[2]);"
            "s.stop(lambda:Path(sys.argv[1]+'/simulated-effect').touch() or True)"
        )
        completed = subprocess.run(
            [sys.executable, "-c", code, str(directory), NONCE],
            cwd=Path(__file__).resolve().parents[1],
            timeout=5,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
        )
        assert completed.returncode == 0 and (directory / "simulated-effect").exists()
        result = s.recover(lambda: True)
        assert result["submitted_stop_quiescence_known"] is True
        assert result["native_service_validated"] is False
