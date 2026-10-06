"""One exclusive Linux read-only receive observation; no service control/retries."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard import systemd_receiver as receiver, systemd_job as jobs

SOURCES = (
    "scripts/systemd_receiver_capture.py",
    "cloudguard/systemd_receiver.py",
    "cloudguard/systemd_job.py",
    "cloudguard/__init__.py",
)
RUN_DIR = ROOT / "output" / "engine2-systemd-receiver-observation-20261006"
CHILD_TIMEOUT = 20
NATIVE_ALARM = 18
CLEANUP_TIMEOUT = 2
OUTPUT_LIMIT = 65536
PROTOCOL = "systemd_receive_capture_v1"


def source_hashes():
    return {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCES
    }


def write_exclusive(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def strict_json(raw):
    if not isinstance(raw, bytes) or not 0 < len(raw) <= OUTPUT_LIMIT:
        raise ValueError("invalid child receipt size")

    def pairs(values):
        result = {}
        for key, value in values:
            if key in result:
                raise ValueError("duplicate receipt key")
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError("nonfinite receipt value")

    return json.loads(
        raw.decode("utf-8", errors="strict"),
        object_pairs_hook=pairs,
        parse_constant=invalid_constant,
    )


def checked_sources(value, names=SOURCES):
    if (
        not isinstance(value, dict)
        or set(value) != set(names)
        or any(
            not isinstance(digest, str) or not re.fullmatch("[0-9a-f]{64}", digest)
            for digest in value.values()
        )
    ):
        raise ValueError("invalid selected source hashes")
    return dict(value)


def checked_receiver(value, expected):
    flags = {
        "matches_acknowledged",
        "subscription_acknowledged",
        "continuity_checks_passed",
        "subscription_released",
        "connection_closed",
        "jobs_submitted_or_canceled",
        "services_modified",
        "native_binding_verified",
        "service_quiesced_verified",
        "may_disarm_recovery",
    }
    required = flags | {
        "protocol",
        "status",
        "stage",
        "backend",
        "window_seconds",
        "process_limit",
        "process_calls",
        "events",
        "source_sha256",
    }
    optional = {
        "epoch_before",
        "epoch_after",
        "error_type",
        "source_sha256_after",
        "library_sha256_after",
        "error_errno",
    }
    if (
        not isinstance(value, dict)
        or not required <= set(value)
        or set(value) - required - optional
    ):
        raise ValueError("invalid receiver fields")
    if (
        value["protocol"] != "systemd_receive_readonly_v1"
        or value["status"] not in {"observed", "unknown"}
        or value["stage"]
        not in {
            "identity",
            "matches",
            "subscribe",
            "identity_after_setup",
            "receive",
            "identity_after_window",
            "unsubscribe",
            "complete",
            "close",
            "source_postflight",
        }
        or any(type(value[key]) is not bool for key in flags)
        or any(
            value[key] is not False
            for key in {
                "jobs_submitted_or_canceled",
                "services_modified",
                "native_binding_verified",
                "service_quiesced_verified",
                "may_disarm_recovery",
            }
        )
        or type(value["window_seconds"]) is not int
        or value["window_seconds"] != 5
        or type(value["process_limit"]) is not int
        or value["process_limit"] != 512
        or type(value["process_calls"]) is not int
        or not 0 <= value["process_calls"] <= 512
    ):
        raise ValueError("incompatible receiver evidence")
    backend = value["backend"]
    if (
        not isinstance(backend, dict)
        or set(backend) != {"library_path", "library_sha256", "abi", "uid"}
        or backend["library_path"] != "/usr/lib/x86_64-linux-gnu/libsystemd.so.0.38.0"
        or backend["library_sha256"] != receiver.LIBRARY_SHA256
        or backend["abi"] != "linux-x86_64-lp64-little-glibc2.39"
        or type(backend["uid"]) is not int
        or backend["uid"] <= 0
    ):
        raise ValueError("incompatible receiver backend")
    for key in {"epoch_before", "epoch_after"} & set(value):
        jobs.epoch(value[key])
    if "error_type" in value and (
        not isinstance(value["error_type"], str)
        or not re.fullmatch("[A-Za-z][A-Za-z0-9]{0,63}", value["error_type"])
    ):
        raise ValueError("invalid sanitized error type")
    if "error_errno" in value and (
        type(value["error_errno"]) is not int
        or not 0 < value["error_errno"] < 4096
        or "error_type" not in value
    ):
        raise ValueError("invalid sanitized errno")
    checked_sources(value["source_sha256"], SOURCES[1:])
    if "source_sha256_after" in value:
        checked_sources(value["source_sha256_after"], SOURCES[1:])
    if "library_sha256_after" in value and (
        not isinstance(value["library_sha256_after"], str)
        or not re.fullmatch("[0-9a-f]{64}", value["library_sha256_after"])
    ):
        raise ValueError("invalid library hash")
    if not isinstance(value["events"], list) or len(value["events"]) > 32:
        raise ValueError("invalid selected event buffer")
    if value["events"]:
        validator = jobs.JobEvidence(
            value["epoch_before"], subscribed=True, matched=True
        )
        validator.begin()
        for event in value["events"]:
            if not validator.removed(event):
                raise ValueError("unselected event refused")
    if value["status"] == "observed" and (
        value["stage"] != "complete"
        or "error_type" in value
        or not all(
            value[key] is True
            for key in flags
            if key.endswith("acknowledged")
            or key
            in {
                "continuity_checks_passed",
                "subscription_released",
                "connection_closed",
            }
        )
        or value.get("epoch_after") != value.get("epoch_before")
        or "epoch_before" not in value
        or value["source_sha256"] != {name: expected[name] for name in SOURCES[1:]}
        or value.get("source_sha256_after") != value["source_sha256"]
        or value.get("library_sha256_after") != receiver.LIBRARY_SHA256
    ):
        raise ValueError("incomplete successful observation")
    return value


def child(expected):
    result = dict(protocol=PROTOCOL, status="failed")
    try:
        expected = checked_sources(strict_json(expected.encode()))
        result["source_sha256"] = source_hashes()
        if result["source_sha256"] != expected:
            raise ValueError("sources changed before native observation")
        result["receiver"] = receiver.observe()
        result["source_sha256_after"] = source_hashes()
        if result["source_sha256_after"] != expected:
            raise ValueError("sources changed after native observation")
        result["status"] = "returned"
    except (Exception, KeyboardInterrupt) as error:
        result["error_type"] = type(error).__name__
        if (
            isinstance(error, OSError)
            and type(error.errno) is int
            and 0 < error.errno < 4096
        ):
            result["error_errno"] = error.errno
    return result


def run_child(expected):
    if sys.platform != "linux" or os.geteuid() == 0:
        raise RuntimeError("ordinary-user Linux capture required")
    process = subprocess.Popen(
        [
            sys.executable,
            str(ROOT / SOURCES[0]),
            "--native-child",
            "--sources",
            json.dumps(expected),
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        shell=False,
        start_new_session=True,
    )
    outcome = dict(
        child_started=True,
        child_reaped=False,
        timed_out=False,
        cleanup_signal=None,
        exit_code=None,
        stdout=b"",
    )
    try:
        outcome["stdout"], _ = process.communicate(timeout=CHILD_TIMEOUT)
    except (Exception, KeyboardInterrupt) as error:
        outcome.update(
            timed_out=isinstance(error, subprocess.TimeoutExpired),
            error_type=type(error).__name__,
            cleanup_signal="terminate",
        )
        try:
            process.terminate()
            outcome["stdout"], _ = process.communicate(timeout=CLEANUP_TIMEOUT)
        except (subprocess.TimeoutExpired, OSError, KeyboardInterrupt):
            outcome["cleanup_signal"] = "kill"
            try:
                process.kill()
                outcome["stdout"], _ = process.communicate(timeout=CLEANUP_TIMEOUT)
            except (subprocess.TimeoutExpired, OSError, KeyboardInterrupt):
                return outcome
    outcome.update(child_reaped=True, exit_code=process.returncode)
    return outcome


def capture(directory=RUN_DIR, runner=run_child):
    directory = Path(directory)
    directory.mkdir(exist_ok=False)  # No deletion, overwrite or replacement attempt.
    started = dict(
        protocol=PROTOCOL,
        status="started",
        planned_attempts=1,
        recorded_at=datetime.now(timezone.utc).isoformat(),
        window_seconds=5,
        child_timeout_seconds=CHILD_TIMEOUT,
        native_alarm_seconds=NATIVE_ALARM,
        cleanup_timeout_seconds=CLEANUP_TIMEOUT,
        services_modified=False,
        jobs_submitted_or_canceled=False,
    )
    report = dict(
        protocol=PROTOCOL,
        status="unknown",
        stage="prepare",
        receiver=None,
        services_modified=False,
        jobs_submitted_or_canceled=False,
        may_disarm_recovery=False,
    )
    write_exclusive(directory / "started.json", started)
    try:
        report["source_sha256"] = source_hashes()
        report["stage"] = "child"
        outcome = runner(report["source_sha256"])
        raw = outcome.pop("stdout")
        report["process"] = outcome
        report["child_stdout_sha256"] = hashlib.sha256(raw).hexdigest()
        report["child_stdout_bytes"] = len(raw)
        report["stage"] = "validate_child"
        if (
            outcome.get("error_type")
            or outcome["timed_out"]
            or not outcome["child_reaped"]
        ):
            raise RuntimeError("child deadline or cleanup not successful")
        parsed = strict_json(raw)
        if not isinstance(parsed, dict) or parsed.get("protocol") != PROTOCOL:
            raise ValueError("invalid child envelope")
        if parsed.get("status") == "failed":
            error_type = parsed.get("error_type")
            if not isinstance(error_type, str) or not re.fullmatch(
                "[A-Za-z][A-Za-z0-9]{0,63}", error_type
            ):
                raise ValueError("invalid child failure type")
            report["child_error_type"] = error_type
            if "error_errno" in parsed:
                if (
                    type(parsed["error_errno"]) is not int
                    or not 0 < parsed["error_errno"] < 4096
                ):
                    raise ValueError("invalid child errno")
                report["child_error_errno"] = parsed["error_errno"]
            raise RuntimeError("native child failed")
        if (
            set(parsed)
            != {
                "protocol",
                "status",
                "source_sha256",
                "source_sha256_after",
                "receiver",
            }
            or parsed["status"] != "returned"
            or outcome["exit_code"] != 0
            or parsed["source_sha256"] != report["source_sha256"]
            or parsed["source_sha256_after"] != report["source_sha256"]
        ):
            raise ValueError("incompatible child envelope")
        report["receiver"] = checked_receiver(
            parsed["receiver"], report["source_sha256"]
        )
        report["stage"] = "source_postflight"
        report["source_sha256_after"] = source_hashes()
        if report["source_sha256_after"] != report["source_sha256"]:
            raise ValueError("parent sources changed")
        report.update(status=report["receiver"]["status"], stage="complete")
    except (Exception, KeyboardInterrupt) as error:
        report["error_type"] = type(error).__name__
    finally:
        write_exclusive(directory / "result.json", report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observe", action="store_true")
    parser.add_argument("--native-child", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--sources", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.native_child:
        if args.observe or args.sources is None:
            parser.error("invalid child arguments")
        if sys.platform != "linux" or os.geteuid() == 0:
            parser.error("ordinary-user Linux child required")
        # Default OS action terminates a stuck native call even if parent dies.
        # This is an adjusted kernel timer, not an absolute physical deadline.
        signal.signal(signal.SIGALRM, signal.SIG_DFL)
        signal.alarm(NATIVE_ALARM)
        try:
            value = child(args.sources)
        finally:
            signal.alarm(0)
        print(json.dumps(value, allow_nan=False))
        return 0 if value["status"] == "returned" else 1
    if not args.observe or args.sources is not None:
        parser.error("explicit --observe required")
    if sys.platform != "linux" or os.geteuid() == 0:
        parser.error("ordinary-user Linux required; Windows may review/test only")
    value = capture()
    print(
        json.dumps(
            dict(status=value["status"], stage=value["stage"], directory=str(RUN_DIR))
        )
    )
    return 0 if value["status"] == "observed" else 1


if __name__ == "__main__":
    sys.exit(main())
