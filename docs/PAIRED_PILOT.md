# Sensor-off/on engineering pilot v1

30 September report hardening: saved interval/per-call clocks are recomputed and cross-checked against boundaries, duration and dispatch schedule. Unknown/mixed timing protocols and missing per-call brackets are rejected. Historical receipts without per-call instrumentation are explicitly labeled legacy_interval_brackets, not silently upgraded. Revalidation output: output/engine2-paired-revalidated-20260930.json; unchanged contrasts, 308 tests each OS. Initial clock-gate/manifest binding and full identity schema remain incomplete; these checks are consistency guards, not authentication or collector-clock alignment.

Update reviewed 30 September: a separate fresh batch completed on 29 September. See [results and unresolved coverage issue](PAIRED_PILOT_RESULTS.md). The aborted batch below remains historical evidence and was not overwritten.

29 September 2026. Predeclared before execution after the owner authorized proceeding with the proposed temporary-NTP-stop comparison. One fixed order: OFF-1, ON-1, ON-2, OFF-2; four-second ping_4 profiles only, no retries. A new six-interval clock diagnostic must pass first. Guest timesyncd must be inactive at each job boundary and restored by the enclosing host try/finally after the batch. No persistent disable or Windows settings change. Abort remaining jobs on any failure and preserve receipts.

Both modes now wait one second, issue two warm-up PINGs each followed by a one-second wait, then wait a one-second guard before measuring. Sensor mode additionally inspects logs for readiness and performs collector startup: total warm-up processing and startup are not identical. The measured schedule and target identity must match. Existing privileges, image, resource ceilings, watchdog, timing tolerance and cleanup remain unchanged. Controls never fabricate event captures.

Pairs are OFF-1 versus ON-1, then OFF-2 versus ON-2 (reversed execution order in second pair). Two pairs are a descriptive pilot, not independent population samples. Report per-run mean Docker-exec round-trip latency and paired differences; do not infer Redis-only latency, full CPU/memory overhead, significance, accuracy or meeting a <5% target. No ML fit, attack label or TCI update. All samples remain redis-ping-development. Runtime effects from readiness checks, background host load, virtualization and warm-up differences remain confounders. Same target ID/image/start/restart fields throughout are necessary, not full deployment attestation.

`scripts/paired_pilot.py` runs as acgresearch, verifies inactive guest NTP before jobs, saves source hashes and run return codes, and stops after failure. It does not stop/restore services itself; that scope belongs to the explicitly approved enclosing PowerShell try/finally. A subprocess timeout may interrupt harness cleanup; the independent sensor watchdog still applies and final sensor enumeration is mandatory. No further workload may begin until cleanup is confirmed.

## Actual batch: aborted, not a comparison result

[Manifest](../output/engine2-paired-pilot-20260929/manifest.json): new clock gate passed; OFF-1 exited 1 before producing identity/measurement fields. [Failure receipt](../output/engine2-paired-pilot-20260929/off-1.json) records ValueError, not a latency observation. ON-1, ON-2 and OFF-2 were not executed. No retry or survivor-only comparison was performed. [Clock receipt](../output/engine2-paired-pilot-20260929/clock.json) is retained, not reused as permission to collect after restoration.

The host try/finally restored guest timesyncd; follow-up confirmed active/running/enabled. Docker inspection then reported its Linux-engine pipe absent. This establishes missing daemon availability at follow-up; the original generic ValueError did not retain a precise failure phase, so do not claim exact root attribution from that field alone. No pilot sensor launched. See INC-028.

Recovery without another experiment: `docker desktop start` restored the existing daemon. Its lab Redis container was stopped (exit 255); cause not established. The other lab services were also stopped. A read-only preflight rejected the absent running target. `docker compose -f testbed/compose.yaml start redis` started only that existing container; no recreation, volume deletion or workload PING run. Final preflight passed and no trial sensors were listed. A new batch must use a new output directory and account for the changed Redis start time; the failed batch is not silently replaced.

## Hardening following the failed attempt

Added `--preflight-only`: check local Docker context, absence of known trial sensors and exactly one valid running Redis before changing any service. The main runner also performs that preflight. Added safe named phases to future control failure receipts. Historical receipts/source hashes remain unchanged. This preflight is a point-in-time check, not a daemon uptime guarantee. Always run it **before** the enclosing temporary service-stop step.

`scripts/paired_report.py` requires the complete declared manifest, all successful profile/warm-up receipts, stable selected identity across all runs, four positive integer PONG latencies and sensor cleanup. Incomplete/failed batches are refused, not summarized over surviving runs. Tests use explicitly synthetic receipts; no real paired summary exists from this aborted experiment. Even a complete future two-pair summary is descriptive Docker-exec latency only, not general sensor CPU/memory overhead or a statistical significance claim.

## Commands and verification

The approved PowerShell wrapper required initially active timesyncd, stopped it through root WSL systemctl, then invoked:

```text
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python scripts/paired_pilot.py --output-dir output/engine2-paired-pilot-20260929
```

Its finally clause started timesyncd and verified active, including on batch failure. Recovery/read-only readiness commands:

```text
docker desktop start
docker compose -f testbed/compose.yaml start redis
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python scripts/paired_pilot.py --preflight-only
```

Final Windows `.venv\Scripts\python.exe -m pytest -q --junitxml=output/engine2-paired-final-windows-tests-20260929.xml`: 298 passed in 1.89 s. Linux same suite via /home/acgresearch/acg-venv/bin/python with Linux-local pytest cache, saved output/engine2-paired-final-linux-tests-20260929.xml: 298 passed in 2.76 s. Initial Windows 290-test XML remains preserved. Ten new tests cover fixed two-PING warm-up, preflight ambiguity and successful/failed summary gates. Ruff lint/format and Windows pip check passed. Full orchestration fault injection remains incomplete. Windows software checks completed during the clock-gate phase, before the attempted control; no experimental latency result is derived from them.

Next: a separately recorded fresh batch after preflight, using the same declared order and reviewed temporary time-service scope. No overhead estimate, ML baseline or accuracy result has been produced by this increment.
