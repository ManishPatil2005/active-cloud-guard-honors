import json
from unittest.mock import patch
import pytest
from cloudguard.pipeline import run
from cloudguard.scanner import literal_secret
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_secret_file_reference():
    assert not literal_secret("POSTGRES_PASSWORD_FILE", "/run/secrets/pg_password")
    assert literal_secret("POSTGRES_PASSWORD", "fixture-password")


def test_inconclusive_preserves_finding(tmp_path):
    inventory = tmp_path / "inventory.json"
    inventory.write_text(
        json.dumps([dict(asset_id="compose/redis", host="127.0.0.1", port=16379)])
    )
    with patch("cloudguard.pipeline.probe", return_value={"outcome": "inconclusive"}):
        result = run(
            ROOT / "data/development/redis-all.yaml",
            ROOT / "knowledge/sources.json",
            inventory,
        )
    assert len(result["findings"]) == 1
    assert result["findings"][0]["priority"]["exposure"] == "inconclusive"


def test_no_probe_for_secret(tmp_path):
    inventory = tmp_path / "inventory.json"
    inventory.write_text(
        json.dumps([dict(asset_id="compose/app", host="127.0.0.1", port=15432)])
    )
    with patch("cloudguard.pipeline.probe") as mocked:
        result = run(
            ROOT / "data/development/postgres-secret.yaml",
            ROOT / "knowledge/sources.json",
            inventory,
        )
    mocked.assert_not_called()
    assert result["findings"][0]["priority"]["exposure"] == "not_applicable"


def test_duplicate_asset_mapping_fails(tmp_path):
    inventory = tmp_path / "inventory.json"
    inventory.write_text(json.dumps([dict(asset_id="x")] * 2))
    with pytest.raises(ValueError):
        run(
            ROOT / "data/development/redis-all.yaml",
            ROOT / "knowledge/sources.json",
            inventory,
        )
