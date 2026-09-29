# Decision register

## ADR-023 - 2026-09-29 - Sampling uncertainty and explicit sensor-off mode

Bracket wall reads with monotonic samples and reject excess uncertainty without widening existing disagreement tolerance. Sensor-off controls reuse fixed profiles but never emit synthetic sensor records or an unearned overhead estimate. Require a passing operator clock receipt before Docker access and preserve planned run deferrals/failures. Clock service changes and disruptive WSL actions are not incidental experiment steps.

## ADR-022 - 2026-09-29 - Declared workload intervals and timing abstention

Use fixed credential-free schedules within four-second measured intervals after readiness, retain both wall and monotonic timing, and reject unsuitable timing rather than silently relabel it. Preserve failed attempts and related scenario grouping. Exact temporal filtering does not prove causal attribution. Docker-exec round-trip time is not sensor overhead. A failed pilot cannot be replaced until a favorable pair appears; future repeated/control runs require a separately declared protocol.

## ADR-021 - 2026-09-28 - Observed readiness and separate collector metrics

Require observed selected process/network records during bounded fixed canaries, rather than liveness alone. Compare minimal pre/post Docker identity; retain unauthenticated mapping. Keep metrics in a local sensor file and publish only hash-bound counter summaries. Collector-wide drops are distinct from Redis event accounting; retain unknown coverage even when counters report zero. Canary attempts stay declared as development workload, not independent benign data. See ENGINE2_INSTRUMENTATION.md.

## ADR-020 - 2026-09-28 - Fail-closed offline adapter and unknown loss

Extend the existing normalized contract without changing Engine 1 or runtime scoring. Bind saved raw bytes to a successful pinned-trial receipt; require exact accepted-count agreement and reject the entire capture on invalid records. Minimize fields and keep stable projected event IDs; reject indistinguishable duplicate projections rather than assume they are retransmissions. Parser accounting is distinct from unmeasured sensor loss. No baseline score from one development smoke. See ENGINE2_ADAPTER.md.

## ADR-019 - 2026-09-28 - Bounded sensor before integration

Use a digest-pinned Falco modern-eBPF experiment harness, not a permanent collector or architecture replacement. Filter by full Redis cgroup ID without Docker socket, disable network/sensitive fields, keep raw logs local and publish hashes/counts. Filtering is not kernel isolation or authenticated deployment identity. Keep coverage unknown and replay disconnected until adapter/loss gates pass. Preserve failures. See ENGINE2_SENSOR_TRIAL.md.

## ADR-018 - 2026-09-25 - Dedicated WSL research distribution

After user requested proceeding on Windows, install separately named Ubuntu-24.04 as ACG-Research, with disk outside Git and unprivileged password-locked user. Preserve Windows/Docker Desktop and global WSL defaults. Separate distribution is not hardened isolation: WSL shares a kernel and automounts Windows files. No second Docker daemon, sensor install, custom kernel or blanket privileged collector. Use Docker's documented explicit distribution integration, requiring owner setting, then independently validate sensor visibility. Actual host preflight is live evidence; it cannot establish eBPF compatibility or completeness. Extends ADR-017; architecture unchanged.

## ADR-017 - 2026-09-25 - Host facts before sensor provisioning

E2-003 inspection found Windows with only stopped Docker-managed WSL and no responding Docker daemon. Add read-only local preflight rather than install a privileged collector implicitly. Marker presence never certifies compatibility. No sensor selected yet; a user-supplied or explicitly approved research Linux environment and sensor-specific privilege plan are required. Linux branches use mocked software tests only. Engine 1 and the Python/Docker/Ollama/Chroma architecture remain unchanged.

## ADR-016 - 2026-09-25 - Observation-only Engine 2 foundation

Freeze Engine 1 before runtime changes. Start with a strict normalized capture contract and transparent standardized-count comparator using existing dependencies, not immediate sensor installation/ML claims. Preserve the planned eBPF/Kubernetes and Isolation Forest/autoencoder path as explicit next work. Require separate declared groups/event records for baseline versus observations and expose unknown coverage. No zero-filling gaps, automated actions, threat confirmation or TCI integration. This makes the future sensor/ML path testable without representing synthetic data as real telemetry.

## ADR-015 - 2026-09-23 - Bounded identity and protocol verification

Before Engine 2, bind observations to the actual Compose source using local daemon checks and pre/post identity comparison. Add only fixed credential-free Redis/PostgreSQL protocol exchanges, separate from the lower-evidence generic TCP pipeline. Do not weaken the testbed to manufacture findings or silently label selected identity checks as full runtime attestation. No score/suppression change. This supports a reproducible Engine 1 freeze while leaving application-state verification and independent evaluation open.

## ADR-014 - 2026-09-23 - Reviewed verification before broader automation

Keep the stack and existing rule scoring. Add strict hash-bound operator policy and model-candidate approval, restricting execution to existing loopback TCP probes. Require digest-bound model requests and exact retained candidate fingerprints. Treat operator deployment equivalence as an assertion, not machine attestation; label it false in verified-equality fields. Model evidence remains unscored/review-required; expected reachability never clears unrelated risk. This prioritizes provenance and reviewability over unsupported automated actionability. Authentication-aware probes, independent labels and deployment attestation remain future work; see ENGINE1_REFINEMENT.md.

Entries below document decisions made during the initial implementation on 2026-09-23. This is a retrospective record; no earlier Git commits or approval dates are implied.

| ID | Decision and reason | Consequence / status |
|---|---|---|
| ADR-001 | Preserve Python CLI/library plus Docker, Ollama and Chroma, following the research deck | Current architecture; user explicitly reaffirmed preservation |
| ADR-002 | Scope the present milestone to M1-3/early Engine 1 | Runtime ML, isolation and full-system benchmarking remain later work |
| ADR-003 | Keep candidate configuration issues distinct from reachability and actionability | TCP acceptance is not proof of authentication bypass or public exposure |
| ADR-004 | Replace the ambiguous negative reachability adjustment with a monotonic provisional policy | Exposure cannot reduce risk; calibration still required |
| ADR-005 | Keep refused/inconclusive evidence from erasing static findings | Conservative behavior may not reduce FP counts; that remains a hypothesis |
| ADR-006 | Implement lexical retrieval alongside Chroma local embeddings | Supports future ablation; nine summaries are only an initial corpus |
| ADR-007 | Preserve failed 1.5B runs and use 3B for final smoke checks | Model selection was development tuning; no held-out claim; latency increased |
| ADR-008 | Check exact input locations and add narrow deterministic auth corroboration | Rejects observed unsupported claims; does not establish general semantic correctness |
| ADR-009 | Use a dedicated bridge with localhost publishing after internal-network port mapping failed | Live checks work; outbound traffic is permitted and documented |
| ADR-010 | Scan supported Trivy fixtures independently with bundled checks and networking disabled | Avoids merging Terraform cases or policy-update incompatibility; rule coverage differs |
| ADR-011 | Commit raw evidence, synthetic fixtures, source deck and documentation; exclude secrets/caches/weights | Repository is reproducible without publishing generated credentials |
| ADR-012 | Create a private GitHub repository by default | Avoids an unrequested public research release; no open-source license inferred |

Supersede decisions with a new entry linked to the old ID. Record rationale, consequences and verification; do not silently rewrite the historical rationale. Architecture changes require the owner's authorization.

## ADR-013 - 2026-09-23 - Engine 1 v2 repeat-work efficiency

Use opt-in exact-request response caching, content/model-addressed index reuse, bounded generation and explicit stage timings. Preserve ADR-001/002/008: same stack, Engine 1 scope and review boundaries. Revalidate cached output; never persist probe decisions for reuse. Avoided model work is measurable, whereas energy savings are not measured here. Default one-hour/128-entry local cache bounds sequential storage; no distributed cache or new service dependency. See ENGINE1_V2.md for tradeoffs and acceptance criteria.
