"""Opt-in actual wheel checks; missing artifact/target explicitly skips qualification."""

import configparser
from email.parser import BytesParser
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tomllib
import zipfile

import pytest

from cloudguard.process_runner import run_bounded

ROOT = Path(__file__).resolve().parents[1]
DIST = "active_cloud_guard-0.5.0.dist-info/"
CHILD = """
import contextlib, importlib.metadata, io, json, os, pathlib, sys
target = pathlib.Path(sys.argv[1]).resolve()
os.chdir(sys.argv[2])
sys.path.insert(0, str(target))
import cloudguard
assert pathlib.Path(cloudguard.__file__).resolve().is_relative_to(target)
distribution = importlib.metadata.distribution('active-cloud-guard')
assert pathlib.Path(distribution.locate_file('')).resolve() == target
assert distribution.version == cloudguard.__version__ == '0.5.0'
entries = [e for e in distribution.entry_points
           if e.group == 'console_scripts' and e.name == 'cloudguard']
assert len(entries) == 1 and entries[0].value == 'cloudguard.cli:main'
main = entries[0].load()
sys.argv = ['cloudguard'] + sys.argv[3:]
stream = io.StringIO()
with contextlib.redirect_stdout(stream):
    main()
print(json.dumps({'installed_package_used': True,
                  'result': json.loads(stream.getvalue())}))
"""


def test_build_backend_is_exactly_qualified():
    manifest = tomllib.loads((ROOT / "pyproject.toml").read_text())
    assert manifest["build-system"] == {
        "requires": ["setuptools==83.0.0"],
        "build-backend": "setuptools.build_meta",
    }


def test_build_tool_wheel_hash_is_pinned():
    profile = (ROOT / "requirements-build-qualification-20261010.txt").read_text()
    assert "-r requirements-remediation-bootstrap-20261009.txt" in profile
    assert (
        "setuptools==83.0.0 --hash=sha256:"
        "29b23c360f22f414dc7336bb39178cc7bcbf6021ed2733cde173f09dba19abb3"
    ) in profile


@pytest.fixture
def artifact(record_testsuite_property):
    wheel, target = os.getenv("ACG_PACKAGE_WHEEL"), os.getenv("ACG_PACKAGE_TARGET")
    if wheel is None and target is None:
        pytest.skip(
            "Installed-wheel qualification requires explicit artifact and target"
        )
    assert wheel and target, "Both package qualification paths are required"
    wheel, target = Path(wheel).resolve(), Path(target).resolve()
    assert wheel.is_file() and wheel.stat().st_size <= 2_000_000
    assert target.is_dir() and target != ROOT and not ROOT.is_relative_to(target)
    record_testsuite_property(
        "wheel_sha256", hashlib.sha256(wheel.read_bytes()).hexdigest()
    )
    return wheel, target


def test_wheel_has_only_exact_package_sources_and_expected_metadata(artifact):
    wheel, target = artifact
    sources = {
        "cloudguard/" + path.name: path.read_bytes()
        for path in (ROOT / "cloudguard").glob("*.py")
    }
    metadata_files = {
        DIST + name
        for name in ("METADATA", "WHEEL", "entry_points.txt", "top_level.txt", "RECORD")
    }
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        assert len(names) == len(set(names)) <= 256
        assert set(names) == sources.keys() | metadata_files
        assert sum(row.file_size for row in archive.infolist()) <= 4_000_000
        for name, raw in sources.items():
            assert archive.read(name) == raw
            assert (target / name).read_bytes() == raw
        metadata = BytesParser().parsebytes(archive.read(DIST + "METADATA"))
        assert (
            metadata["Name"] == "active-cloud-guard" and metadata["Version"] == "0.5.0"
        )
        assert metadata["Requires-Python"] == ">=3.11"
        requirements = set(metadata.get_all("Requires-Dist"))
        assert requirements == {
            "PyYAML==6.0.3",
            "jsonschema==4.23.0",
            "python-hcl2==7.3.1",
            'chromadb==1.0.20; extra == "vector"',
            'pytest==9.0.3; extra == "test"',
            'scikit-learn==1.9.1; extra == "runtime-ml"',
        }
        entries = configparser.ConfigParser()
        entries.read_string(archive.read(DIST + "entry_points.txt").decode())
        assert entries.sections() == ["console_scripts"]
        assert dict(entries["console_scripts"]) == {"cloudguard": "cloudguard.cli:main"}


@pytest.mark.parametrize(
    "command",
    ["scan", "retrieve", "runtime-replay", "integrated-replay", "invalid-input"],
)
def test_installed_console_entry_point_without_source_imports(
    artifact, tmp_path, command
):
    _, target = artifact
    inputs = {
        "postgres": "data/development/postgres-trust.yaml",
        "redis": "data/development/redis-all.yaml",
        "knowledge": "knowledge/sources.json",
        "baseline": "data/runtime/baseline-synthetic.json",
        "observation": "data/runtime/observation-synthetic.json",
        "inventory": "testbed/inventory.json",
    }
    paths = {}
    for key, relative in inputs.items():
        destination = tmp_path / Path(relative).name
        shutil.copyfile(ROOT / relative, destination)
        paths[key] = str(destination)
    runtime = [
        paths["observation"],
        "--baseline",
        paths["baseline"],
        "--inventory",
        paths["inventory"],
    ]
    args = {
        "scan": ["scan", paths["postgres"]],
        "retrieve": [
            "retrieve",
            "PostgreSQL trust authentication",
            "--kb",
            paths["knowledge"],
        ],
        "runtime-replay": ["runtime-replay"] + runtime,
        "integrated-replay": ["integrated-replay", paths["redis"]] + runtime,
        "invalid-input": ["scan", str(tmp_path / "missing.yaml")],
    }[command]
    result = run_bounded(
        [sys.executable, "-I", "-c", CHILD, str(target), str(tmp_path)] + args,
        timeout=30,
        output_limit=1_000_000,
    )
    if command == "invalid-input":
        assert result.returncode == 2 and "no clean verdict" in result.stderr
        assert result.stdout == ""
        return
    assert result.returncode == 0, result.stderr
    envelope = json.loads(result.stdout)
    assert envelope["installed_package_used"] is True
    report = envelope["result"]
    if command == "scan":
        assert [finding["rule_id"] for finding in report["findings"]] == ["AUTH001"]
    elif command == "retrieve":
        assert report[0]["id"] == "postgres-trust"
    else:
        runtime_report = report if command == "runtime-replay" else report["engine2"]
        assert runtime_report["mode"] == "observation_only_replay"
        assert [window["status"] for window in runtime_report["windows"]] == [
            "no_threshold_exceedance",
            "deviation_for_review",
        ]
        assert runtime_report["actions_executed"] == []
        assert (
            not runtime_report["threat_confirmed"]
            and not runtime_report["runtime_sensor_connected"]
        )
