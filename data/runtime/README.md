# Synthetic runtime replay fixtures

These files were authored on 2026-09-25 to test Engine 2 software behavior. Event timestamps are invented test coordinates, not historical sensor captures. Container ID consisting of 64 `f` characters is a placeholder, not the running Redis container.

Baseline: three nonempty one-minute windows, each containing one process_start, one network_connect and one file_open. Observation: one identical count window, followed by nine network_connect events. Expected default-threshold outcomes: no_threshold_exceedance then deviation_for_review. Neither is a threat or safety label. The different scenario_group strings exercise a leakage guard; these fixtures are not an independent benchmark.

No actual attacks, eBPF/Kubernetes telemetry or benign workload recording are represented. Do not add production command lines, secrets or unrestricted raw logs here. Live sensor integration and independent scenario labels remain separate work.
