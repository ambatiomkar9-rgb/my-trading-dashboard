"""In-memory sliding-window rate limiter for FastAPI endpoints."""
from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request


class RateLimiter:
    """Per-key sliding window rate limiter."""

    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._windows: dict[str, deque[float]] = defaultdict(deque)

    def _cleanup(self, key: str, now: float) -> None:
        cutoff = now - self.window_seconds
        window = self._windows[key]
        while window and window[0] < cutoff:
            window.popleft()

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        self._cleanup(key, now)
        if len(self._windows[key]) >= self.max_requests:
            return False
        self._windows[key].append(now)
        return True


_limiters: dict[str, RateLimiter] = {}


def get_limiter(name: str, max_requests: int, window_seconds: int) -> RateLimiter:
    if name not in _limiters:
        _limiters[name] = RateLimiter(max_requests, window_seconds)
    return _limiters[name]


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limit(name: str, max_requests: int, window_seconds: int):
    """FastAPI dependency factory for rate limiting."""
    limiter = get_limiter(name, max_requests, window_seconds)

    async def _check(request: Request) -> None:
        key = f"{name}:{_client_ip(request)}"
        if not limiter.is_allowed(key):
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded for {name}. Try again later.",
            )

    return _check
