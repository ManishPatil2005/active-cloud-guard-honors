# Read-only Windows helper job-policy diagnostic

QA-017/R8/WL-092, 10 October 2026. This follows QA-016's failed hosted inert lifecycle qualification. It is not an Engine2 detector change, production intervention or permission to relax helper safeguards.

## Acceptance and implementation

`scripts/windows_job_diagnostic.py` reads only the calling process's membership and immediate Windows job limits. It uses typed standard-library ctypes calls to GetCurrentProcess, IsProcessInJob and QueryInformationJobObject (class9/extended limits). Fixed-width Windows scalars and pointer-width SIZE_T fields preserve the x64 ABI; tests require basic64/extended144-byte layouts. No process/job handles are opened, no job is assigned or changed, and no process is launched by this reader.

The report retains unknown values for membership/API/length failures; no zero/default flag becomes proof of permission. Selected flags report explicit breakaway, silent breakaway and kill-on-job-close separately. A non-Windows platform refuses native loading and reports unsupported. The CLI reserves a fresh evidence destination before any query. The reader is also called inside the existing explicitly inert intermediate parent, immediately before its unchanged helper launch; a small JSON diagnostic is printed to stderr so a hosted failure preserves the exact actor's observed limits.

Native definitions and scope were checked against Microsoft [membership API](https://learn.microsoft.com/en-us/windows/win32/api/jobapi/nf-jobapi-isprocessinjob), [query API](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-queryinformationjobobject), [basic limits](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information) and [extended limits](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information). A NULL query identifies the immediate job, not every ancestor. An observed immediate permission alone cannot prove that a launch will succeed or authenticate a host's overall policy.

## Executed versus pending

Actual authorized [run38031235575](https://github.com/ManishPatil2005/active-cloud-guard-honors/actions/runs/38031235575), exact source2f2d07da38ea647f7878781da3a4b543c61eec44: Ubuntu1760 passes/zero skips; Windows1722 passes/37 platform skips/one inert lifecycle failure. The **failing intermediate parent**, not a different CLI actor, reports successful membership/query, in_jobtrue/limit_flags0/explicit-breakawayfalse/silent-breakawayfalse, followed by child CreateProcess WinError5. This establishes a non-breakaway immediate job at the failed launch. It does not enumerate ancestors, attribute who created that job or prove absence of another access restriction. Original helper flags and matrix failure remain intact; diagnosis is complete for the immediate-job observation, supported-host lifecycle qualification is not.

Eighteen new contract cases: exact flag bits, ABI, absent/invalid membership, API failures, returned-length mismatch, non-Windows refusal, explicit non-qualification and evidence overwrite refusal. Initial Windows selected89 cases pass4.56s. Actual local CLI reports membershiptrue, flags12288 (silent-breakaway and kill-on-close), explicit breakawayfalse. This describes the CLI process in this local execution context, **not the hosted test parent**. Original safeguards and failed hosted receipts are unchanged. Linux contract/lifecycle results and actual hosted follow-up are recorded in WORK_LOG after execution; no hosted fix is inferred from a local observation.

## Reproduce safely

Use the reviewed portable environment: `python scripts/windows_job_diagnostic.py --output output/my-job-policy-NEW.json`. Existing paths are refused. Inspect status and nulls before interpreting flags. No source/model data is sent externally by this command. Do not use the flags to auto-adjust privileges, job limits or watchdog settings. The actual actor/context matters; diagnostics from a different process do not establish equivalence.

Outstanding: supported-host helper qualification, unqueried ancestors/access policies and real native restoration/timing/coverage. Manual hosted CI remains user-authorized but fail-closed; production deployment, self-hosted provisioning and supervisor/independent evaluation remain separate gates.
