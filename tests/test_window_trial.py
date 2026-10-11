"""Virtual end-to-end lifecycle; no real Docker, Redis or sensor operation."""

from datetime import datetime, timezone
import json
from pathlib import Path

import pytest

from cloudguard.sensor_adapter import RULE
from scripts import window_trial as module

TARGET = "a" * 64
ENDPOINT = "unix:///var/run/docker.sock"


class Clock:
    def __init__(self):
        self.now = 0
        self.epoch = 1_791_676_801_000_000_000

    def mono(self):
        return self.now

    def wall(self):
        return self.epoch + self.now

    def sleep(self, seconds):
        self.now += round(seconds * 1e9)


def event(pid, stamp):
    seconds, fraction = divmod(stamp, 10**9)
    return dict(
        hostname="synthetic",
        output="private",
        priority="Informational",
        rule=RULE,
        source="syscall",
        tags=[],
        time=datetime.fromtimestamp(seconds, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        + f".{fraction:09d}Z",
        output_fields={
            "evt.rawres": 0,
            "evt.rawtime": stamp,
            "evt.time": stamp,
            "evt.type": "connect",
            "thread.cgroups": "/docker/" + TARGET,
            "proc.vpid": pid,
        },
    )


class Lab:
    def __init__(self, path, mode="normal"):
        self.clock = Clock()
        self.path = path
        self.mode = mode
        self.events = []
        self.clients = []
        self.starts = 0
        self.cleanups = 0
        self.pid = 100
        self.first = self.clock.wall()
        self.report = dict(
            launch_confirmed=False,
            cleanup_verified=False,
            recovery=dict(raw_directory=str(path)),
        )
        self.redis = self.transport(TARGET, ENDPOINT)

    def transport(self, target, endpoint):
        assert target == TARGET and endpoint == ENDPOINT
        lab = self

        class Client:
            def __init__(self):
                self.attempts = []
                self.before = None
                self.after = None
                self.fault = None

            def check_identity(self):
                identity = dict(id=TARGET, running=True)
                if self.before is None:
                    self.before = identity
                else:
                    self.after = identity
                if lab.mode == "identity" and len(self.attempts) == 60:
                    raise ValueError("identity changed")
                return identity

            def ping(self):
                lab.pid += 1
                self.attempts.append(
                    dict(index=len(self.attempts), pid=lab.pid, status="completed")
                )
                if lab.mode == "interrupt" and lab.pid == 105:
                    raise KeyboardInterrupt
                if lab.mode == "ping" and lab.pid == 105:
                    self.attempts[-1]["status"] = "rejected"
                    self.fault = "injected"
                    raise ValueError("private error")
                lab.clock.now += 10_000_000
                lab.events.append(event(lab.pid, lab.clock.wall()))
                return "PONG"

            def snapshot(self):
                return json.loads(
                    json.dumps(
                        dict(
                            before=self.before,
                            after=self.after,
                            attempts=self.attempts,
                            fault=self.fault,
                        )
                    )
                )

        client = Client()
        self.clients.append(client)
        return client

    def start(self, approved=False):
        assert approved is True
        self.starts += 1
        if self.mode == "launch":
            raise RuntimeError("private failed launch")
        self.redis.check_identity()
        self.report["launch_confirmed"] = True

    def observe_log(self):
        if self.mode == "readiness":
            return b""
        if self.mode == "canary_offset":
            self.events[-1] = event(self.pid, self.clock.wall() - 20_000_000_000)
        return self.raw()

    def raw(self):
        return ("\n".join(json.dumps(row) for row in self.events) + "\n").encode()

    def snapshot(self):
        return json.loads(json.dumps(self.report))

    def cleanup(self):
        self.cleanups += 1
        if self.mode == "cleanup":
            return self.snapshot()
        self.path.mkdir()
        if self.mode == "missing_event":
            self.events.pop()
        if self.mode == "duplicate":
            self.events.append(self.events[-1])
        if self.mode == "offset":
            last = self.events[-1]
            self.events[-1] = event(
                last["output_fields"]["proc.vpid"],
                last["output_fields"]["evt.rawtime"] - 2_000_000_000,
            )
        raw = self.raw()
        (self.path / "sensor.log").write_bytes(raw)
        rows = []
        for n, stamp in enumerate(range(self.first, self.clock.wall() + 1, 10**9)):
            rows.append(
                dict(
                    output_fields={
                        "evt.time": stamp,
                        "falco.duration_sec": n,
                        "scap.n_evts": n * 100,
                        "scap.n_drops": 0,
                        "falco.outputs_queue_num_drops": 0,
                    }
                )
            )
        if self.mode == "drops":
            rows[-1]["output_fields"]["scap.n_drops"] = 1
        if self.mode == "metrics_gap":
            rows = rows[:1] + rows[-1:]
        if self.mode == "unbracketed":
            rows = rows[:-5]
        metrics = "\n".join(json.dumps(row) for row in rows).encode()
        (self.path / "metrics.jsonl").write_bytes(metrics)
        self.report.update(
            cleanup_verified=True,
            raw_log_sha256=module.digest(raw),
            metrics_raw_sha256=module.digest(metrics),
        )
        return self.snapshot()

    def execute(self, directory):
        return module.execute(
            directory,
            TARGET,
            ENDPOINT,
            approved=True,
            lease_factory=lambda *_: self,
            transport_factory=self.transport,
            monotonic_ns=self.clock.mono,
            wall_ns=self.clock.wall,
            sleep=self.clock.sleep,
        )


@pytest.fixture
def lab(tmp_path, monkeypatch):
    monkeypatch.setattr(module, "sources", lambda: {"synthetic_source": "b" * 64})
    return Lab(tmp_path / "raw")


def test_virtual_end_to_end_journal_and_full_selected_checks(lab, tmp_path):
    path = tmp_path / "journal"
    report = lab.execute(path)
    assert report["status"] == "development_checks_passed"
    assert lab.starts == lab.cleanups == 1
    assert len(lab.events) == 62
    assert report["capture_checks"]["matched_commands"] == 60
    assert report["capture_checks"]["full_telemetry_completeness_verified"] is False
    assert (
        report["independent_evaluation_verified"] is report["labels_created"] is False
    )
    review = module.review_journal(path)
    assert review["status"] == "terminal_record_present"
    assert review["last"]["payload"] == report
    assert review["authenticated"] is False
    assert review["valid_records"] == 132


@pytest.mark.parametrize(
    "mode",
    [
        "launch",
        "readiness",
        "ping",
        "interrupt",
        "identity",
        "cleanup",
        "missing_event",
        "duplicate",
        "offset",
        "drops",
        "metrics_gap",
        "unbracketed",
        "canary_offset",
    ],
)
def test_failed_phases_preserved_no_replacement(mode, lab, tmp_path):
    lab.mode = mode
    report = lab.execute(tmp_path / "journal")
    assert report["status"] == "rejected"
    assert lab.starts == lab.cleanups == 1
    assert report["faults"]
    assert "private" not in json.dumps(report)
    assert (
        module.review_journal(tmp_path / "journal")["status"]
        == "terminal_record_present"
    )
    if mode in {"launch", "readiness"}:
        assert len(lab.clients) == 1
    if mode == "ping":
        assert report["workload"]["attempted_calls"] == 3
        assert report["workload"]["unattempted_calls"] == 57


@pytest.mark.parametrize("approval", [False, None, 1, "yes"])
def test_explicit_approval_before_artifacts(tmp_path, approval):
    with pytest.raises(ValueError):
        module.execute(tmp_path / "journal", TARGET, ENDPOINT, approved=approval)
    assert not (tmp_path / "journal").exists()


def test_existing_journal_refused_before_launch(lab, tmp_path):
    path = tmp_path / "journal"
    path.mkdir()
    marker = path / "historical"
    marker.write_bytes(b"keep")
    with pytest.raises(FileExistsError):
        lab.execute(path)
    assert marker.read_bytes() == b"keep" and lab.starts == lab.cleanups == 0


def test_source_changes_reject_after_owned_cleanup(lab, tmp_path, monkeypatch):
    calls = []

    def changed():
        calls.append(1)
        return {"source": str(len(calls))}

    monkeypatch.setattr(module, "sources", changed)
    report = lab.execute(tmp_path / "journal")
    assert report["source_unchanged"] is False
    assert report["status"] == "rejected" and lab.cleanups == 1


def test_storage_failure_still_attempts_cleanup(lab, tmp_path, monkeypatch):
    original = module.Journal.record

    def fail(self, phase, payload):
        if phase in {"ping_result", "cleanup_intent", "terminal"}:
            raise OSError("private disk failure")
        return original(self, phase, payload)

    monkeypatch.setattr(module.Journal, "record", fail)
    report = lab.execute(tmp_path / "journal")
    assert report["status"] == "journal_failed_operator_review_required"
    assert lab.cleanups == 1
    assert module.review_journal(tmp_path / "journal")["status"] == "incomplete"


@pytest.mark.parametrize(
    "mode", ["partial", "edited", "missing", "after_terminal", "not_int"]
)
def test_recovery_never_accepts_broken_chain(tmp_path, mode):
    journal = module.Journal(tmp_path / "journal")
    journal.record("intent", {})
    journal.record("terminal", {"status": "rejected"})
    first = journal.path / "000.json"
    if mode == "partial":
        (journal.path / "001.json").write_bytes(b"{")
    elif mode == "edited":
        first.write_bytes(first.read_bytes().replace(b"intent", b"changed"))
    elif mode == "missing":
        first.unlink()
    elif mode == "not_int":
        first.write_bytes(
            first.read_bytes().replace(b'"sequence": 0', b'"sequence": false')
        )
    else:
        (journal.path / "002.json").write_text(
            json.dumps(
                dict(
                    sequence=2,
                    previous_sha256=journal.previous,
                    phase="more",
                    payload={},
                )
            )
        )
    report = module.review_journal(journal.path)
    assert report["status"] == "invalid"
    assert (
        report["operator_review_required"] is True and report["actions_executed"] == []
    )


def test_journal_seal_and_oversize_refusal(tmp_path):
    journal = module.Journal(tmp_path / "journal")
    with pytest.raises(ValueError):
        journal.record("intent", {"large": "x" * 300_001})
    assert list(journal.path.iterdir()) == []
    journal.record("intent", {})
    journal.record("terminal", {})
    with pytest.raises(ValueError):
        journal.record("intent", {})


def test_clock_jump_blocks_measurement(lab, tmp_path):
    original = lab.clock.sleep

    def jump(seconds):
        original(seconds)
        if seconds == 0.5:
            lab.clock.epoch += 1_000_000_000

    lab.clock.sleep = jump
    report = lab.execute(tmp_path / "journal")
    assert report["status"] == "rejected" and lab.cleanups == 1
    assert report["workload"] is None


def test_rejected_alignment_retains_end_sample_and_reason(lab, tmp_path):
    original = lab.clock.sleep

    def jump(seconds):
        original(seconds)
        if seconds == 0.5:
            lab.clock.epoch += 1_000_000_000

    lab.clock.sleep = jump
    lab.execute(tmp_path / "journal")
    records = [
        json.loads(path.read_text())
        for path in sorted((tmp_path / "journal").iterdir())
    ]
    observed = [row["payload"] for row in records if row["phase"] == "alignment_result"]
    assert len(observed) == 1
    assert observed[0]["last"]["wall_ns"] > observed[0]["boundary_ns"]
    assert observed[0]["accepted"] is False
    assert "clock_disagreement" in observed[0]["reasons"]


def test_metrics_hash_change_fails_before_acceptance(lab, tmp_path, monkeypatch):
    original = module.summarize

    def changed(path, expected):
        result = original(path, expected)
        Path(path).write_bytes(b"{}")
        return result

    monkeypatch.setattr(module, "summarize", changed)
    report = lab.execute(tmp_path / "journal")
    assert report["status"] == "rejected" and lab.cleanups == 1


@pytest.mark.parametrize("offset", [-200_000_000, 200_000_000, 0])
def test_alignment_returns_complete_numeric_evidence_without_correction(offset):
    clock = Clock()
    first = module.sample(clock.mono, clock.wall)
    boundary = (first["wall_ns"] // module.MINUTE + 1) * module.MINUTE
    clock.epoch += offset
    report = module.wait_alignment(
        first, boundary, monotonic_ns=clock.mono, wall_ns=clock.wall, sleep=clock.sleep
    )
    assert report["boundary_error_ns"] == offset
    assert report["timing"]["clock_difference_ns"] == offset
    assert report["accepted"] is (offset == 0)
    assert report["last"]["wall_ns"] == boundary + offset


def test_sensor_free_diagnostic_never_constructs_transport(tmp_path, monkeypatch):
    monkeypatch.setattr(module, "sources", lambda: {"synthetic_source": "0" * 64})
    monkeypatch.setattr(module, "wait_alignment", lambda *_: {"accepted": False})

    def forbid(*_, **__):
        raise AssertionError("no sensor or Docker in clock-only observation")

    monkeypatch.setattr(module, "SensorLease", forbid)
    monkeypatch.setattr(module, "RedisWindowTransport", forbid)
    report = module.alignment_diagnostic(tmp_path / "journal")
    assert report["status"] == "rejected"
    assert report["sensor_or_workload_executed"] is False
    assert module.review_journal(tmp_path / "journal")["valid_records"] == 3
