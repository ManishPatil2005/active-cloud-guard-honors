# Live kernel clock-state diagnostic (E2-025)

## 11 October follow-up - QA-033 / WL-110

WL-112 addendum: a separately bounded root read of the last 20 timesyncd journal entries succeeded after ordinary-user visibility was insufficient. Selected synchronization/service/boot/server-contact events do not identify the prior failure's actor or establish synchronization now. No settings or service mutation. Root access was used only for this log read; the actual clock-state observation remained ordinary-user. A new full-window development trial was requested separately, not executed at this checkpoint.

Owner explicitly chose continued read-only WSL diagnostics. One unchanged 16-packet protocol completed; [actual receipt](../output/kernel-clock-followup-20261011-qa033.json) and [offline review](../output/kernel-clock-followup-review-20261011-qa033.json). All 15 RAW-minus-MONO elapsed bounds and all 16 wall-minus-BOOT changes include zero. Final bounds: [-10749, 21187] ns and [-456, 421] ns respectively.

However every state reports time_state=5/status=8256, tick=10000 us and frequency=-16386 scaled ppm; timedatectl independently reports NTP=yes, NTPSynchronized=no. Service active/running/enabled before/after; no running acg- named containers observed. Service journal unavailable to ordinary user, not empty-history proof. No intervention or causal repair. A short consistent unsynchronized sample does not qualify UTC, full collector coverage or future stability. Earlier negative evidence below is unchanged. No further diagnostic/sensor run scheduled.

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

## Observed result: one attempt, 5 October

Implementation e0312454136412b1fb768759c0f348969b451fca published/remote matched and clean before execution. Exact declared command ran once, start2026-10-05T11:15:22.679977+00:00 (16:45:22 IST), exit0/sixteen accepted packets/32 queries. No timeout/retry/service/clock/provider/power change or sensor. Existing paired_pilot --preflight-only passed before/after, timesyncd active, known acg-falco- enumeration empty. These endpoint checks do not prove no outside actor intervened.

[Receipt](../output/engine2-kernel-clock-state-20261005.json) SHA834018876154de8a435048b88d063996ecaab029321bb563242ad6fa84ea13cf; [offline review](../output/engine2-kernel-clock-state-review-20261005.json) reproduced all six source hashes, backend continuity, metadata,32 states/RAW brackets,16 ordered domains/native snapshots and summary. Libc SHA3a15d66867d83762c7f2f1e37359cb8f6c5743edb369c65285cb0b1c4f7498bf. Maximum state-query RAW width159167ns (0.159167ms). Windows reviewer did not recheck libc bytes or query kernel. Separate handwritten Python endpoint arithmetic also reproduced final intervals, local consistency only.

| Packet indices | Tick usec (both reads) | Frequency scaled ppm (both reads) | Frequency ppm, divided by65536 |
|---|---|---|---|
| 0–4 | 9698 | 2151784 | +32.8336181640625 |
| 5–12 | 9707 | 2628697 | +40.11073303222656 |
| 13–15 | 9707 | 1165243 | +17.780197143554688 |

All32 reads: modes0, return state0/TIME_OK, status8192/STA_NANO, phase offset0ns, time constant1, tolerance32768000 scaledppm. Maxerror/esterror vary and are retained in the receipt, not treated as measured physical-error bounds. TIME_OK is the kernel-reported state, not evidence that sampled clock relationships were stable. These simultaneous kernel fields differ from E2-024's earlier cached property; distinct times/interfaces, not a contradictory replacement.

Final RAW elapsed [15670270569,15670282452]ns; MONO elapsed [15207033648,15207041346]ns. RAW-minus-MONO [463229223,463248804]ns (~0.46324s); all15 elapsed comparisons exclude zero positively. Wall-minus-BOOT change [867156020,867156662]ns (~+0.867156s);7/16 change intervals exclude zero, first at index9. Exact change instant/actor not captured; state endpoints before/after every snapshot do not record every intervening adjustment.

**Conclusion:** direct kernel parameter changes and adjusted/unadjusted disagreement are live-observed in this run (INC-039), strengthening the discipline-state investigation. Frequency alone is not a complete rate model: tick/other kernel terms also matter in the reviewed upstream implementation. No counterfactual writer isolation, continuous syscall history, independent clock reference, actual collector calibration observation or proof of which service caused current/historical failures. No extrapolation to old Falco lag or +123s relationship change, correction or long-term stability/ML acceptance. Old four timing receipt hashes rechecked unchanged, no source modification since collection or suite rerun; latest504 each OS.

**Next:** review exact guest/host synchronization writers and design an explicitly approved, bounded single-authority comparison with restoration and acceptance criteria before any intervention. Preserve both endpoint regimes and negative evidence; do not fit runtime baselines or claim reliable overhead until a separately declared stability protocol passes. No autonomous repeat or inherited permission to stop synchronization services.
