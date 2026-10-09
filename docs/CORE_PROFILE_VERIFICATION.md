# Offline installed-profile verification

QA-013/R8/WL-087/ADR-075, 9 October 2026. Reproducibility prerequisite, not another engine or security effectiveness result.

## Gap and implementation

The earlier candidate smoke verified four patched versions, not every core/ML pin. A partially installed or drifted environment could pass those four checks. `scripts/core_profile_check.py` now reads the three fixed recommended profile files, each capped at16KiB, validates their exact include chain and exact pin syntax, normalizes package names and refuses duplicate pins, empty profiles or more than128pins. It does not follow user-supplied includes or interpret requirements as commands.

The shared bounded installed-distribution inventory rejects invalid/duplicate metadata and more than256packages. Every required pin gets match/mismatch/missing status with complete counts; mismatches return exit1 and retain details. Extra distributions are listed but explicitly **unqualified**. Three SHA256 values bind the profile bytes read; they do not authenticate those files or installed wheels. Trusted parents/metadata remain prerequisites. No package upgrade, runtime package import, network, sensor, service or model action.

## Actual observations

Both qualified candidates match all31required pins. Windows32installed includes one extra distribution, not certified by this checker; Linux31installed has none. The untouched original Windows environment has95distributions and matches28pins but mismatches pip/pytest/OAuthlib. Its exit1 [negative receipt](../output/core-profile-historical-windows-20261009.json) is expected evidence that default recommendation is not an installed-environment upgrade, not a new engine failure.

[Windows match](../output/core-profile-windows-20261009.json), [Linux match](../output/core-profile-linux-20261009.json). Twenty-one new cases; corrected33profile targets pass each OS. Expanded verifier/inventory/profile/documentation targets67pass on Windows and Linux. Earlier incorrect singular test filename invoked no tests/exit1; [receipt](../output/core-profile-target-windows-20261009.xml) preserved, correct file is `tests/test_dependency_advisories.py`. Full engine suites remain QA-012's1629Windowspasses39skips/1668Linuxpasses; not rerun or recounted as a new full suite for this isolated helper.

## Beginner steps

1. Complete README's recommended fresh-environment installation. Stay at the repository root and select that environment's interpreter.
2. Run `python scripts/core_profile_check.py --output output/my-core-profile-check.json`, using an output filename that does not already exist.
3. A zero exit code and `profile_pins_match` mean all required version metadata matched. Inspect counts and unqualified extras; this does not mean vulnerability-free.
4. For exit1, inspect missing/mismatch rows. Preserve the receipt. Do not mutate the historical environment or bypass a mismatch; use a fresh environment and the recommended installation procedure before producing a separately named check.
5. Then run the candidate smoke and software tests. Vector/package-build/fresh-host/CI/native/image provenance and genuine research approval/data/evaluation still require separate qualification.

Existing output is refused before reading profiles or inventory. Generic input/metadata failures produce sanitized rejected receipts through the existing exclusive publisher. Exact commands and failures: [WORK_LOG](WORK_LOG.md), INC-076. No automatic remediation or monitoring.
