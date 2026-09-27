# Windows-hosted Linux research environment

Task E2-003. Preserve Windows as the development host and the existing Python/Docker Compose/Ollama/Chroma architecture. Installing a Linux distribution is environment provisioning, not completion of Engine 2.

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

## Required next user action

In Docker Desktop, open **Settings > Resources > WSL Integration**, enable **ACG-Research**, and select **Apply** (or Apply & restart as shown). This exposes Docker management access to the research distribution; it is not a read-only permission. Follow [Docker's official integration instructions](https://docs.docker.com/desktop/features/wsl/). Do not enable unrelated distributions. The setting was not changed automatically.

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
