import ast
import json
from pathlib import Path

import pytest

from cloudguard import clock_comparison as control, kernel_clock_state as kernel
from scripts import (
    clock_comparison_review as review,
    kernel_clock_diagnostic as observer,
)
from test_kernel_clock_state import fixture, metadata


def receipt(index):
    packets = fixture()
    delta = index * 100_000_000_000
    for p in packets:
        for key in p["sample"]:
            if key not in {"offset_lower_ns", "offset_upper_ns", "sampling_span_ns"}:
                p["sample"][key] += delta
        for label in ("before", "after"):
            p[label]["raw_before_ns"] += delta
            p[label]["raw_after_ns"] += delta
    m = metadata()
    sources = observer.source_hashes()
    return dict(
        protocol=kernel.PROTOCOL,
        status="observed",
        planned_reads=16,
        spacing_seconds=1,
        clock_settings_modified=False,
        sensor_started=False,
        backend=m,
        libc_sha256_after=m["libc_sha256"],
        source_sha256=sources,
        source_sha256_after=sources,
        packets=packets,
        summary=kernel.summarize(packets),
    )


def blobs():
    return {
        label: json.dumps(receipt(i)).encode() for i, label in enumerate(control.LABELS)
    }


class FakeOps:
    """No WSL/subprocess/native calls: service and watchdog are simulated."""

    def __init__(self, fail_at=None, error=ValueError):
        self.fail_at, self.error = fail_at, error
        self.calls = []
        self.service = dict(active="active", sub="running", unit="enabled")
        self.sources = review.execution_source_hashes()
        self.blobs = blobs()
        self.watchdog = False

    def invoke(self, name, timeout):
        assert 0 < timeout <= 45
        self.calls.append(name)
        if name == self.fail_at:
            raise self.error("private sentinel details")

    def preflight(self, timeout):
        self.invoke("preflight", timeout)
        return dict(
            lab_ready=True, known_sensor_absent=True, service=dict(self.service)
        )

    def source_hashes(self, timeout):
        self.invoke("sources", timeout)
        return self.sources

    def service_state(self, timeout):
        self.invoke("state", timeout)
        return dict(self.service)

    def collect(self, label, timeout):
        self.invoke(label, timeout)
        return self.blobs[label]

    def arm_restore_watchdog(self, deadline_seconds, timeout):
        assert deadline_seconds == 60
        self.invoke("arm", timeout)
        self.watchdog = True
        return dict(armed=True, independent_process=True, deadline_seconds=60)

    def stop_service(self, timeout):
        self.service.update(active="inactive", sub="dead")
        self.invoke(
            "stop", timeout
        )  # Failure can occur after a successful side effect.

    def start_service(self, timeout):
        self.invoke("start", timeout)
        self.service.update(active="active", sub="running")

    def disarm_restore_watchdog(self, timeout):
        self.invoke("disarm", timeout)
        self.watchdog = False
        return True


def run(ops, **kwargs):
    return control.run_comparison(ops, review.verify_receipt, approved=True, **kwargs)


@pytest.mark.parametrize("approved", [False, None, 1, "yes"])
def test_specific_approval_gate_has_no_operations(approved):
    ops = FakeOps()
    with pytest.raises(ValueError, match="approval"):
        control.run_comparison(ops, review.verify_receipt, approved=approved)
    assert ops.calls == []


def test_complete_simulation_is_not_live_or_stable_clock_evidence():
    ops = FakeOps()
    result = run(ops)
    assert result["status"] == "complete"
    assert [b["label"] for b in result["blocks"]] == list(control.LABELS)
    assert result["restoration_status"] == "active_verified"
    assert result["environment_service_stop_attempted"] is True
    assert result["summary"]["stable_clock_accepted"] is False
    assert result["summary"]["service_history_authenticated"] is False
    assert ops.calls.index("arm") < ops.calls.index("stop") < ops.calls.index("start")
    assert (
        ops.calls.index("start")
        < ops.calls.index("disarm")
        < ops.calls.index("restored")
    )
    assert ops.service["active"] == "active" and not ops.watchdog


@pytest.mark.parametrize(
    "stage", ["preflight", "before", "arm", "stop", "stopped", "restored", "disarm"]
)
@pytest.mark.parametrize("error", [ValueError, KeyboardInterrupt])
def test_failure_interrupt_first_stop_restore_and_redact(stage, error):
    ops = FakeOps(stage, error)
    result = run(ops)
    assert result["status"] == "failed"
    assert "private sentinel" not in json.dumps(result)
    if stage in {"stop", "stopped", "restored", "disarm"}:
        assert "start" in ops.calls and ops.service["active"] == "active"
    else:
        assert "stop" not in ops.calls
    if stage != "restored":
        assert "restored" not in ops.calls
    if stage == "stopped":
        assert result["restoration_status"] == "active_verified" and not ops.watchdog
    if stage == "stop":
        assert result["restoration_status"] == "active_observed_stop_delivery_uncertain"
        assert ops.watchdog and "disarm" not in ops.calls
    if stage == "stopped":
        assert result["blocks"][-1]["status"] == "failed"


def test_failed_start_leaves_watchdog_and_cancels_remaining_measurement():
    ops = FakeOps("start")
    result = run(ops)
    assert result["status"] == "failed"
    assert result["restoration_status"] == "failed_watchdog_not_disarmed"
    assert ops.watchdog and "disarm" not in ops.calls and "restored" not in ops.calls


def test_off_stage_deadline_exhaustion_cleans_up_without_collecting():
    ops = FakeOps()
    now = [0]
    original = ops.stop_service

    def stop(timeout):
        original(timeout)
        now[0] = 46

    ops.stop_service = stop
    result = run(ops, clock=lambda: now[0])
    assert result["error_type"] == "TimeoutError" and "stopped" not in ops.calls
    assert result["restoration_status"] == "active_verified" and not ops.watchdog


@pytest.mark.parametrize("mode", ["sensor", "lab", "disabled", "inactive", "truthy"])
def test_preflight_refusals_no_stop(mode):
    ops = FakeOps()
    value = ops.preflight(5)
    ops.calls.clear()
    if mode == "sensor":
        value["known_sensor_absent"] = False
    elif mode == "lab":
        value["lab_ready"] = False
    elif mode == "disabled":
        value["service"]["unit"] = "disabled"
    elif mode == "inactive":
        value["service"].update(active="inactive", sub="dead")
    else:
        value["lab_ready"] = 1
    ops.preflight = lambda **kwargs: value
    assert run(ops)["status"] == "failed" and "stop" not in ops.calls


@pytest.mark.parametrize("mode", ["truthy", "float", "not_independent", "extra"])
def test_bad_watchdog_ack_never_stops(mode):
    ops = FakeOps()
    ack = dict(armed=True, independent_process=True, deadline_seconds=60)
    if mode == "truthy":
        ack["armed"] = 1
    elif mode == "float":
        ack["deadline_seconds"] = 60.0
    elif mode == "not_independent":
        ack["independent_process"] = False
    else:
        ack["extra"] = True
    ops.arm_restore_watchdog = lambda **kwargs: ack
    assert run(ops)["status"] == "failed" and "stop" not in ops.calls


def test_mutated_source_mapping_is_not_aliased_to_freeze():
    ops = FakeOps()
    original = ops.collect

    def collect(label, timeout):
        data = original(label, timeout)
        if label == "stopped":
            ops.sources["cloudguard/clock_comparison.py"] = "b" * 64
        return data

    ops.collect = collect
    result = run(ops)
    assert (
        result["status"] == "failed"
        and result["restoration_status"] == "active_verified"
    )
    assert "restored" not in ops.calls


@pytest.mark.parametrize(
    "mode",
    ["count", "reuse", "order", "backend", "domain", "sources", "summary", "bool"],
)
def test_full_offline_blocks_refuse_incompatible_inputs(mode):
    data = blobs()
    if mode == "reuse":
        data["stopped"] = data["before"]
    elif mode == "order":
        data["before"], data["stopped"] = data["stopped"], data["before"]
    else:
        r = json.loads(data["stopped"])
        if mode == "count":
            r["packets"].pop()
        elif mode == "backend":
            r["backend"]["libc_sha256"] = "b" * 64
            r["libc_sha256_after"] = "b" * 64
        elif mode == "domain":
            for p in r["packets"]:
                p["domain"]["time_namespace"] = "time:[99]"
                p["domain"]["time_namespace_for_children"] = "time:[99]"
        elif mode == "sources":
            r["source_sha256"]["scripts/clock_lineage.py"] = "b" * 64
        elif mode == "summary":
            r["summary"]["state_read_count"] = 32.0
        else:
            r["packets"][0]["before"]["state"]["query_modes"] = False
        data["stopped"] = json.dumps(r).encode()
    with pytest.raises((ValueError, KeyError)):
        control.compare_verified(
            [review.verify_receipt(data[label], label) for label in control.LABELS]
        )


def test_bad_receipt_digest_retained_failure_restore():
    ops = FakeOps()
    ops.blobs["stopped"] = b'{"invalid":"private sentinel"}'
    result = run(ops)
    assert result["blocks"][-1]["stage"] == "verify"
    assert len(result["blocks"][-1]["input_sha256"]) == 64
    assert result["restoration_status"] == "active_verified"
    assert "private sentinel" not in json.dumps(result)


def test_cli_offline_exclusive_output_and_unknown_label(tmp_path, monkeypatch):
    data = blobs()
    args = ["review"]
    for label, raw in data.items():
        path = tmp_path / f"{label}.json"
        path.write_bytes(raw)
        args += [f"--{label}", str(path)]
    target = tmp_path / "summary.json"
    args += ["--output", str(target)]
    monkeypatch.setattr(review.sys, "argv", args)
    assert review.main() == 0
    original = target.read_bytes()
    with pytest.raises(FileExistsError):
        review.main()
    assert target.read_bytes() == original
    with pytest.raises(ValueError):
        review.verify_receipt(data["before"], "unknown")


def test_restore_command_success_without_active_state_is_not_restoration():
    ops = FakeOps()
    ops.start_service = lambda timeout: ops.invoke("start", timeout)
    result = run(ops)
    assert result["restoration_status"] == "failed_watchdog_not_disarmed"
    assert ops.watchdog and "disarm" not in ops.calls and "restored" not in ops.calls


def test_incorrect_verifier_digest_cannot_complete_block():
    ops = FakeOps()

    def incorrect(raw, label):
        value = review.verify_receipt(raw, label)
        value["input_sha256"] = "b" * 64
        return value

    result = control.run_comparison(ops, incorrect, approved=True)
    assert result["status"] == "failed" and result["blocks"][0]["status"] == "failed"
    assert "stop" not in ops.calls


@pytest.mark.parametrize("mode", ["empty", "path", "hash"])
def test_invalid_source_freeze_never_stops(mode):
    ops = FakeOps()
    if mode == "empty":
        ops.sources = {}
    elif mode == "path":
        ops.sources["../outside"] = "a" * 64
    else:
        ops.sources["cloudguard/clock_comparison.py"] = True
    assert run(ops)["status"] == "failed" and "stop" not in ops.calls


def test_oversized_receipt_stops_before_parser_and_redacts():
    ops = FakeOps()
    ops.blobs["stopped"] = b"x" * 100001
    result = run(ops)
    assert result["blocks"][-1]["status"] == "failed"
    assert result["restoration_status"] == "active_verified"
    assert "restored" not in ops.calls


PREFLIGHT_SOURCES = control.EXECUTION_SOURCES[11:]


@pytest.mark.parametrize("path", PREFLIGHT_SOURCES)
def test_preflight_dependency_change_refuses_collection_and_stop(path):
    ops = FakeOps()
    original = ops.preflight
    frozen = dict(ops.sources)

    def changed(timeout):
        value = original(timeout)
        ops.sources[path] = "b" * 64
        return value

    ops.preflight = changed
    result = run(ops)
    assert result["status"] == "failed"
    assert result["source_sha256"] == frozen
    assert "before" not in ops.calls and "stop" not in ops.calls
    assert result["blocks"][0]["stage"] == "source_precheck"


def test_source_freeze_precedes_preflight_and_failure_keeps_frozen_hashes():
    ops = FakeOps("preflight")
    result = run(ops)
    assert ops.calls == ["sources", "preflight"]
    assert result["source_sha256"] == ops.sources
    assert result["failure_phase"] == "preflight"


def test_missing_source_refuses_preflight_before_any_lab_operation(monkeypatch):
    ops = FakeOps()

    def missing(timeout):
        ops.invoke("sources", timeout)
        raise FileNotFoundError("private path")

    ops.source_hashes = missing
    result = run(ops)
    assert result["status"] == "failed" and ops.calls == ["sources"]
    assert result["failure_phase"] == "source_freeze"
    assert "private path" not in json.dumps(result)


def test_frozen_sources_cover_static_local_import_closure():
    # Parse source, never import preflight/sensor modules or execute their code.
    # This checks ordinary Python imports, not dynamic imports/binary attestation.
    root = Path(review.ROOT)
    pending = list(control.EXECUTION_SOURCES)
    found = set()
    while pending:
        relative = pending.pop()
        if relative in found:
            continue
        found.add(relative)
        tree = ast.parse((root / relative).read_text(encoding="utf-8"))
        package = relative.split("/")[0]
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                assert node.level <= 1, "extend audit for nested relative imports"
                module = node.module or ""
                if node.level:
                    module = package + ("." + module if module else "")
                names = [module, *(module + "." + a.name for a in node.names)]
            for name in names:
                if name.split(".")[0] not in {"scripts", "cloudguard"}:
                    continue
                for candidate in (
                    name.replace(".", "/") + ".py",
                    name.replace(".", "/") + "/__init__.py",
                ):
                    if (root / candidate).is_file():
                        pending.append(candidate)
    assert found == set(control.EXECUTION_SOURCES)
    assert len(found) == len(control.EXECUTION_SOURCES) == 24


@pytest.mark.parametrize("error", [TimeoutError, ValueError, KeyboardInterrupt])
def test_delayed_stop_after_active_snapshot_never_disarms_recovery(error):
    ops = FakeOps()
    pending = []

    def delayed(timeout):
        ops.invoke("stop", timeout)
        pending.append("late_stop")
        raise error("private details")

    ops.stop_service = delayed
    result = run(ops)
    assert result["status"] == "failed"
    assert "start" in ops.calls and ops.service["active"] == "active"
    assert "disarm" not in ops.calls and ops.watchdog
    assert result["stop_delivery_status"] == "uncertain"
    assert result["operator_recovery_required"] is True
    assert result["restoration_status"] == "active_observed_stop_delivery_uncertain"
    assert "stopped" not in ops.calls and "restored" not in ops.calls
    # Deliver the simulated request after the active snapshot: it wasn't quiesced.
    assert pending.pop() == "late_stop"
    ops.service.update(active="inactive", sub="dead")
    assert ops.watchdog  # Not a guarantee of eventual native restoration.
