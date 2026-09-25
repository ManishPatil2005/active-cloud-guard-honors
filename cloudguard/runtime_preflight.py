"""Read-only local host facts; never load a sensor or certify compatibility."""

from datetime import datetime, timezone
import os
from pathlib import Path
import platform
import stat


def path_fact(path, expected):
    """Distinguish absent, inaccessible and unexpected file types."""
    try:
        mode = Path(path).stat().st_mode
    except FileNotFoundError:
        return "absent"
    except OSError:
        return "unavailable"
    predicate = {"file": stat.S_ISREG, "directory": stat.S_ISDIR}[expected]
    return "present" if predicate(mode) else "unexpected_type"


def collect():
    system = platform.system()
    linux = system == "Linux"
    markers = {
        "kernel_btf": ("/sys/kernel/btf/vmlinux", "file"),
        "tracefs_path": ("/sys/kernel/tracing", "directory"),
        "cgroup_v2_controllers": ("/sys/fs/cgroup/cgroup.controllers", "file"),
    }
    return {
        "schema_version": "1.0",
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "evidence_level": "local_host_facts",
        "host": {
            "system": system,
            "release": platform.release(),
            "machine": platform.machine(),
            "effective_uid": os.geteuid() if linux else None,
        },
        "linux_markers": {
            name: path_fact(path, kind) if linux else "not_applicable"
            for name, (path, kind) in markers.items()
        },
        "status": "requires_sensor_specific_validation"
        if linux
        else "linux_host_required",
        "sensor_compatibility_verified": False,
        "runtime_sensor_connected": False,
        "actions_executed": [],
        "limitations": [
            "Facts describe this process's host and namespace, not a remote Docker daemon or another WSL distribution.",
            "Path presence does not prove readable BTF, mounted tracefs, effective capabilities or usable eBPF support.",
            "No driver load, sensor execution, Docker connection, network access or privilege change was attempted.",
            "Sensor version, event coverage, loss accounting, deployment identity and overhead remain unvalidated.",
        ],
    }
