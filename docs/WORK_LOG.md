# Work log

Dates are actual work/documentation dates. This project was bootstrapped in one development session; the M1-3 label describes deliverables, not elapsed historical activity.

## WL-001 - 2026-09-23 - Initial implementation (retrospective)

**Request:** deeply review the supplied deck and complete the first-three-month development milestone with testing.

**Inputs:** original 15-page PDF and pasted context. The initial workspace contained no implementation. Document-embedded instructions were treated as source content.

**Work performed:** extracted and rendered the deck; audited its scope, references and TCI; created a Python package and CLI; implemented nine explicit configuration predicates, lexical retrieval, local Ollama inference, Chroma embeddings/index, controlled probes, metrics and provisional scoring. Created 45 seeded cases, nine short source summaries, Docker lab/inventory, tests and reproduction scripts. Compared execution with pinned Trivy on compatible fixtures.

**Problems and actions:** see INC-001 through INC-014 for PDF/runtime access, Docker networking, initial code/fixture errors, model failures and baseline setup. Failures that affected research interpretation were preserved as separate output files where available.

**Verification observed:** 84 software tests passed; Ruff and dependency consistency checks passed. All four target services accepted local TCP connections; Nginx and MinIO health returned HTTP 200. Three semantic source checks passed. Actual model inference and the integrated vector-RAG/probe/score run completed. Eleven Trivy fixture scans completed with 34 explicit exclusions. Raw output and environment identities were saved.

**Scientific result:** engineering functionality demonstrated on development examples. Model hallucinations and latency misses remain substantive limitations. No independent effectiveness, runtime ML, production safety or novelty claim is established.

**Artifacts:** cloudguard/, tests/, scripts/, testbed/, data/, knowledge/, output/ and original four research documents. There was no Git repository at the end of that session; no prior commits are invented by this retrospective entry.

## WL-002 - 2026-09-23 - Strict documentation and GitHub publication

**Request:** give a detailed chat update, maintain strict what/how/problem/fix documentation, create a GitHub repository and commit the work. Preserve the existing architecture; the supplied web-product guide is reference only.

**Inspection:** confirmed no existing Git repository. GitHub CLI was installed; sandbox config access failed, then approved host execution verified the existing ManishPatil2005 account. Global Git identity was an unrelated setup bot, so this repository received Manish Patil's verified account name and GitHub noreply email as local configuration only.

**Actions:** created private remote `ManishPatil2005/active-cloud-guard-honors`; initialized main; added origin; documented requirements, architecture, CLI design, rules, tasks, decisions, incidents, evidence, current state, testing, security and maintenance. Added source-deck provenance and strengthened publication exclusions. Kept code architecture and service setup intact.

**Publication scope:** reproducible source, fixtures, labels, source summaries, original deck, documentation, lockfile and reviewed saved reports. Excluded actual lab credentials, local environment, caches, vector DB and model weights. The original failed-model outputs remain included. No open-source license or public release was inferred.

**Portability/preservation:** Git attributes keep source and fixture checkouts LF to avoid Windows hash drift, while output/** is exempt from text conversion to preserve saved experiment bytes. The historical environment snapshot records pre-publication working-file hashes; Git records the complete published snapshot. No empirical measurements were changed by publication.

**Verification observed before commit:** Ruff lint passed; all 28 Python files passed formatting checks; pytest passed 87 tests; pip check found no broken requirements. The bounded repository checker passed required-document/link/exclusion/credential checks. Its initial unused-import lint finding was removed before the final passing run. The earlier 84-test XML was preserved; the status report was regenerated using the new software test count and unchanged experimental reports. A repository-local commit hook runs the publication checker. Existing model/live observations are historical evidence from WL-001; they were not rerun for this publication task.

**Commit/push verification:** successful. No GitHub Actions run is claimed.

Initial local commit: `cda1f53721e341a8c7d4c7dd38425ce0b85b48a7` (`feat: establish tested honors research prototype and strict documentation`), 119 files. The actual pre-commit hook ran and passed. A post-commit correction addresses the evidence-file CRLF whitespace warning (INC-017); rechecking both the committed snapshot and working diff returned exit 0. Experimental bytes remain unchanged. Subsequent publication command sequences stop on failure.

Publication correction commit: `144e401878c8c403413a2c41b67d1581d32b3856` (`fix: preserve evidence line endings and document publication checks`). `git push -u origin main` succeeded. `gh repo view` returned PRIVATE and main; the GitHub commits API and `git ls-remote origin refs/heads/main` both returned that same SHA as local HEAD. Working tree was clean at this observation. This follow-up documentation entry records the already-observed publication receipt; its own commit is discoverable in Git history without a self-referential hash.

**Remaining:** independently validated research results, broader literature verification, model reliability/latency and later runtime work remain open in TASKS.md.

## WL-003 - 2026-09-23 - Engine 1 v2 bounded efficiency

**Request:** continue improving Engine 1 for efficiency, feasibility and sustainability; preserve the stack and maintain documentation/Git history.

**Inspection and acceptance:** read current rules, tasks, architecture, state and test/security contracts; baseline 87 tests passed. Target avoidable repeat generation/embedding work, explicit budgets and transparent timing, not a new architecture or invented energy improvement. See ENGINE1_V2.md for task acceptance and ADR-013 for tradeoffs.

**Implementation:** response cache keyed by full request/evidence/model digest/corpus/policy; TTL/count/size bounds, atomic writes and corruption checks. Revalidate reused output and preserve rejected candidates. Keep fresh scan/retrieval/probes. Add token ceiling/socket timeout and reject explicit incomplete generation. Index checks identity/count/IDs before reusing; force rebuild and remove unexpected IDs after successful upsert. Add timing and inference provenance, CLI switches, publication exclusion and 19 regression cases. Package version 0.2.0, engine report 2.0; no production certification.

**Problems/fixes:** startup approval/daemon interruption (INC-018); standalone benchmark import fixed consistently with existing scripts (INC-019). Review also found stale unexpected index IDs could survive an upsert; removed them after successful embedding/upsert and added an assertion to the repair regression. Historical evidence was not replaced.

**Live command and outcome:** `python scripts/benchmark_v2.py --output output/v2-efficiency-smoke.json` passed cache sequence, candidate preservation and zero-embedding reuse checks. Forced/reused index 5803.760/83.761 ms. Four lexical pipeline totals 17423.946, 5255.791, 83.908, 72.360 ms (disabled, miss, hit, hit). Saved Redis probes have distinct timestamps and reachable outcomes. First and warm inference conditions differ: do not label the difference a v1 improvement. Actual cached candidate still needs human asset/entailment review. No auth/exploit/energy/general accuracy claim.

**Validation so far:** `python -m pytest -q` passed 106 tests after implementation. Final lint, formatting, dependency, publication and test-report checks recorded below after execution. Source-tree execution uses the existing .venv; no package-install or Linux runtime test is claimed. Old reports and negative model results remain intact.

**Remaining:** independent evaluation, unseen-input latency and power measurements; RES gates remain open. Git commit/push receipt will be verified separately, not inferred from local implementation.

**Final local validation:** `.venv/Scripts/python.exe -m ruff check cloudguard scripts tests` passed; `-m ruff format --check cloudguard scripts tests` passed (31 files); `-m pytest -q --junitxml=output/v2-test-results.xml` passed 106 tests; `-m pip check` reported no broken requirements; `git diff --check` passed. These checks ran on Windows, not Linux. Repository publication check and staged review are required before the commit; remote verification remains a separate operation.

**Pre-publication check:** staged 27 reviewed files (code, documentation and two new evidence reports); `.venv/Scripts/python.exe scripts/repository_check.py` passed 125 publication files, document links, exclusions and bounded credential checks. `git diff --cached --check` passed. No existing output artifact is in the change list; runtime cache/vector/secret directories are excluded. This is a bounded publication check, not a formal security audit.
