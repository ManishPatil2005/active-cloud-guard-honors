# Authorized manual cross-platform regression

QA-016/R8/WL-090/ADR-078, 10 October 2026. User explicitly approved manual GitHub-hosted Windows/Ubuntu testing and acknowledged Actions minutes. No deployment, production credentials or scheduled/push/PR triggers.

## Implemented workflow

[Workflow](../.github/workflows/manual-regression.yml) runs only on workflow_dispatch, with contents:read and checkout credential persistence disabled. Fixed hosted pairs: windows-2025/Python3.12.10 and ubuntu-24.04/Python3.12.14, fail-fast:false and20minutes per job. No user-supplied command input or environment/protected deployment target. The first attempt's unavailable Windows3.12.14 selection is preserved below.

Official action commits were resolved from selected release tags through GitHub's API and their node24 runtime metadata inspected:

- [Checkout v7.0.1](https://github.com/actions/checkout/tree/3d3c42e5aac5ba805825da76410c181273ba90b1).
- [Setup Python v7.0.0](https://github.com/actions/setup-python/tree/5fda3b95a4ea91299a34e894583c3862153e4b97).
- [Upload artifact v7.0.2](https://github.com/actions/upload-artifact/tree/cf430e030ddbb5b0abf93d22962f4752f3646cd9).

Immutable pins reduce moving-tag drift; this is not a complete third-party action security audit. Web API opens were unavailable through the browser tool; authenticated GitHub CLI read-only API calls supplied official release/tag/runtime facts, without displaying credentials.

Each hosted job creates its own core venv, installs the hash-pinned pip bootstrap and wheels-only portable31pin profile, verifies installed pins/compatibility/offline smoke/lint/format/publication, then creates a separate hash-pinned builder and manifest+42module source stage. Wheel build and target-only install are offline. Full regressions receive explicit fresh wheel/target paths, so installed-package cases cannot silently skip due to missing artifacts. No Chroma/model/server/Docker/sensor/service/probe workload is configured; native/inert software tests retain their existing guards and failures.

Always-uploaded artifacts are restricted to output/ci-*.json and output/ci-*.xml, unique by host/runID/attempt, hidden files excluded and retention7days. No source, wheels, environments, synthetic stores, weights, credentials or vector databases uploaded as test artifacts. GitHub itself already hosts the intended private source repository and executes the authorized revision. Core setup does not remediate Chroma or qualify native vector behavior. No OSV query is automatically run by CI.

## Validation versus execution

Ten new structural contract tests enforce manual-only trigger/least privilege/fixed hosts/budget/immutable actions/exact Python, isolated pinned installs, minimal offline package build, actual artifact test paths, restricted always-upload and no deployment/secret/live-service commands. Local selected33case runs:27pass6expected missing-artifact skips eachOS. Those6skips belong to the local contract run, not a remote installed-package success. Structural tests are not a GitHub workflow run.

First authorized [run37980052374](https://github.com/ManishPatil2005/active-cloud-guard-honors/actions/runs/37980052374), sourcef76c9340567ca6673b96e607c0c7cad6f73f433b, completed with mixed outcomes: Ubuntu1722tests passed/zero skips; Windows failed before dependencies/tests because hosted Python3.12.14 x64 was unavailable. No Windows XML was fabricated. Original run summary/Ubuntu receipts preserved in EVIDENCE/WORK_LOG; overall result remains failure.

The official [hosted version manifest](https://raw.githubusercontent.com/actions/python-versions/main/versions-manifest.json), inspected blob6e449c983a836ebb17364e5225798bd8b160b647, lists3.12.10x64 for Windows and3.12.14x64 for Ubuntu24.04. The corrected workflow pins those exact per-host pairs. Existing local3.12.14Windows/3.12.3Linux environments are not changed;3.12.10 is a scoped hosted compatibility test, **not a production-runtime recommendation or matched-patch comparison**. No tests/guards are skipped to obtain green. Corrected source/run outcome remains pending actual new dispatch.

New read-only `scripts/github_ci_receipt.py` requires ACG_CI_RUN_ID and ACG_CI_EXPECTED_SHA, reserves a fresh output before activity, validates exact repository/run/source identities and requires both actual regression steps to succeed. Failed/pending/missing/skipped outcomes cannot become a matrix pass. No dispatch/rerun/monitor/deployment occurs in the reader; downloaded raw test receipts remain necessary for counts/scope. A passed CI job is reproducibility/regression evidence, not supervisor approval, independent labels/held-out effectiveness, qualified runtime acquisition or production security certification.

## Operator steps

1. Ensure access to the existing private repository and an Actions budget; no credential value belongs in source.
2. Open Actions → Manual cross-platform regression → Run workflow, selecting the intended main revision. CLI equivalent: `gh workflow run manual-regression.yml --repo ManishPatil2005/active-cloud-guard-honors --ref main`.
3. Record the actual runID and head SHA. Inspect both jobs; fail-fast:false keeps one platform failure from canceling the other. Do not weaken platform/native guards merely to obtain green.
4. Download the restricted receipts into a fresh ignored directory; preserve original failed receipts and verify their run/host/attempt before copying reviewed evidence into fresh repository output filenames.
5. CI does not run automatically when a commit is pushed. Future runs need deliberate operator dispatch; this workflow is not autonomous research collection, monitoring or deployment.

Remaining: actual authorized execution/triage, optional Linux vector/Chroma/native assurance, broader OS/image/host review and genuine research/operational gates. Exact command records: [WORK_LOG](WORK_LOG.md).
