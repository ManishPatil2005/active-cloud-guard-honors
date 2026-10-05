"""One fixed Linux RAW/timex observation; zero modes only, no clock intervention."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard import kernel_clock_state as kernel, clock_lineage as lineage
from scripts import clock_lineage as guest

SOURCES = (
    *guest.SOURCES,
    "scripts/kernel_clock_diagnostic.py",
    "cloudguard/kernel_clock_state.py",
)


def source_hashes():
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in SOURCES}


def record_packet(packets, query, sources, index):
    packet = dict(index=index, status="started", stage="state_before")
    packets.append(packet)
    try:
        packet["before"] = {}
        kernel.state_sample(query, evidence=packet["before"])
        packet["stage"] = "native_clocks"
        reply = guest.guest_snapshot(raw=True)
        lineage.checked_reply(reply, {p: sources[p] for p in guest.SOURCES}, raw=True)
        packet.update(sample=reply["sample"], domain=reply["domain"])
        packet["stage"] = "state_after"
        packet["after"] = {}
        kernel.state_sample(query, evidence=packet["after"])
        packet.update(status="accepted", stage="validate_pair")
        kernel.checked_pair(packet, packets[-2] if len(packets) > 1 else None)
        packet["stage"] = "complete"
    except (Exception, KeyboardInterrupt) as error:
        packet.update(status="failed", error_type=type(error).__name__)
        raise


def observe(report):
    report["source_sha256"] = source_hashes()
    report["phase"] = "backend"
    query, metadata = kernel.native_backend()
    kernel.checked_metadata(metadata)
    report["backend"] = metadata
    report["phase"] = "pairs"
    for index in range(kernel.READS):
        record_packet(report["packets"], query, report["source_sha256"], index)
        if index < kernel.READS - 1:
            time.sleep(1)
    report["phase"] = "postflight"
    report["source_sha256_after"] = source_hashes()
    if report["source_sha256_after"] != report["source_sha256"]:
        raise ValueError("execution sources changed")
    report["libc_sha256_after"] = hashlib.sha256(kernel.LIBC.read_bytes()).hexdigest()
    if report["libc_sha256_after"] != metadata["libc_sha256"]:
        raise ValueError("backend file changed")
    report["summary"] = kernel.summarize(report["packets"])
    report.update(status="observed", phase="complete")


def review(raw):
    report = lineage.strict_json(raw)
    sources = source_hashes()
    if (
        report["protocol"] != kernel.PROTOCOL
        or report["status"] != "observed"
        or not lineage.same(report["planned_reads"], kernel.READS)
        or not lineage.same(report["spacing_seconds"], 1)
        or report["clock_settings_modified"] is not False
        or report["sensor_started"] is not False
        or report["source_sha256"] != sources
        or report["source_sha256_after"] != sources
    ):
        raise ValueError("incompatible complete kernel receipt")
    kernel.checked_metadata(report["backend"])
    if report["libc_sha256_after"] != report["backend"]["libc_sha256"]:
        raise ValueError("backend digest changed")
    summary = kernel.summarize(report["packets"])
    if not lineage.same(report["summary"], summary):
        raise ValueError("kernel summary differs")
    return dict(
        input_sha256=hashlib.sha256(raw).hexdigest(),
        summary=summary,
        local_consistency_verified=True,
        authenticated_attestation=False,
        independently_evaluated=False,
        libc_bytes_rechecked_on_review_host=False,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument("--review")
    args = parser.parse_args()
    with Path(args.output).open("x", encoding="utf-8") as stream:
        if args.review:
            json.dump(review(Path(args.review).read_bytes()), stream, indent=2)
            stream.write("\n")
            return 0
        report = dict(
            protocol=kernel.PROTOCOL,
            executed_at=datetime.now(timezone.utc).isoformat(),
            planned_reads=kernel.READS,
            spacing_seconds=1,
            packets=[],
            status="started",
            phase="preflight",
            clock_settings_modified=False,
            sensor_started=False,
        )
        try:
            observe(report)
        except (Exception, KeyboardInterrupt) as error:
            report.update(status="failed", error_type=type(error).__name__)
        finally:
            json.dump(report, stream, indent=2)
            stream.write("\n")
    print(json.dumps(dict(status=report["status"], packets=len(report["packets"]))))
    return 0 if report["status"] == "observed" else 1


if __name__ == "__main__":
    sys.exit(main())
