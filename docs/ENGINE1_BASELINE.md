# Engine 1 v2.2: bounded service-verification baseline

Date: 2026-09-23. Package 0.4.0. This baseline closes the two implementation prerequisites for beginning an observation-only Engine 2 **within the existing Redis/PostgreSQL lab scope**. It is not full deployment attestation or research validation.

## What is verified

New command:

```text
python -m cloudguard.cli verify-service testbed/compose.yaml --inventory testbed/inventory.json --service redis
python -m cloudguard.cli verify-service testbed/compose.yaml --inventory testbed/inventory.json --service postgres
python scripts/service_check.py --output output/service-new-observation.json
```

The path must be the actual Compose definition, not one of the seeded development analogues. The workflow scans that file, captures its byte hash, and checks:

- Exactly one running container for the selected Compose service.
- Project/service labels and current Compose service configuration hash.
- Resolved local image identity, explicitly declared command/entrypoint and environment.
- Declared versus actual published ports and exact inventory endpoint mapping.
- Loopback publication and unprivileged container state.
- Source and resolved configuration stability during collection.

Checks run again after the protocol observation. Changed container identity/start time, image, inventory, source or service hash invalidates attribution. A mismatch before probing prevents the protocol probe. The report retains observations invalidated by later drift, with `usable: false` rather than silently assigning them to the configuration.

## Trust boundary and remaining identity limits

This trusts the local Docker daemon and Compose labels. Remote TCP/SSH Docker contexts are rejected. It is **not cryptographic or hardware attestation** and cannot defend against a malicious local administrator. It does not prove mounted-file contents, database state, effective Redis ACLs, pg_hba contents, or every runtime property matches intent. Default image commands are covered by image identity, not by independent process inspection. A short-lived change between observations can escape detection.

`identity_verified` means the documented selected checks matched. It must not be substituted for the v2.1 policy field `deployment_equivalence_verified`, which remains false. The new command has its own directly collected evidence; it does not trust an imported report to authorize a probe. The existing inventory-only pipeline remains a lower-evidence path.

## Protocol checks

Redis sends exactly one RESP `PING`, without AUTH. Outcomes distinguish PONG without credentials, NOAUTH, protected-mode denial, command permission denial, unreachable and inconclusive. PONG establishes only permission to run PING, not permission to read/write data.

PostgreSQL sends a protocol 3.0 startup request for the fixed lab role/database `postgres`, then stops after the first bounded response. Outcomes distinguish an authentication challenge, AuthenticationOk before any supplied credential, rejected startup, unreachable and inconclusive. No password, SQL query, brute force or database read is performed. An AuthenticationOk response is not a demonstrated query/session authorization and does not by itself prove a `trust` configuration. This check does not assess TLS.

Reads are frame-bounded and use a two-second network deadline. Docker subprocess calls have separate 20-second timeouts; total command time includes multiple identity inspections and is not a two-second end-to-end guarantee. Failed Docker commands return a generic error without echoing potentially sensitive configuration. Raw database/Redis response bodies and resolved environment values are not saved. Protocol handshakes may create ordinary server logs.

These results remain observations, not vulnerability confirmations. They do not suppress findings or change provisional scores.

## Actual observations

| Service | Deployment identity | Credential-free observation |
|---|---|---|
| Redis | All selected checks matched before/after | Protected-mode denial |
| PostgreSQL | All selected checks matched before/after | SASL authentication challenge |

Evidence: [final service observation](../output/service-identity-v22-final.json). [Initial observation](../output/service-identity-v22.json) is preserved; final rerun added local-context and protocol-framing hardening, not a change to the services. No container or application configuration was modified. Both observations ran against the original declared loopback lab, not a fake protocol server.

Software checks: [168-test report](../output/engine1-v22-tests.xml), Ruff lint/format, dependency consistency and publication checks. Unit tests cover command/env/image/config/port/running-state drift, malformed/fragmented responses, authentication outcomes, unsupported endpoints, remote daemon rejection, mismatch-before-probe and restart-after-probe. Rejected/credential-free accepted alternatives are unit-tested, not live weak-auth deployments.

## Freeze and next gate

Freeze this coherent Engine 1 revision in Git before Engine 2 work. The baseline remains reproducible with retained code, reports and historical failures. Tag/commit verification belongs in the publication receipt; this document does not invent a future commit ID.

Next: an observation-only runtime ingestion/windowing baseline, with no automated isolation, no fabricated sensor capture and no independent ML accuracy claim. Independent labels, matched baselines, broader service policies, full application-state checks and latency/resource evaluation remain necessary.

## Primary technical references

- [Docker Compose config](https://docs.docker.com/reference/cli/docker/compose/config/): resolved configuration and service hashes.
- [Redis PING](https://redis.io/docs/latest/commands/ping/): fixed non-data command.
- [PostgreSQL protocol formats](https://www.postgresql.org/docs/current/protocol-message-formats.html): startup and authentication response interpretation.
