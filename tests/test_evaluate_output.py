import importlib.util
import hashlib
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]


def evaluator():
    spec = importlib.util.spec_from_file_location(
        "development_evaluator", ROOT / "scripts/evaluate.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def setup_existing(tmp_path, monkeypatch):
    module = evaluator()
    (tmp_path / "data").mkdir()
    fixture = tmp_path / "data/case.yaml"
    fixture.write_bytes(b"services: {}\n")
    records = [
        dict(
            id="case",
            path="data/case.yaml",
            expected_rules=[],
            sha256=hashlib.sha256(fixture.read_bytes()).hexdigest(),
        )
    ]
    (tmp_path / "data/labels.json").write_text(json.dumps(records))
    (tmp_path / "output").mkdir()
    historical = tmp_path / "output/baseline-development.json"
    historical.write_bytes(b"preserved historical evidence\n")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["evaluate.py", "--output", str(historical)])
    calls = []

    def scan(*args):
        calls.append(args)
        return {"findings": []}

    monkeypatch.setattr(module, "scan", scan)
    return module, historical, calls


def test_existing_report_refused_before_scanning(tmp_path, monkeypatch):
    module, historical, calls = setup_existing(tmp_path, monkeypatch)
    try:
        result = module.main()
    except Exception:
        result = 1
    assert calls == []
    assert result == 1


def test_existing_report_bytes_preserved(tmp_path, monkeypatch):
    module, historical, calls = setup_existing(tmp_path, monkeypatch)
    module.main()
    assert historical.read_bytes() == b"preserved historical evidence\n"


def fresh_setup(tmp_path, monkeypatch):
    module, historical, calls = setup_existing(tmp_path, monkeypatch)
    output = tmp_path / "fresh.json"
    monkeypatch.setattr(sys, "argv", ["evaluate.py", "--output", str(output)])
    return module, historical, calls, output


def test_fresh_success_preserves_metrics_and_historical_report(tmp_path, monkeypatch):
    module, historical, calls, output = fresh_setup(tmp_path, monkeypatch)
    assert module.main() == 0
    report = json.loads(output.read_text())
    assert report["status"] == "development_regression_passed"
    assert len(calls) == 5 and report["repetitions"] == 5
    assert report["metrics"] == module.metrics({"case": False}, {"case": False})
    assert report["rule_set_mismatches"] == []
    assert len(report["raw"][0]["latency_ms"]) == 5
    assert historical.read_bytes() == b"preserved historical evidence\n"


def test_mismatches_saved_as_failed_evidence(tmp_path, monkeypatch):
    module, historical, calls, output = fresh_setup(tmp_path, monkeypatch)
    monkeypatch.setattr(
        module, "scan", lambda path: {"findings": [{"rule_id": "unexpected"}]}
    )
    assert module.main() == 1
    report = json.loads(output.read_text())
    assert report["status"] == "development_regression_failed"
    assert report["rule_set_mismatches"] == ["case"]
    assert report["raw"][0]["predicted"] == ["unexpected"]


def test_checksum_failure_refuses_scan_and_records_safe_error(tmp_path, monkeypatch):
    module, historical, calls, output = fresh_setup(tmp_path, monkeypatch)
    (tmp_path / "data/case.yaml").write_text("changed")
    assert module.main() == 1 and calls == []
    report = json.loads(output.read_text())
    assert report["status"] == "rejected" and report["error_type"] == "ValueError"
    assert str(tmp_path) not in output.read_text()


@pytest.mark.parametrize("changed", ["fixture", "manifest"])
def test_inputs_changed_during_scanning_rejected(tmp_path, monkeypatch, changed):
    module, historical, calls, output = fresh_setup(tmp_path, monkeypatch)
    target = tmp_path / (
        "data/case.yaml" if changed == "fixture" else "data/labels.json"
    )

    def scan(path):
        target.write_text("changed")
        return {"findings": []}

    monkeypatch.setattr(module, "scan", scan)
    assert module.main() == 1
    assert json.loads(output.read_text())["status"] == "rejected"


def test_selected_source_changed_rejected(tmp_path, monkeypatch):
    module, historical, calls, output = fresh_setup(tmp_path, monkeypatch)
    original = module.file_hash
    reads = []

    def changed_hash(path):
        if Path(path).name == "evaluate.py":
            reads.append(path)
            if len(reads) > 1:
                return "0" * 64
        return original(path)

    monkeypatch.setattr(module, "file_hash", changed_hash)
    assert module.main() == 1
    assert json.loads(output.read_text())["status"] == "rejected"


def test_empty_corpus_is_not_a_false_pass(tmp_path, monkeypatch):
    module, historical, calls, output = fresh_setup(tmp_path, monkeypatch)
    (tmp_path / "data/labels.json").write_text("[]")
    assert module.main() == 1
    assert json.loads(output.read_text())["status"] == "rejected"


def test_output_required_before_any_scan(tmp_path, monkeypatch):
    module, historical, calls = setup_existing(tmp_path, monkeypatch)
    monkeypatch.setattr(sys, "argv", ["evaluate.py"])
    with pytest.raises(SystemExit) as error:
        module.main()
    assert error.value.code == 2 and calls == []
    assert historical.read_bytes() == b"preserved historical evidence\n"
