"""Independent one-shot restoration helper; --inert never calls WSL or services."""

import argparse
import os
from pathlib import Path
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloudguard import clock_comparison as control
from scripts import (
    clock_comparison_transport as transport,
    clock_comparison_review as review,
)


def watch(directory, *, inert=False, clock=None, sleep=None):
    clock, sleep = clock or time.monotonic_ns, sleep or time.sleep
    directory = Path(directory).resolve()
    request = transport.read_json(directory / "watchdog-request.json")
    mode = "inert" if inert else "restore"
    if (
        set(request) != {"mode", "approved", "nonce", "deadline_ns", "sources"}
        or request["mode"] != mode
        or request["approved"] is not True
        or not isinstance(request["nonce"], str)
        or not re.fullmatch(r"[0-9a-f]{64}", request["nonce"])
        or type(request["deadline_ns"]) is not int
        or not 0 < request["deadline_ns"] - clock() <= 60_000_000_000
        or request["sources"] != review.execution_source_hashes()
    ):
        raise ValueError("incompatible watchdog request")
    if not inert and (
        sys.platform != "win32" or directory != transport.RUN_DIR.resolve()
    ):
        raise ValueError("fixed Windows restoration directory required")
    nonce = request["nonce"]
    transport.save_exclusive(
        directory / "watchdog-ready.json",
        dict(
            mode=mode,
            nonce=nonce,
            pid=os.getpid(),
            deadline_ns=request["deadline_ns"],
        ),
    )
    (directory / "watchdog-ready.signal").open("x").close()
    outcome = dict(mode=mode, nonce=nonce, pid=os.getpid(), status="started")
    try:
        while clock() < request["deadline_ns"]:
            if (directory / "watchdog-cancel.signal").exists():
                try:
                    cancel = transport.read_json(directory / "watchdog-cancel.json")
                    if cancel == dict(nonce=nonce):
                        if not inert:
                            control.checked_service(transport.service_state(5))
                        outcome["status"] = "inert_disarmed" if inert else "disarmed"
                        break
                except (Exception, KeyboardInterrupt):
                    pass  # Bad cancel/state must not defeat deadline restoration.
            sleep(0.02)
    except (Exception, KeyboardInterrupt) as error:
        outcome["trigger_error_type"] = type(error).__name__
    if outcome["status"] == "started":
        try:
            if not inert:
                transport.start_service(5)
                control.checked_service(transport.service_state(5))
            outcome["status"] = "inert_elapsed" if inert else "restored_at_deadline"
        except (Exception, KeyboardInterrupt) as error:
            outcome.update(status="failed", error_type=type(error).__name__)
    transport.save_exclusive(directory / "watchdog-outcome.json", outcome)
    return 1 if outcome["status"] == "failed" else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", required=True)
    parser.add_argument("--inert", action="store_true")
    args = parser.parse_args()
    try:
        return watch(args.directory, inert=args.inert)
    except (Exception, KeyboardInterrupt):
        return 1  # Refused before readiness: no exception messages exported.


if __name__ == "__main__":
    sys.exit(main())
