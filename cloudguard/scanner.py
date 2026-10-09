"""Small, explicit baseline. Unsupported constructs are reported, never 'safe'."""

from __future__ import annotations
import hashlib
import ipaddress
import re
from pathlib import Path
import hcl2
import yaml
from .limits import read_text, MAX_DEPTH, MAX_NODES

RULES = {
    "NET001": (0.65, "Service published beyond loopback", "docker-ports"),
    "AUTH001": (0.9, "PostgreSQL trust authentication enabled", "postgres-trust"),
    "AUTH002": (0.8, "Redis protected mode disabled", "redis-security"),
    "SEC001": (0.85, "Literal credential in configuration", "k8s-secrets"),
    "PRIV001": (0.9, "Privileged container", "k8s-security"),
    "RBAC001": (0.85, "Wildcard Kubernetes RBAC permission", "k8s-rbac"),
    "NET002": (0.65, "Externally exposed Kubernetes service type", "k8s-service"),
    "NET003": (0.75, "World-open security group ingress", "aws-sg"),
    "WEB001": (0.5, "Nginx directory listing enabled", "nginx-autoindex"),
}


class UniqueLoader(yaml.SafeLoader):
    def __init__(self, stream):
        super().__init__(stream)
        self._budget_depth = 0
        self._budget_nodes = 0

    def compose_node(self, parent, index):
        # Aliases/merges can amplify traversal or make cyclic location paths.
        if self.check_event(yaml.events.AliasEvent):
            raise ValueError("YAML aliases are unsupported")
        self._budget_nodes += 1
        self._budget_depth += 1
        try:
            if self._budget_nodes > MAX_NODES or self._budget_depth > MAX_DEPTH:
                raise ValueError("YAML structure budget exceeded")
            return super().compose_node(parent, index)
        finally:
            self._budget_depth -= 1


def _mapping(loader, node, deep=False):
    # Reject ambiguous duplicate keys, including overrides introduced through merges.
    loader.flatten_mapping(node)
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f"duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


def literal_secret(key, value):
    if (
        str(key).upper().endswith("_FILE")
        and isinstance(value, str)
        and value.startswith("/run/secrets/")
    ):
        return False
    if not re.search(r"password|passwd|secret|token|access_key", str(key), re.I):
        return False
    return isinstance(value, str) and bool(value) and not value.startswith(("${", "{{"))


def _public_binding(binding):
    if isinstance(binding, dict):
        host = str(binding.get("host_ip", "0.0.0.0"))
    else:
        value = str(binding).split("/")[0]
        if value.startswith("["):
            host = value.split("]", 1)[0][1:]
        else:
            parts = value.split(":")
            host = parts[0] if len(parts) >= 3 else "0.0.0.0"
    if "${" in host:
        raise ValueError("unresolved host binding; render Compose configuration first")
    try:
        return not ipaddress.ip_address(host).is_loopback
    except ValueError:
        raise ValueError("host binding must be a resolved IP address") from None


def scan(path):
    path = Path(path)
    text = read_text(path)
    findings, warnings = [], []
    digest = hashlib.sha256(text.encode()).hexdigest()

    def add(rule, asset, location):
        score, title, source = RULES[rule]
        identity = f"{digest}:{asset}:{rule}:{location}"
        findings.append(
            dict(
                id=hashlib.sha256(identity.encode()).hexdigest()[:20],
                asset_id=asset,
                rule_id=rule,
                title=title,
                static_score=score,
                location=location,
                source_ids=[source],
                origin="rule_baseline",
                evidence="Configuration predicate matched; no exploitation claim.",
            )
        )

    suffix = path.suffix.lower()
    if suffix in (".yaml", ".yml", ".json"):
        docs = list(yaml.load_all(text, Loader=UniqueLoader))
        for index, doc in enumerate(docs):
            if not isinstance(doc, dict):
                raise ValueError("each YAML document must be a mapping")
            if "services" in doc:
                if not isinstance(doc["services"], dict):
                    raise ValueError("services must be a mapping")
                for name, service in doc["services"].items():
                    if not isinstance(service, dict):
                        raise ValueError("service must be a mapping")
                    asset = f"compose/{name}"
                    for i, port in enumerate(service.get("ports", []) or []):
                        if _public_binding(port):
                            add("NET001", asset, f"services.{name}.ports[{i}]")
                    if service.get("network_mode") == "host":
                        warnings.append(
                            f"{asset}: host networking requires manual exposure review"
                        )
                    if service.get("privileged") is True:
                        add("PRIV001", asset, f"services.{name}.privileged")
                    env = service.get("environment", {}) or {}
                    if isinstance(env, list):
                        normalized = {}
                        for entry in env:
                            if not isinstance(entry, str):
                                raise ValueError("invalid environment list entry")
                            environment_name, separator, value = entry.partition("=")
                            if not environment_name:
                                raise ValueError("invalid environment list entry")
                            if environment_name in normalized:
                                raise ValueError("duplicate environment name")
                            normalized[environment_name] = value if separator else None
                        env = normalized
                    if not isinstance(env, dict):
                        raise ValueError("environment must be list or mapping")
                    for key, value in env.items():
                        loc = f"services.{name}.environment.{key}"
                        if literal_secret(key, value):
                            add("SEC001", asset, loc)
                        if (
                            key == "POSTGRES_HOST_AUTH_METHOD"
                            and str(value).lower() == "trust"
                        ):
                            add("AUTH001", asset, loc)
                    command = service.get("command", "")
                    command = (
                        " ".join(map(str, command))
                        if isinstance(command, list)
                        else str(command)
                    )
                    if re.search(r"--protected-mode(?:\s+|=)no\b", command):
                        add("AUTH002", asset, f"services.{name}.command")
                    if service.get("env_file"):
                        warnings.append(f"{asset}: env_file contents not evaluated")
            elif "kind" in doc:
                kind = doc["kind"]
                meta = doc.get("metadata", {})
                asset = f"k8s/{meta.get('namespace', 'default')}/{kind}/{meta.get('name', index)}"
                if kind in ("Role", "ClusterRole"):
                    for i, rule in enumerate(doc.get("rules", [])):
                        if any(
                            "*" in rule.get(k, [])
                            for k in ("verbs", "resources", "apiGroups")
                        ):
                            add("RBAC001", asset, f"rules[{i}]")
                elif kind == "Service":
                    if doc.get("spec", {}).get("type") in ("NodePort", "LoadBalancer"):
                        add("NET002", asset, "spec.type")
                elif kind == "Secret":
                    if doc.get("data") or doc.get("stringData"):
                        add("SEC001", asset, "data/stringData")
                elif kind in ("Pod", "Deployment", "StatefulSet", "DaemonSet", "Job"):
                    spec = doc.get("spec", {})
                    if kind != "Pod":
                        spec = spec.get("template", {}).get("spec", {})
                    for group in (
                        "containers",
                        "initContainers",
                        "ephemeralContainers",
                    ):
                        for i, container in enumerate(spec.get(group, [])):
                            loc = f"{group}[{i}]"
                            if (
                                container.get("securityContext", {}).get("privileged")
                                is True
                            ):
                                add("PRIV001", asset, loc + ".securityContext")
                            for env in container.get("env", []):
                                if literal_secret(env.get("name"), env.get("value")):
                                    add("SEC001", asset, loc + ".env." + env["name"])
                    if spec.get("hostNetwork"):
                        warnings.append(f"{asset}: hostNetwork requires manual review")
                else:
                    warnings.append(f"unsupported Kubernetes kind: {kind}")
            else:
                warnings.append("unsupported YAML schema")
    elif suffix == ".tf":
        doc = hcl2.loads(text)
        for resource in doc.get("resource", []):
            for kind, instances in resource.items():
                for name, value in instances.items():
                    asset = f"terraform/{kind}/{name}"
                    if kind == "aws_security_group":
                        for i, ingress in enumerate(value.get("ingress", [])):
                            if any(
                                cidr in ("0.0.0.0/0", "::/0")
                                for cidr in ingress.get("cidr_blocks", [])
                                + ingress.get("ipv6_cidr_blocks", [])
                            ):
                                add("NET003", asset, f"ingress[{i}]")
                        if value.get("dynamic"):
                            warnings.append(f"{asset}: dynamic blocks unresolved")
                    else:
                        warnings.append(f"unsupported Terraform resource: {kind}")
        if doc.get("module") or doc.get("variable"):
            warnings.append("Terraform modules/variables require plan-based review")
    elif path.name.lower().startswith("dockerfile"):
        for i, line in enumerate(text.splitlines(), 1):
            if re.match(r"\s*(ENV|ARG)\s", line, re.I):
                for match in re.finditer(
                    r"([A-Za-z_][A-Za-z_0-9]*)[=\s]+([^\s]+)", line.split(None, 1)[1]
                ):
                    if literal_secret(*match.groups()):
                        add("SEC001", "dockerfile/image", f"line:{i}")
        warnings.append("Dockerfile support limited to literal ENV/ARG credentials")
    elif suffix == ".conf":
        for i, raw in enumerate(text.splitlines(), 1):
            line = raw.split("#", 1)[0].strip()
            if re.search(r"\bautoindex\s+on\s*;", line):
                add("WEB001", "config/nginx", f"line:{i}")
            if re.match(r"protected-mode\s+no\s*$", line):
                add("AUTH002", "config/redis", f"line:{i}")
            if re.match(r"host\S*\s+.*\s+trust\s*$", line):
                add("AUTH001", "config/postgresql", f"line:{i}")
        warnings.append(
            "conf support limited to explicit autoindex/protected-mode/host trust directives"
        )
    else:
        raise ValueError(f"unsupported input format: {path.name}")
    return dict(
        schema_version="1.0",
        file=str(path),
        sha256=digest,
        findings=findings,
        warnings=warnings,
        coverage="selected predicates only; absence of findings is not proof of safety",
    )
