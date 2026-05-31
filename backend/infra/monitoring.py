"""Shared monitoring helpers for health check payloads."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def build_health_snapshot(service_name: str, status: str = "ok", extra: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build a simple JSON health payload for probes and dashboards."""

    payload: dict[str, Any] = {
        "service": service_name,
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if extra:
        payload.update(extra)
    return payload

