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

IMAGE = "falcosecurity/falco@sha256:788f1129c542171813083d4afc61b16730a47dde8c23d9c39370acef996349b6"


def command(*args, timeout=20):
    return subprocess.run(
        ["docker", *args], capture_output=True, text=True, timeout=timeout, check=True
    ).stdout.strip()


def rules(container_id):
    if not re.fullmatch("[a-f0-9]{64}", container_id):
        raise ValueError("full lowercase container ID required")
    return (
        "- rule: ACG Redis selected syscall smoke\n"
        "  desc: Selected successful calls from one lab cgroup, not a threat rule\n"
        "  condition: >\n"
        "    evt.type in (execve, execveat, open, openat, openat2, connect)\n"
        "    and evt.rawres >= 0\n"
        f"    and thread.cgroups contains {container_id}\n"
        "  output: 'acg time=%evt.rawtime type=%evt.type result=%evt.rawres cgroups=%thread.cgroups'\n"
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
    args = parser.parse_args()
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
            raw_dir = ROOT / "output/runtime-raw" / name
            raw_dir.mkdir(parents=True, exist_ok=False)
            rule_path = raw_dir / "rules.yaml"
            rule_text = rules(container_id)
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
            # Being alive is not proof of probe readiness; matching events are required.
            time.sleep(3)
            running = (
                command("inspect", "--format", "{{.State.Running}}", name) == "true"
            )
            report["workload_executed"] = running
            if running:
                report["workload_result"] = command(
                    "exec", container_id, "redis-cli", "-h", "127.0.0.1", "PING"
                )
            command("wait", name, timeout=32)
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
