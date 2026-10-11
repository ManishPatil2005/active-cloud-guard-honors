"""Mock Docker boundary, real existing direct-client supervisor tests separate."""

import copy
import json
from unittest.mock import Mock

import pytest

from cloudguard.process_runner import BoundedProcessError, ProcessResult
from scripts.window_transport import (
    RedisWindowTransport,
    TransportRejected,
    PING_SCRIPT,
)
from scripts.window_workload import run

CONTAINER = "a" * 64
ENDPOINT = "unix:///var/run/docker.sock"


@pytest.fixture(autouse=True)
def no_overrides(monkeypatch):
    monkeypatch.delenv("DOCKER_HOST", raising=False)
    monkeypatch.delenv("DOCKER_CONTEXT", raising=False)


def identity():
    return dict(
        id=CONTAINER,
        image="sha256:" + "b" * 64,
        started_at="2026-10-11T00:00:00Z",
        running=True,
        restarts=0,
        project="honors-cloud-guard",
        service="redis",
    )


def transport(reply=ProcessResult(0, "123\nPONG\n", "")):
    runner = Mock(side_effect=[ProcessResult(0, json.dumps(identity()), ""), reply])
    client = RedisWindowTransport(CONTAINER, ENDPOINT, runner=runner)
    client.check_identity()
    return client, runner


def test_fixed_command_deadline_and_selected_identity():
    client, runner = transport()
    assert client.ping() == "PONG"
    args, kwargs = runner.call_args
    assert args[0] == [
        "docker",
        "--host",
        ENDPOINT,
        "exec",
        CONTAINER,
        "/bin/sh",
        "-c",
        PING_SCRIPT,
    ]
    assert kwargs == dict(timeout=0.5, output_limit=128)
    saved = client.snapshot()
    assert saved["attempts"] == [dict(index=0, status="completed", pid=123)]
    saved["before"]["running"] = False
    assert client.snapshot()["before"]["running"] is True
    assert saved["remote_exec_completion_verified"] is False


@pytest.mark.parametrize(
    "endpoint",
    [
        "tcp://example.com:2375",
        "ssh://host",
        "unix://relative",
        "unix:///../sock",
        "unix:///var//sock",
        "unix:///var/./sock",
        "unix:///sock\x00",
        "npipe:////./pipe/docker_engine",
        None,
    ],
)
def test_bad_endpoint_never_invokes_runner(endpoint):
    runner = Mock()
    with pytest.raises(ValueError):
        RedisWindowTransport(CONTAINER, endpoint, runner=runner)
    runner.assert_not_called()


@pytest.mark.parametrize("container", [None, True, "redis", "A" * 64, "a" * 63])
def test_bad_container_refused(container):
    with pytest.raises(ValueError):
        RedisWindowTransport(container, ENDPOINT)


def test_identity_required_before_ping_and_fault_sticky():
    runner = Mock()
    client = RedisWindowTransport(CONTAINER, ENDPOINT, runner=runner)
    with pytest.raises(TransportRejected):
        client.ping()
    with pytest.raises(TransportRejected):
        client.check_identity()
    runner.assert_not_called()


@pytest.mark.parametrize(
    "field,value",
    [
        ("running", 1),
        ("restarts", True),
        ("id", "b" * 64),
        ("project", "other"),
        ("service", "nginx"),
        ("image", "redis:latest"),
        ("started_at", []),
        ("restarts", -1),
    ],
)
def test_invalid_identity_refused(field, value):
    changed = identity()
    changed[field] = value
    runner = Mock(return_value=ProcessResult(0, json.dumps(changed), ""))
    client = RedisWindowTransport(CONTAINER, ENDPOINT, runner=runner)
    with pytest.raises(TransportRejected):
        client.check_identity()
    assert client.snapshot()["fault"]["code"] == "invalid_target_identity"


@pytest.mark.parametrize(
    "reply",
    [
        ProcessResult(1, "private", ""),
        ProcessResult(False, "123\nPONG", ""),
        ProcessResult(0, "123\nPONG", "warning"),
        ProcessResult(0, "x" * 129, ""),
        ProcessResult(0, "\ud800", ""),
        ProcessResult(0, "PONG", ""),
        ProcessResult(0, "0\nPONG", ""),
        ProcessResult(0, "123\nPONG\nextra", ""),
        None,
    ],
)
def test_bad_reply_stops_retries_without_raw_diagnostic(reply):
    client, runner = transport(reply)
    with pytest.raises(TransportRejected):
        client.ping()
    with pytest.raises(TransportRejected):
        client.ping()
    assert runner.call_count == 2
    assert client.snapshot()["attempts"][0]["status"] == "rejected"
    assert "private" not in str(client.snapshot())


def test_timeout_records_cleanup_but_not_remote_completion():
    client, runner = transport()
    runner.side_effect = BoundedProcessError(
        "timeout", b"private", reaped=True, pipes_closed=True
    )
    with pytest.raises(TransportRejected):
        client.ping()
    fault = client.snapshot()["fault"]
    assert fault == dict(
        code="client_timeout",
        direct_child_reaped=True,
        pipes_closed=True,
        external_job_completion_verified=False,
    )
    assert "private" not in str(client.snapshot())


def test_duplicate_pid_rejected():
    client, runner = transport()
    assert client.ping() == "PONG"
    runner.side_effect = None
    runner.return_value = ProcessResult(0, "123\nPONG", "")
    with pytest.raises(TransportRejected):
        client.ping()
    assert client.snapshot()["fault"]["code"] == "duplicate_pid"


def test_post_identity_change_retained_and_blocks_more_calls():
    client, runner = transport()
    after = copy.deepcopy(identity())
    after["restarts"] = 1
    runner.side_effect = None
    runner.return_value = ProcessResult(0, json.dumps(after), "")
    with pytest.raises(TransportRejected):
        client.check_identity()
    assert client.snapshot()["after"]["restarts"] == 1
    with pytest.raises(TransportRejected):
        client.ping()


@pytest.mark.parametrize("variable", ["DOCKER_CONTEXT", "DOCKER_HOST"])
def test_environment_change_refused_before_client_launch(variable, monkeypatch):
    client, runner = transport()
    monkeypatch.setenv(variable, "remote")
    with pytest.raises(TransportRejected):
        client.ping()
    assert runner.call_count == 1


def test_full_scheduler_transport_pair_and_budget_no_real_docker():
    now = [0]
    pids = [100]

    def runner(argv, **kwargs):
        if "inspect" in argv:
            return ProcessResult(0, json.dumps(identity()), "")
        now[0] += 10_000_000
        pids[0] += 1
        return ProcessResult(0, f"{pids[0]}\nPONG\n", "")

    client = RedisWindowTransport(CONTAINER, ENDPOINT, runner=runner)
    client.check_identity()

    def sleep(seconds):
        now[0] += round(seconds * 10**9)

    report = run(
        client.ping,
        monotonic_ns=lambda: now[0],
        wall_ns=lambda: now[0] + 10**18,
        sleep=sleep,
    )
    assert report["status"] == "completed"
    client.check_identity()
    assert client.snapshot()["before"] == client.snapshot()["after"]
    assert len(client.snapshot()["attempts"]) == 60
    with pytest.raises(TransportRejected):
        client.ping()
    assert pids[0] == 160
