# Recommended portable profile promotion

QA-012/WL-086/ADR-074, 9 October 2026. This promotes a documented source-tree setup, **not the installed historical environments**, an engine version or production approval.

## Acceptance and implementation

- `requirements-core-current.txt` includes the unchanged dated portable profile qualified in QA-011, retaining its exact pins and shared synthetic ML snapshot.
- The package test extra now selects pytest9.0.3. Vector remains Chroma1.0.20 and runtime-ML remains scikit-learn1.9.1; no engine algorithm or architecture change.
- README recommends a fresh ignored directory, hash-pinned pip bootstrap and wheels-only installation. Both shell examples refuse an existing environment destination. Source-tree execution does not imply an editable package build or fresh-host qualification.
- Historical locks, original environments, model weights, vector databases and Engine1 tag remain untouched. Existing hook interpreter selection remains unchanged and may use historical `.venv`; it does not attest a patched environment.
- Three additional contract tests enforce profile reuse, test/vector/ML boundaries and the recommended setup's exclusion of the old combined vector/test default.

## What an operator can do

Follow README Reproducibility steps1–2 from the repository root. Pick a new environment and smoke output filename. Installations need network access; software checks do not need live Docker or Ollama. Inspect the smoke: absent vector dependencies are explicitly unqualified, not repaired. Stop on failure and retain its receipt before selecting another output name.

The source-tree profile supports configuration scans, lexical retrieval, saved statistical replay and synthetic comparator tests. Indexing/semantic retrieval requires separately reviewed vector dependencies. A complete package build, cross-platform CI, macOS, independent fresh host, full optional Windows profile and native/image/dependency-chain assurance are not established by this promotion.

## Verification and limits

Full Windows1629passed39skips60.72s; Linux1668passed291.08s;1668collected each/zero failures/errors. Documentation18pass and both candidate compatibility checks pass; actual Windows scan/lexical retrieval worked. Regression wall times are not matched efficiency or security-detection measurements. Historical evidence/lock hashes and Engine1 baseline tag unchanged.

Exact executed commands and current results are in [WORK_LOG](WORK_LOG.md). First Windows target:12passed with a cache write permission warning; preserved [receipt](../output/core-promotion-target-windows-20261009.xml). Subsequent suites explicitly select separate cache paths, without deleting or changing ownership of the historical cache (INC-075).

QA-011's approved32Windows/31Linux package queries apply to those candidate inventories only; no advisory query was rerun for this documentation/default change. Chroma and original environment matches remain open. No new service, clock, sensor, model server, remote scan, independent label or real-data study was executed. Genuine supervisor approval, qualified timing/coverage/identity, independent held-out evaluation/calibration/ablations/false alarms/overhead/energy and operational readiness remain pending.
