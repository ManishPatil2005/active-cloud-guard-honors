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
