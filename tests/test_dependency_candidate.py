from pathlib import Path
import importlib.util
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "candidate_check", ROOT / "scripts/dependency_candidate_check.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def pins(name):
    return dict(
        line.split("==", 1)
        for line in (ROOT / name).read_text().splitlines()
        if line and not line.startswith(("#", "-"))
    )


def test_windows_candidate_changes_only_three_root_versions():
    original = pins("requirements-lock.txt")
    candidate = pins("requirements-remediation-windows-candidate-20261009.txt")
    assert original.keys() == candidate.keys()
    assert {
        key: candidate[key] for key in original if original[key] != candidate[key]
    } == {"pip": "26.2", "pytest": "9.0.3", "oauthlib": "4.0.0"}


def test_linux_candidate_preserves_core_except_pytest():
    original = pins("requirements-linux-core-20260928.txt")
    candidate = pins("requirements-remediation-linux-candidate-20261009.txt")
    assert {
        key: candidate[key] for key in original if original[key] != candidate[key]
    } == {"pytest": "9.0.3"}
    assert candidate["pip"] == "26.2" and candidate["oauthlib"] == "4.0.0"


def test_bootstrap_requires_pypi_wheel_hash():
    text = (ROOT / "requirements-remediation-bootstrap-20261009.txt").read_text()
    assert (
        "pip==26.2 --hash=sha256:931c303696af6fa3417112103b1cad26890e5a07eccb5b99783700e33f2b8aad"
        in text
    )


def test_optional_ml_snapshot_reused_not_replaced():
    for name in ["windows", "linux"]:
        text = (
            ROOT / f"requirements-remediation-{name}-candidate-20261009.txt"
        ).read_text()
        assert "-r requirements-runtime-ml-20261006.txt" in text


@pytest.mark.parametrize("changed", ["pip", "pytest", "oauthlib", "requests-oauthlib"])
def test_smoke_refuses_stale_versions(changed):
    versions = {
        "pip": "26.2",
        "pytest": "9.0.3",
        "oauthlib": "4.0.0",
        "requests-oauthlib": "2.0.0",
    }
    versions[changed] = "old-version"
    with patch.object(
        MODULE.importlib.metadata, "version", side_effect=versions.__getitem__
    ):
        with pytest.raises(ValueError, match="candidate version mismatch"):
            MODULE.collect(None)


def test_smoke_existing_output_refused_before_imports(tmp_path):
    path = tmp_path / "existing"
    path.write_bytes(b"failed evidence")
    with (
        patch("sys.argv", ["candidate", "--output", str(path)]),
        patch.object(MODULE.importlib.metadata, "version") as version,
    ):
        assert MODULE.evidence_main(MODULE.collect) == 1
    version.assert_not_called()
    assert path.read_bytes() == b"failed evidence"
