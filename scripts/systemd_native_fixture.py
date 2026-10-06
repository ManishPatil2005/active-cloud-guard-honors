"""Test-only synthetic messages on an unnamed private socketpair; no broker.

Invoke one fixed case per child. This is not a receiver observation, real job
receipt, public engine interface or service-control implementation.
"""

import argparse
from contextlib import contextmanager
import ctypes as C
import gc
import json
import os
from pathlib import Path
import signal
import socket
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cloudguard import systemd_receiver as r

CASES = (
    "copied-lifetime",
    "uint32-max",
    "canceled",
    "skipped",
    "sender",
    "missing-sender",
    "path",
    "interface",
    "member",
    "method-type",
    "short-signature",
    "trailing-signature",
    "wrong-basic-type",
    "consumed-first",
    "consumed-all",
    "unsealed",
    "job-id-mismatch",
    "zero-job-id",
    "wrong-unit",
    "oversized-result",
    "invalid-result",
    "unicode-result",
    "replay",
    "overflow",
    "owner-change",
    "disconnect",
    "consumer-error",
    "consumer-interrupt",
)
IDENTITY = dict(boot_sha256="a" * 64, bus_id="b" * 32, manager_owner=":1.4242")
READER_APIS = frozenset(
    {
        "sd_bus_message_get_sender",
        "sd_bus_message_get_path",
        "sd_bus_message_get_interface",
        "sd_bus_message_get_member",
        "sd_bus_message_get_type",
        "sd_bus_message_get_signature",
        "sd_bus_message_read_basic",
        "sd_bus_message_at_end",
        "sd_bus_close_unref",
        "sd_bus_slot_unref",
    }
)


class _PrivateReader:
    def __init__(self, lib):
        self.native = lib
        self.registrations = []

    def sd_bus_add_match(self, bus, slot, rule, callback, userdata):
        # Never call AddMatch. No native slot is allocated; leave output NULL.
        assert C.cast(slot, r.PP).contents.value is None
        assert userdata is None
        self.registrations.append(rule.decode("ascii"))
        return 0

    def __getattr__(self, name):
        if name not in READER_APIS:
            raise AssertionError("fixture receiver attempted a non-reader operation")
        return getattr(self.native, name)


@contextmanager
def _private_bus():
    metadata = r._backend()  # ABI/hash/socket stat only; never opens system bus.
    lib = r._bind(C.CDLL(metadata["library_path"]))
    definitions = {
        "sd_bus_set_fd": (C.c_int, [r.P, C.c_int, C.c_int]),
        "sd_bus_message_new_signal": (C.c_int, [r.P, r.PP, r.S, r.S, r.S]),
        "sd_bus_message_set_sender": (C.c_int, [r.P, r.S]),
        "sd_bus_message_seal": (C.c_int, [r.P, C.c_uint64, C.c_uint64]),
        "sd_bus_message_rewind": (C.c_int, [r.P, C.c_int]),
    }
    for name, (result, arguments) in definitions.items():
        function = getattr(lib, name)
        function.restype, function.argtypes = result, arguments
    # Do not run _NativeBus.__init__: it connects to the fixed real system bus.
    bus = r._NativeBus.__new__(r._NativeBus)
    bus.bus, bus.slots, bus.callbacks = r.P(), [], []
    bus.fault, bus.subscribed = False, False
    bus.lib = _PrivateReader(lib)
    left, peer = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
    donated = None
    try:
        r._check(lib.sd_bus_new(C.byref(bus.bus)))
        donated = left.detach()
        r._check(lib.sd_bus_set_fd(bus.bus, donated, donated))
        donated = None  # sd-bus owns this FD from successful set_fd onward.
        r._check(lib.sd_bus_start(bus.bus))
        assert lib.sd_bus_is_open(bus.bus) == 1
        assert lib.sd_bus_is_ready(bus.bus) == 0  # No completed peer authentication.
        yield bus, lib, metadata
    finally:
        if donated is not None:
            os.close(donated)
        bus.close()
        left.close()
        peer.close()
        assert not bus.bus.value and not bus.slots and not bus.callbacks


@contextmanager
def _message(
    bus,
    lib,
    *,
    sender=":1.4242",
    path=r.MANAGER_PATH,
    interface=r.INTERFACE,
    member="JobRemoved",
    signature="uoss",
    values=None,
    method=False,
    sealed=True,
):
    if values is None:
        values = [7, "/org/freedesktop/systemd1/job/7", r.jobs.UNIT, "done"]
    message = r.P()
    try:
        if method:
            r._check(
                lib.sd_bus_message_new_method_call(
                    bus.bus,
                    C.byref(message),
                    b":1.4242",
                    path.encode(),
                    interface.encode(),
                    member.encode(),
                )
            )
        else:
            r._check(
                lib.sd_bus_message_new_signal(
                    bus.bus,
                    C.byref(message),
                    path.encode(),
                    interface.encode(),
                    member.encode(),
                )
            )
        if sender is not None:
            r._check(lib.sd_bus_message_set_sender(message, sender.encode()))
        for kind, value in zip(signature, values, strict=True):
            native = C.c_uint32(value) if kind == "u" else r.S(value.encode("utf-8"))
            pointer = C.byref(native) if kind == "u" else C.cast(native, r.P)
            r._check(lib.sd_bus_message_append_basic(message, kind.encode(), pointer))
        if sealed:
            r._check(lib.sd_bus_message_seal(message, 1, 0))
            r._check(lib.sd_bus_message_rewind(message, 1))
        yield message
        # The callback borrowed it. Native getters still work before owner unref.
        assert lib.sd_bus_message_get_member(message) == member.encode()
    finally:
        lib.sd_bus_message_unref(message)


def run_case(case):
    if case not in CASES:
        raise ValueError("unknown fixture case")
    with _private_bus() as (bus, lib, metadata):
        state = r._ReceiveState(IDENTITY)
        bus.install(IDENTITY, state)
        assert len(bus.callbacks) == len(bus.lib.registrations) == 3
        assert not bus.slots
        gc.collect()  # Receiver, not a local temporary, retains CFUNCTYPE objects.
        callback = bus.callbacks[2]
        values = [7, "/org/freedesktop/systemd1/job/7", r.jobs.UNIT, "done"]
        options = {"values": values}
        envelope_faults = {
            "sender": ("sender", ":1.4243"),
            "missing-sender": ("sender", None),
            "path": ("path", "/org/freedesktop/systemd1/other"),
            "interface": ("interface", "org.example.Other"),
            "member": ("member", "Other"),
            "method-type": ("method", True),
            "unsealed": ("sealed", False),
        }
        if case in envelope_faults:
            key, value = envelope_faults[case]
            options[key] = value
        if case == "short-signature":
            options.update(signature="uos", values=values[:3])
        if case == "trailing-signature":
            options.update(signature="uosss", values=values + ["extra"])
        if case == "wrong-basic-type":
            options.update(signature="soss", values=["7"] + values[1:])
        if case == "uint32-max":
            values[:2] = [2**32 - 1, f"/org/freedesktop/systemd1/job/{2**32 - 1}"]
        if case in {"canceled", "skipped"}:
            values[3] = case
        if case == "job-id-mismatch":
            values[0] = 8
        if case == "zero-job-id":
            values[:2] = [0, "/org/freedesktop/systemd1/job/0"]
        if case == "wrong-unit":
            values[2] = "fixture-other.service"
        if case in {"oversized-result", "invalid-result", "unicode-result"}:
            values[3] = {
                "oversized-result": "x" * 257,
                "invalid-result": "x" * 33,
                "unicode-result": "döné",
            }[case]
        if case == "owner-change":
            callback = bus.callbacks[0]
            options = dict(
                sender=r.DBUS,
                path=r.DBUS_PATH,
                interface=r.DBUS,
                member="NameOwnerChanged",
                signature="sss",
                values=[r.MANAGER, ":1.4242", ":1.4243"],
            )
        if case == "disconnect":
            callback = bus.callbacks[1]
            options = dict(
                sender=r.DBUS,
                path="/org/freedesktop/DBus/Local",
                interface="org.freedesktop.DBus.Local",
                member="Disconnected",
                signature="",
                values=[],
            )
        if case in {"consumer-error", "consumer-interrupt"}:

            def fail(sender, received):
                raise ValueError() if case == "consumer-error" else KeyboardInterrupt()

            bus._match(
                "fixture-only",
                (":1.4242", r.MANAGER_PATH, r.INTERFACE, "JobRemoved"),
                "uoss",
                fail,
            )
            callback = bus.callbacks[-1]
        count = 33 if case == "overflow" else 2 if case == "replay" else 1
        for index in range(count):
            if case == "overflow":
                values[:2] = [index + 1, f"/org/freedesktop/systemd1/job/{index + 1}"]
            with _message(bus, lib, **options) as message:
                if case == "consumed-first":
                    assert bus._read(message, "u") == 7
                if case == "consumed-all":
                    assert [bus._read(message, kind) for kind in "uoss"] == values
                assert callback(message, None, None) == 1
        # All native messages have now been unrefed; retained values are copies.
        gc.collect()
        accepted = {"copied-lifetime", "uint32-max", "canceled", "skipped"}
        continuity_faults = {"owner-change", "disconnect"}
        body_faults = {
            "job-id-mismatch",
            "zero-job-id",
            "wrong-unit",
            "invalid-result",
            "replay",
            "overflow",
        }
        assert bus.fault == (case not in accepted | continuity_faults)
        assert state.invalid == (case in continuity_faults | body_faults)
        assert len(state.events) == (
            1 if case in accepted | {"replay"} else 32 if case == "overflow" else 0
        )
        if case in accepted:
            event = state.events[values[1]]
            assert event == dict(
                sender=":1.4242",
                job_id=values[0],
                job_path=values[1],
                unit=values[2],
                result=values[3],
            )
            assert type(event["job_id"]) is int
            assert all(
                type(event[key]) is str
                for key in ("sender", "job_path", "unit", "result")
            )
            evidence = r.jobs.JobEvidence(IDENTITY, subscribed=True, matched=True)
            evidence.begin()
            evidence.removed(event)
            outcome = evidence.result(
                IDENTITY
            )  # No submitted job/reply, even synthetic.
            assert outcome["status"] == "unknown"
            assert not outcome["native_binding_verified"]
            assert not outcome["service_quiesced_verified"]
            assert not outcome["may_disarm_recovery"]
        # Subsequent valid input cannot clear a recorded fault.
        if case not in accepted and case not in {"replay", "overflow"}:
            with _message(bus, lib) as message:
                assert bus.callbacks[2](message, None, None) == 1
            assert bus.fault == (case not in continuity_faults)
            assert state.invalid == (case in continuity_faults | body_faults)
        summary = dict(
            case=case,
            passed=True,
            synthetic=True,
            native_message_decoding=True,
            broker_routing_tested=False,
            jobs_submitted_or_canceled=False,
            services_modified=False,
            native_binding_verified=False,
            may_disarm_recovery=False,
            backend=metadata,
        )
    summary["private_connection_closed"] = True
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=CASES, required=True)
    args = parser.parse_args()
    signal.signal(signal.SIGALRM, signal.SIG_DFL)
    signal.alarm(8)  # OS default termination, not an exception in a C callback.
    try:
        result = run_case(args.case)
        signal.alarm(0)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (Exception, KeyboardInterrupt) as error:
        print(
            json.dumps(
                dict(case=args.case, passed=False, error_type=type(error).__name__)
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
