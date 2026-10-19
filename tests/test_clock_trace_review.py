import hashlib
import json

import pytest

from scripts import clock_trace_review as review


def check(text):
    raw = text.encode("ascii")
    return review.review_trace(raw, hashlib.sha256(raw).hexdigest())


def call(
    mode="ADJ_OFFSET|ADJ_NANO",
    result="0 (TIME_OK)",
    name="clock_adjtime",
    stamp="1791820584.566849",
):
    prefix = "CLOCK_REALTIME, " if name == "clock_adjtime" else ""
    return f"{stamp} {name}({prefix}{{modes={mode}, tick=10791, freq=-1763827}}) = {result} <0.000156>\n"


@pytest.mark.parametrize(
    "mode,kind",
    [
        ("0", "decoded_query_mode"),
        ("ADJ_OFFSET_SS_READ", "decoded_read_marker"),
        ("ADJ_OFFSET|ADJ_NANO", "decoded_nonquery_modes"),
        ("ADJ_TICK", "decoded_nonquery_modes"),
    ],
)
def test_modes_not_returned_tick_determine_only_decoded_category(mode, kind):
    result = check(call(mode))
    assert result["parsed_calls"] == 1
    assert result["rows"][0]["mode_observation"] == kind
    assert result["returned_timex_values_are_requests"] is False
    assert result["process_identity_verified"] is False
    assert result["cause_identified"] is False


@pytest.mark.parametrize(
    "value", ["ADJ_FUTURE", "ADJ_TICK|ADJ_TICK", "0|ADJ_TICK", "0x4000"]
)
def test_unknown_modes_do_not_become_writers_or_disappear(value):
    result = check(call(value))
    assert result["parsed_calls"] == 0 and result["uninterpreted_lines"] == 1


@pytest.mark.parametrize(
    "result", ["0 (TIME_OK)", "5 (TIME_ERROR)", "-1 EPERM (Operation not permitted)"]
)
def test_return_state_and_failure_not_stability(result):
    value = check(call(result=result))["rows"][0]
    assert value["status"] == "parsed"
    assert value["completion"] == (
        "failed" if result.startswith("-1") else "nonnegative_return_state"
    )


@pytest.mark.parametrize(
    "line",
    [
        "",
        "unrecognized private text\n",
        "1791820584.566849 clock_adjtime(CLOCK_REALTIME, <unfinished ...>\n",
        "[pid 7] 1791820584.566849 clock_adjtime(...) = 0 <0.001>\n",
    ],
)
def test_empty_unknown_and_unfinished_never_claim_completeness(line):
    result = check(line)
    assert result["trace_completeness_verified"] is False
    assert result["global_writer_coverage"] is False
    assert result["parsed_calls"] == 0
    assert "private text" not in json.dumps(result)


def test_backward_wall_timestamps_keep_original_line_order():
    result = check(call(stamp="200.000001") + call(stamp="100.000001", name="adjtimex"))
    assert result["parsed_calls"] == 2
    assert [row["line"] for row in result["rows"]] == [0, 1]


@pytest.mark.parametrize(
    "name,args",
    [("clock_settime", "CLOCK_REALTIME, NULL"), ("settimeofday", "NULL, NULL")],
)
def test_setter_name_with_null_args_not_proof_of_effect(name, args):
    result = check(f"1791820584.566849 {name}({args}) = 0 <0.000001>\n")
    assert result["rows"][0]["mode_observation"] == "setter_name_only"
    assert result["cause_identified"] is False


@pytest.mark.parametrize("fault", ["hash", "bytes", "lines", "width", "encoding"])
def test_budget_digest_and_encoding_refusals(fault):
    raw = (
        b"x" * (review.LIMIT + 1)
        if fault == "bytes"
        else b"\n" * 4097
        if fault == "lines"
        else b"x" * 4097
        if fault == "width"
        else b"\xff"
        if fault == "encoding"
        else b""
    )
    expected = "0" * 64 if fault == "hash" else hashlib.sha256(raw).hexdigest()
    with pytest.raises((ValueError, UnicodeError)):
        review.review_trace(raw, expected)


def test_cli_refuses_overwrite_and_suppresses_private_error(tmp_path, monkeypatch):
    target = tmp_path / "out.json"
    monkeypatch.setattr(
        review.sys,
        "argv",
        [
            "review",
            "--input",
            str(tmp_path / "private-missing"),
            "--expected-sha256",
            "0" * 64,
            "--output",
            str(target),
        ],
    )
    assert review.main() == 1
    original = target.read_bytes()
    assert b"private-missing" not in original
    with pytest.raises(FileExistsError):
        review.main()
    assert target.read_bytes() == original
