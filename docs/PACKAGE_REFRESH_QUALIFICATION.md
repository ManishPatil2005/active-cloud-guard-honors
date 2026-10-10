# Refined-source package and full regression qualification

QA-021/R8/WL-097, 10 October 2026, source `e0b8d89ca14f4b0961b278f10529cbb530f68a9d`. No detector, architecture, dependency, version or test change in this milestone.

## Actual outcomes

| Check | Windows | Linux ACG-Research |
|---|---|---|
| New minimal offline wheel and target install | Pass | Pass |
| Actual package cases:42module archive/installed byte equality, metadata, isolated entry points |8pass/no skips|8pass/no skips|
| Full source-tree regression suite,1794cases |1735pass/39skip/20fail/0errors|1794pass/0skip/0fail/0errors|
| Time, console / XML |72.07s /72.023s|90.76s /90.744s|

Windows result is **failed qualification**, not a platform skip or a passed two-platform milestone. Raw negative receipt is preserved. The8package assertions pass within that failed suite; installed CLI checks do not exercise every optional native dependency. Full suite runs from checkout; selected installed children use Python-I/non-root cwd and verified target origin.

## New artifacts; historical artifacts unchanged

Fresh ignored roots `tmp/package-refresh-windows-20261010-qa021` and `tmp/package-refresh-linux-20261010-qa021`; each source stage contains only pyproject.toml and42cloudguard Python modules. Reuse existing isolated hash-pinned pip26.2/setuptools83.0.0 builders, not working runtime environments. Build with `-m pip wheel --no-index --no-deps --no-build-isolation --wheel-dir <root>/artifacts <root>/source`; install with `-m pip install --no-index --no-deps --target <root>/installed <root>/artifacts/active_cloud_guard-0.5.0-py3-none-any.whl`. Do not overwrite a prior root or artifact. No PyPI/release upload or runtime promotion.

| New wheel | Bytes | SHA256 |
|---|---:|---|
| Windows |95674|`7b3c474d574e148a2e027cf7fa1489baf0efb7bdf824d37b0803361094f52033`|
| Linux |95665|`796ad85811d78ecdc47a88711db70703618c3a90a41b4fb5e46d15d501e534dd`|

Archive bytes differ; reproducible identical builds not established. Exact source and installed bytes agree on each OS. Prior QA-014 wheels do not contain the refined vector.py and remain historical, unmodified evidence.

## Windows failure diagnosis and safety

Twenty failures involve optional Isolation Forest backend imports and dependent integration assertions. Direct traceback identifies sklearn `_loss.cp312-win_amd64.pyd` as blocked by Application Control. Read-only recent Code Integrity Operational3077query (15-minute window, max40records, exact candidate/_loss match) returns20matching records; selected8297/8292/8287 correspond10October13:57:23/22/21local time, with the same candidate DLL and bundled Python process. This corroborates a host-policy load refusal for **this run**, not all historical intermittent imports. Operator policy ownership, rule rationale and appropriate signed-runtime exception remain unqualified.

DLL SHA256 `323f709430ebfcf14a67760f8b0f585bcece1377ae3ff816762e572731226410`. No policy/privilege/ACL mutation, file unblock, reinstall, fallback, retry-to-green or weakened test. No new hosted run; earlier hosted parent-job failure remains a separate unresolved observation.

## Repeat and inspect

Use new names for every build/test result. For the actual Windows run, ACG_PACKAGE_WHEEL points to the absolute Windows wheel above, ACG_PACKAGE_TARGET to its installed directory. Qualified optional interpreter `tmp/vector-candidate-windows-20261010/Scripts/python.exe` runs `-m pytest -q --basetemp=tmp/package-refresh-full-windows-20261010-qa021 -o cache_dir=tmp/package-refresh-full-cache-windows-20261010-qa021 --junitxml=output/package-refresh-full-windows-20261010-qa021.xml`.

Linux uses corresponding absolute `/mnt/d/research f1/tmp/package-refresh-linux-20261010-qa021/` paths, interpreter `/var/tmp/acg-vector-candidate-linux-20261010-qa018/bin/python`, guest300s TERM/kill5timeout, basetemp `/var/tmp/acg-package-refresh-full-20261010-qa021`, cache `/var/tmp/acg-package-refresh-full-cache-20261010-qa021`, XML `output/package-refresh-full-linux-20261010-qa021.xml`. Exact invocation in WORK_LOG. Missing either artifact selector is not an installed-package pass.

Receipts: [Windows negative](../output/package-refresh-full-windows-20261010-qa021.xml), [Linux](../output/package-refresh-full-linux-20261010-qa021.xml). These software/synthetic results do not measure detection effectiveness, latency efficiency, energy, calibration or novelty. Live model/server/sensor/clock/cloud experiments, genuine approval/independent labels/held-out study, Chroma remediation, native ext4 storage and production acceptance remain open. Next reviewed engineering step is supported Windows runtime/policy-owner assessment and native synthetic-store qualification, not policy bypass.
