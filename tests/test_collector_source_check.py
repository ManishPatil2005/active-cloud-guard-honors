import sys

import pytest

from scripts import collector_source_check as review


@pytest.mark.parametrize("mode", ["valid", "missing", "duplicate", "wrong"])
def test_release_metadata(mode):
    value = "Falco version: 0.45.0\nLibs version:  0.26.0\nEngine: 0.65.0\n"
    if mode == "missing":
        value = value.replace("Libs version:  0.26.0\n", "")
    elif mode == "duplicate":
        value += "Libs version: 0.26.0\n"
    elif mode == "wrong":
        value = value.replace("0.26.0", "0.25.0")
    if mode == "valid":
        assert review.version_fields(value) == dict(
            falco="0.45.0", libs="0.26.0", engine="0.65.0"
        )
    else:
        with pytest.raises(ValueError):
            review.version_fields(value)


@pytest.mark.parametrize("mode", ["valid", "path", "size", "marker"])
def test_source_scope_and_markers(mode):
    path = "driver/modern_bpf/helpers/store/ringbuf_store_params.h"
    payload = b"header\nmaps__get_boot_time() + bpf_ktime_get_boot_ns()\n"
    if mode == "path":
        path = "unreviewed.c"
    elif mode == "size":
        payload = b"x" * 256_001
    elif mode == "marker":
        payload = b"unrelated"
    if mode == "valid":
        record = review.source_record(path, payload)
        assert list(record["marker_lines"].values()) == [[2]]
        assert review.LIBS_COMMIT in record["url"] and len(record["sha256"]) == 64
    else:
        with pytest.raises(ValueError):
            review.source_record(path, payload)


def test_existing_output_refuses_docker_or_network(tmp_path, monkeypatch):
    report = tmp_path / "existing.json"
    report.write_text("preserve")
    monkeypatch.setattr(sys, "argv", ["review", "--output", str(report)])
    monkeypatch.setattr(
        review, "local_daemon", lambda: pytest.fail("unexpected Docker")
    )
    monkeypatch.setattr(
        review, "urlopen", lambda *a, **k: pytest.fail("unexpected network")
    )
    with pytest.raises(FileExistsError):
        review.main()
    assert report.read_text() == "preserve"


def test_failed_metadata_preserves_receipt(tmp_path, monkeypatch):
    report = tmp_path / "new.json"
    monkeypatch.setattr(sys, "argv", ["review", "--output", str(report)])

    def fail():
        raise ValueError("synthetic unavailable daemon")

    monkeypatch.setattr(review, "local_daemon", fail)
    with pytest.raises(ValueError):
        review.main()
    import json

    receipt = json.loads(report.read_text())
    assert receipt["status"] == "failed" and receipt["phase"] == "local_metadata"
    assert receipt["sensor_started"] is False and receipt["sources"] == []
