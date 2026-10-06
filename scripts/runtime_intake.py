"""Inspect a dedicated offline bundle; save a fresh minimized consistency report."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cloudguard.runtime_intake import inspect


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    destination = Path(args.output)
    manifest = Path(args.manifest)
    try:
        if destination.resolve().is_relative_to(manifest.parent.resolve()):
            raise ValueError("output must be outside input bundle")
        with destination.open("x", encoding="utf-8") as stream:
            try:
                report = inspect(manifest)
                code = 0
            except (Exception, KeyboardInterrupt) as error:
                report = dict(
                    protocol="runtime_intake_v1",
                    status="rejected",
                    error_type=type(error).__name__,
                    independent_evaluation_verified=False,
                    model_fitting_authorized=False,
                    predictions_computed=False,
                    actions_executed=[],
                )
                code = 1
            json.dump(report, stream, indent=2)
            stream.write("\n")
        print(json.dumps(dict(status=report["status"], model_fitting_authorized=False)))
        return code
    except (Exception, KeyboardInterrupt) as error:
        print(
            json.dumps(
                dict(status="output_refused_or_failed", error_type=type(error).__name__)
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
