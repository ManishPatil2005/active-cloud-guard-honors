# Opt-in integration execution cost

E2-044 / E2-004 / V2-004 / R7, 7 October 2026. Implements a measurement prerequisite for efficiency work, not the pending matched overhead/energy/independent evaluation itself.

## Implementation and acceptance

The existing `integration.replay(..., measure_stages=True)` and CLI/fixed runner `--measure-stages` expose `execution_cost`. Default omission does not read these measurement clocks or add that field. Detector calculations, model parameters, component reports, source/input guards and actions stay unchanged. There is no additional engine, dependency, serialized model, profiling service or architecture change.

Protocol `integrated_process_cost_v1` records integer nanoseconds using `perf_counter_ns` for local elapsed time and `process_time_ns` for process CPU. It names each clock's implementation/resolution/monotonic/adjustable metadata; nanosecond units are not a claim of nanosecond accuracy. Negative/non-integer elapsed intervals are rejected, not clipped to zero. A component exception still rejects the operation; no partial successful report is returned.

Non-overlapping stages: `configuration_rule_baseline`, `runtime_statistical`, selected `isolation_forest`/`autoencoder`, and optional `engine1_pipeline`. Only executed stages appear. Total also covers hashing, inventory reads, local module imports, consistency checks and context/report assembly. It begins after option validation and ends before timing metadata assembly/CLI serialization. Pipeline stage includes its own scanner/retrieval/scoring; the prevalidation rule stage is separate work, not a duplicated timing interval. Original Engine1 stage timings remain available, nested within the pipeline measurement; do not sum them with their enclosing stage.

ML measurements include each existing component's parsing, checks, shared statistical calculation, lazy backend imports, fitting and scoring. **They are not fit-only comparisons**: the first selected model may pay shared import/setup cost while the second reuses imported libraries. Process CPU includes threads in this process, not children, model server, collector or system-wide CPU. Threaded CPU can exceed elapsed time; coarse process-clock resolution can report zero for short stages, not cost-free execution.

No power/energy/memory measurement, deadline enforcement, sensor-off/on contrast, cross-clock event alignment or real detection evaluation is added. `sensor_overhead_evaluated`, `energy_measured`, `independent_performance_evaluation` remain false. Existing failed timing/coverage evidence is untouched.

## Beginner reproduction

Activate the existing environment, open the repository root, choose a **fresh** output name, then run:

```powershell
python scripts/integration_check.py --engine1-pipeline --runtime-ml both --measure-stages --output output/my-fresh-cost.json
```

The fixed invented-data example performs local lexical retrieval/scoring and synthetic fits, not Ollama inference/TCP/sensor operations. Open the JSON: ten boolean checks should pass. Under `result.execution_cost`, divide `wall_ns` or `process_cpu_ns` by 1,000,000 for milliseconds. Read `total`, stage names and limitations; do not interpret speed as accuracy or abstention as safety. Existing files are refused. An unavailable optional backend produces a rejected receipt, not fabricated timings or a clean verdict.

Direct command:

```powershell
python -m cloudguard.cli integrated-replay data/integration/redis-auth-only.yaml data/runtime/ml-observation-synthetic.json --baseline data/runtime/ml-baseline-synthetic.json --inventory testbed/inventory.json --engine1-pipeline --kb knowledge/sources.json --runtime-ml both --measure-stages
```

## Actual observations and checks

One fresh fixed example per environment passed ten checks:

| Development observation | Total elapsed | Total process CPU |
|---|---:|---:|
| Windows | 1.249916400 s | 1.234375000 s |
| Linux/WSL | 3.010083762 s | 8.516130197 s |

Receipts: `output/integration-cost-synthetic-{windows,linux}-20261007.json`. Runs occurred while regression suites were active; contention, import order, differing environment clocks and one observation per system prevent fair OS/model speed comparisons. These values demonstrate collection only, not representative latency, optimal model choice, sensor overhead or sustainability savings.

23 new cases validate strict option types, zero measurement reads by default, exact injected intervals and unchanged calculations, rejected invalid clocks, all eight selection/pipeline combinations, component-failure propagation, pipeline evidence preservation, actual CLI/exclusive runner and detached clock metadata. Target102cases/zero failures/skips, XML26.565s: `output/integration-cost-target-windows-20261007.xml`. Final complete suites: Windows1,308passed/38skips/101.52s console (101.481s XML); Linux1,346passed/340.03s (328.120s XML), both1,346collected/zero failures/errors, all final code/launcher included. Receipts: `output/integration-cost-full-{windows,linux}-20261007.xml`. Documentation18pass/0.32s (0.203s XML), `output/integration-cost-docs-20261007.xml`. Both pip checks, Ruff and125-file formatting passed. Both demo receipts' input/source/launcher hashes match current files. Exact commands in WORK_LOG; suite duration is not detector latency. No package install, live collector, service/clock change, independent-human study or real-data fit was performed.

## Next pending work

Use these observations to locate parsing/import/model work before designing an optimization; preserve direct-model evidence equivalence. Real overhead/efficiency claims still need approved context/protocol, qualified comparable captures, matched conditions, sufficient grouped independent data and actual energy measurement if energy is claimed. Supervisor proposal remains DRAFT — NOT APPROVED. This measurement feature does not authorize those experiments.
