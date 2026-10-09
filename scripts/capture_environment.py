"""Capture reproducibility metadata without inspecting credential contents."""

import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
from pathlib import Path
from urllib.request import build_opener, ProxyHandler
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.evidence import evidence_main
from cloudguard.llm import LocalOnlyRedirect
from cloudguard.limits import json_response


def collect(args):
    images = [
        "redis:7.4.2-alpine",
        "postgres:17.4-alpine",
        "nginx:1.28.0-alpine",
        "quay.io/minio/minio:RELEASE.2025-04-22T22-12-26Z",
        "ollama/ollama:0.6.5",
        "aquasec/trivy:0.60.0",
    ]
    digests = {
        image: json.loads(
            subprocess.check_output(
                [
                    "docker",
                    "image",
                    "inspect",
                    image,
                    "--format",
                    "{{json .RepoDigests}}",
                ],
                text=True,
            )
        )
        for image in images
    }
    with build_opener(ProxyHandler({}), LocalOnlyRedirect()).open(
        "http://127.0.0.1:11434/api/tags", timeout=5
    ) as response:
        models = json_response(response)
    versions = {
        d.metadata["Name"]: d.version for d in importlib.metadata.distributions()
    }
    lock = (
        "\n".join(
            f"{name}=={v}"
            for name, v in sorted(versions.items(), key=lambda item: item[0].lower())
        )
        + "\n"
    )
    files = {}
    for folder in ["cloudguard", "tests", "knowledge", "data", "docs"]:
        for p in (ROOT / folder).rglob("*"):
            if p.is_file() and "__pycache__" not in p.parts:
                files[str(p.relative_to(ROOT))] = hashlib.sha256(
                    p.read_bytes()
                ).hexdigest()
    source = Path(r"C:\Users\manis\Downloads\Honors_Research_1st_Monitoring_Deck.pdf")
    report = dict(
        observed_at=datetime.now(timezone.utc).isoformat(),
        platform=platform.platform(),
        python=platform.python_version(),
        docker_version=subprocess.check_output(
            ["docker", "version", "--format", "{{.Server.Version}}"], text=True
        ).strip(),
        image_digests=digests,
        models=models,
        packages=versions,
        file_hashes=files,
        source_pdf_sha256=hashlib.sha256(source.read_bytes()).hexdigest()
        if source.exists()
        else None,
    )
    return {"output": report, "lock-output": lock}, 0


def main():
    return evidence_main(
        collect, outputs=("output", "lock-output"), text_outputs=("lock-output",)
    )


if __name__ == "__main__":
    raise SystemExit(main())
