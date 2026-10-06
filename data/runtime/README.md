# Synthetic runtime replay fixtures

## Additional ML software fixtures — 6 October 2026

ml-baseline-synthetic.json and ml-observation-synthetic.json were authored for the optional [synthetic ML comparator](../../docs/SYNTHETIC_RUNTIME_ML.md). January3/4timestamps are invented coordinates, not backdated observations. Container ID64a is a placeholder. Baseline32one-minute windows use process1or2/file2..4/connect1..3; three observation windows use (process,file,connect)=(1,2,1),(1,2,16),(2,3,2). All events and scenario groups are developer-authored, not independent labels, attacks or benign recordings. These fixtures must remain development software data. Existing fixtures described below are unchanged and historical.

These files were authored on 2026-09-25 to test Engine 2 software behavior. Event timestamps are invented test coordinates, not historical sensor captures. Container ID consisting of 64 `f` characters is a placeholder, not the running Redis container.

Baseline: three nonempty one-minute windows, each containing one process_start, one network_connect and one file_open. Observation: one identical count window, followed by nine network_connect events. Expected default-threshold outcomes: no_threshold_exceedance then deviation_for_review. Neither is a threat or safety label. The different scenario_group strings exercise a leakage guard; these fixtures are not an independent benchmark.

No actual attacks, eBPF/Kubernetes telemetry or benign workload recording are represented. Do not add production command lines, secrets or unrestricted raw logs here. Live sensor integration and independent scenario labels remain separate work.
