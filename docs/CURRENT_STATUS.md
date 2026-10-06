# Active Cloud Guard — current capability and research status

Updated 6 October 2026. This is the current status summary; dated implementation checkpoints in other documents are historical evidence, not additional engines or today's task list. Actual code, saved artifacts and their limitations take precedence over prose. Preserve Python/CLI, Docker Compose, Ollama and Chroma; no web/SaaS or cloud-account mutation is implied.

## What “complete” means here

**Engine 2's observation-only replay baseline is implemented. We are refining its experimental infrastructure; several planned capabilities and scientific validation gates remain unfinished.** Do not describe it simply as “not built,” “fully complete,” “production ready” or “validated threat detection.” A working baseline, a refinement and an independently evaluated research result are different milestones.

| Layer | Current capability | Evidence and remaining boundary |
|---|---|---|
| Engine 1 engineering baseline | Configuration checks, retrieval/local-model transport, scoped probes, bounded reuse and reviewed service observations | Frozen engine1-v2.2 at commit 6736a577f1ba08b4700daf8a86370ec3bbd1c019; [baseline](ENGINE1_BASELINE.md). Independent effectiveness/latency/hallucination/TCI calibration remain open |
| Engine 2 runtime baseline | Saved normalized captures, identity/schema validation, nonempty time windows, statistical count-deviation comparator | cloudguard/runtime.py; [foundation](ENGINE2_FOUNDATION.md). Model is statistical, uncalibrated, observation-only; low score is not safety |
| Engine 2 telemetry tooling | Separate bounded Falco capture, saved-data normalization, selected readiness/identity/drop metrics and correlation diagnostics | [Instrumentation](ENGINE2_INSTRUMENTATION.md), [adapter](ENGINE2_ADAPTER.md). Not a continuously integrated sensor or independent threat benchmark; coverage/clock stability unresolved |
| Supporting refinements | Timing diagnosis, receiver, private native callback tests and inert durable job/fence records | [Receiver](SYSTEMD_RECEIVER_CAPTURE.md), [native fixtures](NATIVE_CALLBACK_VALIDATION.md), [inert gate](DURABLE_JOB_GATE.md). Experimental-safety mechanisms, not additional engines or anomaly-detection models |
| Full runtime research objectives | Not yet independently established | Runtime labels/grouped held-out data, planned ML comparisons, calibrated detection/false alarms/misses/delay/overhead and Engine1/runtime evidence integration remain open |

The current replay output now includes implementation_scope for **runtime_replay_baseline** only: status implemented; saved sensor exports supported; live input/trained ML/independent detection evaluation/automatic response false. It no longer claims the entire repository has no eBPF collector. Acquisition/normalization are separate experimental paths. Added metadata/text do not change scores, thresholds, windows or leakage guards.

No Isolation Forest/autoencoder, validated runtime threat classifier, automated cloud isolation, integrated runtime TCI contribution or production deployment is claimed. The original first-three-month engineering milestone principally concerned Engine1; later runtime objectives are not retrospectively required/declared completed. See [deck audit](DECK_AUDIT.md), [requirements](PRD.md), [tasks](../TASKS.md).

## Current verification, not effectiveness

Status-clarification change: three new scope regressions; targeted runtime tests: 31 passed in 0.69 s. Full [Windows XML](../output/engine2-status-windows-tests-20261006.xml): 854 collected, 817 passed / 37 Linux-only skips, zero failures/errors, console 8.34 s / XML 8.343 s. Full [Linux XML](../output/engine2-status-linux-tests-20261006.xml): 854 passed, zero failures/errors/skips, console 39.56 s / XML 37.570 s. These are **whole-repository software tests**, not 854 attack scenarios or independent accuracy observations. Console/XML timing difference undiagnosed, no clock-accuracy/engine-performance claim. Ruff lint/format (102 files) and pip check pass.

[Fresh synthetic replay](../output/engine2-status-clarification-replay-20261006.json) passed all four checks: expected states, no actions, no sensor claim, declared synthetic. Compared every result field against the [historical baseline](../output/engine2-replay-smoke.json), excluding only new scope metadata/clarified limitation text: all other calculated fields/provenance identical. Original artifacts untouched, no real collector/clock/service/model action. Recorded executed_at2026-10-06T11:05:16.527834+00:00 is reported walltime, not clock-accuracy evidence. Commands/checks/staged review/publication in WL-057.

### Executed checks and reproduction

At the configured repository root, using the existing environments:

```powershell
.venv/Scripts/python.exe -m ruff format cloudguard/runtime.py tests/test_runtime.py
.venv/Scripts/python.exe -m pytest -q tests/test_runtime.py --basetemp=tmp/engine-status-target-win-20261006-01 -o cache_dir=tmp/pytest-cache-20261006
.venv/Scripts/python.exe scripts/runtime_check.py --output output/engine2-status-clarification-replay-20261006.json
.venv/Scripts/python.exe -m pytest -q --basetemp=tmp/engine-status-full-win-20261006-01 -o cache_dir=tmp/pytest-cache-20261006 --junitxml=output/engine2-status-windows-tests-20261006.xml
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python -m pytest -q --basetemp=tmp/engine-status-full-linux-20261006-01 -o cache_dir=/home/acgresearch/.cache/acg-pytest --junitxml=output/engine2-status-linux-tests-20261006.xml
.venv/Scripts/python.exe -m ruff check cloudguard scripts tests
.venv/Scripts/python.exe -m ruff format --check cloudguard scripts tests
.venv/Scripts/python.exe -m pip check
```

Use fresh temporary/report filenames when reproducing; do not replace these saved artifacts or old fixed-output evidence. Whole-suite host execution was approved for existing inert process tests and ordinary-user WSL; no native service intervention. The existing synthetic runner refuses an existing output file. Scope metadata is an implementation declaration supported by tests/source review, not runtime attestation or independent evaluation.

## Work direction and acceptance gates

Next default priority is **E2-035: grouped runtime dataset and independent-label intake**, mapped to E2-004/RQ3—not another safety helper by default. [Runtime evaluation plan](RUNTIME_EVALUATION_PLAN.md) specifies the next deliverable and boundaries; intake tooling/new independent data are **planned, not implemented or obtained by this change**.

1. Audit existing captures/receipts, retain development and timing-rejected data as such; do not promote them into untouched/independently labeled test data.
2. Prepare a bounded offline run/window manifest and separate blinded reviewer submissions; guard template/deployment/run grouping, duplicate captures and event leakage before assigning splits. No prediction-visible/generated “independent” labels.
3. Establish eligible comparable captures, timing/coverage/identity evidence and actual human adjudication before fitting a research model or claiming a benchmark. Existing clock failures remain open; do not relax/retrofit their gates.
4. Implement/test planned model comparisons under that frozen protocol; software tests with synthetic data may validate code but cannot establish effectiveness.
5. Evaluate misses/false alarms/abstentions, grouped uncertainty, delay/overhead and carefully scoped Engine1/runtime integration. Publication readiness requires actual research evidence, not a test count.

Existing E2-034/native restoration work stays partial. Expand/resume it only for a defined dependency of a reviewed diagnostic/intervention; do not mistake such progress for detection progress. Generic proceed never authorizes time-service stops, clock changes, production scanning or response. Any real service intervention still needs the safe native job-owner/recovery protocol, old unfenced-path elimination, current preflight, explicit fresh human consent and restoration validation. This page schedules no unattended work.

## Maintenance rule

Every substantive change must update this current summary when capabilities/priority/evidence change, plus MEMORY/TASKS/WORK_LOG/CHANGELOG and relevant contracts. Record separately: implemented baseline, completed refinements, missing planned capabilities and scientific gates. Say “complete” only for named acceptance criteria. Keep dated snapshots visibly historical; never rewrite negative experiment bytes or infer execution from documentation. [Maintenance contract](DOCUMENTATION_WORKFLOW.md).
