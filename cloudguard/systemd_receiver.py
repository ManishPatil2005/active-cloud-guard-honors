"""Isolated Linux sd-bus notification diagnostic; never submit/control a job.

Only reviewed nonvariadic APIs are bound. Native calls trust the local OS and
library; bounded pumping is not a hard deadline against a hung native call.
"""

import ctypes as C
import hashlib
import os
from pathlib import Path
import platform
import re
import stat
import sys
import time

from cloudguard import systemd_job as jobs

DBUS = "org.freedesktop.DBus"
DBUS_PATH = "/org/freedesktop/DBus"
MANAGER = "org.freedesktop.systemd1"
MANAGER_PATH = "/org/freedesktop/systemd1"
INTERFACE = MANAGER + ".Manager"
LIBRARY = Path("/lib/x86_64-linux-gnu/libsystemd.so.0")
LIBRARY_SHA256 = "bdf59c828b547bcdbe7b3576c0810d9d9d2e982d8b61b365812542da6a4c4a99"
SOCKET = Path("/run/dbus/system_bus_socket")
CALL_USEC = 1_000_000
WINDOW_SECONDS = 5
PROCESS_LIMIT = 512
EVENT_LIMIT = 32
HANDLER = C.CFUNCTYPE(C.c_int, C.c_void_p, C.c_void_p, C.c_void_p)
P = C.c_void_p
PP = C.POINTER(P)
S = C.c_char_p


def _check(value):
    if value < 0:
        raise OSError(-value, "native bus operation failed")
    return value


def _text(raw, limit=256):
    if raw is None or len(raw) > limit:
        raise ValueError("missing or oversized native string")
    return raw.decode("ascii", errors="strict")


def _backend():
    if (
        sys.platform != "linux"
        or platform.machine() != "x86_64"
        or sys.byteorder != "little"
        or C.sizeof(P) != 8
        or C.sizeof(C.c_long) != 8
        or platform.libc_ver() != ("glibc", "2.39")
        or os.geteuid() == 0
    ):
        raise RuntimeError("unreviewed or privileged receiver backend")
    if not stat.S_ISSOCK(SOCKET.stat().st_mode):
        raise RuntimeError("fixed system bus socket unavailable")
    digest = hashlib.sha256(LIBRARY.read_bytes()).hexdigest()
    if digest != LIBRARY_SHA256:
        raise RuntimeError("native library requires fresh review")
    return dict(
        library_path=str(LIBRARY.resolve(strict=True)),
        library_sha256=digest,
        abi="linux-x86_64-lp64-little-glibc2.39",
        uid=os.geteuid(),
    )


def _bind(lib):
    """All types below follow the tagged v255.4 sd-bus.h header."""
    definitions = {
        "sd_bus_new": (C.c_int, [PP]),
        "sd_bus_set_address": (C.c_int, [P, S]),
        "sd_bus_set_bus_client": (C.c_int, [P, C.c_int]),
        "sd_bus_set_allow_interactive_authorization": (C.c_int, [P, C.c_int]),
        "sd_bus_set_exit_on_disconnect": (C.c_int, [P, C.c_int]),
        "sd_bus_set_method_call_timeout": (C.c_int, [P, C.c_uint64]),
        "sd_bus_start": (C.c_int, [P]),
        "sd_bus_is_open": (C.c_int, [P]),
        "sd_bus_is_ready": (C.c_int, [P]),
        "sd_bus_close_unref": (P, [P]),
        "sd_bus_slot_unref": (P, [P]),
        "sd_bus_message_unref": (P, [P]),
        "sd_bus_message_new_method_call": (C.c_int, [P, PP, S, S, S, S]),
        "sd_bus_message_set_auto_start": (C.c_int, [P, C.c_int]),
        "sd_bus_message_append_basic": (C.c_int, [P, C.c_char, P]),
        "sd_bus_call": (C.c_int, [P, P, C.c_uint64, P, PP]),
        "sd_bus_message_get_type": (C.c_int, [P, C.POINTER(C.c_uint8)]),
        "sd_bus_message_get_cookie": (C.c_int, [P, C.POINTER(C.c_uint64)]),
        "sd_bus_message_get_reply_cookie": (C.c_int, [P, C.POINTER(C.c_uint64)]),
        "sd_bus_message_get_signature": (S, [P, C.c_int]),
        "sd_bus_message_get_sender": (S, [P]),
        "sd_bus_message_get_path": (S, [P]),
        "sd_bus_message_get_interface": (S, [P]),
        "sd_bus_message_get_member": (S, [P]),
        "sd_bus_message_read_basic": (C.c_int, [P, C.c_char, P]),
        "sd_bus_message_at_end": (C.c_int, [P, C.c_int]),
        "sd_bus_add_match": (C.c_int, [P, PP, S, HANDLER, P]),
        "sd_bus_process": (C.c_int, [P, PP]),
        "sd_bus_wait": (C.c_int, [P, C.c_uint64]),
    }
    for name, (result, arguments) in definitions.items():
        function = getattr(lib, name)
        function.restype, function.argtypes = result, arguments
    return lib


class _NativeBus:
    """One ordinary-user connection. Internal method calls are allowlisted."""

    def __init__(self):
        self.metadata = _backend()
        self.lib = _bind(C.CDLL(self.metadata["library_path"]))
        self.bus = P()
        self.slots = []
        self.callbacks = []  # Keep C callback addresses alive until bus is closed.
        self.subscribed = False
        self.fault = False
        try:
            _check(self.lib.sd_bus_new(C.byref(self.bus)))
            _check(
                self.lib.sd_bus_set_address(
                    self.bus, b"unix:path=/run/dbus/system_bus_socket"
                )
            )
            _check(self.lib.sd_bus_set_bus_client(self.bus, 1))
            _check(self.lib.sd_bus_set_allow_interactive_authorization(self.bus, 0))
            _check(self.lib.sd_bus_set_exit_on_disconnect(self.bus, 0))
            _check(self.lib.sd_bus_set_method_call_timeout(self.bus, CALL_USEC))
            _check(self.lib.sd_bus_start(self.bus))
        except BaseException:
            self.close()
            raise

    def _read(self, message, kind):
        value = C.c_uint32() if kind == "u" else S()
        if (
            _check(
                self.lib.sd_bus_message_read_basic(
                    message, kind.encode(), C.byref(value)
                )
            )
            == 0
        ):
            raise ValueError("missing native basic argument")
        return value.value if kind == "u" else _text(value.value)

    def _type(self, message):
        value = C.c_uint8()
        _check(self.lib.sd_bus_message_get_type(message, C.byref(value)))
        return value.value

    def _call(self, member, owner=None):
        if member not in {"GetId", "GetNameOwner", "Subscribe", "Unsubscribe"}:
            raise ValueError("non-observation method refused")
        broker = member in {"GetId", "GetNameOwner"}
        destination = DBUS if broker else owner
        if not broker and (
            not isinstance(owner, str) or not re.fullmatch(r":[0-9]+\.[0-9]+", owner)
        ):
            raise ValueError("unique manager destination required")
        request, reply = P(), P()
        try:
            _check(
                self.lib.sd_bus_message_new_method_call(
                    self.bus,
                    C.byref(request),
                    destination.encode(),
                    (DBUS_PATH if broker else MANAGER_PATH).encode(),
                    (DBUS if broker else INTERFACE).encode(),
                    member.encode(),
                )
            )
            _check(self.lib.sd_bus_message_set_auto_start(request, 0))
            if member == "GetNameOwner":
                # append_basic('s') takes char[], not char**. Bytes copied by sd-bus.
                _check(
                    self.lib.sd_bus_message_append_basic(
                        request, b"s", C.cast(S(MANAGER.encode()), P)
                    )
                )
            _check(
                self.lib.sd_bus_call(self.bus, request, CALL_USEC, None, C.byref(reply))
            )
            sent, returned = C.c_uint64(), C.c_uint64()
            _check(self.lib.sd_bus_message_get_cookie(request, C.byref(sent)))
            _check(self.lib.sd_bus_message_get_reply_cookie(reply, C.byref(returned)))
            signature = "s" if broker else ""
            if (
                sent.value == 0
                or returned.value != sent.value
                or self._type(reply) != 2
                or _text(self.lib.sd_bus_message_get_sender(reply), 64) != destination
                or _text(self.lib.sd_bus_message_get_signature(reply, 1), 16)
                != signature
            ):
                raise ValueError("incompatible native method reply")
            value = self._read(reply, "s") if broker else None
            if _check(self.lib.sd_bus_message_at_end(reply, 1)) != 1:
                raise ValueError("trailing native reply arguments")
            return value
        finally:
            self.lib.sd_bus_message_unref(reply)
            self.lib.sd_bus_message_unref(request)

    def identity(self):
        boot = Path("/proc/sys/kernel/random/boot_id").read_bytes()
        if not re.fullmatch(rb"[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\n", boot):
            raise ValueError("invalid native boot identifier")
        return jobs.epoch(
            dict(
                boot_sha256=hashlib.sha256(boot).hexdigest(),
                bus_id=self._call("GetId"),
                manager_owner=self._call("GetNameOwner"),
            )
        )

    def _match(self, rule, expected, kinds, consumer):
        def callback(message, userdata, error):
            try:
                actual = (
                    _text(self.lib.sd_bus_message_get_sender(message), 64),
                    _text(self.lib.sd_bus_message_get_path(message)),
                    _text(self.lib.sd_bus_message_get_interface(message)),
                    _text(self.lib.sd_bus_message_get_member(message)),
                )
                if (
                    self._type(message) != 4
                    or any(
                        wanted is not None and got != wanted
                        for got, wanted in zip(actual, expected, strict=True)
                    )
                    or _text(self.lib.sd_bus_message_get_signature(message, 1), 16)
                    != kinds
                ):
                    raise ValueError("incompatible selected signal envelope")
                values = [self._read(message, kind) for kind in kinds]
                if _check(self.lib.sd_bus_message_at_end(message, 1)) != 1:
                    raise ValueError("trailing native signal arguments")
                consumer(actual[0], values)
            except BaseException:
                # No Python exception may cross the C callback boundary.
                self.fault = True
            return 1

        handler, slot = HANDLER(callback), P()
        self.callbacks.append(handler)
        try:
            _check(
                self.lib.sd_bus_add_match(
                    self.bus, C.byref(slot), rule.encode(), handler, None
                )
            )
        finally:
            if slot.value:
                self.slots.append(slot)

    def install(self, identity, state):
        self._match(
            "type='signal',sender='org.freedesktop.DBus',path='/org/freedesktop/DBus',interface='org.freedesktop.DBus',member='NameOwnerChanged',arg0='org.freedesktop.systemd1'",
            (DBUS, DBUS_PATH, DBUS, "NameOwnerChanged"),
            "sss",
            state.owner_changed,
        )
        self._match(
            "type='signal',path='/org/freedesktop/DBus/Local',interface='org.freedesktop.DBus.Local',member='Disconnected'",
            (
                None,
                "/org/freedesktop/DBus/Local",
                "org.freedesktop.DBus.Local",
                "Disconnected",
            ),
            "",
            state.disconnected,
        )
        owner = identity["manager_owner"]
        self._match(
            f"type='signal',sender='{owner}',path='{MANAGER_PATH}',interface='{INTERFACE}',member='JobRemoved',arg2='{jobs.UNIT}'",
            (owner, MANAGER_PATH, INTERFACE, "JobRemoved"),
            "uoss",
            state.removed,
        )

    def subscribe(self, owner):
        self._call("Subscribe", owner)
        self.subscribed = True

    def ready(self):
        return (
            not self.fault
            and self.lib.sd_bus_is_open(self.bus) == 1
            and self.lib.sd_bus_is_ready(self.bus) == 1
        )

    def process(self):
        return _check(self.lib.sd_bus_process(self.bus, None))

    def wait(self, usec):
        _check(self.lib.sd_bus_wait(self.bus, usec))

    def unsubscribe(self, owner):
        self._call("Unsubscribe", owner)
        self.subscribed = False

    def close(self):
        for slot in self.slots:
            self.lib.sd_bus_slot_unref(slot)
        self.slots.clear()
        if self.bus.value:
            self.lib.sd_bus_close_unref(self.bus)
            self.bus = P()
        self.callbacks.clear()


class _ReceiveState:
    def __init__(self, identity):
        self.identity = jobs.epoch(identity)
        self.invalid = False
        self.events = {}

    def owner_changed(self, sender, values):
        self.invalid = True  # Even a return to the same unique owner stays unknown.

    def disconnected(self, sender, values):
        self.invalid = True

    def removed(self, sender, values):
        try:
            identifier, path, unit, result = values
            event = dict(
                sender=sender,
                job_id=identifier,
                job_path=path,
                unit=unit,
                result=result,
            )
            # Reuse the strict decoded-event validator without claiming a submission.
            validator = jobs.JobEvidence(self.identity, subscribed=True, matched=True)
            validator.begin()
            if not validator.removed(event):
                raise ValueError("unexpected selected unit")
            if path in self.events or len(self.events) >= EVENT_LIMIT:
                raise ValueError("selected event limit or replay")
            self.events[path] = event
        except BaseException:
            self.invalid = True
            raise


def _observe(bus, now=time.monotonic):
    """Injected orchestration for tests; production observe always uses native bus."""
    report = dict(
        protocol="systemd_receive_readonly_v1",
        status="unknown",
        stage="identity",
        backend=dict(bus.metadata),
        window_seconds=WINDOW_SECONDS,
        process_limit=PROCESS_LIMIT,
        process_calls=0,
        events=[],
        matches_acknowledged=False,
        subscription_acknowledged=False,
        continuity_checks_passed=False,
        subscription_released=False,
        connection_closed=False,
        jobs_submitted_or_canceled=False,
        services_modified=False,
        native_binding_verified=False,
        service_quiesced_verified=False,
        may_disarm_recovery=False,
    )
    state = None
    try:
        identity = bus.identity()
        report["epoch_before"] = identity
        state = _ReceiveState(identity)
        report["stage"] = "matches"
        bus.install(identity, state)
        report["matches_acknowledged"] = True
        report["stage"] = "subscribe"
        bus.subscribe(identity["manager_owner"])
        report["subscription_acknowledged"] = True
        report["stage"] = "identity_after_setup"
        if bus.identity() != identity or state.invalid or not bus.ready():
            raise ValueError("identity or stream changed during setup")
        deadline = now() + WINDOW_SECONDS
        report["stage"] = "receive"
        while now() < deadline:
            if report["process_calls"] >= PROCESS_LIMIT:
                raise ValueError("receive processing limit")
            report["process_calls"] += 1
            processed = bus.process()
            if state.invalid or not bus.ready():
                raise ValueError("receive continuity fault")
            if processed == 0:
                bus.wait(min(100_000, max(0, int((deadline - now()) * 1_000_000))))
        report["stage"] = "identity_after_window"
        report["epoch_after"] = bus.identity()
        if report["epoch_after"] != identity or state.invalid or not bus.ready():
            raise ValueError("identity or stream changed after window")
        report["stage"] = "unsubscribe"
        bus.unsubscribe(identity["manager_owner"])
        report["subscription_released"] = True
        if state.invalid or not bus.ready():
            raise ValueError("receive fault during unsubscribe")
        report["continuity_checks_passed"] = True
        report.update(status="observed", stage="complete")
    except (Exception, KeyboardInterrupt) as error:
        report["error_type"] = type(error).__name__
        if (
            isinstance(error, OSError)
            and type(error.errno) is int
            and 0 < error.errno < 4096
        ):
            report["error_errno"] = error.errno
    finally:
        if state:
            report["events"] = [dict(value) for value in state.events.values()]
        try:
            # Disconnect also drops any subscription if setup/unsubscribe failed.
            bus.close()
            report["connection_closed"] = True
        except (Exception, KeyboardInterrupt) as error:
            report.update(
                status="unknown",
                continuity_checks_passed=False,
                error_type=type(error).__name__,
                stage="close",
            )
    return report


def observe():
    """Explicit five-second native notification observation, no service controls.

    Backend construction errors raise before observation; no silent simulation.
    Caller must preserve any returned unknown/partial report without retrying.
    """
    root = Path(__file__).resolve().parents[1]
    paths = (
        "cloudguard/systemd_receiver.py",
        "cloudguard/systemd_job.py",
        "cloudguard/__init__.py",
    )
    before = {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in paths
    }
    bus = _NativeBus()
    report = _observe(bus)
    report["source_sha256"] = before
    try:
        after = {
            name: hashlib.sha256((root / name).read_bytes()).hexdigest()
            for name in paths
        }
        report["source_sha256_after"] = after
        report["library_sha256_after"] = hashlib.sha256(
            LIBRARY.read_bytes()
        ).hexdigest()
        if (
            before != after
            or report["library_sha256_after"] != bus.metadata["library_sha256"]
        ):
            raise ValueError("receiver source or library changed")
    except (Exception, KeyboardInterrupt) as error:
        report.update(
            status="unknown",
            continuity_checks_passed=False,
            error_type=type(error).__name__,
            stage="source_postflight",
        )
    return report
