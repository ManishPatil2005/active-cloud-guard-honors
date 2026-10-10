"""Read current-process Windows job limits; never set policy or launch processes."""

import ctypes
from pathlib import Path
import sys


class BasicLimits(ctypes.Structure):
    _fields_ = [
        ("process_time", ctypes.c_int64),
        ("job_time", ctypes.c_int64),
        ("flags", ctypes.c_uint32),
        ("minimum_working_set", ctypes.c_size_t),
        ("maximum_working_set", ctypes.c_size_t),
        ("active_process_limit", ctypes.c_uint32),
        ("affinity", ctypes.c_size_t),
        ("priority_class", ctypes.c_uint32),
        ("scheduling_class", ctypes.c_uint32),
    ]


class ExtendedLimits(ctypes.Structure):
    _fields_ = [
        ("basic", BasicLimits),
        ("io_counters", ctypes.c_uint64 * 6),
        ("process_memory_limit", ctypes.c_size_t),
        ("job_memory_limit", ctypes.c_size_t),
        ("peak_process_memory", ctypes.c_size_t),
        ("peak_job_memory", ctypes.c_size_t),
    ]


def load_api():
    api = ctypes.WinDLL("kernel32", use_last_error=True)
    api.GetCurrentProcess.argtypes = []
    api.GetCurrentProcess.restype = ctypes.c_void_p
    api.IsProcessInJob.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_int32),
    ]
    api.IsProcessInJob.restype = ctypes.c_int32
    api.QueryInformationJobObject.argtypes = [
        ctypes.c_void_p,
        ctypes.c_int32,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32),
    ]
    api.QueryInformationJobObject.restype = ctypes.c_int32
    return api


def read_job(api, last_error):
    result = dict(
        status="membership_failed",
        in_job=None,
        limit_flags=None,
        breakaway_ok=None,
        silent_breakaway_ok=None,
        kill_on_job_close=None,
        error_code=None,
    )
    membership = ctypes.c_int32()
    if not api.IsProcessInJob(api.GetCurrentProcess(), None, ctypes.byref(membership)):
        result["error_code"] = last_error()
        return result
    if membership.value not in (0, 1):
        result["status"] = "invalid_membership"
        return result
    result["in_job"] = bool(membership.value)
    if not result["in_job"]:
        result["status"] = "not_in_job"
        return result
    limits = ExtendedLimits()
    returned = ctypes.c_uint32()
    if not api.QueryInformationJobObject(
        None, 9, ctypes.byref(limits), ctypes.sizeof(limits), ctypes.byref(returned)
    ):
        result["status"] = "limits_failed"
        result["error_code"] = last_error()
        return result
    if returned.value != ctypes.sizeof(limits):
        result["status"] = "invalid_limits_length"
        return result
    flags = limits.basic.flags
    result.update(
        status="observed",
        limit_flags=flags,
        breakaway_ok=bool(flags & 0x800),
        silent_breakaway_ok=bool(flags & 0x1000),
        kill_on_job_close=bool(flags & 0x2000),
    )
    return result


def describe_current_job():
    if sys.platform != "win32":
        return dict(status="unsupported_platform", platform=sys.platform)
    result = read_job(load_api(), ctypes.get_last_error)
    result.update(
        platform="win32",
        scope="Current process/immediate job only; ancestors and other access policies unqueried.",
        policy_changed=False,
        helper_launch_qualified=False,
        production_ready=False,
    )
    return result


def collect(args):
    report = describe_current_job()
    return {"output": report}, 0 if report["status"] in {
        "observed",
        "not_in_job",
    } else 1


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from cloudguard.evidence import evidence_main

    raise SystemExit(evidence_main(collect))
