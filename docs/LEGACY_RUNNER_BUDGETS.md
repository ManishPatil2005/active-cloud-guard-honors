# Legacy runner input, client-process and publication budgets

QA-008 / R7 / R8, 9 October 2026; readiness sequence2, start revisiond8daff9ce582431cedfab66b8a562dc0952b92c4. Existing Python/Compose/Ollama/Chroma architecture retained. No detector algorithm/model change or new Docker/model/sensor study.

## Acceptance and implemented scope

Selected legacy reads must reject oversized files before parsing/model/probe work. Trivy and environment metadata clients must use bounded combined stdout/stderr and finite deadlines, never shell composition. Failure must retain prior observations, expose owned cleanup uncertainty and stop a Trivy batch rather than silently replace a failed slot. Existing exclusive output reservation remains before activity; incomplete environment capture cannot produce a plausible successful dependency lock.

Implemented two shared stdlib helpers:

- legacy_io.InputBudget: default8MB aggregate/256files/600-second cooperative batch deadline; selected reads1MB, historical JSON/XML2MB. Hashes stream64KB with8MB per-file cap. Environment metadata uses32MB/2048files/180seconds and10,000traversal-entry cap; symlinks refused. XML accepts UTF-8 and rejects DTD/entity declarations, then checks depth64/nodes50,000 after parsing. Duplicate/nonfinite/deep JSON inherits existing strict checks.
- process_runner.run_bounded: trusted argv list only, stdin DEVNULL, shell=false, hidden Windows child, two concurrent pipe readers with a shared retained-byte cap (default2MB, maximum8MB), finite timeout<=180seconds. Streams read at most4096bytes per chunk and retain no more than the combined cap. Nonzero exit codes remain observations; invalid UTF-8/output overflow/timeout/interrupt/launch/pipe/cleanup faults reject explicitly. Failure retains separate bounded raw byte prefixes and a static owned diagnostic message.

Direct-child cleanup attempts kill and wait up to5seconds; reader joins share a1second cleanup budget. Receipt fields distinguish direct_child_reaped, pipes_closed and external_job_completion_verified=false. On supervision failure or child launch failure no successful result is invented. No whole process tree, Windows Job Object, Docker-daemon job/container cancellation, parent-crash watchdog, OS memory/CPU sandbox or uninterruptible syscall deadline guarantee. A Docker CLI killed locally can leave remote work running: stop the batch, preserve uncertainty and require separately scoped operator inspection. No automatic broad container cleanup or service control was added.

## Runner behavior

| Runner | Selected changes |
|---|---|
| trivy_baseline.py | Strict bounded manifest1..256unique basename IDs, fixed existing image/network-disabled command.600-second cooperative batch/8MB aggregate client outputs, per-client<=180seconds/2MB. Failed current row retains prefixes/diagnostic; previous rows retained; remaining supported fixtures listed not_attempted; unsupported names still excluded separately. No retries/replacement or accuracy claim. |
| capture_environment.py | Fixed six image-inspect and one version client, each<=30seconds/128KB; seven calls give a finite declared aggregate output bound. Partial digests/package/source facts retained on failure, output status rejected and lock-output contains a rejection receipt—not installable requirements. Package/traversal/hash budgets and malformed lock-token guards. Source PDF now portable repository copy docs/source, not a Windows Downloads path; historical reports unchanged. |
| rag_check.py | Preload three bounded configurations and knowledge-file precheck before inference. Cooperative checkpoints and remaining-time audit timeout. Failed model strings still retained under previous review rules. |
| vector_check.py | Bounded configuration/knowledge preflight before index/model activity, checkpoints between selected stages, remaining-time chat timeout. Underlying embedding/index/native calls retain their own timeouts and can overshoot a cooperative batch deadline before the next check. |
| live_check.py | Bounded strict inventory read and existing schema/loopback validation before probes. Core pipeline behavior unchanged; this is not a hard deadline for every core operation or authenticated deployment mapping. |
| summarize.py | Bounded aggregate historical JSON/XML reads; existing historical arithmetic retained. No new live experiment from generating a summary. |
| integrated_check.py / shared publisher | Core scanner/retrieval/model bounds already apply. Shared evidence publisher caps combined serialized output8MB; oversized new publication yields a rejected receipt, never overwrites old evidence. Serialization precedes its final byte check, not a hard allocation limit or per-step activity journal. |

Batch/file/byte/checkpoint limits are scoped engineering guards. They do not cover every subprocess or reader elsewhere in the repository. Filesystem races, native dependency allocations, parser fuzzing, remote-job recovery and broader calibrated/qualified research remain open. Source hashing/metadata collection is not authenticated provenance or an independent benchmark.

## Evidence, incidents and execution limits

Final source/cases: Windows1,566passed/38existing platform skips; Linux1,604passed, both1,604collected/zero failures/errors.50newcases; corrected103target checks eachOS,18documentation tests, lint/140fileformat/bothcompatibility checks pass. Not an independent detector benchmark or guarantee of container cleanup.

Before input regressions:2failed in output/legacy-budget-before-windows-20261009.xml. The initial live regression omitted HTTP/pipeline mocks and attempted the two fixed loopback health URLs; no TCP probe from its empty inventory, no model/Docker/sensor workload or clock/service action. Returned health outcomes were not preserved or claimed as qualified observations. Corrected isolation before further runs; record the mistake, not a false “no HTTP requests” statement. INC-071.

Targets:55passed initially,94expanded,102before cross-platform correction, then103corrected on each OS, including harmless actual Python direct-child exit/nonzero/stdout/stderr/output overflow/timeout/interrupt/invalid-UTF8 tests. Initial Windows full1565passed38skips; initial Linux full interrupted after725passed because the interruption test patched shared time.sleep also used by Linux subprocess.wait cleanup. Isolate injected interrupts to private supervision pause; cleanup-time interrupt now produces owned interrupted/unverified-reap diagnostic. Added regression without weakening actual kill/reap assertions. Partial Linux receipt preserved, not called a complete suite. Docker clients/metadata capture and model/probe paths mocked; no actual Trivy or metadata Docker run. Simulated cleanup failure remains explicitly unverified. Raw negative receipt preserved. Fresh historical summarizer executed separately; original reports/lock/snapshot/import-negative hashes unchanged. Exact final full-suite/docs/publication results in [WORK_LOG](WORK_LOG.md).

Next readiness step: local pinned-dependency/advisory review and focused resource/parser/artifact/native review under [roadmap](PRODUCTION_RESEARCH_ROADMAP.md). Production readiness, novelty, original intermittent import/timing causes, actual supervisor approval/humans/held-out data/calibration/overhead/energy remain open. Do not mark those complete from this helper's tests.
