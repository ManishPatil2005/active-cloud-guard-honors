"""Pinned collector metadata/source review; never load a sensor or correct clocks."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.deployment import local_daemon
from scripts.sensor_trial import IMAGE

LIBS_COMMIT = "8fc2f1fbfc90f8ce7f68e00cdfa692cc7a9983a3"
SOURCES = {
    "userspace/libscap/engine/modern_bpf/scap_modern_bpf.c": [
        "scap_get_precise_boot_time",
        "pman_set_boot_time",
    ],
    "userspace/libscap/scap_engine_util.c": [
        "scap_get_precise_boot_time",
        "CLOCK_BOOTTIME",
        "CLOCK_REALTIME",
    ],
    "userspace/libpman/src/maps.c": [
        "pman_set_boot_time",
        "settings.boot_time = boot_time",
    ],
    "driver/modern_bpf/helpers/base/maps_getters.h": [
        "maps__get_boot_time",
        "settings->boot_time",
    ],
    "driver/modern_bpf/helpers/store/ringbuf_store_params.h": [
        "maps__get_boot_time() + bpf_ktime_get_boot_ns()",
    ],
    "driver/modern_bpf/helpers/store/auxmap_store_params.h": [
        "maps__get_boot_time() + bpf_ktime_get_boot_ns()",
    ],
}


def version_fields(stdout):
    result = {}
    for label, key in (
        ("Falco version", "falco"),
        ("Libs version", "libs"),
        ("Engine", "engine"),
    ):
        matches = re.findall(rf"^{label}:\s+([0-9]+\.[0-9]+\.[0-9]+)\s*$", stdout, re.M)
        if len(matches) != 1:
            raise ValueError("unexpected collector version metadata")
        result[key] = matches[0]
    if result["falco"] != "0.45.0" or result["libs"] != "0.26.0":
        raise ValueError("collector release does not match reviewed source")
    return result


def source_record(path, payload):
    if path not in SOURCES or len(payload) > 256_000:
        raise ValueError("source outside bounded review")
    lines = payload.decode("utf-8").splitlines()
    locations = {
        marker: [i + 1 for i, line in enumerate(lines) if marker in line]
        for marker in SOURCES[path]
    }
    if any(not locations[m] for m in SOURCES[path]):
        raise ValueError("expected source marker missing")
    return dict(
        path=path,
        url=f"https://raw.githubusercontent.com/falcosecurity/libs/{LIBS_COMMIT}/{path}",
        sha256=hashlib.sha256(payload).hexdigest(),
        bytes=len(payload),
        marker_lines=locations,
    )


def docker(*args):
    return subprocess.run(
        ["docker", *args], capture_output=True, text=True, check=True, timeout=20
    ).stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    with Path(args.output).open("x", encoding="utf-8") as stream:
        report = dict(
            executed_at=datetime.now(timezone.utc).isoformat(),
            status="started",
            image=IMAGE,
            libs_release="0.26.0",
            libs_source_commit=LIBS_COMMIT,
            sources=[],
            sensor_started=False,
            clock_settings_modified=False,
            correction_applied=False,
            binary_source_attested=False,
            independent_evaluation=False,
        )
        try:
            report["phase"] = "local_metadata"
            local_daemon()
            identity = json.loads(
                docker(
                    "image",
                    "inspect",
                    IMAGE,
                    "--format",
                    '{"id":{{json .Id}},"digests":{{json .RepoDigests}}}',
                )
            )
            if IMAGE not in identity.get("digests", []):
                raise ValueError("expected image digest missing")
            report["image_identity"] = identity
            # Version mode only, no mounts, capabilities, network or persistent container.
            stdout = docker(
                "run",
                "--rm",
                "--pull",
                "never",
                "--network",
                "none",
                "--cap-drop",
                "ALL",
                "--read-only",
                "--memory",
                "128m",
                "--cpus",
                "1",
                "--pids-limit",
                "32",
                "--entrypoint",
                "/usr/bin/falco",
                IMAGE,
                "--version",
            )
            report["versions"] = version_fields(stdout)
            report["phase"] = "official_source_review"
            for path in SOURCES:
                url = f"https://raw.githubusercontent.com/falcosecurity/libs/{LIBS_COMMIT}/{path}"
                with urlopen(url, timeout=15) as response:
                    payload = response.read(256_001)
                report["sources"].append(source_record(path, payload))
            report["status"] = "reviewed"
        except Exception as error:
            report.update(status="failed", error_type=type(error).__name__)
            raise
        finally:
            json.dump(report, stream, indent=2)
            stream.write("\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
