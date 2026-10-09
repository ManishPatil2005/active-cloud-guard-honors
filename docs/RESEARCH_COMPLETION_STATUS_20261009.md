# Research completion status and remaining gates

Active Cloud Guard, 9 October 2026. QA-005 / QA-006 / R7 / R8; follows the [engine audit](ENGINE_AUDIT_20261009.md). This is a status and execution record, not approval, independent evaluation or security certification.

## Current research position

Final software verification for this batch: Windows1,464passed/38existing platform skips; Linux1,502passed, both1,502collected/zero failures/errors.54newcases; corrected208target cases,18documentation tests, lint/134fileformat/bothdependency-compatibility checks pass. Initial source-freeze and stale-count failures retained, not erased. One fresh offline historical summary executed; model/network/Docker runner behavior tested with mocks, no new live study. These are engineering checks, not independently evaluated attacks or security certification.

The two-engine architecture remains appropriate to the stated research question: configuration audit and scoped verification, followed by runtime evidence for prioritization. Python, Docker Compose, Ollama and Chroma are preserved. Engine1's frozen engineering baseline remains engine1-v2.2; current maintenance source is newer. Engine2's statistical replay, bounded acquisition/adapter tools and optional synthetic Isolation Forest/autoencoder are implemented. Their general effectiveness has not been established. No third engine is needed to solve missing evidence.

| Work requested | Action in this maintenance batch | Acceptance still missing |
|---|---|---|
| Preserve legacy outputs | Seven runners require explicit fresh destinations, reserve all outputs before collection, refuse existing paths; environment lock snapshot also fresh | Cooperative local publication, not transactional multi-file storage, authenticated evidence or all-repository writer migration |
| Input/response resources | Bounded selected file/stream reads, JSON depth/duplicate/nonfinite checks, YAML composition depth/node/alias guards, knowledge/embedding budgets, streaming hashes | Not an OS memory/CPU sandbox, exhaustive parser/native fuzzing, trusted-file race protection or global resource proof |
| Runtime timing/identity/coverage | Existing negative evidence and eligibility checklist reviewed; new dependency included in selected source freezes | No new qualified captures, source authentication, full coverage or causal clock repair; native intervention remains separately gated |
| Supervisor/labels/held-out data | Existing proposal/guidelines/intake remain usable drafts and software-tested aids | Genuine supervisor decisions, actual independent humans, untouched qualified grouped data; no invented approval/votes |
| Calibration/ablations/overhead | Existing accounting, synthetic comparators, stage-cost instrumentation retained | Real matched study, training-only calibration, grouped uncertainty, FN/FP/abstentions, valid delay/overhead/energy measurements |

There is no defensible overall percentage from counting software tests. Engineering implementation is substantial; the independent empirical validation phase remains open. The deck's FP/F1/AUC/latency/overhead targets remain unproven. A reproducible negative result is legitimate research evidence, not something to hide to make the project appear successful.

## Evidence-safe runner interface

All seven scripts now require `--output FRESH_PATH`. Additionally:

- live_check.py requires `--pipeline-output FRESH_PATH`.
- capture_environment.py requires `--lock-output FRESH_PATH`; it no longer replaces requirements-lock.txt.
- rag_check.py/vector_check.py retain --model.
- summarize.py reads historical fixed inputs and writes an explicitly historical summary with actual generation time. It is not today's full project status.

Example for the offline historical summarizer only:

```powershell
.venv/Scripts/python.exe scripts/summarize.py --output output/legacy-summary-NEW.md
```

Use a new filename for every execution; missing parents/existing files are refused. Model/network/Docker runners still have their existing operational prerequisites: fresh filenames do not grant experiment authorization. Outputs are reserved with exclusive create before collection, not secretly appended/replaced. A later reservation failure can leave an earlier empty new file; a crash/IO failure can leave incomplete files. Do not delete/rename such artifacts to claim successful execution. A collector exception writes a sanitized rejected receipt with class only, including to text-output destinations; it does not falsely assert no actions happened. Individual smoke checks still retain their raw rejected model responses where previously provided. Multi-file reservations are not an atomic transaction or per-step activity journal.

## Selected resource contract and compatibility

- Selected configuration/knowledge/context reads request at most 1,000,001 bytes and reject over 1,000,000 bytes before parsing; cache reads use their existing 2,000,000-byte cap. Hashing streams 64KB chunks instead of allocating full files; hashing time remains proportional to file size.
- JSON response reads request at most 2,000,001 bytes; nested JSON is bounded before decoding, duplicate keys and nonfinite constants/numbers refused, post-decode structural depth64/nodes50,000.
- YAML composition is bounded at depth64/nodes50,000. Aliases (including merge aliases and cyclic anchors) are explicitly unsupported and rejected, not expanded or silently reported clean. This narrows formerly unbounded alias handling and must be disclosed to reproducing researchers. Plain supported fixtures retain original findings/locations/hashes; UTF-8 universal-newline behavior is retained. The configuration file cap is now bytes, not characters, so oversized multibyte files are correctly refused.
- Knowledge corpus: 1..256 objects with nonempty string id/title/text/url and unique IDs. Retrieval count1..256. Embedding request1..256 strings/1MB total input, response exact row count, consistent nonempty dimensions<=8192, finite numeric values/no booleans and magnitude<=1e100. These are engineering limits, not tuned detector parameters or attestations of the model.
- Local model identity/chat/embedding/vector metadata now use bounded strict JSON; redirects remain refused. Audit cache policy advances to bounded-input version to avoid reuse under the old acceptance policy. Existing model/corpus/vector artifacts are not rewritten or certified. Selected integration/evaluator/clock preflight source lists cover the new limits dependency; this does not make native service intervention safe or authorized.

Remaining resource gaps include some legacy script input/subprocess reads, aggregate/time budgets, hostile filesystem races, third-party/native allocation behavior and malformed-model envelope diagnostics. The entire repository is not declared sandboxed.

## Why open failures cannot be closed by another green run

Original intermittent Windows optional-backend import failure remains unexplained. Diagnostic categorization and bounded later import observations exist; no unsupported reinstall, dependency upgrade, cache purge or success-seeking import loop occurred here. The prior failed receipt is unchanged.

Collector/harness timing exclusions and coverage misses remain historical experimental failures. No retrospective offset, failed-slot replacement, new service stop or timestamp correction is used. Current saved declarations/hashes prove selected consistency, not deployment equivalence or clock truth. Actual qualified collection needs the [capture checklist](RUNTIME_CAPTURE_ELIGIBILITY.md) and [evaluation proposal](ENGINE2_SUPERVISOR_REVIEW_PROPOSAL.md), with genuine human decisions.

## Concrete completion path

1. Supervisor reviews ENGINE2_SUPERVISOR_REVIEW_PROPOSAL.md and approves/revises the claim/label target, context, grouping, sample/analysis, acquisition and privacy. Approval is not an AI task.
2. Qualify acquisition under the approved scope: identity, readiness, accounting/coverage, clock/event bounds, comparability and cleanup. If intervention is needed, review the unfinished native fence/restoration integration and obtain separate explicit consent before acting.
3. Collect new declared independent scenario families with every failed/missing slot retained. Keep prior development/synthetic captures out of untouched evaluation.
4. Two real reviewers independently annotate blinded approved context, retain votes/disagreements/unknowns, then adjudicate. Use the existing private templates/intake; do not generate votes.
5. Freeze grouped splits and study software. Implement separately reviewed real-data fitting/threshold/calibration path without bypassing synthetic-only guardrails. Train/calibrate on training/validation only.
6. Run matched scanner/LLM/RAG/probe and runtime comparator variants on untouched test groups; report uncertainty and full abstention/exclusion denominators. Measure resource overhead under matched qualified conditions; energy needs appropriate measurement, not CPU-time inference.
7. Write thesis/paper with the measured successes and negatives, related-work verification, reproducibility and limits; external review determines publication suitability.

No exact completion date can be justified without supervisor/reviewer availability, qualified data collection and chosen study size. Additional code alone cannot finish these scientific gates. Exact executed checks/receipts/publication for this batch are in [WORK_LOG](WORK_LOG.md); tests establish software behavior, not independent security effectiveness.
