import pytest

from cloudguard import systemd_job as jobs

IDENTITY = dict(boot_sha256="a" * 64, bus_id="b" * 32, manager_owner=":1.5")
PATH = "/org/freedesktop/systemd1/job/42"


def tracker():
    t = jobs.JobEvidence(IDENTITY, subscribed=True, matched=True)
    t.begin()
    return t


def event(result="done", path=PATH):
    return dict(
        sender=":1.5",
        job_id=jobs.job_id(path),
        job_path=path,
        unit=jobs.UNIT,
        result=result,
    )


@pytest.mark.parametrize("before_reply", [False, True])
def test_completion_before_or_after_reply_does_not_grant_recovery_authority(
    before_reply,
):
    t = tracker()
    if before_reply:
        t.removed(event())
    t.reply(PATH)
    if not before_reply:
        t.removed(event())
    value = t.result(IDENTITY)
    assert value["tracked_job_done"]
    assert not value["may_disarm_recovery"]
    assert (
        not value["service_quiesced_verified"] and not value["native_binding_verified"]
    )


@pytest.mark.parametrize(
    "result",
    [
        "canceled",
        "timeout",
        "failed",
        "dependency",
        "skipped",
        "collected",
        "future-result",
    ],
)
def test_other_results_never_mean_success_or_safe_cancellation(result):
    t = tracker()
    t.reply(PATH)
    t.removed(event(result))
    assert t.result(IDENTITY)["status"] == "job_not_successful"


@pytest.mark.parametrize(
    "mode", ["lost_reply", "missing_event", "unrelated_job", "other_unit"]
)
def test_incomplete_or_unbound_completion_is_unknown(mode):
    t = tracker()
    if mode != "lost_reply":
        t.reply(PATH)
    if mode != "missing_event":
        e = event(
            path=PATH if mode != "unrelated_job" else "/org/freedesktop/systemd1/job/43"
        )
        if mode == "other_unit":
            e["unit"] = "other.service"
        t.removed(e)
    assert t.result(IDENTITY)["status"] == "unknown"


@pytest.mark.parametrize("field", ["boot_sha256", "bus_id", "manager_owner"])
def test_epoch_change_sticky_even_if_original_returns(field):
    t = tracker()
    t.reply(PATH)
    t.removed(event())
    changed = dict(IDENTITY)
    changed[field] = {
        "boot_sha256": "c" * 64,
        "bus_id": "d" * 32,
        "manager_owner": ":1.6",
    }[field]
    assert t.result(changed)["status"] == "unknown"
    assert t.result(IDENTITY)["status"] == "unknown"


@pytest.mark.parametrize(
    "subscribed,matched", [(False, True), (True, False), (1, True), (True, 1)]
)
def test_pre_submission_readiness_requires_exact_acknowledgments(subscribed, matched):
    with pytest.raises(ValueError):
        jobs.JobEvidence(IDENTITY, subscribed=subscribed, matched=matched)


@pytest.mark.parametrize(
    "field,value",
    [
        ("sender", ":1.8"),
        ("job_id", True),
        ("job_id", 43),
        ("job_path", "private text"),
        ("result", "DONE"),
        ("extra", "private text"),
    ],
)
def test_invalid_evidence_poison_cannot_be_ignored_then_accepted(field, value):
    t = tracker()
    t.reply(PATH)
    e = event()
    e[field] = value
    with pytest.raises(ValueError):
        t.removed(e)
    t.removed(event())
    assert t.result(IDENTITY)["status"] == "unknown"


def test_disconnect_duplicate_and_overflow_sticky():
    t = tracker()
    t.reply(PATH)
    t.removed(event())
    t.disconnected()
    assert t.result(IDENTITY)["status"] == "unknown"
    with pytest.raises(ValueError):
        t.removed(event())
    t = tracker()
    for i in range(1, 33):
        t.removed(event(path=f"/org/freedesktop/systemd1/job/{i}"))
    with pytest.raises(ValueError):
        t.removed(event())
    t.reply("/org/freedesktop/systemd1/job/1")
    assert t.result(IDENTITY)["status"] == "unknown"


def test_source_dicts_detached_and_continuity_failure_sticky():
    identity = dict(IDENTITY)
    t = jobs.JobEvidence(identity, subscribed=True, matched=True)
    identity["bus_id"] = "c" * 32
    t.begin()
    e = event()
    t.removed(e)
    e["result"] = "failed"
    t.reply(PATH)
    assert t.result(IDENTITY)["tracked_job_done"]
    assert t.result(IDENTITY, continuous=False)["status"] == "unknown"
    assert t.result(IDENTITY)["status"] == "unknown"


def test_no_submission_or_duplicate_reply_or_begin_proves_nothing():
    t = jobs.JobEvidence(IDENTITY, subscribed=True, matched=True)
    assert t.result(IDENTITY)["status"] == "unknown"
    with pytest.raises(ValueError):
        t.reply(PATH)
    t = tracker()
    t.reply(PATH)
    with pytest.raises(ValueError):
        t.reply(PATH)
    with pytest.raises(ValueError):
        t.begin()
    t.removed(event())
    assert t.result(IDENTITY)["status"] == "unknown"
