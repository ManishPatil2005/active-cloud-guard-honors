"""Inert-only guest fencing prototype: no service commands or native binding."""

from contextlib import contextmanager
import json
import math
import os
from pathlib import Path
import re
import sys
import time

PROTOCOL = "inert_guest_fence_v1"


def bounded_timeout(value):
    if (
        type(value) not in {int, float}
        or not math.isfinite(value)
        or not 0 < value <= 5
    ):
        raise ValueError("invalid fence lock budget")
    return value


def nonce_value(value):
    if not isinstance(value, str) or not re.fullmatch("[0-9a-f]{64}", value):
        raise ValueError("invalid fence nonce")
    return value


def exclusive(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(value, stream)
        stream.flush()
        os.fsync(stream.fileno())


def read(path):
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise ValueError("duplicate fence field")
            value[key] = item
        return value

    with Path(path).open("rb") as stream:
        data = stream.read(4097)
    if len(data) > 4096:
        raise ValueError("fence record too large")
    return json.loads(data, object_pairs_hook=pairs)


@contextmanager
def linux_lock(path, timeout):
    """Independent opens, no inherited handles; advisory and local-filesystem only."""
    if sys.platform != "linux":
        raise ValueError("native fence lock requires Linux")
    import fcntl

    deadline = time.monotonic() + bounded_timeout(timeout)
    fd = os.open(path, os.O_RDWR | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise TimeoutError("fence lock unavailable") from None
                time.sleep(0.01)
        yield
    finally:
        os.close(fd)


class InertGuestFence:
    """Caller-supplied simulations only; never connect to real service actions.

    The callback's return is a simulation acknowledgment, not proof of job drain.
    Sessions are exclusive and terminal after recovery; never delete/reopen seal.
    """

    def __init__(self, directory, nonce, *, lock=None, clock=None):
        self.directory = Path(directory)
        self.nonce = nonce_value(nonce)
        self.lock = lock or linux_lock
        self.clock = clock or time.monotonic_ns
        request = read(self.directory / "request.json")
        if (
            not isinstance(request, dict)
            or set(request) != {"protocol", "mode", "nonce", "deadline_ns"}
            or request["protocol"] != PROTOCOL
            or request["mode"] != "inert"
            or request["nonce"] != self.nonce
            or type(request["deadline_ns"]) is not int
            or request["deadline_ns"] <= 0
        ):
            raise ValueError("incompatible inert fence request")
        self.deadline_ns = request["deadline_ns"]

    @classmethod
    def initialize(cls, directory, nonce, *, inert=False, lock=None, clock=None):
        if inert is not True:
            raise ValueError("only explicit inert sessions supported")
        nonce_value(nonce)
        clock = clock or time.monotonic_ns
        deadline = clock() + 60_000_000_000
        directory = Path(directory)
        directory.mkdir(exist_ok=False)
        (directory / "session.lock").open("x").close()
        exclusive(
            directory / "request.json",
            dict(protocol=PROTOCOL, mode="inert", nonce=nonce, deadline_ns=deadline),
        )
        return cls(directory, nonce, lock=lock, clock=clock)

    def stop(self, simulate, *, timeout=5):
        timeout = bounded_timeout(timeout)
        with self.lock(self.directory / "session.lock", timeout):
            if (self.directory / "sealed.json").exists():
                raise ValueError("recovery permanently sealed this session")
            if self.clock() >= self.deadline_ns:
                raise TimeoutError("stop request expired")
            intent = self.directory / "stop-intent.json"
            exclusive(intent, dict(nonce=self.nonce))
            # Recovery may seal while we hold the lock; it must then wait for us.
            if (self.directory / "sealed.json").exists():
                raise ValueError("recovery sealed before simulated dispatch")
            if simulate() is not True:
                raise ValueError("simulation acknowledgment required")
            exclusive(self.directory / "stop-complete.json", dict(nonce=self.nonce))
        return dict(mode="inert", status="simulated_stop_completed")

    def recover(self, simulate, *, timeout=5):
        timeout = bounded_timeout(timeout)
        # Publish terminal closure BEFORE waiting on the operation lock.
        # Even a malformed/partial seal prevents later stop admission.
        seal = self.directory / "sealed.json"
        try:
            exclusive(seal, dict(nonce=self.nonce))
        except FileExistsError:
            if read(seal) != dict(nonce=self.nonce):
                raise ValueError("fence seal differs") from None
        with self.lock(self.directory / "session.lock", timeout):
            if (self.directory / "recovery.json").exists():
                raise FileExistsError("recovery result already exists")
            intent = self.directory / "stop-intent.json"
            complete = self.directory / "stop-complete.json"
            # An interrupted intent is UNKNOWN, even when recovery looks active.
            known = not intent.exists() and not complete.exists()
            if intent.exists():
                try:
                    known = read(intent) == read(complete) == dict(nonce=self.nonce)
                except (Exception, KeyboardInterrupt):
                    known = False
            exclusive(self.directory / "recover-intent.json", dict(nonce=self.nonce))
            if simulate() is not True:
                raise ValueError("recovery simulation acknowledgment required")
            result = dict(
                mode="inert",
                status="simulated_recovery_observed",
                new_stop_requests_fenced=True,
                submitted_stop_quiescence_known=known,
                operator_recovery_required=not known,
                native_service_validated=False,
            )
            exclusive(self.directory / "recovery.json", result)
            return result
