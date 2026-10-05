# Progress Execution

**Next read-only step, 5 October:** Windows' time service is now running; Linux uses the tsc timer and has both host synchronization and its own NTP service enabled. These snapshots do not tell us what caused earlier failures. We added an optional check using Linux's unadjusted clock alongside its normal clocks, without changing any settings. It can help separate clock-adjustment effects from a provider/reference difference. One new short observation is planned after tests/publication; Engine 2 is still under validation. [Provider facts and simple commands](CLOCK_PROVIDER_REVIEW.md).

**Clock investigation result, 5 October:** the one planned read-only check completed sixteen readings. Linux's clocks stayed consistent with each other, but advanced less than Windows' timer across the observation, even after allowing for command delays. This was visible in thirteen of fifteen elapsed-time comparisons. It gives us useful sensor-free evidence; we still do not know which clock mechanism caused it or whether it explains the earlier sensor issue. We kept the result, changed no time settings/services and did not retry. Engine 1 unchanged; Engine 2 timing reliability and machine-learning evaluation remain unfinished. Next: inspect clock-provider facts before choosing a separately planned stability test. [Evidence and reproduction](CLOCK_LINEAGE.md).

**Next clock investigation, 5 October:** a new read-only tool will watch Windows time and three Linux clocks together, up to sixteen times. It keeps the uncertainty caused by command delays instead of assuming the computers share one clock. No time settings, services or sensors are changed. All 455 software tests pass on each OS. One short observation is planned after publishing the tool; even a successful result cannot explain a past clock change or prove long-term reliability. This remains Engine 2 groundwork, not Engine 3. [Simple protocol and commands](CLOCK_LINEAGE.md).

## A beginner's guide to Active Cloud Guard

**Collector follow-up result, 5 October:** the one new sensor-on check completed, matched all four measured test connections and passed the recorded timing checks. We checked 27 boot/wall-time samples and the saved event summaries; sensor removed, no clock changes. However, comparing the earlier and current startup readings shows the boot/wall relationship differs by about 123 seconds between runs. We do not know when or why it changed, and missing service/power logs do not prove nothing happened. This is an exploratory finding, not proof of a cause. Engine 2 still needs trustworthy long-term timing and independent evaluation; the latest software suite passes 428 tests per OS. [Evidence and limits](RECORDED_BOOT_CLOCK_FOLLOWUP.md).

**Collector-specific follow-up preparation, 5 October:** we are adding time-since-boot/wall-time readings around each server-time check, saving them before a check can reject the result. This will provide more information if a future sensor-on run fails. It does not change clocks, loosen safety limits or recover earlier lost data. One new bounded follow-up is planned after tests and commit. [Protocol](RECORDED_BOOT_CLOCK_FOLLOWUP.md).

**Sensor-free result, 5 October:** all six time reads passed in the one planned run. Commands took about 54–86 milliseconds; clock readings agreed within the tested bounds, and the service stayed unchanged. We checked the saved numbers and hashes independently of the live command (offline consistency, not independent scientific evaluation). No sensor, retry or clock adjustment. This is useful evidence that the later sensor-free check worked, not proof the earlier problem is fixed. Next is a carefully planned collector-specific check using the improved failure recording. Engine 1 unchanged; Engine 2 timing/ML evaluation still unfinished. [Results](SENSOR_FREE_TIME_ATTEMPTS.md).

**Next diagnostic, 5 October:** we are preparing a check that asks the existing Redis service for time up to six times, with a one-second pause between successful reads. It runs without a sensor and stops at the first failed check, saving the available timing details. This can tell us whether a new failure is due to a slow command or incompatible clock readings; it cannot recover the earlier lost details or prove Engine 2 is finished. One new attempt is planned after testing/commit. [Method](SENSOR_FREE_TIME_ATTEMPTS.md).

**Failure-recording improvement, 5 October:** future failed time reads now save the available timing details and failure stage without exposing raw error messages. Tests cover seven different failure paths; 414 pass on both operating systems. This improves our ability to diagnose a future failure, but cannot recover details lost in the earlier attempt. We did not run another sensor trial or change clocks. The research timing problem is still open; next is a separately planned check without a sensor. [Recording details](CLOCK_DOMAINS.md).

**Single live attempt, 5 October:** the new tool verified initial clock comparability and recorded the first test connection correctly. It stopped during the second time read because a safety check failed; we did not repeat it to get a better result. Unfortunately the failed read's timing details were not saved, so we cannot yet say why it failed. The sensor was removed and clock settings stayed unchanged. Next we will improve failure recording, with tests, before another separately planned experiment. Engine 2 is not complete; Engine 1 stays unchanged. [Partial result](BOOT_CLOCK_DIAGNOSTIC.md).

**Boot-clock tool, 5 October:** we added a read-only tool to compare wall time with time since boot around sensor startup and each test command. It checks whether the measuring program and containers have comparable clocks before interpreting numbers. 407 tests pass on each OS. This is implementation progress, not proof the timing problem is fixed; the one planned live diagnostic has not run at this checkpoint. No clock settings or Engine 1 changes. [Protocol and limits](BOOT_CLOCK_DIAGNOSTIC.md).

**Collector review, 5 October:** we inspected the exact installed collector version and its corresponding release code. It builds event time using a boot-time offset set during initialization. If the relationship between wall time and boot time changes later, this could explain early event timestamps—but we have not directly proven that happened. We added a small reproducible version/source checker and preserved source hashes; 378 tests pass on each OS. No new sensor trial or clock changes. Next is careful read-only clock-relationship measurement, not declaring the engine fixed. [Review and limits](COLLECTOR_TIMESTAMP_REVIEW.md).

**Next 5 October step:** a new diagnostic now asks the Redis server for its time immediately before and after each measured PING. In one trial, all eight server readings were compatible with the measuring program, but the four matching sensor event times were about a second earlier than both. This narrows where to investigate; it does not prove the cause or fix the problem. We preserved the finding, removed the sensor and adjusted no clocks. 368 software tests pass on each OS. These extra time reads change the workload, so we do not call this an overhead benchmark or a successful repeatability study. [Clock-domain report](CLOCK_DOMAINS.md).

**5 October update:** we ran a separately declared three-trial check using the improved runner. All three started; the first two passed, but the third failed because its recorded event times were about 0.8 seconds earlier than the measuring program's command times. The commands themselves succeeded and their connections were recorded. This shows why collecting events is not the same as measuring them reliably. We preserved the failure, removed every trial sensor and changed no clocks; we did not repeat runs to obtain a favorable result. Fresh software suites still pass 351 tests on each OS. Next is careful clock-domain diagnosis, not a claim that Engine 2 is finished. [Detailed study](READINESS_REPEATS.md). Older updates below are historical snapshots.

Latest repeatability check: **351 software tests pass on each OS**. We planned three identical trials, but a path-handling error stopped the batch after the first passed. The other two never started. We preserved the incomplete study and improved the runner; we did not rerun until obtaining a favorable result. One successful run is not proof of repeatability. See [study record](READINESS_REPEATS.md).

Latest readiness improvement: **343 tests pass on both operating systems**. Measurement now waits for evidence belonging specifically to the second preparation PING, rather than accepting any earlier activity. One new trial observed both preparation PINGs and all four measured PINGs. This is a successful six-command check, not proof of complete monitoring. Earlier misses remain documented; next is a fixed repeated evaluation rather than declaring the problem permanently solved.

Latest progress: **338 tests pass on both operating systems**. We now track the two preparation PINGs separately. The new trial found no connection record for the first preparation command, but found the second and all four measured commands. This identifies where the gap occurred in this trial, not its cause; overall completeness is still unproven. Docker/Redis needed restarting before the test; nothing was recreated or deleted. Next is stricter sensor-readiness checking. See [detailed diagnostic](PID_CORRELATION.md).

Latest sensor step: **332 tests pass on each OS**. In one new supervised trial we identified each of four measured PING processes and found exactly one matching sensor connection for each. Their timestamps were compatible with the command timings. This is useful progress, but the earlier clock issue is not proven fixed and total warmup coverage is still uncertain. The sensor was removed and no time settings changed. See [PID correlation](PID_CORRELATION.md). Older totals below are historical snapshots.

Latest clock investigation: **318 tests now pass on each OS**. We asked the existing Redis lab for its time six times and compared it with the measuring program, allowing for command delay. None of these samples demonstrated a clock difference. This was a later check with no sensor running, so the earlier sensor-timing problem remains open. No clocks or database data were changed. See [clock diagnostic and limits](CLOCK_BRIDGE.md). Older test totals below describe earlier snapshots.

Latest follow-up: **308 software tests pass on each OS**. Comparison reports now double-check the saved clock readings and refuse to compare different timing methods. The old pilot was rechecked without changing its results. This protects reporting; it does not fix the sensor-clock discrepancy. The 301-test counts later in this guide identify the earlier timing-guard snapshot; a current checkout should report 308. Latest test records: [Windows](../output/engine2-report-guards-windows-tests-20260930.xml), [Linux](../output/engine2-report-guards-linux-tests-20260930.xml).

Researcher: **Manish Patil**. Updated **30 September 2026**. This document explains the research, its actual progress, and how to try the implemented parts. It is written for students, supervisors and reviewers who do not work with software every day.

Read sections 1–5 first. Sections 6–10 are practical steps. The safe demonstrations need no cloud account, paid API, AI model or running server. Advanced experiments are separate because they require additional permissions and careful measurement.

## 1. What problem are we studying?

Software can be installed with unsafe settings: for example, a database may be configured to trust a connection without checking a password. Finding such a setting is useful, but it does not automatically prove that an attacker can reach or exploit the system.

Active Cloud Guard investigates whether three kinds of evidence can support a better security review:

1. Read the settings and check clearly defined rules.
2. Retrieve relevant security guidance and ask a local AI model to suggest concerns.
3. Make limited, authorized observations to check what is actually reachable or happening.

The aim is evidence-supported review, not automatic declarations that a system is safe or compromised. The research hypothesis still needs independent evaluation.

## 2. The two engines, without jargon

**Engine 1 is the configuration reviewer.** Think of it as inspecting a building's plan. It reads supported configuration files, applies nine defined checks, can retrieve supporting guidance, and can ask a locally running AI model for suggestions. Some verification checks can contact explicitly listed services on this computer. AI suggestions require human review.

**Engine 2 is the activity observer.** Think of it as examining a building's activity log. It can read saved events, count activity in time intervals and flag a difference from a supplied baseline for review. A limited Linux sensor has also recorded real activity from the local Redis lab. The live sensor is a separate bounded research tool, not a continuously deployed protection system.

The engines do not automatically block users, shut down services or repair a deployment. An activity difference is not automatically an attack. A reachable port is not automatically a vulnerability.

## 3. Small dictionary

| Term | Plain meaning |
|---|---|
| Repository / GitHub | The versioned project folder / its online copy |
| Commit | A named saved revision; use its identifier when citing results |
| Terminal | A window where you type commands |
| Python | The language used to implement the project |
| Virtual environment | A separate folder holding this project's Python packages |
| Docker / container | A way to run the disposable lab services in separate software environments |
| Compose | The file that describes the lab services |
| Ollama | The local program that runs the AI model |
| Chroma | A local store used to retrieve related guidance by meaning |
| Fixture | A deliberately prepared example used during development |
| JSON | Structured text containing fields and results; open it in a text editor |
| Regression test | An automatic check that a known behavior still works |
| Baseline | Reference behavior used for comparison |
| PING / PONG | A small Redis availability request / its successful reply |
| Hash / SHA256 | A fingerprint used to detect changed file bytes, not proof of trustworthy authorship |
| WSL | A Linux environment hosted on Windows |
| eBPF / Falco | Linux observation technology / the sensor used in the bounded trials |
| Latency | How long an operation takes |
| Abstention | The system does not accept a claim; this is not a clean safety verdict |

## 4. What has actually been completed?

| Area | Implemented and checked | Still limited or unfinished |
|---|---|---|
| Research planning | Original proposal reviewed; architecture, rules, tasks and evidence documented | Literature review and supervisor-approved independent evaluation remain open |
| Configuration checks | Nine rules; 45 prepared development examples | These examples are not an untouched test set; broader security coverage is not claimed |
| Retrieval and AI | Local retrieval, structured model output, source/location checks and narrow rejection guards | AI can still make unsupported claims; general accuracy is unmeasured |
| Engine 1 verification | Restricted local network checks and selected Redis/PostgreSQL identity/protocol observations | No general exploit verification or full deployment attestation |
| Efficiency | Reuse of identical AI requests and unchanged vector indexes | General speed, energy and sustainability improvement is not established |
| Engine 1 preservation | Baseline frozen under tag engine1-v2.2 | Frozen means preserved, not scientifically complete |
| Engine 2 replay | Saved-event validation, interval counts, simple deviation comparison | No independently evaluated runtime ML model |
| Live observation | Bounded Linux sensor trials and offline conversion of saved logs | Coverage and sensor-to-harness timing alignment remain uncertain |
| Comparison pilot | Two sensor-off and two sensor-on runs completed | Results are too limited and inconsistent for a general overhead claim |
| Latest timing safeguards | Clock readings around each measured PING; rejection of large per-call clock disagreement | Software-tested, not yet exercised in a new live sensor experiment |
| Software quality | 301 tests pass on Windows and Linux at this revision | Passing tests do not prove detection accuracy or production safety |

The Python, Docker Compose, Ollama and Chroma architecture has been preserved. The supplied web-app workflow was used as a documentation reference, not as a request to change the technology stack.

## 5. Results, problems and honest interpretation

### Engine 1

The 45 development examples matched their expected rule sets. This demonstrates behavior on the examples used during development, not real-world detection accuracy.

One earlier repeat-work experiment observed approximately 0.084 and 0.072 seconds for cached runs, while still making fresh network observations. This does not mean every new configuration is checked that quickly. Separate uncached AI examples took roughly 12 seconds and missed the 3.5-second target. Earlier malformed AI responses and unsupported suggestions remain saved in the repository.

### Engine 2

A completed four-run experiment measured average Docker-exec round trips:

| Run | Sensor | Mean time |
|---|---|---:|
| OFF-1 | Off | 59.423 ms |
| ON-1 | On | 91.887 ms |
| ON-2 | On | 66.066 ms |
| OFF-2 | Off | 72.592 ms |

The paired changes were +54.63% and -8.99%. They point in opposite directions. These measurements include Docker's command-launch work; they are not pure Redis response times or a reliable estimate of sensor overhead.

The second sensor run returned four measured PONGs, but only three connect events had timestamps inside the selected interval. Offline inspection found six connect events in the entire capture, including warm-up activity. One was timestamped 65.4 ms before the measured start. A clock-alignment problem is plausible, but the events cannot yet be confidently linked to individual commands. We did not move the boundaries to make the counts look better.

Earlier clock checks also failed. Temporarily stopping a guest time-synchronization service for explicitly approved experiments improved those checks; the service was restored afterward. This is not a permanent clock fix. **Do not disable time services by following this beginner guide.**

Latest improvement: every new measured PING now gets its own before/after clock readings. A test confirms that a temporary clock jump can be rejected even when the overall experiment's endpoint clocks agree. This does not align the sensor clock or retrospectively repair old results.

Detailed records: [Engine 1 baseline](ENGINE1_BASELINE.md), [paired results](PAIRED_PILOT_RESULTS.md), [event alignment](EVENT_ALIGNMENT.md), [incidents](INCIDENTS.md).

## 6. Before typing commands

Use a personal or explicitly approved research computer. Do not point the project at your college, employer or anyone else's servers. Do not deploy the deliberately weak example configurations.

Choose one route:

- **Existing research computer:** use the current project folder and environment; do not create another clone or replace the environment.
- **New Windows computer:** follow 6A, then 7.
- **New Linux computer:** follow 6B, then use the same demonstration commands with the Linux Python path.

The repository is private. Ask Manish for access before cloning. Permission to view it is not permission to redistribute it. Have Git and Python 3.11 or newer available before starting; an administrator can help install them. Docker is unnecessary for the first demonstrations. The project does not promise a universal minimum RAM/disk requirement; AI models and lab images can require several GB of downloads and additional memory.

Commands in code boxes should be copied without the surrounding backticks. Run each separately; stop at an error instead of continuing blindly. A command finishing normally usually returns you to the prompt. Never publish credentials or raw telemetry when asking for help.

### 6A. Windows PowerShell

Open PowerShell. Check installed tools:

```powershell
git --version
python --version
```

On a new checkout only, choose your parent folder using File Explorer, open PowerShell there, then:

```powershell
git clone https://github.com/ManishPatil2005/active-cloud-guard-honors.git
cd active-cloud-guard-honors
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
```

If you already use this research computer instead:

```powershell
Set-Location 'D:\research f1'
.\.venv\Scripts\python.exe --version
```

Do not recreate its existing .venv. This guide uses the environment's full Python path, so you do not need to activate it or loosen PowerShell execution policy. Installation requires network access; the offline demos do not download a model.

### 6B. Linux shell

For a new Linux checkout with Git, Python and venv support installed:

```bash
git clone https://github.com/ManishPatil2005/active-cloud-guard-honors.git
cd active-cloud-guard-honors
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
```

In all later Python commands, replace `.\.venv\Scripts\python.exe` with `.venv/bin/python`. Never copy a Windows virtual environment into Linux; create a Linux environment separately. Core/tests are verified on the recorded Ubuntu WSL setup; arbitrary Linux machines and full AI/vector installations are not all validated. For the existing ACG-Research environment, use [the recorded paths and setup](WINDOWS_LINUX_SETUP.md), not a fresh installation over it.

## 7. Safe demonstration: check installation

From the project root on Windows:

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest -q
```

Expected: no broken requirements; at this revision, **301 passed**. Newer revisions may have more tests. A failure means stop and inspect it; do not delete the test or change its expected answer merely to obtain a green result. Tests use controlled examples and mocks where appropriate; they do not prove that Docker or the AI model is currently working.

Record your checkout identity:

```powershell
git rev-parse HEAD
git status --short
```

The first command prints a revision fingerprint. The second prints changed/untracked files; empty output means a clean working tree. A different revision or environment can produce different results.

## 8. Safe demonstration: Engine 1 without AI

### Step 1 — Scan one prepared configuration

```powershell
.\.venv\Scripts\python.exe -m cloudguard.cli scan data/development/postgres-trust.yaml
```

Expected: JSON containing rule_id `AUTH001` and title `PostgreSQL trust authentication enabled`. The location explains where the setting was found. `origin: rule_baseline` means a defined rule, not an AI guess. This command reads the example; it does not deploy PostgreSQL or exploit a database. A score of 0.9 is a provisional score, not a measured 90% attack probability.

### Step 2 — Retrieve supporting guidance

```powershell
.\.venv\Scripts\python.exe -m cloudguard.cli retrieve "PostgreSQL trust authentication"
```

Expected: a list containing the `postgres-trust` source summary, its source URL and provenance fields. It retrieves local summaries; it is not a fresh internet search or proof that a model's conclusion is correct.

### Step 3 — Understand what you have shown

You have demonstrated a known rule and retrieval on a prepared example. You have not measured AI accuracy, independently validated a vulnerability, or proven that a real server is exposed. These two commands were rerun successfully when this guide was written.

## 9. Safe demonstration: Engine 2 without a live sensor

Run this one-line command:

```powershell
.\.venv\Scripts\python.exe -m cloudguard.cli runtime-replay data/runtime/observation-synthetic.json --baseline data/runtime/baseline-synthetic.json --inventory testbed/inventory.json
```

Expected: `status: observations_processed`, one window with `no_threshold_exceedance`, another with `deviation_for_review`, and `actions_executed: []`. At this revision, the constructed changed window has deviation_score 8.0. `source: synthetic` means the event data was deliberately invented for demonstration. `runtime_sensor_connected: false` means this replay command is not collecting live events. It does not mean the separate sensor-trial tools have never existed.

`threat_confirmed: false` is important: a count difference is not an attack diagnosis. `partial_or_unknown` means observation completeness is not established. No network connection, container launch or automatic response is performed by this replay command. It was rerun successfully for this guide.

### Save a separate replay-check report

```powershell
.\.venv\Scripts\python.exe scripts/runtime_check.py --output output/my-first-replay.json
```

Use that name only if it does not exist. On a second run use a new name, such as `my-second-replay.json`. The script refuses to replace an existing report. Open the file in your editor to inspect it. This optional saving command is supported by the repository; this guide did not create a file with that suggested name.

## 10. Read the real research evidence

You do not need Docker to open these existing files:

1. [Paired experiment summary](../output/engine2-paired-audited-20260929/summary.json): inspect `runs`, `pairs`, `independent_evaluation` and `sensor_cpu_memory_overhead`.
2. [Second-run alignment report](../output/engine2-on-2-alignment-20260930.json): inspect `event_regions` and `network_connect_offsets`. Negative offsets mean before the recorded start, not negative processing time.
3. [Windows timing-guard tests](../output/engine2-call-clocks-windows-tests-20260930.xml) and [Linux tests](../output/engine2-call-clocks-linux-tests-20260930.xml): machine-readable software-test records.
4. [Work log](WORK_LOG.md): what was done, why, commands, failures and limitations.
5. [Task ledger](../TASKS.md): what is complete, partial or still open.

The saved results came from the recorded research machine and specific dates. Reading them is evidence review, not rerunning their experiments. Raw sensor logs are intentionally not in GitHub; a fresh clone cannot reconstruct those logs from hashes. The minimized summaries are available for review.

## 11. Optional advanced route: AI and local lab

Do this only after sections 7–9 pass, on a disposable approved lab computer, with Docker Linux-container support available. Have a technical supervisor help if Docker or model setup is unfamiliar. These steps can download large images/models and start local services. They are not required to understand the research.

On a **new lab**, install vector support and create local credentials (values are not printed):

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[vector,test]"
.\.venv\Scripts\python.exe scripts/init_secrets.py
docker version
docker compose -f testbed/compose.yaml --profile ai up -d
docker compose -f testbed/compose.yaml ps
```

If the server section of `docker version` fails, stop: Docker is not ready. On an existing research lab, ask the owner before `up -d` because it can recreate containers if their definitions changed. Do not delete volumes or reset Docker to fix an unexplained error.

Download the local models and build the retrieval index:

```powershell
docker compose -f testbed/compose.yaml exec -T ollama ollama pull qwen2.5:3b
docker compose -f testbed/compose.yaml exec -T ollama ollama pull nomic-embed-text
.\.venv\Scripts\python.exe -m cloudguard.cli index
```

Run the restricted demonstration:

```powershell
.\.venv\Scripts\python.exe -m cloudguard.cli run data/development/redis-all.yaml --inventory testbed/inventory.json --model qwen2.5:3b --cache-dir output/audit-cache --max-tokens 512 --timeout 180
```

Read every warning and distinguish rule findings, AI candidates and network observations. The model may abstain or return rejected candidates. That is not proof that the input is safe. Repeating the exact request may reuse cached model work; network observations are still fresh. The command above uses default lexical retrieval; add `--vector-index output/chroma` to explicitly use the built semantic index. Model tags can change; compare recorded digests before claiming identical reproduction.

Stop this lab when finished, without deleting volumes:

```powershell
docker compose -f testbed/compose.yaml --profile ai stop
```

Only stop it when no other authorized experiment needs it. Keep credentials, .venv, caches, model weights and vector databases out of Git. The lab binds published ports to this computer's loopback interface, but is not fully isolated from outbound networking. Do not use real personal or institutional data.

These AI/lab commands follow the implemented workflow; they were **not rerun for this document**. Earlier live results are historical. See [README](../README.md) and [security boundaries](SECURITY.md) for details.

## 12. Live Engine 2 collection: supervised work only

Windows can be used for development and replay; the tested live sensor route uses Linux through ACG-Research WSL and Docker integration. A Python-only Windows replay is not the same as a Linux kernel sensor. Separate Linux installation details are in [Windows/Linux setup](WINDOWS_LINUX_SETUP.md).

Do not run sensor_trial.py or paired_pilot.py as a beginner shortcut. A supervisor must first verify the approved target, image digest, permissions, time-service policy, bounded duration, output location, resource limits and cleanup. The time-service stop/restore used in earlier tests was explicitly scoped; it is not general permission to disable synchronization. New per-call timing fields still need live validation and collector-clock alignment remains open.

The next supervised sequence is: review measurement design; verify prerequisites; collect a separately named bounded diagnostic if authorized; inspect all failures and cleanup; compare clocks without inventing event associations; only then plan repeated baselines. Do not fit an ML model to uncertain measurements or rename related samples to pretend they are independent.

## 13. If something goes wrong

| Symptom | First safe action |
|---|---|
| GitHub asks for access | Ask the owner to grant access; never share tokens in chat |
| Python or Git not found | Ask the computer administrator to install the missing prerequisite |
| Module not found | Check you are in the repository root and using its environment's Python |
| PowerShell activation blocked | Use the full Python path in this guide; do not weaken system policy |
| Tests fail | Save the command and error; record Git revision; stop before live work |
| Output file already exists | Choose a new filename; preserve the old observation |
| Docker unavailable | Start/check Docker through the approved setup; do not reset data |
| Model missing or slow | Check model/service availability; allow download time; do not call a timeout a clean verdict |
| Counts or clocks disagree | Keep the result, mark it uncertain and investigate; do not shift timestamps to force agreement |
| No findings / rejected candidate | Interpret it as limited coverage or abstention, not proof of security |

When asking for help, give: the step number, exact command, expected result, actual error, operating system and Git revision. Redact secrets and do not upload raw telemetry without review.

## 14. How to maintain a trustworthy research record

For each new change or experiment, write what you intended, what changed, the exact command, what actually happened, failures, limitations and next action. Keep old failed reports. Use a new filename for each run. Update WORK_LOG, MEMORY, TASKS and CHANGELOG together; update test/security/architecture documents when relevant.

Before publishing, run the repository checker, inspect the staged files and exclude secrets/raw telemetry. Commit only the intended work with a descriptive message. After pushing, compare local and remote revision IDs; a local commit alone is not a GitHub backup. This project's checks run locally; do not present them as hosted CI or peer review.

For a presentation, a defensible summary is: **“We have a tested configuration-review prototype and a bounded runtime-observation pipeline. We preserve evidence and failures. Independent detection accuracy, reliable sensor timing, general overhead and production readiness remain under evaluation.”**

## 15. What comes next?

1. Validate the new per-call timing measurements and establish collector-to-harness clock/correlation evidence.
2. Strengthen automated experiment/report validation and predeclare repeat counts and stopping rules.
3. Collect comparable, resource-instrumented samples with honest coverage accounting.
4. Obtain independent labels and a genuinely untouched grouped evaluation set.
5. Evaluate runtime models and compare Engine 1 alternatives fairly; report errors and abstentions.
6. Assess general latency, resource cost and sustainability before claiming improvements.

The project has made measurable engineering progress. It is not appropriate to claim “zero errors,” “all vulnerabilities detected,” or “research completed” from the current evidence.
