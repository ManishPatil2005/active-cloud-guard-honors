"""Query installed public package names/versions; no source or paths uploaded."""

import importlib.metadata
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
from urllib.request import Request, build_opener, ProxyHandler, HTTPRedirectHandler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cloudguard.evidence import evidence_main
from cloudguard.limits import json_response

URL = "https://api.osv.dev/v1/querybatch"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("advisory redirects refused")


def inventory():
    packages = {}
    for distribution in importlib.metadata.distributions():
        name, version = distribution.metadata.get("Name"), distribution.version
        if not isinstance(name, str) or not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", name
        ):
            raise ValueError("invalid package name")
        if not isinstance(version, str) or not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9_.+!-]{0,127}", version
        ):
            raise ValueError("invalid package version")
        name = re.sub(r"[-_.]+", "-", name).lower()
        if name in packages:
            raise ValueError("duplicate installed package")
        packages[name] = version
        if len(packages) > 256:
            raise ValueError("package count exceeded")
    if not packages:
        raise ValueError("empty package inventory")
    return [
        {"name": name, "version": version} for name, version in sorted(packages.items())
    ]


def lookup(batch):
    payload = {
        "queries": [
            {
                "package": {"name": p["name"], "ecosystem": "PyPI"},
                "version": p["version"],
            }
            for p in batch
        ]
    }
    request = Request(
        URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with build_opener(ProxyHandler({}), NoRedirect()).open(
        request, timeout=30
    ) as stream:
        result = json_response(stream)
    if (
        not isinstance(result, dict)
        or set(result) != {"results"}
        or not isinstance(result["results"], list)
        or len(result["results"]) != len(batch)
    ):
        raise ValueError("advisory batch count/envelope mismatch")
    rows = []
    for package, record in zip(batch, result["results"], strict=True):
        if not isinstance(record, dict) or set(record) - {"vulns"}:
            raise ValueError("invalid advisory result")
        vulnerabilities = record.get("vulns", [])
        if not isinstance(vulnerabilities, list) or len(vulnerabilities) > 256:
            raise ValueError("advisory count exceeded")
        ids = []
        for vulnerability in vulnerabilities:
            if (
                not isinstance(vulnerability, dict)
                or not isinstance(vulnerability.get("id"), str)
                or not re.fullmatch(
                    r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", vulnerability["id"]
                )
            ):
                raise ValueError("invalid advisory ID")
            ids.append(vulnerability["id"])
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate advisory ID")
        rows.append(dict(package, status="queried", advisory_ids=sorted(ids)))
    return rows


def collect(args):
    packages = inventory()
    rows, failure = [], None
    for start in range(0, len(packages), 32):
        try:
            rows.extend(lookup(packages[start : start + 32]))
        except Exception as error:
            failure = type(error).__name__
            break
    queried = len(rows)
    rows.extend(
        dict(p, status="not_queried", advisory_ids=None) for p in packages[queried:]
    )
    report = dict(
        checked_at_utc=datetime.now(timezone.utc).isoformat(),
        status="complete_database_query"
        if failure is None
        else "partial_database_query",
        database=URL,
        packages=rows,
        queried_count=queried,
        installed_count=len(packages),
        error_type=failure,
        exploitability_verified=False,
        vulnerability_free=False,
        limits=[
            "Database coverage is not exhaustive; absence of IDs is not security clearance.",
            "Package metadata is not authenticated provenance; IDs require condition/remediation triage.",
            "Only installed Python distributions queried; OS, images, Ollama/model/native binaries excluded.",
            "No source upload, upgrade, exploit or automatic retry; per-request socket timeout not whole-run deadline.",
        ],
    )
    return {"output": report}, 0 if failure is None else 1


if __name__ == "__main__":
    raise SystemExit(evidence_main(collect))
