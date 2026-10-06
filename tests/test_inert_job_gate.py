"""Supplied synthetic jobs only; actual Linux tests use files/locks/processes."""

from contextlib import contextmanager
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

import pytest

from cloudguard import guest_fence as fence
from cloudguard import inert_job_gate as gate

NONCE = "a" * 64
IDENTITY = dict(boot_sha256="b" * 64, bus_id="c" * 32, manager_owner=":1.4242")
PATH = "/org/freedesktop/systemd1/job/7"


@contextmanager
def simulated_lock(path, timeout):
    yield


def session(tmp_path, **kwargs):
    return gate.InertJobGate.initialize(
        tmp_path / "session", NONCE, IDENTITY, inert=True, lock=simulated_lock, **kwargs
    )


def reopen(s):
    return gate.InertJobGate(
        s.directory, NONCE, lock=simulated_lock, clock=s.fence.clock
    )


def event(path=PATH, result="done"):
    return dict(
        sender=IDENTITY["manager_owner"],
        job_id=gate.jobs.job_id(path),
        job_path=path,
        unit=gate.jobs.UNIT,
        result=result,
    )


def completed(writer):
    writer.reply(PATH)
    writer.removed(event())
    return True


def assert_no_authority(value):
    assert value["mode"] == "inert"
    assert value["operator_recovery_required"] is True
    for name in (
        "native_binding_verified",
        "service_quiesced_verified",
        "may_disarm_recovery",
    ):
        assert value[name] is False


@pytest.mark.parametrize("inert", [False, 1, "yes", None])
def test_explicit_inert_before_directory(tmp_path, inert):
    with pytest.raises(ValueError, match="inert"):
        gate.InertJobGate.initialize(tmp_path / "session", NONCE, IDENTITY, inert=inert)
    assert not (tmp_path / "session").exists()


@pytest.mark.parametrize("before_reply", [False, True])
def test_durable_event_and_reply_orders_reopen_and_recovery(tmp_path, before_reply):
    s = session(tmp_path)
    received = event()
    retained = []

    def simulate(writer):
        assert fence.read(s.directory / "job-intent.json")["value"] == dict(
            operation="simulated_stop"
        )
        assert not (s.directory / "window-complete.json").exists()
        retained.append(writer)
        if before_reply:
            writer.removed(received)
        writer.reply(PATH)
        if not before_reply:
            writer.removed(received)
        received["result"] = "failed"
        return True

    value = s.stop(simulate, IDENTITY)
    assert value["simulated_job_done"] is True
    assert value["new_stop_requests_fenced"] is False
    assert_no_authority(value)
    s = reopen(s)
    assert s.inspect(IDENTITY)["status"] == "simulated_tracked_job_done"
    before = {path.name: path.read_bytes() for path in s.directory.glob("*.json")}
    result = s.recover(lambda: True, IDENTITY)
    assert result["new_stop_requests_fenced"] is True
    assert result["simulated_recovery_observed"] is True
    assert_no_authority(result)
    for name, data in before.items():
        assert (s.directory / name).read_bytes() == data
    assert reopen(s).inspect(IDENTITY)["simulated_job_done"] is True
    with pytest.raises(ValueError, match="scope"):
        retained[0].reply(PATH)
    with pytest.raises(ValueError, match="sealed"):
        s.stop(lambda _: pytest.fail("late callback"), IDENTITY)


@pytest.mark.parametrize("result", ["canceled", "skipped", "failed", "timeout"])
def test_non_success_persisted_never_promoted(tmp_path, result):
    s = session(tmp_path)

    def simulate(writer):
        writer.reply(PATH)
        writer.removed(event(result=result))
        return True

    assert s.stop(simulate, IDENTITY)["status"] == "simulated_job_not_successful"
    value = reopen(s).recover(lambda: True, IDENTITY)
    assert value["simulated_job_done"] is False
    assert_no_authority(value)


@pytest.mark.parametrize("missing", ["reply", "event", "both", "unrelated"])
def test_missing_or_unrelated_evidence_no_inference_from_true_callback(
    tmp_path, missing
):
    s = session(tmp_path)

    def simulate(writer):
        if missing not in {"reply", "both"}:
            writer.reply(PATH)
        if missing not in {"event", "both"}:
            writer.removed(
                event(
                    path="/org/freedesktop/systemd1/job/8"
                    if missing == "unrelated"
                    else PATH
                )
            )
        return True

    assert s.stop(simulate, IDENTITY)["status"] == "unknown"
    value = reopen(s).recover(lambda: True, IDENTITY)
    assert value["status"] == "unknown"
    assert_no_authority(value)


@pytest.mark.parametrize(
    "error", [ValueError, TimeoutError, KeyboardInterrupt, SystemExit]
)
def test_callback_failure_keeps_intent_and_never_window_completion(tmp_path, error):
    s = session(tmp_path)

    def simulate(writer):
        completed(writer)
        raise error("fixture-only")

    with pytest.raises(error):
        s.stop(simulate, IDENTITY)
    assert (s.directory / "job-intent.json").exists()
    assert not (s.directory / "window-complete.json").exists()
    assert reopen(s).inspect(IDENTITY)["status"] == "unknown"
    assert_no_authority(reopen(s).recover(lambda: True, IDENTITY))


@pytest.mark.parametrize(
    "fault",
    [
        "duplicate-reply",
        "duplicate-event",
        "wrong-unit",
        "bad-sender",
        "disconnected",
        "epoch",
    ],
)
def test_swallowed_writer_fault_sticky_across_new_instance(tmp_path, fault):
    s = session(tmp_path)

    def simulate(writer):
        completed(writer)
        try:
            if fault == "duplicate-reply":
                writer.reply(PATH)
            elif fault == "duplicate-event":
                writer.removed(event())
            elif fault in {"wrong-unit", "bad-sender"}:
                value = event(path="/org/freedesktop/systemd1/job/8")
                value["unit" if fault == "wrong-unit" else "sender"] = (
                    "other.service" if fault == "wrong-unit" else ":1.9"
                )
                writer.removed(value)
            elif fault == "disconnected":
                writer.disconnected()
            else:
                writer.check_epoch(dict(IDENTITY, manager_owner=":1.9"))
        except ValueError:
            pass
        return True

    with pytest.raises(ValueError):
        s.stop(simulate, IDENTITY)
    assert not (s.directory / "window-complete.json").exists()
    assert reopen(s).inspect(IDENTITY)["status"] == "unknown"


def test_event_overflow_preserves_32_and_latches_fault(tmp_path):
    s = session(tmp_path)

    def simulate(writer):
        for index in range(1, 34):
            writer.removed(event(path=f"/org/freedesktop/systemd1/job/{index}"))
        return True

    with pytest.raises(ValueError):
        s.stop(simulate, IDENTITY)
    assert len(list(s.directory.glob("event-*.json"))) == 32
    assert reopen(s).inspect(IDENTITY)["status"] == "unknown"


def test_integer_window_acknowledgment_is_not_exact_true(tmp_path):
    s = session(tmp_path)
    s.stop(completed, IDENTITY)
    path = s.directory / "window-complete.json"
    value = fence.read(path)
    value["value"]["continuous"] = 1
    path.write_text(json.dumps(value), encoding="utf-8")
    assert s.inspect(IDENTITY)["status"] == "unknown"


def test_duplicate_stop_and_false_ack_never_repeat_or_finish(tmp_path):
    s = session(tmp_path)
    s.stop(completed, IDENTITY)
    before = (s.directory / "job-intent.json").read_bytes()
    with pytest.raises(ValueError, match="intent"):
        reopen(s).stop(lambda _: pytest.fail("duplicate callback"), IDENTITY)
    assert (s.directory / "job-intent.json").read_bytes() == before
    other = gate.InertJobGate.initialize(
        tmp_path / "false-ack", NONCE, IDENTITY, inert=True, lock=simulated_lock
    )
    with pytest.raises(ValueError, match="acknowledgment"):
        other.stop(lambda _: False, IDENTITY)
    assert not (other.directory / "window-complete.json").exists()
    assert reopen(other).inspect(IDENTITY)["status"] == "unknown"


@pytest.mark.parametrize(
    "name,field,value",
    [
        ("job-reply.json", "nonce", "d" * 64),
        ("event-01.json", "epoch", dict(IDENTITY, manager_owner=":1.9")),
        ("window-complete.json", "extra", True),
    ],
)
def test_journal_binding_schema_change_persists_unknown(tmp_path, name, field, value):
    s = session(tmp_path)
    s.stop(completed, IDENTITY)
    path = s.directory / name
    record = fence.read(path)
    record[field] = value
    path.write_text(json.dumps(record), encoding="utf-8")
    assert s.inspect(IDENTITY)["status"] == "unknown"
    assert reopen(s).inspect(IDENTITY)["status"] == "unknown"


@pytest.mark.parametrize("field", ["boot_sha256", "bus_id", "manager_owner"])
def test_epoch_change_poison_persists_even_when_original_returns(tmp_path, field):
    s = session(tmp_path)
    s.stop(completed, IDENTITY)
    changed = dict(IDENTITY)
    changed[field] = {
        "boot_sha256": "d" * 64,
        "bus_id": "e" * 32,
        "manager_owner": ":1.9",
    }[field]
    assert s.inspect(changed)["status"] == "unknown"
    assert reopen(s).inspect(IDENTITY)["status"] == "unknown"


@pytest.mark.parametrize(
    "artifact",
    [
        "reply",
        "event",
        "window",
        "gap",
        "orphan",
        "legacy",
        "extra",
        "duplicate-json",
        "recovery",
    ],
)
def test_corruption_incomplete_history_not_repaired_by_recovery(tmp_path, artifact):
    s = session(tmp_path)
    s.stop(completed, IDENTITY)
    if artifact in {"reply", "event", "window"}:
        name = {
            "reply": "job-reply.json",
            "event": "event-01.json",
            "window": "window-complete.json",
        }[artifact]
        (s.directory / name).write_bytes(b"{incomplete")
    elif artifact == "gap":
        (s.directory / "event-01.json").rename(s.directory / "event-02.json")
    elif artifact == "orphan":
        (s.directory / "job-intent.json").unlink()
    elif artifact in {"legacy", "extra"}:
        fence.exclusive(
            s.directory
            / ("stop-complete.json" if artifact == "legacy" else "unknown.json"),
            dict(nonce=NONCE),
        )
    elif artifact == "duplicate-json":
        (s.directory / "job-reply.json").write_bytes(b'{"nonce":"bad","nonce":"bad"}')
    else:
        s._record("job-recovery.json", dict(may_disarm_recovery=True))
    assert s.inspect(IDENTITY)["status"] == "unknown"
    assert reopen(s).inspect(IDENTITY)["status"] == "unknown"
    if artifact != "recovery":
        assert_no_authority(reopen(s).recover(lambda: True, IDENTITY))


@pytest.mark.parametrize(
    "file",
    [
        "job-intent.json",
        "job-reply.json",
        "event-01.json",
        "window-complete.json",
        "fault.json",
    ],
)
def test_storage_failure_no_ack_or_retry(tmp_path, monkeypatch, file):
    s = session(tmp_path)
    original = gate.fence.exclusive

    def fail(path, value):
        if Path(path).name == file:
            raise OSError("fixture-only-storage")
        original(path, value)

    monkeypatch.setattr(gate.fence, "exclusive", fail)
    calls = []

    def simulate(writer):
        calls.append("entered")
        completed(writer)
        if file == "fault.json":
            raise ValueError("fixture-only-fault")
        return True

    with pytest.raises((OSError, ValueError)):
        s.stop(simulate, IDENTITY)
    assert calls == ([] if file == "job-intent.json" else ["entered"])
    assert not (s.directory / "window-complete.json").exists()
    assert reopen(s).inspect(IDENTITY)["status"] == "unknown"


def test_expired_or_changed_request_never_dispatches(tmp_path):
    now = [1]
    s = session(tmp_path, clock=lambda: now[0])
    now[0] = s.fence.deadline_ns
    with pytest.raises(TimeoutError):
        s.stop(lambda _: pytest.fail("expired callback"), IDENTITY)
    assert not (s.directory / "job-intent.json").exists()
    request = fence.read(s.directory / "request.json")
    request["deadline_ns"] += 1
    (s.directory / "request.json").write_text(json.dumps(request), encoding="utf-8")
    with pytest.raises(ValueError):
        s.stop(lambda _: pytest.fail("changed request"), IDENTITY)


def test_seal_before_dispatch_and_timeout_before_recovery(tmp_path):
    s = session(tmp_path)
    original = s._record

    def seal_at_intent(name, value):
        original(name, value)
        if name == "job-intent.json":
            fence.exclusive(s.directory / "sealed.json", dict(nonce=NONCE))

    s._record = seal_at_intent
    with pytest.raises(ValueError, match="sealed"):
        s.stop(lambda _: pytest.fail("seal raced dispatch"), IDENTITY)
    assert s.inspect(IDENTITY)["status"] == "unknown"


@pytest.mark.parametrize("success", [True, False])
def test_recovery_never_repeated_after_success_or_failure(tmp_path, success):
    s = session(tmp_path)
    calls = []

    def simulate():
        calls.append(1)
        return success

    if success:
        value = s.recover(simulate, IDENTITY)
        assert value["status"] == "not_dispatched"
        assert_no_authority(value)
    else:
        with pytest.raises(ValueError):
            s.recover(simulate, IDENTITY)
    with pytest.raises(FileExistsError):
        reopen(s).recover(simulate, IDENTITY)
    assert calls == [1]
    with pytest.raises(ValueError, match="sealed"):
        reopen(s).stop(lambda _: pytest.fail("late"), IDENTITY)


@pytest.mark.parametrize(
    "field,value",
    [
        ("mode", "native"),
        ("nonce", "d" * 64),
        ("unit", "other.service"),
        ("deadline_ns", True),
        ("extra", True),
    ],
)
def test_context_mismatch_refused_before_callback(tmp_path, field, value):
    s = session(tmp_path)
    path = s.directory / "job-context.json"
    context = fence.read(path)
    context[field] = value
    path.write_text(json.dumps(context), encoding="utf-8")
    with pytest.raises(ValueError):
        reopen(s)
    with pytest.raises(ValueError):
        s.stop(lambda _: pytest.fail("changed context"), IDENTITY)


def wait_marker(path, process):
    deadline = time.monotonic() + 5
    while not path.exists():
        if process.poll() is not None or time.monotonic() >= deadline:
            pytest.fail("inert worker did not reach marker")
        time.sleep(0.01)


@pytest.mark.skipif(sys.platform != "linux", reason="real guest flock/process case")
@pytest.mark.parametrize("stage", ["intent", "reply", "event"])
def test_actual_inert_worker_death_keeps_unknown_and_queued_stop_fenced(stage):
    with tempfile.TemporaryDirectory(prefix="acg-inert-job-") as scratch:
        root = Path(scratch)
        s = gate.InertJobGate.initialize(root / "session", NONCE, IDENTITY, inert=True)
        code = (
            "import sys,json,time;from pathlib import Path;"
            "from cloudguard.inert_job_gate import InertJobGate;"
            "s=InertJobGate(sys.argv[1],sys.argv[2]);e=json.loads(sys.argv[3]);"
            "p='/org/freedesktop/systemd1/job/7'\n"
            "def simulate(w):\n"
            " if sys.argv[4]!='intent':w.reply(p)\n"
            " if sys.argv[4]=='event':w.removed(dict(sender=e['manager_owner'],job_id=7,job_path=p,unit='systemd-timesyncd.service',result='done'))\n"
            " Path(sys.argv[5]).touch();time.sleep(20);return True\n"
            "s.stop(simulate,e)"
        )
        process = subprocess.Popen(
            [
                sys.executable,
                "-c",
                code,
                str(s.directory),
                NONCE,
                json.dumps(IDENTITY),
                stage,
                str(root / "entered"),
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
        )
        queued = None
        try:
            wait_marker(root / "entered", process)
            queued_code = (
                "import sys,json;from pathlib import Path;"
                "from cloudguard.inert_job_gate import InertJobGate;"
                "s=InertJobGate(sys.argv[1],sys.argv[2]);"
                "Path(sys.argv[4]).touch()\n"
                "try:s.stop(lambda w:Path(sys.argv[5]).touch() or True,json.loads(sys.argv[3]))\n"
                "except ValueError as e:\n"
                " if 'sealed' not in str(e):raise\n"
                "else:raise SystemExit(2)"
            )
            queued = subprocess.Popen(
                [
                    sys.executable,
                    "-c",
                    queued_code,
                    str(s.directory),
                    NONCE,
                    json.dumps(IDENTITY),
                    str(root / "waiting"),
                    str(root / "late-effect"),
                ],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                close_fds=True,
            )
            wait_marker(root / "waiting", queued)
            with pytest.raises(TimeoutError):
                s.recover(
                    lambda: pytest.fail("must not race holder"), IDENTITY, timeout=0.1
                )
            assert (s.directory / "sealed.json").exists()
            process.kill()
            process.wait(timeout=3)
            value = s.recover(lambda: True, IDENTITY)
            assert value["status"] == "unknown"
            assert_no_authority(value)
            assert queued.wait(timeout=3) == 0
            assert not (root / "late-effect").exists()
            assert not (s.directory / "window-complete.json").exists()
        finally:
            for child in (process, queued):
                if child is not None and child.poll() is None:
                    child.kill()
                    child.wait(timeout=3)


@pytest.mark.skipif(sys.platform != "linux", reason="real guest flock/process case")
def test_actual_inert_completed_child_replays_durable_evidence():
    with tempfile.TemporaryDirectory(prefix="acg-inert-job-") as scratch:
        s = gate.InertJobGate.initialize(
            Path(scratch) / "session", NONCE, IDENTITY, inert=True
        )
        code = (
            "import sys,json;from cloudguard.inert_job_gate import InertJobGate;"
            "s=InertJobGate(sys.argv[1],sys.argv[2]);e=json.loads(sys.argv[3]);"
            "p='/org/freedesktop/systemd1/job/7'\n"
            "def simulate(w):\n"
            " w.removed(dict(sender=e['manager_owner'],job_id=7,job_path=p,unit='systemd-timesyncd.service',result='done'));w.reply(p);return True\n"
            "s.stop(simulate,e)"
        )
        result = subprocess.run(
            [sys.executable, "-c", code, str(s.directory), NONCE, json.dumps(IDENTITY)],
            timeout=5,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
        )
        assert result.returncode == 0
        value = s.recover(lambda: True, IDENTITY)
        assert value["status"] == "simulated_tracked_job_done"
        assert_no_authority(value)
