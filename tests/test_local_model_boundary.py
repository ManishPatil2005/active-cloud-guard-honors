import io
import json
from unittest.mock import patch
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler
from urllib.request import Request
from urllib.request import HTTPHandler, build_opener
from urllib.error import HTTPError
from urllib.response import addinfourl
from email.message import Message

import pytest

from cloudguard import llm, vector

SOURCES = [
    dict(
        id="s", title="source", text="synthetic evidence", url="https://example.invalid"
    )
]


@pytest.mark.parametrize("operation", ["audit", "identity"])
def test_port_cannot_change_request_authority(operation):
    with patch.object(llm, "build_opener") as opener:
        opener.return_value.open.return_value = io.BytesIO(
            json.dumps(
                {
                    "models": [{"name": "model:latest", "digest": "test"}],
                    "message": {"content": '{"findings":[]}'},
                }
            ).encode()
        )
        with pytest.raises(ValueError):
            if operation == "audit":
                llm.audit(
                    "services: {a: {image: redis}}",
                    SOURCES,
                    "model",
                    port="11434@example.invalid",
                )
            else:
                llm.model_identity("model", "11434@example.invalid")
    opener.assert_not_called()


def test_identity_opener_does_not_allow_default_redirects():
    with patch.object(llm, "build_opener") as opener:
        opener.return_value.open.return_value = io.BytesIO(
            b'{"models":[{"name":"model:latest","digest":"test"}]}'
        )
        llm.model_identity("model", 11434)
    handlers = opener.call_args.args
    assert any(
        isinstance(h, HTTPRedirectHandler) and type(h) is not HTTPRedirectHandler
        for h in handlers
    )


@pytest.mark.parametrize(
    "port", [True, False, 0, -1, 65536, 11434.0, None, "11434", "11434@example.invalid"]
)
@pytest.mark.parametrize("operation", ["audit", "identity"])
def test_invalid_ports_fail_before_network(port, operation):
    with patch.object(llm, "build_opener") as opener:
        with pytest.raises(ValueError):
            if operation == "audit":
                llm.audit("services: {a: {image: redis}}", SOURCES, "model", port=port)
            else:
                llm.model_identity("model", port)
    opener.assert_not_called()


@pytest.mark.parametrize("code", [301, 302, 303, 307, 308])
@pytest.mark.parametrize(
    "destination", ["http://example.invalid/foreign", "http://127.0.0.1:9999/foreign"]
)
def test_redirect_handler_refuses_every_destination(code, destination):
    request = Request("http://127.0.0.1:11434/api/chat", data=b"synthetic")
    with pytest.raises(HTTPError) as caught:
        llm.LocalOnlyRedirect().redirect_request(
            request, None, code, "redirect", {}, destination
        )
    assert caught.value.code == code
    assert destination not in str(caught.value)


def test_embedding_uses_fixed_url_no_proxy_and_no_redirects():
    with patch.object(vector, "build_opener") as opener:
        opener.return_value.open.return_value = io.BytesIO(b'{"embeddings":[[1,2]]}')
        assert vector.embed(["synthetic"]) == [[1, 2]]
        request = opener.return_value.open.call_args.args[0]
    assert urlsplit(request.full_url).hostname == "127.0.0.1"
    assert any(isinstance(h, llm.LocalOnlyRedirect) for h in opener.call_args.args)
    assert any(
        isinstance(h, ProxyHandler) and h.proxies == {} for h in opener.call_args.args
    )


def test_chat_uses_fixed_url_and_no_redirects():
    with patch.object(llm, "build_opener") as opener:
        opener.return_value.open.return_value = io.BytesIO(
            b'{"message":{"content":"{\\"findings\\":[]}"}}'
        )
        result = llm.audit("services: {a: {image: redis}}", SOURCES, "model")
        request = opener.return_value.open.call_args.args[0]
    assert result["output"] == {"findings": []}
    assert urlsplit(request.full_url).hostname == "127.0.0.1"
    assert any(isinstance(h, llm.LocalOnlyRedirect) for h in opener.call_args.args)


@pytest.mark.parametrize("code", [301, 302, 303, 307, 308])
def test_real_opener_refuses_redirect_without_second_request(code):
    calls = []

    class SyntheticHTTP(HTTPHandler):
        def http_open(self, request):
            calls.append(request.full_url)
            headers = Message()
            headers["Location"] = "http://example.invalid/redirected"
            response = addinfourl(io.BytesIO(b""), headers, request.full_url, code)
            response.msg = "synthetic redirect"
            return response

    opener = build_opener(ProxyHandler({}), SyntheticHTTP(), llm.LocalOnlyRedirect())
    with pytest.raises(HTTPError):
        opener.open("http://127.0.0.1:11434/api/tags")
    assert calls == ["http://127.0.0.1:11434/api/tags"]
