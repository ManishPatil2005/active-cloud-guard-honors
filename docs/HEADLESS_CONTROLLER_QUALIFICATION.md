# Headless inert-controller lifecycle qualification

QA-019/R8/WL-094, 10 October 2026. Test-harness refinement after [actual Windows job diagnosis](WINDOWS_JOB_DIAGNOSTIC.md). No production helper, transport, engine algorithm or job policy is changed.

## Why this is a separate scope

The original hosted fixture launched an intermediate hidden-console parent; the actual parent was observed in a job with neither breakaway permission, then its helper creation failed. That negative remains valid and preserved. The headless fixture now uses Windows DETACHED_PROCESS for the **intermediate inert controller only** (zero flags on Linux). Microsoft [process-creation flags](https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags) distinguish a console application running without a window from a process not inheriting a console. This is an explicit supported test-context choice, not a claim that every hidden console/runner/application context works or that the original host policy was modified.

The child still uses the unchanged production HIDDEN|BREAKAWAY|NEW_GROUP flags, direct base interpreter, closed handles and explicitly inert mode. Tests still require readiness, actual parent kill, helper outcome after parent death, matching PID/nonce/mode/status, plus inert cancellation. No fallback, skip, retry, deadline weakening or live service/clock action. Two new flag-contract cases assert both the platform-specific parent choice and unchanged child flags. Successful parent diagnostics are retained in the JUnit suite property `inert_parent_job_context`, not discarded just because a run passes.

## Executed evidence

Selected four-file target: [Windows91 passes](../output/headless-controller-target-windows-20261010.xml), [Linux91 passes](../output/headless-controller-target-linux-20261010.xml). Windows actual headless parent reports membershiptrue/immediate flags10240 (explicit breakaway and kill-on-close), then readiness/parent-kill/exact helper outcome assertions pass. That local actor differs from both the original hosted flags0 parent and the standalone CLI's flags12288 actor. Linux property says unsupported native platform; its real inert lifecycle still executes. These results do not qualify arbitrary ancestor/security policy or native service restoration. Full exact-source hosted execution remains separately pending until run/head/job/raw XML are observed.

Existing [Linux optional compatibility](LINUX_VECTOR_QUALIFICATION.md) and historical failed CI runs remain intact. Any subsequent matrix pass is regression/reproducibility evidence for these fixed environments and the headless fixture, not independent detection effectiveness, Chroma remediation, research novelty or production readiness.
