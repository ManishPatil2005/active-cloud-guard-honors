"""Fail-stop comparison controller; service transport is separately approval-gated."""

import hashlib
import re
import time

from cloudguard import kernel_clock_state as kernel

LABELS = ("before", "stopped", "restored")
PROTOCOL = "guest_client_removal_controller_v1"
EXECUTION_SOURCES = (
    "scripts/clock_comparison_batch.py",
    "scripts/clock_restore_watchdog.py",
    "scripts/clock_comparison_transport.py",
    "cloudguard/clock_comparison.py",
    "scripts/clock_comparison_review.py",
    "scripts/kernel_clock_diagnostic.py",
    "cloudguard/kernel_clock_state.py",
    "scripts/clock_lineage.py",
    "cloudguard/clock_lineage.py",
    "cloudguard/boot_clock.py",
    "cloudguard/clock_check.py",
    # Preflight imports these modules even though it does not run their workloads.
    "scripts/paired_pilot.py",
    "scripts/sensor_trial.py",
    "scripts/workload_control.py",
    "cloudguard/__init__.py",
    "cloudguard/deployment.py",
    "cloudguard/verification.py",
    "cloudguard/workload.py",
    "cloudguard/correlation.py",
    "cloudguard/clock_domains.py",
    "cloudguard/cache.py",
    "cloudguard/sensor_adapter.py",
    "cloudguard/runtime.py",
)


def checked_service(value, stopped=False):
    expected = dict(
        active="inactive" if stopped else "active",
        sub="dead" if stopped else "running",
        unit="enabled",
    )
    if value != expected:
        raise ValueError("service state incompatible")
    return expected


def checked_sources(value):
    if (
        not isinstance(value, dict)
        or set(value) != set(EXECUTION_SOURCES)
        or any(
            not isinstance(k, str)
            or not re.fullmatch(r"(?:cloudguard|scripts)/[a-z_]+\.py", k)
            or not isinstance(v, str)
            or not re.fullmatch(r"[0-9a-f]{64}", v)
            for k, v in value.items()
        )
    ):
        raise ValueError("invalid execution source freeze")
    return dict(value)


def compare_verified(blocks):
    """Inputs must come from full receipt verification, not summaries alone."""
    if [b["label"] for b in blocks] != list(LABELS):
        raise ValueError("three ordered verified blocks required")
    if len({b["input_sha256"] for b in blocks}) != 3:
        raise ValueError("reused receipt refused")
    origin = blocks[0]
    for previous, block in zip(blocks, blocks[1:]):
        if (
            block["backend"] != origin["backend"]
            or block["sources"] != origin["sources"]
            or block["first"]["domain"] != origin["first"]["domain"]
        ):
            raise ValueError("between-block identity changed")
        kernel.checked_pair(block["first"], previous["last"])
    return dict(
        protocol=PROTOCOL,
        blocks=[
            dict(
                label=b["label"],
                input_sha256=b["input_sha256"],
                final_intervals=b["summary"]["rows"][-1],
                sampled_state_values=b["summary"]["sampled_state_values"],
            )
            for b in blocks
        ],
        service_history_authenticated=False,
        stable_clock_accepted=False,
        causal_attribution="not_proven",
        independent_evaluation=False,
        kernel_rate_state_reset=False,
    )


def run_comparison(ops, verify_receipt, *, approved=False, clock=None):
    """Injected operations only; the caller must obtain real human approval.

    Backend contract: enforce each timeout, retain exclusive partial child files,
    freeze execution sources, arm an independent restore watchdog before stop,
    and acknowledge disarm/reap only after verifying active state. A boolean
    is not authenticated approval; live use needs explicit operator authority.
    """
    if approved is not True:
        raise ValueError("specific intervention approval required")
    clock = clock or time.monotonic
    report = dict(
        protocol=PROTOCOL,
        status="started",
        phase="source_freeze",
        actions=[],
        blocks=[],
        environment_service_stop_attempted=False,
        restoration_status="not_required",
        watchdog_requested=False,
        kernel_rate_state_reset=False,
        sensor_started=False,
    )
    verified = []

    def call(name, method, **kwargs):
        action = dict(operation=name, status="started")
        report["actions"].append(action)
        try:
            value = method(**kwargs)
            action["status"] = "completed"
            return value
        except (Exception, KeyboardInterrupt) as error:
            action.update(status="failed", error_type=type(error).__name__)
            raise

    def fail(error):
        report.update(status="failed", error_type=type(error).__name__)
        report.setdefault("failure_phase", report["phase"])
        if report["blocks"] and report["blocks"][-1]["status"] == "started":
            report["blocks"][-1].update(
                status="failed", error_type=type(error).__name__
            )

    def preflight():
        value = call("preflight", ops.preflight, timeout=5)
        if (
            set(value) != {"lab_ready", "known_sensor_absent", "service"}
            or value["lab_ready"] is not True
            or value["known_sensor_absent"] is not True
        ):
            raise ValueError("preflight incompatible")
        checked_service(value["service"])

    def remaining(deadline, maximum):
        if deadline is None:
            return maximum
        available = min(maximum, deadline - clock())
        if available <= 0:
            raise TimeoutError("off-stage budget exhausted")
        return available

    def block(label, deadline=None):
        report["phase"] = label
        row = dict(label=label, status="started", stage="source_precheck")
        report["blocks"].append(row)
        if (
            call("source_check", ops.source_hashes, timeout=remaining(deadline, 5))
            != frozen
        ):
            raise ValueError("execution sources changed")
        row["stage"] = "service_precheck"
        checked_service(
            call("service_state", ops.service_state, timeout=remaining(deadline, 5)),
            stopped=label == "stopped",
        )
        row["stage"] = "collect"
        raw = call(label, ops.collect, label=label, timeout=remaining(deadline, 45))
        row["stage"] = "verify"
        if not isinstance(raw, bytes) or len(raw) > 100000:
            raise ValueError("bounded byte receipt required")
        row["input_sha256"] = hashlib.sha256(raw).hexdigest()
        value = verify_receipt(raw, label)
        if value["input_sha256"] != row["input_sha256"]:
            raise ValueError("verifier receipt digest differs")
        if any(frozen.get(k) != v for k, v in value["sources"].items()):
            raise ValueError("receipt sources do not match execution freeze")
        if verified:
            previous = verified[-1]
            if (
                value["backend"] != previous["backend"]
                or value["sources"] != previous["sources"]
            ):
                raise ValueError("between-block backend/sources changed")
            kernel.checked_pair(value["first"], previous["last"])
        row["stage"] = "service_postcheck"
        checked_service(
            call("service_state", ops.service_state, timeout=remaining(deadline, 5)),
            stopped=label == "stopped",
        )
        if (
            call("source_check", ops.source_hashes, timeout=remaining(deadline, 5))
            != frozen
        ):
            raise ValueError("execution sources changed")
        remaining(deadline, 5)
        verified.append(value)
        row.update(status="verified", stage="complete")

    try:
        frozen = checked_sources(call("source_freeze", ops.source_hashes, timeout=5))
        report["source_sha256"] = dict(frozen)
        report["phase"] = "preflight"
        preflight()
        block("before")
        report["phase"] = "watchdog_arm"
        report["watchdog_requested"] = True
        watchdog = call(
            "watchdog_arm", ops.arm_restore_watchdog, deadline_seconds=60, timeout=5
        )
        if (
            not isinstance(watchdog, dict)
            or set(watchdog) != {"armed", "independent_process", "deadline_seconds"}
            or watchdog["armed"] is not True
            or watchdog["independent_process"] is not True
            or type(watchdog["deadline_seconds"]) is not int
            or watchdog["deadline_seconds"] != 60
        ):
            raise ValueError("independent restore watchdog required")
        deadline = clock() + 45
        report["phase"] = "stop_service"
        report["environment_service_stop_attempted"] = True
        call("stop_service", ops.stop_service, timeout=remaining(deadline, 5))
        block("stopped", deadline)
    except (Exception, KeyboardInterrupt) as error:
        fail(error)
    finally:
        if report["watchdog_requested"]:
            try:
                if report["environment_service_stop_attempted"]:
                    report["restoration_status"] = "attempted"
                    call("start_service", ops.start_service, timeout=5)
                checked_service(call("restoration_state", ops.service_state, timeout=5))
                report["restoration_status"] = "active_verified"
                disarmed = call(
                    "watchdog_disarm", ops.disarm_restore_watchdog, timeout=5
                )
                if disarmed is not True:
                    raise ValueError("watchdog disarm/reap acknowledgement required")
                report["watchdog_status"] = "disarmed"
            except (Exception, KeyboardInterrupt) as error:
                report.update(status="failed", cleanup_error_type=type(error).__name__)
                report["restoration_status"] = (
                    "cleanup_failed_after_active_verification"
                    if report["restoration_status"] == "active_verified"
                    else "failed_watchdog_not_disarmed"
                )
    if report["status"] == "failed":
        return report
    try:
        block("restored")
        report["phase"] = "postflight"
        preflight()
        if call("source_check", ops.source_hashes, timeout=5) != frozen:
            raise ValueError("execution sources changed")
        report["summary"] = compare_verified(verified)
        report.update(status="complete", phase="complete", source_sha256=frozen)
    except (Exception, KeyboardInterrupt) as error:
        fail(error)
    return report
