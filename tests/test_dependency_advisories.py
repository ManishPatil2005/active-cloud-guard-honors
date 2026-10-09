import importlib.util
import io
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

spec = importlib.util.spec_from_file_location(
    "advisory_check",
    Path(__file__).resolve().parents[1] / "scripts/dependency_advisory_check.py",
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
PACKAGE = {"name": "demo", "version": "1.0"}


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {},
        {"results": []},
        {"results": [None]},
        {"results": [{"next_page_token": "more"}]},
        {"results": [{"vulns": None}]},
        {"results": [{"vulns": [{"id": "../private"}]}]},
        {"results": [{"vulns": [{"id": "GHSA-demo"}, {"id": "GHSA-demo"}]}]},
    ],
)
def test_bad_database_reply_rejected(payload):
    with patch.object(module, "build_opener") as opener:
        opener.return_value.open.return_value = io.BytesIO(json.dumps(payload).encode())
        with pytest.raises(ValueError):
            module.lookup([PACKAGE])


def test_public_query_and_allowlisted_projection():
    with patch.object(module, "build_opener") as opener:
        opener.return_value.open.return_value = io.BytesIO(
            b'{"results":[{"vulns":[{"id":"GHSA-demo","modified":"private ignored"}]}]}'
        )
        assert module.lookup([PACKAGE]) == [
            dict(PACKAGE, status="queried", advisory_ids=["GHSA-demo"])
        ]
        request = opener.return_value.open.call_args.args[0]
        assert request.full_url == module.URL
        assert json.loads(request.data) == {
            "queries": [
                {"package": {"name": "demo", "ecosystem": "PyPI"}, "version": "1.0"}
            ]
        }
        assert opener.return_value.open.call_args.kwargs["timeout"] == 30


def test_partial_failure_preserves_completed_and_unqueried():
    packages = [dict(name=f"demo{i}", version="1.0") for i in range(33)]
    completed = [dict(p, status="queried", advisory_ids=[]) for p in packages[:32]]
    with (
        patch.object(module, "inventory", return_value=packages),
        patch.object(
            module, "lookup", side_effect=[completed, OSError("private token")]
        ) as lookup,
    ):
        reports, code = module.collect(None)
    report = reports["output"]
    assert code == 1 and lookup.call_count == 2
    assert report["queried_count"] == 32
    assert report["packages"][-1]["status"] == "not_queried"
    assert report["packages"][-1]["advisory_ids"] is None
    assert "private token" not in json.dumps(report)
    assert not report["vulnerability_free"] and not report["exploitability_verified"]


@pytest.mark.parametrize(
    "packages",
    [
        [],
        [SimpleNamespace(metadata={"Name": "../bad"}, version="1")],
        [SimpleNamespace(metadata={"Name": "ok"}, version="bad/path")],
        [
            SimpleNamespace(metadata={"Name": "Demo_pkg"}, version="1"),
            SimpleNamespace(metadata={"Name": "demo-pkg"}, version="1"),
        ],
    ],
)
def test_invalid_inventory_refused(packages):
    with patch.object(
        module.importlib.metadata, "distributions", return_value=packages
    ):
        with pytest.raises(ValueError):
            module.inventory()


def test_redirect_never_followed():
    with pytest.raises(ValueError):
        module.NoRedirect().redirect_request(
            None, None, 302, "", {}, "https://elsewhere.invalid"
        )


def test_existing_evidence_refused_before_inventory(tmp_path):
    output = tmp_path / "existing.json"
    output.write_bytes(b"original failed evidence")
    with (
        patch("sys.argv", ["check", "--output", str(output)]),
        patch.object(module, "inventory") as inventory,
    ):
        assert module.evidence_main(module.collect) == 1
    inventory.assert_not_called()
    assert output.read_bytes() == b"original failed evidence"
