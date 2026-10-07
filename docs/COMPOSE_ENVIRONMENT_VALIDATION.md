# Compose environment-list validation

QA-002 / M3-004, 7 October 2026. This refinement improves the existing Engine 1 configuration parser. Engine 2 and the research evaluation gates retain their current scope.

## Problem and acceptance

The scanner converted Compose environment lists directly to a dictionary. Repeated names silently discarded earlier values, including conflicting `POSTGRES_HOST_AUTH_METHOD` settings and a literal synthetic password followed by a bare variable name. Some malformed entries raised incidental TypeError exceptions; empty names were accepted. This conflicted with the scanner's existing refusal of ambiguous duplicate YAML keys.

Accept only string list entries with nonempty names and reject repeated names before returning a scan report. Bare names, empty values and values containing additional equals signs retain their existing interpretation. Mapping-form input remains unchanged. Errors must omit supplied names/values. `scan` and `run` CLI paths must exit2 with no report or clean verdict; the pipeline must stop before retrieval/model/probe calls.

## Implementation and compatibility

`cloudguard/scanner.py` splits each string at the first equals sign, checks the name against the accumulated mapping, and then records it. Both conflicting and identical duplicates are refused; comparison remains case-sensitive and names are not trimmed or resolved from the host environment. Bare names become None as before. Generic ValueError messages expose no supplied content.

This is a deliberately conservative scanner input contract. It does not assert that Docker Compose rejects every such input or reproduce Docker's interpolation/merge/runtime semantics. Users must remove duplicate declarations or provide a reviewed resolved configuration. The nine rule predicates, finding schema, existing mapping behavior and historical baseline tag remain intact; current parser behavior becomes stricter for the affected lists.

Fifteen new cases cover five duplicate patterns, seven malformed entries, valid list/mapping rule-and-location equivalence with embedded equals signs, and both CLI paths refusing ambiguous input without downstream work. Initial12fail/1pass reproduction is preserved. The first implementation accidentally reused the outer service-name variable; the valid-input equivalence test caught changed finding locations. That failure is retained and the correction uses the distinct environment_name variable. See INC-061/062 and WL-069.

## Execution record

Commands from the repository root; fresh output names required for future runs:

```powershell
.venv/Scripts/python.exe -m pytest -q tests/test_core.py -k 'compose_environment_list' --basetemp=tmp/compose-env-negative-20261007 -o cache_dir=tmp/pytest-cache-20261007 --junitxml=output/compose-env-negative-20261007.xml
.venv/Scripts/python.exe -m pytest -q --basetemp=tmp/compose-env-windows-20261007 -o cache_dir=tmp/pytest-cache-20261007 --junitxml=output/compose-env-windows-tests-20261007.xml
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python -m pytest -q --basetemp=tmp/compose-env-linux-20261007 -o cache_dir=/home/acgresearch/.cache/acg-pytest --junitxml=output/compose-env-linux-tests-20261007.xml
```

Initial reproduction: [12 failed, 1 passed, 70 deselected](../output/compose-env-negative-20261007.xml), 0.83s console. SHA-256 `e1fd1e057affc7f3089e383161441be61a1b0d38ee156624088b7ad7ff83fb33`. First Windows full suite: [1 failed, 1,205 passed, 38 skipped](../output/compose-env-windows-tests-20261007.xml), 22.76s console. The failing equivalence assertion identified the service-name regression; it must pass without weakening its expected location.

First Linux full suite: [1 failed, 1,243 passed](../output/compose-env-linux-tests-20261007.xml), 89.11s console / 86.203s XML; same location regression. Negative SHA-256: Windows `1b73368b9ec486cefec200374ce89d1491f595bc41f5260f76b0c0b4b4452683`, Linux `bd029ab4c8214ad8d656e0f10beeb5544431e9f849eb995421eabbbb3a70d217`. Original reproduction XML time0.572s; first Windows XML time22.756s. These files retain their original bytes.

After correction: [15 targeted cases passed](../output/compose-env-target-fixed-20261007.xml),70deselected,0.44s console/0.189s XML. [Final Windows full suite](../output/compose-env-final-windows-tests-20261007.xml):1,206passed/38skipped,22.28s console/22.280s XML. [Final Linux full suite](../output/compose-env-final-linux-tests-20261007.xml):1,244passed,109.00s console. Both1,244collected,zero failures/errors. Windows skips retain their existing Linux-only/symlink-privilege reasons. Suite duration is not detector latency or clock qualification.

```powershell
.venv/Scripts/python.exe -m pytest -q tests/test_core.py -k 'compose_environment_list or ambiguous_environment_cli' --basetemp=tmp/compose-env-target-fixed-20261007 -o cache_dir=tmp/pytest-cache-20261007 --junitxml=output/compose-env-target-fixed-20261007.xml
.venv/Scripts/python.exe -m pytest -q --basetemp=tmp/compose-env-final-windows-20261007 -o cache_dir=tmp/pytest-cache-20261007 --junitxml=output/compose-env-final-windows-tests-20261007.xml
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python -m pytest -q --basetemp=tmp/compose-env-final-linux-20261007 -o cache_dir=/home/acgresearch/.cache/acg-pytest --junitxml=output/compose-env-final-linux-tests-20261007.xml
.venv/Scripts/python.exe -m ruff check cloudguard scripts tests
.venv/Scripts/python.exe -m ruff format --check cloudguard scripts tests
.venv/Scripts/python.exe -m pip check
wsl -d ACG-Research -u acgresearch --exec /home/acgresearch/acg-venv/bin/python -m pip check
```

Ruff lint and119fileformat passed after correction; both dependency checks passed during this change and no packages changed. Full-suite commands used normal host access required by existing inert process/loopback tests; no restricted retry was needed this turn. Actual suite fitting remains synthetic software validation.

This software change does not establish detector accuracy, complete schema validation, independent evaluation or a solution to the historical intermittent backend import. No live collection, cloud scan, service/clock intervention or package installation is part of this step. Real supervisor approval, qualified captures/context and independent labels remain necessary for the research study.

## Beginner use

Final Linux XML duration105.113s. Documentation contracts: [18 passed](../output/compose-env-docs-tests-20261007.xml),0.20s console, command `.venv/Scripts/python.exe -m pytest -q tests/test_repository_check.py tests/test_runtime_research_pack.py --basetemp=tmp/compose-env-docs-20261007 -o cache_dir=tmp/pytest-cache-20261007 --junitxml=output/compose-env-docs-tests-20261007.xml`. Publication requires `python scripts/repository_check.py` against the staged content; this bounded checker does not certify research claims. Git commit/push status is verified separately after execution.

Use the configured Python environment at the repository root. `python -m cloudguard.cli scan <configuration.yaml>` scans a local file. If an environment-list name appears twice, consolidate it to one intended declaration and review the configuration before scanning again. For the developer checks, run `python -m pytest -q tests/test_core.py -k 'compose_environment_list or ambiguous_environment_cli'`. The added cases use temporary synthetic configurations; they need no running Docker or model service. Read [Progress Execution](<Progress Execution.md>) for the broader setup and result interpretation.
