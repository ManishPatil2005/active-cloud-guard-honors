"""Cooperative legacy batch input/deadline guards; not hard filesystem isolation."""

import hashlib
import io
import math
from pathlib import Path
import time
import xml.etree.ElementTree as ET

from .limits import json_value, MAX_DEPTH, MAX_NODES


class InputBudget:
    def __init__(self, *, total=8_000_000, files=256, seconds=600):
        if (
            type(total) is not int
            or not 1 <= total <= 32_000_000
            or type(files) is not int
            or not 1 <= files <= 4096
        ):
            raise ValueError("invalid legacy input budget")
        if (
            type(seconds) not in (int, float)
            or not math.isfinite(seconds)
            or not 0 < seconds <= 600
        ):
            raise ValueError("invalid legacy batch deadline")
        self.remaining = total
        self.files = files
        self.deadline = time.monotonic() + seconds

    def check(self):
        if time.monotonic() >= self.deadline:
            raise ValueError("legacy batch deadline exceeded")

    def timeout(self, maximum=180):
        if (
            type(maximum) not in (int, float)
            or not math.isfinite(maximum)
            or not 0 < maximum <= 180
        ):
            raise ValueError("invalid legacy process timeout")
        self.check()
        return min(maximum, self.deadline - time.monotonic())

    def bytes(self, path, limit=1_000_000):
        if type(limit) is not int or not 1 <= limit <= 8_000_000:
            raise ValueError("invalid legacy file limit")
        self.check()
        if self.files <= 0:
            raise ValueError("legacy input file count exceeded")
        self.files -= 1
        cap = min(limit, self.remaining)
        with Path(path).open("rb") as stream:
            raw = stream.read(cap + 1)
        if len(raw) > cap:
            raise ValueError("legacy byte budget exceeded")
        self.remaining -= len(raw)
        self.check()
        return raw

    def text(self, path, limit=1_000_000):
        with io.TextIOWrapper(
            io.BytesIO(self.bytes(path, limit)), encoding="utf-8"
        ) as stream:
            return stream.read()

    def json(self, path, limit=1_000_000):
        return json_value(self.bytes(path, limit))

    def digest(self, path, limit=8_000_000):
        if type(limit) is not int or not 1 <= limit <= 8_000_000:
            raise ValueError("invalid legacy hash limit")
        self.check()
        if self.files <= 0:
            raise ValueError("legacy input file count exceeded")
        self.files -= 1
        cap = min(limit, self.remaining)
        size = 0
        digest = hashlib.sha256()
        with Path(path).open("rb") as stream:
            while True:
                self.check()
                chunk = stream.read(min(65536, cap - size + 1))
                if not chunk:
                    break
                size += len(chunk)
                if size > cap:
                    raise ValueError("legacy hash byte budget exceeded")
                digest.update(chunk)
        self.remaining -= size
        return digest.hexdigest()

    def xml(self, path):
        text = self.bytes(path, 2_000_000).decode("utf-8")
        if "<!DOCTYPE" in text.upper() or "<!ENTITY" in text.upper():
            raise ValueError("XML declarations unsupported")
        root = ET.fromstring(text)
        pending = [(root, 0)]
        count = 0
        while pending:
            element, depth = pending.pop()
            count += 1
            if count > MAX_NODES or depth > MAX_DEPTH:
                raise ValueError("XML structure budget exceeded")
            pending.extend((child, depth + 1) for child in element)
        return root
