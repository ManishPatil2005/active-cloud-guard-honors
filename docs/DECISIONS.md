# Decision register

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
