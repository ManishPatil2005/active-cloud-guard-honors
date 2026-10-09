# Local wheel and installed-package qualification

QA-014/R8/WL-088/ADR-076, 10 October 2026. This closes a selected packaging gap, **not independent fresh-host, CI, vector or production qualification**.

## Why this milestone matters

Earlier regression suites ran from the checkout. An editable/source-tree pass does not establish that a wheel contains the right modules, preserves declared dependencies or loads its installed entry point. We now build and install a local wheel on Windows and WSL Linux and explicitly check those boundaries.

The architecture remains Python/CLI, Docker Compose, Ollama and Chroma, with the same two engines and package version0.5.0. No detector/model algorithm changes or additional engine. Default new setup remains the recommended source-tree profile; this is an opt-in package qualification route.

## Build isolation and provenance

Fresh ignored Windows/Linux builder environments contain hash-pinned pip26.2 and setuptools83.0.0. [Build requirements](../requirements-build-qualification-20261010.txt) reuse the existing pip bootstrap and pin the inspected [official setuptools wheel SHA256](https://pypi.org/pypi/setuptools/83.0.0/json). Original build manifest admitted any setuptools>=75; it now selects the qualified83.0.0 exactly. Tool hashes verify downloaded bytes, not signatures or a vulnerability-free dependency chain.

Setuptools80.9.0 was considered but **not installed**: its [official metadata](https://pypi.org/pypi/setuptools/80.9.0/json) lists the Unicode filename/manifest source-distribution exclusion advisory fixed in83.0.0. No exploit or affected project distribution observed. This milestone builds wheels only, not source distributions, and copies only the manifest and42package Python modules into each build stage. No repository history, documents, experiments, credentials, environments, weights or vector databases enter the build stage.

Both final wheels build offline with `--no-index --no-deps --no-build-isolation`, using the preinstalled pinned backend. Installations use `--no-index --no-deps --target` into fresh ignored targets. Neither the historical nor qualified portable environments receives a project distribution or tool upgrade. Installed checks reuse qualified portable third-party dependencies, so **this is not a fresh runtime environment/host test**.

| Artifact | Bytes | SHA256 |
|---|---:|---|
| Final Windows wheel | 95275 | `2f5619f90ffd85e4d141959bf185c5ee99d074dbfb12bd751641458d62a3070a` |
| Final Linux wheel | 95267 | `d13f3a23f20f2b5fcd565564be820f903c624f9c3b3abfd9f50d1f4842acd3df` |

Hashes differ; **byte-for-byte reproducible builds are not established**. Both must pass source-content/metadata assertions; no causal explanation for archive-byte differences is assumed. A preliminary Windows wheel, built before the manifest pin, remains separate under ignored artifacts; it was not used for final qualification or published. No wheel or package is uploaded to PyPI/GitHub releases.

## Tests and scope

Actual first targets8pass on Windows/Linux. Full suites1697collected each: Windows1658pass39skips63.29s/Linux1697pass216.39s, zero failures/errors. Both suites preceded the final additional installed-source byte comparison; final expanded59targets eachOS pass (Windows1.53s/Linux7.20s), including that amendment. Ruff lint/149fileformat and both build-tool compatibility checks pass. Both candidate31requiredpins remain matched with unchanged32Windows/31Linuxinstalled counts; historical evidence/lock hashes and frozen Engine1 tag unchanged. [Receipts](EVIDENCE.md).

Eight new cases: exact backend/hash profile, exact42source modules and five expected metadata files/no extra archive paths or duplicate names, declared core/optional dependencies and entry point, and five isolated child cases. Python `-I` removes ambient source/PYTHONPATH import reliance; children use a non-root working directory, explicit copied inputs, assert the package/distribution loads from the installed target, and invoke the installed `cloudguard` entry-point function.

The children exercise Engine1 configuration scan and lexical retrieval, Engine2 saved synthetic statistical replay, their existing offline integration, and a missing-input rejection that must retain a non-clean error. No Docker/model/server/probe/sensor/service/clock action. Generated OS launcher executables, default corpus outside a checkout, installed optional ML/vector/native paths, source distributions, signatures and adversarial tampering remain unqualified. Metadata equality is not independent security detection evidence.

Without both `ACG_PACKAGE_WHEEL` and `ACG_PACKAGE_TARGET`, the six actual-artifact cases explicitly skip; the two build-profile contracts still run. Providing only one path fails. Never describe those skips as an installed-package pass. Wheel SHA is recorded in actual JUnit suite properties. Exact executions/results: [WORK_LOG](WORK_LOG.md).

## Operator steps

1. Keep the repository checkout and existing environments untouched. Choose a **new** ignored build directory; refuse an existing destination. Install the hash-pinned build profile into a new builder with `--only-binary=:all: --no-deps --require-hashes` and the explicit official PyPI index. Network is needed only for tools not already cached.
2. Create a fresh source stage containing `pyproject.toml` and only `cloudguard/*.py`, not the whole repository. Run the offline wheel command above with a separate artifacts destination. Preserve any failed build and do not overwrite a prior wheel while claiming unchanged evidence.
3. Install that trusted local wheel into a fresh target, not `.venv`. Select the qualified portable interpreter for tests; no copied Windows venv on Linux.
4. Set `ACG_PACKAGE_WHEEL` to the absolute wheel path and `ACG_PACKAGE_TARGET` to the absolute target directory. Run `python -m pytest -q tests/test_package_installation.py --basetemp=tmp/package-check-new -o cache_dir=tmp/package-cache-new --junitxml=output/package-check-new.xml`, with fresh test/report names.
5. Expect8passes/zero skips for the actual-artifact run. Inspect failures, wheel SHA and stated limits. Keep generated builders, stages, installed targets and wheels ignored; publish only reviewed source/tests/documentation/receipts.

Research supervisor approval, qualified timing/identity/coverage, independent reviewers/held-out captures, calibration/ablations/false alarms/overhead/energy and novelty remain pending. Passing package checks does not bypass those gates or authorize production deployment.
