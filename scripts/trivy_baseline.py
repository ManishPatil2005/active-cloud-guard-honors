"""Run an established scanner independently per supported fixture.

Different fixtures may reuse Terraform resource names; scanning their directory as
one module would incorrectly combine independent experimental cases.
"""

import json
import subprocess
import time
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]


def main():
    labels = json.loads((ROOT / "data/labels.json").read_text())
    rows = []
    skipped = []
    for record in labels:
        name = record["id"]
        if not (name.endswith(".tf") or name.startswith(("k8s-", "Dockerfile"))):
            skipped.append(name)
            continue
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
        completed = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8", timeout=180
        )
        try:
            result = json.loads(completed.stdout)
        except json.JSONDecodeError:
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
        limitation="Tool execution baseline only. Rule coverage differs; no cross-tool accuracy/FP reduction claim.",
    )
    (ROOT / "output").mkdir(exist_ok=True)
    (ROOT / "output/trivy-baseline.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    errors = [r["case"] for r in rows if r["exit_code"] or r["result"] is None]
    print(
        json.dumps(
            dict(cases=len(rows), excluded=len(skipped), errors=errors), indent=2
        )
    )
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
