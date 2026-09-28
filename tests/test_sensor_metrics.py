import hashlib
import json

import pytest

from cloudguard.sensor_metrics import summarize


@pytest.mark.parametrize(
    "mode",
    [
        "valid",
        "drops",
        "missing",
        "boolean",
        "reset",
        "time",
        "hash",
        "empty",
        "duplicate",
    ],
)
def test_metrics_accounting(tmp_path, mode):
    rows = [
        dict(
            output_fields={
                "evt.time": n,
                "falco.duration_sec": n,
                "scap.n_evts": n * 100,
                "scap.n_drops": 0,
                "falco.outputs_queue_num_drops": 0,
                "private_host_field": "not published",
            }
        )
        for n in (1, 2)
    ]
    last = rows[-1]["output_fields"]
    if mode == "drops":
        last["scap.n_drops"] = 7
    elif mode == "missing":
        del last["scap.n_drops"]
    elif mode == "boolean":
        last["scap.n_drops"] = False
    elif mode == "reset":
        last["scap.n_evts"] = 0
    elif mode == "time":
        last["evt.time"] = 1
    raw = "\n".join(json.dumps(r) for r in rows).encode()
    if mode == "empty":
        raw = b""
    if mode == "duplicate":
        raw = b'{"a":1,"a":2}\n{}'
    path = tmp_path / "metrics"
    path.write_bytes(raw)
    digest = "wrong" if mode == "hash" else hashlib.sha256(raw).hexdigest()
    if mode not in {"valid", "drops"}:
        with pytest.raises(ValueError):
            summarize(path, digest)
    else:
        report = summarize(path, digest)
        assert report["observed_counter_deltas"]["scap.n_drops"] == (
            7 if mode == "drops" else 0
        )
        assert report["coverage"] == "partial_or_unknown"
        assert "private_host_field" not in json.dumps(report)
