# Read-only Windows/WSL synchronization diagnosis

29 September 2026, following INC-026/027. No clock setting, service state, kernel option or WSL lifecycle was changed during these checks. No sensor/control workload was run.

## Observations

| Check | Observed result |
|---|---|
| Windows services | W32Time and vmictimesync both Stopped / Manual |
| WSL version | 2.7.3.0, kernel 6.6.114.1-1 |
| ACG-Research systemd-timesyncd | Enabled, active/running; latest observed start 2026-09-29 13:54:42 UTC |
| NTP status | ntp.ubuntu.com, 32-second poll; one sampled reply, offset +242.499 ms, delay 326.560 ms |
| Hyper-V implicit synchronization | /sys/module/hv_utils/parameters/timesync_implicit = Y |
| Current kernel clocksource | tsc |
| Distro configuration | /etc/wsl.conf contains boot/systemd=true |

The ordinary user could not see system journal entries. A separately approved read-only root journal query showed timesyncd initial synchronization and start/stop entries across boots, including initial synchronization at 13:54:43 UTC. These entries do not directly cover or attribute the earlier 18:46 UTC-on-28-September diagnostic jump. Do not infer that this agent restarted the service: it did not. The environment has changed since the earlier run; service snapshots are not continuous history.

A sequential Linux/Windows time read at approximately 13:55:05 UTC appeared close, but command latency prevents interpreting it as a precise offset measurement or a stability certificate.

## Supported diagnosis versus hypothesis

Canonical's [Ubuntu on WSL time-sync documentation](https://ubuntu.com/wsl/docs/stable/explanation/time-sync/) describes Hyper-V implicit synchronization and warns that an in-guest NTP client can conflict with it. For Ubuntu 24.04 it discusses disabling timesyncd when relying on host synchronization. Actual observations establish that both paths are enabled here. **A competing-sync mechanism is a plausible cause, not a proven attribution of the recorded jumps.** A stopped Windows service alone was never sufficient to establish causality. Hyper-V synchronization is not inferred from vmictimesync service status; the Linux kernel parameter was checked directly.

## Original reversible test proposal

Historical proposal below was subsequently approved and executed once; see the execution receipt after the command list. It is not pending anymore.

With explicit owner approval, temporarily stop only systemd-timesyncd in ACG-Research, confirm its state, run one predeclared six-by-four-second bracketed diagnostic with a new output filename, and restore the original running service in a finally/cleanup path. Do not persistently disable the unit, change Windows services, set clocks manually, alter kernel options or restart WSL. Check restoration explicitly. WSL shares its kernel clock, so the experiment can influence Docker's time environment; no sensor/control measurements should run concurrently.

This test changes one competing synchronization path. A clean 24-second batch would support the hypothesis but would not establish long-term reliability or justify retroactively accepting failed data. A failed batch must also be preserved. No repeated attempts until success. Controls remain deferred until the result and next protocol are reviewed.

## Read-only commands executed

```text
Get-Service W32Time,vmictimesync | Select-Object Name,Status,StartType
wsl --version
wsl -d ACG-Research --exec /usr/bin/timedatectl timesync-status
wsl -d ACG-Research -u root --exec /usr/bin/journalctl -u systemd-timesyncd --since '2026-09-28 18:30:00 UTC' --no-pager -n 35
wsl -d ACG-Research --exec /usr/bin/systemctl show systemd-timesyncd --property=ActiveState --property=SubState --property=ExecMainStartTimestamp
wsl -d ACG-Research --exec /bin/cat /sys/devices/system/clocksource/clocksource0/current_clocksource
wsl -d ACG-Research --exec /bin/cat /sys/module/hv_utils/parameters/timesync_implicit
wsl -d ACG-Research --exec /bin/cat /etc/wsl.conf
wsl -d ACG-Research --exec /usr/bin/systemctl is-enabled systemd-timesyncd
```

No application source changed. The most recent software suites remain 288 passing on each OS; they were not rerun for this documentation-only investigation. Documentation/publication checks are separate from scientific verification.

## Approved temporary test execution

Owner answered "do needful" to the explicit temporary-stop, single-batch, restore proposal. A PowerShell try/finally sequence first required active service state, ran `wsl -d ACG-Research -u root --exec /usr/bin/systemctl stop systemd-timesyncd`, verified inactive, and invoked the existing diagnostic as acgresearch:

```text
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python scripts/clock_diagnostic.py --output output/engine2-clock-guest-ntp-stopped-20260929.json
```

Finally it ran `systemctl start systemd-timesyncd` through the same root WSL invocation and verified active. Follow-up show confirmed ActiveState=active, SubState=running, UnitFileState=enabled. Journal stop at 13:57:03 UTC and start at 13:57:27 UTC bracket the diagnostic; no intermediate start was shown. Later stop/start entries at 13:57:42/47 indicate additional environment lifecycle activity, not a change initiated by this task. There was no explicit WSL restart command.

[Saved diagnostic](../output/engine2-clock-guest-ntp-stopped-20260929.json): six of six checks passed; elapsed durations approximately 4.004..4.025 s; maximum absolute disagreement 3,505 ns, maximum sampling uncertainty 4,600 ns. Its clock_settings_modified=false field describes the diagnostic script itself, which never changes clocks; the surrounding approved experiment **did temporarily stop a synchronization service**, as recorded here. Do not use that field to claim no environmental intervention occurred.

Interpretation: this short trial supports the competing-sync hypothesis, but there was no concurrent matched guest-NTP-on batch in the same boot, and the environment changed since the historical failure. No causal proof, long-term reliability certificate, overhead result or retroactive acceptance of failed captures. Service restored; no persistent disable, Windows setting change, sensor/control run or clock command. Original failures remain published. Further controls must not use this temporary-state passing report as proof that the restored state is stable. A permanent synchronization policy or another service-managed workload experiment requires separate owner approval.
