# Runtime labeling coordinator pack — draft 0.1

18October2026 implementation update: optional `--review-agreement` now computes
the original pair table, unknown coverage and known-pair Cohen kappa before
adjudication. [Method and interpretation](RUNTIME_INTAKE.md). Older statements
below describing agreement fraction only are historical. This software extension
does not supply actual humans, approve a final analysis plan or certify blinding.
Owner-reported proposal0.1 approval is [recorded separately](SUPERVISOR_APPROVAL_RECORD.md).

**DRAFT — NOT APPROVED.** E2-035/RQ3/E2-004 preparation, 6 October 2026. This pack is prepared for supervisor review, not supervisor-reviewed or signed. No actual reviewers recruited, messages sent, labels obtained, telemetry collected, model trained or benchmark established. Existing Python/Compose/Ollama/Chroma and two-engine boundaries preserved. [Current status](CURRENT_STATUS.md).

## Decisions before annotation

Use [the blank supervisor sheet](templates/runtime-supervisor-review.md) to approve/revise the reviewer-facing [labeling guidelines](RUNTIME_LABELING_GUIDELINES.md), threat scope, context packet, window size, grouping/sample design, blinding, adjudication, unknown handling and intended claims. Proposed target is security-review necessity within a narrow approved scope, **not confirmed attack detection**. Broad threat claims require evidence the current three-kind projection does not contain; do not change the original research question or silently substitute a count-change benchmark.

The existing static-scenario planning target of 120 is not a runtime sample-size/power calculation. A supervisor-reviewed run/family count and uncertainty plan is needed before collection; windows from one run are not independent replications. Use the same approved scope for future statistical/ML comparisons. The engine's current scores and synthetic labels are forbidden annotation answer keys.

## Roles, separation and private records

| Role | Responsibilities | Must not imply |
|---|---|---|
| Supervisor | Approve/revise target/protocol/claims and required evidence/safety | A blank signature or this draft is approval |
| Coordinator | Freeze approved guideline bytes/hash, source/case lineage and grouping; prepare neutral packets; retain originals/exclusions | Declared IDs/splits/hashes authenticate humans or unseen data |
| Two human reviewers | Independently label the same observed windows using approved context, without predictions or each other's votes | Generated/synthetic votes are independent submissions |
| Adjudicator | Resolve disagreements/unknowns with reasons after original votes locked; preserve original agreement statistics | A forced agreement or edited originals is valid adjudication |

Reviewer participation, conflicts, consent, identity-to-pseudonym mapping, exposure log, private context/seed key, original submissions, approval records and exclusion ledger belong in **private/runtime-labeling/** or approved access-controlled storage, not public examples. The folder is Git-ignored and the publication checker rejects it if force-staged. These are accidental-publication controls, not encryption, access control or prevention of copying elsewhere. No actual private records created here. Publish only separately consented, minimized materials after manual review.

## Packet design and blinding audit

Coordinator packet contains assigned neutral run/asset/window IDs, frozen guideline hash, normalized events for those units, supervisor-approved independent contextual evidence with opaque IDs, and standardized quality/missingness information. Reviewers need adequate context; hiding predictions must not hide all evidence needed to interpret authorization. Context cannot be generated from model judgments or adapted to make predictions correct.

Keep seed labels, answer keys, detector scores/flags/thresholds, model output, other votes, train/validation/test assignments and prediction-dependent analysis outside the packet. Audit filenames, scenario names, file metadata and explanations for answer leakage. Current synthetic bundles are intentionally unblinded development tutorials, **not distributable independent annotation packets**. Neutral aliases must preserve a private bijection to manifest run/asset/epoch units; new aliases/bytes create a new version, not an unchanged historical capture. Do not rename development data into candidate evaluation or correct old clocks.

## Execution sequence — manual prerequisites, not an automatic pipeline

1. Obtain actual supervisor decisions and review the [capture checklist](RUNTIME_CAPTURE_ELIGIBILITY.md). All draft/pending gates stay pending; a draft is not collection/intervention permission.
2. Freeze the approved reviewer guideline file and exact SHA256, selected window size, evidence/context policy, run-family grouping, sample design, exclusion/unknown and analysis plan. Keep versions of every revision and why it changed. Hashing documents integrity, not approval.
3. Establish comparable authorized captures with sufficient reviewed identity/coverage/alignment evidence for the intended claim. Existing development/timing-rejected trials do not satisfy this. New experiments require their own reviewed scope and any applicable explicit operational approval.
4. Build a neutral packet and private [case/exclusion ledger](templates/runtime-case-ledger.md), audit leakage, assign the same observed units independently to two actual humans. Do not generate or prefill their votes. Keep consent/conflict/blinding records separate from the research dataset.
5. Obtain and hash each original review. Existing JSON contract: schema_version/runtime_review_v1, reviewer_id, origin, guidelines_sha256, blinded and labels; each label has run_id/asset_id/start_epoch/label/reason. IDs follow ASCII/length rules, exact integer epochs, known label enum, complete observed-window coverage. Current tool checks declarations, not actual humans.
6. Compute/report original agreement and unknown counts before discussion. Current intake provides known agreement fraction only; other reliability statistics need a separately reviewed implementation/analysis plan, not fabricated results.
7. If needed, save separate [adjudication JSON](templates/runtime-adjudication.json.example) binding both original review hashes and approved guideline hash. Resolve uncertainty with reasons or retain unknown. Known agreements cannot be silently flipped; use explicit reannotation/versioning for a discovered shared error.
8. Assemble an authorized local intake bundle using existing role-relative paths and byte limits. A fresh report outside it may check artifact/selected-source consistency. It never flips evaluation_eligible, independent_evaluation_verified or model_fitting_authorized true. No new ready-for-training authority exists in this pack.
9. Before actual evaluation/fitting, review all gates and freeze untouched grouped test data, model/features/calibration/analysis/exclusion rules and software versions. Never fit on hidden test labels or derive labels from system predictions. Record misses, false alarms, abstentions and unknown coverage, not just favorable cases.

## Templates and compatibility

The implemented [coordinator unit index](RUNTIME_ANNOTATION_INDEX.md) can list exact observed run/asset/epoch keys from a consistent offline bundle without generating votes. It validates supplied reviews if present, but exports neither votes nor review metadata. IDs/epochs/hashes may reveal/link scenarios: **not a blinded packet**. Do not distribute it as one or treat indexing a draft as approval; actual neutralization/context/exposure audit and human decisions remain required. This safe offline aid does not perform the execution sequence or satisfy its gates.

The review and adjudication files use .json.example and intentionally invalid placeholders/null fields, so they cannot be mistaken for completed submissions. The runtime path contract expects .json inside labels, not .json.example. Only actual authorized humans may fill independent votes/blinding declarations into separate private files after approval. No template is an existing reviewer result or an executable automated workflow. Eligibility/approval/ledger Markdown is manual governance and is **not parsed by runtime_intake**.

For exact implemented schemas use [intake](RUNTIME_INTAKE.md) and [selected receipts](RUNTIME_RECEIPTS.md). Guidelines and checklist propose research acceptance; they do not relax the implementation's no-eligibility defaults. All historical source/results and algorithms stay unchanged.

## Current unresolved gates

No supervisor sign-off or actual blinded submissions; no independent held-out runtime data; capture coverage and collector/harness timing stability unresolved; selected identity snapshots are not full deployment attestation; planned ML/overhead/integration remain open. Software tests and zero drop counters cannot resolve these by themselves. Next action is actual human scope approval; safe offline tooling/checklist verification can continue without fabricating it.
