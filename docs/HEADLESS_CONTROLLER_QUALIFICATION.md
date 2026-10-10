# Rejected headless controller trials and retained lifecycle diagnostics

QA-019/R8/WL-094, 10 October 2026. Finite test-context trials after [actual Windows job diagnosis](WINDOWS_JOB_DIAGNOSTIC.md). **Hosted proposal rejected; original parent flags restored.** No production helper, transport, engine algorithm or job policy is changed.

## Why this is a separate scope

The original hosted fixture launched an intermediate hidden-console parent; the actual parent was observed in a job with neither breakaway permission, then its helper creation failed. That negative remains valid and preserved. The first trial used Windows DETACHED_PROCESS for the intermediate inert controller only. Microsoft [process-creation flags](https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags) distinguish console attachment from job attachment; no-console alone did not escape the hosted job. A second local trial added explicit parent breakaway and also failed. Both alternatives were rejected; the original HIDDEN parent flag is restored (zero on Linux). No host policy was modified or successful supported-host context claimed.

The child still uses unchanged production HIDDEN|BREAKAWAY|NEW_GROUP flags, direct base interpreter, closed handles and explicitly inert mode. Tests still require readiness, actual parent kill, helper outcome after parent death, matching PID/nonce/mode/status, plus inert cancellation. No fallback, skip, deadline weakening or live service/clock action. The two retained flag-contract cases now assert the restored original parent choice and unchanged child flags. Successful parent diagnostics are retained in the JUnit suite property `inert_parent_job_context`, not discarded just because a local run passes.

## Executed evidence

First trial selected targets: [Windows91 passes](../output/headless-controller-target-windows-20261010.xml), [Linux91 passes](../output/headless-controller-target-linux-20261010.xml). Local Windows headless parent reports immediate flags10240; actual readiness/parent-kill/helper outcome pass. Actual [run38032656526](https://github.com/ManishPatil2005/active-cloud-guard-honors/actions/runs/38032656526)/source336fcc4: Ubuntu1762 passes, Windows1724 passes/37 platform skips/one failure. Hosted headless parent still reports immediate flags0/no breakaway, then WinError5. Local pass did not predict hosted acceptance.

Second local detached-plus-breakaway trial: [1 failed/90 passed](../output/detached-breakaway-target-windows-20261010.xml); parent immediate flags8192/no breakaway, then child WinError5. This failed proposal was not sent to another hosted run. Original parent flags restored; final selected regression receipts are recorded in WORK_LOG after execution. Underlying assigning authority/ancestors remain unqueried. Supported-host qualification is open; no further automatic trial, self-hosted provisioning or privilege/job-policy change occurs.

Final restored-default selected checks: [Windows109 passes](../output/controller-restored-windows-20261010.xml) and [Linux109 passes](../output/controller-restored-linux-20261010.xml), including both invariant cases, actual inert lifecycle and documentation contracts. These are local selected checks, not a new full hosted run. Preserve the distinction between this source and the failed source336fcc4 trial.

Existing [Linux optional compatibility](LINUX_VECTOR_QUALIFICATION.md) and historical failed CI runs remain intact. A future matrix pass requires a separately reviewed supported-host strategy and exact-source evidence; it would still not establish independent detection effectiveness, Chroma remediation, research novelty or production readiness.
