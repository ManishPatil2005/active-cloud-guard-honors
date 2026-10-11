"""Bounded Redis callback for full-window qualification; no sensor launcher."""

import copy
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.correlation import parse_ping
from cloudguard.limits import json_value
from cloudguard.process_runner import BoundedProcessError, ProcessResult, run_bounded

IDENTITY_FORMAT = (
    '{"id":{{json .Id}},"image":{{json .Image}},"started_at":{{json .State.StartedAt}},'
    '"running":{{json .State.Running}},"restarts":{{json .RestartCount}},'
    '"project":{{json (index .Config.Labels "com.docker.compose.project")}},'
    '"service":{{json (index .Config.Labels "com.docker.compose.service")}}}'
)
PING_SCRIPT = 'printf "%s\\n" "$$"; exec redis-cli -h 127.0.0.1 PING'


class TransportRejected(RuntimeError):
    pass


class RedisWindowTransport:
    """Trusted local daemon/client; snapshots are not deployment attestation."""

    def __init__(self, container_id, endpoint, *, runner=run_bounded):
        if type(container_id) is not str or not re.fullmatch(
            "[a-f0-9]{64}", container_id
        ):
            raise ValueError("full lowercase container ID required")
        if (
            type(endpoint) is not str
            or len(endpoint) > 512
            or not re.fullmatch(r"unix:///[A-Za-z0-9_./-]+", endpoint)
            or any(part in ("", ".", "..") for part in endpoint[8:].split("/"))
        ):
            raise ValueError("explicit local Unix socket required")
        if not callable(runner):
            raise ValueError("bounded runner required")
        self._id = container_id
        self._endpoint = endpoint
        self._runner = runner
        self._before = None
        self._after = None
        self._attempts = []
        self._fault = None

    def _reject(self, code, **fields):
        self._fault = dict(code=code, **fields)
        raise TransportRejected("Redis window transport rejected: " + code)

    def _command(self, args, *, timeout, limit):
        if self._fault is not None:
            raise TransportRejected("Redis window transport remains rejected")
        # Avoid context/host overrides, including changes between calls.
        if os.environ.get("DOCKER_CONTEXT") or os.environ.get("DOCKER_HOST"):
            self._reject("docker_environment_override")
        try:
            result = self._runner(
                ["docker", "--host", self._endpoint, *args],
                timeout=timeout,
                output_limit=limit,
            )
        except BoundedProcessError as error:
            self._reject(
                "client_" + error.code,
                direct_child_reaped=error.diagnostic["direct_child_reaped"],
                pipes_closed=error.diagnostic["pipes_closed"],
                external_job_completion_verified=False,
            )
        except Exception:
            self._reject("client_failed")
        if (
            type(result) is not ProcessResult
            or type(result.returncode) is not int
            or type(result.stdout) is not str
            or type(result.stderr) is not str
            or len(result.stdout) + len(result.stderr) > limit
        ):
            self._reject("invalid_client_result")
        try:
            encoded_length = len(result.stdout.encode("utf-8")) + len(
                result.stderr.encode("utf-8")
            )
        except UnicodeError:
            self._reject("invalid_client_result")
        if encoded_length > limit:
            self._reject("invalid_client_result")
        if result.returncode != 0 or result.stderr:
            self._reject("client_nonzero_or_stderr")
        return result.stdout

    def check_identity(self):
        raw = self._command(
            ["inspect", "--format", IDENTITY_FORMAT, self._id], timeout=5, limit=4096
        )
        try:
            identity = json_value(raw)
            valid = (
                isinstance(identity, dict)
                and set(identity)
                == {
                    "id",
                    "image",
                    "started_at",
                    "running",
                    "restarts",
                    "project",
                    "service",
                }
                and identity["id"] == self._id
                and identity["running"] is True
                and identity["project"] == "honors-cloud-guard"
                and identity["service"] == "redis"
                and type(identity["image"]) is str
                and re.fullmatch(r"sha256:[a-f0-9]{64}", identity["image"])
                and type(identity["started_at"]) is str
                and 1 <= len(identity["started_at"]) <= 64
                and type(identity["restarts"]) is int
                and identity["restarts"] >= 0
            )
        except Exception:
            valid = False
        if not valid:
            self._reject("invalid_target_identity")
        if self._before is None:
            self._before = identity
        else:
            self._after = identity
            if identity != self._before:
                self._reject("target_identity_changed")
        return copy.deepcopy(identity)

    def ping(self):
        if self._fault is not None:
            raise TransportRejected("Redis window transport remains rejected")
        if self._before is None:
            self._reject("identity_check_required")
        if len(self._attempts) >= 60:
            self._reject("ping_budget_exhausted")
        attempt = dict(index=len(self._attempts), status="attempted", pid=None)
        self._attempts.append(attempt)
        try:
            reply = self._command(
                ["exec", self._id, "/bin/sh", "-c", PING_SCRIPT], timeout=0.5, limit=128
            )
            try:
                pid = parse_ping(reply)
            except Exception:
                self._reject("invalid_pid_pong")
            if pid in {row["pid"] for row in self._attempts[:-1]}:
                self._reject("duplicate_pid")
            attempt.update(status="completed", pid=pid)
            return "PONG"
        except TransportRejected:
            attempt["status"] = "rejected"
            raise

    def snapshot(self):
        return copy.deepcopy(
            dict(
                protocol="redis_window_transport_v1",
                before=self._before,
                after=self._after,
                attempts=self._attempts,
                fault=self._fault,
                remote_exec_completion_verified=False,
                collector_coverage="not_verified",
                independent_evaluation_verified=False,
            )
        )
