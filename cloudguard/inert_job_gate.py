"""Durable supplied-job evidence under an inert guest gate; no native actions.

Trusted local storage/callers only. File fsync is not directory/power-loss
durability or authenticated evidence. Never bind these callbacks to services.
"""

from pathlib import Path

from cloudguard import guest_fence as fence
from cloudguard import systemd_job as jobs

PROTOCOL = "inert_durable_job_gate_v1"
BASE = {"request.json", "session.lock", "job-context.json"}
JOURNAL = {"job-intent.json", "job-reply.json", "window-complete.json", "fault.json"}
RECOVERY = {"sealed.json", "job-recovery-intent.json", "job-recovery.json"}
EVENTS = tuple(f"event-{index:02d}.json" for index in range(1, 33))


class _Writer:
    """Scope-bound supplied-evidence writer, used only while the gate owns lock."""

    def __init__(self, gate):
        self.gate = gate
        self.closed = False
        self.failed = False
        self.evidence = jobs.JobEvidence(gate.identity, subscribed=True, matched=True)
        self.evidence.begin()

    def _accept(self, action):
        if self.closed:
            raise ValueError("writer scope ended")
        if self.failed:
            raise ValueError("writer already invalid")
        try:
            return action()
        except BaseException:
            self.failed = True
            self.gate._poison()
            raise

    def reply(self, path):
        def action():
            self.evidence.reply(path)
            self.gate._record("job-reply.json", dict(path=path))

        self._accept(action)

    def removed(self, value):
        def action():
            if not self.evidence.removed(value):
                raise ValueError("only selected-unit evidence allowed")
            event = self.evidence.events[value["job_path"]]
            self.gate._record(EVENTS[len(self.evidence.events) - 1], dict(event))

        self._accept(action)

    def check_epoch(self, identity):
        def action():
            if jobs.epoch(identity) != self.gate.identity:
                raise ValueError("supplied epoch changed")

        self._accept(action)

    def disconnected(self):
        def action():
            raise ValueError("supplied receive continuity lost")

        self._accept(action)


class InertJobGate:
    """Inert simulations only; all native/quiescence/disarm authority is false.

    Reuses the existing guest lock/deadline/terminal seal, NOT its bare-True stop
    completion rule. Readiness/epochs/events are supplied declarations, not bus
    observations. A fresh exclusive session is mandatory; never clear a fault.
    """

    def __init__(self, directory, nonce, *, lock=None, clock=None):
        self.fence = fence.InertGuestFence(directory, nonce, lock=lock, clock=clock)
        self.directory = Path(directory)
        self.nonce = self.fence.nonce
        context = fence.read(self.directory / "job-context.json")
        if (
            not isinstance(context, dict)
            or set(context)
            != {"protocol", "mode", "nonce", "epoch", "unit", "deadline_ns"}
            or context["protocol"] != PROTOCOL
            or context["mode"] != "inert"
            or context["nonce"] != self.nonce
            or context["unit"] != jobs.UNIT
            or type(context["deadline_ns"]) is not int
            or context["deadline_ns"] != self.fence.deadline_ns
        ):
            raise ValueError("invalid inert job context")
        self.identity = jobs.epoch(context["epoch"])
        self.context = dict(context, epoch=dict(self.identity))
        self.failed = False

    @classmethod
    def initialize(
        cls, directory, nonce, identity, *, inert=False, lock=None, clock=None
    ):
        if inert is not True:
            raise ValueError("only explicit inert job sessions supported")
        identity = jobs.epoch(identity)
        session = fence.InertGuestFence.initialize(
            directory, nonce, inert=True, lock=lock, clock=clock
        )
        fence.exclusive(
            session.directory / "job-context.json",
            dict(
                protocol=PROTOCOL,
                mode="inert",
                nonce=session.nonce,
                epoch=identity,
                unit=jobs.UNIT,
                deadline_ns=session.deadline_ns,
            ),
        )
        return cls(directory, nonce, lock=lock, clock=clock)

    def _record(self, name, value):
        fence.exclusive(
            self.directory / name,
            dict(nonce=self.nonce, epoch=dict(self.identity), value=value),
        )

    def _poison(self):
        self.failed = True
        try:
            self._record("fault.json", dict(reason="evidence_or_storage_fault"))
        except BaseException:
            # Preserve original error; absent/partial window still denies success.
            # Failed storage cannot guarantee durable publication of this latch.
            pass

    def _value(self, name):
        path = self.directory / name
        if path.is_symlink() or not path.is_file():
            raise ValueError("journal record is not a regular local file")
        record = fence.read(path)
        if (
            not isinstance(record, dict)
            or set(record) != {"nonce", "epoch", "value"}
            or record["nonce"] != self.nonce
            or jobs.epoch(record["epoch"]) != self.identity
        ):
            raise ValueError("incompatible journal record")
        return record["value"]

    def _summary(self, status):
        return dict(
            protocol=PROTOCOL,
            mode="inert",
            status=status,
            simulated_job_done=status == "simulated_tracked_job_done",
            new_stop_requests_fenced=(self.directory / "sealed.json").exists(),
            operator_recovery_required=True,
            native_binding_verified=False,
            service_quiesced_verified=False,
            may_disarm_recovery=False,
        )

    def _replay(self, identity):
        if self.failed or (self.directory / "fault.json").exists():
            return self._summary("unknown")
        try:
            current = fence.InertGuestFence(
                self.directory, self.nonce, lock=self.fence.lock, clock=self.fence.clock
            )
            if (
                fence.read(self.directory / "job-context.json") != self.context
                or current.deadline_ns != self.context["deadline_ns"]
                or jobs.epoch(identity) != self.identity
            ):
                raise ValueError("request/context/epoch changed")
            names = set()
            for path in self.directory.iterdir():
                names.add(path.name)
                if len(names) > 42 or path.name not in BASE | JOURNAL | RECOVERY | set(
                    EVENTS
                ):
                    raise ValueError("unexpected journal entry")
            if "sealed.json" in names and fence.read(
                self.directory / "sealed.json"
            ) != dict(nonce=self.nonce):
                raise ValueError("incompatible terminal seal")
            if "job-recovery-intent.json" in names:
                if self._value("job-recovery-intent.json") != dict(
                    operation="simulated_recovery"
                ):
                    raise ValueError("invalid recovery intent")
            if "job-recovery.json" in names:
                value = self._value("job-recovery.json")
                if (
                    "sealed.json" not in names
                    or "job-recovery-intent.json" not in names
                    or not isinstance(value, dict)
                    or set(value)
                    != set(self._summary("unknown")) | {"simulated_recovery_observed"}
                    or value["protocol"] != PROTOCOL
                    or value["mode"] != "inert"
                    or value["status"]
                    not in {
                        "unknown",
                        "not_dispatched",
                        "simulated_tracked_job_done",
                        "simulated_job_not_successful",
                    }
                    or value["simulated_recovery_observed"] is not True
                    or value["new_stop_requests_fenced"] is not True
                    or value["operator_recovery_required"] is not True
                    or value["simulated_job_done"]
                    is not (value["status"] == "simulated_tracked_job_done")
                    or any(
                        value[key] is not False
                        for key in (
                            "native_binding_verified",
                            "service_quiesced_verified",
                            "may_disarm_recovery",
                        )
                    )
                ):
                    raise ValueError("invalid inert recovery record")
            artifacts = (JOURNAL - {"fault.json"}) | set(EVENTS)
            if "job-intent.json" not in names:
                if names & artifacts:
                    raise ValueError("orphan journal artifact")
                return self._summary("not_dispatched")
            if self._value("job-intent.json") != dict(operation="simulated_stop"):
                raise ValueError("incompatible job intent")
            evidence = jobs.JobEvidence(self.identity, subscribed=True, matched=True)
            evidence.begin()
            present = [name for name in EVENTS if name in names]
            if present != list(EVENTS[: len(present)]):
                raise ValueError("journal event sequence has a gap")
            for name in present:
                if not evidence.removed(self._value(name)):
                    raise ValueError("wrong selected unit")
            if "job-reply.json" in names:
                value = self._value("job-reply.json")
                if not isinstance(value, dict) or set(value) != {"path"}:
                    raise ValueError("invalid reply record")
                evidence.reply(value["path"])
            if "window-complete.json" not in names:
                return self._summary("unknown")
            value = self._value("window-complete.json")
            if (
                not isinstance(value, dict)
                or set(value) != {"continuous"}
                or value["continuous"] is not True
            ):
                raise ValueError("invalid window completion")
            status = evidence.result(identity)["status"]
            return self._summary(
                {
                    "tracked_job_done": "simulated_tracked_job_done",
                    "job_not_successful": "simulated_job_not_successful",
                    "unknown": "unknown",
                }[status]
            )
        except (Exception, KeyboardInterrupt):
            self._poison()
            return self._summary("unknown")

    def inspect(self, identity, *, timeout=5):
        """Locked replay; validation faults persist a sticky marker when possible."""
        with self.fence.lock(
            self.directory / "session.lock", fence.bounded_timeout(timeout)
        ):
            return self._replay(identity)

    def stop(self, simulate, identity, *, timeout=5):
        with self.fence.lock(
            self.directory / "session.lock", fence.bounded_timeout(timeout)
        ):
            if (self.directory / "sealed.json").exists():
                raise ValueError("session permanently sealed")
            if self._replay(identity)["status"] != "not_dispatched":
                raise ValueError("existing or invalid job intent refused")
            if self.fence.clock() >= self.fence.deadline_ns:
                raise TimeoutError("inert request expired")
            writer = _Writer(self)
            try:
                self._record("job-intent.json", dict(operation="simulated_stop"))
                if (self.directory / "sealed.json").exists():
                    raise ValueError("session sealed before inert dispatch")
                if simulate(writer) is not True or writer.failed:
                    raise ValueError("valid simulation acknowledgment required")
                self._record("window-complete.json", dict(continuous=True))
                return self._replay(identity)
            except BaseException:
                self._poison()
                raise
            finally:
                writer.closed = True

    def recover(self, simulate, identity, *, timeout=5):
        timeout = fence.bounded_timeout(timeout)
        try:
            fence.exclusive(self.directory / "sealed.json", dict(nonce=self.nonce))
        except FileExistsError:
            if fence.read(self.directory / "sealed.json") != dict(nonce=self.nonce):
                raise ValueError("invalid terminal seal") from None
        with self.fence.lock(self.directory / "session.lock", timeout):
            # Exclusive intent precedes simulation, so failure cannot repeat it.
            self._record(
                "job-recovery-intent.json", dict(operation="simulated_recovery")
            )
            value = self._replay(identity)
            if simulate() is not True:
                raise ValueError("inert recovery acknowledgment required")
            result = dict(value, simulated_recovery_observed=True)
            self._record("job-recovery.json", result)
            return result
