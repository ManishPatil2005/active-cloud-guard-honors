"""Generate transparent DEVELOPMENT fixtures, never pretend these are held-out data."""

import hashlib
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def main():
    directory = ROOT / "data" / "development"
    directory.mkdir(parents=True, exist_ok=True)
    labels = []

    def save(name, text, rules, family):
        (directory / name).write_text(text, encoding="utf-8", newline="\n")
        labels.append(
            dict(
                id=name,
                path=f"data/development/{name}",
                expected_rules=sorted(rules),
                family=family,
                split="development",
                sha256=hashlib.sha256(text.encode()).hexdigest(),
                label_basis="manually specified seeded policy predicate; not real-world vulnerability ground truth",
            )
        )

    for app, port in [
        ("redis", 6379),
        ("postgres", 5432),
        ("nginx", 80),
        ("minio", 9000),
    ]:
        for variant, binding, expected in [
            ("all", f"{port}:{port}", ["NET001"]),
            ("loopback", f"127.0.0.1:{port}:{port}", []),
            ("ipv6", f"[::]:{port}:{port}", ["NET001"]),
            ("ipv6-loopback", f"[::1]:{port}:{port}", []),
            (
                "long",
                {"target": port, "published": port, "host_ip": "0.0.0.0"},
                ["NET001"],
            ),
        ]:
            save(
                f"{app}-{variant}.yaml",
                yaml.safe_dump({"services": {app: {"image": app, "ports": [binding]}}}),
                expected,
                f"{app}-binding",
            )
    for name, service, rules in [
        (
            "postgres-trust",
            {"environment": {"POSTGRES_HOST_AUTH_METHOD": "trust"}},
            ["AUTH001"],
        ),
        (
            "postgres-secret",
            {"environment": {"POSTGRES_PASSWORD": "fixture-only"}},
            ["SEC001"],
        ),
        (
            "postgres-reference",
            {"environment": {"POSTGRES_PASSWORD": "${PG_PASSWORD}"}},
            [],
        ),
        (
            "redis-unprotected",
            {"command": ["redis-server", "--protected-mode", "no"]},
            ["AUTH002"],
        ),
        (
            "redis-protected",
            {"command": ["redis-server", "--protected-mode", "yes"]},
            [],
        ),
        ("privileged", {"privileged": True}, ["PRIV001"]),
        ("unprivileged", {"privileged": False}, []),
        (
            "minio-secret",
            {"environment": ["MINIO_ROOT_PASSWORD=fixture-only"]},
            ["SEC001"],
        ),
    ]:
        save(
            name + ".yaml", yaml.safe_dump({"services": {"app": service}}), rules, name
        )
    for value, rules in [
        ("NodePort", ["NET002"]),
        ("LoadBalancer", ["NET002"]),
        ("ClusterIP", []),
    ]:
        save(
            f"k8s-{value}.yaml",
            yaml.safe_dump(
                {
                    "apiVersion": "v1",
                    "kind": "Service",
                    "metadata": {"name": "app"},
                    "spec": {"type": value},
                }
            ),
            rules,
            "k8s-service",
        )
    for wild in (True, False):
        save(
            f"k8s-role-{wild}.yaml",
            yaml.safe_dump(
                {
                    "apiVersion": "rbac.authorization.k8s.io/v1",
                    "kind": "Role",
                    "metadata": {"name": "app"},
                    "rules": [
                        {
                            "apiGroups": [""],
                            "resources": ["pods"],
                            "verbs": ["*" if wild else "get"],
                        }
                    ],
                }
            ),
            ["RBAC001"] if wild else [],
            "k8s-rbac",
        )
    for privileged in (True, False):
        save(
            f"k8s-pod-{privileged}.yaml",
            yaml.safe_dump(
                {
                    "apiVersion": "v1",
                    "kind": "Pod",
                    "metadata": {"name": "app"},
                    "spec": {
                        "containers": [
                            {
                                "name": "app",
                                "image": "nginx",
                                "securityContext": {"privileged": privileged},
                            }
                        ]
                    },
                }
            ),
            ["PRIV001"] if privileged else [],
            "k8s-privilege",
        )
    for cidr, name, rules in [
        ("0.0.0.0/0", "world", ["NET003"]),
        ("10.0.0.0/24", "private", []),
    ]:
        save(
            f"sg-{name}.tf",
            f'resource "aws_security_group" "db" {{\n ingress {{\n from_port = 5432\n to_port = 5432\n protocol = "tcp"\n cidr_blocks = ["{cidr}"]\n }}\n}}\n',
            rules,
            "terraform-sg",
        )
    save(
        "Dockerfile.secret",
        "FROM alpine:3.21\nENV API_TOKEN=fixture-only\n",
        ["SEC001"],
        "docker-credentials",
    )
    save(
        "Dockerfile.clean",
        "FROM alpine:3.21\nENV APP_MODE=development\n",
        [],
        "docker-credentials",
    )
    save(
        "nginx-on.conf",
        "events {}\nhttp { server { listen 80; autoindex on; } }\n",
        ["WEB001"],
        "nginx-listing",
    )
    save(
        "nginx-off.conf",
        "events {}\nhttp { server { listen 80; autoindex off; } }\n",
        [],
        "nginx-listing",
    )
    save("redis-off.conf", "protected-mode no\n", ["AUTH002"], "redis-directive")
    save("redis-on.conf", "protected-mode yes\n", [], "redis-directive")
    save("pg-trust.conf", "host all all 0.0.0.0/0 trust\n", ["AUTH001"], "postgres-hba")
    save(
        "pg-scram.conf", "host all all 10.0.0.0/24 scram-sha-256\n", [], "postgres-hba"
    )
    (ROOT / "data" / "labels.json").write_text(
        json.dumps(labels, indent=2), encoding="utf-8"
    )
    print(f"{len(labels)} development fixtures written; no independent test-set claim.")


if __name__ == "__main__":
    main()
