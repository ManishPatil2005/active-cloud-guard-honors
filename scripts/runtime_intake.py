"""Inspect a dedicated offline bundle; save a fresh minimized consistency report."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cloudguard.runtime_intake import ANNOTATION_PROTOCOL, annotation_index, inspect


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    output_mode = parser.add_mutually_exclusive_group()
    output_mode.add_argument(
        "--annotation-index",
        action="store_true",
        help="Index observed units for a coordinator, not a blinded packet or labels",
    )
    output_mode.add_argument(
        "--review-agreement",
        action="store_true",
        help="Add original-review agreement counts and known-pair Cohen kappa",
    )
    args = parser.parse_args()
    destination = Path(args.output)
    manifest = Path(args.manifest)
    try:
        if destination.resolve().is_relative_to(manifest.parent.resolve()):
            raise ValueError("output must be outside input bundle")
        with destination.open("x", encoding="utf-8") as stream:
            try:
                report = (
                    annotation_index(manifest)
                    if args.annotation_index
                    else inspect(manifest, include_review_agreement=True)
                    if args.review_agreement
                    else inspect(manifest)
                )
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
                if args.annotation_index:
                    report.update(
                        protocol=ANNOTATION_PROTOCOL,
                        labels_created=False,
                        supervisor_approval_verified=False,
                        blinding_verified=False,
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
