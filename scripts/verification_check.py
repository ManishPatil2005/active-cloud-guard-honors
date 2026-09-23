"""Real local sockets, synthetic policies; no deployed Redis or LLM claim."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import socketserver
import sys
import tempfile
import threading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.pipeline import run
from cloudguard.verification import file_hash


class AcceptOnly(socketserver.BaseRequestHandler):
    def handle(self):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    result = dict(
        started_at=datetime.now(timezone.utc).isoformat(),
        platform=platform.platform(),
        observations=[],
        scope="Synthetic configuration analogue and real loopback listener; no actual service deployment, model inference, human review or independent benchmark",
    )
    # Refuse overwriting historical evidence, including failed runs.
    with target.open("x", encoding="utf-8") as output:

        def save():
            output.seek(0)
            json.dump(result, output, indent=2)
            output.write("\n")
            output.truncate()
            output.flush()

        try:
            with tempfile.TemporaryDirectory(
                prefix="cloudguard-verification-"
            ) as temporary:
                directory = Path(temporary)
                source, inventory, policy = [
                    directory / name
                    for name in ("input.yaml", "inventory.json", "policy.json")
                ]
                source.write_text(
                    'services: {probe_target: {ports: ["12345:12345"]}}\n',
                    encoding="utf-8",
                )
                with socketserver.TCPServer(("127.0.0.1", 0), AcceptOnly) as server:
                    worker = threading.Thread(target=server.serve_forever, daemon=True)
                    worker.start()
                    try:
                        inventory.write_text(
                            json.dumps(
                                [
                                    dict(
                                        asset_id="compose/probe_target",
                                        host="127.0.0.1",
                                        port=server.server_address[1],
                                    )
                                ]
                            ),
                            encoding="utf-8",
                        )
                        for expectation in ("allowed", "forbidden"):
                            policy.write_text(
                                json.dumps(
                                    dict(
                                        version="1.0",
                                        configuration_sha256=file_hash(source),
                                        inventory_sha256=file_hash(inventory),
                                        reviewed_by="synthetic-smoke-policy-not-human-review",
                                        rationale="Controlled software check only",
                                        assets=[
                                            dict(
                                                asset_id="compose/probe_target",
                                                expected_reachability=expectation,
                                                relationship="analogue",
                                            )
                                        ],
                                    )
                                ),
                                encoding="utf-8",
                            )
                            report = run(
                                source,
                                ROOT / "knowledge/sources.json",
                                inventory,
                                policy=policy,
                            )
                            result["observations"].append(
                                dict(expectation=expectation, report=report)
                            )
                            save()
                        source.write_text(
                            source.read_text(encoding="utf-8") + "\n", encoding="utf-8"
                        )
                        try:
                            run(
                                source,
                                ROOT / "knowledge/sources.json",
                                inventory,
                                policy=policy,
                            )
                        except ValueError as error:
                            result["stale_binding_rejected"] = (
                                str(error) == "stale configuration/inventory binding"
                            )
                        else:
                            result["stale_binding_rejected"] = False
                    finally:
                        server.shutdown()
                        worker.join(timeout=2)
            findings = [x["report"]["findings"][0] for x in result["observations"]]
            result["checks"] = dict(
                real_connections=all(
                    f["probe"]["outcome"] == "reachable" for f in findings
                ),
                policy_distinction=[f["verification"]["status"] for f in findings]
                == ["expected_reachability", "unexpected_reachability"],
                no_suppression=all(
                    not f["verification"]["finding_suppressed"] for f in findings
                ),
                fresh_observations=len({f["probe"]["observed_at"] for f in findings})
                == 2,
                stale_binding_rejected=result["stale_binding_rejected"],
            )
            if not all(result["checks"].values()):
                raise RuntimeError("verification smoke acceptance failed")
            result["completed_at"] = datetime.now(timezone.utc).isoformat()
            save()
        except Exception as error:
            result["error"] = dict(type=type(error).__name__, message=str(error))
            save()
            raise
    print(json.dumps(result["checks"]))


if __name__ == "__main__":
    main()
