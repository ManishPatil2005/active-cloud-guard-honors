import json
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
from concurrent.futures import ThreadPoolExecutor

import pytest

from cloudguard.cache import AuditCache, fingerprint


@pytest.mark.parametrize(
    "kwargs",
    [
        {"ttl": True},
        {"ttl": "10"},
        {"ttl": float("nan")},
        {"max_entries": True},
        {"max_entries": 1.5},
    ],
)
def test_cache_options_exact_types(kwargs, tmp_path):
    with pytest.raises(ValueError):
        AuditCache(tmp_path, **kwargs)


@pytest.mark.parametrize("created", [True, "100", None])
def test_cache_timestamp_type_rejected(created, tmp_path):
    cache = AuditCache(tmp_path)
    key = fingerprint("key")
    cache.put(key, {"value": 1})
    entry = json.loads(cache.path(key).read_text())
    entry["created_at"] = created
    cache.path(key).write_text(json.dumps(entry))
    with patch("cloudguard.cache.time.time", return_value=2):
        assert cache.get(key) is None


def symlink_or_skip(link, target):
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symlink privilege unavailable")


def test_cache_symlink_leaf_not_read(tmp_path):
    cache = AuditCache(tmp_path / "cache")
    key = fingerprint("key")
    cache.put(key, {"value": 1})
    outside = tmp_path / "outside.json"
    cache.path(key).replace(outside)
    symlink_or_skip(cache.path(key), outside)
    with patch(
        "cloudguard.cache.time.time",
        return_value=json.loads(outside.read_text())["created_at"],
    ):
        assert cache.get(key) is None


def test_disappeared_eviction_victim_not_failed_publication(tmp_path):
    cache = AuditCache(tmp_path, max_entries=1)
    first, second = fingerprint("first"), fingerprint("second")
    cache.put(first, {"value": 1})
    original = Path.unlink

    def raced(path, *args, **kwargs):
        if path == cache.path(first):
            original(path)
            raise FileNotFoundError("another writer removed victim")
        return original(path, *args, **kwargs)

    with patch.object(Path, "unlink", raced):
        cache.put(second, {"value": 2})
    assert cache.get(second) == {"value": 2}


def test_changed_opened_identity_is_miss(tmp_path):
    cache = AuditCache(tmp_path)
    key = fingerprint("key")
    cache.put(key, {"value": 1})
    info = cache.path(key).stat()
    with patch(
        "cloudguard.cache.os.fstat",
        return_value=SimpleNamespace(
            st_mode=info.st_mode, st_dev=info.st_dev, st_ino=info.st_ino + 1
        ),
    ):
        assert cache.get(key) is None


def test_concurrent_atomic_replacements_not_partial_json(tmp_path):
    cache = AuditCache(tmp_path, max_entries=64)
    key = fingerprint("shared")
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda i: cache.put(key, {"value": i}), range(16)))
    assert cache.get(key)["value"] in range(16)
    assert list(tmp_path.iterdir()) == [cache.path(key)]


def test_disappeared_snapshot_entry_does_not_over_evict(tmp_path):
    cache = AuditCache(tmp_path, max_entries=2)
    first, second, third = [fingerprint(i) for i in range(3)]
    cache.put(first, {"value": 1})
    cache.put(second, {"value": 2})
    original = Path.stat
    calls = 0

    def disappear(path, *args, **kwargs):
        nonlocal calls
        if path == cache.path(first) and kwargs.get("follow_symlinks", True):
            calls += 1
            if calls == 2:
                path.unlink()
                raise FileNotFoundError("removed between enumeration and sorting")
        return original(path, *args, **kwargs)

    with patch.object(Path, "stat", disappear):
        cache.put(third, {"value": 3})
    assert cache.get(second) == {"value": 2}
    assert cache.get(third) == {"value": 3}
