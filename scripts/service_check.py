"""Capture read-only identity/protocol checks without replacing historical evidence."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.service_probe import verify_service


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report = dict(
        started_at=datetime.now(timezone.utc).isoformat(),
        observations=[],
        scope="Existing authorized loopback Compose lab; no credentials, SQL, data writes or container mutations",
    )
    with Path(args.output).open("x", encoding="utf-8") as stream:
        try:
            for service in ("redis", "postgres"):
                report["observations"].append(
                    verify_service(
                        ROOT / "testbed/compose.yaml",
                        ROOT / "testbed/inventory.json",
                        service,
                    )
                )
            report["checks"] = dict(
                identity_stable=all(r["usable"] for r in report["observations"]),
                protocol_observed=all(
                    r["service_observation"]
                    and r["service_observation"]["status"]
                    not in {"inconclusive", "unreachable"}
                    for r in report["observations"]
                ),
            )
        except Exception as error:
            report["error"] = type(error).__name__  # No subprocess/config payload.
            raise
        finally:
            json.dump(report, stream, indent=2)
            stream.write("\n")
    print(json.dumps(report["checks"]))
    if not all(report["checks"].values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
