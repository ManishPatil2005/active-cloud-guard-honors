import ctypes
import json
from unittest.mock import patch

import pytest

from scripts import windows_job_diagnostic as module


class Api:
    def __init__(
        self, membership=1, flags=0, membership_ok=True, query_ok=True, size=None
    ):
        self.membership = membership
        self.flags = flags
        self.membership_ok = membership_ok
        self.query_ok = query_ok
        self.size = size
        self.queries = 0

    def GetCurrentProcess(self):
        return -1

    def IsProcessInJob(self, process, job, result):
        assert process == -1 and job is None
        ctypes.cast(
            result, ctypes.POINTER(ctypes.c_int32)
        ).contents.value = self.membership
        return self.membership_ok

    def QueryInformationJobObject(self, job, kind, output, size, returned):
        assert (
            job is None and kind == 9 and size == ctypes.sizeof(module.ExtendedLimits)
        )
        self.queries += 1
        ctypes.cast(
            output, ctypes.POINTER(module.ExtendedLimits)
        ).contents.basic.flags = self.flags
        ctypes.cast(returned, ctypes.POINTER(ctypes.c_uint32)).contents.value = (
            size if self.size is None else self.size
        )
        return self.query_ok


@pytest.mark.parametrize("flags", [0, 0x800, 0x1000, 0x2000, 0x3800, 0xFFFFFFFF])
def test_exact_selected_flags_and_null_current_job(flags):
    api = Api(flags=flags)
    report = module.read_job(api, lambda: 5)
    assert report["status"] == "observed" and report["limit_flags"] == flags
    assert report["breakaway_ok"] is bool(flags & 0x800)
    assert report["silent_breakaway_ok"] is bool(flags & 0x1000)
    assert report["kill_on_job_close"] is bool(flags & 0x2000)
    assert api.queries == 1 and report["error_code"] is None


@pytest.mark.parametrize("membership", [0, 2, -1])
def test_absent_or_invalid_membership_never_queries_limits(membership):
    api = Api(membership=membership)
    report = module.read_job(api, lambda: 5)
    assert report["status"] == (
        "not_in_job" if membership == 0 else "invalid_membership"
    )
    assert api.queries == 0 and report["limit_flags"] is None


@pytest.mark.parametrize("phase", ["membership", "limits"])
def test_native_failure_keeps_unknown_flags(phase):
    api = Api(membership_ok=phase != "membership", query_ok=phase != "limits")
    report = module.read_job(api, lambda: 5)
    assert report["status"] == f"{phase}_failed" and report["error_code"] == 5
    assert report["breakaway_ok"] is None and report["silent_breakaway_ok"] is None


@pytest.mark.parametrize("size", [0, 1, 999])
def test_wrong_native_length_not_observed(size):
    report = module.read_job(Api(size=size), lambda: 5)
    assert report["status"] == "invalid_limits_length"
    assert report["limit_flags"] is None


def test_non_windows_refuses_native_loading(monkeypatch):
    monkeypatch.setattr(module.sys, "platform", "linux")
    monkeypatch.setattr(module, "load_api", lambda: pytest.fail("native API called"))
    assert module.describe_current_job() == dict(
        status="unsupported_platform", platform="linux"
    )


def test_windows_scope_is_not_qualification(monkeypatch):
    monkeypatch.setattr(module.sys, "platform", "win32")
    monkeypatch.setattr(module, "load_api", lambda: Api(flags=0x800))
    monkeypatch.setattr(ctypes, "get_last_error", lambda: 5, raising=False)
    report = module.describe_current_job()
    assert report["status"] == "observed"
    assert report["policy_changed"] is report["helper_launch_qualified"] is False
    assert report["production_ready"] is False
    assert "ancestors" in report["scope"]
    assert len(json.dumps(report)) < 1024


def test_fixed_abi_layout_for_x64():
    if ctypes.sizeof(ctypes.c_void_p) == 8:
        assert ctypes.sizeof(module.BasicLimits) == 64
        assert module.BasicLimits.flags.offset == 16
        assert module.BasicLimits.affinity.offset == 48
        assert ctypes.sizeof(module.ExtendedLimits) == 144


def test_existing_output_refused_before_native_api(tmp_path):
    from cloudguard.evidence import evidence_main

    output = tmp_path / "job.json"
    output.write_bytes(b"preserved failure")
    with (
        patch("sys.argv", ["job", "--output", str(output)]),
        patch.object(module, "describe_current_job") as collect,
    ):
        assert evidence_main(module.collect) == 1
    collect.assert_not_called()
    assert output.read_bytes() == b"preserved failure"
