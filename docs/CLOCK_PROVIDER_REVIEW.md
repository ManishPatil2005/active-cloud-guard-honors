# Clock-provider review and raw-clock diagnostic (E2-024)

## Question and current facts

The E2-023 sensor-free run found Windows/WSL elapsed-time disagreement beyond launch/receive bounds. E2-024 asks whether WSL's unadjusted RAW elapsed clock shows the same discrepancy as its adjusted MONOTONIC/BOOTTIME clocks. This is Engine 2 instrumentation research, not Engine 3, a production fix or a baseline acceptance test.

Read-only sequential checks on 5 October: Ubuntu 24.04.5, systemd255.4-1ubuntu8.17, WSL2.7.3.0, guest kernel6.6.114.1-microsoft-standard-WSL2; current clocksource tsc, alternatives hyperv_clocksource_tsc_page/hyperv_clocksource_msr/acpi_pm. Hyper-V implicit sync Y, guest timesyncd active/running/enabled, NTP/NTPSynchronized yes. Windows CIM10.0.26200/build26200, hypervisor present; W32Time running/manual, vmictimesync stopped/manual. These are minimized/manual-transcribed [facts with commands](../output/engine2-clock-provider-facts-20261005.json), not simultaneous trial facts or authenticated attestation. W32Time differed from the older stopped snapshot; no service was changed by this task, cause/time of change unknown.

Timesync Frequency=-861091 scaled ppm (divide by65536, approximately -13.14ppm), poll32s/root-distance limit5s. Reviewed [upstream systemd255 bus source](https://raw.githubusercontent.com/systemd/systemd/v255/src/timesync/timesyncd-bus.c) exposes manager drift_freq; [manager source](https://raw.githubusercontent.com/systemd/systemd/v255/src/timesync/timesyncd-manager.c) updates it after clock adjustment. Thus this property is cached, **not a live kernel timex reading**, and not a contemporaneous explanation of the earlier ~0.7–1.0s discrepancy. [Linux adjtimex documentation](https://man7.org/linux/man-pages/man2/adjtimex.2.html) specifies scaled ppm units. Upstream source review is not binary/Ubuntu-patch attestation; no native adjustment syscall was invoked here.

Canonical [WSL time-sync guidance](https://ubuntu.com/wsl/docs/stable/explanation/time-sync/) describes possible conflict between implicit host synchronization and a guest NTP client. Both paths are currently enabled; that remains a hypothesis, not proven cause. Do not disable either path from this document. No service/clock/power/kernel change is authorized by a successful read.

## Implementation and acceptance

Add opt-in `scripts/clock_lineage.py --raw-clock` using the existing fixed Windows/WSL bridge/source/domain/privacy/overwrite gates. New protocol `windows_wsl_raw_clock_lineage_v1` prevents merging with the original lineage trial. Ordinary sampling/math/limits remain unchanged; execution source hashes change and old receipts must be reviewed from their original revision. No historical receipts enriched or corrected.

Native read order: RAW / MONOTONIC / BOOTTIME / REALTIME / BOOTTIME / MONOTONIC / RAW. Raw symbol/backend required, no fallback; all spans <=5ms, true nonnegative integers and nonbackward order. [Linux clock API documentation](https://man7.org/linux/man-pages/man3/clock_gettime.3.html) distinguishes RAW from NTP/adjtime-adjusted MONOTONIC; RAW excludes suspend and is not an external physical time standard in a VM.

Acceptance: software cases for native order/no fallback, raw shape/scalars/width/order, refusal of mixed protocols, raw/mono interval changes and strict complete offline binding, fixed command/first-failure preservation and unchanged legacy regressions. Run full suites both OS, lint/format/pip/publication/staged checks; publish implementation before one observation. No sensors, direct timex calls, installed packages, configuration migration or default-engine changes.

## One new observation predeclared

After implementation push/remote match, verify known trial sensors absent, lab accessible and time service active. Exactly one run to a new output:

```powershell
.venv\Scripts\python.exe scripts/clock_lineage.py --raw-clock --output output/engine2-raw-clock-lineage-20261005.json
```

Sixteen snapshots maximum/fifteen fixed one-second gaps, five-second timeout per child, two-second host round-trip gate; existing50ms disagreement/5ms span limits. First failure stops with sanitized partial evidence. No retries/replacements, induced suspend or adaptive extension; scheduling adds duration. Fixed child vector adds only --raw-clock, no extra subprocess or sysfs access during sampling. Pre/post provider/service checks are sequential context, not continuous attestation.

Offline review infers the raw protocol from the receipt (do not add --raw-clock to review):

```powershell
.venv\Scripts\python.exe scripts/clock_lineage.py --review output/engine2-raw-clock-lineage-20261005.json --output output/engine2-raw-clock-lineage-review-20261005.json
```

Reuse full host dispatch/receive bounds for host-minus-RAW elapsed, never equate epochs. Raw-minus-MONO elapsed interval = [raw_elapsed_low-mono_elapsed_high, raw_elapsed_high-mono_elapsed_low]. Additional raw wall-change ranges are descriptive; no fitted correction or accuracy gate.

If RAW and adjusted guest clocks both disagree with host, the sampled adjusted-vs-raw difference alone is insufficient to account for the discrepancy; provider/virtualization/reference assumptions remain candidates. If only adjusted clocks disagree, read-only live discipline/tick-state sampling is motivated, not a proven attribution. Neither outcome establishes which clock is absolutely accurate, explains old collector calibration or passes long-term stability/ML gates. Preserve every outcome and choose a separately reviewed next step.

Implementation checkpoint: live pending; checks recorded in WORK_LOG/TEST_PLAN after execution.

## Declared raw-clock observation: 5 October

Exactly one run after implementation `d86234cf82862b7f9363879d8beec6fc4b19ed16` was pushed/remote verified; start 10:43:05 UTC/16:13:05 IST, exit 0, sixteen packets/fifteen gaps. [Receipt](../output/engine2-raw-clock-lineage-20261005.json) SHA256 `70fff0419aa8bb6d42e9ab460bf0ae32162bcea3eb78102d85869c46f89dfe0a`; [offline review](../output/engine2-raw-clock-lineage-review-20261005.json). Full protocol/source/domain/sample/order/gap/gate/summary recomputation passed. Separately handwritten endpoint formulas reproduced the final intervals locally; not independent scientific evaluation. No retry or source changes during/after collection.

| Comparison | Result | Limit |
|---|---|---|
| Host counter minus RAW elapsed | 15/15 ranges include zero; final [-237223931,177704238] ns | Compatibility at dispatch/receive resolution, not exact equality or physical accuracy |
| Host counter minus BOOT elapsed | 11/15 exclude zero positively; final [330188272,745105771] ns | Adjusted guest advance differs from host reference in these samples |
| Host counter minus MONO elapsed | 11/15 exclude zero positively; final [330185300,745109255] ns | Similar to BOOT; no causal attribution |
| RAW minus MONO elapsed | 15/15 exclude zero positively; final [567397862,567416386] ns | Direct local unadjusted/adjusted advance difference, approximately 0.5674 s |
| Wall-minus-BOOT change | 14/16 exclude zero; final [316705263,316705962] ns | Approximately+0.3167s relationship change first seen at index2, not an identified adjustment actor/time |
| Guest-minus-host wall | 12/16 exclude zero; first [-286381877,-108656377] ns, last [-537431586,-299534286] ns | No cross-clock stable-offset certificate |

Final bounded host elapsed [17273873000,17688789800] ns; RAW [17511085562,17511096931], MONO [16943680545,16943687700], BOOT [16943684029,16943684728] ns. Native wall/MONO change likewise14/16 exclude zero; final [316702291,316709446] ns. Wall/RAW change15/16 exclude zero, final [-250706940,-250695571] ns. These are diagnostic intervals, not a corrected baseline.

Packet durations 119.5797–251.11255 ms; host endpoint wall/counter disagreement -1167650..192100 ns. Maximum native BOOT/MONO/RAW spans 468/3890/6196 ns, host sampling span 2000 ns. Whole-window host wall-minus-QPC 54,050 ns is descriptive, not an added gate. Same recorded guest namespace/children 4026531834, zero offsets/kernel boot hash as E2-023. Host reports QueryPerformanceCounter(), monotonic true/adjustable false/resolution 100 ns; metadata is not accuracy attestation.

Pre/post external lab/known-sensor checks passed and time service active; no synchronization/service/provider/power change or sensor workload initiated. Prior lineage SHA179ebdfa0f8b26a27ba0ed83b2a921b865f4438077567fe3f2e503cb38722710 and original rejection SHA754c29d9e63b9a13ab455b0bcb829a5ed340b0c1c8f70d1bdfe024c25fbecddb unchanged. Last suites 468 each OS; no code change/suite rerun since collection.

INC-037 records a new diagnostic outcome: RAW is host-compatible at this resolution while adjusted clocks differ, and wall/BOOT relationship also changed. This motivates live, read-only kernel frequency/tick/status observations paired with RAW/MONO sampling. It does **not** prove NTP caused the change, rule out other clock mechanisms, identify an absolute standard, explain old Falco calibration or pass stability/ML gates. Cached manager frequency/static provider snapshots are insufficient to make that attribution. Any service/clock/provider intervention requires separate explicit approval.
