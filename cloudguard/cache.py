"""Bounded, opt-in local cache. Stores model responses, never live probes."""

import hashlib
import json
import os
import stat
from pathlib import Path
import tempfile
import threading
import time
from .limits import read_stream, json_value

MAX_BYTES = 2_000_000


def fingerprint(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


class AuditCache:
    def __init__(self, directory, ttl=3600, max_entries=128):
        if (
            type(ttl) not in (int, float)
            or not 0 < ttl <= 86400
            or type(max_entries) is not int
            or not 1 <= max_entries <= 1024
        ):
            raise ValueError("cache TTL/count outside supported bounds")
        self.directory = Path(directory)
        self.ttl = ttl
        self.max_entries = max_entries
        self._lock = threading.RLock()

    def path(self, key):
        if (
            not isinstance(key, str)
            or len(key) != 64
            or any(c not in "0123456789abcdef" for c in key)
        ):
            raise ValueError("invalid cache key")
        return self.directory / (key + ".json")

    def get(self, key):
        with self._lock:
            return self._get(key)

    def _get(self, key):
        path = self.path(key)
        try:
            before = path.lstat()
            if (
                self.directory.is_symlink()
                or not stat.S_ISREG(before.st_mode)
                or before.st_size > MAX_BYTES
                or getattr(before, "st_file_attributes", 0)
                & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
            ):
                return None
            flags = (
                os.O_RDONLY
                | getattr(os, "O_BINARY", 0)
                | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_NONBLOCK", 0)
            )
            with os.fdopen(os.open(path, flags), "rb") as stream:
                opened = os.fstat(stream.fileno())
                if not stat.S_ISREG(opened.st_mode) or (
                    opened.st_dev,
                    opened.st_ino,
                ) != (before.st_dev, before.st_ino):
                    return None
                entry = json_value(read_stream(stream, MAX_BYTES))
            if type(entry.get("created_at")) not in (int, float):
                return None
            age = time.time() - entry["created_at"]
            if not 0 <= age < self.ttl or entry["key"] != key:
                return None
            if fingerprint(entry["response"]) != entry["checksum"]:
                return None
            return entry["response"]
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            return None

    def put(self, key, response):
        with self._lock:
            return self._put(key, response)

    def _put(self, key, response):
        target = self.path(key)
        if self.directory.is_symlink():
            raise ValueError("cache directory must not be a symlink")
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        entry = dict(
            key=key,
            created_at=time.time(),
            response=response,
            checksum=fingerprint(response),
        )
        payload = json.dumps(entry).encode()
        if len(payload) > MAX_BYTES:
            return
        # Restrict eviction to this cache's hash-named regular files.
        files = [
            p
            for p in self.directory.glob("*.json")
            if len(p.stem) == 64
            and all(c in "0123456789abcdef" for c in p.stem)
            and p.is_file()
            and not p.is_symlink()
        ]
        others = [p for p in files if p != target]
        dated = []
        for path in others:
            try:
                dated.append((path.stat().st_mtime, path))
            except FileNotFoundError:
                continue
        victims = [p for _, p in sorted(dated)][
            : max(0, len(dated) + 1 - self.max_entries)
        ]
        name = None
        try:
            with tempfile.NamedTemporaryFile(
                dir=self.directory, delete=False
            ) as stream:
                name = stream.name
                stream.write(payload)
            os.replace(name, target)
            # Evict only after publication succeeds; never evict the replaced key.
            for old in victims:
                try:
                    old.unlink()
                except FileNotFoundError:
                    pass
        finally:
            if name and Path(name).exists():
                Path(name).unlink()
