import copy
import io
import socket
import struct
from unittest.mock import patch, MagicMock

import pytest
from cloudguard.deployment import compare
from cloudguard.deployment import local_daemon
from cloudguard.service_probe import protocol_check, verify_service


def identity_fixture():
    spec = dict(
        command=["redis-server"],
        environment={"A": "b"},
        ports=[
            dict(target=6379, published="16379", host_ip="127.0.0.1", protocol="tcp")
        ],
    )
    container = dict(
        Id="a" * 64,
        Image="sha256:abc",
        State=dict(Running=True, StartedAt="time"),
        Config=dict(
            Cmd=["redis-server"],
            Env=["A=b"],
            Labels={
                "com.docker.compose.project": "lab",
                "com.docker.compose.service": "redis",
                "com.docker.compose.config-hash": "hash",
            },
        ),
        HostConfig=dict(Privileged=False),
        NetworkSettings=dict(
            Ports={"6379/tcp": [dict(HostIp="127.0.0.1", HostPort="16379")]}
        ),
    )
    return spec, container, dict(host="127.0.0.1", port=16379)


def test_identity_matches():
    spec, container, endpoint = identity_fixture()
    assert all(
        compare(
            spec, "lab", "redis", "hash", "sha256:abc", container, endpoint
        ).values()
    )


@pytest.mark.parametrize(
    "endpoint", ["tcp://example.org:2375", "ssh://host", "https://host"]
)
def test_remote_daemon_rejected(endpoint):
    with (
        patch.dict("os.environ", {"DOCKER_HOST": endpoint}),
        patch("cloudguard.deployment.docker") as command,
    ):
        with pytest.raises(ValueError):
            local_daemon()
    command.assert_not_called()


@pytest.mark.parametrize(
    "change",
    [
        "command",
        "environment",
        "image",
        "hash",
        "project",
        "service",
        "port",
        "privilege",
        "running",
    ],
)
def test_identity_drift_rejected(change):
    spec, container, endpoint = identity_fixture()
    if change == "command":
        container["Config"]["Cmd"] = ["different"]
    elif change == "environment":
        container["Config"]["Env"] = ["A=changed"]
    elif change == "image":
        container["Image"] = "changed"
    elif change in {"hash", "project", "service"}:
        key = "config-hash" if change == "hash" else change
        container["Config"]["Labels"]["com.docker.compose." + key] = "changed"
    elif change == "port":
        container["NetworkSettings"]["Ports"]["6379/tcp"][0]["HostIp"] = "0.0.0.0"
    elif change == "privilege":
        container["HostConfig"]["Privileged"] = True
    else:
        container["State"]["Running"] = False
    assert not all(
        compare(
            spec, "lab", "redis", "hash", "sha256:abc", container, endpoint
        ).values()
    )


def protocol_response(data, service):
    response = io.BytesIO(data)
    connection = MagicMock()
    connection.__enter__.return_value = connection
    connection.recv.side_effect = lambda count: response.read(min(count, 2))
    with patch(
        "cloudguard.service_probe.socket.create_connection", return_value=connection
    ):
        result = protocol_check(
            "127.0.0.1", 1234, service, allowlist={("127.0.0.1", 1234)}
        )
    assert connection.sendall.call_count == 1
    assert not result["credentials_sent"] and not result["application_data_accessed"]
    return result


@pytest.mark.parametrize(
    "data,status",
    [
        (b"+PONG\r\n", "ping_accepted_without_credentials"),
        (b"-NOAUTH Authentication required\r\n", "authentication_required"),
        (b"-DENIED protected mode\r\n", "protected_mode_denied"),
        (b"-NOPERM unavailable\r\n", "command_not_permitted"),
        (b"+OTHER\r\n", "inconclusive"),
        (b"+P", "inconclusive"),
    ],
)
def test_redis_protocol(data, status):
    assert protocol_response(data, "redis")["status"] == status


@pytest.mark.parametrize(
    "code,status",
    [
        (0, "startup_authentication_ok_without_credentials"),
        (3, "authentication_challenge"),
        (5, "authentication_challenge"),
        (10, "authentication_challenge"),
        (99, "inconclusive"),
    ],
)
def test_postgres_protocol(code, status):
    extra = {5: b"salt", 10: b"SCRAM-SHA-256\0\0"}.get(code, b"")
    assert (
        protocol_response(
            b"R" + struct.pack("!II", 8 + len(extra), code) + extra, "postgres"
        )["status"]
        == status
    )


@pytest.mark.parametrize(
    "data,status",
    [
        (b"E" + struct.pack("!I", 5) + b"\0", "startup_rejected"),
        (b"R" + struct.pack("!I", 99999), "inconclusive"),
        (b"R\0", "inconclusive"),
    ],
)
def test_postgres_invalid_or_rejected(data, status):
    assert protocol_response(data, "postgres")["status"] == status


@pytest.mark.parametrize(
    "error,status",
    [(ConnectionRefusedError, "unreachable"), (socket.timeout, "inconclusive")],
)
def test_network_failure(error, status):
    with patch("cloudguard.service_probe.socket.create_connection", side_effect=error):
        result = protocol_check(
            "127.0.0.1", 1234, "redis", allowlist={("127.0.0.1", 1234)}
        )
    assert result["status"] == status


def test_out_of_scope_no_network():
    with patch("cloudguard.service_probe.socket.create_connection") as connect:
        with pytest.raises(ValueError):
            protocol_check("8.8.8.8", 6379, "redis", allowlist={("8.8.8.8", 6379)})
    connect.assert_not_called()


def test_mismatch_does_not_probe(tmp_path):
    source = tmp_path / "compose.yaml"
    source.write_text("services: {}")
    with (
        patch(
            "cloudguard.deployment.attest", return_value={"identity_verified": False}
        ),
        patch("cloudguard.service_probe.protocol_check") as probe,
    ):
        result = verify_service(source, "inventory", "redis")
    probe.assert_not_called()
    assert not result["usable"]


def test_restart_during_probe_invalidates(tmp_path):
    from cloudguard.verification import file_hash

    source = tmp_path / "compose.yaml"
    source.write_text("services: {}")
    before = dict(
        identity_verified=True,
        endpoint=dict(host="127.0.0.1", port=6379),
        configuration_bytes_sha256=file_hash(source),
        inventory_sha256="inventory",
        compose_service_hash="hash",
        container_id="a",
        container_started_at="first",
        image_id="image",
    )
    after = copy.deepcopy(before)
    after["container_started_at"] = "second"
    with (
        patch("cloudguard.deployment.attest", side_effect=[before, after]),
        patch(
            "cloudguard.service_probe.protocol_check",
            return_value={"status": "authentication_required"},
        ),
    ):
        result = verify_service(source, "inventory", "redis")
    assert not result["usable"] and result["service_observation"]
