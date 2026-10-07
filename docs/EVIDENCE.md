# Evidence index

## Existing pipeline/runtime integration (2026-10-07)

E2-042: [contract/commands](PIPELINE_RUNTIME_INTEGRATION.md),28newcases/target114pass2.31s/XML2.234. [Windows](../output/pipeline-integration-full-windows-tests-20261007.xml)1268pass38skip26.85s/XML26.847; [Linux](../output/pipeline-integration-full-linux-tests-20261007.xml)1306pass111.65s/XML108.127,1306collected both/0failures/errors. Lint123fileformat/bothpipchecks pass. Actual [Windows](../output/pipeline-integration-synthetic-windows-20261007.json)/[Linux](../output/pipeline-integration-synthetic-linux-20261007.json) examples8checks each/fullresult hashes equal after platformfile/stage-timings exclusion; actual retrieval/scoring, no model/TCP calls. Model/probe/review/vector paths mocked; software integration not independently evaluated detection. Historical default report equality/old negative hashes preserved. WL-073.

## Integrated configuration/runtime replay (2026-10-07)

E2-041/R6/RQ3: [contract/commands](INTEGRATED_REPLAY.md),34newcases/target149pass1deselected2.04s/XML1.897; [Windows full](../output/integration-full-windows-tests-20261007.xml)1240pass38skip29.03s/XML29.021, [Linux full](../output/integration-full-linux-tests-20261007.xml)1278pass104.13s/XML100.897,1278collected both/zero failures/errors. Lint122fileformat/bothpipchecks pass. Actual [Windows](../output/integration-synthetic-windows-20261007.json)/[Linux](../output/integration-synthetic-linux-20261007.json) fixed demos all6checks; full result equality excluding only platform-specific engine1.file, all hashes/launcher/checks agree. Components/context software evidence, no independent threat/calibrated fusion or research approval. Pending scanner commit/push a555b32 verified; WL-070.

## Compose parser refinement (2026-10-07)

QA-002/M3-004: [contract and commands](COMPOSE_ENVIRONMENT_VALIDATION.md),15new cases. Beforefix12fail/1pass; first-fix location regression1failure on each platform preserved. Final Windows1206pass38skip22.28s/XML22.280; Linux1244pass109.00s;1244collected each,zero failures/errors. Lint119fileformat/bothpipchecks passed. This validates selected parser/CLI behavior and regression compatibility; independent research gates remain open. WL-069/INC-061/062/ADR-059.

## Bounded import observation / current-memory maintenance (2026-10-07)

[Post-edit document contracts](../output/engine2-current-memory-docs-tests-20261007.xml):18pass0.22s/XML0.134/no failures/errors/skips, separate subset. No new executable/tests/full-suite measurement; current full-suite remains1226cases at prior software milestone.

[One-off Windows import observation](BACKEND_IMPORT_OBSERVATION_20261007.md):4planned/launched/0unlaunched fresh processes, IF→AE/AE→IF twice each, all imported with Python3.12.14/pinnedsklearn1.9.1 and existing seven-package versions.30sper-childtimeout/stoponfirstfailure; no fitting/install/cache purge/service/clock/telemetry/action. Manually transcribed Markdown with exact executed stdin command; consoleJSON not saved as a generated report, no timing/pressure/native-fault reproduction/causal-fix claim or future monitoring. INC-056 originalfailedXML SHA cdbbb46f11703516e63b180b26115ac5d66cd30184b600bee5eff89bbfec5571 unchanged.

DOC-006 [historical MEMORY snapshot](MEMORY_HISTORY_20261007.md) equals previous committed docs/MEMORY.md byte-for-byte,56,968bytes/SHA4e51af83e38e11bb9347eb3e1f27d59440d67397417a18e12096fcea2ba89c9a. Same directory preserves relative links; new MEMORY.md is current summary, not deletion/reinterpretation of old evidence. No new source/test/capture or full-suite run; WL-067 documents verification/publication, ADR-057/INC-058.

## Optional backend diagnostic refinement (2026-10-07)

[Post-document contracts](../output/engine2-backend-diagnostic-docs-tests-20261007.xml)18pass0.24s/XML0.104/no failures/errors/skips, separate rerun not new full-suite cases or human approval. LinuxfullXMLtime83.577s versus86.58s console, not clock/engine-performance interpretation.

[Contract](RUNTIME_ML_BACKEND_DIAGNOSTICS.md), E2-040/WL-066/ADR-056: original INC-056raw failure still SHA cdbbb46f11703516e63b180b26115ac5d66cd30184b600bee5eff89bbfec5571/causeunknown. Current directbackend imports/pin/pipcheck pass. [New injected pre-fix negative](../output/engine2-backend-diagnostic-negative-windows-20261007.xml)8failed0.22s/XML0.092, SHA fc0568281994893e9d33cf84c158d9b74d699c3c50670cf71f8dcee053a62d6b: category absent under both existing adapters, **not nativefault reproduction**. INC-057reportinggap reproduced/fixed, no dependency reinstall or invented cause.

[Initialtarget](../output/engine2-backend-diagnostic-target-windows-20261007.xml)105pass5.50s/XML5.498/[expanded](../output/engine2-backend-diagnostic-target-final-windows-20261007.xml)129pass5.43s/XML5.427/[verified](../output/engine2-backend-diagnostic-target-verified-windows-20261007.xml)129pass5.51s/XML5.504.32newcases, including6injected CLI cases; temporary fault receipts not published as observed native failures. [Windowsfull](../output/engine2-backend-diagnostic-windows-tests-20261007.xml)1188pass38skips22.74s/XML22.736/[Linuxfull](../output/engine2-backend-diagnostic-linux-tests-20261007.xml)1226pass86.58s,1226collected each/0failures/errors, lint119fileformat/bothpipchecks pass. Success calculations/currentmodelboundaries unchanged; no independent detector/clock/performance evidence. Historical model-source digests stay original despite selected source changes.

## Synthetic decision-accounting software (2026-10-07)

[Post-document contracts](../output/engine2-accounting-docs-tests-20261007.xml)18passed0.15s/XML0.106/no failures/errors/skips, separate rerun not added cases or approval of the draft research plan.

[Linux full](../output/engine2-accounting-linux-tests-20261007.xml)1,194passed140.05s/XML137.061/no skips; [separate final Windows](../output/engine2-accounting-windows-final-tests-20261007.xml)1,156passed38skips27.83s/XML27.819,1194collected each/zero failures/errors in those runs. Lint/118fileformat/bothpipchecks pass. FirstWindowsnegative/diagnostic below retained, not root-cause resolution; suite durations not detector efficiency/overhead or clock validation.

[Contract](SYNTHETIC_RUNTIME_ACCOUNTING.md), E2-039/WL-065/ADR-055: [fixed Windows](../output/engine2-accounting-windows-20261007.json)/[Linux](../output/engine2-accounting-linux-20261007.json), all6checks/equal complete result/check objects,11invented slots/9observed1missing1unusable; conditionalconfusion each1, positive/negative abstention each1, conditionalrecall1/2/inclusivepositive1/3. Not actual model predictions or research accuracy. RawinputSHAe234d8d78a696aca6c2156396e046142581cbc713e0ab9132e9be6acb2286a53; canonicalJSON095c3a6b56a941e0b6745cd814a7d75283ff595e452a077095470a405f0ba7b6; selectedlibrary8f89a63e9101bbe3dd917459994f1d22431ec01fa7a15589d61141002ec7bc39. Exact file/source bindings verified, not full environment attestation or original-file canonical equality.

[Initial target](../output/engine2-accounting-target-windows-20261007.xml)34pass0.56s/XML0.502/[final target](../output/engine2-accounting-target-final-windows-20261007.xml)46pass0.40s/XML0.352. [First Windows full](../output/engine2-accounting-windows-tests-20261007.xml)1failed1,155pass38skips54.54s/XML54.528,1194collected; existing IFoptional-backend import failure, rawSHAcdbbb46f11703516e63b180b26115ac5d66cd30184b600bee5eff89bbfec5571 (INC-056). [Diagnostic failedcase+accounting](../output/engine2-accounting-import-check-windows-20261007.xml)47pass1.42s/XML1.416; direct optionalimport and pipcheckpass, cause not established/no dependency or old production fix. Raw failure retained; passing later checks cannot erase it.

## Existing runtime data audit / supervisor proposal (2026-10-06)

Final post-document [publication/research-pack contracts](../output/engine2-data-readiness-docs-tests-20261006.xml):18pass0.26s/XML0.119, zero failures/errors/skips. Separate rerun, not additional full-suite cases or actual proposal approval.

[Readiness audit](RUNTIME_DATA_READINESS_AUDIT.md), E2-038/E2-035/RQ3: read-only seven-capture parser/count/hash/HEAD checks (5synthetic/2sensor-development;380stored event rows/45per-file60swindow records, not independent samples), exact two-projection reuse rejected by existing analyze guard, same sensor development group, failed3trial manifest/all3receipt hashes retained and trial3localclocktrue/4collector exclusions. Audit contains actual source hashes and exact executed stdin command; console assertions were not separately saved as a generated artifact. No raw export re-normalization/eligibility/approval/authentication/independent labels/new experiment/model operation. INC-055 preserves reuse risk without claiming executed split contamination.

[Windows existing-test subset](../output/engine2-data-readiness-target-windows-20261006.xml)208pass1symlink-privilege skip6.69s/XML6.549; [Linux subset](../output/engine2-data-readiness-target-linux-20261006.xml)209pass43.77s/XML42.210,209collected each/0failures/errors. No new executable/tests; whole-suite1148case checkpoint below unchanged/not rerun. [Supervisor-ready proposal](ENGINE2_SUPERVISOR_REVIEW_PROPOSAL.md) DOC-005 is prepared DRAFT — NOT APPROVED, following user's explicit lack of approval; no independent reviewer decision or research result is represented. WL-064/ADR-054 cover scope/verification/publication.

## Synthetic reconstruction autoencoder software (2026-10-06)

After Markdown updates, [publication/research-pack contract tests](../output/engine2-autoencoder-docs-tests-20261006.xml)18passed0.14s, zero failure/error/skip; full-suite totals below are not increased by this separate rerun. Repository publication checker run again against final staging; WL-063 records actual review.

[Contract](SYNTHETIC_RUNTIME_AUTOENCODER.md), E2-037/WL-063/ADR-053. Final [Windows demo](../output/engine2-autoencoder-windows-verified-20261006.json) SHA d8d3afb445699a0d603bcdbc42edbec377d594d58885dc3be259fc5913b23e48 / [Linux demo](../output/engine2-autoencoder-linux-verified-20261006.json) SHA 55e5a9a3961eba11dd57aac43f04bac2bba466ec1b4507d1650133f54b730cf6. Fixed32invented training windows/3observations, baseline-only scaling/reconstruction,20iterations/no warnings/all6checks/3scored0abstained. Computed reconstruction MSE retained, no threshold/binary threat labels/real authority/actions. Software evidence only.

[IF refactor compatibility target](../output/engine2-autoencoder-iforest-compat-tests-20261006.xml)47pass10.33s/XML10.329; [initial combined target](../output/engine2-autoencoder-target-tests-20261006.xml)90pass8.59s/XML8.588 (Ruff still failed17fixture-import/shadowing diagnostics, INC-053); [expanded target](../output/engine2-autoencoder-target-final-tests-20261006.xml)96pass21.32s/XML21.308. [Precision regression](../output/engine2-autoencoder-target-precision-tests-20261006.xml)2failed95pass15.05s/XML15.040, SHA e408f0ad53458ef7ef924d73a0c1d91349125b2d3a7b817dc3c7b69ba84d34fb, INC-054. [Final verified target](../output/engine2-autoencoder-target-verified-tests-20261006.xml)97pass14.34s/XML14.331. [Windows full XML](../output/engine2-autoencoder-windows-tests-20261006.xml)1,110pass38skips66.63s/XML66.602/[Linux full XML](../output/engine2-autoencoder-linux-tests-20261006.xml)1,148pass245.99s/XML241.721, both1,148collected/0failures/errors. Lint/format115files/bothpipchecks pass. Suite timing is not engine performance or host-clock validation.

[Deliberate one-iteration negative](../output/engine2-autoencoder-one-iteration-20261006.json), SHA a9a8792f13a7fd5f52c010fb707385b657085fba2a0359b57250bc6161a2f102: exit1/synthetic_check_failed,1training iteration/1convergence warning, actual fitting attempted, no reconstruction attempt,0scored3abstained. Retained negative, not an unexpected execution bug or confirmed clean verdict.

[Initial Windows demo](../output/engine2-autoencoder-windows-20261006.json), [expanded demo](../output/engine2-autoencoder-windows-final-20261006.json) and [pre-fix demo named precision](../output/engine2-autoencoder-windows-precision-20261006.json) passed smoke checks but rounded scores; they are historical, not final precision evidence. Filenames containing “final”/“precision” do not override actual result/source revision. Their selected source hashes refer to uncommitted development states not separately archived as full source; no full pre-fix replayability claim. Original XML/JSON bytes retained; final source/receipts committed together. Both optional methods implemented software, real research gates still open.

## Optional synthetic Isolation Forest software (2026-10-06)

[Contract](SYNTHETIC_RUNTIME_ML.md), [final Windows demo](../output/engine2-synthetic-iforest-windows-final-20261006.json) SHAb39476763ea5acdaee9c0594c5aab0828e423da044f1c3809f1ada50d9beefbc/[final Linux demo](../output/engine2-synthetic-iforest-linux-final-20261006.json) SHA1b489feed51803badac8fd575aa0c9359090cc141f9def4b20216ec8776a537b: actual32invented baseline windows/3observations, synthetic ephemeral fit, all6checks/same3scores/3scored0abstained; no binary ML labels/threat/real approval/actions. [Final target](../output/engine2-synthetic-iforest-target-final-fixed-tests-20261006.xml)47pass, [Windows](../output/engine2-synthetic-iforest-windows-final-tests-20261006.xml)1,060pass38skips/[Linux](../output/engine2-synthetic-iforest-linux-final-tests-20261006.xml)1,098pass/zero failures/errors. Software evidence, not independent evaluation.

INC-051 [initial assertion](../output/engine2-synthetic-iforest-target-tests-20261006.xml)43pass1fail SHAfd430b85a8dab3e2c37a68db4fe9bee70345cdc2a9eed7fba7daabffd608731a/[collection error](../output/engine2-synthetic-iforest-target-final-tests-20261006.xml)1error SHAf31d254596821edd1f0f8e7735b8280e409c2a5b5bd0979d908b4c15a20bff01; [subsequent46pass target](../output/engine2-synthetic-iforest-target-verified-tests-20261006.xml). INC-052 [all-abstention regression](../output/engine2-synthetic-iforest-abstention-regression-20261006.xml)2fail1pass43deselected SHAc1a5b6a81855db3dd458bf3044bead7dd98081cca98891e06c3a865d754c5282. Preliminary [Windows](../output/engine2-synthetic-iforest-windows-tests-20261006.xml)/[Linux](../output/engine2-synthetic-iforest-linux-tests-20261006.xml)1,097collected and [Windows](../output/engine2-synthetic-iforest-windows-20261006.json)/[Linux](../output/engine2-synthetic-iforest-linux-20261006.json) demonstrations kept byte-exact, not final abstention coverage. WL-062 commands/limits; original default replay remains exactly equal to saved historical result.

## Coordinator observed-unit export (2026-10-06)

[Contract](RUNTIME_ANNOTATION_INDEX.md), [synthetic3unit index](../output/engine2-annotation-index-synthetic-20261006.json) SHA86bbc98f411ba315c3ba2175ecfb4879c5ecad42ce05a5276ce0922bf411a4fa. No labels/approval/blinding/fitting/predictions/actions. [Final target](../output/engine2-annotation-index-target-final-tests-20261006.xml)181pass1skip; [Windows](../output/engine2-annotation-index-windows-tests-20261006.xml)1,013pass38skips/[Linux](../output/engine2-annotation-index-linux-tests-20261006.xml)1,051pass/0failures/errors.22new software cases, not independent human/attack data. [Initial failed XML](../output/engine2-annotation-index-target-tests-20261006.xml) INC-0501failure180pass1skip, SHA6a4c8a284ea316567998020c25f681a2bfe1b789c2887d3071304e89523eae43: test updated wrong capture ref, existing guard rejected; test-only ordering fix. Old v1/count example/count-negative hashes re-read unchanged, equality regressions pass. WL-061/ADR-051. No live experiment or research-gate completion.

## Draft review pack and software/publication checks (2026-10-06)

[Coordinator pack](RUNTIME_LABELING_PROTOCOL.md), [reviewer guidelines](RUNTIME_LABELING_GUIDELINES.md), [capture checklist](RUNTIME_CAPTURE_ELIGIBILITY.md), four unfilled templates: prepared **not approved**, not human reviews/independent data. [Target XML](../output/engine2-research-pack-target-tests-20261006.xml)18pass; [Windows XML](../output/engine2-research-pack-windows-tests-20261006.xml)991pass38skips; [Linux XML](../output/engine2-research-pack-linux-tests-20261006.xml)1,029pass; zero failures/errors, software evidence only. Private reserved folder ignored/publication-excluded, no actual records created. WL-060 exact commands/limitations; ADR-050 proposed target not confirmed attack or approval. Original count-negative SHA c771cebc2353d935fa1e7edcf04e401a085be0f152950d1d3cd98f6f1da5f53c, initial-host negative SHA c457628fb1078177626e2e17324828602bdd3918cc3af3091317eaaf1272f959 and final counted synthetic SHA6def16b58710150349d36849fc7b6009016e1503c2efd801edf0390b2586292b re-read unchanged. No new observations/labels/model results.

## Selected typed-source consistency and preserved count defect (2026-10-06)

[Contract](RUNTIME_RECEIPTS.md), [final counted example](../output/engine2-typed-intake-counted-synthetic-20261006.json), [preserved uncounted input rejected](../output/engine2-typed-intake-uncounted-rejected-20261006.json), [final Windows XML](../output/engine2-typed-intake-windows-final-tests-20261006.xml), [final Linux XML](../output/engine2-typed-intake-linux-final-tests-20261006.xml).77new cases, finalWindows976pass38skips/Linux1,014pass/zero failures/errors. Selected source/count/snapshot/local-endpoint checks only; all full coverage/alignment/authenticity/eligibility/fitting/action flags false, no reviewers/new real data. [Raw three-failure regression XML](../output/engine2-typed-intake-count-regression-20261006.xml) INC-049, SHA c771cebc2353d935fa1e7edcf04e401a085be0f152950d1d3cd98f6f1da5f53c; actual fix cross-checks trial totals/exact kinds. [Pre-fix example](../output/engine2-typed-intake-synthetic-20261006.json), uncounted source/wrapper/manifest and initial target/preliminary full XMLs retained, not final success. Existing80-event accounting and four-exclusion historical trial tested offline, no new observation/repaired clock claim. Original v1 report exactly unchanged; WL-059 commands/limitations.

## Offline research intake consistency (2026-10-06)

[Contract](RUNTIME_INTAKE.md), [synthetic example](../data/runtime/intake-example/README.md), [executed report](../output/engine2-intake-synthetic-20261006.json), [Windows XML](../output/engine2-intake-windows-tests-20261006.xml), [Linux XML](../output/engine2-intake-linux-tests-20261006.xml).83new synthetic cases; fullWindows899pass38skips/Linux937pass, zero failures/errors. Three fixture windows:1known agreement/1disagreement/1unknown pair, adjudication1benign2unknown. All independence/eligibility/receipt-semantics/fitting/action gates false, no actual human labels/new independent data. [Original failing host XML](../output/engine2-intake-initial-host-tests-20261006.xml) and [manual sandbox context](../output/engine2-intake-sandbox-attempt-20261006.json) retained, INC-048/WL-058. Software/intake evidence, not detector evaluation/complete coverage/stable timing. Old artifacts unchanged; next semantic receipt and genuine human/data gates open.

## Implemented baseline versus research-scope reporting (2026-10-06)

[Current summary](CURRENT_STATUS.md), [Windows XML](../output/engine2-status-windows-tests-20261006.xml), [Linux XML](../output/engine2-status-linux-tests-20261006.xml), [new synthetic replay](../output/engine2-status-clarification-replay-20261006.json).3scope regressions/current CLI checks; Windows817pass37Linux-only skips/Linux854pass,0failures/errors. All old replay result fields identical apart from new implementation_scope/clarified limits. Actual four smoke checks true, explicitly synthetic/no live input/actions/threat/ML/independence. No historical data replaced, runtime detector effectiveness or independent dataset claimed. Planned next intake specification not execution/data evidence; INC-047 wording/confusion correction, not a new detector/model result.

## Inert durable job/gate validation (2026-10-06)

[Report](DURABLE_JOB_GATE.md), [Windows XML](../output/engine2-durable-job-windows-tests-20261006.xml), [Linux XML](../output/engine2-durable-job-linux-tests-20261006.xml), [before-fix negative XML](../output/engine2-durable-job-window-regression-20261006.xml).60new cases/four actual Linux inert process/lock checks. Windows814pass/37Linux-only skips; Linux851pass,0failures/errors. Negative one-case numeric1window failure preserved/fixed exactTrue (INC-046); other evidence synthetic supplied events/storage doubles, no real jobs/bus/clock/restoration/threat benchmark. Exclusive journal/reopen/sticky faults and cooperating-worker seal mechanics tested; native/quiescence/disarm authority false always, native integration incomplete. Historical reports/live receipts unchanged.

## Private native callback software validation (2026-10-06)

[Report](NATIVE_CALLBACK_VALIDATION.md), [Windows XML](../output/engine2-native-callback-windows-tests-20261006.xml), [Linux XML](../output/engine2-native-callback-linux-tests-20261006.xml).31new tests;28actual pinned Linux native message/C trampoline/read/copy/fault cases with synthetic data/private socketpair,3portable fixture guards. Linux791pass/Windows758pass33Linux-only skips, no failures/errors. Not a live broker-delivered event receipt, independent benchmark, real disconnect/job binding/quiescence/restoration or timing/ML evidence. No production-source change/retry/history replacement/real job or service action.

## One read-only native receiver setup observation (2026-10-06)

[Report](SYSTEMD_RECEIVER_CAPTURE.md), [actual start](../output/engine2-systemd-receiver-observation-20261006/started.json), [actual native result](../output/engine2-systemd-receiver-observation-20261006/result.json), [manual live context](../output/engine2-systemd-receiver-live-context-20261006.json). After authorized Desktop recovery/fresh successful gate, one native run50process calls/0selected events, epoch/Subscribe/Unsubscribe/close/source and child reaping checks pass. Offline selected schema/hash/serialization reproduced, no raw stdout retained/authentication claim. No native JobRemoved callback/fault/job-binding/time-service control/timing/ML proof; prior unavailable-engine summary and760case XML unchanged.

## Receiver precheck refusal, no native observation (2026-10-06)

[Result/protocol](SYSTEMD_RECEIVER_CAPTURE.md), [minimized manual summary](../output/engine2-systemd-receiver-precheck-20261006.json). Verified implementation commit/source hashes; service snapshot/timeout available but guest Docker mount/CLI target and verified local Windows engine pipe unavailable. Required named-sensor inventory unknown, native capture not launched; no subscription/job/service/Docker/settings/restart action. INC-045 preserves actual precheck failure; this is not a native receive receipt, sensor absence proof or timing/ML acceptance. Implementation760case XML unchanged.

## Exclusive receiver launcher software checks (2026-10-06)

[Protocol/report](SYSTEMD_RECEIVER_CAPTURE.md), [Windows755pass/5skips](../output/engine2-systemd-capture-windows-tests-20261006.xml), [Linux760pass](../output/engine2-systemd-capture-linux-tests-20261006.xml).34new cases, two actual inert Linux children and synthetic receipt/source/timeout/errno/alarm wiring checks; no native bus or service action. One read-only receive observation predeclared but pending at implementation checkpoint. Older726reports/native clock failures unchanged; no independent detection or job-fencing evidence.

## Read-only persistent receiver software checks (2026-10-06)

[Report](SYSTEMD_RECEIVER.md), [Windows723pass/3skips](../output/engine2-systemd-receiver-windows-tests-20261006.xml), [Linux726pass](../output/engine2-systemd-receiver-linux-tests-20261006.xml).54new synthetic/C-level tests, current actual selected ABI/library hash/export availability without connection. No native subscription/event/job evidence, service action or recovery authority; native reception and durable binding unfinished. INC-044 retains intermediate fixture failure; old672reports/native receipts unchanged.

## Systemd job schema review and offline contract (2026-10-06)

[Report](SYSTEMD_JOB_CONTRACT.md), [manual interface summary](../output/engine2-systemd-interface-review-20261006.json), [Windows669pass/3skips](../output/engine2-systemd-job-windows-tests-20261006.xml), [Linux672pass](../output/engine2-systemd-job-linux-tests-20261006.xml). Actual selected Manager Introspect signatures only; job examples synthetic, no Subscribe/control/native job completion.29additions/no disarm or service-quiescence authority; older643reports/native receipts unchanged.

## Isolated guest fence software/inert process checks (2026-10-06)

[Report](GUEST_FENCE_PROTOTYPE.md), [Windows640pass/3skips](../output/engine2-guest-fence-windows-tests-20261006.xml), [Linux643pass](../output/engine2-guest-fence-linux-tests-20261006.xml):33new cases, three Linux-only actual inert file/process integrations. Terminal seal blocks a queued cooperating worker; killed holder leaves submitted operation unknown. Detached job may still execute outside gate. No service/job/native integration or causal/stability/ML evidence; prior610reports/live receipts unchanged.

## Uncertain stop software regression (2026-10-06)

[Report](CLOCK_STOP_DELIVERY.md), [Windows610](../output/engine2-stop-delivery-windows-tests-20261006.xml), [Linux610](../output/engine2-stop-delivery-linux-tests-20261006.xml):14 additions, simulated delayed-stop and marker/cancel/IO cases plus existing explicitly inert lifecycle tests. Three before-fix assertion failures preserved in INC-043/report, not a live WSL race claimed. No real time-service action, native comparison, clock fix or guest-job fencing proof; historical596/live receipts unchanged.

## Preflight source freeze software checks (2026-10-06)

[Report](CLOCK_COMPARISON_PREFLIGHT.md), [Windows596](../output/engine2-preflight-freeze-windows-tests-20261006.xml), [Linux596](../output/engine2-preflight-freeze-linux-tests-20261006.xml):15 new static-closure/dependency-change/order/missing-source regressions. Simulated service operations and existing real inert helper tests only; no native comparison. INC-042 records coverage gap, sandbox WSL refusal retained in report/work log. Prior581 reports/negative observations unchanged; late-request safety/protocol/consent gates open.

## Transport/helper software and inert lifecycle checks (2026-10-06)

[Report](CLOCK_COMPARISON_TRANSPORT.md), [Windows581](../output/engine2-comparison-transport-windows-tests-20261006.xml), [Linux581](../output/engine2-comparison-transport-linux-tests-20261006.xml):30 additions, mocked native service/WSL operations and real explicitly inert process parent-kill/cancel tests. INC-040/041 retain setup/launcher/job failures and host retry context. Concrete backend exists but no native service trial/clock comparison/causal fix; approval/protocol/native safety gates pending. Old551 suite/live receipts preserved, no independent effectiveness claim.

## Comparison controller software milestone (2026-10-05)

[Implementation/limits](CLOCK_COMPARISON_CONTROLLER.md), [Windows551](../output/engine2-comparison-controller-windows-tests-20261005.xml), [Linux551](../output/engine2-comparison-controller-linux-tests-20261005.xml):47 additions use simulated service/watchdog operations and synthetic complete native receipts only. No native/service transport/real watchdog launcher or comparison experiment executed. Current observer sources and old evidence unchanged; actual approval/concrete safety integration pending, not cause/stability/ML evidence.

## Synchronization writer review (2026-10-05)

[Minimized sequential facts/source hashes](../output/engine2-sync-writer-review-20261005.json), [review/proposed comparison](SYNC_WRITER_REVIEW.md). Actual selected service/drop-in/backend/process-name context and four reviewed official file hashes, not simultaneous trial/syscall trace/binary attestation or exhaustive absence. Residual tick/frequency and incomplete caller visibility limit “single authority” interpretation. No new clock observation/intervention; current504-test evidence historical, no causal/stability/ML acceptance.

## Live kernel-state observation (2026-10-05)

[Receipt](../output/engine2-kernel-clock-state-20261005.json), [offline review](../output/engine2-kernel-clock-state-review-20261005.json), [protocol/result](KERNEL_CLOCK_STATE.md): one16-packet/32-query run, six sources/libc continuity/domains/bounds/summary reproduced; SHA834018876154de8a435048b88d063996ecaab029321bb563242ad6fa84ea13cf. Tick/frequency changes directly sampled with RAW/MONO gap~0.46324s and wall/BOOT change~0.867156s. INC-039, TIME_OK not stable-clock/cause/ML acceptance. No intervention/retry/source change since504 suites; old receipt hashes unchanged. Offline arithmetic is local consistency, not independent scientific evaluation.

## Live kernel-state implementation (2026-10-05)

Software: [Windows504](../output/engine2-kernel-state-windows-tests-20261005.xml), [final Linux504](../output/engine2-kernel-state-linux-final-tests-20261005.xml), [earlier Linux504](../output/engine2-kernel-state-linux-tests-20261005.xml). Thirty-six additions; lint/format83files/dependency pass. Initial unused import corrected after first Linux run, original receipt not overwritten. No live state queried by tests.

[Protocol](KERNEL_CLOCK_STATE.md): separate zero-mode ordinary-user query/native-pair observer with complete offline reduction;36 targeted tests pass using injected state/backends only. INC-038 preserves initial two test-double failures. One sensor-free live observation pending after publication; no clock changes, causal/stability/ML evidence.

## Raw-versus-adjusted observation (2026-10-05)

[Receipt](../output/engine2-raw-clock-lineage-20261005.json), [offline review](../output/engine2-raw-clock-lineage-review-20261005.json), [protocol/result/provider context](CLOCK_PROVIDER_REVIEW.md). One sixteen-packet run: RAW-host15/15 compatible, adjusted11/15 discrepant, local RAW/MONO final gap~0.5674s and wall/BOOT change~0.3167s. Four sources/all sample/domain/gap/gate/summary checks reproduced; SHA70fff0419aa8bb6d42e9ab460bf0ae32162bcea3eb78102d85869c46f89dfe0a. INC-037, not attributed cause/absolute accuracy/stability/ML evidence. No changes/intervention/retry or source change since468 suites; old receipts unchanged.

## Clock-provider facts and raw protocol (2026-10-05)

[Minimized manually transcribed facts/commands](../output/engine2-clock-provider-facts-20261005.json), [review and raw protocol](CLOCK_PROVIDER_REVIEW.md). Sequential point-in-time tsc/alternatives, implicit/guest sync states, versions/minimized host hypervisor/services; no simultaneous attribution or authenticated clock accuracy. Frequency is cached in reviewed upstream source, not live timex. Raw trial pending at implementation checkpoint; old negative receipts unchanged.

Software [Windows](../output/engine2-raw-lineage-windows-tests-20261005.xml) / [Linux](../output/engine2-raw-lineage-linux-tests-20261005.xml):468 each, thirteen additions. Synthetic raw difference is not a reproduced runtime cause; no independent evaluation.

## Sensor-free Windows/WSL lineage observation (2026-10-05)

[Receipt](../output/engine2-clock-lineage-20261005.json), [offline review](../output/engine2-clock-lineage-review-20261005.json), [protocol/result](CLOCK_LINEAGE.md). One sixteen-packet run; four sources/all native+host samples/domains/gaps/gates/intervals checked. 13/15 elapsed comparisons and14/16 wall offsets exclude zero; native relative changes sampled zero-compatible. SHA179ebdfa0f8b26a27ba0ed83b2a921b865f4438077567fe3f2e503cb38722710; local consistency, not independent clock accuracy/attestation or explained historical cause. INC-036. No settings/service/sensor/clock action/retry; known-sensor absence/preflight/active time service checked externally; no source change since455-test suites.

## Clock-lineage implementation checks (2026-10-05)

[Protocol](CLOCK_LINEAGE.md), [Windows suite](../output/engine2-clock-lineage-windows-tests-20261005.xml) / [Linux suite](../output/engine2-clock-lineage-linux-tests-20261005.xml): 455 each OS, 27 additions. Native bounds, fixed bridge, interval/strict-data/refusal/privacy/partial-receipt and offline-binding behavior tested. No live observation at implementation checkpoint; synthetic jump is not a reproduced historical incident. Existing failed receipts unchanged.

## Recorded collector-on follow-up (2026-10-05)

[Receipt](../output/engine2-recorded-boot-clock-20261005.json), [offline review](../output/engine2-recorded-boot-review-20261005.json), [metrics](../output/engine2-recorded-boot-metrics-20261005.json), [protocol/result](RECORDED_BOOT_CLOCK_FOLLOWUP.md). Four measured events, eight TIME reads and 27 native samples compatible in one new run; seven source/raw/response hashes/summaries/namespace facts checked. Metrics zero drops, unknown coverage. Exploratory prelaunch relationship difference +123.10316 s against original receipt; no cause/change time or long-term stability established. Failed history intact; no clock adjustments/correction/independent evaluation. Raw data retained locally/ignored; last software suite 428 each OS.

## Recorded boot/TIME implementation checks (2026-10-05)

[Protocol](RECORDED_BOOT_CLOCK_FOLLOWUP.md), [Windows](../output/engine2-recorded-boot-windows-tests-20261005.xml) / [Linux](../output/engine2-recorded-boot-linux-tests-20261005.xml): 428 each. Native TIME endpoint recording/rejected-clock preservation and diagnostic exclusion software-tested; no v2 collector-on observation at this checkpoint. Historical receipts unchanged.

## Sensor-free TIME observation (2026-10-05)

[Receipt](../output/engine2-sensor-free-time-attempts-20261005.json), [offline review](../output/engine2-sensor-free-time-review-20261005.json), [protocol/result/reproduction](SENSOR_FREE_TIME_ATTEMPTS.md). One run six accepted reads/five gaps, all offset bounds include zero; six source/response hashes and available math reproduced offline. No sensors/retries/clock changes, identity unchanged. Later bounded observation cannot identify historical rejected-read cause or verify Falco alignment; no accuracy/overhead/independent evaluation claim. Software unchanged from 421 tests each OS.

## Sensor-free attempt-mode implementation (2026-10-05)

[Protocol](SENSOR_FREE_TIME_ATTEMPTS.md), software [Windows](../output/engine2-sensor-free-attempts-windows-tests-20261005.xml) / [Linux](../output/engine2-sensor-free-attempts-linux-tests-20261005.xml): 421 each. Shared sanitized recorder/fixed-count and refusal behavior tested; one live diagnostic planned but not executed at this checkpoint. Existing negative results remain unchanged.

## TIME failure-recording software checks (2026-10-05)

[Windows](../output/engine2-time-failure-windows-tests-20261005.xml) / [Linux](../output/engine2-time-failure-linux-tests-20261005.xml): 414 each. Seven failure regressions retain sanitized samples/stages/rejection flags without raw replies/error details. This is software verification, not a new live result or retrospective repair of E2-019. INC-033 / [diagnostic recording contract](CLOCK_DOMAINS.md).

## Incomplete boot-clock attempt (2026-10-05)

[Failed receipt](../output/engine2-boot-clock-20261005.json), [offline partial review](../output/engine2-boot-clock-partial-review-20261005.json), [protocol/result](BOOT_CLOCK_DIAGNOSTIC.md). One attempt, second TIME gate rejected; only first measured PING and five boot samples available. Seven source hashes/raw partial PID accounting checked. Missing failed bracket/post facts/metrics/full summaries prevent complete acceptance; compatible initial samples do not resolve INC-032. No retries/corrections. Software unchanged since 407-test implementation.

## Boot-clock implementation (2026-10-05)

[Protocol](BOOT_CLOCK_DIAGNOSTIC.md), software [Windows](../output/engine2-boot-clock-implementation-windows-tests-20261005.xml) / [Linux](../output/engine2-boot-clock-implementation-linux-tests-20261005.xml): 407 each. Native clock/namespace validation is software-tested; a live boot-clock trial has not run at this checkpoint. No corrected timestamp, causal or independent evaluation claim.

## Pinned collector source review (2026-10-05)

[Review](COLLECTOR_TIMESTAMP_REVIEW.md), [metadata/source receipt](../output/engine2-collector-source-review-20261005.json), software [Windows](../output/engine2-collector-review-windows-tests-20261005.xml) / [Linux](../output/engine2-collector-review-linux-tests-20261005.xml): 378 each. Local Falco/libs versions, immutable upstream URLs, hashes and line markers; no copied/executed upstream source. Initialization-offset mechanism reviewed, not proven experimental cause or binary-source attestation. No new sensor/clock intervention.

## Same-trial clock domains (2026-10-05)

[Protocol/results](CLOCK_DOMAINS.md), [receipt](../output/engine2-clock-domains-20261005.json), [metrics](../output/engine2-clock-domains-metrics-20261005.json), software [Windows](../output/engine2-clock-domains-windows-tests-20261005.xml) / [Linux](../output/engine2-clock-domains-linux-tests-20261005.xml): 368 each. Eight server/harness brackets include zero; all four collector events outside nested PING and server brackets. Offline source/raw/correlation/summary checks passed; sensor removed. Negative alignment result, not a corrected baseline, overhead study or proven cause. Raw logs remain private/local; INC-032.

## Separate repeatability follow-up (2026-10-05)

[Protocol and review](READINESS_REPEATS.md), [manifest](../output/engine2-readiness-repeats-20261005/manifest.json), trial [1](../output/engine2-readiness-repeats-20261005/trial-1.json) / [2](../output/engine2-readiness-repeats-20261005/trial-2.json) / [3](../output/engine2-readiness-repeats-20261005/trial-3.json), metrics [1](../output/engine2-readiness-repeats-20261005/trial-1-metrics.json) / [2](../output/engine2-readiness-repeats-20261005/trial-2-metrics.json) / [3](../output/engine2-readiness-repeats-20261005/trial-3-metrics.json). Three launched, two accepted, third timing-rejected despite unique PID matches. Frozen source/receipt/raw-correlation and cross-trial identity checked offline. No repeated-stability, full coverage, ML accuracy or general overhead claim. Fresh [Windows](../output/engine2-repeat-followup-windows-tests-20261005.xml) / [Linux](../output/engine2-repeat-followup-linux-tests-20261005.xml) software reports: 351 each. Raw logs stay local/ignored; INC-032.

## Aborted paired pilot (2026-09-29)

[Manifest](../output/engine2-paired-pilot-20260929/manifest.json), [clock](../output/engine2-paired-pilot-20260929/clock.json), [OFF-1 failure](../output/engine2-paired-pilot-20260929/off-1.json): later jobs not executed; no empirical paired result. [Report](PAIRED_PILOT.md) records restored guest NTP and Docker/Redis recovery. [Windows](../output/engine2-paired-final-windows-tests-20260929.xml) / [Linux](../output/engine2-paired-final-linux-tests-20260929.xml): 298 tests each.

## Clock/control gate (2026-09-29 local)

[Diagnostic](../output/engine2-clock-diagnostic-20260929.json): one of six sensor-free intervals rejected. [Report](CLOCK_AND_CONTROLS.md) includes time-service observations, exact commands and deferred controls. Final [Windows](../output/engine2-control-final-windows-tests-20260929.xml) and [Linux](../output/engine2-control-final-linux-tests-20260929.xml) suites: 288 each. No live control or overhead result.

## Measured workloads (2026-09-29 local)

[Protocol/results](RUNTIME_WORKLOAD_PROTOCOL.md), [rejected ping_1](../output/engine2-ping1-measured-20260929.json), [accepted ping_4](../output/engine2-ping4-measured-20260929.json), [interval](../output/engine2-ping4-interval-20260929.json), [metrics](../output/engine2-ping4-metrics-20260929.json). One accepted/one rejected pilot is not a valid paired benchmark. [Windows](../output/engine2-workload-windows-tests-20260929.xml) and [Linux](../output/engine2-workload-linux-tests-20260929.xml): 279 tests each.

## Instrumented trial (2026-09-28)

[Trial](../output/engine2-instrumented-trial-20260928.json), [metrics](../output/engine2-metrics-20260928.json), [normalized accounting](../output/engine2-instrumented-normalized-20260928/accounting.json): observed readiness, stable selected identity, 80 records, 16 collector-wide snapshots and cleanup. [Windows](../output/engine2-instrumented-windows-tests-20260928.xml) / [Linux](../output/engine2-instrumented-linux-tests-20260928.xml): 268 tests each. Interpretation and exact commands: [instrumentation report](ENGINE2_INSTRUMENTATION.md). Not independent evaluation or full-coverage evidence.

## Offline adapter (2026-09-28)

[Adapter report](ENGINE2_ADAPTER.md), [minimized capture](../output/engine2-normalized-20260928/capture.json) and [accounting](../output/engine2-normalized-20260928/accounting.json): prior live log processed offline, 40 validated records, zero rejected, unknown sensor loss. [Windows tests](../output/engine2-adapter-windows-tests-20260928.xml) and [Linux tests](../output/engine2-adapter-linux-tests-20260928.xml): 250 passed each. No independent baseline or detection result.

## Bounded sensor smoke (2026-09-28)

[Trial record](ENGINE2_SENSOR_TRIAL.md) explains all preserved attempts and limits. [Verified summary](../output/engine2-sensor-trial-verified-20260928.json): 40 selected syscall records, PONG, exit 0, sensor removed; no threat/completeness claim. Raw logs local only, digest published. [Windows](../output/engine2-sensor-windows-tests-20260928.xml) and [Linux](../output/engine2-sensor-linux-tests-20260928.xml): 216 tests passed each. Earlier sensor-absent snapshots remain historical.

## Linux regression and Docker integration (2026-09-28)

- [First Linux suite](../output/engine2-linux-tests-20260928.xml): 204 passed; two cache warnings in command output, recorded in INC-023.
- [Clean Linux rerun](../output/engine2-linux-tests-final-20260928.xml): 204 passed after Linux-local cache selection.
- [Linux synthetic replay](../output/engine2-linux-replay-20260928.json): all four software smoke checks passed, no live telemetry.
- [Core/test dependency snapshot](../requirements-linux-core-20260928.txt) and WL-011 record reproduction and actual Windows/WSL Redis ID match. No claim of sensor visibility.

## Linux provisioning (2026-09-25)

[WSL Linux preflight](../output/engine2-linux-wsl-preflight.json): actual ACG-Research execution, UID 1000, Linux 6.6.114.1, three markers present. Not a loaded-probe test, full Linux regression suite or real telemetry capture. [Setup record](WINDOWS_LINUX_SETUP.md) and WL-010 document commands and unresolved Docker integration.

## Engine 2 host preflight (2026-09-25)

- [Windows host facts](../output/engine2-windows-preflight.json): actual local OS observation, linux_host_required. Not a Linux/sensor test.
- [Preflight regression suite](../output/engine2-preflight-tests.xml): 204 software tests passed; Linux branches mocked. No accuracy, collection or overhead claim.

These files are observations, not marketing claims. Timestamps in JSON are UTC; work occurred on 2026-09-23 in Asia/Calcutta. Original reports can contain local file paths. Repository visibility is private.

| ID | Artifact | What it establishes / limit |
|---|---|---|
| EV-001 | source/Honors_Research_1st_Monitoring_Deck.pdf | Original proposal, not proof of implementation |
| EV-002 | ../data/labels.json and development/ fixtures | Seeded development expectations and hashes; not independent ground truth |
| EV-003 | ../output/test-results.xml | Saved software-test outcomes; latest snapshot may be refreshed after relevant code checks |
| EV-004 | ../output/baseline-development.json | 45 exact-rule comparisons and repeated scanner timing; no generalization claim |
| EV-005 | ../output/live-testbed.json | Four local TCP observations and two HTTP checks at recorded time |
| EV-006 | ../output/pipeline-demo.json | Rule candidate linked to explicit staging endpoint and provisional score |
| EV-007 | ../output/rag-smoke-initial-failures.json | Initial 1.5B schema failure summaries; earliest malformed response bodies were not saved |
| EV-008 | ../output/rag-smoke-ungrounded-candidates.json | Unsupported 1.5B model candidates despite schema-valid output |
| EV-009 | ../output/rag-smoke-3b-before-policy-guard.json | 3B unsupported trust-authentication claim before narrow guard |
| EV-010 | ../output/rag-smoke.json | Final three-case candidates, rejections and timing; tuned development data |
| EV-011 | ../output/vector-smoke.json | Actual vector index, source checks and one model audit |
| EV-012 | ../output/trivy-baseline.json | Per-fixture established-tool observations and exclusions; policy scope differs |
| EV-013 | ../output/integrated-demo.json | Full vector-RAG, explicit probe and priority path executed |
| EV-014 | ../output/environment.json | Historical dependency/image/model identities and hashes for files then present |
| EV-015 | ../output/RESEARCH_STATUS.md | Generated interpretation of the saved reports, not an additional experiment |
| EV-016 | ../output/test-results-initial-84.xml | Preserved original 84-test snapshot before three repository-check tests were added |

The historical environment snapshot is not a manifest of documentation added later. Git identifies the complete committed snapshot. Do not regenerate historical experiment output merely to refresh documentation dates.

## Evidence preservation

Engine 2 initial evidence: [synthetic replay](../output/engine2-replay-smoke.json) and [software suite](../output/engine2-foundation-tests.xml). Source fixtures live under data/runtime/ and are explicitly invented, including timestamps/container ID. They are not eBPF/Kubernetes recordings or independent labels. ENGINE2_FOUNDATION.md documents interpretation.

V2.2: [initial local service observation](../output/service-identity-v22.json), [final identity/protocol observation](../output/service-identity-v22-final.json), [168-test report](../output/engine1-v22-tests.xml). Both real lab services matched selected identity checks; Redis denied via protected mode, PostgreSQL challenged via SASL. No passwords/data/SQL were sent. Interpretation: ENGINE1_BASELINE.md.

V2.1 additions: [136-test report](../output/verification-v21-tests.xml) and [real loopback/synthetic-policy smoke](../output/verification-v21-smoke.json). [Refinement report](ENGINE1_REFINEMENT.md) defines their scope. Model-review integration is mock-tested, not independently reviewed or live-model evaluated. No historical result is replaced.

V2 additions: [efficiency smoke](../output/v2-efficiency-smoke.json) records actual model/index/probe observations, full model/corpus identity and timings. [V2 test report](../output/v2-test-results.xml) records software regression results. Historical v1 artifacts above remain unchanged. ENGINE1_V2.md describes conditions and limitations.

For a changed experiment, preserve the earlier report under a descriptive revision name or rely on an already committed version, then record the new run's date, command, inputs, software/model identities and changed conditions. Keep failures, exclusions and abstentions. Never claim a mock-based unit test is a live inference run. Derived summaries must identify their source reports.
# QA-001 evidence — 7 October 2026

[Selected software audit/cache preservation](REFINEMENT_AUDIT_20261007.md): before-fix3failure rawXML, restricted Windows161fail/1030pass/38skip retained; fresh host Windows1191pass38skip/22.66s (XML22.659), Linux1229pass84.14s (XML81.600),1229collected/zero failures/errors in host runs. Lint119fileformat/bothpipchecks pass. Three reproduced cache defects fixed, not161 new code fixes or an exhaustive security/independent detector evaluation. Original native import cause unknown; no live collection/model smoke/service/clock/cloud action or research approval. Commands, receipt links/hashes/context limitations in report/WL-068.
