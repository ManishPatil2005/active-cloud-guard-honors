"""Owned bounded sensor lifecycle only; no autonomous collection or live CLI."""

import copy
import hashlib
import io
import os
from pathlib import Path
import re
import sys
import tarfile
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.limits import json_value, read_bytes
from cloudguard.process_runner import (
    BinaryProcessResult,
    BoundedProcessError,
    ProcessResult,
    run_bounded,
)
from scripts.sensor_trial import IMAGE, rules
from scripts.window_transport import RedisWindowTransport

CONFIG_SHA = "0777b22af20748394a8f403e1a8e6c4c6452452a4de77f015723e463c0d2e54a"
OWNERSHIP_FORMAT = (
    '{"id":{{json .Id}},"name":{{json .Name}},"image":{{json .Config.Image}},'
    '"running":{{json .State.Running}},'
    '"nonce":{{json (index .Config.Labels "acg.window.nonce")}}}'
)


class SensorRejected(RuntimeError):
    pass


class SensorLease:
    def __init__(self, target_id, endpoint, *, runner=run_bounded):
        self.redis = RedisWindowTransport(target_id, endpoint, runner=runner)
        self._target = target_id
        self._endpoint = endpoint
        self._runner = runner
        self._nonce = uuid.uuid4().hex
        self._name = "acg-window-" + self._nonce
        self._id = None
        self._submitted = False
        self._sealed = False
        self._raw_dir = None
        self._report = dict(
            protocol="sensor_window_lease_v3",
            event_format="falco_fields_only_v1",
            retention_protocol="nonrotating_file_fsize_v1",
            event_file_limit_bytes=1_000_000,
            status="not_launched",
            launch_confirmed=False,
            launch_completion_uncertain=False,
            cleanup_attempted=False,
            removal_observed=False,
            cleanup_verified=False,
            collector_coverage="not_verified",
            independent_evaluation_verified=False,
            commands=[],
            faults=[],
        )

    def _command(self, phase, args, timeout=5, limit=4096, combine=False, binary=False):
        entry = dict(phase=phase, status="attempted")
        self._report["commands"].append(entry)
        try:
            if os.environ.get("DOCKER_HOST") or os.environ.get("DOCKER_CONTEXT"):
                raise SensorRejected("docker_environment_override")
            result = self._runner(
                ["docker", "--host", self._endpoint, *args],
                timeout=timeout,
                output_limit=limit,
                **({"binary": True} if binary else {}),
            )
            if (
                type(result) is not (BinaryProcessResult if binary else ProcessResult)
                or type(result.returncode) is not int
                or result.returncode != 0
                or type(result.stdout) is not (bytes if binary else str)
                or type(result.stderr) is not (bytes if binary else str)
                or (result.stderr and not combine)
                or len(result.stdout) + len(result.stderr) > limit
                or len(result.stdout if binary else result.stdout.encode("utf-8"))
                + len(result.stderr if binary else result.stderr.encode("utf-8"))
                > limit
            ):
                raise SensorRejected("invalid_client_result")
            entry["status"] = "completed"
            return result.stdout + result.stderr if combine else result.stdout
        except BoundedProcessError as error:
            entry.update(status="rejected", diagnostic=copy.deepcopy(error.diagnostic))
            self._report["faults"].append(
                dict(phase=phase, code="client_" + error.code)
            )
        except Exception as error:
            entry["status"] = "rejected"
            self._report["faults"].append(dict(phase=phase, code=type(error).__name__))
        raise SensorRejected("sensor command rejected: " + phase)

    def start(self, *, approved=False):
        if (
            approved is not True
            or self._submitted
            or self._sealed
            or self._report["status"] != "not_launched"
        ):
            raise SensorRejected("explicit reviewed launch and unused lease required")
        self._report["status"] = "preflight"
        try:
            self.redis.check_identity()
            config = ROOT / "testbed/falco-window-fields.yaml"
            if hashlib.sha256(read_bytes(config)).hexdigest() != CONFIG_SHA:
                raise SensorRejected("collector config changed")
            raw_dir = ROOT / "output/runtime-raw" / self._name
            raw_dir.mkdir(parents=True, exist_ok=False)
            self._raw_dir = raw_dir
            rule_path = raw_dir / "rules.yaml"
            rule_text = rules(self._target, correlation=True)
            with rule_path.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(rule_text)
                stream.flush()
                os.fsync(stream.fileno())
            if any(
                char in str(path)
                for path in (rule_path, config)
                for char in (",", "\n", "\r")
            ):
                raise SensorRejected("invalid bind source path")
            self._report.update(
                config_sha256=CONFIG_SHA,
                rules_sha256=hashlib.sha256(rule_text.encode()).hexdigest(),
            )
            self._submitted = True
            self._report["launch_completion_uncertain"] = True
            args = [
                "run",
                "-d",
                "--pull",
                "never",
                "--name",
                self._name,
                "--label",
                "acg.window.nonce=" + self._nonce,
                "--network",
                "none",
                "--cap-drop",
                "ALL",
                "--cap-add",
                "BPF",
                "--cap-add",
                "PERFMON",
                "--cap-add",
                "SYS_RESOURCE",
                "--cap-add",
                "SYS_PTRACE",
                "--memory",
                "512m",
                "--cpus",
                "1",
                "--pids-limit",
                "64",
                "--log-opt",
                "max-size=1m",
                "--log-opt",
                "max-file=1",
                "--ulimit",
                "fsize=1000000:1000000",
                "--mount",
                "type=bind,src=/proc,dst=/host/proc,readonly",
                "--mount",
                "type=bind,src=/sys/kernel/tracing,dst=/sys/kernel/tracing,readonly",
                "--mount",
                f"type=bind,src={rule_path},dst=/acg/rules.yaml,readonly",
                "--mount",
                f"type=bind,src={config},dst=/acg/config.yaml,readonly",
                "--entrypoint",
                "/usr/bin/timeout",
                IMAGE,
                "-s",
                "TERM",
                "-k",
                "3",
                "150",
                "/usr/bin/falco",
                "-c",
                "/acg/config.yaml",
                "-M",
                "140",
                "-r",
                "/acg/rules.yaml",
                "-U",
            ]
            returned = self._command("launch", args, timeout=10, limit=128).strip()
            if not re.fullmatch("[a-f0-9]{64}", returned):
                raise SensorRejected("invalid sensor ID")
            self._id = returned
            self._owned(require_running=True)
            self._report.update(
                status="launched_not_ready",
                launch_confirmed=True,
                launch_completion_uncertain=False,
            )
        except (Exception, KeyboardInterrupt) as error:
            self._report["status"] = "launch_rejected"
            self._report["faults"].append(
                dict(phase="start", code=type(error).__name__)
            )
            self.cleanup()
            raise
        return self.snapshot()

    def _owned(self, *, require_running=None):
        identity = json_value(
            self._command(
                "ownership",
                ["inspect", "--format", OWNERSHIP_FORMAT, self._id or self._name],
            )
        )
        if (
            not isinstance(identity, dict)
            or set(identity) != {"id", "name", "image", "running", "nonce"}
            or type(identity["id"]) is not str
            or not re.fullmatch("[a-f0-9]{64}", identity["id"])
            or (self._id is not None and identity["id"] != self._id)
            or identity["name"] != "/" + self._name
            or identity["image"] != IMAGE
            or identity["nonce"] != self._nonce
            or type(identity["running"]) is not bool
            or (
                require_running is not None
                and identity["running"] is not require_running
            )
        ):
            raise SensorRejected("sensor ownership not verified")
        self._id = identity["id"]
        return identity

    def cleanup(self):
        if self._sealed:
            return self.snapshot()
        self._sealed = True
        if not self._submitted:
            return self.snapshot()
        self._report["cleanup_attempted"] = True
        try:
            owned = self._owned()
            if owned["running"]:
                self._command(
                    "stop", ["stop", "--time", "3", self._id], timeout=10, limit=128
                )
                self._owned(require_running=False)
            # Preserve raw evidence before removing this container. On export
            # failure leave the stopped container for operator review.
            log = self._file("acg-events.jsonl", 1_000_000)
            with (self._raw_dir / "sensor.log").open("xb") as stream:
                stream.write(log)
                stream.flush()
                os.fsync(stream.fileno())
            self._report["raw_log_sha256"] = hashlib.sha256(log).hexdigest()
            if len(log) == 1_000_000:
                raise SensorRejected(
                    "event file reached hard cap; preserve stopped sensor"
                )
            metrics = self._file("acg-metrics.jsonl", 900_000)
            with (self._raw_dir / "metrics.jsonl").open("xb") as stream:
                stream.write(metrics)
                stream.flush()
                os.fsync(stream.fileno())
            self._report["metrics_raw_sha256"] = hashlib.sha256(metrics).hexdigest()
            self._command("remove", ["rm", self._id], timeout=5, limit=128)
            remaining = self._command(
                "absence",
                [
                    "ps",
                    "-a",
                    "--no-trunc",
                    "--filter",
                    "label=acg.window.nonce=" + self._nonce,
                    "--format",
                    "{{.ID}}",
                ],
                limit=128,
            )
            if remaining.strip():
                raise SensorRejected("owned sensor still present")
            self._report["removal_observed"] = True
            self._report["cleanup_verified"] = (
                self._report["launch_confirmed"]
                and not self._report["launch_completion_uncertain"]
            )
        except (Exception, KeyboardInterrupt) as error:
            self._report["faults"].append(
                dict(phase="cleanup", code=type(error).__name__)
            )
        return self.snapshot()

    def snapshot(self):
        return copy.deepcopy(
            dict(
                self._report,
                recovery=dict(
                    name=self._name,
                    nonce=self._nonce,
                    sensor_id=self._id,
                    target_id=self._target,
                    endpoint=self._endpoint,
                    raw_directory=str(self._raw_dir) if self._raw_dir else None,
                ),
            )
        )

    def observe_log(self):
        """Bounded readiness snapshot from the exact owned, running sensor."""
        if not self._report["launch_confirmed"] or self._sealed:
            raise SensorRejected("active owned lease required")
        self._owned(require_running=True)
        return self._file("acg-events.jsonl", 1_000_000)

    def _file(self, name, payload_limit):
        """One fixed regular file, bounded tar bytes; never extract archive paths.

        Tar overhead counts toward the original 1MB pipe budget. A near-cap
        file may therefore refuse export: retain the stopped container, never
        truncate it or increase the pipe limit to force a completed receipt.
        """
        if (name, payload_limit) not in (
            ("acg-events.jsonl", 1_000_000),
            ("acg-metrics.jsonl", 900_000),
        ):
            raise SensorRejected("unreviewed file export")
        archive = self._command(
            "events" if name == "acg-events.jsonl" else "metrics",
            ["cp", self._id + ":/tmp/" + name, "-"],
            limit=1_000_000,
            binary=True,
        )
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as bundle:
            members = bundle.getmembers()
            if (
                len(members) != 1
                or members[0].name != name
                or not members[0].isreg()
                or not 1 <= members[0].size <= payload_limit
            ):
                raise SensorRejected("invalid bounded file archive")
            with bundle.extractfile(members[0]) as source:
                data = source.read(payload_limit + 1)
            if len(data) != members[0].size:
                raise SensorRejected("incomplete file archive")
        return data
