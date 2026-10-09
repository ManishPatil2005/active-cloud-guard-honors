import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load_runner(name):
    spec = importlib.util.spec_from_file_location(
        name, ROOT / "scripts" / (name + ".py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_rag_oversized_input_refuses_before_model(tmp_path):
    module = load_runner("rag_check")
    (tmp_path / "data/development").mkdir(parents=True)
    for name in (
        "postgres-trust.yaml",
        "redis-unprotected.yaml",
        "postgres-reference.yaml",
    ):
        (tmp_path / "data/development" / name).write_bytes(b"#" + b"x" * 1000000)
    with (
        patch.object(module, "ROOT", tmp_path),
        patch.object(module, "retrieve", return_value=[]),
        patch.object(module, "audit") as model,
        pytest.raises(ValueError, match="byte budget"),
    ):
        module.collect(SimpleNamespace(model="m"))
    model.assert_not_called()


def test_live_oversized_inventory_refuses_before_probe(tmp_path):
    module = load_runner("live_check")
    (tmp_path / "testbed").mkdir()
    (tmp_path / "testbed/inventory.json").write_bytes(b"[" + b" " * 1000000 + b"]")
    with (
        patch.object(module, "ROOT", tmp_path),
        patch.object(module, "probe") as probe,
        patch.object(module, "build_opener"),
        patch.object(module, "run"),
        pytest.raises(ValueError, match="byte budget"),
    ):
        module.collect(None)
    probe.assert_not_called()
