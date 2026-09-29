"""Descriptive two-pair Docker-exec latency summary; not a general overhead claim."""

import argparse
import json
from pathlib import Path
from statistics import mean
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.verification import read_json


def summarize(directory):
    directory = Path(directory)
    manifest, manifest_hash = read_json(directory / "manifest.json")
    expected = ["clock", "off-1", "on-1", "on-2", "off-2"]
    if manifest.get("status") != "completed" or manifest.get("sequence") != [
        dict(name=n, exit_code=0) for n in expected
    ]:
        raise ValueError("complete planned pilot required; no survivor-only summary")
    rows, identities = {}, []
    for name in expected[1:]:
        run, digest = read_json(directory / (name + ".json"))
        on = name.startswith("on")
        status = "events_observed" if on else "completed"
        before_key = "target_identity_before" if on else "identity_before"
        after_key = "target_identity_after" if on else "identity_after"
        m = run.get("measurement", {})
        if (
            run.get("status") != status
            or run.get("warmup_protocol") != "two_pings_v1"
            or m.get("status") != "completed"
            or m.get("profile") != "ping_4"
            or m.get("scenario_group") != "redis-ping-development"
            or len(m.get("calls", [])) != 4
            or not run.get(before_key)
            or run[before_key] != run.get(after_key)
            or (on and run.get("sensor_removed") is not True)
            or (
                not on
                and (
                    run.get("mode") != "sensor_off_control"
                    or run.get("sensor_started") is not False
                )
            )
        ):
            raise ValueError("incompatible or failed run")
        times = []
        for call in m["calls"]:
            value = call.get("docker_exec_round_trip_ns")
            if call.get("pong") is not True or type(value) is not int or value <= 0:
                raise ValueError("invalid workload latency")
            times.append(value / 1_000_000)
        identities.append(run[before_key])
        rows[name] = dict(
            receipt_sha256=digest, mean_docker_exec_ms=mean(times), calls_ms=times
        )
    if any(i != identities[0] for i in identities):
        raise ValueError("target identity changed across pilot")
    pairs = []
    for number in (1, 2):
        off, on = (
            rows[f"off-{number}"]["mean_docker_exec_ms"],
            rows[f"on-{number}"]["mean_docker_exec_ms"],
        )
        pairs.append(
            dict(
                pair=number,
                on_minus_off_ms=on - off,
                relative_difference_percent=(on - off) / off * 100,
            )
        )
    return dict(
        manifest_sha256=manifest_hash,
        runs=rows,
        pairs=pairs,
        independent_evaluation=False,
        sensor_cpu_memory_overhead=None,
        threat_confirmed=False,
        interpretation="Descriptive two-pair Docker-exec latency contrasts only; not a calibrated sensor-overhead or significance estimate.",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if Path(args.output).exists():
        raise FileExistsError("choose a new report path")
    result = summarize(args.directory)
    with Path(args.output).open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
