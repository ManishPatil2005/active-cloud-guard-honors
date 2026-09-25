"""Credential-free, read-only protocol observations on explicit loopback endpoints."""

from datetime import datetime, timezone
import ipaddress
import socket
import struct
import time


def protocol_check(host, port, service, *, allowlist, timeout=2.0):
    if service not in {"redis", "postgres"}:
        raise ValueError("unsupported service")
    if not ipaddress.ip_address(host).is_loopback or (host, port) not in allowlist:
        raise ValueError("explicit loopback endpoint required")
    if isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65535:
        raise ValueError("invalid port")
    if isinstance(timeout, bool) or not 0 < timeout <= 2:
        raise ValueError("timeout must be in (0,2]")
    start = time.monotonic()
    deadline = start + timeout
    status, method = "inconclusive", None
    try:
        with socket.create_connection((host, port), timeout=timeout) as connection:

            def receive(count):
                data = b""
                while len(data) < count:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise TimeoutError()
                    connection.settimeout(remaining)
                    part = connection.recv(count - len(data))
                    if not part:
                        raise ValueError("truncated protocol response")
                    data += part
                return data

            connection.settimeout(max(0.001, deadline - time.monotonic()))
            if service == "redis":
                connection.sendall(b"*1\r\n$4\r\nPING\r\n")
                response = b""
                while not response.endswith(b"\r\n") and len(response) < 4096:
                    response += receive(1)
                if not response.endswith(b"\r\n"):
                    raise ValueError("oversized Redis response")
                if response == b"+PONG\r\n":
                    status = "ping_accepted_without_credentials"
                elif response.startswith(b"-NOAUTH "):
                    status = "authentication_required"
                elif response.startswith(b"-DENIED "):
                    status = "protected_mode_denied"
                elif response.startswith(b"-NOPERM "):
                    status = "command_not_permitted"
            else:
                # Protocol 3.0 startup only; fixed lab role/database, no PasswordMessage or SQL.
                payload = (
                    struct.pack("!I", 196608)
                    + b"user\x00postgres\x00database\x00postgres\x00\x00"
                )
                connection.sendall(struct.pack("!I", len(payload) + 4) + payload)
                kind = receive(1)
                length = struct.unpack("!I", receive(4))[0]
                if not 4 <= length <= 4096:
                    raise ValueError("invalid protocol frame size")
                payload = receive(length - 4)
                if kind == b"R" and len(payload) >= 4:
                    code = struct.unpack("!I", payload[:4])[0]
                    method = {
                        0: "authentication_ok",
                        3: "cleartext_password",
                        5: "md5",
                        10: "sasl",
                    }.get(code, "other")
                    if code == 0 and len(payload) == 4:
                        status = "startup_authentication_ok_without_credentials"
                    elif (
                        (code == 3 and len(payload) == 4)
                        or (code == 5 and len(payload) == 8)
                        or (
                            code == 10
                            and len(payload) > 6
                            and payload.endswith(b"\0\0")
                        )
                    ):
                        status = "authentication_challenge"
                elif kind == b"E":
                    status = "startup_rejected"
    except ConnectionRefusedError:
        status = "unreachable"
    except (OSError, ValueError, struct.error):
        status = "inconclusive"
    return dict(
        service=service,
        host=host,
        port=port,
        status=status,
        auth_method=method,
        observed_at=datetime.now(timezone.utc).isoformat(),
        elapsed_ms=round((time.monotonic() - start) * 1000, 3),
        credentials_sent=False,
        application_data_accessed=False,
        vulnerability_confirmed=False,
        scope="One credential-free command/startup from local-host; no public-exposure, full authorization or TLS assessment",
    )


def verify_service(compose, inventory, service):
    from .deployment import attest
    from .scanner import scan
    from .verification import file_hash

    config_hash = file_hash(compose)
    scan_report = scan(compose)
    before = attest(compose, inventory, service)
    report = dict(
        engine_version="2.2",
        scan=scan_report,
        deployment_before=before,
        service_observation=None,
        usable=False,
    )
    if (
        not before["identity_verified"]
        or config_hash != before["configuration_bytes_sha256"]
    ):
        report["reason"] = "deployment identity mismatch; no protocol probe attempted"
        return report
    endpoint = before["endpoint"]
    report["service_observation"] = protocol_check(
        endpoint["host"],
        endpoint["port"],
        service,
        allowlist={(endpoint["host"], endpoint["port"])},
    )
    after = attest(compose, inventory, service)
    report["deployment_after"] = after
    identity_fields = (
        "container_id",
        "container_started_at",
        "image_id",
        "configuration_bytes_sha256",
        "inventory_sha256",
        "compose_service_hash",
    )
    report["usable"] = after["identity_verified"] and all(
        before[k] == after[k] for k in identity_fields
    )
    report["reason"] = (
        "identity stable around observation"
        if report["usable"]
        else "identity drift; observation must not be attributed to configuration"
    )
    return report
