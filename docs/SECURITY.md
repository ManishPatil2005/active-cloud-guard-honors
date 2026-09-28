# Security boundaries and publication policy

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
