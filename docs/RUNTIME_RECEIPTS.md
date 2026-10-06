# Selected offline runtime receipt checks (E2-035)

6 October 2026. Implemented refinement of the existing Engine2 research intake, tied to RQ3/E2-004. **This is not Engine2 version 2, a new detector or research eligibility.** runtime_intake_v2 is a versioned bundle format; runtime replay engine version0.1 and Engine1 frozen v2.2 are unchanged. [Current status](CURRENT_STATUS.md), [base intake contract](RUNTIME_INTAKE.md).

## Flow and compatibility

Dedicated bundle -> existing role/path/schema/hash/byte guards -> typed wrapper -> hash-bound source JSON -> selected arithmetic/binding checks -> minimized report -> existing postflight checks. New cloudguard/runtime_receipts.py imports the existing clock comparison, runtime timestamp parser, adapter kind mapping/pinned image and schema helpers. No network/subprocess/model/collection/service/native/clock operations. No new dependencies or default-engine/comparison source-freeze integration.

Original runtime_intake_v1 remains hash-only for opaque receipt objects, with unchanged report values: an executed regression compares the complete original example report. Opt-in runtime_intake_v2 uses the same manifest fields but requires typed wrappers for nonnull receipt references. Null roles remain missing/unknown, not successful. No silent fallback from unsupported v2 receipts to opaque v1. The original CLI rejection envelope retains its runtime_intake_v1 marker; it is a generic sanitized error envelope, not input-version validation.

## Wrapper contract

Every wrapper must contain exactly:

| Field | Meaning/check |
|---|---|
| schema_version | runtime_receipt_v1 |
| kind | accounting/identity/timing, matching manifest role |
| run_id | Exact declared run ID |
| capture_sha256 | Exact normalized capture bytes |
| inventory_sha256 | Exact inventory bytes |
| collection_protocol | acg_falco_selected_v1; only the selected ACG lab receipt family, not arbitrary Falco/Kubernetes data |
| origin | synthetic_fixture/recorded_projection, a declaration, not authentication |
| source | path/sha256 reference to original source JSON, inside receipts directory and subject to existing bundle limits |

Synthetic captures cannot claim recorded_projection; sensor exports require that declared origin. Source JSON explicitly marked fixture_only=true cannot claim recorded provenance. Missing/removed markers or renamed/reformatted fixtures are not fully detectable: all authenticity/eligibility flags stay false regardless. No supplied wrapper can grant a new action or approve fitting.

## Checked facts and deliberately unchecked facts

| Role | Selected checks | Remaining limits |
|---|---|---|
| Accounting | Exact supported adapter0.1 schema; inventory hash; syscall counts mapped through existing KINDS equal capture kind totals; validated/rejected/diagnostic line arithmetic and rejection-reason sum; normalized/rejected status recomputed | Raw export not reread or normalized by this tool. Caller-supplied accounting may be forged. Diagnostic lines/zero rejection/drop declarations do not establish complete delivery |
| Identity | One compose/redis binding for identity/timing; source pinned Falco image/full container ID/explicit unauthenticated flag; strict before/after snapshot schemas and valid started_at; both IDs match capture; stable recomputed from equal snapshots and running=true | Container/project/image snapshots are saved declarations, not current Docker queries, mounted-file equivalence or authenticated host identity. Changed/nonrunning states stay negative |
| Timing | Source measurement timing_protocol per_call_brackets_v1; strict first/last wall/monotonic midpoint/span integers; existing compare recomputes elapsed/difference/uncertainty/within_tolerance; redundant measurement endpoints match; optional recorded zero_excluded_samples retained | **Harness endpoints only**: not every call, schedule, duration, namespace/domain/source closure, collector PID/event bounds or full historical protocol. Local compatibility cannot prove collector alignment or long-term stability |
| Cross-role | Accounting trial_sha256 binds the exact identity/timing source; raw_sha256 equals that source's raw_log_sha256; trial matched_event_count and exact integer event_type_counts match accounting; identity/timing share one source hash | These are saved-document consistency checks, not physical origin or causal authenticity |

Accounting expects all original adapter fields (see ACCOUNTING schema), unknown extra fields refused; counts bounded0..10000, known syscall names only. Nonzero rejected counts, false receipt_counts_match or zero validated events require rejected status; retain a consistent negative result rather than treating it as normal. Unsupported sensor_dropped_events/complete-coverage/threat/action claims refused by this selected schema, not automatically accepted as newer protocols.

Identity snapshots contain id, image (sha256: plus64lowercase hex), started_at, running, restarts, project, service=redis. Restarts0..10000. Started time uses existing aware1970..2100 parser, equality retains original strings; no timestamp correction. Snapshot equality is scoped, never native binding.

Clock samples contain wall_ns, monotonic_mid_ns, sampling_span_ns; clock_sampling also elapsed_monotonic_ns, clock_difference_ns, sampling_uncertainty_ns and boolean within_tolerance. Values bounded to existing1970..2100 nanosecond range; signed elapsed/difference allowed to preserve rejection. Booleans are not counters; integral floats are refused. Existing compare unchanged: positive elapsed, abs(difference)+uncertainty <=50ms and each sampling span <=5ms. Negative elapsed/wide spans produce false, not eligibility. Optional recorded collector rejection count0..4 or absent/null; this is not a reconstructed correlation result. Zero/absent count is not proven alignment.

Selected output scopes: adapter_counts_only, selected_recorded_snapshots_only, harness_endpoints_only. selected_consistency_checked=true means this named subset passed; full receipt_semantics_verified, binding_verified, evaluation_eligible, independent_evaluation_verified, model_fitting_authorized and predictions_computed remain false; actions_executed empty. Reports omit source paths/bodies, private identity fields, event bodies, clock packets and reviewer reasons. Raw/source/wrapper hashes are provenance bindings, not attestations.

## Harmless reproduction

At the configured repository root, with a new output filename:

```powershell
.venv/Scripts/python.exe scripts/runtime_intake.py --manifest data/runtime/intake-example/manifest-typed-counted.json --output output/my-fresh-typed-report.json
.venv/Scripts/python.exe -m pytest -q tests/test_runtime_receipts.py tests/test_runtime_intake.py
```

Linux uses the existing environment's Python. No Docker/Ollama/services needed. Every source/wrapper/event in this example is invented, not independent data. [Executed final report](../output/engine2-typed-intake-counted-synthetic-20261006.json): three events/windows, eight unique artifacts/5,187bytes, all selected roles checked, no reviewers, no eligible data/fitting/actions. Synthetic event times are not matched to the practice measurement interval; endpoint arithmetic is not collector alignment. Raw export not supplied/verified.

Earlier manifest-typed.json and uncounted receipt sources are preserved **negative fixtures**. Current checker rejects missing trial count fields: [executed rejection](../output/engine2-typed-intake-uncounted-rejected-20261006.json). Do not use the [pre-fix report](../output/engine2-typed-intake-synthetic-20261006.json) as current success. Its source/wrapper/manifest bytes are retained, not silently replaced by counted ones. All old v1/historical evidence unchanged.

## Review failure and remaining gates

Final verification: **77 new cases**, including two saved-artifact parser checks (not new experiments). Full [Windows final XML](../output/engine2-typed-intake-windows-final-tests-20261006.xml):1,014collected,976passed/38skips (37existing Linux-only/one symlink privilege), zero failures/errors,15.31s console/XML15.304. [Linux final XML](../output/engine2-typed-intake-linux-final-tests-20261006.xml):1,014passed/no skips,90.48s console/XML87.088. Ruff lint/format107files/pipcheck pass. Earlier target146pass/1skip5.78s, then153pass/1skip5.70s; preliminary fullLinux1,010pass/Windows972pass38skips before the additional count regressions. Whole-repository software tests, not attack accuracy/performance/clock proof; console/XML differences undiagnosed. Final suites include the reproduced/fixed count cases and preserved missing-count fixture rejection. WL-059 exact commands and receipt paths; never overwrite artifacts on reproduction.

INC-049: review identified missing cross-check between accounting and its referenced trial count claims. Three before-fix cases (wrong total, boolean-as-count, redistributed kinds) all failed with DID NOT RAISE,3failed/73deselected0.44s/XML0.263. [Raw negative XML](../output/engine2-typed-intake-count-regression-20261006.xml), SHA c771cebc2353d935fa1e7edcf04e401a085be0f152950d1d3cd98f6f1da5f53c. Fixed by checking exact trial counts, without weakening hashes/schema/timing/eligibility. Initial passing suites were preliminary, not proof the review-discovered gap absent; preserve them. WL-059 records all commands, subsequent final suites and an earlier fixture-import lint fix.

Two regression cases read existing historical artifacts, not new trials: instrumented accounting matches80saved events but coverage remains false; trial-3 from5October has acceptable local endpoint arithmetic and four recorded collector exclusions, with collector alignment/stability false. Source bytes preserved. These checks do not revalidate the entire original experiment or repair clock failures.

Next E2-035 acceptance: actual supervisor decisions on the now-prepared [draft reviewer pack](RUNTIME_LABELING_PROTOCOL.md)/[guidelines](RUNTIME_LABELING_GUIDELINES.md)/[capture checklist](RUNTIME_CAPTURE_ELIGIBILITY.md), then eligible comparable evidence-bearing captures under reviewed timing/coverage/identity protocols. Drafts not approved. Full receipt compatibility/coverage/correlation, genuine independent human labels, frozen held-out data/model/effectiveness/overhead/integration remain open. No automatic collection, service/clock intervention, external import, research completion or future monitoring implied. Latest software receipts WL-060; final typed refinement verification above is historical.
