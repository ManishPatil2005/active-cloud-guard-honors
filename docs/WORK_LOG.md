# Work log

## WL-009 - 2026-09-25 - Engine 2 host preflight (E2-003, partial)

**Request/acceptance:** continue Engine 2 without changing Engine 1 or the stack. Establish actual host availability; provide reproducible read-only facts, distinguish unavailable/absent prerequisites, never certify a sensor from path presence, and preserve existing reports.

**Prior publication:** replay foundation main was published as `52efa64a82431d05a4beaaa47dd530900f91f4db`; working tree was clean at this increment's start.

**Environment observed:** initial sandbox WSL enumeration returned E_ACCESSDENIED and Docker config access was denied. Approved host retry of `wsl --list --verbose` listed only docker-desktop, Stopped, WSL 2. `docker version --format '{{.Server.Version}}'` could not connect to the Docker Desktop Linux engine pipe. No distribution, service, package, privilege or kernel settings were changed. These observations do not invalidate historical successful service experiments.

**Implementation:** runtime_preflight module reports local platform, Linux effective UID and file-type facts for BTF, tracefs path and cgroup-v2 marker. Errors remain unavailable, not absent. No subprocess/network/driver operations. The script exclusively creates a report. Even all markers present yields requires_sensor_specific_validation, never readiness. Package/replay schemas and Engine 1 unchanged.

**Verification commands/results:** `.venv\Scripts\python.exe -m ruff check cloudguard scripts tests` passed; `-m ruff format --check cloudguard scripts tests` passed (44 files); `-m pytest -q --junitxml=output/engine2-preflight-tests.xml` passed 204 tests including eight new cases; `scripts/runtime_preflight.py --output output/engine2-windows-preflight.json` saved actual Windows facts, linux_host_required; `-m pip check` passed. Script zero exit means report saved, not readiness. Publication checker and Git staged/whitespace review precede commit; remote SHA is verified after push and reported in chat.

**Limits/next:** Linux branches use mocked tests, not live Linux validation. E2-003 remains partial; host/setup selection and a scoped sensor privilege plan are needed before a real capture. No live runtime, ML, overhead or independent effectiveness experiment. See INC-021. No historical evidence overwritten.

## WL-008 - 2026-09-25 - Engine 2 replay foundation (E2-001/002)

**Publication receipt:** Engine 1 baseline committed as `6736a577f1ba08b4700daf8a86370ec3bbd1c019`; tag `engine1-v2.2`. Pre-commit publication checker passed 139 files. Push succeeded; git ls-remote returned the same SHA for main and the tag. Working tree was clean before Engine 2 implementation. Historical live reports remain dated 23 September.

**Scope/acceptance:** user asked to proceed after freezing Engine 1. Implement a minimal observation-only runtime data path, preserving Python/Docker/Ollama/Chroma and scientific boundaries. No authorization inferred for background monitoring, kernel changes, isolation, production data or fabricated real captures.

**Implementation:** added strict normalized captures, bounded parsing, declared full-container-ID inventory bindings, timezone-aware sorted events, nonempty count windows, per-asset baseline statistics and review-only deviations. Same group/capture and overlapping event reuse across fitting/observation are rejected. Baseline is never fitted on observation records. No zero-fill of collection gaps, no threat verdict, no actions or TCI integration. Added runtime-replay CLI, synthetic provenance/fixtures and a non-overwriting smoke script. No new dependencies. Deferred raw sensor adapters and ML pending real-data contracts rather than claiming them implemented.

**Verification observed:** Ruff lint passed; full pytest suite 196 passed, saved as output/engine2-foundation-tests.xml; pip check passed. `python scripts/runtime_check.py --output output/engine2-replay-smoke.json` passed all four checks. CLI help and subprocess smoke passed. Synthetic normal-count window scored zero; constructed nine-connect window scored 8.0 and flagged review. This is software behavior, not measured threat detection. No new live Docker/model/sensor experiment was run for Engine 2. Publication/formatting checks repeated before commit.

**Problems/limits:** preventing data leakage, falsely treating silence as normal and trusting imported identity are explicit design constraints, covered by negative tests and documentation—not problems claimed solved scientifically. Capture metadata can be forged; independent benign labels and completeness are absent. Scoring floor/threshold and three-window minimum are engineering choices, not validated statistics. Real Linux sensor/adapter, coverage accounting, ML models and independent runtime evaluation remain open. No failed experiment or historical artifact was overwritten.

**Final publication checks:** Ruff lint passed and all 41 Python files passed formatting; 196 tests passed again; pip check passed; staged whitespace check passed. Inspected 27 staged files. `python scripts/repository_check.py` passed 148 publication files, links, exclusions and bounded credential checks. Raw telemetry publication is blocked at output/runtime-raw/. No hosted CI or live sensor test is claimed. Exact final commit/remote match is checked during push and reported in the task handoff.

## WL-007 - 2026-09-25 - Resume and freeze Engine 1 baseline

User asked to continue publication and begin Engine 2. Re-inspected the uncommitted Engine 1 work and required context. On 25 September, Ruff lint and formatting (38 files), all 168 tests, dependency consistency and git whitespace checks passed again. The live service observations remain the actual 23 September runs; they were not relabeled or rerun merely for publication. Freeze the reviewed v2.2 snapshot before runtime additions. Publication/link checks and remote commit/tag verification are performed at the commit boundary.

## WL-006 - 2026-09-23 - Engine 1 v2.2 baseline before runtime work

**Request/acceptance:** proceed with remaining critical Engine 1 gaps, freeze a tested baseline, then begin minimal observation-only Engine 2. Preserve documentation, reports and Git history.

**Implementation:** read required docs and actual code; inspected existing running Docker lab and current Compose service hashes. Consulted official Compose, Redis and PostgreSQL protocol references. Added local-daemon-only identity comparison (Compose labels/hash, image, declared command/env/ports and running state), source stability and pre/post container identity. Added fixed Redis PING/PostgreSQL startup without passwords/queries. No deployment or container mutations. New verify-service command scans the actual deployed Compose file rather than a development analogue.

**Checks/results:** Ruff passed; pytest 168 passed in output/engine1-v22-tests.xml; pip check passed. Two `python scripts/service_check.py --output ...` runs saved separately as service-identity-v22.json and service-identity-v22-final.json. Both checked Redis and PostgreSQL identities before/after; Redis protected-mode denial, PostgreSQL SASL challenge. No protocol responses or environment secrets logged. Review hardened local Docker endpoint enforcement, response framing, and preserved selected-scope rather than full-attestation language. No failed live observation was discarded.

**Scope/next:** ENGINE1_BASELINE.md is the report and freeze contract. Identity evidence trusts Docker, not a hostile administrator; mounted content and application state remain outside scope. Independent accuracy/latency evaluation still open. Freeze this revision before runtime scaffold work. Final publication checks and exact commit/tag receipts are verified during publication.

## WL-005 - 2026-09-23 - Engine 1 reviewed verification (E1R-001..004)

**Request/acceptance:** refine Engine 1 following the discussion, supply a report, maintain documentation and commits. Keep the existing stack. This increment targets strict context binding, explicit policy, reviewed model-to-inventory linkage and honest assessment; it does not claim all research gates complete.

**Work and rationale:** inspected current code/evidence and required docs. Added verification.py for bounded duplicate-safe JSON, strict loopback inventory, policy/review schemas and conservative outcomes. Pipeline snapshots inventory, records byte hashes, checks source consistency before probing, matches exact retained candidate fingerprints and model request identity, then attaches TCP observations only with explicit operator approval. Added CLI flags, package 0.3.0 / engine2.1 identity and review templates. Retained legacy rule-score behavior; model verification remains unscored and all deployment equivalence remains unverified.

**Problems handled:** initial atomic patch rejected because a CLI context line did not match; no files were changed by the rejection, and corrected patches applied. Review identified that request hashes without model digests would not adequately bind model identity, so the approval gate requires digest-bound audits (existing cache-enabled path). Updated the old pipeline mock and version expectation to the new output contract. Tests cover wrong/missing digest, changed request/candidate/input, rejected candidates, invalid scope and no unauthorized probes. No experimental failure was hidden or overwritten.

**Observed verification:** Ruff lint passed; pytest passed 136 tests with output/verification-v21-tests.xml; pip check passed; CLI run --help exposes policy/reviews; git diff --check passed. `python scripts/verification_check.py --output output/verification-v21-smoke.json` passed all five checks using real local connections and explicitly synthetic policies. Model integration is mock-tested, not live-model/human-reviewed; no Docker deployment or energy/accuracy study was run. Final formatting/publication and remote checks are recorded at handoff.

**Artifacts and limits:** ENGINE1_REFINEMENT.md is the requested report. Existing output files remain intact. E1R-004 (actual deployment attestation/auth-aware checks), independent labels, matched baselines, latency, calibration and Engine 2 remain open. Hashes prevent stale document reuse, not malicious operator records; reviewed_by is not authenticated. No research approval, deployment equivalence or completed human review was fabricated.

**Final pre-publication verification:** `python -m ruff check cloudguard scripts tests` passed; `python -m ruff format --check cloudguard scripts tests` passed all 34 files; `python -m pytest -q --junitxml=output/verification-v21-tests.xml` passed 136 tests; `python -m pip check` passed. Reviewed 24 staged files. `python scripts/repository_check.py` passed 131 publication files; `git diff --cached --check` passed. Numeric inventory ports are explicitly Python integers as well as schema-valid, preventing JSON integer-valued floats from passing preflight then failing at the socket boundary. Runtime caches, environments and secrets remain excluded. Commit/push and exact remote SHA are verified during publication and reported in the task handoff.

## WL-004 - 2026-09-23 - Research-facing GitHub README (DOC-002)

**Request/acceptance:** make the README formal, visually organized and suitable for research review. Include motivation/questions, actual architecture and scope, evidence-linked observations, reproducibility and validity limits; do not invent endorsement, novelty, a DOI or an open-source license.

**Work:** replaced the operational-note-led introduction with a centered project identity, abstract, reviewer navigation, Mermaid architecture, capability/results tables and explicit research gates. Preserved Python/Docker/Ollama/Chroma. Separated v2 observations from historical reports. Organized setup into environment, model-free checks, lab and experiments; removed the old default sequence that regenerated fixtures and overwrote saved reports. Added cross-platform activation guidance marked unvalidated, safety boundaries and attribution instructions.

**Verification scope:** checked claims against PRD, architecture/protocol and saved v2 evidence. Documentation-only: no runtime changes or new model/experiment results. Publication/link checks and staged review are recorded below after execution. An initial patch syntax attempt was rejected before editing files; the corrected atomic README replacement succeeded. No project data were lost or runtime incident introduced. Historical scripts and evidence were not modified.

**Observed checks:** Python structure check passed balanced code fences/div markup and all 40 local README links. `.venv/Scripts/python.exe scripts/repository_check.py` passed all 125 publication files; `git diff --check` and `git diff --cached --check` passed. Staged review contains exactly five documentation files. GitHub visual rendering was not separately inspected; software tests and live experiments were not rerun for this prose-only change. The cited 106-test result is the saved v2 run. Commit/push verification is performed at publication, with the exact receipt supplied in the task handoff.

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
