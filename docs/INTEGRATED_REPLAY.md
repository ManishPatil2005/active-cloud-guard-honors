# Engine 1 and Engine 2 offline context integration

Implemented 7 October 2026. E2-041 connects R6 evidence-linked prioritization preparation and RQ3 runtime context through a bounded saved-input workflow. This is the first integration step: configuration **rule-baseline** findings and statistical runtime replay appear in one inspectable report. Model-assisted Engine1 auditing, active verification, calibrated fusion and continuously collected runtime integration remain separate work.

## What the command does

`cloudguard/integration.py:replay` takes a configuration file,1..20 separate baseline captures, one observation capture and an explicit inventory. It checks bounded input hashes, runs the existing scanner and runtime comparator, and groups references by exact declared asset IDs. It retains the complete original component reports. Joining never modifies a finding, count, score, runtime status or baseline parameter.

Every inventory asset and every static finding asset is represented. A static asset absent from inventory remains `unmapped_static_asset`. No model-authored aliases or fuzzy name matching are used. Matching an ID is `declared_asset_id_only`; deployment binding remains false. There is no evidence that the configuration was deployed with the supplied capture, that capture time matches configuration time, or that an ID authenticates a host/container.

| Input situation | Result |
|---|---|
| Finding and runtime windows share a declared asset | References to both components, original window statuses/scores retained |
| Static finding but no observed windows | Finding retained; no_observed_window and null runtime_review_required |
| Observation without sufficient baseline | insufficient_baseline; original null scores retained |
| Runtime score below threshold | Original no_threshold_exceedance retained; configuration finding is not suppressed |
| Runtime windows but no static findings | Windows retained with an empty finding-reference list |
| Static asset absent from inventory | Finding retained as unmapped, no fabricated alias/deployment match |
| Inventory asset without findings or observed windows | Explicit empty context; collection silence does not become a normal window |

The report's combined_priority remains null and joint_priority_calculated is false. Statistical deviation is unbounded and uncalibrated; transforming it into the TCI anomaly input would require a defined/calibrated mapping and qualified evidence. Every asset context remains review_required=true because identity, coverage and joint interpretation are unqualified. A per-window comparator review flag can still be false; it only describes that comparator's threshold result.

## Boundaries and consistency checks

Each supplied file is read up to1,000,001bytes and rejected above1,000,000bytes before component work. The scanner's separate existing character/format handling remains unchanged. At most1000configuration findings are accepted by this integration wrapper; runtime retains its existing inventory100assets/capture2000events/baseline20/window1..3600second bounds and source/group/event-overlap guards.

Input role hashes freeze exact original bytes; inventory and capture hashes reported by the runtime component must agree. All input roles and five selected implementation files are checked again before returning. Selected files: integration.py,scanner.py,runtime.py,verification.py,cache.py. This is a selected consistency check, not a complete dependency/native/environment attestation. The scanner's sha256 remains its existing normalized-text hash; configuration_bytes_sha256 is the separate raw-file hash. Caller-supplied paths/filesystem are trusted; equal pre/post hashes do not defeat temporary changes between reads, symlink races, blocking special files, malicious host code or resource exhaustion. No hard wall-clock/CPU/memory or crash-durability guarantee is added.

The library has no collector/model fitting/network/subprocess/service/clock/action path. Existing normalized sensor exports can be replayed under their original declared-source restrictions; they gain no benchmark eligibility from this wrapper. Reports retain selected paths/IDs/timestamps from components and may reveal scenario information. Keep real private captures and results in approved private storage and review before publishing. Output binding/independent evaluation/real-data authority/sensor connection/calibration/threat flags remain false; actions_executed is empty. The existing `run`, `scan`, `runtime-replay`, models and historical baseline remain intact.

## Reproduce the combined workflow

Use the existing configured clone and Python environment at the repository root. No Docker or Ollama service is needed for these commands.

```text
python -m cloudguard.cli integrated-replay data/development/redis-all.yaml data/runtime/observation-synthetic.json --baseline data/runtime/baseline-synthetic.json --inventory testbed/inventory.json
python scripts/integration_check.py --output output/integration-new-example.json
python -m pytest -q tests/test_integration.py
```

The first command prints a report; callers saving stdout are responsible for choosing a fresh destination. The fixed demonstration script requires an exclusive new output file, refusing an existing one **before input reads**. It has no arbitrary input/model arguments. On rejection it saves only error_type/empty actions; write interruption may leave incomplete JSON. No fsync/atomic report-publication guarantee. Its selected launcher hash is retained on success and rechecked; it is not a signed receipt.

Beginner steps:

1. Read [Progress Execution](<Progress Execution.md>) and activate the already configured Python environment.
2. Run the first command above. Locate engine1.findings: the fixed fixture contains one NET001 configuration finding for compose/redis.
3. Locate engine2.windows: the two synthetic windows retain no_threshold_exceedance and deviation_for_review, with the latter constructed score8.0.
4. Locate asset_contexts: Redis references its one finding/two windows. PostgreSQL,Nginx,MinIO have no observed windows in this fixture; their runtime state stays unknown.
5. Confirm combined_priority is null, deployment_binding_verified=false and actions_executed=[]. The displayed context aids review; it does not establish an attack or actual deployed configuration.
6. To keep a generated example, use a new filename with the fixed script. It refuses old output instead of replacing previous evidence.

The fixture timestamps/IDs are invented development coordinates. No independent labels, real detector benchmark, calibrated threshold or matched overhead experiment is created by these demonstrations.

## Observed execution and tests

Pending scanner milestone was completed first: commit a555b32d7d58d43b158e5793feb8f0dda92a961b verified equal to GitHub main, clean worktree afterward. Earlier automatic approval usage-limit failure had prevented that command from executing; no approval bypass/package/permission configuration change was used to resume.

Thirty-four new regression cases cover exact component equality, finding retention, missing/insufficient/below-threshold runtime, unmapped/no-static assets, false authority/no observed external operations, inherited schema/source/identity/group/overlap/parameter guards, finding/input limits, input/source/component hash changes, sensor declaration limits, real CLI/redacted error and exclusive fixed-demo output. Target scanner/runtime/integration149pass/1local-loopbacktestdeselected,2.04s console/1.897s XML. The full suites include that deselected test. Collect-only34cases emitted one harmless default pytest-cache permission warning because its cache override was omitted; actual test runs use the designated cache directory.

Fixed examples: [Windows](../output/integration-synthetic-windows-20261007.json) and [Linux](../output/integration-synthetic-linux-20261007.json), all six checks pass. Full result objects match after excluding only the platform-dependent engine1.file path; selected source/input/launcher hashes match. Actual executions differ in executed_at as expected. No successful old report was rewritten and no failed evidence was removed.

Exact executed commands:

```powershell
.venv/Scripts/python.exe -m pytest -q tests/test_integration.py tests/test_runtime.py tests/test_core.py -k 'not probe_local_live' --basetemp=tmp/integration-target-20261007 -o cache_dir=tmp/pytest-cache-20261007 --junitxml=output/integration-target-windows-tests-20261007.xml
.venv/Scripts/python.exe -m pytest -q --basetemp=tmp/integration-full-windows-20261007 -o cache_dir=tmp/pytest-cache-20261007 --junitxml=output/integration-full-windows-tests-20261007.xml
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python -m pytest -q --basetemp=tmp/integration-full-linux-20261007 -o cache_dir=/home/acgresearch/.cache/acg-pytest --junitxml=output/integration-full-linux-tests-20261007.xml
.venv/Scripts/python.exe scripts/integration_check.py --output output/integration-synthetic-windows-20261007.json
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python scripts/integration_check.py --output output/integration-synthetic-linux-20261007.json
.venv/Scripts/python.exe -m ruff check cloudguard scripts tests
.venv/Scripts/python.exe -m ruff format --check cloudguard scripts tests
.venv/Scripts/python.exe -m pip check
wsl -d ACG-Research -u acgresearch --exec /home/acgresearch/acg-venv/bin/python -m pip check
```

Final whole-suite and publication outcomes are recorded after completion in [WORK_LOG](WORK_LOG.md)/[current MEMORY](MEMORY.md). Tests demonstrate implemented software behavior; the current research gates remain genuine supervisor decisions, qualified timing/coverage/context, independent labels and calibrated held-out evaluation. Full RAG/probe/ML/TCI/live integration needs separate acceptance; this milestone supplies the bounded offline rule/statistical-context step.

Final whole suites observed: [Windows](../output/integration-full-windows-tests-20261007.xml)1,240passed/38skipped,29.03s console/29.021s XML; [Linux](../output/integration-full-linux-tests-20261007.xml)1,278passed,104.13s console/100.897s XML. Both1,278collected,zero failures/errors. Ruff lint/122fileformat/bothpipchecks pass. Local regression receipts are not GitHub-hosted CI or independent security effectiveness measurements.

After documentation edits, [18 documentation/publication contract cases](../output/integration-docs-tests-20261007.xml) passed0.26s console/0.119s XML. Command: `.venv/Scripts/python.exe -m pytest -q tests/test_repository_check.py tests/test_runtime_research_pack.py --basetemp=tmp/integration-docs-20261007 -o cache_dir=tmp/pytest-cache-20261007 --junitxml=output/integration-docs-tests-20261007.xml`. Preliminary repository publication checker551files passed; final indexed review/hook and remote commit verification are separate steps, reported after actual execution.
