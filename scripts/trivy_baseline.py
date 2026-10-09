"""Run an established scanner independently per supported fixture.

Different fixtures may reuse Terraform resource names; scanning their directory as
one module would incorrectly combine independent experimental cases.
"""

import re
import time
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.evidence import evidence_main
from cloudguard.legacy_io import InputBudget
from cloudguard.limits import json_value
from cloudguard.process_runner import run_bounded, BoundedProcessError


def collect(args):
    budget = InputBudget()
    labels = budget.json(ROOT / "data/labels.json")
    if (
        not isinstance(labels, list)
        or not 1 <= len(labels) <= 256
        or any(
            not isinstance(record, dict)
            or not isinstance(record.get("id"), str)
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,255}", record["id"])
            for record in labels
        )
        or len({record["id"] for record in labels}) != len(labels)
    ):
        raise ValueError("invalid baseline fixture manifest")
    rows = []
    skipped = []
    supported = []
    for record in labels:
        name = record["id"]
        if not (name.endswith(".tf") or name.startswith(("k8s-", "Dockerfile"))):
            skipped.append(name)
            continue
        supported.append(name)
    remaining_output = 8_000_000
    not_attempted = []
    for index, name in enumerate(supported):
        command = [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "-v",
            str(ROOT / "data/development") + ":/fixtures:ro",
            "aquasec/trivy:0.60.0",
            "config",
            "--skip-check-update",
            "--format",
            "json",
            "/fixtures/" + name,
        ]
        start = time.perf_counter()
        try:
            if remaining_output <= 0:
                raise ValueError("legacy batch output budget exceeded")
            completed = run_bounded(
                command,
                timeout=budget.timeout(),
                output_limit=min(2_000_000, remaining_output),
            )
            remaining_output -= len(completed.stdout.encode()) + len(
                completed.stderr.encode()
            )
        except (BoundedProcessError, ValueError, KeyboardInterrupt) as error:
            rows.append(
                dict(
                    case=name,
                    exit_code=None,
                    result=None,
                    stderr=getattr(error, "stderr", b"").decode(
                        "utf-8", errors="replace"
                    ),
                    stdout_prefix=getattr(error, "stdout", b"").decode(
                        "utf-8", errors="replace"
                    ),
                    error_type=type(error).__name__,
                    process_diagnostic=getattr(error, "diagnostic", None),
                    elapsed_s=time.perf_counter() - start,
                )
            )
            not_attempted = supported[index + 1 :]
            break
        try:
            result = json_value(completed.stdout)
        except (ValueError, TypeError):
            result = None
        rows.append(
            dict(
                case=name,
                exit_code=completed.returncode,
                result=result,
                stderr=completed.stderr,
                elapsed_s=time.perf_counter() - start,
            )
        )
    report = dict(
        observed_at=datetime.now(timezone.utc).isoformat(),
        image="aquasec/trivy:0.60.0",
        checks="bundled policies, skip-check-update, network disabled",
        cases=rows,
        excluded=skipped,
        not_attempted=not_attempted,
        limitation="Tool execution baseline only. Rule coverage differs; no cross-tool accuracy/FP reduction claim.",
    )
    errors = [r["case"] for r in rows if r["exit_code"] or r["result"] is None]
    return {"output": report}, int(bool(errors))


def main():
    return evidence_main(collect)


if __name__ == "__main__":
    raise SystemExit(main())
