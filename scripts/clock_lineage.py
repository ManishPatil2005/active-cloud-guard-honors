"""Read-only Windows/WSL clock lineage; fixed lab, no sensor or clock intervention."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard import boot_clock, clock_check, clock_lineage as lineage

SOURCES = (
    "scripts/clock_lineage.py",
    "cloudguard/clock_lineage.py",
    "cloudguard/boot_clock.py",
    "cloudguard/clock_check.py",
)
GUEST_COMMAND = (
    "wsl",
    "-d",
    "ACG-Research",
    "-u",
    "acgresearch",
    "--cd",
    "/mnt/d/research f1",
    "--exec",
    "/home/acgresearch/acg-venv/bin/python",
    "scripts/clock_lineage.py",
    "--guest-snapshot",
)


def source_hashes():
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in SOURCES}


def guest_snapshot(*, raw=False):
    domain = boot_clock.namespace_facts(
        os.readlink("/proc/self/ns/time"),
        Path("/proc/self/timens_offsets").read_text(),
        Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
    )
    domain["time_namespace_for_children"] = os.readlink(
        "/proc/self/ns/time_for_children"
    )
    boot_clock.checked_domain(domain)
    return dict(
        sample=lineage.native_snapshot(raw=raw),
        domain=domain,
        source_sha256=source_hashes(),
    )


def host_sample():
    return clock_check.sample(time.perf_counter_ns, time.time_ns)


def record_packet(packets, sources, index, *, raw=False):
    packet = dict(index=index, status="started", stage="host_first")
    packets.append(packet)
    try:
        packet["host_first"] = host_sample()
        packet["stage"] = "guest_command"
        result = subprocess.run(
            GUEST_COMMAND + ("--raw-clock",) if raw else GUEST_COMMAND,
            capture_output=True,
            timeout=lineage.TIMEOUT_SECONDS,
            check=True,
        )
        packet["stage"] = "host_last"
        packet["host_last"] = host_sample()
        packet["stage"] = "parse_guest"
        packet["guest"] = lineage.checked_reply(
            lineage.strict_json(result.stdout), sources, raw=raw
        )
        packet["comparison"] = clock_check.compare(
            packet["host_first"], packet["host_last"]
        )
        packet.update(stage="validate_packet", status="accepted")
        lineage.checked_packet(packet, sources, raw=raw)
        packet["stage"] = "complete"
    except Exception as error:
        packet.update(status="failed", error_type=type(error).__name__)
        raise


def observe(report):
    if sys.platform != "win32":
        raise ValueError("Windows host required; guest mode is separate")
    info = time.get_clock_info("perf_counter")
    report["host_counter"] = dict(
        implementation=info.implementation,
        monotonic=info.monotonic,
        adjustable=info.adjustable,
        resolution_seconds=info.resolution,
    )
    if not info.monotonic:
        raise ValueError("monotonic host performance counter required")
    report["source_sha256"] = source_hashes()
    report["phase"] = "snapshots"
    raw = report.get("raw_clock", False)
    for index in range(lineage.READS):
        if raw:
            record_packet(report["packets"], report["source_sha256"], index, raw=True)
        else:
            record_packet(report["packets"], report["source_sha256"], index)
        if index < lineage.READS - 1:
            time.sleep(lineage.GAP_SECONDS)
    report["phase"] = "source_recheck"
    report["source_sha256_after"] = source_hashes()
    if report["source_sha256_after"] != report["source_sha256"]:
        raise ValueError("source changed during observation")
    report["summary"] = lineage.summarize(
        report["packets"], report["source_sha256"], raw=raw
    )
    report.update(status="observed", phase="complete")


def review(raw):
    report = lineage.strict_json(raw)
    sources = source_hashes()
    raw_clock = report["protocol"] == lineage.RAW_PROTOCOL
    if (
        report["protocol"] not in (lineage.PROTOCOL, lineage.RAW_PROTOCOL)
        or report.get("raw_clock", False) is not raw_clock
        or report["status"] != "observed"
        or not lineage.same(report["planned_reads"], lineage.READS)
        or not lineage.same(report["spacing_seconds"], lineage.GAP_SECONDS)
        or report["source_sha256"] != sources
        or report["source_sha256_after"] != sources
        or report["clock_settings_modified"] is not False
        or report["sensor_started"] is not False
    ):
        raise ValueError("receipt protocol/source/action facts incompatible")
    summary = lineage.summarize(report["packets"], sources, raw=raw_clock)
    if not lineage.same(report["summary"], summary):
        raise ValueError("saved summary differs")
    return dict(
        input_sha256=hashlib.sha256(raw).hexdigest(),
        local_consistency_verified=True,
        summary=summary,
        independently_evaluated=False,
        authenticated_attestation=False,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--guest-snapshot", action="store_true")
    parser.add_argument("--raw-clock", action="store_true")
    parser.add_argument("--review")
    parser.add_argument("--output")
    args = parser.parse_args()
    if args.guest_snapshot:
        if args.review or args.output:
            parser.error("guest snapshot does not accept file options")
        print(json.dumps(guest_snapshot(raw=args.raw_clock)))
        return 0
    if not args.output:
        parser.error("new output path required")
    if args.review and args.raw_clock:
        parser.error("review reads the protocol from the receipt; omit --raw-clock")
    # Exclusive creation before any observation: evidence is never overwritten.
    with Path(args.output).open("x", encoding="utf-8") as stream:
        if args.review:
            report = review(Path(args.review).read_bytes())
            json.dump(report, stream, indent=2)
            stream.write("\n")
            return 0
        report = dict(
            protocol=lineage.RAW_PROTOCOL if args.raw_clock else lineage.PROTOCOL,
            raw_clock=args.raw_clock,
            executed_at=datetime.now(timezone.utc).isoformat(),
            planned_reads=lineage.READS,
            spacing_seconds=lineage.GAP_SECONDS,
            packets=[],
            status="started",
            phase="preflight",
            clock_settings_modified=False,
            sensor_started=False,
        )
        try:
            observe(report)
        except Exception as error:
            report.update(status="failed", error_type=type(error).__name__)
        finally:
            json.dump(report, stream, indent=2)
            stream.write("\n")
    print(json.dumps(dict(status=report["status"], packets=len(report["packets"]))))
    return 0 if report["status"] == "observed" else 1


if __name__ == "__main__":
    sys.exit(main())
