"""Persist live TCP and harmless HTTP observations; fail if a service is absent."""

import json
import sys
import platform
from pathlib import Path
from urllib.request import build_opener, ProxyHandler
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.probe import probe
from cloudguard.pipeline import run


def main():
    inventory = json.loads((ROOT / "testbed/inventory.json").read_text())
    rows = [
        probe(
            e["host"],
            e["port"],
            allowlist={(e["host"], e["port"])},
            asset_id=e["asset_id"],
        )
        for e in inventory
    ]
    http = []
    opener = build_opener(ProxyHandler({}))
    for port, path in [(18080, "/"), (19000, "/minio/health/live")]:
        try:
            with opener.open(f"http://127.0.0.1:{port}{path}", timeout=2) as response:
                http.append(dict(port=port, path=path, status=response.status))
        except Exception as error:
            http.append(dict(port=port, path=path, error=type(error).__name__))
    report = dict(
        observed_at=datetime.now(timezone.utc).isoformat(),
        platform=platform.platform(),
        tcp=rows,
        http=http,
        scope="localhost service availability only; not authentication or Internet exposure",
    )
    (ROOT / "output").mkdir(exist_ok=True)
    (ROOT / "output/live-testbed.json").write_text(json.dumps(report, indent=2))
    pipeline = run(
        ROOT / "data/development/redis-all.yaml",
        ROOT / "knowledge/sources.json",
        ROOT / "testbed/inventory.json",
    )
    (ROOT / "output/pipeline-demo.json").write_text(json.dumps(pipeline, indent=2))
    print(json.dumps(report, indent=2))
    if any(e["outcome"] != "reachable" for e in rows) or any(
        e.get("status") != 200 for e in http
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
