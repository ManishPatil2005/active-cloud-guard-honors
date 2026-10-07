# Software refinement audit — 7 October 2026

## Outcome and scope

QA-001 / V2-002, WL-068: review current capability/evidence, inspect selected Engine 1 cache/scanner/probe/scoring and Engine 2 accounting code, and execute the whole existing regression suite on both supported development environments. This is not an exhaustive line-by-line security audit, formal verification, independent detection benchmark or production release review. Preserve Python, Docker Compose, Ollama, Chroma and both engines.

The actual research gate remains supervisor approval and qualified comparable data/context/independent human labels. The [supervisor proposal](ENGINE2_SUPERVISOR_REVIEW_PROPOSAL.md) remains **DRAFT — NOT APPROVED**. No sensor workload, model smoke, Docker operation, cloud scan, service/clock intervention or new research collection was performed. Existing synthetic model tests do perform synthetic fitting; this is software evidence, not real-data evaluation.

## Concrete defect and refinement

`AuditCache.put` formerly evicted files before validating the requested key or publishing its replacement. Three new tests failed before the fix: an invalid key removed the existing entry; replacing a key at capacity removed another valid entry; an injected replacement failure destroyed the old entry. Cause confidence is high from direct control-flow inspection and these reproductions, not a speculative native import diagnosis.

The fix resolves/validates the key first, excludes its destination from eviction candidates, and evicts only after successful atomic replacement. Invalid-key and failed-replacement calls retain previous bytes; successful replacement keeps unrelated entries when no capacity reduction is needed. Existing bounds, TTL, response schema/grounding checks, fresh probes and no cached verification authority remain unchanged. The historical engine1-v2.2 baseline/tag is untouched; current working code has this narrow maintenance fix, not a new engine or detector version.

Limitations: trusted single-user sequential cache, not transactional shared storage. Publication briefly precedes eviction. An eviction error can leave excess entries/new published content and propagate the existing write warning; no crash/power-loss durability, hostile-filesystem or concurrency guarantee added. No cache performance/energy improvement was measured.

## Execution ledger

Run from `D:\research f1`, using fresh output/temp names; future runs must choose other names.

```powershell
.venv/Scripts/python.exe -m pytest -q tests/test_v2.py -k 'invalid_write or replacement_preserves or failed_replacement' --basetemp=tmp/cache-negative-20261007 -o cache_dir=tmp/pytest-cache-20261007 --junitxml=output/cache-refinement-negative-20261007.xml
.venv/Scripts/python.exe -m pytest -q --basetemp=tmp/cache-audit-windows-20261007 -o cache_dir=tmp/pytest-cache-20261007 --junitxml=output/cache-audit-windows-tests-20261007.xml
.venv/Scripts/python.exe -m pytest -q --basetemp=tmp/cache-audit-host-windows-20261007 -o cache_dir=tmp/pytest-cache-20261007 --junitxml=output/cache-audit-host-windows-tests-20261007.xml
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python -m pytest -q --basetemp=tmp/cache-audit-host-linux-20261007 -o cache_dir=/home/acgresearch/.cache/acg-pytest --junitxml=output/cache-audit-host-linux-tests-20261007.xml
.venv/Scripts/python.exe -m ruff check cloudguard scripts tests
.venv/Scripts/python.exe -m ruff format --check cloudguard scripts tests
.venv/Scripts/python.exe -m pip check
wsl -d ACG-Research -u acgresearch --exec /home/acgresearch/acg-venv/bin/python -m pip check
.venv/Scripts/python.exe scripts/repository_check.py
```

| Run | Observed result |
|---|---|
| Before-fix three regression cases | [3 failed](../output/cache-refinement-negative-20261007.xml), 19 deselected, 0.94 s console / 0.684 s XML; intentional defect reproduction retained |
| Restricted Windows full suite | [161 failed, 1,030 passed, 38 skipped](../output/cache-audit-windows-tests-20261007.xml), 30.03 s / 29.929 s XML; permission/path resolution, inert child and loopback failures observed |
| Normal-host Windows full suite | [1,191 passed, 38 skipped](../output/cache-audit-host-windows-tests-20261007.xml), 22.66 s / 22.659 s XML, 1,229 collected, zero failures/errors |
| Normal-host Linux full suite | [1,229 passed](../output/cache-audit-host-linux-tests-20261007.xml), 84.14 s console / 81.600 s XML, 1,229 collected, zero failures/errors/skips |
| Ruff lint / format | Passed / 119 files already formatted |
| Windows / Linux pip check | Both passed; no packages changed |
| Final documentation contract tests | [18 passed](../output/cache-audit-docs-tests-20261007.xml), 0.19 s console, after documentation edits |

Restricted WSL launch/pip check returned `Wsl/E_ACCESSDENIED`, before Linux test execution; no XML created by that launch. Normal-host access was requested for the existing inert tests/dependency inspection, not service control. All 161 Windows failures disappeared in the single host-access run with the same source/tests; strong evidence of execution-context restrictions, not 161 implemented bug fixes. Do not discard the restricted run or claim every initial symptom has a separately diagnosed root cause. The three new regression cases also passed in the restricted full run after the fix.

Preserved negative SHA-256: before-fix XML `6a511c1924247dfe32260093c23ae40450d130536a6ebb88de8711a7c07b3967`; restricted Windows XML `ca0e4d3551834578b964d8624d48ce4b35b850de5e7b3e075f7fe8ea3dcb9f80`. Old INC-056 import cause remains unknown, and old MEMORY history/raw experimental evidence are unchanged.

## How a nontechnical reader can check it

1. Read [current MEMORY](MEMORY.md) and [Progress Execution](<Progress Execution.md>) first. Engine 2 comparators exist; validation is not research completion.
2. In an already configured clone, open a terminal at the repository root. Do not paste service/clock commands from old documents as permission to execute them.
3. Run `python -m pytest -q tests/test_v2.py`. The cache tests use temporary local files and mocked model responses, not an Ollama service or private data. Use the project's installed Python environment.
4. A pass means the selected cache contracts held in that environment. For historical counts, inspect the linked XML receipts rather than rerunning into their names.
5. Compare limitations and next research gates with the supervisor. No test count establishes cloud-security accuracy, thesis acceptance or production readiness.

Next meaningful research action: genuine supervisor decisions and a qualified collection/evaluation plan. Further code work should address a demonstrated defect or an approved research dependency, not invent additional engine versions.

Final documentation command: `.venv/Scripts/python.exe -m pytest -q tests/test_repository_check.py tests/test_runtime_research_pack.py --basetemp=tmp/cache-audit-docs-20261007 -o cache_dir=tmp/pytest-cache-20261007 --junitxml=output/cache-audit-docs-tests-20261007.xml`. Publication/index review and remote verification are separate from tests. Preserved MEMORY archive SHA and original INC-056 XML SHA match their prior records; no historical evidence rewritten.

Staged publication check: 533 files passed; 22 explicitly staged changes inspected. Raw traceback whitespace is retained in the two negative receipts; scoped whitespace check excluding exactly those two files passes everything else. Working and staged negative blobs match (restricted run `0250314144731b0c82ac1075dfc1a65d532ddf12`, before-fix `ef51cb12fa0585e664bce1f8cec9e4772a7888e8`). This preserves evidence, not an exemption for source formatting or secret checks. No credentials/environments/models/vector databases staged. Commit/push verification is reported after actual execution in chat/Git, not invented here.
