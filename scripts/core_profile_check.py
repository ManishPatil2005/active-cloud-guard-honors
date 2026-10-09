"""Offline installed-pin verification of the fixed recommended source-tree profile."""

import hashlib
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cloudguard.evidence import evidence_main
from cloudguard.limits import read_bytes
from scripts.dependency_advisory_check import inventory

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    "requirements-core-current.txt",
    "requirements-remediation-linux-candidate-20261009.txt",
    "requirements-runtime-ml-20261006.txt",
)
PIN = re.compile(
    r"([A-Za-z0-9][A-Za-z0-9_.-]{0,127})==([A-Za-z0-9][A-Za-z0-9_.+!-]{0,127})"
)


def profile(root=ROOT):
    """Read only the three fixed bounded files; no arbitrary include expansion."""
    pins, sources = {}, []
    for index, name in enumerate(FILES):
        raw = read_bytes(root / name, limit=16_384)
        lines = raw.decode("utf-8").splitlines()
        includes = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("-r "):
                includes.append(line[3:])
                continue
            match = PIN.fullmatch(line)
            if match is None:
                raise ValueError("unsupported profile requirement")
            package, version = match.groups()
            package = re.sub(r"[-_.]+", "-", package).lower()
            if package in pins:
                raise ValueError("duplicate profile pin")
            pins[package] = version
            if len(pins) > 128:
                raise ValueError("profile pin count exceeded")
        expected = [FILES[index + 1]] if index < len(FILES) - 1 else []
        if includes != expected:
            raise ValueError("profile include contract mismatch")
        sources.append({"file": name, "sha256": hashlib.sha256(raw).hexdigest()})
    if not pins:
        raise ValueError("empty profile")
    return pins, sources


def collect(args):
    expected, sources = profile()
    installed = {row["name"]: row["version"] for row in inventory()}
    rows = []
    for name, version in sorted(expected.items()):
        actual = installed.get(name)
        rows.append(
            {
                "name": name,
                "expected_version": version,
                "installed_version": actual,
                "status": "missing"
                if actual is None
                else "match"
                if actual == version
                else "mismatch",
            }
        )
    counts = {
        status: sum(r["status"] == status for r in rows)
        for status in ("match", "missing", "mismatch")
    }
    accepted = counts["missing"] == counts["mismatch"] == 0
    return {
        "output": {
            "status": "profile_pins_match" if accepted else "profile_pins_mismatch",
            "profile_sources": sources,
            "required_count": len(rows),
            "installed_count": len(installed),
            "counts": counts,
            "packages": rows,
            "extra_packages": [
                {"name": name, "version": installed[name]}
                for name in sorted(installed.keys() - expected.keys())
            ],
            "extra_packages_qualified": False,
            "vector_qualified": False,
            "production_ready": False,
            "independent_evaluation": False,
            "limits": [
                "Exact installed metadata matching only; not wheel-byte or runtime integrity attestation.",
                "Additional distributions are reported, not silently certified or prohibited.",
                "No installation, package imports, network, service, sensor or model actions.",
                "Profile files and their parent directory must be trusted; hashes are not signatures.",
            ],
        }
    }, 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(evidence_main(collect))
