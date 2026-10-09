"""Capture reproducibility metadata without inspecting credential contents."""

import importlib.metadata
import json
import platform
import re
import sys
from pathlib import Path
from urllib.request import build_opener, ProxyHandler
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.evidence import evidence_main
from cloudguard.llm import LocalOnlyRedirect
from cloudguard.limits import json_response
from cloudguard.limits import json_value
from cloudguard.legacy_io import InputBudget
from cloudguard.process_runner import run_bounded, BoundedProcessError


def collect(args):
    budget = InputBudget(total=32_000_000, files=2048, seconds=180)
    images = [
        "redis:7.4.2-alpine",
        "postgres:17.4-alpine",
        "nginx:1.28.0-alpine",
        "quay.io/minio/minio:RELEASE.2025-04-22T22-12-26Z",
        "ollama/ollama:0.6.5",
        "aquasec/trivy:0.60.0",
    ]
    report = dict(
        status="collecting",
        observed_at=datetime.now(timezone.utc).isoformat(),
        platform=platform.platform(),
        python=platform.python_version(),
        docker_version=None,
        image_digests={},
        models=None,
        packages={},
        file_hashes={},
        source_pdf_sha256=None,
    )
    try:
        for image in images:
            result = run_bounded(
                [
                    "docker",
                    "image",
                    "inspect",
                    image,
                    "--format",
                    "{{json .RepoDigests}}",
                ],
                timeout=budget.timeout(30),
                output_limit=128_000,
            )
            if result.returncode:
                raise ValueError("metadata command failed")
            report["image_digests"][image] = json_value(result.stdout)
        with build_opener(ProxyHandler({}), LocalOnlyRedirect()).open(
            "http://127.0.0.1:11434/api/tags", timeout=min(5, budget.timeout())
        ) as response:
            report["models"] = json_response(response)
        for index, distribution in enumerate(importlib.metadata.distributions()):
            budget.check()
            if index >= 2048:
                raise ValueError("package count budget exceeded")
            name, version = distribution.metadata["Name"], distribution.version
            if (
                not isinstance(name, str)
                or not 1 <= len(name) <= 256
                or not isinstance(version, str)
                or not 1 <= len(version) <= 256
                or any(c in name + version for c in "\r\n\0")
            ):
                raise ValueError("invalid package metadata")
            if not re.fullmatch(
                r"[A-Za-z0-9][A-Za-z0-9_.-]*", name
            ) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.+!-]*", version):
                raise ValueError("invalid package lock token")
            if name in report["packages"]:
                raise ValueError("duplicate package metadata")
            report["packages"][name] = version
        entries = 0
        for folder in ["cloudguard", "tests", "knowledge", "data", "docs"]:
            for path in (ROOT / folder).rglob("*"):
                budget.check()
                entries += 1
                if entries > 10000 or path.is_symlink():
                    raise ValueError("metadata traversal refused")
                if path.is_file() and "__pycache__" not in path.parts:
                    report["file_hashes"][str(path.relative_to(ROOT))] = budget.digest(
                        path
                    )
        source = ROOT / "docs/source/Honors_Research_1st_Monitoring_Deck.pdf"
        if source.exists():
            report["source_pdf_sha256"] = budget.digest(source)
        result = run_bounded(
            ["docker", "version", "--format", "{{.Server.Version}}"],
            timeout=budget.timeout(30),
            output_limit=128_000,
        )
        if result.returncode:
            raise ValueError("metadata command failed")
        report["docker_version"] = result.stdout.strip()
        report["status"] = "completed"
        lock = (
            "\n".join(
                f"{name}=={version}"
                for name, version in sorted(
                    report["packages"].items(), key=lambda pair: pair[0].lower()
                )
            )
            + "\n"
        )
        return {"output": report, "lock-output": lock}, 0
    except (Exception, KeyboardInterrupt) as error:
        report.update(status="rejected", error_type=type(error).__name__)
        if isinstance(error, BoundedProcessError):
            report["process_diagnostic"] = error.diagnostic
        # Preserve partial observations, never publish a plausible successful lock.
        rejected = (
            json.dumps(dict(status="rejected", error_type=type(error).__name__)) + "\n"
        )
        return {"output": report, "lock-output": rejected}, 1


def main():
    return evidence_main(
        collect, outputs=("output", "lock-output"), text_outputs=("lock-output",)
    )


if __name__ == "__main__":
    raise SystemExit(main())
