"""API authentication and request throttling controls."""

from __future__ import annotations

import hmac
import logging
import time
from collections import defaultdict, deque
from typing import Deque, Dict, Iterable, Optional

from fastapi import Header, HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from trading_system.config.settings import AppSettings

logger = logging.getLogger(__name__)


class ApiKeyGuard:
    """Header-based API key guard."""

    def __init__(self, settings: AppSettings) -> None:
        self.require_api_key = settings.api.require_api_key
        self.keys = [k for k in settings.api.api_keys if k]

    async def __call__(self, x_api_key: Optional[str] = Header(default=None)) -> None:
        if not self.require_api_key:
            return
        if not self.keys:
            raise HTTPException(status_code=503, detail="API key auth enabled but no keys configured.")
        incoming = x_api_key or ""
        if not any(hmac.compare_digest(incoming, valid) for valid in self.keys):
            raise HTTPException(status_code=401, detail="Invalid API key.")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory per-IP token bucket by minute."""

    def __init__(
        self,
        app: object,
        enabled: bool = True,
        requests_per_minute: int = 120,
        exempt_paths: Iterable[str] | None = None,
    ) -> None:
        super().__init__(app)
        self.enabled = enabled
        self.requests_per_minute = max(1, int(requests_per_minute))
        self.exempt_paths = set(exempt_paths or [])
        self._windows: Dict[str, Deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        if not self.enabled:
            return await call_next(request)
        path = request.url.path
        if path in self.exempt_paths:
            return await call_next(request)
        ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = self._windows[ip]
        cutoff = now - 60.0
        while window and window[0] < cutoff:
            window.popleft()
        if len(window) >= self.requests_per_minute:
            logger.warning("Rate limit exceeded ip=%s path=%s", ip, path)
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded."})
        window.append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.requests_per_minute - len(window)))
        return response
