# Engine2 research-data intake — next planned task (E2-035)

Status 6 October 2026: **planned protocol/deliverable**, not implemented intake tooling, new collection, reviewer recruitment, model fitting or independent results. This extends the runtime run/window and two-reviewer requirements in [EXPERIMENT_PROTOCOL](EXPERIMENT_PROTOCOL.md), while preserving the existing baseline and unresolved timing/coverage/identity gates. [Current status](CURRENT_STATUS.md).

## Research connection

RQ3 asks what value and overhead runtime evidence adds to cloud OSS security review. A syscall-count deviation is not an independently labeled attack; a successful dummy recovery test is not a detector benchmark. Next work should make eligible data/labels/splits traceable before comparing the existing statistical baseline with the planned Isolation Forest/autoencoder. No new engine/stack or automatic cloud action.

## Next implementation acceptance

Build an offline intake validator and report, reusing existing normalized-capture/inventory parsing where suitable. It must perform no collection, network access, service control, model fitting or predictions. Start with synthetic fixtures solely to test the validator; real eligibility remains separate.

| Required declaration/artifact | Intake check and interpretation |
|---|---|
| Run/capture/asset/window identity and normalized capture SHA256 | Bind exact bytes and existing schema; reject duplicate IDs/unbound assets, preserve empty/missing windows as unknown |
| Scenario/template/deployment/run group and declared split | Keep related windows/variants together across train/validation/test; reject declared group crossings and exact event reuse. Names alone do not prove independent groups |
| Data role/source | Distinguish development/synthetic/prior exploratory from candidate evaluation; never automatically promote historical tuned data |
| Collection/accounting/identity/timing references | Bind supplied reviewed receipt hashes; absent/rejected/incompatible evidence blocks real eligibility, never rename a failed trial as accepted |
| Labeling guidelines/version/hash and window label unit | Freeze meaning of benign/seeded suspicious/unknown; seed specification is not human ground truth |
| Two separate blinded reviewer submissions | Preserve each original vote/reason/hash; distinct supplied IDs and “blinded” flags are declarations, not identity/independence attestation |
| Adjudication and exclusions | Preserve disagreement/pre-adjudication agreement, resolution/reason/unknowns; report all exclusions rather than dropping difficult cases from denominators |

The future validator may establish **artifact/schema consistency**, not authenticate humans/hosts, certify benignity, prove timing stability, guarantee all template leakage absent or grant independent evaluation status. No true “independent_evaluation_verified” flag merely from metadata. Final naming/schema/CLI must be documented and tested when implemented; this table is not an existing API.

## Human and experiment gates

Actual professor/reviewer agreement on labels/threat scope and independently completed blinded annotation remain human prerequisites. No generated labels may impersonate that work. Public/external data need primary source/license/provenance review and applicability to the lab, not blind downloading. No source chosen/imported here.

The existing preserved captures are development/exploratory evidence, not a valid matched benign/attack held-out set. Earlier timing failures and partial coverage remain visible. Stable comparable collection must be established before real timing/detection/overhead evaluation; this plan does not authorize new sensor/service/clock experiments or adjust historical timestamps.

After intake and eligible data exist: freeze grouped splits/guidelines/features, train/calibrate only development/training partitions, compare statistical baseline and planned models on the untouched grouped test set, report failures/abstentions/FN/FP and uncertainty. Fit/score/threshold/overhead commands are future tasks, not performed here. Engine1/runtime integration and response are separate later acceptance gates.

## Reviewer checklist for the next change

- Are manifest paths/byte limits/duplicate JSON handling and hashes bounded, with no untrusted-data command execution?
- Are run/template/deployment groups and exact duplicates refused across partitions without claiming complete semantic deduplication?
- Are unknown labels/coverage/timing and missing receipts visible, not converted to normal/zero?
- Are all existing development/negative receipts preserved, and independent human work distinguished from supplied declarations?
- Are synthetic software cases reported as software tests, with no benchmark/model/collection claim?
- Are CURRENT_STATUS/MEMORY/TASKS/WORK_LOG/CHANGELOG and relevant architecture/security/test documents updated in the same coherent commit?
