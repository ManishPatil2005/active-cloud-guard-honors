# Existing Engine 1 pipeline with saved Engine 2 context

Implemented7October2026, E2-042/R4/R5/R6/RQ3. The earlier E2-041 command combined the configuration rule scanner with statistical saved-runtime replay. This opt-in extension executes the existing Engine1 pipeline and preserves its retrieval, model audit, rule priorities, policy interpretation and reviewed TCP evidence alongside the same runtime component.

## Behavior

`integration.replay(..., engine1_pipeline=True, kb=...)` enables the path. The flag is an exact boolean and the knowledge corpus is required. Supplying model/vector/cache/policy/review/budget options without pipeline mode is rejected instead of silently ignored. The CLI forwards these existing Engine1 options to pipeline.run. Its underlying algorithms, default run command, runtime comparator and package/engine versions remain unchanged.

The wrapper first validates inventory/configuration and saved runtime inputs, including source/group/event-overlap/parameter checks. It freezes input bytes and eleven selected implementation files and rechecks both before calling the optional pipeline. Thus malformed runtime and observed pre-pipeline mutations refuse that execution. Pipeline.run then applies its existing input/model/policy/review/probe guards. Final wrapper checks compare configuration/inventory component hashes and repeat the frozen checks before returning. Bounds:1MB per configuration/knowledge/inventory/capture/optional policy/review document,1..20baseline captures,1000rule findings; original window/event/asset limits retained. No whole-workflow hard deadline or hostile filesystem guarantee added.

The complete Engine1 report is retained, including:

- retrieved_sources/retrieval_mode and rag output with original candidate/rejection metadata;
- model_candidate_ids/model_verifications, hash-bound operator context and review boundaries;
- each rule finding's probe, verification and original provisional priority;
- the current pipeline's actual stage timings and policy notes.

Asset contexts retain original configuration finding IDs and runtime window indices. Additional model_verification_indices reference only the pipeline's explicit operator-approved inventory mapping. An unreviewed model asset name, even one resembling an inventory ID, is not automatically mapped or used as a network target. Active verification asset count counts unique assets, not duplicate finding/approval references; existing within-run probe reuse still applies.

Runtime never changes Engine1 priority or validates a candidate. combined_priority remains null, joint_priority_calculated=false, deployment_binding_verified=false and actions_executed=[]. Engine1's priority.runtime_observed stays false because its existing scoring input has no runtime anomaly. Missing windows and insufficient baselines remain explicit. Saved timestamps/declared bindings still do not establish deployment or time equivalence. Real independent evaluation and calibrated score fusion remain open.

## Operational scope

Default integrated-replay remains the no-model/no-probe rule context workflow. **Pipeline mode can invoke existing local services**: explicit --model requests local Ollama; --vector-index requests existing Chroma/Ollama retrieval; mapped network findings and explicitly reviewed candidates use existing literal-loopback TCP probes. --cache-dir can write the existing private local audit cache. Use only approved local inventories/models/operator documents. No cloud account, collector, workload, service/clock change or autonomous response is implemented by this extension.

Errors propagate through the existing redacted CLI handler; no fabricated clean fallback. Final mutation/model/approval failures can happen after a requested local stage has executed, and cannot undo its inference/probe/log/cache effects. The wrapper is not an atomic operation or authority to bypass human review. Reports include file paths, corpus/model/probe/reviewer metadata; keep real private reports in appropriate storage and review before publication.

Selected source hashes: the original five integration/scanner/runtime/verification/cache files plus pipeline/retrieval/llm/grounding/scoring/vector. This selected set is not an authenticated dependency closure; index/cache/model/native/external state retains its original trust and identity limitations. Underlying import/package installation is unchanged.

## Safe fixed demonstration and beginner steps

The new development fixture [redis-auth-only.yaml](../data/integration/redis-auth-only.yaml) contains AUTH002 for compose/redis with no published-port predicate. It is not deployed or added to the original45case accuracy corpus. The fixed runner uses this fixture, the existing synthetic runtime captures, lexical retrieval, model=None and no operator candidate review. It therefore performs **actual local retrieval/scoring and saved replay, with no model or network call**. Real model/probe/review integration is unit-tested with mocks only in this milestone.

1. Open the configured clone in a terminal and activate its Python environment.
2. Run `python scripts/integration_check.py --engine1-pipeline --output output/pipeline-context-new-example.json`, using a new filename.
3. Check that all eight checks pass. The script refuses an old output before input reads; failure/interruption may leave incomplete JSON as previously documented.
4. In result.engine1 inspect retrieved_sources, finding AUTH002, verification=not_applicable and priority.runtime_observed=false. rag=null and active_verification_asset_count=0.
5. In result.engine2 inspect the two constructed runtime windows; in asset_contexts inspect Redis's original finding/two window references and the other assets' missing windows. combined_priority remains null.
6. Run `python -m pytest -q tests/test_integration_pipeline.py` for the regression checks. Network/model paths in these added cases are mocked; reviewer names/approvals are synthetic test objects, not real human decisions.

General CLI form:

```text
python -m cloudguard.cli integrated-replay data/integration/redis-auth-only.yaml data/runtime/observation-synthetic.json --baseline data/runtime/baseline-synthetic.json --inventory testbed/inventory.json --engine1-pipeline --kb knowledge/sources.json
```

Existing optional --model/--vector-index/--cache-dir/--timeout/--max-tokens/--policy/--reviews require pipeline mode. Adding model or using a network-predicate configuration requests the existing corresponding local operations; the fixed example above avoids them by construction.

## Actual verification

Twenty-eight new regression cases exercise real local pipeline retrieval/scoring, preservation of model/rejected/probe/review evidence under mocks, reviewed-only context linkage/within-run probe reuse, stale/rejected approvals/model failure, runtime refusal before pipeline, exact mode/required corpus/options, vector delegation, knowledge/source/component mutation checks, actual CLI and exclusive fixed demonstration. Default rule-mode calculated output equals the historical E2-041 result after excluding only revision-specific source hashes/platform file path; previous reports remain untouched.

Target114passed2.31s console/2.234s XML, [receipt](../output/pipeline-integration-target-windows-tests-20261007.xml). [Windows fixed example](../output/pipeline-integration-synthetic-windows-20261007.json)/[Linux fixed example](../output/pipeline-integration-synthetic-linux-20261007.json) each pass eight checks. Full result objects/input/source/launcher hashes agree after excluding only platform-dependent file path and separately measured Engine1 stage timings. Execution timestamps differ normally; no stored report was rewritten for comparison.

Exact commands from repository root:

```powershell
.venv/Scripts/python.exe -m pytest -q tests/test_integration_pipeline.py tests/test_integration.py tests/test_verification.py tests/test_v2.py --basetemp=tmp/pipeline-integration-target-20261007 -o cache_dir=tmp/pytest-cache-20261007 --junitxml=output/pipeline-integration-target-windows-tests-20261007.xml
.venv/Scripts/python.exe -m pytest -q --basetemp=tmp/pipeline-integration-full-windows-20261007 -o cache_dir=tmp/pytest-cache-20261007 --junitxml=output/pipeline-integration-full-windows-tests-20261007.xml
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python -m pytest -q --basetemp=tmp/pipeline-integration-full-linux-20261007 -o cache_dir=/home/acgresearch/.cache/acg-pytest --junitxml=output/pipeline-integration-full-linux-tests-20261007.xml
.venv/Scripts/python.exe scripts/integration_check.py --engine1-pipeline --output output/pipeline-integration-synthetic-windows-20261007.json
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python scripts/integration_check.py --engine1-pipeline --output output/pipeline-integration-synthetic-linux-20261007.json
.venv/Scripts/python.exe -m ruff check cloudguard scripts tests
.venv/Scripts/python.exe -m ruff format --check cloudguard scripts tests
.venv/Scripts/python.exe -m pip check
wsl -d ACG-Research -u acgresearch --exec /home/acgresearch/acg-venv/bin/python -m pip check
```

Current results/publication in [MEMORY](MEMORY.md)/[WORK_LOG](WORK_LOG.md). This closes the software wiring of the existing Engine1 pipeline to saved statistical runtime context. Actual joint model/probe observations, ML comparator integration, qualified continuous collection, authenticated deployment/time mapping, calibration and independent detection/overhead evaluation remain separate acceptance gates. Supervisor approval still absent; no humans/ground truth/benchmark eligibility fabricated.

Final actual whole suites: [Windows](../output/pipeline-integration-full-windows-tests-20261007.xml)1,268passed/38skipped26.85s console/26.847s XML; [Linux](../output/pipeline-integration-full-linux-tests-20261007.xml)1,306passed111.65s console/108.127s XML,1,306collected each/zero failures/errors. Lint/123fileformat/bothpipchecks pass. No new failing regression/incident this milestone; historical negatives and immutable memory snapshot retained. Publication requires final doc contracts and indexed repository checker/staged review followed by actual remote equality, not inference from local tests.

Final documentation contracts: [18passed](../output/pipeline-integration-docs-tests-20261007.xml),0.30s console/0.110s XML. Exact command `.venv/Scripts/python.exe -m pytest -q tests/test_repository_check.py tests/test_runtime_research_pack.py --basetemp=tmp/pipeline-integration-docs-20261007 -o cache_dir=tmp/pytest-cache-20261007 --junitxml=output/pipeline-integration-docs-tests-20261007.xml`. Preliminary publication563files passed required docs/links/exclusions/bounded credential checks; final index/commit/push verification follows separately.
