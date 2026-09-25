"""Save a synthetic Engine 2 replay demonstration; never claim live telemetry."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard.runtime import analyze


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report = dict(
        executed_at=datetime.now(timezone.utc).isoformat(),
        evidence_level="synthetic_replay",
        live_sensor=False,
    )
    with Path(args.output).open("x", encoding="utf-8") as stream:
        try:
            report["result"] = analyze(
                [ROOT / "data/runtime/baseline-synthetic.json"],
                ROOT / "data/runtime/observation-synthetic.json",
                ROOT / "testbed/inventory.json",
            )
            result = report["result"]
            report["checks"] = dict(
                expected_states=[w["status"] for w in result["windows"]]
                == ["no_threshold_exceedance", "deviation_for_review"],
                no_actions=result["actions_executed"] == [],
                no_sensor_claim=result["runtime_sensor_connected"] is False,
                declared_synthetic=result["observation"]["source"] == "synthetic",
            )
            if not all(report["checks"].values()):
                raise ValueError("synthetic replay acceptance failed")
        except Exception as error:
            report["error"] = type(error).__name__
            raise
        finally:
            json.dump(report, stream, indent=2)
            stream.write("\n")
    print(json.dumps(report["checks"]))


if __name__ == "__main__":
    main()
