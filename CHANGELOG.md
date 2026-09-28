# Changelog

## 2026-09-28 - Instrumented Engine 2 trial

- Added bounded matching-event readiness and selected pre/post Redis identity continuity checks.
- Added local Falco kernel metrics and minimized hash-bound summaries; no privilege/network expansion.
- Live trial: 80 normalized events, 16 snapshots, zero reported drop deltas, cleanup verified; completeness remains unknown.
- Eighteen new tests; 268 pass on Windows and Linux. No independent detection/overhead claim.

## 2026-09-28 - Offline Engine 2 sensor normalization

- Added bounded, receipt/hash-bound Falco adapter and non-overwriting CLI; minimized output uses the existing runtime capture contract.
- Processed the prior live sample: 40 events, zero rejected records; sensor loss stays unknown. No new capture or threat score.
- Added 34 tests; 250 passed on both Windows and Linux. Saved accounting, normalized capture and regression evidence; Engine 1 unchanged.

## 2026-09-28 - Bounded Engine 2 live sensor smoke

- Added digest-pinned, time/resource-bounded Falco trial with local-only raw logs, minimized published summaries and scoped cleanup.
- Observed 40 selected Redis-cgroup syscall records and PONG; preserved failed attempts and their fixes. No ongoing sensor, threat or completeness claim.
- Added 12 regression tests; 216 pass on both Windows and Linux. Raw adapter, coverage accounting and independent evaluation remain open.

## 2026-09-28 - Docker WSL integration and Linux regression validation

- Enabled ACG-Research Docker Desktop integration through its UI; verified server and matching running Redis identity from Windows/WSL.
- Created separate Linux core/test virtual environment with an observed dependency snapshot. Full Linux suite: 204 passed; lint/format/dependency checks and synthetic replay passed.
- Preserved initial cache warnings; isolated Linux pytest cache and reran successfully. No Engine 1 code change, kernel sensor, live telemetry or accuracy claim.

## 2026-09-25 - Windows-hosted Linux research setup

- Provisioned dedicated ACG-Research Ubuntu WSL distribution outside Git; added non-admin Linux user and saved actual Linux preflight evidence.
- Documented installer retries and successful terminal-attached install, host resources, security scope and reproduction.
- Restarted existing Docker Desktop; Docker access from the new distribution awaits its explicit WSL integration setting. No sensor installed or runtime accuracy claim. Windows 204-test regression rerun passed.

## 2026-09-25 - Engine 2 host preflight tooling

- Added read-only platform/Linux-marker facts and a non-overwriting report script; no sensor installation or compatibility claim.
- Added eight tests; full suite 204 passed. Saved actual Windows preflight and separate regression evidence.
- Documented stopped Docker WSL environment and unavailable daemon as live-telemetry prerequisites. Engine 1 and replay contracts unchanged.

Changes are recorded on the date they occurred or were documented. Historical failures are retained, not removed from the narrative.

## 2026-09-25 - Engine 1 freeze and Engine 2 foundation (package 0.5.0)

- Published Engine 1 v2.2 at commit 6736a57 and tag engine1-v2.2 before runtime changes; local/remote references matched.
- Added bounded normalized runtime capture ingestion, declared container-to-inventory bindings and UTC count windows.
- Added a separate-baseline standardized-count comparator, leakage guards, unknown/insufficient-data states and observation-only CLI. No actions, sensor connection or TCI updates.
- Added explicit synthetic fixtures/replay evidence and 28 tests; full suite passes 196. No independent accuracy, live telemetry or ML-model claim.
- Excluded raw runtime logs from publication and documented live Linux/sensor prerequisites. Existing stack and dependencies preserved.

## 2026-09-23 - Engine 1 v2.2 baseline (package 0.4.0)

- Added local Compose/container identity verification before and after fixed credential-free service observations.
- Added read-only Redis PING and PostgreSQL startup classification, bounded framing/deadline, strict loopback scope and remote-Docker rejection.
- Passed 168 tests and two real lab runs: stable selected identities; Redis protected-mode denial and PostgreSQL SASL challenge.
- Kept all prior evidence and unchanged service settings; documented selected-identity scope, missing full attestation and remaining scientific gates.

## 2026-09-23 - Reviewed verification (Engine 1 v2.1, package 0.3.0)

- Added strict loopback inventory and hash-bound operator policy/review validation; reject stale context, duplicate records and unauthorized scope.
- Linked explicitly approved retained model candidates to inventory TCP observations, while preserving review requirements and withholding automatic model scores.
- Added expected/unexpected reachability assessments without suppressing findings or claiming deployment equivalence, authentication bypass or vulnerability confirmation.
- Added 30 regression cases (136 total) and a real-loopback/synthetic-policy smoke with five passing checks; preserved historical reports.
- Added a detailed refinement report, operator templates, trust boundaries and remaining research gates. No Engine 2 or independent effectiveness claim.

## 2026-09-23 - Research-facing README

- Reorganized the GitHub landing page around an abstract, research questions, architecture, linked measurements and threats to validity.
- Added staged reproduction instructions, evidence-preservation warnings, repository navigation and version-specific attribution guidance.
- Distinguished v2 measurements from historical reports and local software checks from independent evaluation; no implementation, stack, measurements or license changed.

## 2026-09-23 - Engine 1 v2 efficiency (package 0.2.0)

- Added opt-in bounded exact-request audit cache, current model identity checks and cached-output revalidation; probes remain fresh.
- Reuse complete unchanged Chroma collections without re-embedding; support forced rebuild and repair unexpected IDs.
- Expose generation ceilings, socket timeout, cache/inference provenance and per-stage timings. Reject explicitly truncated output.
- Added 19 v2 test cases (106 total), a non-overwriting live benchmark and separate v2 evidence; preserved all v1 reports.
- Live single-fixture smoke: warm miss 5.256 s; hits 0.084/0.072 s; index rebuild/reuse 5.804/0.084 s. Uncached first run 17.424 s; no energy or independent accuracy claim.

## 2026-09-23 - Initial research implementation (retrospective entry)

- Created the bounded Python rule scanner, local model adapter, lexical and Chroma retrieval, explicit TCP probe, provisional risk score and integrated CLI.
- Created 45 development fixtures, nine source summaries, four-service Docker lab and reproducibility scripts.
- Recorded 84 passing software tests, live service observations, model smoke runs and Trivy execution on 11 compatible fixtures.
- Corrected the reachability score direction; distinguished missing runtime evidence from zero anomaly.
- Preserved schema failures, unsupported model claims and latency misses. Added location checks and narrow authentication-policy corroboration.
- Wrote the original deck audit, experiment protocol, literature review notes and measured status report.

## 2026-09-23 - Documentation and repository publication

- Added project requirements, architecture, interface design, test plan, security boundaries, decisions, incident history, current state and maintenance workflow.
- Added a task ledger, contributor/agent working agreement, evidence index and publication exclusions.
- Added a bounded documentation/credential/publication checker, three tests and a repository-local pre-commit hook. The local suite now passes 87 tests; the original 84-test snapshot is retained. No hosted CI is claimed.
- Created and pushed the private `ManishPatil2005/active-cloud-guard-honors` GitHub repository on main. GitHub API and Git remote verification matched local HEAD; receipt and commit identities are tracked in docs/WORK_LOG.md.
- Preserved the existing architecture and stack. The user's supplied web-product guide was used only as a documentation-process reference.
- Preserved saved-report bytes and applied a path-specific CRLF-aware whitespace check after recording the initial publication warning in INC-017.
