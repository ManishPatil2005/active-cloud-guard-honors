"""Bounded TCP checks against explicitly allowed loopback endpoints only."""

import ipaddress
import socket
import time
from datetime import datetime, timezone


def probe(host, port, *, allowlist, timeout=1.0, vantage="local-host", asset_id=None):
    ip = ipaddress.ip_address(host)  # No DNS resolution / rebinding.
    if not ip.is_loopback or (host, port) not in allowlist:
        raise ValueError("endpoint must be loopback and explicitly allowlisted")
    if isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65535:
        raise ValueError("invalid port")
    if not 0 < timeout <= 2:
        raise ValueError("timeout must be in (0,2]")
    start = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            outcome, reason = (
                "reachable",
                "TCP connection accepted; authentication not tested",
            )
    except ConnectionRefusedError:
        outcome, reason = (
            "unreachable",
            "connection refused from this vantage at this time",
        )
    except (TimeoutError, OSError) as error:
        outcome, reason = "inconclusive", type(error).__name__
    return dict(
        asset_id=asset_id,
        host=host,
        port=port,
        vantage=vantage,
        outcome=outcome,
        reason=reason,
        elapsed_ms=round((time.perf_counter() - start) * 1000, 3),
        observed_at=datetime.now(timezone.utc).isoformat(),
        protocol="tcp",
    )
