# Live kernel clock-state diagnostic (E2-025)

## Question and scope

E2-024 observed adjusted/unadjusted elapsed disagreement without live kernel discipline state. Does a new sensor-free observation retain that difference while recording kernel frequency, tick, phase, status and return state? Diagnostic only, not Engine 2 ML, matched overhead, clock correction or stability certification. Engine 1 and existing lineage sources/receipts remain unchanged.

## Reviewed interface and safeguards

`cloudguard/kernel_clock_state.py` independently represents Linux x86_64 LP64 little-endian glibc 2.39's 208-byte timex layout. Size and nine field offsets are checked. Native collection refuses Windows, other architectures/ABIs/versions and root. Fixed library `/lib/x86_64-linux-gnu/libc.so.6`; version function and typed adjtimex signature checked before querying. No installation or dependency added.

Every query allocates a fresh buffer and verifies all 208 input bytes zero and modes=0. No caller-supplied modes, setter or privilege escalation. The [Linux interface](https://man7.org/linux/man-pages/man2/adjtimex.2.html) permits ordinary-user zero-mode queries; frequency is scaled ppm (divide by 65536), STA_NANO controls phase-offset units, TIME_ERROR=5 is retained as state rather than confused with syscall failure -1. [Reviewed glibc 2.39 layout](https://raw.githubusercontent.com/bminor/glibc/glibc-2.39/sysdeps/unix/sysv/linux/bits/timex.h) and [Linux v6.6 implementation](https://raw.githubusercontent.com/torvalds/linux/v6.6/kernel/time/ntp.c) support this reading, not exact Ubuntu/WSL binary or loaded-memory attestation.

Local `/bin/cat /usr/include/x86_64-linux-gnu/bits/timex.h` failed (file absent), no package installed. `uname -m`, `getconf LONG_BIT`, `getconf GNU_LIBC_VERSION`: x86_64/64/glibc2.39; fixed libc stat size2129424 bytes. Layout review uses upstream header/runtime guards, not local compile-time proof. A nonessential assumed glibc source-path fetch failed; successfully reviewed header/kernel paths are cited above.

## Fixed protocol and acceptance

`linux_raw_timex_pairs_v1`: sixteen packets, fifteen fixed one-second sleeps, no retries/adaptive extension. Each packet: RAW-bracketed state query, existing native RAW/MONO/BOOT/realtime/domain snapshot, second RAW-bracketed state query. Complete run has32 queries. State brackets must advance and be <=5ms; native bounds/order/domain gates reused unchanged. Zero namespace offsets/shared recorded boot hash/unchanged domain/ordered packets required. State need not report synchronization success: negative states remain evidence.

Six execution files (four guest dependencies plus new module/script) hashed before/after; guest replies bind the four dependencies. Libc file bytes hashed before/after, not loaded-memory attestation. First failure/interruption stops and retains available sanitized endpoints, stage and exception class, never messages. Exclusive outputs refuse overwrite. Abrupt kill/power loss/blocked C call cannot guarantee saved receipt.

Offline complete review requires sixteen packets, true integers/protocol/source digests, backend metadata/digest continuity, domain/order/bounds and recomputed summary. Windows review performs no native query; libc bytes are not rechecked there. Local consistency, not authenticated or independently evaluated evidence.

Summary: RAW-minus-MONO elapsed intervals, wall-minus-BOOT changes, distinct values in32 state snapshots. Endpoints are not continuous adjustment history: do not integrate sampled frequency/tick as a complete causal account or attribute changes to NTP/Hyper-V without further evidence. No accurate physical reference or historical Falco calibration value assumed.

## One predeclared observation

Publish tested implementation first, verify intended private remote SHA/clean tree. Existing lab preflight, time service active and no known acg-falco- containers before/after. No intentionally concurrent tests/sensors/workloads during collection. No service stop, clocks/provider/power changes or WSL restart; interventions need separate explicit approval.

Run once from repository PowerShell, stop on error:

```powershell
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /usr/bin/timeout --signal=INT --kill-after=3s 45s /home/acgresearch/acg-venv/bin/python scripts/kernel_clock_diagnostic.py --output output/engine2-kernel-clock-state-20261005.json
```

45-second guest-clock timeout is operational, not independent physical time. SIGINT retained when Python can handle it; three-second forced-kill fallback may prevent finalization. At most one attempt, including failure, no automatic repeat.

If complete, offline review:

```powershell
.venv\Scripts\python.exe scripts/kernel_clock_diagnostic.py --review output/engine2-kernel-clock-state-20261005.json --output output/engine2-kernel-clock-state-review-20261005.json
```

Minimized receipts published only after review; historical evidence unchanged. Live pending at implementation checkpoint. Tests: tests/test_kernel_clock_state.py; exact full checks recorded in WORK_LOG/TEST_PLAN after execution.
