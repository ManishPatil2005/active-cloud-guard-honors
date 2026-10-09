# Cache boundary and installed-dependency advisory review

Follow-up QA-011: [isolated patched candidate qualification](DEPENDENCY_CANDIDATE_QUALIFICATION.md). Portable candidate setup has updated pip/pytest/OAuthlib, separate inventories/smokes/regressions; current/historical environments and full optional vector profile not promoted or cleared. This document retains the earlier95/23environment finding scope.

QA-010/R7/R8/V2-001, 9 October 2026, WL-084/ADR-072/INC-073. Continuation of roadmap3: scoped cache fixes and all observed installed Python distributions queried against OSV. Not full system security assurance or independent research evaluation. Existing engine algorithms, model policy4, Python/Compose/Ollama/Chroma architecture and frozen Engine1 tag unchanged.

Final verification includes29newcases: Windows1617passed39skips61.81s/Linux1656passed176.56s,1656collected each/zero failures/errors. Earlier1655case suites precede the reproduced/fixed stale-count regression. Docs18pass/lint144fileformat/bothpipchecks; raw negatives preserved. Test timing is not engine efficiency or security detection measurement.

## Cache implementation and boundaries

- Exact numeric nonboolean TTL in(0,86400] and exact integer count1..1024; invalid key types reject explicitly. Boolean creation timestamps are misses.
- Reads inspect the leaf with lstat, reject nonregular/symlink/Windows-reparse entries and oversize files. Open read-only with NOFOLLOW/NONBLOCK when available; compare descriptor device/inode to inspected leaf before bounded reading. This catches selected substitutions; not full host/ancestor authentication or malicious inode-reuse resistance.
- New final cache directories request0700 permissions; existing directories/ancestors/Windows ACLs are not repaired or certified. Cache directory symlinks refused on write and treated as misses on read. Operators must secure parent directories; hardlinks/in-place mutation/ancestor swaps remain outside this guarantee.
- Same-instance get/put operations serialize through a reentrant thread lock. A four-thread16-write Windows test first failed with PermissionError; after serialization it passes without weakening the assertion. Different instances/processes are not serialized; their platform errors remain visible. Lock waiting/filesystem calls have no hard total deadline.
- Vanished eviction candidates are skipped; a victim already removed by another writer is not an error after successful publication. Final review reproduced extra eviction from counting vanished-sort candidates; count now uses surviving dated entries. Other permission/I/O failures remain errors. New response replacement still precedes eviction. Counts are best-effort under other writers, not an atomic directory transaction; eviction can race another process's fresh replacement. Directory enumeration, pre-serialization allocation, crash durability and malicious storage remain unqualified.

Historical cache/probe semantics retained: invalid/corrupt/expired entries miss, cached content revalidated by model adapter, fresh probe evidence never cached. Checksums are not authentication; use private trusted cache/index storage and publication exclusions.

## Actual advisory queries

An initial combined test/query command was denied before execution for inventory egress. No workaround/query was used. User then explicitly approved sending package names/versions to `https://api.osv.dev`. New stdlib runner sends no source/paths/secrets/model data, refuses redirects, bypasses proxies, caps256packages/32perbatch/2MBresponse/256IDsperpackage and uses30s socket timeouts. Existing exclusive publisher reserves output before inventory/network. Failure retains completed batches and remaining `not_queried` rows with null IDs, not a clean result. Pagination/unsupported result fields reject the batch, not silently truncate. No automatic retries/installation/upgrades/exploits or future monitoring.

Following the [official OSV batch API](https://google.github.io/osv.dev/post-v1-querybatch/), actual results:

| Environment | Queried/installed | Packages with returned IDs | Raw IDs (aliases may duplicate issues) |
|---|---|---|---|
| Windows |95/95|Chroma1.0.20, OAuthlib3.3.1, pip25.0.1, pytest8.3.5|26IDs;13GHSA IDs|
| Linux ACG-Research |23/23|pip24.0, pytest8.3.5|14IDs;7GHSA IDs|

Receipts: [Windows](../output/dependency-advisories-windows-20261009.json), [Linux](../output/dependency-advisories-linux-20261009.json). All batch replies validated, no pagination observed. Reports preserve minimized IDs/package versions and query time, not complete advisory bodies or software provenance. Empty IDs mean no matches returned by this database at that time, never guaranteed absence of vulnerabilities. OS packages, containers, Ollama, model/native binaries, missing extras and uninstalled packages excluded. Neither software weakness nor exploitation is independently verified by these matches.

## Condition and remediation triage

All matching GHSA records inspected; PYSEC records retained in receipts, not counted as separate confirmed exploits. Four earlier records detailed in [prior review](DEPENDENCY_STREAM_REVIEW.md).

| Match | Conditions / current workflow distinction | Upstream patched version listed; action |
|---|---|---|
| Chroma four GHSA records | Prior three server findings plus [RBAC scope failure](https://github.com/advisories/GHSA-xph7-9rjv-w5fr), affected0.5.0–1.5.9. Inspected embedded workflow has no server/provider setup; this is not package clearance | No patched version in inspected records; keep local trusted embedded use, server deployment prohibited; upstream remediation open |
| OAuthlib [JSONP revocation](https://github.com/advisories/GHSA-hj66-6f7g-4r5v) |0.6.1–3.3.1, enabled JSONP with attacker-controlled callback. No OAuth server endpoint references found in cloudguard/scripts/testbed |4.0.0; assess transitive compatibility in isolated environment, not blind historical lock replacement |
| OAuthlib [PKCE timing](https://github.com/advisories/GHSA-xpv3-w29h-x7cv) |3.0.0–<4.0.0, server verifier comparison; no corresponding project endpoint observed |4.0.0; same open dependency remediation |
| pip [tar/ZIP ambiguity](https://github.com/advisories/GHSA-58qw-9mgm-455v) |<=26.0.1, ambiguous install archive |26.1; installer remediation pending |
| pip [wheel paths](https://github.com/advisories/GHSA-6vgw-5pg2-w6jp) |<26.0, crafted wheel extraction |26.0; installer remediation pending |
| pip [postinstall module import](https://github.com/advisories/GHSA-jp4c-xjxw-mgf9) |<26.1, newly installed module imported by deferred self-update check |26.1; installer remediation pending |
| pip [doubly encoded index URL](https://github.com/advisories/GHSA-qwm4-qh6w-59xr) |<26.2.0, malicious package index; avoid untrusted indexes/packages, not a complete mitigation |26.2.0; evaluate isolated installer update covering returned advisories |
| pip [entry-point paths](https://github.com/advisories/GHSA-wf93-45jw-7689) |<26.1.2, malicious console/gui entry-point paths |26.1.2; installer remediation pending |
| pytest [UNIX tmpdir](https://github.com/advisories/GHSA-6w46-j5rx-g56g) |<9.0.3, predictable default/tmp/pytest-of-user directories. This milestone's Linux tests specify fresh basetemp under trusted repository; not universal host protection |9.0.3; compatibility-tested tooling update pending |

The earlier pip fallback-tar finding depends on absent PEP706 filtering; both inspected Python interpreters provide the filter. That distinction applies only to that record, not the other installer findings above. No package/environment/historical lock was upgraded or rewritten. No project exploit, OAuth/Chroma server or install operation was performed. Existing environments must not be called vulnerability-free. Next coherent milestone: isolated installer/test-tool and transitive OAuth update qualification with fresh snapshots, respecting unpatched Chroma restrictions; then parser/native/artifact-parent boundary work and fresh-host/CI. Genuine supervisor/independent data/timing/coverage/calibration/novelty/operational gates remain open.

## Beginner reproduction

Offline local tests:

```powershell
.venv/Scripts/python.exe -m pytest -q tests/test_cache_boundaries.py tests/test_dependency_advisories.py tests/test_v2.py tests/test_research_io.py
```

Only with approved package-inventory egress, use a new filename (never an existing evidence path):

```powershell
.venv/Scripts/python.exe scripts/dependency_advisory_check.py --output output/dependency-advisories-new.json
```

Look for queried_count==installed_count/status complete_database_query; inspect advisory_ids and conditions, not a green security badge. Failed/partial results mean unknown remaining coverage. Exact execution/negative receipts and test results: [WORK_LOG](WORK_LOG.md). No evidence file from earlier work replaced.
