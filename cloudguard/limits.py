"""Selected finite byte/structure budgets, not a hostile-input sandbox."""

import io
import json
import math
from pathlib import Path

INPUT_BYTES = 1_000_000
RESPONSE_BYTES = 2_000_000
MAX_DEPTH = 64
MAX_NODES = 50_000


def read_bytes(path, limit=INPUT_BYTES):
    with Path(path).open("rb") as stream:
        return read_stream(stream, limit)


def read_stream(stream, limit=RESPONSE_BYTES):
    raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise ValueError("byte budget exceeded")
    return raw


def read_text(path, limit=INPUT_BYTES):
    # Match Path.read_text's UTF-8/universal-newline behavior on accepted files.
    with io.TextIOWrapper(
        io.BytesIO(read_bytes(path, limit)), encoding="utf-8"
    ) as stream:
        return stream.read()


def check_structure(value):
    pending = [(value, 0)]
    nodes = 0
    while pending:
        current, depth = pending.pop()
        nodes += 1
        if depth > MAX_DEPTH or nodes > MAX_NODES:
            raise ValueError("structure budget exceeded")
        if isinstance(current, dict):
            pending.extend((child, depth + 1) for child in current.values())
        elif isinstance(current, list):
            pending.extend((child, depth + 1) for child in current)
        elif isinstance(current, float) and not math.isfinite(current):
            raise ValueError("nonfinite numeric value")
    return value


def json_value(raw):
    text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
    # Bound nesting before the recursive stdlib decoder, ignoring quoted tokens.
    depth = 0
    quoted = escaped = False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in "[{":
            depth += 1
            if depth > MAX_DEPTH:
                raise ValueError("JSON nesting budget exceeded")
        elif char in "]}":
            depth -= 1

    def mapping(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    def constant(value):
        raise ValueError("nonfinite JSON constant")

    return check_structure(
        json.loads(text, object_pairs_hook=mapping, parse_constant=constant)
    )


def json_response(stream):
    return json_value(read_stream(stream))


def knowledge(path):
    raw = read_bytes(path)
    docs = json_value(raw)
    if not isinstance(docs, list) or not 1 <= len(docs) <= 256:
        raise ValueError("knowledge corpus count outside bounds")
    for doc in docs:
        if not isinstance(doc, dict) or any(
            not isinstance(doc.get(key), str) or not doc[key]
            for key in ("id", "title", "text", "url")
        ):
            raise ValueError("invalid knowledge source")
    if len({d["id"] for d in docs}) != len(docs):
        raise ValueError("duplicate knowledge source IDs")
    return raw, docs
