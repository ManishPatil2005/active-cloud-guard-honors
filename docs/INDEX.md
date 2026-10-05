# Documentation index

Latest result: [live kernel state](KERNEL_CLOCK_STATE.md), one16-packet/32-query observation: tick/frequency change alongside RAW/MONO gap~0.46324s and wall/BOOT change~0.867156s. INC-039; no actor/cause/stability/ML acceptance or settings intervention. Next exact writer review and separately approved comparison design.

Latest implementation: [live kernel-state diagnostic](KERNEL_CLOCK_STATE.md), separate Linux-only ordinary-user zero-mode queries/native clocks. One fixed sensor-free observation predeclared after publication; no clock/service change, causal fix or stability/ML acceptance.

Latest result: [raw-clock/provider diagnostic](CLOCK_PROVIDER_REVIEW.md), one sixteen-packet run: RAW host-compatible15/15, adjusted elapsed comparisons disagree11/15, local RAW/MONO advance differs~0.5674s and wall/BOOT relationship changes~0.3167s. INC-037; cause/stability/ML unresolved, next read-only live discipline-state sampling.

Latest review/implementation: [provider facts and raw-clock protocol](CLOCK_PROVIDER_REVIEW.md): two sync paths enabled, current tsc provider, cached NTP frequency distinguished from live kernel state. Opt-in RAW/adjusted/host comparison implemented, one separate observation pending after publication; cause/stability remain open.

Latest result: [Windows/WSL clock lineage](CLOCK_LINEAGE.md), sixteen completed sensor-free packets but 13/15 elapsed comparisons disagree beyond delay bounds. WSL native clock relationships stable during sampling; cause unproven (INC-036), timing/ML gates open.

Latest implementation/protocol: [Windows/WSL clock lineage](CLOCK_LINEAGE.md), a read-only fixed sixteen-snapshot observation with native boot/monotonic clocks and delay-aware host intervals. One observation pending after implementation publication; no clock changes or resolved-cause claim.

Latest result: [recorded collector-on boot/TIME follow-up](RECORDED_BOOT_CLOCK_FOLLOWUP.md), one compatible 27-sample trial. Exploratory between-run relationship change (+123.10316 s) remains unexplained; long-term timing gate still open (INC-034).

Latest implementation/protocol: [collector-on boot/TIME recording](RECORDED_BOOT_CLOCK_FOLLOWUP.md), native endpoints retained before rejection; one new bounded follow-up predeclared, live pending at this checkpoint.

Latest observation: [sensor-free TIME result](SENSOR_FREE_TIME_ATTEMPTS.md), one run six accepted reads; full offline consistency checks passed. No rejection reproduced or Falco alignment conclusion; timing gate remains open.

Latest planned diagnostic: [sensor-free TIME attempts](SENSOR_FREE_TIME_ATTEMPTS.md), shared sanitized recording and six-read/five-gap protocol. Implementation live result pending at this checkpoint; timing gate unresolved.

Latest software fix: [sanitized TIME failure evidence](CLOCK_DOMAINS.md), 414 tests each OS. Failed attempt remains preserved; no live rerun or timing-stability claim. Next sensor-free bracket diagnostic design.

Latest observation: [boot-clock attempt and partial review](BOOT_CLOCK_DIAGNOSTIC.md) stopped at its second TIME bracket; one measured PING/five boot samples retained, no full stability result. Next failed-bracket evidence retention; INC-033.

Latest implementation: [namespace-gated boot-clock diagnostic](BOOT_CLOCK_DIAGNOSTIC.md), 407 tests each OS; one live trial predeclared, not yet executed at this checkpoint. Timing gate remains open.

Latest source review: [pinned collector timestamp path](COLLECTOR_TIMESTAMP_REVIEW.md), initialization boot-offset mechanism traced; causal drift still unproven, no clock intervention.

Latest diagnostic: [same-trial clock-domain comparison](CLOCK_DOMAINS.md), server/harness compatible but four collector events outside both brackets; collector cause still unresolved.

Latest evaluation: [three-trial repeatability studies](READINESS_REPEATS.md): 5 October follow-up launched all three, two accepted and third timing-rejected. September interruption remains preserved; stability gate still unmet.

Latest sensor diagnostic: [process-ID correlation](PID_CORRELATION.md), including successful measured matches and remaining warmup coverage uncertainty.

Latest diagnostic: [Redis-to-harness clock bridge](CLOCK_BRIDGE.md), a bounded live read-only check, not Falco calibration.

Nontechnical starting point: [Progress Execution](<Progress Execution.md>) — research explained, current progress, safe beginner demonstrations, optional lab setup and result interpretation.

Latest follow-up: [offline event alignment investigation](EVENT_ALIGNMENT.md); no new workload, no retrospective boundary correction.

Latest experiment review: [audited paired pilot results](PAIRED_PILOT_RESULTS.md), including the unresolved interval-count discrepancy.

Start here when reviewing or continuing the project. The owner is Manish Patil; repository: [active-cloud-guard-honors](https://github.com/ManishPatil2005/active-cloud-guard-honors), private.

| Document | Purpose |
|---|---|
| [PRD](PRD.md) | What the research prototype must do and why |
| [Architecture](ARCHITECTURE.md) | Existing stack, modules, flow and boundaries |
| [Engine 1 v2](ENGINE1_V2.md) | Repeat-work efficiency, budgets, cache contracts and reproduction |
| [Engine 1 refinement](ENGINE1_REFINEMENT.md) | V2.1 reviewed verification, operator templates, results and remaining gates |
| [Engine 1 baseline](ENGINE1_BASELINE.md) | V2.2 local deployment identity and bounded Redis/PostgreSQL checks |
| [Engine 2 foundation](ENGINE2_FOUNDATION.md) | Observation-only replay contract, statistical baseline, evidence and sensor prerequisites |
| [Engine 2 sensor trial](ENGINE2_SENSOR_TRIAL.md) | Bounded live Falco observation, failed attempts, privileges, tests and remaining integration gates |
| [Engine 2 adapter](ENGINE2_ADAPTER.md) | Offline raw-event validation, minimized normalized capture, accounting and remaining coverage gates |
| [Engine 2 instrumentation](ENGINE2_INSTRUMENTATION.md) | Event-observed readiness, selected identity continuity and collector-wide loss counters |
| [Runtime workload protocol](RUNTIME_WORKLOAD_PROTOCOL.md) | Fixed measured profiles, timing gates, preserved pilot failure and next control experiments |
| [Clock and controls](CLOCK_AND_CONTROLS.md) | Bracketed diagnostics, reproduced timing failure and deferred sensor-off controls |
| [Clock domains](CLOCK_DOMAINS.md) | Opt-in server TIME/PING/TIME diagnostic, precise event bounds and preserved negative result |
| [Sensor-free TIME attempts](SENSOR_FREE_TIME_ATTEMPTS.md) | Opt-in rejected-bracket evidence, bounded six-read protocol and outcome limits |
| [Boot-clock diagnostic](BOOT_CLOCK_DIAGNOSTIC.md) | Native boot/realtime sandwiches, namespace comparability gates and separate single-trial protocol |
| [Recorded boot-clock follow-up](RECORDED_BOOT_CLOCK_FOLLOWUP.md) | Boot_v2 TIME endpoints including rejected reads and separate collector-on protocol |
| [Collector timestamp review](COLLECTOR_TIMESTAMP_REVIEW.md) | Pinned local versions, official source hashes, timestamp mechanism and unproven cause |
| [Time-sync diagnosis](TIME_SYNC_DIAGNOSIS.md) | Read-only evidence of competing synchronization paths and proposed reversible test |
| [Paired pilot](PAIRED_PILOT.md) | Fixed warm-up, comparison guards, aborted batch and prerequisite recovery |
| [Windows/Linux setup](WINDOWS_LINUX_SETUP.md) | Installed research WSL distribution, actual Linux preflight, Docker integration handoff and sensor gates |
| [Interface design](DESIGN.md) | CLI/output contracts; no proposed web redesign |
| [Rules](../RULES.md) | Implementation, evidence and Git rules |
| [Working agreement](../AGENTS.md) | Required context and maintenance for future work |
| [Tasks](../TASKS.md) | Completed, partial, open and deferred work |
| [Decisions](DECISIONS.md) | Durable decisions and consequences |
| [Current state](MEMORY.md) | Current capabilities, limits and next steps |
| [Test plan](TEST_PLAN.md) | Checks, commands, evidence and interpretation |
| [Security](SECURITY.md) | Probe limits, secrets, model trust and publication policy |
| [Work log](WORK_LOG.md) | What changed, how, verification and unresolved work |
| [Incident ledger](INCIDENTS.md) | Symptoms, diagnoses, fixes and remaining limits |
| [Evidence index](EVIDENCE.md) | Saved observations and what each can establish |
| [Documentation workflow](DOCUMENTATION_WORKFLOW.md) | Required updates per change and reusable templates |
| [Changelog](../CHANGELOG.md) | Human-readable change history |
| [Run instructions](../README.md) | Setup, operation and reproducibility |
| [Deck audit](DECK_AUDIT.md) | Slide-by-slide interpretation and corrections |
| [Experiment protocol](EXPERIMENT_PROTOCOL.md) | Independent scientific evaluation plan |
| [Literature audit](LITERATURE.md) | Source verification levels and uncertainties |
| [M1-3 acceptance ledger](MONTHS_1_TO_3.md) | Engineering milestone versus research gates |
| [Measured status](../output/RESEARCH_STATUS.md) | Generated summary of saved experimental evidence |
| [Source provenance](source/README.md) | Original deck and content hash |

Authority: explicit user requests govern scope; actual source code and saved observations determine implementation status. A plan is not evidence of execution. `MEMORY.md` describes current state; `WORK_LOG.md`, `INCIDENTS.md`, `DECISIONS.md` and Git preserve history. Do not rewrite old observations to match a later implementation.
