"""Trusted operator context, not model-generated probe authority or ground truth."""

import hashlib
import ipaddress
from pathlib import Path
from jsonschema import validate as schema_validate, ValidationError
from .cache import fingerprint
from .limits import read_bytes, json_value

HASH = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
TEXT = {"type": "string", "minLength": 1, "maxLength": 500}


def validate(value, schema):
    try:
        schema_validate(value, schema)
    except ValidationError as error:
        raise ValueError("invalid verification document schema") from error


def object_schema(properties):
    return dict(
        type="object",
        properties=properties,
        required=list(properties),
        additionalProperties=False,
    )


POLICY_SCHEMA = object_schema(
    dict(
        version={"const": "1.0"},
        configuration_sha256=HASH,
        inventory_sha256=HASH,
        reviewed_by=TEXT,
        rationale=TEXT,
        assets={
            "type": "array",
            "maxItems": 100,
            "items": object_schema(
                dict(
                    asset_id=TEXT,
                    expected_reachability={"enum": ["allowed", "forbidden"]},
                    relationship={
                        "enum": ["analogue", "operator_asserted_same_configuration"]
                    },
                )
            ),
        },
    )
)
REVIEW_SCHEMA = object_schema(
    dict(
        version={"const": "1.0"},
        configuration_sha256=HASH,
        inventory_sha256=HASH,
        audit_request_sha256=HASH,
        reviewed_by=TEXT,
        approvals={
            "type": "array",
            "maxItems": 50,
            "items": object_schema(
                dict(
                    candidate_sha256=HASH,
                    inventory_asset_id=TEXT,
                    verification_scope={"const": "tcp_reachability_only"},
                    rationale=TEXT,
                )
            ),
        },
    )
)


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path):
    raw = read_bytes(path)
    return json_value(raw), hashlib.sha256(raw).hexdigest()


def load_inventory(path):
    if path is None:
        return {}, None
    entries, digest = read_json(path)
    validate(
        entries,
        {
            "type": "array",
            "maxItems": 100,
            "items": object_schema(
                dict(
                    asset_id=TEXT,
                    host=TEXT,
                    port={"type": "integer", "minimum": 1, "maximum": 65535},
                )
            ),
        },
    )
    result = {}
    for entry in entries:
        if isinstance(entry["port"], bool) or not isinstance(entry["port"], int):
            raise ValueError("inventory port must be an integer")
        if entry["asset_id"] in result:
            raise ValueError("duplicate inventory asset")
        if not ipaddress.ip_address(entry["host"]).is_loopback:
            raise ValueError("inventory must contain only literal loopback endpoints")
        result[entry["asset_id"]] = entry
    return result, digest


def load_context(path, schema, configuration_hash, inventory_hash):
    if path is None:
        return None
    document, digest = read_json(path)
    validate(document, schema)
    if (
        document["configuration_sha256"] != configuration_hash
        or document["inventory_sha256"] != inventory_hash
    ):
        raise ValueError("stale configuration/inventory binding")
    return dict(document=document, sha256=digest)


def policy_assets(context, inventory):
    result = {}
    for asset in context["document"]["assets"] if context else []:
        identity = asset["asset_id"]
        if identity not in inventory or identity in result:
            raise ValueError("unknown or duplicate policy asset")
        result[identity] = asset
    return result


def approved_candidates(context, rag, inventory, policies):
    if context is None:
        return []
    if rag is None or context["document"]["audit_request_sha256"] != rag.get(
        "request_sha256"
    ):
        raise ValueError("review does not match the current audit request")
    if not rag.get("model_digest"):
        raise ValueError("review requires digest-bound audit; enable --cache-dir")
    candidates = {}
    for candidate in rag["output"]["findings"]:
        key = fingerprint(candidate)
        if key in candidates:
            raise ValueError("ambiguous duplicate model candidate")
        candidates[key] = candidate
    result, seen = [], set()
    for approval in context["document"]["approvals"]:
        key, asset = approval["candidate_sha256"], approval["inventory_asset_id"]
        if key not in candidates or key in seen:
            raise ValueError(
                "unknown, changed, rejected or duplicate candidate approval"
            )
        if asset not in inventory or asset not in policies:
            raise ValueError("approval needs an explicit inventory endpoint and policy")
        seen.add(key)
        result.append((approval, candidates[key]))
    return result


def assess(policy, evidence, applicable=True):
    status = "not_applicable" if not applicable else "policy_missing"
    if applicable and policy:
        outcome = evidence.get("outcome") if evidence else None
        status = {
            "reachable": "expected_reachability"
            if policy["expected_reachability"] == "allowed"
            else "unexpected_reachability",
            "unreachable": "not_observed_from_this_vantage",
            "inconclusive": "inconclusive",
        }.get(outcome, "not_tested")
    return dict(
        status=status,
        policy=policy,
        deployment_equivalence_verified=False,
        vulnerability_confirmed=False,
        finding_suppressed=False,
        scope="TCP only; operator-declared mapping is not deployment attestation",
    )
