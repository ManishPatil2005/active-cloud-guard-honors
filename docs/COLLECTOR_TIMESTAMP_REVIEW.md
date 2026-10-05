# Pinned collector timestamp-source review

E2-018, 5 October 2026. Investigate INC-032 without changing clocks, loading a probe, rerunning failed workloads or correcting historical events. Preserve Python/Docker/Ollama/Chroma architecture. Separate observed binary metadata, reviewed release source and unproven causal hypotheses.

## Scope and reproducible method

Inspect the already-local pinned Falco image and run only `/usr/bin/falco --version` in a disposable read-only container: no network, no mounts, all capabilities dropped, 128 MiB/one CPU/32 PID limits, `--pull never`, `--rm`. This version command exits without opening the capture engine. It is metadata execution, not a sensor trial. Fetch six allowlisted official source files at immutable libs commit `8fc2f1fbfc90f8ce7f68e00cdfa692cc7a9983a3`; bound downloads to 256,000 bytes/file and record SHA256, length and marker line numbers, never execute or vendor downloaded code. Refuse mismatching Falco/libs version, overwrite, unexpected source markers and preserve partial failure receipts.

Command: `.venv/Scripts/python.exe scripts/collector_source_check.py --output output/engine2-collector-source-review-20261005.json`. The receipt must use a new output path. Binary versions/digest provide local provenance, not a reproducible-build attestation or cryptographic proof that every source line matches the image. The source review does not exhaustively inspect all call paths or malicious-host alternatives.

## Source-backed mechanism

The local pinned image reports Falco 0.45.0, libs 0.26.0 and engine 0.65.0. The official release source chain is:

1. [Modern-BPF initialization](https://github.com/falcosecurity/libs/blob/8fc2f1fbfc90f8ce7f68e00cdfa692cc7a9983a3/userspace/libscap/engine/modern_bpf/scap_modern_bpf.c#L269) obtains a precise boot offset and sets it on the probe.
2. [Boot offset utility](https://github.com/falcosecurity/libs/blob/8fc2f1fbfc90f8ce7f68e00cdfa692cc7a9983a3/userspace/libscap/scap_engine_util.c#L33) reads CLOCK_BOOTTIME and CLOCK_REALTIME and subtracts the former from the latter.
3. [Setter](https://github.com/falcosecurity/libs/blob/8fc2f1fbfc90f8ce7f68e00cdfa692cc7a9983a3/userspace/libpman/src/maps.c#L132) stores that offset in capture settings; the [getter](https://github.com/falcosecurity/libs/blob/8fc2f1fbfc90f8ce7f68e00cdfa692cc7a9983a3/driver/modern_bpf/helpers/base/maps_getters.h#L25) reads it.
4. Both [fixed-size](https://github.com/falcosecurity/libs/blob/8fc2f1fbfc90f8ce7f68e00cdfa692cc7a9983a3/driver/modern_bpf/helpers/store/ringbuf_store_params.h#L141) and [variable-size](https://github.com/falcosecurity/libs/blob/8fc2f1fbfc90f8ce7f68e00cdfa692cc7a9983a3/driver/modern_bpf/helpers/store/auxmap_store_params.h#L170) event headers add the stored offset to kernel boot-clock nanoseconds, rather than reading live userspace realtime for each event.

Conceptual relationship: event epoch time = stored boot-to-epoch offset + current kernel boot time. If the actual realtime-minus-boot relationship increases after calibration while the stored value remains unchanged, generated epoch timestamps can lag current realtime. This is an **inference from the source**, not proof that a particular time service changed that relationship in our trials. The reviewed engine file contains the initialization setter call; no claim that every possible external update path has been exhaustively excluded.

This mechanism is consistent with E2-017's compatible Redis/harness readings and earlier collector timestamps. However, there were no direct simultaneous boot-clock/offset observations at calibration in E2-016 or E2-017. Thus neither calibration drift, a specific Falco bug, WSL behavior nor NTP causality is independently established. Do not subtract a fitted second, widen timing tolerances or certify historical alignment.

## Observed review receipt and software checks

The declared reviewer command completed with status reviewed: [receipt](../output/engine2-collector-source-review-20261005.json) records exact local digest, versions, six immutable official source URLs, byte lengths, SHA256 and marker lines. Source review confirms initialization lines 271/274, utility clock reads 36/40, setting assignment 137, getter 31, and fixed/variable timestamp formula lines 144/171. These markers are reproducibility aids, not an automated semantic proof. No full third-party files were copied into the repository or executed. A preliminary capability-free version inspection used the same image before the reviewer; this was metadata only, not a repeated workload experiment. Fetches through the web reader sometimes failed on guessed paths/cache; corrected paths from the official API tree and immutable commit were read with HTTPS and then hashed by the reviewer.

Fresh suites: [Windows](../output/engine2-collector-review-windows-tests-20261005.xml) 378 passed/2.11 s; [Linux](../output/engine2-collector-review-linux-tests-20261005.xml) 378/2.93 s. Ten added tests cover version mismatch/missing/duplicate metadata, source allowlist/size/markers, overwrite refusal and saved failure receipt. Ruff check/format (72 files), Windows pip check pass. Live source/Docker failures and temporary metadata-container timeout cleanup are not exhaustively injected. No new Falco syscall trial, Redis workload, model evaluation, clock-service action or calibration fix. Prior alignment failures remain unchanged.

## Next diagnostic design, not authorization for clock changes

Design a new fixed read-only protocol sampling realtime/boot-time relationships around actual collector initialization and each identified event, with uncertainty and clock-domain/namespace identity recorded. Explicitly establish whether the sampled boot clock matches the driver helper's clock; do not substitute CLOCK_MONOTONIC for CLOCK_BOOTTIME or assume different namespaces have identical offsets. Prefer existing runtimes/no added capabilities; review any needed backend helper before implementation. Keep collectors bounded, retain failures, do not disable NTP/restart WSL or change kernel/time settings incidentally. Until this gate is measured, retain INC-032 and defer real baseline/ML acceptance.
