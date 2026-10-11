"""Mock lifecycle only: no Falco, Docker or Redis commands executed."""

import json
import io
import tarfile

import pytest

from cloudguard.process_runner import (
    BinaryProcessResult,
    BoundedProcessError,
    ProcessResult,
)
from scripts import window_sensor as module

TARGET = "a" * 64
SENSOR = "c" * 64


class Daemon:
    def __init__(self, mode="normal"):
        self.mode = mode
        self.calls = []
        self.running = True
        self.lease = None

    def __call__(self, argv, **kwargs):
        self.calls.append((argv, kwargs))
        args = argv[3:]
        if args[0] == "inspect" and args[-1] == TARGET:
            value = dict(
                id=TARGET,
                image="sha256:" + "b" * 64,
                started_at="2026-10-11T00:00:00Z",
                running=True,
                restarts=0,
                project="honors-cloud-guard",
                service="redis",
            )
            return ProcessResult(0, json.dumps(value), "")
        if args[0] == "run":
            if self.mode in ("launch_timeout", "absent_timeout"):
                raise BoundedProcessError(
                    "timeout", b"private", reaped=True, pipes_closed=True
                )
            return ProcessResult(0, SENSOR + "\n", "")
        if args[0] == "inspect":
            if self.mode == "absent_timeout":
                return ProcessResult(1, "", "private")
            value = dict(
                id=SENSOR,
                name="/" + self.lease._name,
                image=module.IMAGE,
                running=self.running,
                nonce=self.lease._nonce,
            )
            if self.mode in ("nonce", "name", "image", "id", "running_type"):
                field = "running" if self.mode == "running_type" else self.mode
                value[field] = 1 if field == "running" else "other"
            return ProcessResult(0, json.dumps(value), "")
        if args[0] == "stop":
            if self.mode == "stop_failed":
                return ProcessResult(1, "private", "")
            if self.mode != "still_running":
                self.running = False
            return ProcessResult(0, SENSOR, "")
        if args[0] == "rm":
            if self.mode == "remove_failed":
                return ProcessResult(1, "private", "")
            return ProcessResult(0, SENSOR, "")
        if args[0] == "logs":
            if self.mode == "oversize_log":
                return ProcessResult(0, "x" * 1_000_001, "")
            return ProcessResult(0, "saved raw\n", "saved stderr\n")
        if args[0] == "cp":
            data = b'{"metrics":"uninterpreted raw"}\n'
            archive = io.BytesIO()
            with tarfile.open(
                fileobj=archive, mode="w", format=tarfile.GNU_FORMAT
            ) as bundle:
                member = tarfile.TarInfo(
                    "wrong" if self.mode == "bad_archive" else "acg-metrics.jsonl"
                )
                if self.mode == "empty_metrics":
                    data = b""
                elif self.mode == "oversize_metrics":
                    data = b"x" * 900_001
                member.size = len(data)
                if self.mode == "binary_archive":
                    member.uid = 2**40  # GNU base-256 header, invalid UTF-8.
                if self.mode == "link_metrics":
                    member.type = tarfile.SYMTYPE
                    member.linkname = "/etc/passwd"
                    member.size = 0
                bundle.addfile(member, io.BytesIO(data))
                if self.mode == "multiple_metrics":
                    other = tarfile.TarInfo("extra")
                    bundle.addfile(other)
            assert kwargs["binary"] is True
            return BinaryProcessResult(0, archive.getvalue(), b"")
        if args[0] == "ps":
            return ProcessResult(0, SENSOR if self.mode == "still_present" else "", "")
        raise AssertionError("unplanned command")


@pytest.fixture
def factory(tmp_path, monkeypatch):
    monkeypatch.delenv("DOCKER_HOST", raising=False)
    monkeypatch.delenv("DOCKER_CONTEXT", raising=False)
    config = module.read_bytes(module.ROOT / "testbed/falco-trial.yaml")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    (tmp_path / "testbed").mkdir()
    (tmp_path / "testbed/falco-trial.yaml").write_bytes(config)

    def build(mode="normal"):
        daemon = Daemon(mode)
        lease = module.SensorLease(TARGET, "unix:///var/run/docker.sock", runner=daemon)
        daemon.lease = lease
        return lease, daemon

    return build


def test_fixed_runtime_and_owned_cleanup(factory):
    lease, daemon = factory()
    report = lease.start(approved=True)
    assert report["launch_confirmed"] is True
    assert report["status"] == "launched_not_ready"
    launch = next(argv for argv, _ in daemon.calls if "run" in argv)
    assert launch[launch.index("--pull") + 1] == "never"
    assert launch[launch.index("--network") + 1] == "none"
    assert launch[launch.index(module.IMAGE) + 1 :][:6] == [
        "-s",
        "TERM",
        "-k",
        "3",
        "150",
        "/usr/bin/falco",
    ]
    assert launch[launch.index("-M") + 1] == "140"
    assert "--privileged" not in launch and not any(
        "docker.sock" in arg for arg in launch[3:]
    )
    report = lease.cleanup()
    assert report["cleanup_verified"] is True
    assert "raw_log_sha256" in report and "metrics_raw_sha256" in report
    assert report["collector_coverage"] == "not_verified"
    stops = [argv for argv, _ in daemon.calls if "stop" in argv or "rm" in argv]
    assert all(argv[-1] == SENSOR for argv in stops)
    count = len(daemon.calls)
    lease.cleanup()
    assert len(daemon.calls) == count
    with pytest.raises(module.SensorRejected):
        lease.start(approved=True)


def test_binary_tar_header_is_preserved_without_text_decoding(factory):
    lease, daemon = factory("binary_archive")
    lease.start(approved=True)
    report = lease.cleanup()
    assert report["cleanup_verified"] is True
    assert "metrics_raw_sha256" in report


@pytest.mark.parametrize("approval", [False, None, 1, "yes"])
def test_no_implicit_authority(factory, approval):
    lease, daemon = factory()
    with pytest.raises(module.SensorRejected):
        lease.start(approved=approval)
    assert daemon.calls == []


@pytest.mark.parametrize("mode", ["nonce", "name", "image", "id", "running_type"])
def test_foreign_or_malformed_sensor_never_stopped(factory, mode):
    lease, daemon = factory(mode)
    with pytest.raises(module.SensorRejected):
        lease.start(approved=True)
    assert lease.snapshot()["cleanup_verified"] is False
    assert not any(argv[3] in ("stop", "rm") for argv, _ in daemon.calls)


@pytest.mark.parametrize("mode", ["launch_timeout", "absent_timeout"])
def test_uncertain_launch_never_becomes_verified_cleanup(factory, mode):
    lease, daemon = factory(mode)
    with pytest.raises(module.SensorRejected):
        lease.start(approved=True)
    report = lease.snapshot()
    assert report["launch_completion_uncertain"] is True
    assert report["cleanup_attempted"] is True
    assert report["cleanup_verified"] is False
    assert report["removal_observed"] is (mode == "launch_timeout")
    assert sum(argv[3] == "run" for argv, _ in daemon.calls) == 1
    assert "private" not in str(report)


@pytest.mark.parametrize(
    "mode", ["stop_failed", "still_running", "remove_failed", "still_present"]
)
def test_cleanup_failures_preserved_and_not_retried(factory, mode):
    lease, daemon = factory(mode)
    lease.start(approved=True)
    report = lease.cleanup()
    assert report["cleanup_verified"] is False
    assert report["faults"]
    count = len(daemon.calls)
    lease.cleanup()
    assert len(daemon.calls) == count
    if mode in ("stop_failed", "still_running"):
        assert not any(argv[3] == "rm" for argv, _ in daemon.calls)


def test_changed_config_blocks_launch(factory):
    lease, daemon = factory()
    (module.ROOT / "testbed/falco-trial.yaml").write_bytes(b"changed")
    with pytest.raises(module.SensorRejected):
        lease.start(approved=True)
    assert not any(argv[3] == "run" for argv, _ in daemon.calls)
    assert lease.snapshot()["cleanup_attempted"] is False


def test_cleanup_seals_unused_lease(factory):
    lease, daemon = factory()
    lease.cleanup()
    with pytest.raises(module.SensorRejected):
        lease.start(approved=True)
    assert daemon.calls == []


def test_nonce_directory_collision_preserves_existing_files(factory):
    lease, daemon = factory()
    directory = module.ROOT / "output/runtime-raw" / lease._name
    directory.mkdir(parents=True)
    kept = directory / "rules.yaml"
    kept.write_bytes(b"historical")
    with pytest.raises(FileExistsError):
        lease.start(approved=True)
    assert kept.read_bytes() == b"historical"
    assert not any(argv[3] == "run" for argv, _ in daemon.calls)


def test_snapshot_does_not_expose_mutable_internal_evidence(factory):
    lease, daemon = factory()
    report = lease.start(approved=True)
    report["commands"].clear()
    assert lease.snapshot()["commands"]
    lease.cleanup()


def test_failed_export_preserves_stopped_container_and_partial_raw(factory):
    lease, daemon = factory("bad_archive")
    lease.start(approved=True)
    report = lease.cleanup()
    assert report["cleanup_verified"] is False
    assert "raw_log_sha256" in report
    assert "metrics_raw_sha256" not in report
    assert daemon.running is False
    assert not any(argv[3] == "rm" for argv, _ in daemon.calls)


@pytest.mark.parametrize(
    "mode",
    [
        "oversize_log",
        "empty_metrics",
        "oversize_metrics",
        "link_metrics",
        "multiple_metrics",
    ],
)
def test_export_limits_no_archive_extraction_or_unsafe_remove(factory, mode):
    lease, daemon = factory(mode)
    lease.start(approved=True)
    report = lease.cleanup()
    assert report["cleanup_verified"] is False
    assert daemon.running is False
    assert not any(argv[3] == "rm" for argv, _ in daemon.calls)
    assert not (module.ROOT / "etc/passwd").exists()
