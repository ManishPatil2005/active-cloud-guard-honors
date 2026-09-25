"""Read-only local Compose identity checks; trusts the local Docker daemon."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess

from .verification import file_hash, load_inventory

SERVICES = {"redis": 6379, "postgres": 5432}


def local_daemon():
    override = os.environ.get("DOCKER_HOST")
    if override and not override.startswith(("npipe://", "unix:///")):
        raise ValueError("remote Docker endpoints are outside this lab")
    endpoint = json.loads(
        docker("context", "inspect", "--format", "{{json .Endpoints.docker.Host}}")
    )
    if not isinstance(endpoint, str) or not endpoint.startswith(
        ("npipe://", "unix:///")
    ):
        raise ValueError("local Docker socket context required")


def docker(*arguments):
    result = subprocess.run(
        ["docker", *arguments], capture_output=True, text=True, timeout=20, check=False
    )
    if result.returncode:
        # Docker output can contain sensitive resolved config: never echo it.
        raise ValueError("Docker identity command failed; no verified identity")
    if len(result.stdout) > 2_000_000:
        raise ValueError("Docker identity response too large")
    return result.stdout


def compare(spec, project, service, config_hash, expected_image, container, endpoint):
    labels = container["Config"].get("Labels") or {}
    env = dict(
        item.split("=", 1) for item in container["Config"].get("Env", []) if "=" in item
    )
    expected_env = spec.get("environment", {})
    desired_ports = {
        f"{p['target']}/{p.get('protocol', 'tcp')}": [
            (p.get("host_ip"), str(p.get("published")))
        ]
        for p in spec.get("ports", [])
    }
    actual_ports = {
        key: sorted((v["HostIp"], v["HostPort"]) for v in values)
        for key, values in container["NetworkSettings"].get("Ports", {}).items()
        if values
    }
    target = f"{SERVICES[service]}/tcp"
    return dict(
        running=container["State"].get("Running") is True,
        compose_project=labels.get("com.docker.compose.project") == project,
        compose_service=labels.get("com.docker.compose.service") == service,
        compose_hash=labels.get("com.docker.compose.config-hash") == config_hash,
        image_identity=container["Image"] == expected_image,
        command=spec.get("command") is None
        or container["Config"].get("Cmd") == spec["command"],
        entrypoint=spec.get("entrypoint") is None
        or container["Config"].get("Entrypoint") == spec["entrypoint"],
        declared_environment=all(env.get(k) == str(v) for k, v in expected_env.items()),
        port_bindings=actual_ports == desired_ports,
        inventory_binding=actual_ports.get(target)
        == [(endpoint["host"], str(endpoint["port"]))],
        loopback_only=all(
            host in {"127.0.0.1", "::1"}
            for values in actual_ports.values()
            for host, _ in values
        ),
        unprivileged=container["HostConfig"].get("Privileged") is False,
    )


def attest(compose, inventory, service):
    if service not in SERVICES:
        raise ValueError("only Redis/PostgreSQL lab services are supported")
    local_daemon()
    compose = Path(compose).resolve()
    before = file_hash(compose)
    entries, inventory_hash = load_inventory(inventory)
    asset = "compose/" + service
    if asset not in entries:
        raise ValueError("service missing from explicit inventory")
    prefix = ("compose", "-f", str(compose))
    resolved = json.loads(docker(*prefix, "config", "--format", "json"))
    spec = resolved["services"][service]
    hash_lines = docker(*prefix, "config", "--hash", service).splitlines()
    hashes = [
        line.split()[1]
        for line in hash_lines
        if len(line.split()) == 2 and line.split()[0] == service
    ]
    if len(hashes) != 1 or not re.fullmatch(r"[0-9a-f]{64}", hashes[0]):
        raise ValueError("ambiguous service config identity")
    ids = docker(*prefix, "ps", "-q", service).split()
    if len(ids) != 1 or not re.fullmatch(r"[0-9a-f]{12,64}", ids[0]):
        raise ValueError("exactly one running service container required")
    container = json.loads(docker("inspect", ids[0]))[0]
    expected_image = json.loads(docker("image", "inspect", spec["image"]))[0]["Id"]
    checks = compare(
        spec,
        resolved["name"],
        service,
        hashes[0],
        expected_image,
        container,
        entries[asset],
    )
    checks["configuration_unchanged"] = file_hash(compose) == before
    # Re-resolve to detect ordinary environment/config changes during collection.
    checks["resolved_configuration_unchanged"] = (
        json.loads(docker(*prefix, "config", "--format", "json")) == resolved
    )
    return dict(
        asset_id=asset,
        service=service,
        endpoint=entries[asset],
        configuration_bytes_sha256=before,
        inventory_sha256=inventory_hash,
        compose_service_hash=hashes[0],
        container_id=container["Id"],
        image_id=container["Image"],
        container_started_at=container["State"]["StartedAt"],
        observed_at=datetime.now(timezone.utc).isoformat(),
        checks=checks,
        identity_verified=all(checks.values()),
        scope="Local Docker/Compose identity and declared runtime fields; not cryptographic attestation, mounted-file content or application-state equivalence",
    )
