import pytest
from scripts.clock_bridge import bracket


def point(wall, mono):
    return dict(wall_ns=wall, monotonic_mid_ns=mono, sampling_span_ns=0)


@pytest.mark.parametrize(
    "remote,excluded", [(1_050_000, False), (900_000, True), (1_200_000, True)]
)
def test_bounds_without_symmetric_latency_assumption(remote, excluded):
    seconds, micros = divmod(remote, 1_000_000)
    result = bracket(
        point(10**9, 0), point(1_100_000_000, 100_000_000), f"{seconds}\n{micros}"
    )
    assert result["zero_within_bounds"] is not excluded
    assert result["offset_upper_ns"] - result["offset_lower_ns"] == 100_000_999


@pytest.mark.parametrize("reply", ["1", "1\n1000000", "-1\n0", "1\nx", "1\n0\n2"])
def test_bad_time_reply(reply):
    with pytest.raises(ValueError):
        bracket(point(10**9, 0), point(1_100_000_000, 100_000_000), reply)


@pytest.mark.parametrize(
    "wall,mono", [(1_300_000_000, 100_000_000), (2_000_000_000, 1_000_000_000)]
)
def test_unstable_or_wide_bracket(wall, mono):
    with pytest.raises(ValueError):
        bracket(point(10**9, 0), point(wall, mono), "1\n1000")
