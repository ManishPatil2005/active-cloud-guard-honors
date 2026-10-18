# Refined-source package and full regression qualification

## 18 October qualification — QA-040 / WL-118

Built source6aa5b0e1ee1cd7dc6a37076f899d2e550c4b434e, including the completed
exact rule accounting and reviewer agreement changes. Fresh isolated Windows
and Linux stages copy only pyproject.toml/43core Python modules. Existing
pip/setuptools builders reused with --no-index/--no-deps/--no-build-isolation;
fresh target installations, no downloads or working-environment replacement.
Windows TEMP/TMP redirected only within the build command and restored afterward.

Windows installed-package checks:8passed/no skips. Linux full suite:2101passed,
zero skips/failures/errors,93.90s console. This supersedes the earlier2030case
checkpoint for current source, not independent effectiveness or full Windows
qualification. The suite runs from source; selected isolated installed CLI
children check the package origin, metadata, exact43module bytes and both
offline engines. Same existing hosts/dependencies, not fresh-machine acceptance.

| Platform | Wheel bytes | SHA256 |
|---|---:|---|
| Windows |100461|`6798e3324fc85f94fafa301db79338fae534baae8a9ca6cb2d469c61de8734d0`|
| Linux |100454|`29be94199e96034f6a18de967a499684ea3fc4f10805169600e986517d78af49`|

Ignored roots:tmp/package-completion-PLATFORM-20261018-qa040; artifacts/ holds
the wheel and installed/ its fresh target. Archive bytes differ and are retained;
no byte-reproducibility or public artifact release claimed. [Qualification receipt](../output/package-completion-qualification-20261018-qa040.json),
[Windows checks](../output/package-completion-windows-20261018-qa040.xml),
[full Linux](../output/package-completion-full-linux-20261018-qa040.xml).

Windows host-policy/hosted-process failures, Chroma advisory conditions, live
clock/coverage qualification, real-data evaluation, independent human labels,
calibration/novelty and deployment-specific acceptance remain separate gates.
No clock/service action, new sensor or model experiment. Commands in WL-118;
earlier dates below retain their historical scope.

## 11 October follow-up - QA-032 / WL-109

After the runtime binary-export refinement, rebuilt from source f624e6c535319125abe52185e9b217a8a9091512.
Existing pip26.2/setuptools83.0.0 builders reused; only pyproject.toml and42core
modules copied to fresh ignored stages. Dependencies reused, no download or
working-environment replacement. Supplementary research scripts remain source-tree tools.

Fresh roots: tmp/package-window-windows-20261011-qa032 and
tmp/package-window-linux-20261011-qa032. Windows artifacts-final/ and Linux
artifacts/ contain active_cloud_guard-0.5.0-py3-none-any.whl; installed/ holds each
separate target. Windows wheel95,736bytes/SHA8a87e5c9b1247f1846a82137b5ce117debfe06085887cdcc1a9553e25be96e06;
Linux95,728bytes/SHA2cf5d09e13b49f008d17aa25d0f353354142921cdc73e308dc760410bf9a30cf.
Byte-identical cross-platform builds are not claimed; exact source/package bytes pass.

Windows initial pip build-tracker writes in sandbox system temp failed with
PermissionError/exit2. A fresh workspace-local local-temp/ and per-command
TEMP/TMP resolved the build; original stage and failed-temp observations retained,
no ACL/security-policy changes or manual deletion. INC-089.

Actual installed-package checks:8passed on Windows, zero skips. Full Linux
source-tree suite with the new wheel/target supplied:1,984passed, zero skips,
including all8package checks and the6artifact-dependent checks absent in QA-030.
Only selected installed-entry-point children execute installed code; the full
suite itself is source-tree. Not a fresh-host certification or a repaired
Windows native-policy result. No new sensor/clock workload or research acceptance.

Machine-readable [build/test receipt](../output/package-window-qualification-20261011-qa032.json),
[Windows tests](../output/package-window-check-windows-20261011-qa032.xml),
[Linux full tests](../output/package-window-full-linux-20261011-qa032.xml).
Exact commands and scope in WL-109; repeat only into fresh paths. Earlier results below remain historical.

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
