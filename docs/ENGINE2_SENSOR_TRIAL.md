# Engine 2 bounded live sensor trial

Observed 28 September 2026. This is an engineering smoke test, not a threat-detection benchmark. Engine 1 remains frozen; the Python/Docker/Ollama/Chroma architecture is unchanged.

## Scope and acceptance

E2-003: establish whether a bounded modern-eBPF collector can observe selected successful syscalls from the existing Redis lab container on Windows-hosted Linux. Require matching events, a successful fixed Redis PING, saved evidence and sensor cleanup. Raw-event normalization, authenticated deployment binding and completeness are separate gates.

## Implementation and safety

`scripts/sensor_trial.py` selects exactly one running Redis container by existing Compose labels, requires its full lowercase 64-character ID, and rejects a remote Docker context. A generated rule filters successful execve/execveat/open/openat/openat2/connect calls by that ID in thread cgroups. Summaries revalidate event kind, result and ID boundaries. Output excludes command lines, environment, filenames and payloads. Cgroup filtering minimizes output; it does not restrict the kernel probe's underlying visibility.

The temporary sensor has network disabled, all capabilities dropped except BPF, PERFMON, SYS_RESOURCE and SYS_PTRACE, read-only proc/tracing/config mounts, 512 MiB memory, one CPU, 64 PIDs and one 1 MiB rotated log. No Docker socket, host /etc, privileged mode, SYS_ADMIN or host PID namespace is granted. Falco runs for a configured 15 seconds; an independent BusyBox watchdog sends TERM at 25 seconds and KILL three seconds later. These are configured limits, not measured wall-clock duration or overhead. The harness attempts stop/removal of only its unique sensor container, including a client-timeout path. That latter cleanup hardening was added after the live capture and has not been fault-injected live.

Image: Falco 0.45.0, pinned to `falcosecurity/falco@sha256:788f1129c542171813083d4afc61b16730a47dde8c23d9c39370acef996349b6`. The registry digest was observed after pulling the version tag; no independent publisher-signature verification was performed. `testbed/falco-trial.yaml` disables plugins, network outputs and webserver. The image remains cached locally; no persistent sensor is installed.

Environment: ACG-Research Ubuntu 24.04.5, kernel 6.6.114.1-microsoft-standard-WSL2, Docker server 29.8.0. WSL shares a kernel and Docker access is powerful; this is not a hardened tenant isolation boundary.

## Preserved runs

All paths below are under `output/`; raw logs/rules stay in ignored, publication-blocked `output/runtime-raw/`. Published reports contain hashes and minimized counts, not raw telemetry.

| Report | Actual outcome |
|---|---|
| engine2-sensor-trial-20260928.json | Startup failed: GNU timeout options unsupported by BusyBox. Exit 1, no workload/events. Historical status incorrectly says no_matching_events; treat it as failure. |
| engine2-sensor-trial-retry-20260928.json | Startup failed: list-valued configuration override caused YAML conversion failure. Exit 1, no workload. |
| engine2-sensor-trial-config-20260928.json | Minimal YAML configuration succeeded: PONG, exit 0, 40 events; deprecated evt.dir warning retained. |
| engine2-sensor-trial-final-20260928.json | Refused before sensor launch because Redis was not running. |
| engine2-sensor-trial-verified-20260928.json | After starting only existing Redis and removing deprecated field: PONG, exit 0, 40 events, sensor removed. |

The verified report records 2 execve, 25 openat, 8 openat2, 4 open and 1 connect events. These are selected syscall records, not unique requests or malicious actions. No attack was injected. All created trial sensors were removed. Final Docker enumeration found no acg-falco containers and only lab Redis running.

Falco reported BPF iterators disabled without the root PID namespace. Its successful-run shutdown reported zero event-drop action occurrences; this is not proof of zero lost events. Coverage stays unknown. Deployment binding is explicitly unauthenticated. `actions_executed=[]` denotes no security-response actions, not absence of the documented trial/workload operations.

## Commands and verification

Run from the repository in the already configured WSL environment, only when this privileged lab observation is authorized:

```sh
docker pull falcosecurity/falco:0.45.0
/home/acgresearch/acg-venv/bin/python scripts/sensor_trial.py --output output/engine2-sensor-trial-verified-20260928.json
/home/acgresearch/acg-venv/bin/python -m pytest -q -o cache_dir=/home/acgresearch/.cache/acg-pytest --junitxml=output/engine2-sensor-linux-tests-20260928.xml
```

These are historical output paths: choose a new filename for reproduction. The sensor script refuses existing reports. Intermediate attempts used the filenames above and the evolving script; their failures are not rewritten as executions of the final source.

Windows: `.venv\Scripts\python.exe -m pytest -q --junitxml=output/engine2-sensor-windows-tests-20260928.xml`: 216 passed. Linux command above: 216 passed. Windows `python -m ruff check .`, `python -m ruff format --check .`: passed, 46 Python files formatted. Windows and Linux `python -m pip check`: passed. Twelve new tests cover rule identity rejection, minimized fields, report non-overwrite and selected event validation. These do not establish complete launcher lifecycle coverage.

## Remaining gates

1. A strict Falco-to-runtime adapter with timestamp/schema validation and explicit dropped/rejected-record accounting; do not feed a summary count to the existing replay engine as though it were normalized telemetry.
2. Pre/post container identity checks, collector readiness and loss/coverage instrumentation. Filtering is not authenticated deployment attestation.
3. Separate, labeled baseline/observation workloads and repeatable overhead measurement before ML comparisons. No Isolation Forest/autoencoder, independent accuracy or production readiness is established.

Reference designs consulted: [Falco container setup](https://falco.org/docs/setup/container/), [supported fields](https://falco.org/docs/reference/rules/supported-fields/), [kernel event source](https://falco.org/docs/concepts/event-sources/kernel/). Actual image help and live results determine the narrower observed compatibility here.
