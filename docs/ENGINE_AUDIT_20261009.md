# Engine audit, research alignment and open gaps

QA-004 / R4 / R7 / R8, 9 October 2026. Start revision c711c1aa02ea506b9e0b1b9fe357f742a1e40a16; this audit includes the transport maintenance change described below. **The system is a working research prototype, not a complete secure product or publication-ready independently evaluated detector.**

## Scope and assurance limits

Repository-wide library inventory/AST syntax review:38Python modules,231definitions, zero syntax errors, no literal shell=True call keywords in that library scan. Repository-wide risky-call search covered library/scripts; focused manual review covered scanner, LLM/grounding, retrieval/vector, cache, pipeline/probes/verification/deployment, scoring, runtime replay/model/input/accounting and adapter boundaries. Requirements were compared to PRD/deck audit/task ledger/current evidence. Full regression suites ran on both OS.

This is **not** an exhaustive line-by-line audit of every script, native FFI/job/restoration path, package/transitive dependency, historical artifact or deployed host. Broad search and tests do not prove absence of vulnerabilities. No independent pentest, CVE/advisory audit, hostile-filesystem/resource proof, fuzz campaign or live adversarial model/service test was performed. The available AWS scan skill requires source upload/cloud setup; no AWS provisioning/upload/scan ran. Local review proceeded without claiming managed findings. No new deployment, service/clock intervention, sensor workload or autonomous monitoring.

## Why reported failures do not all mean the same thing

| Evidence | Meaning and current disposition |
|---|---|
| INC-067 evaluator negative tests | Old evaluator overwrote a fixed filename; deliberately reproduced in temporary test roots, then fixed/tested. An initial empty-corpus test was insufficient and is retained as such. Final post-fix results passed; real historical report unchanged. |
| INC-066 traversal negative | Old code repeatedly inspected window lists; reproduced/fixed with deterministic work-count and full-report equivalence checks. Not a threat-detection failure. |
| INC-056 Windows optional-backend import | Actual intermittent failure; cause remains unknown. Later successful imports/tests do not establish a repair or erase the failure. |
| Timing/coverage negatives (including INC-032/039) | Actual experimental qualification failures/instability; collector/harness relationships and actor/cause unresolved. Those gates remain open. |
| INC-068 transport boundary negatives | New mocked reproduction: invalid port accepted and redirect protection absent. Fixed below; no external connection or observed data exfiltration claimed. |

Negative results are retained to explain defects and limits, not rewritten to make progress appear green.

## Fixed finding: local model transport was not fully confined

`llm.audit` and `model_identity` interpolated an unchecked library port into a URL. A string shaped like `11434@example.invalid` changes URL authority away from127.0.0.1. This parameter is not exposed by the current core CLI; exploitation depends on caller-supplied library arguments, not ordinary IaC text. In addition, ProxyHandler({}) disabled proxies but did not disable urllib's default HTTP redirects. The local server could redirect identity/chat/embedding paths and allow a nonlocal request or foreign-origin result. **Do not infer that urllib forwards a POST configuration body on every redirect**: method/body behavior depends on code; crafted initial-port URL and redirected requests are different issues.

Fix: exact integer port1..65535 validation before requests/cache work; explicit shared LocalOnlyRedirect handler refusing all redirects (including other local endpoints) on chat, identity, embedding and vector model-identity requests. Default endpoints/proxy suppression remain unchanged. Audit cache policy changes to engine1-v2-auth-guard-2-local-only so old-policy responses are not reused. Existing vector collections are not rewritten or certified by this fix; their historical provenance remains a trusted-local-artifact assumption. Frozen engine1-v2.2 tag/history unchanged; current maintenance source differs.

38newcases: malformed/bool/float/out-of-range ports refuse before opener creation, direct redirect refusal301/302/303/307/308 to local/foreign destinations, fixed chat/embedding URLs/proxy/handler wiring, plus actual stdlib opener-chain tests using a synthetic HTTP handler and no sockets. Three before-fix tests failed; final target66passed (earlier61pass retained). Existing cache-context test now uses the current policy constant for non-policy variants, preserving isolated invalidation checks rather than accidentally changing two inputs.

Primary API reference: [Python urllib.request documentation](https://docs.python.org/3/library/urllib.request.html), build_opener/HTTPRedirectHandler/ProxyHandler; actual runtime behavior tested in Python3.12. No real Ollama inference, network pentest or exfiltration trial.

## Remaining engineering/security gaps

| Priority | Gap / evidence scope | Required next work |
|---|---|---|
| P1 before new experiments | Several legacy writers still replace fixed outputs: live_check, integrated_check, rag_check, vector_check, trivy_baseline, capture_environment, summarize; evaluate.py alone is repaired | Add explicit fresh-output/refusal semantics and regression tests before rerunning each. Do not execute them now just to obtain green results. |
| P1 for hostile inputs | Some paths read full files before size checks; YAML recursion/expansion and some model-identity/embedding JSON reads lack strong budgets | Bound reads/structure and reject ambiguous/nonfinite envelopes. Current limits are engineering guards, not a resource sandbox. |
| P1 research trust | Source membership/exact locations plus two narrow predicate guards are not general entailment; approvals/bindings/reviewer names/source declarations are not authenticated independent evidence | Actual blinded review, qualified provenance/context and correct claim target; no generated independent labels. |
| P1 runtime qualification | Clock/collector alignment, completeness/partial coverage and native restoration/fencing are unresolved | Approved protocol/current preflight and separately authorized safe interventions only if needed; no generic-proceed permission. |
| P2 host/artifact trust | Local Ollama/Docker/cache/vector files trusted; cache is plaintext and no hostile-race/full dependency attestation | Access-controlled ignored storage, reviewed artifact provenance, threat-model-specific hardening. A file hash is not encryption, authorization or ground truth. |
| P2 assurance | Dependency compatibility passes, but current vulnerability advisories, native memory safety, exhaustive parser fuzzing and host/container hardening not assessed here | Separate pinned-dependency/advisory review, native security review and resource tests. No “zero vulnerabilities” claim. |
| Open planned capability | Continuous runtime acquisition/qualified real-data ML/calibrated TCI/response absent or intentionally gated | Do not promote saved/synthetic software to a live calibrated detector or enable autonomous isolation without reviewed scope. |

No confirmed exploit is asserted for every gap. Source-level review items and known limitations are distinguished from the reproduced transport defect.

## Does it follow the research topic and original plan?

Yes in architectural direction: Python/CLI, Compose, Ollama, Chroma, configuration candidates + scoped staging evidence + later runtime observations. Two engines remain; statistical/Isolation Forest/autoencoder are Engine2 comparators, not three engines. No stack migration/SaaS/dashboard or production cloud mutation was made.

| Original requirement | Engineering state | Research gate still open |
|---|---|---|
| R1 scope/related work | Deck/threat/scoring/protocol documents and source register | Literature full-text/source/novelty audit partial; supervisor decisions pending |
| R2 local testbed | Four-service Compose and historical bounded live observations | Fresh-host/security/coverage qualification not proven by old receipts |
| R3 configuration baseline | Nine explicit predicates/45development fixtures | General Terraform/Helm and full semantic policy scope unsupported; seed labels not independent ground truth |
| R4 grounded local model | Retrieval/adapter/schema/location/membership guards; transport hardened | Broad entailment/hallucination reduction and held-out RAG effectiveness unproven |
| R5 scoped verification | Allowlisted literal loopback TCP and selected identity/auth observations | TCP accept is not Internet exposure, exploitation or full deployment equivalence |
| R6 evidence prioritization | Provisional monotonic score, missing runtime explicit, context integration | Calibration/real runtime contribution/fair prioritization benefit unproven |
| R7 reproducibility | Hashes/raw reports/tests/negative evidence; evaluator safer | Legacy output writers/experimental comparability still need work |
| R8 maintenance | Strict documents/private Git history/local publication checker | No GitHub CI or independent security certification |

The deck's90%FP reduction/F1.92/AUC.95/3.5-second static/<5%overhead figures remain targets, not achieved guarantees. First M1–3 engineering scope principally covers Engine1; later Engine2 research is not retrospectively declared complete. Genuine independent labels/untouched grouped test data, comparable qualified captures, actual scanner/LLM/RAG/probe ablations, calibration/grouped uncertainty and matched overhead/energy remain the critical publication path. Repeated synthetic utilities are preparations, not replacements for that study.

## Verification and closure

Before `output/local-boundary-before-windows-20261009.xml`:3failed/0.88s. Post-fix initial61pass, final66pass0.40s in `output/local-boundary-final-target-windows-20261009.xml`. Full Windows1,410passed38existing skips/60.80s; full Linux1,448passed/177.80s, both1,448collected/zero failures/errors, final source/cases included. Receipts `output/engine-audit-full-{windows,linux}-20261009.xml`; exact XML times/docs/publication checks in WORK_LOG. Lint131fileformat/bothpipchecks pass. Historical MEMORY/baseline/original failed import bytes unchanged. All tests are software checks, not independently evaluated attack scenarios or certification.

Next practical order: finish legacy evidence writers before new experiments; harden input/response budgets; obtain actual protocol/context/independent-human decisions and qualify captures; execute frozen fair ablations/calibration/grouped evaluation/overhead under approved conditions. Do not add arbitrary model/engine versions or claim prevention/production readiness to substitute for these missing results.
