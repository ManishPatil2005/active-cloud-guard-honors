# Linux optional-vector compatibility qualification

## QA-022 - Native ext4 clean persistence now executed

10October2026/WL-098: existing helper now accepts `collect(args, storage_parent=Path(...))` for an existing absolute trusted nonsymlink parent. Actual ordinary-user parent `/var/tmp/acg-native-storage-20261010-qa022`, fresh stores r8s8l15m/e7i1vz0c: findmnt confirms ext4, parent/final store mode700acgresearch. Both actual two-process explicit-vector write/clean exit/reopen/query pass; only owned synthetic collection deleted, stores retained. [Final receipt](../output/vector-ext4-final-linux-20261010-qa022.json); earlier receipt preserved, final location wording corrected. This closes native ext4 **clean persistence only**, not crash/concurrency/durability/native security/advisory clearance. Default mounted-store behavior unchanged.

Six new contracts; [Linux full](../output/native-storage-full-linux-20261010-qa022.xml)1800passes/85.11s before minor receipt sentence/two assertions, final four-file amended-source target62Linux passes/61Windows passes1symlink privilege skip with actual current package paths. No engine/core/wheel change; Windows policy/hosted lifecycle and genuine approval/data/research/production gates remain open. Earlier QA-018 paragraphs below describe historical mounted9p scope, superseded only for this named new native clean-persistence observation. Exact command including evidence-first publication in WL-098.

QA-018/R7/R8/WL-093, 10 October 2026. Completes selected Linux installation and embedded synthetic-storage checks, **not Chroma remediation, production security or independent research evaluation**. Existing two-engine Python/Compose/Ollama/Chroma architecture and environments remain unchanged.

## Actual environment and installation

Fresh Linux-native `/var/tmp/acg-vector-candidate-linux-20261010-qa018`, ordinary user `acgresearch`, Python 3.12.3 in ACG-Research. Directory absence checked before creation; no system-site packages. Hash-pinned pip 26.2 bootstrap succeeds, then unchanged `requirements-remediation-windows-candidate-20261009.txt` installs wheels only, with zero retries/resume retries and a 20-second socket timeout. Guest `/usr/bin/timeout --signal=TERM --kill-after=5s` imposes 60 seconds for bootstrap and 180 seconds for full installation; actual exit codes were zero. No root/system package install, old environment overwrite, source build, Docker/model/sensor/clock/service action or manual WSL restart.

The dated profile's name is Windows-oriented, but its unchanged 95 distinct declared pins match actual Linux metadata too; shared numpy appears identically in the included ML profile. Installation has 96 distributions; the one additional platform dependency is uvloop 0.23.0. The complete queried inventory plus the existing core verifier's 31 matching required pins and 65 reported extras preserve that distinction. Profile SHA256: `bc68e799513036f65a42dda6e87e8dadd97087f18ae06ea9f2e3635db82351d2`. Metadata matching is not wheel integrity/native provenance certification or approval of every extra.

The earlier mounted-drive partial candidate remains unchanged. A separate fresh `/tmp` bootstrap succeeded, but that path was subsequently absent and its full install was **not launched** (timeout exit 127: missing executable). Read-only path checks and guest uptime of zero minutes were observed; no pre/post boot identity comparison was captured, so disappearance/boot-cleanup cause is unproven. No agent deletion/restart occurred. `/var/tmp` was selected as a separate persistent candidate, not a retry inside either earlier environment. INC-082; this success does not prove why the mounted-drive attempt timed out.

## Executed checks

- pip check: no broken requirements.
- [Core/complete-extra inventory](../output/vector-native-core-linux-20261010.json): 31 core matches, no missing/mismatches, 96 installed distributions and 65 reported extras.
- [Ephemeral smoke](../output/vector-native-smoke-linux-20261010.json): patched installer/test/OAuth versions and explicit-vector add/get/count pass, no model inference or server.
- [Two-process persistent storage](../output/vector-native-storage-linux-20261010.json): exact Chroma 1.0.20; two invented vectors, clean write-process exit and separate read/query/owned-collection delete pass. Fresh ignored store retained. Exact child source matches the Windows qualification; Python socket guards are not OS/native network isolation. Clean reopen is not crash/concurrency/durability/security testing.
- [Approved OSV query](../output/vector-native-advisories-linux-20261010.json): 96/96 installed names/versions, only Chroma matched four GHSA IDs and four PYSEC aliases. No source/paths/credentials/model data sent. Matches remain open; absence of IDs is not security clearance. Prior working-environment findings are retained.
- [Full Linux suite](../output/vector-native-full-linux-20261010.xml): **1,760 passed, zero skips/failures/errors, 135.39 seconds** at source `2f2d07d`, with actual QA-014 wheel and installed-target paths. The six opt-in artifact cases ran, not silently skipped. Wheel/dependencies are reused local artifacts; this is not a fresh-host or standalone dependency bundle. Test-suite time is not engine latency/energy or effectiveness.

Filesystem scope was checked explicitly: the venv is on guest root ext4, but the helper's retained synthetic store is inside the mounted research repository (`/mnt/d`, reported as 9p by findmnt). Thus this executes a Linux backend against that mounted store; **native ext4 database storage, crash durability and filesystem portability are not qualified**. Full-suite XML time is 135.368 seconds; 135.39 seconds above is pytest's console total. Windows/Linux child source hashes match exactly.

## Simple reproduction path

1. Use a new Linux-native directory with sufficient space and a reviewed Python3.12 interpreter. Never reuse or delete an existing venv to make a failed attempt disappear. `/tmp` persistence cannot be assumed across WSL sessions.
2. Create an isolated venv. Install the hash-pinned bootstrap from `requirements-remediation-bootstrap-20261009.txt`, then the unchanged optional profile above using wheels-only and explicit finite installer budgets. This profile is optional, not the recommended portable default.
3. Run its `python -m pip check`; run `scripts/core_profile_check.py --output output/my-linux-pins-NEW.json`. Inspect installed/missing/mismatch/extra counts; extras are reported, not automatically qualified.
4. Run `scripts/dependency_candidate_check.py --output output/my-linux-smoke-NEW.json`, then `scripts/vector_storage_check.py --output output/my-linux-storage-NEW.json`. Both require fresh outputs. Inspect each storage phase and preserve incomplete/failed evidence and ignored stores.
5. An OSV inventory query requires approval for package/version egress; it is not automatic setup or proof of exploitability. No Chroma server exposure is authorized.
6. For artifact-enabled full tests, follow [package qualification](PACKAGE_QUALIFICATION.md) and supply both ACG_PACKAGE_WHEEL/ACG_PACKAGE_TARGET pointing to reviewed local artifacts. Omitting both intentionally skips six artifact checks; that is not equivalent to the executed 1,760-pass result.

Remaining: Chroma advisory-condition/remediation review, broader native/OS/ancestor assurance, Windows supported-host lifecycle qualification, genuine supervisor approval and qualified timing/coverage/independent data/evaluation/calibration/novelty/production gates. Exact commands and preserved failures: [WORK_LOG](WORK_LOG.md).
