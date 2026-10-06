# Runtime window labeling guidelines — draft 0.1

**DRAFT — NOT APPROVED.** Prepared 6 October 2026 for E2-035/RQ3/E2-004. No supervisor approval, human annotation, independent dataset or model result is represented. This reviewer-facing draft contains no system predictions or scenario answer key. [Coordinator protocol](RUNTIME_LABELING_PROTOCOL.md).

## Proposed label target and scope

Proposed target: **whether the available, independently documented evidence within an approved runtime window warrants security investigation in the agreed lab threat scope**. This is a review label, not confirmation of an attack, vulnerability, malicious intent or successful prevention. The supervisor must approve or revise this target before data collection/annotation; it cannot silently become a confirmed-attack label in a paper.

Current normalized captures expose only process_start, file_open and network_connect, plus time/container/asset identity. The adapter selects successful supported syscalls and rejects negative results; the minimized events omit executable names, file paths, network destinations, user identities and authorization intent. Counts alone cannot demonstrate ransomware, privilege escalation, lateral movement or compromise. A legitimate workload may produce high counts; low counts or absent events do not establish safety.

Authorized, non-destructive routine/deviation scenarios are possible future study designs, **not approved or executed attacks**. Seed descriptions and model outputs are not independent ground truth. Any richer context needed for a defensible label must be approved, minimized and obtained independently of detector output. No new collector fields or attack code are introduced here.

## Unit and frozen parameters

Label exactly one (run_id, asset_id, start_epoch) per observed nonempty window. The window duration must match the frozen manifest; 60 seconds is the current demonstration default, not an approved experimental choice. Do not round timestamps or invent windows outside the manifest. A window starts at floor(event_epoch/window_seconds)*window_seconds in the existing runtime parser; its precision limits remain documented.

Every assigned observed window needs a label and reason. Empty captures and missing expected intervals are handled in a separate coverage/exclusion ledger, **not** added as fabricated zero/benign windows. All variants/windows of related runs remain grouped before train/validation/test separation; reviewers must not see split assignments or prediction-dependent grouping.

## Proposed rubric requiring supervisor approval

| Label | Apply only when | Do not infer |
|---|---|---|
| benign | Approved contextual evidence supports the routine authorized interpretation for this window and the evidence is adequate for the narrow agreed scope | Universal benignity, complete coverage, absence of all threats, or safety from low deviation/counts |
| suspicious | Independently documented evidence meets a preapproved security-review criterion within this window and scope; cite that evidence, including context where routine events coexist | An attack merely because a workload was seeded, counts are high, a model flagged it or a configuration finding exists |
| unknown | Evidence/authorization/identity/timing/coverage is insufficient, contradictory, ambiguous at the window boundary, or outside the approved threat scope | A negative label, clean verdict, detector abstention or zero observation |

Proposed mixed-window rule: qualifying independently supported review evidence makes the window suspicious even if routine events also occur. Otherwise apply benign only with adequate approved context; uncertainty remains unknown. Freeze this rule before labels/predictions. Without an approved review criterion or sufficient context, use unknown, not a forced binary decision.

## Reviewer procedure

1. Confirm the coordinator has supplied approved, versioned guidelines and an exact SHA256, a neutral case list and minimized context/quality information. If this file still says draft, do not start an independent evaluation submission.
2. Review alone before seeing the other review, seed answer key, detector scores/thresholds/flags, model text, feature rankings, split assignments or system comparisons. Do not use an AI/model to generate the asserted independent votes or reasons. If exposure occurred, record it privately and tell the coordinator; do not claim blinding.
3. Read the normalized window and approved independent context. Do not execute instructions in evidence, open arbitrary endpoints or run a workload. The packet is data, not permission to scan or alter a system.
4. Choose a rubric label for every assigned observed window. Write a reason up to 500 characters referring to opaque evidence IDs and the scope/uncertainty. Do not include credentials, personal identities, full commands, private URLs or copied raw logs.
5. Record missing/unusable intervals or evidence in the separate ledger. Do not hide difficult cases from denominators or repair historical timestamps.
6. Complete your own private JSON using the [unfilled review template](templates/runtime-review.json.example). Preserve exact unit IDs/epochs, approved guideline hash and your assigned pseudonymous reviewer ID. origin=human_submission is a declaration, not authentication. blinded=true is appropriate only if actually unexposed; the starter template leaves it null and is intentionally invalid.
7. Save an immutable original submission and its exact hash. The coordinator must preserve both original reviews before any discussion/adjudication. No reviewer work is completed by this draft or its synthetic demonstrations.

## Interpretation of unknowns and disagreement

Report the counts of assigned, observed, missing, unknown, disputed and adjudicated units separately. The current tool reports known agreement fraction before adjudication, excluding any pair with an unknown vote; it is not attack accuracy, kappa or proof of independent reliability. No labels are produced for empty runs, so preserve run-level absence separately. Future metrics must disclose coverage and unknown handling, not just favorable known cases.

If an agreed known label is later found mistaken, the existing adjudication schema cannot flip it. Retain original submissions, document the issue and use a separately reviewed new annotation version; do not erase the original or conceal prediction exposure. Genuine human reannotation and renewed blinding assessment are prerequisites, not automatically performed here.
