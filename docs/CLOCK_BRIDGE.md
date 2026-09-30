# Redis-to-harness clock diagnostic

30 September 2026. E2-011 narrows INC-029 without launching a sensor or changing clocks. This is not Falco timestamp calibration.

## Predeclared method and limits

Use exactly six sequential Redis TIME reads through docker exec, only against the one running Redis labeled honors-cloud-guard. Check local daemon, known sensor absence and selected target identity before/after. No credentials, data reads/writes, clock adjustment, restart, installation or sensor launch. TIME reports server seconds and microseconds ([official Redis documentation](https://redis.io/docs/latest/commands/time/), reviewed 30 September).

Bracket each command using the existing wall/monotonic sampler. Reject a bracket if its observed endpoint clock disagreement plus uncertainty exceeds 50 ms, either sampling span exceeds 5 ms, or command bracket exceeds 500 ms. Reject malformed server responses. Each Docker TIME invocation has a five-second timeout; failures abort, retain prior samples and safe phase/error fields, and do not retry. The output path must be new.

Assuming the server read occurred between the local endpoints and clocks remained sufficiently stable during that bracket, server-minus-harness offset lies between server_time minus local_end and server_time minus local_start. Expand for sampling uncertainty, endpoint disagreement and microsecond quantization. Do not assume symmetric Docker/network latency or divide round-trip time by two. Endpoint samples cannot detect every transient clock excursion. A range including zero means no disagreement demonstrated at this resolution, not clocks proven identical. A range excluding zero is a lead, not proof of the historical Falco cause. No timestamp correction or baseline acceptance follows automatically.

## Actual observation

[Receipt](../output/engine2-clock-bridge-20260930.json): six valid samples, zero excluded from all six ranges, identity stable and known trial sensors absent at endpoints. Round trips ranged approximately 61.7–160.7 ms. Individual lower limits ranged -15.98 to -6.65 ms; upper limits +53.29 to +144.73 ms. Do not combine these into a single constant offset without an additional stability assumption. No claim about the original run's clocks follows from this later observation.

Executed as ordinary acgresearch, with no time-service manipulation:

```text
wsl -d ACG-Research -u acgresearch --cd '/mnt/d/research f1' --exec /home/acgresearch/acg-venv/bin/python scripts/clock_bridge.py --output output/engine2-clock-bridge-20260930.json
```

The sensor was deliberately absent, so falco_alignment_verified=false. No new sensor capture or latency comparison. The TIME calls cause small process/network activity in the lab, but do not change Redis application data. Service configuration and Engine 1 unchanged.

## Verification and next gate

Ten new tests exercise zero-included/excluded bounds, unsymmetric delay interval width, malformed responses, clock disagreement and overlong brackets. Full Windows suite 318/1.97 s and Linux 318/3.48 s: output/engine2-clock-bridge-{windows,linux}-tests-20260930.xml. Ruff lint/format (64 files) and Windows pip check pass. CLI exception/cleanup branches are not exhaustively fault-injected; pre/post sensor absence is not proof no unrelated collector ever ran.

Next diagnostic design must compare actual collector timestamps with an independently bracketed, uniquely correlatable event, without collecting arbitrary command lines or expanding privileges. Predeclare correlation criteria and refuse ambiguous/missing matches. The current minimized event schema lacks that identity; do not infer it by choosing the nearest timestamp. Adding a correlation field requires explicit schema/privacy review, tests and new evidence, not retroactive edits. Only then perform a bounded sensor-specific trial under the reviewed time-service policy. INC-029 remains open; no ML fitting or corrected historical count.
