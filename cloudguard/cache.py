"""Bounded, opt-in local cache. Stores model responses, never live probes."""

import hashlib
import json
import os
from pathlib import Path
import tempfile
import time

MAX_BYTES = 2_000_000


def fingerprint(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


class AuditCache:
    def __init__(self, directory, ttl=3600, max_entries=128):
        if not 0 < ttl <= 86400 or not 1 <= max_entries <= 1024:
            raise ValueError("cache TTL/count outside supported bounds")
        self.directory = Path(directory)
        self.ttl = ttl
        self.max_entries = max_entries

    def path(self, key):
        if len(key) != 64 or any(c not in "0123456789abcdef" for c in key):
            raise ValueError("invalid cache key")
        return self.directory / (key + ".json")

    def get(self, key):
        path = self.path(key)
        try:
            if path.stat().st_size > MAX_BYTES:
                return None
            entry = json.loads(path.read_text(encoding="utf-8"))
            age = time.time() - entry["created_at"]
            if not 0 <= age < self.ttl or entry["key"] != key:
                return None
            if fingerprint(entry["response"]) != entry["checksum"]:
                return None
            return entry["response"]
        except (OSError, ValueError, KeyError, TypeError):
            return None

    def put(self, key, response):
        self.directory.mkdir(parents=True, exist_ok=True)
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
        for old in sorted(files, key=lambda p: p.stat().st_mtime)[
            : max(0, len(files) - self.max_entries + 1)
        ]:
            old.unlink()
        name = None
        try:
            with tempfile.NamedTemporaryFile(
                dir=self.directory, delete=False
            ) as stream:
                name = stream.name
                stream.write(payload)
            os.replace(name, self.path(key))
        finally:
            if name and Path(name).exists():
                Path(name).unlink()
