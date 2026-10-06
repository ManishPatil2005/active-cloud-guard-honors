# Synthetic offline intake example

All captures, reviewer IDs, votes and adjudication in this directory are
software fixtures. No human reviewer, real capture, benchmark or independent
evaluation is represented. Receipt references are intentionally absent.

From the repository root, with the existing Python environment:

```powershell
.venv/Scripts/python.exe scripts/runtime_intake.py --manifest data/runtime/intake-example/manifest.json --output output/my-fresh-intake-report.json
```

The output must not already exist and must be outside this dedicated bundle.
Expected: three observed windows, one known agreement, one known disagreement,
one unknown pair; all research-eligibility/model-fitting flags false and no
actions. The reasons stay in the original label files, not in the report.
This command does not start Docker, collect telemetry, contact a model or
train anything. See [the contract](../../../docs/RUNTIME_INTAKE.md).
