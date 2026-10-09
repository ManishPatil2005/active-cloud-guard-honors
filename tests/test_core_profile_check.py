import hashlib
from unittest.mock import patch

import pytest

from scripts import core_profile_check as module


def sample(root, middle="Example_Package==1.2.3", tail="second==4.5.6"):
    bodies = [
        "# selected profile\n-r " + module.FILES[1] + "\n",
        middle + "\n-r " + module.FILES[2] + "\n",
        tail + "\n",
    ]
    for name, body in zip(module.FILES, bodies, strict=True):
        (root / name).write_text(body, encoding="utf-8")


def test_fixed_profile_normalizes_and_binds_actual_bytes(tmp_path):
    sample(tmp_path)
    pins, sources = module.profile(tmp_path)
    assert pins == {"example-package": "1.2.3", "second": "4.5.6"}
    assert sources == [
        {
            "file": name,
            "sha256": hashlib.sha256((tmp_path / name).read_bytes()).hexdigest(),
        }
        for name in module.FILES
    ]


def test_actual_recommended_profile_has_all_31_pins():
    pins, sources = module.profile()
    assert len(pins) == 31 and len(sources) == 3
    assert pins["pip"] == "26.2" and pins["pytest"] == "9.0.3"
    assert pins["oauthlib"] == "4.0.0" and "chromadb" not in pins


@pytest.mark.parametrize(
    "line",
    [
        "pkg>=1",
        "pkg==1 --hash=sha256:123",
        "https://example.test/wheel",
        "-e .",
        "--index-url https://example.test",
        "pkg==1 # inline",
        "bad name==1",
        "pkg==",
        "pkg==1\n-r ../../private",
        "pkg==1\n-r " + module.FILES[2],
    ],
)
def test_unsupported_or_extra_include_rejected(tmp_path, line):
    sample(tmp_path, middle=line)
    with pytest.raises(ValueError):
        module.profile(tmp_path)


@pytest.mark.parametrize("tail", ["Example-Package==1.2.3", "example.package==9"])
def test_duplicate_normalized_pin_refused_even_same_version(tmp_path, tail):
    sample(tmp_path, tail=tail)
    with pytest.raises(ValueError, match="duplicate"):
        module.profile(tmp_path)


def test_bad_include_does_not_read_arbitrary_path(tmp_path):
    (tmp_path / module.FILES[0]).write_text("-r private.txt\n")
    with patch.object(module, "read_bytes", wraps=module.read_bytes) as read:
        with pytest.raises(ValueError, match="include"):
            module.profile(tmp_path)
    assert read.call_count == 1


def test_oversized_profile_refused(tmp_path):
    sample(tmp_path)
    (tmp_path / module.FILES[0]).write_bytes(b"#" * 16_385)
    with pytest.raises(ValueError, match="budget"):
        module.profile(tmp_path)


def test_empty_and_too_many_pins_refused(tmp_path):
    sample(tmp_path, middle="# no pins", tail="# no pins")
    with pytest.raises(ValueError, match="empty"):
        module.profile(tmp_path)
    sample(tmp_path, middle="\n".join(f"pkg{i}==1" for i in range(129)))
    with pytest.raises(ValueError, match="count"):
        module.profile(tmp_path)


@pytest.mark.parametrize(
    "actual,status,exit_code",
    [("1", "match", 0), ("2", "mismatch", 1), (None, "missing", 1)],
)
def test_reports_complete_missing_mismatch_and_extra_inventory(
    actual, status, exit_code
):
    installed = [{"name": "extra", "version": "5"}]
    if actual is not None:
        installed.append({"name": "required", "version": actual})
    with (
        patch.object(module, "profile", return_value=({"required": "1"}, [])),
        patch.object(module, "inventory", return_value=installed),
    ):
        reports, code = module.collect(None)
    report = reports["output"]
    assert code == exit_code
    assert report["packages"] == [
        {
            "name": "required",
            "expected_version": "1",
            "installed_version": actual,
            "status": status,
        }
    ]
    assert report["counts"][status] == 1
    assert sum(report["counts"].values()) == report["required_count"] == 1
    assert report["extra_packages"] == [{"name": "extra", "version": "5"}]
    for field in (
        "vector_qualified",
        "extra_packages_qualified",
        "production_ready",
        "independent_evaluation",
    ):
        assert report[field] is False


def test_existing_receipt_refused_before_profile_or_inventory(tmp_path):
    output = tmp_path / "existing.json"
    output.write_bytes(b"negative evidence")
    with (
        patch("sys.argv", ["profile", "--output", str(output)]),
        patch.object(module, "profile") as profile,
        patch.object(module, "inventory") as inventory,
    ):
        assert module.evidence_main(module.collect) == 1
    profile.assert_not_called()
    inventory.assert_not_called()
    assert output.read_bytes() == b"negative evidence"
