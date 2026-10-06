"""Offline job-event contract; no D-Bus connection, service call or recovery authority."""

import re

UNIT = "systemd-timesyncd.service"


def epoch(value):
    if (
        not isinstance(value, dict)
        or set(value) != {"boot_sha256", "bus_id", "manager_owner"}
        or not isinstance(value["boot_sha256"], str)
        or not re.fullmatch("[0-9a-f]{64}", value["boot_sha256"])
        or not isinstance(value["bus_id"], str)
        or not re.fullmatch("[0-9a-f]{32}", value["bus_id"])
        or not isinstance(value["manager_owner"], str)
        or len(value["manager_owner"]) > 64
        or not re.fullmatch(r":[0-9]+\.[0-9]+", value["manager_owner"])
    ):
        raise ValueError("invalid job epoch")
    return dict(value)


def job_id(path):
    if not isinstance(path, str) or len(path) > 64:
        raise ValueError("invalid job path")
    matched = re.fullmatch(r"/org/freedesktop/systemd1/job/([1-9][0-9]*)", path)
    if not matched or not 0 < int(matched[1]) < 2**32:
        raise ValueError("invalid job identifier")
    return int(matched[1])


class JobEvidence:
    """Selected-unit decoded events only; caller facts are not authenticated.

    Subscribe/match acknowledgments must precede begin; buffer removal before
    reply to avoid dropping fast completion. Any evidence fault is sticky.
    """

    def __init__(self, identity, *, subscribed=False, matched=False):
        self.identity = epoch(identity)
        if subscribed is not True or matched is not True:
            raise ValueError("subscription and match must be acknowledged")
        self.started = False
        self.invalid = False
        self.reply_path = None
        self.events = {}

    def begin(self):
        if self.started:
            self.invalid = True
            raise ValueError("duplicate submission refused")
        self.started = True

    def reply(self, path):
        try:
            job_id(path)
            if not self.started or self.reply_path is not None:
                raise ValueError("unexpected job reply")
            self.reply_path = path
        except (Exception, KeyboardInterrupt):
            self.invalid = True
            raise

    def removed(self, value):
        try:
            if (
                not self.started
                or not isinstance(value, dict)
                or set(value) != {"sender", "job_id", "job_path", "unit", "result"}
            ):
                raise ValueError("invalid removal event")
            if (
                value["sender"] != self.identity["manager_owner"]
                or type(value["job_id"]) is not int
                or job_id(value["job_path"]) != value["job_id"]
                or not isinstance(value["unit"], str)
                or len(value["unit"]) > 256
                or not isinstance(value["result"], str)
                or not re.fullmatch("[a-z][a-z-]{0,31}", value["result"])
            ):
                raise ValueError("incompatible removal event")
            if value["unit"] != UNIT:
                return False
            if value["job_path"] in self.events or len(self.events) >= 32:
                raise ValueError("duplicate event or buffer limit")
            self.events[value["job_path"]] = dict(value)
            return True
        except (Exception, KeyboardInterrupt):
            self.invalid = True
            raise

    def disconnected(self):
        self.invalid = True

    def result(self, identity, *, continuous=True):
        try:
            if epoch(identity) != self.identity or continuous is not True:
                self.invalid = True
        except (Exception, KeyboardInterrupt):
            self.invalid = True
            raise
        event = self.events.get(self.reply_path)
        status = "unknown"
        if self.started and not self.invalid and self.reply_path is not None and event:
            status = (
                "tracked_job_done"
                if event["result"] == "done"
                else "job_not_successful"
            )
        return dict(
            status=status,
            tracked_job_done=status == "tracked_job_done",
            tracked_result=event["result"] if event and not self.invalid else None,
            native_binding_verified=False,
            service_quiesced_verified=False,
            may_disarm_recovery=False,
        )
