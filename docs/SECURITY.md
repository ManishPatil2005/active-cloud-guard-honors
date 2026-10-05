# Security boundaries and publication policy

Raw-clock lineage adds native reads only, fixed child --raw-clock flag and distinct receipt protocol. No direct timex/clock adjustment, new sysfs paths during sampling, installs, service/power/provider changes or extra privileges. Same strict JSON/domain/source/partial-evidence/redaction/exclusive gates. Provider review uses selected read-only sysfs/D-Bus/service/CIM facts; no hostnames, IPs, NTP addresses or interop socket IDs published. Cached frequency/local flags do not authenticate clock accuracy; CLOCK_PROVIDER_REVIEW.md.

E2-023 clock lineage uses one fixed WSL command vector and native/allowlisted proc/source reads. No shell interpolation, credentials, network, Docker/sensor launch, clock setting, power setting or service control. Save only validated guest facts plus available host samples/class/stage; malformed replies/raw stderr/error messages excluded. Boot UUID hashed, not exported. Exclusive output prevents replacement; complete offline review is local consistency, not authenticated attestation. Diagnostic-only timing limits do not weaken other engine gates; CLOCK_LINEAGE.md.

Boot_v2 adds only local native clock reads around existing fixed TIME calls, no new proc paths, privilege, mounts or endpoints. Numerical endpoints saved before validation; raw reply/error messages remain excluded. Early boot sampler failures preserve safe stage/class and available fields; no fabricated calibration value. Same namespace gate/sensor limits; source hashes distinguish changed instrumentation and old evidence is not rewritten. RECORDED_BOOT_CLOCK_FOLLOWUP.md.

Sensor-free record-attempts mode uses only existing local-daemon/single lab Redis identity gates and fixed loopback TIME commands. Checks known sensor name/image absence at endpoints (not all possible collectors). No container creation, service/clock action, credentials or data writes. Shared recorder preserves numeric fields/hash/stage/class only; six reads maximum/five gaps, existing timeouts/gates. Source hashes are local integrity checks, not authenticated provenance. No correction or permission for ML/baseline acceptance; SENSOR_FREE_TIME_ATTEMPTS.md.

TIME failure evidence exports numeric clock samples, fixed phase/stage/rejection labels, response SHA256 and exception class only. Never publish raw TIME reply, exception message, command stderr or command text; tests assert sentinel details absent in malformed-reply/command/sampling failures. Same fixed local commands/limits, no new access. Hash is integrity metadata, not authentication. Failure at an early stage legitimately leaves later fields absent; do not infer missing values.

Boot-clock mode adds only fixed readlink/cat reads of /proc/self/ns/time, /proc/self/ns/time_for_children, /proc/self/timens_offsets and /proc/sys/kernel/random/boot_id in harness/selected Redis/sensor domains. Boot ID exported as SHA256 only; no proc writes, added privileges/mounts, runtime helper installation, settings changes or new endpoint. Active/children equality prevents offset misattribution. Same bounded sensor/watchdog; extra execs affect collected activity. Facts are local/non-authenticated and do not authorize correction or baseline promotion. Raw logs remain excluded; BOOT_CLOCK_DIAGNOSTIC.md.

Collector source reviewer runs only pinned-image --version, no mounts/network/capabilities, read-only filesystem, --pull never and fixed resource limits. Six official immutable HTTPS sources are size/timeout bounded, hashed but never executed/vendored. Minimized metadata does not publish startup stderr/configuration; overwrite/mismatch/failure refused and retained. This is not a sensor run, signature/build attestation or authority to adjust timestamps/clocks. Timeout cleanup of the short-lived metadata container is not exhaustively tested. See COLLECTOR_TIMESTAMP_REVIEW.md.

Clock-domain mode performs exactly eight read-only Redis TIME commands in the existing identity-gated loopback lab, before/after four identified PINGs; no credentials, application-data access/write, new endpoint, permission or clock-service action. Same Falco capabilities/watchdog. Partial rows and auxiliary unassigned connects retained; new diagnostic label excluded from old repeat/latency protocols. Numerical bounds/PIDs/hashes are not attestation or permission for timestamp correction. Raw logs remain excluded; source hashes validate bytes, not authority. See CLOCK_DOMAINS.md.

Repeat runner keeps existing sensor permissions/duration and uses fixed child arguments only. Three planned trials maximum, pre/post local readiness, no replacements or clock changes. Source/receipt hashes are integrity metadata, not authentication. On timeout the sensor watchdog still applies; inspect cleanup before any further workload. Raw logs remain excluded.

Identified readiness reuses the strict bounded correlation parser and requires the current second canary PID's unique successful connect, not arbitrary earlier events. Snapshot hashes/counts are preserved without exporting command text. No new privilege or network scope. PID matching remains non-authenticated and readiness is a point-in-time observation, not uptime/coverage assurance.

Warmup v2 reuses the fixed PID-print/exec-PING helper for two readiness commands, without new exported fields or privileges. Diagnostic IDs must be six distinct positive integers; missing warmup remains visible. Recovery starts existing Docker/Redis only; no data reset or time-service changes. PIDs remain bounded local correlation, not authenticated identities.

Opt-in PID diagnostic adds only proc.vpid, using a fixed non-user-interpolated shell program that prints its PID then execs loopback redis-cli PING. No command-line/environment/path output, extra capabilities, mounts, network endpoints or clock changes. Raw diagnostic logs remain ignored. Container/PID association is not authenticated and does not defeat PID reuse; ambiguity rejects the result. Ordinary adapter rejects the extra field and paired reports reject diagnostic receipts.

Clock bridge permits only six fixed Redis TIME reads via existing-container loopback redis-cli, gated by local daemon, exact lab selection, selected identity and known-sensor absence. No arbitrary commands/destinations, credentials, Redis data writes, time-service changes or added capabilities. TIME causes small lab process/network activity. Bounds/identity remain non-authenticated observations.

Paired-report timing validation recomputes clock evidence and refuses inconsistent or mixed instrumentation. It grants no new access and does not authenticate operator-supplied receipts. Full initial-gate/manifest binding and identity-schema validation remain separate limitations.

Per-call clock instrumentation only reads clocks around existing approved PING callbacks; it changes no time service, privilege or target. Beginner guidance separates offline demonstrations from supervised live collection and does not authorize permanent time-service changes.

30 September offline alignment diagnostics reuse strict bounded hash-validated normalization and export only event counts and relative connect timestamps. No raw commands, host metadata, new access or service changes. Relative times remain research metadata requiring review; offsets are not authenticated clock/correlation evidence. Historical artifacts remain unchanged.

Paired pilot adds fixed two-PING warm-up and bounded four-run orchestration, with no broader sensor capabilities. Prerequisite preflight must precede approved guest-NTP stop; restoration remains external try/finally with explicit state checks. Docker/Redis recovery started existing services only. No control/sensor workloads were retried after batch abort. Manifest hashes are provenance, not authentication; comparisons remain observation-only.

Clock/control tooling reads clocks without changing settings. Sensor-off controls perform only existing Redis PINGs and selected Docker identity/known-sensor checks; never stop unrelated collectors or fabricate telemetry. A passing clock report is operator-declared input, not authenticated/fresh evidence. The actual failed diagnostic blocked planned controls; no new sensor or host service change occurred.

Measured workload update (29 September): profiles permit only one or four fixed loopback Redis PING commands over four seconds, plus existing bounded readiness canaries. No arbitrary workload commands or destinations. Sensor privileges/watchdog unchanged. Timing-invalid runs fail and retain evidence; wall-clock alignment and Docker identity are not authenticated. No new network endpoints or persistent monitor.

Instrumentation update: fixed PING readiness canaries (maximum three) and final PING affect only existing lab Redis. Pre/post inspection exports selected identity fields, not credentials/environment. Metrics are written inside the isolated sensor then copied to the ignored raw directory; default metrics may contain host/network metadata, so only allowlisted counter summaries are published. No extra privileges, host mounts or network endpoints. Identity continuity is not cryptographic attestation. See ENGINE2_INSTRUMENTATION.md.

Offline adapter update: untrusted saved logs are size/record bounded, receipt-hash checked and schema validated; no content is executed. Published capture omits raw output/cgroup strings but retains lab identities/timestamps. Receipts and operator asset mappings are not authenticated. Rejected records block capture output; diagnostics cannot establish sensor completeness. See ENGINE2_ADAPTER.md.

Latest (28 September): a bounded Falco trial was run and removed; earlier sensor-absent statements are historical. It grants BPF/PERFMON/SYS_RESOURCE/SYS_PTRACE and read-only proc/tracing mounts, without privileged mode, host PID namespace, Docker socket or network. Filtering is not kernel isolation. Raw logs remain ignored/publication-blocked; summaries contain identities/hashes/counts. Watchdog/resource/log ceilings do not prove completeness. Digest pinning is not signature verification. No permanent collector or automated response. See ENGINE2_SENSOR_TRIAL.md.

## Research execution

ACG-Research is a separately registered Ubuntu WSL distribution with password-locked acgresearch user, no sudo membership. This is not a hardened boundary: WSL distributions share a kernel and standard Windows drive mounts remain accessible. Docker WSL integration was enabled on 28 September at the user's request and grants daemon management access, not read-only access; the account is therefore not a least-privilege Docker reader. No sensor, privileged container or new Docker daemon installed. See WINDOWS_LINUX_SETUP.md.

Engine 2 preflight inspects fixed path metadata and platform facts only, without privilege changes, driver loading or process execution. OS/kernel details need review before public sharing. Running inside a namespace/container does not establish host capabilities. Sensor installation and permissions remain a separate explicitly scoped setup decision.

Only declared localhost lab endpoints are eligible for probes. IPs are literal loopback addresses and endpoints are allowlisted; no DNS rebinding path or model-directed arbitrary network scan is provided. TCP outcomes do not validate credentials or prove Internet exposure. The current lab bridge permits outbound traffic.

IaC and retrieved text are untrusted data. No model output is executed as shell code. Model transport uses the local Ollama endpoint, bypassing system HTTP proxies. Schema, source membership, exact locations and two narrow policy guards constrain output, but human entailment review is still necessary. No automatic isolation or deployment decision is implemented.

## Secrets and data

Real lab credentials are generated locally, never printed and never committed. PostgreSQL/MinIO use secret files; synthetic `fixture-only` credential values in test fixtures are intentionally nonfunctional labels, not account credentials. Keep `.env*`, `testbed/secrets/`, local environments and caches out of Git. The original deck contains the researcher's identity and is included only in the private research repository.

Commit reproducible code, labels, official-source summaries, dependency lock, documentation and reviewed experiment outputs. Do not commit Chroma database files, model weights or Docker volumes; record identities and rebuild instructions instead. Saved evidence contains local machine paths/platform details; repository visibility is private. Review these before any public release.

## Residual risks

Engine 2 replay treats telemetry as untrusted structured data. Unknown fields (including commands), oversized/duplicate records and unbound assets are rejected. No sensor input is executed or used as a network destination; the runtime module has no action path. Source/container bindings are declarations, not authenticated evidence. Missing windows are not normal behavior. Keep raw telemetry in ignored/publication-blocked output/runtime-raw/ until reviewed and redacted. Observation scores are not threat probabilities or isolation authority.

V2.2 `verify-service` trusts a local Docker daemon and selected inspect fields/Compose hashes. It rejects remote contexts and never prints resolved secrets. Only credential-free Redis PING or PostgreSQL startup is sent to a matched loopback endpoint; no AUTH/password, SQL, application data access or configuration write. Server logs can be generated. Mounted-file/application state and malicious-admin resistance are not attested. No outcome is a complete authorization/vulnerability verdict. See ENGINE1_BASELINE.md.

V2.1 policy/review files are trusted operator authority; a reviewer label is not authenticated. Never accept model-authored approvals automatically. They authorize only TCP observations at validated inventory endpoints. Hashes prevent stale-document reuse, not malicious approval forgery or proof of deployment equivalence. No policy outcome suppresses a finding. Review documents have no TTL; operators must renew review when deployment or intended access changes. See [contracts and examples](ENGINE1_REFINEMENT.md).

V2 audit caching is opt-in. Generated responses may echo sensitive configuration even though request prompts are not persisted in cache records. Use a private local directory; `output/audit-cache/` is ignored and rejected by the publication checker. A custom cache location needs equivalent exclusion. Checksums are not authentication; do not share or import untrusted cache/vector databases. TTL controls reuse, not secure erasure. Generation limits and socket timeouts are resource controls, not hard server-compute cancellation. See [v2 contracts](ENGINE1_V2.md).

The scanner is partial. Current guards do not eliminate hallucinations. Historical pinned container images are not certified current or vulnerability-free. The model API has no application authentication and must remain loopback-bound. Disposable storage is unsuitable for important data. Source-ID checks are not proof that a source entails a finding.

Never broaden access, publish publicly, expose a service, run against a production account, or enable autonomous response as an incidental documentation change. Record security-relevant decisions and unresolved risks in the work log.

## Reporting

For this private research project, report problems directly to the owner/reviewer through the agreed channel; no public disclosure process or security support guarantee is established. Do not put working secrets or third-party sensitive data in GitHub issues or commits.
