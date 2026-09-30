"""One bounded Redis cgroup smoke trial; no anomaly or completeness claim."""

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.deployment import local_daemon
from cloudguard.workload import PROFILES, run as run_workload
from cloudguard.correlation import parse_ping, correlate

IMAGE = "falcosecurity/falco@sha256:788f1129c542171813083d4afc61b16730a47dde8c23d9c39370acef996349b6"


def target_identity(container_id):
    """Select only non-secret fields; trust the local daemon, not attestation."""
    fields = json.loads(
        command(
            "inspect",
            "--format",
            '{"id":{{json .Id}},"image":{{json .Image}},"started_at":{{json .State.StartedAt}},'
            '"running":{{json .State.Running}},"restarts":{{json .RestartCount}},'
            '"project":{{json (index .Config.Labels "com.docker.compose.project")}},'
            '"service":{{json (index .Config.Labels "com.docker.compose.service")}}}',
            container_id,
        )
    )
    if (
        fields.get("id") != container_id
        or fields.get("running") is not True
        or fields.get("project") != "honors-cloud-guard"
        or fields.get("service") != "redis"
        or not isinstance(fields.get("image"), str)
        or not fields["image"].startswith("sha256:")
        or not fields.get("started_at")
        or type(fields.get("restarts")) is not int
    ):
        raise ValueError("running lab identity required")
    return fields


def await_canary(name, container_id, *, fixed_two=False, ping=None):
    """Bounded fixed PING attempts; observed matching events, not mere liveness."""
    for attempt in range(1, 3 if fixed_two else 4):
        if command("inspect", "--format", "{{.State.Running}}", name) != "true":
            raise ValueError("sensor stopped before readiness")
        pong = (
            ping()
            if ping is not None
            else command("exec", container_id, "redis-cli", "-h", "127.0.0.1", "PING")
        )
        if fixed_two and pong != "PONG":
            raise ValueError("fixed warmup PING failed")
        time.sleep(1)
        counts = summarize_events(command("logs", name), container_id)
        if (
            pong == "PONG"
            and (not fixed_two or attempt == 2)
            and counts.get("execve", 0) + counts.get("execveat", 0) > 0
            and counts.get("connect", 0) > 0
        ):
            return dict(
                status="matching_events_observed",
                canary_attempts=attempt,
                causal_attribution="not_proven",
                canary_included_in_capture=True,
            )
    raise ValueError("matching readiness events not observed")


def command(*args, timeout=20):
    return subprocess.run(
        ["docker", *args], capture_output=True, text=True, timeout=timeout, check=True
    ).stdout.strip()


def identified_ping(container_id, ids):
    reply = command(
        "exec",
        container_id,
        "/bin/sh",
        "-c",
        'printf "%s\\n" "$$"; exec redis-cli -h 127.0.0.1 PING',
    )
    ids.append(parse_ping(reply))
    return "PONG"


def rules(container_id, *, correlation=False):
    if not re.fullmatch("[a-f0-9]{64}", container_id):
        raise ValueError("full lowercase container ID required")
    return (
        "- rule: ACG Redis selected syscall smoke\n"
        "  desc: Selected successful calls from one lab cgroup, not a threat rule\n"
        "  condition: >\n"
        "    evt.type in (execve, execveat, open, openat, openat2, connect)\n"
        "    and evt.rawres >= 0\n"
        f"    and thread.cgroups contains {container_id}\n"
        "  output: 'acg time=%evt.rawtime type=%evt.type result=%evt.rawres cgroups=%thread.cgroups"
        + (" vpid=%proc.vpid" if correlation else "")
        + "'\n"
        "  priority: INFORMATIONAL\n"
        "  source: syscall\n"
    )


def summarize_events(stdout, container_id):
    counts = Counter()
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if (
            not isinstance(event, dict)
            or event.get("rule") != "ACG Redis selected syscall smoke"
        ):
            continue
        fields = event.get("output_fields", {})
        kind = fields.get("evt.type")
        result = fields.get("evt.rawres")
        if (
            kind not in {"execve", "execveat", "open", "openat", "openat2", "connect"}
            or type(result) is not int
            or result < 0
            or not re.search(
                r"(?<![a-f0-9])" + container_id + r"(?![a-f0-9])",
                fields.get("thread.cgroups", ""),
            )
        ):
            raise ValueError("unexpected sensor event scope or result")
        counts[kind] += 1
    return dict(counts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument("--profile", choices=tuple(PROFILES), default="ping_1")
    parser.add_argument("--fixed-warmup", action="store_true")
    parser.add_argument("--correlate", action="store_true")
    args = parser.parse_args()
    if args.correlate and (args.profile != "ping_4" or not args.fixed_warmup):
        parser.error("correlation requires ping_4 and fixed warmup")
    report = dict(
        executed_at=datetime.now(timezone.utc).isoformat(),
        image=IMAGE,
        evidence_level="sensor_smoke_attempt",
        duration_seconds=15,
        threat_confirmed=False,
        coverage="unknown",
        actions_executed=[],
    )
    with Path(args.output).open("x", encoding="utf-8") as destination:
        name = "acg-falco-" + uuid.uuid4().hex
        started = False
        try:
            local_daemon()
            ids = command(
                "ps",
                "--no-trunc",
                "-q",
                "--filter",
                "label=com.docker.compose.project=honors-cloud-guard",
                "--filter",
                "label=com.docker.compose.service=redis",
            ).splitlines()
            if len(ids) != 1:
                raise ValueError("one running lab Redis required")
            container_id = ids[0]
            report["target_identity_before"] = target_identity(container_id)
            raw_dir = ROOT / "output/runtime-raw" / name
            raw_dir.mkdir(parents=True, exist_ok=False)
            rule_path = raw_dir / "rules.yaml"
            rule_text = rules(container_id, correlation=args.correlate)
            rule_path.write_text(rule_text, encoding="utf-8", newline="\n")
            report.update(
                container_id=container_id,
                rules_sha256=hashlib.sha256(rule_text.encode()).hexdigest(),
                config_sha256=hashlib.sha256(
                    (ROOT / "testbed/falco-trial.yaml").read_bytes()
                ).hexdigest(),
                deployment_binding_authenticated=False,
            )
            # No socket or host /etc access. Filters minimize output, not kernel visibility.
            # Attempt cleanup even if the client times out after daemon-side creation.
            started = True
            sensor_id = command(
                "run",
                "-d",
                "--name",
                name,
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
                "--mount",
                "type=bind,src=/proc,dst=/host/proc,readonly",
                "--mount",
                "type=bind,src=/sys/kernel/tracing,dst=/sys/kernel/tracing,readonly",
                "--mount",
                f"type=bind,src={rule_path},dst=/acg/rules.yaml,readonly",
                "--mount",
                f"type=bind,src={ROOT / 'testbed/falco-trial.yaml'},dst=/acg/config.yaml,readonly",
                "--entrypoint",
                "/usr/bin/timeout",
                IMAGE,
                "-s",
                "TERM",
                "-k",
                "3",
                "25",
                "/usr/bin/falco",
                "-c",
                "/acg/config.yaml",
                "-M",
                "15",
                "-r",
                "/acg/rules.yaml",
                "-U",
            )
            if not re.fullmatch("[a-f0-9]{64}", sensor_id):
                raise ValueError("unexpected sensor ID")
            report["sensor_container_id"] = sensor_id
            time.sleep(1)
            warmup_pids = []
            if args.correlate:
                report["diagnostic_protocol"] = "container_pid_connect_v2"
                report["warmup_process_ids"] = warmup_pids
            report["readiness"] = await_canary(
                name,
                container_id,
                fixed_two=args.fixed_warmup,
                ping=(lambda: identified_ping(container_id, warmup_pids))
                if args.correlate
                else None,
            )
            report["warmup_protocol"] = (
                "two_pings_v1" if args.fixed_warmup else "adaptive_v1"
            )
            # Guard interval separates dispatches, not proven causal event ownership.
            time.sleep(1)
            report["workload_executed"] = True
            pids = []

            def ping():
                if not args.correlate:
                    return command(
                        "exec", container_id, "redis-cli", "-h", "127.0.0.1", "PING"
                    )
                identified_ping(container_id, pids)
                report["correlation_process_ids"] = list(pids)
                return "PONG"

            report["measurement"] = run_workload(
                args.profile,
                ping,
            )
            if report["measurement"]["status"] != "completed":
                raise ValueError("measured workload failed or timing outside tolerance")
            report["workload_result"] = "PONG"
            command("wait", name, timeout=32)
            report["target_identity_after"] = target_identity(container_id)
            report["target_identity_stable"] = (
                report["target_identity_before"] == report["target_identity_after"]
            )
            if not report["target_identity_stable"]:
                raise ValueError("target changed during collection")
            # Copy only the fixed sensor metrics file to this unique local raw dir.
            command(
                "cp", name + ":/tmp/acg-metrics.jsonl", str(raw_dir / "metrics.jsonl")
            )
            report["metrics_raw_sha256"] = hashlib.sha256(
                (raw_dir / "metrics.jsonl").read_bytes()
            ).hexdigest()
            log_result = subprocess.run(
                ["docker", "logs", name], capture_output=True, timeout=10, check=True
            )
            raw = log_result.stdout + log_result.stderr
            (raw_dir / "sensor.log").write_bytes(raw)
            report["raw_log_sha256"] = hashlib.sha256(raw).hexdigest()
            report["exit_code"] = int(
                command("inspect", "--format", "{{.State.ExitCode}}", name)
            )
            counts = summarize_events(
                log_result.stdout.decode("utf-8", errors="strict"), container_id
            )
            report["event_type_counts"] = counts
            report["matched_event_count"] = sum(counts.values())
            report["status"] = (
                "sensor_failed"
                if report["exit_code"] != 0
                else "events_observed"
                if counts
                else "no_matching_events"
            )
            if args.correlate:
                report["correlation"] = correlate(
                    raw,
                    container_id,
                    pids,
                    report["measurement"]["calls"],
                    warmup_pids=warmup_pids,
                )
            report["raw_log_local_only"] = True
        except Exception as error:
            report["status"] = "trial_failed"
            report["error_type"] = type(error).__name__
            raise
        finally:
            if started:
                if "raw_log_sha256" not in report:
                    try:
                        failure_log = subprocess.run(
                            ["docker", "logs", name],
                            capture_output=True,
                            timeout=10,
                            check=True,
                        )
                        raw = failure_log.stdout + failure_log.stderr
                        (raw_dir / "sensor.log").write_bytes(raw)
                        report["raw_log_sha256"] = hashlib.sha256(raw).hexdigest()
                    except Exception:
                        report["raw_log_unavailable"] = True
                # Only this trial's unique container is stopped/removed, never the lab.
                try:
                    command("stop", "--time", "3", name)
                    command("rm", name)
                    report["sensor_removed"] = True
                except Exception:
                    report["sensor_removed"] = False
            json.dump(report, destination, indent=2)
            destination.write("\n")
    print(json.dumps(report))
    if report["status"] != "events_observed" or not report.get("sensor_removed"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
