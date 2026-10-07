"""Injected import faults, not a reproduction of the historical Windows fault."""

import builtins
import importlib.util
import json
from pathlib import Path
import sys

import pytest

from cloudguard import runtime_ml as ml, runtime_autoencoder as ae


@pytest.mark.parametrize(
    "model,module", [(ml, "sklearn.ensemble"), (ae, "sklearn.neural_network")]
)
@pytest.mark.parametrize(
    "kind,name,code,dependency",
    [
        (ImportError, None, "backend_import_failed", None),
        (ModuleNotFoundError, "sklearn", "optional_module_not_found", "sklearn"),
        (ModuleNotFoundError, "scipy.special", "backend_dependency_not_found", "scipy"),
        (ModuleNotFoundError, "private_module", "backend_dependency_not_found", None),
    ],
)
def test_import_category_is_preserved_without_private_text(
    monkeypatch, model, module, kind, name, code, dependency
):
    original = builtins.__import__

    def fail(selected, *args, **kwargs):
        if selected == module:
            raise kind("PRIVATE_BACKEND_TEXT", name=name)
        return original(selected, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fail)
    with pytest.raises(RuntimeError) as captured:
        model._backend()
    assert getattr(captured.value, "diagnostic", None) == dict(
        code=code, cause_kind=kind.__name__, dependency=dependency
    )
    assert "PRIVATE" not in str(captured.value)
    assert f"code={code}" in str(captured.value)
    assert f"cause={kind.__name__}" in str(captured.value)


@pytest.mark.parametrize(
    "name", ["threadpoolctl", "sklearn.ensemble", "numpy", None, b"private"]
)
@pytest.mark.parametrize(
    "model,module", [(ml, "sklearn.ensemble"), (ae, "sklearn.neural_network")]
)
def test_missing_name_shape_and_submodule_distinction(monkeypatch, model, module, name):
    original = builtins.__import__

    def fail(selected, *args, **kwargs):
        if selected == module:
            raise ModuleNotFoundError("PRIVATE", name=name)
        return original(selected, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fail)
    with pytest.raises(ml.RuntimeMLBackendError) as captured:
        model._backend()
    diagnostic = captured.value.diagnostic
    assert diagnostic["code"] == (
        "optional_module_not_found"
        if name == "threadpoolctl"
        else "backend_dependency_not_found"
    )
    assert diagnostic["dependency"] == {
        "threadpoolctl": "threadpoolctl",
        "sklearn.ensemble": "sklearn",
        "numpy": "numpy",
    }.get(name)
    assert "PRIVATE" not in json.dumps(diagnostic)


@pytest.mark.parametrize("kind", ["missing", "mismatch"])
def test_metadata_failure_is_typed_and_redacted(monkeypatch, kind):
    def version(_):
        if kind == "missing":
            raise ml.metadata.PackageNotFoundError("PRIVATE_METADATA_TEXT")
        return "PRIVATE_VERSION_TEXT"

    monkeypatch.setattr(ml.metadata, "version", version)
    with pytest.raises(ml.RuntimeMLBackendError) as captured:
        ml._verify_backend_version()
    assert captured.value.diagnostic == dict(
        code="backend_metadata_missing"
        if kind == "missing"
        else "backend_version_mismatch",
        cause_kind="PackageNotFoundError" if kind == "missing" else "VersionMismatch",
        dependency="scikit-learn",
    )
    assert "PRIVATE" not in str(captured.value)


@pytest.mark.parametrize(
    "arguments",
    [
        ("private", "ImportError", None),
        ("backend_import_failed", "PrivateType", None),
        ("backend_import_failed", "ImportError", "private"),
        ([], "ImportError", None),
    ],
)
def test_diagnostic_constructor_rejects_unowned_categories(arguments):
    with pytest.raises(ValueError):
        ml.RuntimeMLBackendError(*arguments)


def test_diagnostic_copy_and_unrelated_error_projection():
    error = ml.RuntimeMLBackendError("backend_import_failed", "ImportError")
    diagnostic = error.diagnostic
    diagnostic["dependency"] = "PRIVATE"
    assert ml.backend_failure_fields(error)["backend_diagnostic"]["dependency"] is None
    assert ml.backend_failure_fields(RuntimeError("PRIVATE")) == {}


def test_private_exception_subclass_name_not_exported():
    class PrivateImportType(ImportError):
        pass

    error = ml._import_failure(PrivateImportType("PRIVATE", name="private"))
    assert error.diagnostic == dict(
        code="backend_import_failed", cause_kind="ImportError", dependency=None
    )


@pytest.mark.parametrize("runner", ["runtime_ml_check", "runtime_autoencoder_check"])
@pytest.mark.parametrize(
    "code,cause",
    [
        ("backend_import_failed", "ImportError"),
        ("backend_metadata_missing", "PackageNotFoundError"),
        ("backend_version_mismatch", "VersionMismatch"),
    ],
)
def test_both_cli_failure_receipts_retain_only_safe_categories(
    monkeypatch, tmp_path, capsys, runner, code, cause
):
    path = Path(__file__).resolve().parents[1] / "scripts" / f"{runner}.py"
    spec = importlib.util.spec_from_file_location(runner, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    error = ml.RuntimeMLBackendError(
        code, cause, "scikit-learn" if cause != "ImportError" else None
    )

    def fail(*args, **kwargs):
        raise error

    monkeypatch.setattr(module, "compare_synthetic", fail)
    output = tmp_path / "fault.json"
    monkeypatch.setattr(sys, "argv", [str(path), "--output", str(output)])
    assert module.main() == 1
    report = json.loads(output.read_text())
    assert report["status"] == "rejected"
    assert report["error_type"] == "RuntimeMLBackendError"
    assert report["backend_diagnostic"] == error.diagnostic
    assert report["actions_executed"] == []
    assert "PRIVATE" not in output.read_text() + capsys.readouterr().out
    before = output.read_bytes()
    assert module.main() == 1
    assert output.read_bytes() == before
