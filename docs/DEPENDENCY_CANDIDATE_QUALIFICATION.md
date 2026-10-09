# Isolated dependency remediation candidate

QA-011/R7/R8, 9 October 2026; WL-085/ADR-073/INC-074. This is candidate qualification, not a claim that the working environments, original lockfiles or Chroma have been remediated. Preserve Python/Compose/Ollama/Chroma and the two-engine research boundaries.

Both portable candidate installations completed. Full Windows1626passed39skips70.05s/Linux1665passed230.82s,1665collected each/zero failures/errors. Candidate compatibility checks and both offline OAuth/version smokes passed. Approved OSV queries completed32Windows/31Linux installed distributions with no IDs returned, **only for those candidate inventories**. Working environments still retain their earlier findings. Nine new contract cases and18candidate documentation checks pass; final lint/146fileformat checks pass. [Windows suite](../output/dependency-candidate-full-windows-tests-20261009.xml), [Linux suite](../output/dependency-candidate-full-linux-tests-20261009.xml), [Windows smoke](../output/dependency-candidate-windows-smoke-20261009.json), [Linux smoke](../output/dependency-candidate-linux-smoke-20261009.json), [Windows query](../output/dependency-candidate-windows-advisories-20261009.json), [Linux query](../output/dependency-candidate-linux-advisories-20261009.json).

## Changes and supported scope

Official release metadata inspected for [pip26.2](https://pypi.org/pypi/pip/26.2/json), [pytest9.0.3](https://pypi.org/pypi/pytest/9.0.3/json) and [OAuthlib4.0.0](https://pypi.org/pypi/oauthlib/4.0.0/json). They are candidates for the patched versions listed in the [advisory triage](CACHE_ADVISORY_REVIEW.md), not guarantees of zero new vulnerabilities.

- [Bootstrap](../requirements-remediation-bootstrap-20261009.txt) pins pip26.2 and the official wheel SHA256; install with require-hashes/no-deps/wheels-only. Observed successful bootstrap on both new environments; hashes verify those downloaded bytes, not all dependency provenance or signatures.
- [Windows optional profile](../requirements-remediation-windows-candidate-20261009.txt) preserves all89root package names/versions except pip/pytest/OAuthlib; reuses the unchanged optional ML snapshot. **Full optional-profile installation/qualification remains incomplete.**
- [Portable core/ML profile](../requirements-remediation-linux-candidate-20261009.txt) starts from historical Linux core with pytest updated, adds patched pip/OAuthlib and pinned OAuth client dependencies/Pygments, and reuses unchanged ML pins. Filename reflects its initial Linux profile; these core pins are also being qualified on Windows. Windows-specific pytest colorama is resolver-added. Not a replacement for the89package vector environment.
- New `scripts/dependency_candidate_check.py` requires exact patched versions, prepares a synthetic OAuth client body without making a request, and optionally checks an **ephemeral** Chroma explicit-vector roundtrip if installed. No embeddings/model downloads, server deployment, sensor/clock/service/exploit action. Absent Chroma is explicitly unqualified, never remediated by omission. Persistent storage is not exercised by this smoke.
- Nine contract cases compare all root/core pins, verify bootstrap hash/shared ML snapshot, refuse each stale patched version and refuse existing evidence before imports.

Candidate directories under ignored `tmp/` are separate venvs, without system-site-packages. No copied working site-packages, source-distribution builds, historical environment upgrades or historical lock overwrites. Candidate testing is source-tree testing, not a signed package build or independent fresh-host attestation. `pyproject.toml` test extra and original environments still use historical pytest8.3.5; installing `.[test]` is not this candidate procedure and would select the old test pin. Promotion needs a separate coherent update after qualification.

## Preserved failures and limitations

First Windows full-profile dry run returned no matching distribution for aiohappyeyeballs2.7.1. [Official version metadata](https://pypi.org/pypi/aiohappyeyeballs/2.7.1/json) and one uncached index diagnostic confirmed that version exists. An uncached full installation then progressed through metadata, so release absence is not established. Cache/index/transport cause remains **unknown**; do not replace valid pins or label a later success a causal repair.

The uncached full optional Windows attempt was stopped during the observed resolution/download phase after rechecking exactly its owned PID/executable/command. Exit1/incomplete, no complete profile acceptance. No other process stopped. Default CIM query initially lacked access; escalated read identified the owned installer. Portable candidate installation proceeded separately. Linux pip emitted one automatic incomplete-download resume warning despite --retries0; resume retry is a separate pip option. Subsequent Windows portable install also specifies --resume-retries0. No global cache deletion or persistent pip configuration change.

Preliminary Windows selected-package smoke passed with14installed distributions; approved OSV query14/14 returned no IDs. This is **not** clearance of the original95package environment, uninstalled packages, Chroma or all advisory databases. Preliminary unconstrained dependencies included iniconfig2.3.1/charset-normalizer3.5.2; portable profile restores selected pinned2.3.0/3.5.1. Final receipts must describe actual final inventory, not reuse preliminary counts.

Original working versions observed unchanged: Windows pip25.0.1/pytest8.3.5/OAuthlib3.3.1/Chroma1.0.20; Linux pip24.0/pytest8.3.5/scikit-learn1.9.1. Their prior matches remain open. Chroma server restrictions and genuine timing/coverage/identity/supervisor/humans/held-out evaluation/calibration/novelty/operational gates remain unchanged. No independent security certification, repaired native-import cause or production-ready claim.

## Reproduction: candidate only

Choose a **new** ignored venv directory; never point these install commands at your working/historical environment:

```powershell
.venv/Scripts/python.exe -m venv tmp/dependency-candidate-new
tmp/dependency-candidate-new/Scripts/python.exe -m pip --isolated install --index-url https://pypi.org/simple --only-binary=:all: --no-deps --require-hashes --disable-pip-version-check --no-input -r requirements-remediation-bootstrap-20261009.txt
tmp/dependency-candidate-new/Scripts/python.exe -m pip --isolated install --index-url https://pypi.org/simple --only-binary=:all: --disable-pip-version-check --no-input --retries 0 --resume-retries 0 --timeout 20 -r requirements-remediation-linux-candidate-20261009.txt
tmp/dependency-candidate-new/Scripts/python.exe -m pip check
tmp/dependency-candidate-new/Scripts/python.exe -m pytest -q --basetemp=tmp/candidate-tests-new
tmp/dependency-candidate-new/Scripts/python.exe scripts/dependency_candidate_check.py --output output/candidate-smoke-new.json
```

Linux uses its existing interpreter to create a new venv and that venv's bin/python for subsequent steps. No privilege/service change required. Run the advisory runner only with approved package/version egress and a fresh output filename. Preserve failed/partial outputs and inspect result scope before interpreting success. Exact commands and observed final outcomes: [WORK_LOG](WORK_LOG.md). Full optional-profile acceptance, default-pin/environment promotion and broader native/image/host/CI assurance remain separate tasks.
