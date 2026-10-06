# Synthetic offline intake example

All captures, reviewer IDs, votes and adjudication in this directory are
software fixtures. No human reviewer, real capture, benchmark or independent
evaluation is represented. Original manifest.json has no receipt references.
manifest-typed-counted.json is the current opt-in v2 example with invented
receipt sources/wrappers. Existing v1 manifest/capture/guideline/label bytes
unchanged. Earlier manifest-typed.json and uncounted sources are preserved
negative fixtures: the strengthened checker now rejects their missing trial
count fields. Do not use that earlier manifest as a passing example.

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

To try the typed example, choose another fresh output file:

```powershell
.venv/Scripts/python.exe scripts/runtime_intake.py --manifest data/runtime/intake-example/manifest-typed-counted.json --output output/my-fresh-typed-intake-report.json
```

Expect selected adapter-count, identity-snapshot and local-clock consistency,
not authenticated identity, complete coverage, collector alignment or eligible
data. No reviews are included in this second manifest. The synthetic capture
events are not bound to the practice measurement interval: this demonstrates
that endpoint arithmetic alone cannot establish collector alignment. No raw
export was collected/validated. All evaluation/fitting/action gates stay false.
