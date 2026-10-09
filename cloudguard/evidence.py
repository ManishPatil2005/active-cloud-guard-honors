"""Exclusive publication for legacy research runners; never replace evidence."""

import argparse
from contextlib import ExitStack
import json
from pathlib import Path


def evidence_main(collect, *, outputs=("output",), text_outputs=(), model=False):
    parser = argparse.ArgumentParser(description=collect.__doc__)
    for name in outputs:
        parser.add_argument("--" + name, required=True, help="Fresh output filename")
    if model:
        parser.add_argument("--model", default="qwen2.5:3b")
    args = parser.parse_args()
    streams = {}
    try:
        with ExitStack() as stack:
            # Reserve every destination before collect can read inputs or act.
            # An unsuccessful reservation can leave earlier empty new files.
            for name in outputs:
                streams[name] = stack.enter_context(
                    Path(getattr(args, name.replace("-", "_"))).open(
                        "x", encoding="utf-8", newline="\n"
                    )
                )
            try:
                reports, code = collect(args)
                if set(reports) != set(outputs):
                    raise ValueError("runner output contract mismatch")
                payloads = {
                    name: reports[name]
                    if name in text_outputs
                    else json.dumps(reports[name], indent=2, allow_nan=False) + "\n"
                    for name in outputs
                }
                if any(not isinstance(p, str) for p in payloads.values()):
                    raise ValueError("text output must be a string")
            except (Exception, KeyboardInterrupt) as error:
                code = 1
                receipt = dict(status="rejected", error_type=type(error).__name__)
                # No actions_executed=[] claim: a failure may follow real activity.
                payloads = {
                    name: json.dumps(receipt, indent=2) + "\n" for name in outputs
                }
            for name, payload in payloads.items():
                streams[name].write(payload)
        print(json.dumps(dict(status="saved" if code == 0 else "failed_saved")))
        return code
    except (Exception, KeyboardInterrupt) as error:
        print(
            json.dumps(
                dict(status="output_refused_or_failed", error_type=type(error).__name__)
            )
        )
        return 1
