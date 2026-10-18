import copy
import json

import pytest

from cloudguard import kernel_clock_state as kernel
from scripts import (
    kernel_clock_diagnostic as diagnostic,
    kernel_domain_review as reviewer,
)
from test_kernel_clock_state import fixture, metadata


def receipt(block=0):
    packets = fixture()
    shift = block * 40_000_000_000
    for packet in packets:
        for side in ("before", "after"):
            for key in ("raw_before_ns", "raw_after_ns"):
                packet[side][key] += shift
        sample = packet["sample"]
        for key in (
            "raw_before_ns",
            "raw_after_ns",
            "mono_before_ns",
            "mono_after_ns",
            "boot_before_ns",
            "boot_after_ns",
            "realtime_ns",
        ):
            sample[key] += shift
    return dict(
        protocol=kernel.PROTOCOL,
        status="observed",
        planned_reads=16,
        spacing_seconds=1,
        clock_settings_modified=False,
        sensor_started=False,
        source_sha256={"fixture": "a" * 64},
        source_sha256_after={"fixture": "a" * 64},
        backend=metadata(),
        libc_sha256_after="a" * 64,
        packets=packets,
        summary=kernel.summarize(packets),
    )


def encoded(report):
    report["summary"] = kernel.summarize(report["packets"])
    return json.dumps(report).encode()


@pytest.fixture(autouse=True)
def offline_sources(monkeypatch):
    monkeypatch.setattr(diagnostic, "source_hashes", lambda: {"fixture": "a" * 64})

    def forbid(*args, **kwargs):
        pytest.fail("offline reviewer must never call native backend")

    monkeypatch.setattr(kernel, "native_backend", forbid)
    monkeypatch.setattr(diagnostic, "observe", forbid)


def test_single_block_preserves_old_receipt_and_accounts_domains():
    report = receipt()
    original = copy.deepcopy(report)
    output = reviewer.review_batch([encoded(report)])
    assert report == original
    assert output["samples"] == 16 and output["live_actions_executed"] == []
    last = output["rows"][-1]
    assert last["from_first"]["raw_minus_mono"] == dict(
        lower_ns=14984, upper_ns=15016, includes_zero=False
    )
    assert last["from_previous"]["raw_minus_mono"] == dict(
        lower_ns=984, upper_ns=1016, includes_zero=False
    )
    for key in ("wall_minus_mono", "wall_minus_boot", "boot_minus_mono"):
        assert last["from_first"][key]["includes_zero"] is True
    assert output["causal_attribution"] == "not_proven"
    assert output["step_vs_slew_identified"] is False


def test_wall_shift_is_localized_without_attributing_writer():
    report = receipt()
    for packet in report["packets"][8:]:
        for key in ("realtime_ns", "offset_lower_ns", "offset_upper_ns"):
            packet["sample"][key] += 60_000_000
    rows = reviewer.review_batch([encoded(report)])["rows"]
    assert rows[8]["from_previous"]["wall_minus_mono"]["lower_ns"] > 59_000_000
    assert rows[8]["from_previous"]["wall_minus_boot"]["lower_ns"] > 59_000_000
    assert rows[8]["from_previous"]["boot_minus_mono"]["includes_zero"] is True
    assert rows[9]["from_previous"]["wall_minus_mono"]["includes_zero"] is True


def test_four_blocks_have_cross_boundary_accounting():
    output = reviewer.review_batch([encoded(receipt(i)) for i in range(4)])
    assert output["samples"] == 64 and output["blocks"] == 4
    assert output["rows"][16]["from_previous"] is not None


@pytest.mark.parametrize("shift", [-60_000_000, 60_000_000])
def test_monotonic_shift_does_not_get_misattributed_to_wall_boot(shift):
    report = receipt()
    for packet in report["packets"][8:]:
        packet["sample"]["mono_before_ns"] += shift
        packet["sample"]["mono_after_ns"] += shift
    result = reviewer.review_batch([encoded(report)])
    changes = result["rows"][8]["from_previous"]
    assert changes["wall_minus_boot"]["includes_zero"] is True
    for name in ("wall_minus_mono", "boot_minus_mono", "raw_minus_mono"):
        assert changes[name]["includes_zero"] is False
        expected = -shift + (1000 if name == "raw_minus_mono" else 0)
        assert changes[name]["lower_ns"] <= expected <= changes[name]["upper_ns"]
    assert result["causal_attribution"] == "not_proven"


@pytest.mark.parametrize(
    "bad",
    [b"{}" * 50_001, b'{"x":1,"x":2}', "not bytes"],
    ids=["over-budget", "duplicate-key", "non-bytes"],
)
def test_existing_receipt_size_and_strict_json_bounds_remain(bad):
    with pytest.raises(ValueError):
        reviewer.review_batch([bad])


@pytest.mark.parametrize(
    "fault", ["domain", "order", "backend", "source", "summary", "partial"]
)
def test_batch_refuses_invalid_or_discontinuous_evidence(fault):
    values = [receipt(i) for i in range(4)]
    last = values[-1]
    if fault == "domain":
        for p in last["packets"]:
            p["domain"]["kernel_boot_sha256"] = "f" * 64
    elif fault == "order":
        values[-1] = receipt(0)
    elif fault == "backend":
        last["backend"]["libc_sha256"] = last["libc_sha256_after"] = "b" * 64
    elif fault == "source":
        last["source_sha256"] = {"fixture": "f" * 64}
    elif fault == "summary":
        last["summary"]["state_read_count"] = 32.0
    else:
        last["status"] = "failed"
    with pytest.raises(ValueError):
        reviewer.review_batch([json.dumps(value).encode() for value in values])


@pytest.mark.parametrize("count", [0, 2, 3, 5])
def test_only_declared_fixed_batch_sizes(count):
    with pytest.raises(ValueError):
        reviewer.review_batch([encoded(receipt())] * count)


def test_cli_exclusive_and_failure_contains_no_private_message(tmp_path, monkeypatch):
    output = tmp_path / "result.json"
    absent = tmp_path / "private-path-do-not-publish"
    monkeypatch.setattr(
        reviewer.sys,
        "argv",
        ["review", "--input", str(absent), "--output", str(output)],
    )
    assert reviewer.main() == 1
    before = output.read_bytes()
    assert b"private-path" not in before
    with pytest.raises(FileExistsError):
        reviewer.main()
    assert output.read_bytes() == before
