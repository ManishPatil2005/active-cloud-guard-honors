import io
from unittest.mock import Mock

import pytest

from cloudguard import limits


@pytest.mark.parametrize("limit", [-2, -1, 0, True, False, 1.5, None, "10", 8_000_001])
def test_invalid_budget_rejected_before_read(limit):
    stream = Mock()
    with pytest.raises(ValueError, match="invalid byte budget"):
        limits.read_stream(stream, limit)
    stream.read.assert_not_called()


@pytest.mark.parametrize("limit", [-2, 0, True, None])
def test_invalid_file_budget_rejected_before_open(limit):
    with pytest.raises(ValueError, match="invalid byte budget"):
        limits.read_bytes("absent-file", limit)


class ShortStream(io.BytesIO):
    def read(self, size=-1):
        return super().read(min(size, 2))


@pytest.mark.parametrize("stream_type", [io.BytesIO, ShortStream])
@pytest.mark.parametrize("raw", [b"", b"1234", b"12345"])
def test_exact_budget_and_eof(stream_type, raw):
    stream = stream_type(raw)
    if len(raw) > 4:
        with pytest.raises(ValueError, match="byte budget exceeded"):
            limits.read_stream(stream, 4)
    else:
        assert limits.read_stream(stream, 4) == raw


def test_short_response_does_not_accept_first_valid_json_prefix():
    with pytest.raises(ValueError):
        limits.json_response(ShortStream(b"{} trailing"))


@pytest.mark.parametrize("reply", [None, "abc", b"too long"])
def test_invalid_binary_stream_contract(reply):
    stream = Mock()
    stream.read.return_value = reply
    with pytest.raises(ValueError):
        limits.read_stream(stream, 4)
