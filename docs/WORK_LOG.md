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

**Commit/push verification:** to be appended after the remote state is observed. No GitHub Actions run is claimed.

Initial local commit: `cda1f53721e341a8c7d4c7dd38425ce0b85b48a7` (`feat: establish tested honors research prototype and strict documentation`), 119 files. The actual pre-commit hook ran and passed. A post-commit correction addresses the evidence-file CRLF whitespace warning (INC-017); rechecking both the committed snapshot and working diff returned exit 0. Experimental bytes remain unchanged. Subsequent publication command sequences stop on failure.

**Remaining:** independently validated research results, broader literature verification, model reliability/latency and later runtime work remain open in TASKS.md.
