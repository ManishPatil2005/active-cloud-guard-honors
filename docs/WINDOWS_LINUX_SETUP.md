# Windows-hosted Linux research environment

Current new-checkout recommendation: [portable profile promotion](CORE_PROFILE_PROMOTION.md) and README steps1–2. The dated environment installation commands below preserve historical reproduction guidance and old advisory-matched versions; do not use them to overwrite an existing environment or as today's recommended default. WSL/Docker provisioning is separate from dependency qualification.

Task E2-003. Preserve Windows as the development host and the existing Python/Docker Compose/Ollama/Chroma architecture. Installing a Linux distribution is environment provisioning, not completion of Engine 2.

## Runtime availability recovery, 6 October 2026

INC-045 recorded unavailable expected Docker Desktop guest mount/CLI target and local Windows engine pipe. Following the explicit startup question and user's approval, started the verified installed Docker Desktop Hidden; local Windows/ACG-Research engine29.8.0 answered again. No integration/PATH/configuration change, WSL restart or manual container start/recreation. Later running-container count0 and required named-sensor queries returned no IDs; scoped snapshots, not continuous/transient absence. The earlier failed precheck is preserved unchanged. [One read-only native receiver observation](SYSTEMD_RECEIVER_CAPTURE.md) then completed setup/release/close with0selected events, not Falco/job-fencing/timing/ML validation. Current engine API availability does not mean the stopped testbed/model services have been started or benchmark-ready. Historical setup checkpoints below retain their original observations.

## Observed host, 25 September 2026

- WSL 2.7.3.0; reported kernel 6.6.114.1-1; default version 2.
- Windows hypervisor present; physical memory 16,886,128,640 bytes (about 15.7 GiB).
- Initial free disk: C approximately 75.4 GB, D approximately 100.1 GB (decimal).
- Only docker-desktop was registered, stopped. It remains a Docker-managed environment, not the research distribution.
- Installed: Ubuntu-24.04, registered separately as ACG-Research at `D:\ACG-Research-WSL`, outside Git. Reported Ubuntu 24.04.5 LTS, Python 3.12.3, kernel 6.6.114.1-microsoft-standard-WSL2.
- Created password-locked, non-admin user acgresearch (UID 1000), no sudo membership; set as this distribution's default user. Global default distribution remains docker-desktop. No password was generated or published.
- [Actual Linux preflight](../output/engine2-linux-wsl-preflight.json): BTF, tracefs path and cgroup-v2 marker present, UID 1000. Separate read checks confirmed readable BTF and tracefs/cgroup2 mounts. No bpftool found; ring-buffer/probe loading untested.
- Started existing Docker Desktop hidden; Windows Docker server reported 29.8.0. Both distributions running at final observation. No Compose recreation or sensor install. Linux Docker shim explicitly reports WSL integration must be enabled.

WSL distributions share a kernel; separate registration is organizational separation, not a hardened security boundary. Windows drives are available inside this distribution under standard WSL automount behavior.

## Integration completed, 28 September 2026

Following explicit user instruction, the computer-use skill enabled ACG-Research under Resources > WSL integration and applied the restart. Docker CLI subsequently reported server 29.8.0 inside the distribution and listed the existing lab containers. Only the existing Redis container was started using `docker compose -f testbed/compose.yaml start redis`; Windows and Linux returned the same full running ID (see WL-011). No other service started/recreated. No WSL global defaults changed. Integration grants daemon management access, not read-only access. This gate is no longer blocked on user settings.

### Linux application verification

Installed Ubuntu python3-venv support and created `/home/acgresearch/acg-venv` as acgresearch. Windows .venv remains separate. The [observed dependency snapshot](../requirements-linux-core-20260928.txt) covers core/tests only, not Chroma or live sensor tooling. For a fresh Linux environment after venv support is installed:

```bash
python3 -m venv /home/acgresearch/acg-venv
/home/acgresearch/acg-venv/bin/python -m pip install -r requirements-linux-core-20260928.txt
/home/acgresearch/acg-venv/bin/python -m pytest -q -o cache_dir=/home/acgresearch/.cache/acg-pytest
```

Run creation only if the target is absent; run project commands from `/mnt/d/research f1`. Full suite [204 passed on Linux](../output/engine2-linux-tests-final-20260928.xml), plus Ruff lint/format, pip check and [synthetic replay](../output/engine2-linux-replay-20260928.json). The [first test run](../output/engine2-linux-tests-20260928.xml) also passed but emitted two cache permission warnings, recorded in INC-023. Using the Linux-local cache removed them without changing permissions or deleting Windows caches. Vector/LLM transports in software tests use mocks; this is not a Linux live Chroma/Ollama validation.

No kernel-level sensor or bpftool probe was executed. Container CLI access is established; kernel event visibility and representative telemetry remain unverified. Before the next trial, explicitly scope the sensor artifact/privileges, bounded duration, lab allowlist, event selection, data minimization, loss counters and cleanup. Leave automatic responses disabled.

## Historical integration handoff (25 September)

The initial handoff requested **Settings > Resources > WSL Integration**, enable **ACG-Research**, and **Apply**. This was completed on 28 September as recorded above. Follow [Docker's official integration instructions](https://docs.docker.com/desktop/features/wsl/) on fresh setups; do not enable unrelated distributions.

Then verify `wsl -d ACG-Research --exec sh -lc 'docker version'`. A working CLI still does not prove sensor event/container visibility. Do not install a second Docker daemon inside this distribution just to bypass the integration gate.

## Provisioning command

This command installs software and consumes disk/network resources. Run only for this approved research environment; first check that the name and destination are unused. Do not overwrite another installation or use an unregister command as troubleshooting.

```powershell
wsl --list --verbose
Test-Path -LiteralPath 'D:\ACG-Research-WSL'
wsl --install Ubuntu-24.04 --name ACG-Research --location D:\ACG-Research-WSL --no-launch --web-download
```

The command is based on [Microsoft's WSL command documentation](https://learn.microsoft.com/en-us/windows/wsl/basic-commands) and this host's `wsl --help`. No global WSL upgrade, custom kernel, security-policy change or Docker reset is part of this procedure. If interactive first-run setup requests a Linux username/password, the owner should choose them locally; do not paste passwords into chat or source control.

## Reproduction of host validation

```powershell
wsl --list --verbose
wsl -d ACG-Research -- uname -r
wsl -d ACG-Research -- python3 --version
wsl -d ACG-Research --cd '/mnt/d/research f1' -- python3 scripts/runtime_preflight.py --output output/engine2-linux-host-new.json
```

Choose a fresh report filename. If Python is missing, establish a scoped dependency installation first. Do not reuse the Windows .venv as a Linux environment. The standard-library preflight alone requires no project dependency installation. Run it as the normal Linux user. Confirm Ubuntu release locally as well; a WSL package version is not a distribution version.

Successful preflight is not successful monitoring. Falco is a candidate, not installed or selected as the final collector. Its [modern eBPF requirements](https://falco.org/docs/concepts/event-sources/kernel/) include kernel BTF and ring-buffer support; a version string/path alone is insufficient. The official [Ubuntu quickstart](https://falco.org/docs/getting-started/falco-linux-quickstart/) is a starting reference, not proof of support on this WSL host.

Two initial non-terminal installer attempts made no visible progress/registration and were stopped by verified task-specific process IDs. The same web-download invocation with a terminal attached completed successfully. Non-interactive invocation is a suspected factor, not a proven root cause. A first direct useradd invocation failed command lookup; using `/usr/sbin/useradd` succeeded. No distribution deletion/reset or global security changes were used. See INC-022.

## Sensor gates

1. Establish which Linux kernel/namespaces contain the actual lab containers. Docker CLI visibility is not proof that a sensor can observe their events.
2. Select and pin the sensor version, verify package provenance, and document narrowly scoped privileges. Do not grant a blanket privileged Docker container as a shortcut.
3. Agree bounded capture duration, explicit lab container allowlist, local-only outputs, loss counters and stop procedure before loading a probe. Linux process visibility can include sensitive data; do not collect unrelated user workloads.
4. Validate process/file/connect event semantics and mapping against real controlled lab operations, including failed operations and drop/coverage accounting. Default security alerts are not a representative complete event stream.
5. Normalize reviewed data to Engine 2's contract. Keep raw logs in ignored output/runtime-raw; never label synthetic fixtures as live captures.

No kernel probe, permanent monitoring service, Docker integration change, container migration or raw capture is authorized implicitly by a passing host preflight. Full detection and overhead evaluation remain separate gates.
