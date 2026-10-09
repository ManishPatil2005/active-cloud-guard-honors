# Dependency and stream-boundary review

Follow-up QA-010: [cache and installed-package advisory coverage](CACHE_ADVISORY_REVIEW.md). Approved95Windows/23Linux OSV queries and additional matched records triaged; this document retains the earlier four-record review scope. No original receipt/lock replacement or automatic upgrade.

9 October 2026; QA-009, roadmap sequence3 **partial**, WL-083. The two engines, model policy4, Python/Compose/Ollama/Chroma stack and frozen Engine1 tag remain unchanged. No source upload, cloud provisioning, package installation/upgrade, live sensor/model workload or penetration test.

## Implemented acceptance

`cloudguard/limits.py` now rejects non-integer/boolean/nonpositive or over8MB budgets before opening/reading. Each binary read requests at most64KiB and only the remaining allowance plus one overflow byte. Short reads continue until EOF; a valid JSON prefix followed by trailing data cannot be accepted just because the first read was short. Invalid stream return types/oversized chunks fail closed. Existing1MB input/2MB response defaults unchanged.

The allocation and byte counts are finite for compliant streams. Reads can still block; socket timeout is not an overall elapsed-time guarantee. Trusted Python objects can violate interfaces; this is not process isolation, filesystem-race protection, a native parser sandbox or exhaustive fuzzing. JSON/YAML post-decoding node limits and other native boundaries require further review.

## Observed dependencies and advisory triage

Read `pyproject.toml`, root lock, Linux core snapshot and optional runtime-ML snapshot. All89root pins match Windows installed metadata;95packages installed, six additional optional ML packages (numpy already in root). Windows reports Python3.12.14, pip25.0.1, Chroma1.0.20, scikit-learn1.9.1. Linux Python3.12.3 reports pip24.0, core PyYAML6.0.3/jsonschema4.23.0/python-hcl2 7.3.1, scikit-learn1.9.1; Chroma is not installed there. Do not overwrite historical locks or interpret a compatibility check as a CVE scan.

Selected authoritative advisory records checked online on9October2026:

| Record | Version match and conditions | Disposition |
|---|---|---|
| [CVE-2026-45829](https://github.com/advisories/GHSA-f4j7-r4q5-qw2c) | Chroma1.0.20 falls in1.0.0–1.5.9; server collection creation with hostile model repository/remote-code trust | Open dependency finding; advisory lists no patched version |
| [CVE-2026-45830](https://github.com/advisories/GHSA-2wm9-hf6c-p5cr) | Chroma1.0.20 falls in0.4.17–1.5.9; authenticated server tenant authorization | Open dependency finding; no patched version listed |
| [CVE-2026-45833](https://github.com/advisories/GHSA-36p7-vc44-83pf) | Same range; authenticated server collection update and hostile remote-code model | Open dependency finding; no patched version listed |
| [CVE-2025-8869](https://github.com/advisories/GHSA-4xh5-x5gv-qwph) | pip versions<=25.2; fallback tar extraction when Python lacks PEP706 support; patched pip25.3 | Version match both observed installers; both interpreters expose tarfile.data_filter. Windows installed pip source selects filtered branch when available. Selected fallback condition not observed; not an all-advisory clearance |

Source inspection: `cloudguard/vector.py` constructs `PersistentClient` with telemetry disabled, passes `embedding_function=None`, supplies explicit local Ollama embeddings. Search of cloudguard/scripts/testbed found no HttpClient, Chroma server launch or trust_remote_code setting. Therefore the described server-request paths are **not evidenced in the inspected workflow**, not proven unreachable in all dependency internals or external deployments. Never expose Chroma as a server or import untrusted vector databases under this prototype's acceptance. No host/listener attestation or exploit execution performed. Blind upgrade is not a demonstrated fix, especially when the records list no patched version.

This is a selected four-record triage, **not a full transitive advisory database scan**, signed SBOM, package provenance attestation or claim zero vulnerabilities. Remaining priority: complete version-by-version advisory coverage, investigate supported upstream remediation, review artifact/cache permissions and races, deterministic parser fuzz cases/native boundaries, then fresh-host reproduction/CI. Approval, qualified timing/coverage, independent humans/data, calibration/ablations/energy/novelty and operational release remain open.

## Reproduction and receipts

From repository root, existing Windows environment:

```powershell
.venv/Scripts/python.exe -m pytest -q tests/test_stream_budget.py tests/test_research_io.py tests/test_legacy_io.py
.venv/Scripts/python.exe -m pip list --format=json
.venv/Scripts/python.exe -m pip check
```

Use a fresh --junitxml destination to retain new receipts. Exact before/initial/final commands and outcomes: [WORK_LOG](WORK_LOG.md).23newcases; before22cases17failed5passed, initial100targets2failed98passed (single-read assertion/endless response mocks), corrected101Linux targets pass. Full Windows1589passed38existing skips/1627collected. Original negatives retained; full Linux not rerun in this milestone. Tests are software evidence, not detection effectiveness or security certification.
