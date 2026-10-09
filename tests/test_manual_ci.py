from pathlib import Path
import re

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / ".github/workflows/manual-regression.yml"


@pytest.fixture
def workflow():
    return yaml.safe_load(PATH.read_text())


def test_only_manual_trigger_and_read_only_permissions(workflow):
    assert workflow["on"] == {"workflow_dispatch": {}}
    assert workflow["permissions"] == {"contents": "read"}
    assert "concurrency" not in workflow


def test_fixed_host_matrix_finite_budget_and_both_failures_retained(workflow):
    assert set(workflow["jobs"]) == {"regression"}
    job = workflow["jobs"]["regression"]
    assert job["timeout-minutes"] == 20
    assert job["strategy"] == {
        "fail-fast": False,
        "matrix": {"os": ["windows-2025", "ubuntu-24.04"]},
    }
    assert job["runs-on"] == "${{ matrix.os }}"
    assert workflow["defaults"]["run"]["shell"] == "pwsh"
    assert "permissions" not in job and "environment" not in job


@pytest.mark.parametrize(
    "action,pin",
    [
        ("actions/checkout", "3d3c42e5aac5ba805825da76410c181273ba90b1"),
        ("actions/setup-python", "5fda3b95a4ea91299a34e894583c3862153e4b97"),
        ("actions/upload-artifact", "cf430e030ddbb5b0abf93d22962f4752f3646cd9"),
    ],
)
def test_official_actions_are_exact_immutable_commit_pins(workflow, action, pin):
    uses = [
        row["uses"] for row in workflow["jobs"]["regression"]["steps"] if "uses" in row
    ]
    assert action + "@" + pin in uses
    assert len(uses) == 3
    assert all(re.fullmatch(r"actions/[a-z-]+@[0-9a-f]{40}", item) for item in uses)


def test_checkout_does_not_persist_credentials_and_python_is_exact(workflow):
    steps = workflow["jobs"]["regression"]["steps"]
    checkout = next(
        row for row in steps if row.get("uses", "").startswith("actions/checkout@")
    )
    python = next(
        row for row in steps if row.get("uses", "").startswith("actions/setup-python@")
    )
    assert checkout["with"] == {"persist-credentials": False}
    assert python["with"] == {"python-version": "3.12.14"}


def test_isolated_pinned_install_and_each_command_failure_visible(workflow):
    script = workflow["jobs"]["regression"]["steps"][2]["run"]
    assert "Test-Path -LiteralPath .venv" in script
    assert "--require-hashes" in script and "--only-binary=:all:" in script
    assert "--isolated" in script and "https://pypi.org/simple" in script
    assert "--retries 0 --resume-retries 0 --timeout 20" in script
    assert "requirements-core-current.txt" in script
    assert script.count("$LASTEXITCODE -ne 0") == 3
    assert "requirements-lock.txt" not in script and ".[vector" not in script


def test_minimized_offline_build_and_installed_artifact_tests(workflow):
    steps = workflow["jobs"]["regression"]["steps"]
    build = next(
        row["run"]
        for row in steps
        if row["name"] == "Build and install minimized local wheel"
    )
    assert "requirements-build-qualification-20261010.txt" in build
    assert "Get-ChildItem -LiteralPath cloudguard -File -Filter '*.py'" in build
    assert "Copy-Item -LiteralPath pyproject.toml" in build
    assert "--no-index --no-deps --no-build-isolation" in build
    assert "--target tmp/ci-installed" in build
    tests = next(
        row["run"]
        for row in steps
        if row["name"] == "Run full regressions including installed wheel"
    )
    assert "$env:ACG_PACKAGE_WHEEL" in tests and "$env:ACG_PACKAGE_TARGET" in tests
    assert "--basetemp=tmp/ci-tests" in tests and "--junitxml=output/ci-tests-" in tests
    assert "${{ github.run_id }}-${{ github.run_attempt }}" in tests


def test_only_receipts_uploaded_always_with_bounded_retention(workflow):
    upload = workflow["jobs"]["regression"]["steps"][-1]
    assert upload["if"] == "always()"
    options = upload["with"]
    assert options["path"].splitlines() == ["output/ci-*.json", "output/ci-*.xml"]
    assert options["include-hidden-files"] is False
    assert options["retention-days"] == 7
    assert options["if-no-files-found"] == "warn"


def test_no_secrets_deployment_live_services_or_automatic_dispatch():
    text = PATH.read_text()
    for prohibited in (
        "secrets.",
        "workflow_call:",
        "pull_request:",
        "schedule:",
        "docker compose",
        "aws ",
        "systemctl ",
        "gh workflow run",
    ):
        assert prohibited not in text
