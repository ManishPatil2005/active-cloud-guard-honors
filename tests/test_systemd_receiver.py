import ctypes as C
from types import SimpleNamespace

import pytest

from cloudguard import systemd_receiver as receiver
from cloudguard import systemd_job as jobs

IDENTITY = dict(boot_sha256="a" * 64, bus_id="b" * 32, manager_owner=":1.5")
PATH = "/org/freedesktop/systemd1/job/42"


class FakeBus:
    metadata = {"test_double": True}

    def __init__(self, fault=None):
        self.fault = fault
        self.time = 0
        self.calls = []
        self.identities = 0
        self.state = None

    def identity(self):
        self.identities += 1
        self.calls.append("identity")
        if self.fault == "identity_error":
            raise OSError("private exception text must not be saved")
        value = dict(IDENTITY)
        if self.fault == "setup_epoch" and self.identities == 2:
            value["manager_owner"] = ":1.6"
        if self.fault == "final_epoch" and self.identities == 3:
            value["bus_id"] = "c" * 32
        return value

    def install(self, identity, state):
        self.calls.append("install")
        self.state = state
        if self.fault == "match":
            raise OSError()

    def subscribe(self, owner):
        self.calls.append("subscribe")
        if self.fault == "subscribe":
            raise OSError()

    def ready(self):
        return self.fault != "not_ready"

    def process(self):
        self.calls.append("process")
        if self.fault == "interrupt":
            raise KeyboardInterrupt()
        if self.fault == "disconnect":
            self.state.disconnected(None, [])
        if self.fault == "owner_change":
            self.state.owner_changed(receiver.DBUS, [receiver.MANAGER, ":1.5", ":1.6"])
        if self.fault == "event":
            self.state.removed(":1.5", [42, PATH, jobs.UNIT, "done"])
            self.fault = None
        return 1 if self.fault == "flood" else 0

    def wait(self, usec):
        self.calls.append("wait")
        assert 0 <= usec <= 100_000
        if self.fault == "wait":
            raise OSError()
        self.time += usec / 1_000_000 + 0.001

    def unsubscribe(self, owner):
        self.calls.append("unsubscribe")
        if self.fault == "unsubscribe":
            raise OSError()
        if self.fault == "unsubscribe_fault":
            self.state.invalid = True

    def close(self):
        self.calls.append("close")
        if self.fault == "close":
            raise OSError()


@pytest.mark.parametrize("event", [False, True])
def test_finite_observation_orders_subscription_and_never_grants_job_authority(event):
    bus = FakeBus("event" if event else None)
    report = receiver._observe(bus, now=lambda: bus.time)
    assert report["status"] == "observed"
    assert report["continuity_checks_passed"] and report["connection_closed"]
    assert report["subscription_released"]
    assert bus.calls[:4] == ["identity", "install", "subscribe", "identity"]
    assert bus.calls[-3:] == ["identity", "unsubscribe", "close"]
    assert 5 <= bus.time < 5.2 and report["process_calls"] < 512
    assert len(report["events"]) == int(event)
    for key in (
        "jobs_submitted_or_canceled",
        "services_modified",
        "native_binding_verified",
        "service_quiesced_verified",
        "may_disarm_recovery",
    ):
        assert report[key] is False


@pytest.mark.parametrize(
    "fault",
    [
        "identity_error",
        "match",
        "subscribe",
        "setup_epoch",
        "final_epoch",
        "not_ready",
        "interrupt",
        "disconnect",
        "owner_change",
        "flood",
        "wait",
        "unsubscribe",
        "unsubscribe_fault",
        "close",
    ],
)
def test_faults_are_unknown_no_retry_and_connection_cleanup_attempted(fault):
    bus = FakeBus(fault)
    report = receiver._observe(bus, now=lambda: bus.time)
    assert report["status"] == "unknown" and not report["continuity_checks_passed"]
    assert bus.calls[-1] == "close" and bus.calls.count("subscribe") <= 1
    assert "private exception" not in str(report)
    assert not report["may_disarm_recovery"]
    if fault == "flood":
        assert report["process_calls"] == 512


@pytest.mark.parametrize(
    "values",
    [
        [True, PATH, jobs.UNIT, "done"],
        [43, PATH, jobs.UNIT, "done"],
        [42, PATH, "other.service", "done"],
        [42, PATH, jobs.UNIT, "DONE"],
        [42, PATH, jobs.UNIT],
    ],
)
def test_selected_malformed_events_poison_state(values):
    state = receiver._ReceiveState(IDENTITY)
    with pytest.raises((ValueError, TypeError)):
        state.removed(":1.5", values)
    assert state.invalid


def test_event_copy_replay_and_buffer_bound():
    state = receiver._ReceiveState(IDENTITY)
    values = [42, PATH, jobs.UNIT, "done"]
    state.removed(":1.5", values)
    values[-1] = "failed"
    assert state.events[PATH]["result"] == "done"
    with pytest.raises(ValueError):
        state.removed(":1.5", [42, PATH, jobs.UNIT, "done"])
    assert state.invalid
    state = receiver._ReceiveState(IDENTITY)
    for identifier in range(1, 33):
        state.removed(
            ":1.5",
            [identifier, PATH.rsplit("/", 1)[0] + f"/{identifier}", jobs.UNIT, "done"],
        )
    with pytest.raises(ValueError):
        state.removed(":1.5", [42, PATH, jobs.UNIT, "done"])
    assert state.invalid and len(state.events) == 32


@pytest.mark.parametrize("raw", [None, b"x" * 257, b"\xff"])
def test_native_strings_strict(raw):
    with pytest.raises((ValueError, UnicodeError)):
        receiver._text(raw)


def test_native_errno_is_not_success():
    with pytest.raises(OSError) as error:
        receiver._check(-5)
    assert error.value.errno == 5
    assert receiver._check(0) == 0


class MessageLib:
    """C-level fixture, no native library or D-Bus connection."""

    def __init__(self, fault=None):
        self.fault = fault
        self.member = None
        self.destination = None
        self.unrefs = []
        self.appended = []
        self.signature = b"s"
        self.values = [b"b" * 32]
        self.type = 2
        self.sender = receiver.DBUS.encode()
        self.headers = [
            receiver.DBUS_PATH.encode(),
            receiver.DBUS.encode(),
            b"NameOwnerChanged",
        ]

    def sd_bus_message_new_method_call(
        self, bus, request, dest, path, interface, member
    ):
        self.member, self.destination = member, dest
        C.cast(request, receiver.PP)[0] = receiver.P(100)
        return 0

    def sd_bus_message_set_auto_start(self, request, flag):
        assert flag == 0
        return 0

    def sd_bus_message_append_basic(self, message, kind, pointer):
        assert kind == b"s"
        self.appended.append(C.cast(pointer, C.c_char_p).value)
        return 0

    def sd_bus_call(self, bus, request, timeout, error, reply):
        assert timeout == 1_000_000 and error is None
        C.cast(reply, receiver.PP)[0] = receiver.P(200)
        return -5 if self.fault == "call" else 1

    def sd_bus_message_get_cookie(self, message, pointer):
        C.cast(pointer, C.POINTER(C.c_uint64))[0] = (
            0 if self.fault == "zero_cookie" else 9
        )
        return 0

    def sd_bus_message_get_reply_cookie(self, message, pointer):
        C.cast(pointer, C.POINTER(C.c_uint64))[0] = 10 if self.fault == "cookie" else 9
        return 0

    def sd_bus_message_get_type(self, message, pointer):
        C.cast(pointer, C.POINTER(C.c_uint8))[0] = (
            3 if self.fault == "type" else self.type
        )
        return 0

    def sd_bus_message_get_sender(self, message):
        return b":1.9" if self.fault == "sender" else self.sender

    def sd_bus_message_get_signature(self, message, complete):
        assert complete == 1
        return b"u" if self.fault == "signature" else self.signature

    def sd_bus_message_read_basic(self, message, kind, pointer):
        value = self.values.pop(0)
        native_type = C.c_uint32 if kind == b"u" else C.c_char_p
        C.cast(pointer, C.POINTER(native_type))[0] = value
        return 0 if self.fault == "missing_basic" else 1

    def sd_bus_message_at_end(self, message, complete):
        return 0 if self.fault == "trailing" else 1

    def sd_bus_message_unref(self, message):
        self.unrefs.append(message.value)

    def sd_bus_message_get_path(self, message):
        return self.headers[0]

    def sd_bus_message_get_interface(self, message):
        return self.headers[1]

    def sd_bus_message_get_member(self, message):
        return self.headers[2]

    def sd_bus_add_match(self, bus, slot, rule, handler, userdata):
        self.handler = handler
        C.cast(slot, receiver.PP)[0] = receiver.P(300)
        return 0


def fake_native(lib):
    bus = receiver._NativeBus.__new__(receiver._NativeBus)
    bus.lib, bus.bus = lib, receiver.P(1)
    bus.fault, bus.slots, bus.callbacks = False, [], []
    return bus


@pytest.mark.parametrize(
    "fault",
    [
        None,
        "call",
        "zero_cookie",
        "cookie",
        "type",
        "sender",
        "signature",
        "missing_basic",
        "trailing",
    ],
)
def test_typed_reply_checks_and_owned_message_release(fault):
    lib = MessageLib(fault)
    bus = fake_native(lib)
    if fault:
        with pytest.raises((ValueError, OSError)):
            bus._call("GetId")
    else:
        assert bus._call("GetId") == "b" * 32
    assert lib.unrefs == [200, 100]


def test_string_append_uses_char_array_not_pointer_to_pointer():
    lib = MessageLib()
    lib.values = [b":1.5"]
    assert fake_native(lib)._call("GetNameOwner") == ":1.5"
    assert lib.appended == [receiver.MANAGER.encode()]


@pytest.mark.parametrize(
    "method", ["StopUnit", "StartUnit", "CancelJob", "SetTime", "Reload"]
)
def test_service_methods_refused_before_any_native_call(method):
    lib = MessageLib()
    with pytest.raises(ValueError):
        fake_native(lib)._call(method)
    assert lib.member is None


@pytest.mark.parametrize(
    "fault", [None, "header", "signature", "callback", "interrupt", "trailing"]
)
def test_callback_catches_errors_copies_values_and_does_not_unref_borrowed_message(
    fault,
):
    lib = MessageLib(
        "signature"
        if fault == "signature"
        else "trailing"
        if fault == "trailing"
        else None
    )
    lib.type, lib.signature, lib.values = (
        4,
        b"sss",
        [receiver.MANAGER.encode(), b":1.5", b":1.6"],
    )
    if fault == "header":
        lib.headers[2] = b"Unexpected"
    seen = []

    def consumer(sender, values):
        if fault == "callback":
            raise ValueError()
        if fault == "interrupt":
            raise KeyboardInterrupt()
        seen.append((sender, values))

    bus = fake_native(lib)
    bus._match(
        "fixed-test-rule",
        (receiver.DBUS, receiver.DBUS_PATH, receiver.DBUS, "NameOwnerChanged"),
        "sss",
        consumer,
    )
    assert lib.handler(receiver.P(400), None, None) == 1
    assert bus.fault == bool(fault)
    assert not lib.unrefs and len(bus.callbacks) == len(bus.slots) == 1
    if not fault:
        assert seen[0][1] == [receiver.MANAGER, ":1.5", ":1.6"]


def test_nonreviewed_backend_refused_before_loader(monkeypatch):
    monkeypatch.setattr(receiver.sys, "platform", "win32")
    monkeypatch.setattr(receiver.C, "CDLL", lambda *args: pytest.fail("loader called"))
    with pytest.raises(RuntimeError):
        receiver._NativeBus()


def test_bound_api_is_nonvariadic_and_has_exact_basic_pointer_types():
    class FakeLibrary:
        def __getattr__(self, name):
            value = SimpleNamespace()
            setattr(self, name, value)
            return value

    lib = receiver._bind(FakeLibrary())
    assert lib.sd_bus_message_append_basic.argtypes == [
        receiver.P,
        C.c_char,
        receiver.P,
    ]
    assert lib.sd_bus_message_read_basic.argtypes == [receiver.P, C.c_char, receiver.P]
    assert lib.sd_bus_call.argtypes[-1] == receiver.PP
    assert "sd_bus_call_method" not in vars(lib)


@pytest.mark.parametrize("failure", [None, "address", "start"])
def test_constructor_fixed_address_no_interactive_auth_and_cleanup_on_failure(
    monkeypatch, failure
):
    calls = []

    class SetupLib:
        def __getattr__(self, name):
            def function(*args):
                calls.append((name, args))
                if name == "sd_bus_new":
                    C.cast(args[0], receiver.PP)[0] = receiver.P(1)
                if name == f"sd_bus_set_{failure}" or name == f"sd_bus_{failure}":
                    return -5
                return 0

            return function

    lib = SetupLib()
    monkeypatch.setattr(receiver, "_backend", lambda: {"library_path": "test-only"})
    monkeypatch.setattr(receiver, "_bind", lambda value: value)
    monkeypatch.setattr(receiver.C, "CDLL", lambda path: lib)
    if failure:
        with pytest.raises(OSError):
            receiver._NativeBus()
        assert calls[-1][0] == "sd_bus_close_unref"
    else:
        bus = receiver._NativeBus()
        values = {name: args[1] for name, args in calls if len(args) == 2}
        assert values["sd_bus_set_address"] == b"unix:path=/run/dbus/system_bus_socket"
        assert values["sd_bus_set_bus_client"] == 1
        assert values["sd_bus_set_allow_interactive_authorization"] == 0
        assert values["sd_bus_set_exit_on_disconnect"] == 0
        assert values["sd_bus_set_method_call_timeout"] == 1_000_000
        bus.close()


def test_real_backend_guard_rejects_root_and_library_change_without_loading(
    monkeypatch,
):
    monkeypatch.setattr(receiver.sys, "platform", "linux")
    monkeypatch.setattr(receiver.platform, "machine", lambda: "x86_64")
    monkeypatch.setattr(receiver.platform, "libc_ver", lambda: ("glibc", "2.39"))
    native_sizeof = receiver.C.sizeof
    monkeypatch.setattr(
        receiver.C,
        "sizeof",
        lambda kind: 8 if kind is C.c_long else native_sizeof(kind),
    )
    monkeypatch.setattr(receiver.os, "geteuid", lambda: 0, raising=False)
    with pytest.raises(RuntimeError):
        receiver._backend()
    monkeypatch.setattr(receiver.os, "geteuid", lambda: 1000)
    monkeypatch.setattr(
        receiver,
        "SOCKET",
        SimpleNamespace(stat=lambda: SimpleNamespace(st_mode=0o140000)),
    )
    # A real file is unnecessary: this fixture models changed installed bytes.
    monkeypatch.setattr(
        receiver, "LIBRARY", SimpleNamespace(read_bytes=lambda: b"changed-library")
    )
    with pytest.raises(RuntimeError, match="fresh review"):
        receiver._backend()


def test_observe_does_not_silently_fall_back_on_backend_error(monkeypatch):
    def backend():
        raise RuntimeError("unsupported")

    monkeypatch.setattr(receiver, "_NativeBus", backend)
    with pytest.raises(RuntimeError):
        receiver.observe()
