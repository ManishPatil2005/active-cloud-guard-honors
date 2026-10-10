# Optional Windows vector-profile qualification

Later QA-018/WL-093 [Linux-native qualification](LINUX_VECTOR_QUALIFICATION.md) now executes actual Linux ephemeral/two-process persistence and full1760-case suite with installed-wheel checks. The original QA-015 Linux mocked-contract statement below remains accurate for that historical milestone. Selected compatibility on both platforms is not Chroma remediation/native server/security/research acceptance; original negative and partial environments preserved.

QA-015/R7/R8/WL-089/ADR-077/INC-077, 10 October 2026. Selected installation/embedded compatibility qualification, **not Chroma security remediation or research/production acceptance**.

## Actual environment and scope

A new ignored `tmp/vector-candidate-windows-20261010` venv was created without system-site-packages. Hash-pinned pip26.2 bootstrap succeeded. The unchanged dated full optional profile installed with official PyPI/wheels-only/no source builds/retries0/resume-retries0/socket timeout20s, inside the existing bounded-process supervisor with180s/direct-child/2MB output limits. Exit0; cached wheels were used. All95expected normalized package/version pins matched the saved actual inventory. Compatibility passed. Earlier failed index/incomplete installations remain preserved; success does not establish their cause.

The original working environments,31pin portable candidates, historical locks/Engine1 tag/engines/stack remain unchanged. The full optional candidate is **not the recommended default**. [Ephemeral smoke](../output/vector-candidate-smoke-windows-20261010.json) passed exact patched versions/OAuth body and explicit-vector add/get/count; [core/inventory receipt](../output/vector-candidate-core-pins-windows-20261010.json) records31required matches plus64unqualified extras.

## Embedded cold-process storage check

New `scripts/vector_storage_check.py` reserves a fresh output before inspecting versions or creating a store. Exact Chroma1.0.20 is required. Two separate bounded isolated Python children use a new ignored directory, telemetry disabled and `embedding_function=None`. First child writes two invented explicit vectors and checks count/IDs/nearest neighbor; after its clean exit, a fresh child reads/query-checks the persisted collection and deletes only that owned synthetic collection. The synthetic database directory remains ignored for review; no working index is touched.

Python socket connect/bind/DNS audit hooks refuse selected Python network activity; they are **not native/OS network isolation**. No model download/inference/server/probe/sensor/clock/service action in the selected code. Child output is bounded/strict JSON; incorrect phase/type/count/ID/envelope or nonzero process rejects. Partial completed steps and bounded cleanup diagnostics survive failure; remaining phases are not_attempted. Raw child messages are not published. [Actual Windows receipt](../output/vector-storage-windows-20261010.json) passed both phases and confirms cold_process_reopen_verified, while production/independent/server-security/network-isolation qualifications remain false.

## Tests and findings

Fifteen new contract cases. Initial Windows target:1fixture-helper failure47passes (duplicate phase keyword), [negative receipt](../output/vector-storage-target-windows-20261010.xml) retained; helper renamed without weakening cross-phase rejection. Final66targets pass on [Windows](../output/vector-storage-final-windows-20261010.xml) and [Linux](../output/vector-storage-final-linux-20261010.xml). Linux is mocked/portable contract qualification only, **not an actual Linux Chroma installation or storage observation**.

Full optional Windows [suite](../output/vector-full-windows-20261010.xml):1658passed39skips73.56s/1697collected/zero failures/errors, including actual QA-014 installed-wheel cases. It preceded the15new storage-helper cases; final targets qualify those additions. Ruff lint/151fileformat pass. Actual [approved OSV query](../output/vector-candidate-advisories-windows-20261010.json) completed95/95packages: only Chroma returned IDs in this inventory,4GHSA plus4PYSEC aliases. No IDs for patched pip/pytest/OAuthlib is database matching, not universal clearance; Chroma findings remain open. Prior working-environment findings are not erased.

## Beginner steps and pending work

1. Use a separately reviewed fresh optional candidate, not your original environment. Follow the dated profile/bootstrap instructions in the prior candidate guide; do not silently substitute pins or overwrite an existing venv.
2. Run that candidate's `python -m pip check`, then `python scripts/dependency_candidate_check.py --output output/my-vector-smoke.json` with a fresh filename.
3. Run `python scripts/vector_storage_check.py --output output/my-vector-storage.json`. Inspect both phase statuses. A passed synthetic reopen does not qualify existing/untrusted stores, native isolation, crash/concurrency/durability or server authorization/security.
4. Preserve failed/partial receipts and ignored synthetic stores. Never relabel a failure or database match as security clearance. Advisory queries require approved name/version egress; this milestone reused the user's existing approval and uploaded no source/model data.
5. Actual Linux optional-profile/storage qualification, Chroma remediation/native/dependency-chain assurance, authorized fresh-host/CI, independent real-data review/evaluation and production gates remain separate tasks.

Exact commands/limits: [WORK_LOG](WORK_LOG.md). No background experiments or automated response scheduled.
