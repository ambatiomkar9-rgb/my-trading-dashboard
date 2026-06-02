"""Circuit Breaker — protects external API calls from cascading failures.

States:
  CLOSED  — normal operation, requests pass through
  OPEN    — too many failures, requests are blocked
  HALF_OPEN — testing if the service recovered

Usage:
    breaker = CircuitBreaker("ollama", failure_threshold=3, recovery_timeout=30)
    async with breaker.call():
        result = await ollama_client.generate(...)
"""
from __future__ import annotations

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerOpen(Exception):
    """Raised when the circuit breaker is open and blocking calls."""

    def __init__(self, name: str, remaining: float) -> None:
        self.name = name
        self.remaining = remaining
        super().__init__(f"Circuit breaker '{name}' is open. Retry in {remaining:.0f}s")


class CircuitBreaker:
    """Stateful circuit breaker for protecting external calls.

    Args:
        name: Identifier for logging.
        failure_threshold: Consecutive failures before opening the circuit.
        recovery_timeout: Seconds to wait before trying again (half-open).
        success_threshold: Consecutive successes in half-open to close the circuit.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 3,
        recovery_timeout: float = 30.0,
        success_threshold: int = 1,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0.0
        self._total_calls = 0
        self._total_failures = 0
        self._total_rejected = 0

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            if time.time() - self._last_failure_time >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._success_count = 0
                logger.info("Circuit breaker '%s' → HALF_OPEN", self.name)
        return self._state

    def record_success(self) -> None:
        self._total_calls += 1
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.success_threshold:
                self._state = CircuitState.CLOSED
                self._failure_count = 0
                self._success_count = 0
                logger.info("Circuit breaker '%s' → CLOSED (recovered)", self.name)
        elif self._state == CircuitState.CLOSED:
            self._failure_count = 0

    def record_failure(self) -> None:
        self._total_calls += 1
        self._total_failures += 1
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.OPEN
            logger.warning("Circuit breaker '%s' → OPEN (half-open test failed)", self.name)
        elif self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
            logger.warning(
                "Circuit breaker '%s' → OPEN (failures=%d/%d)",
                self.name,
                self._failure_count,
                self.failure_threshold,
            )

    def allow_request(self) -> bool:
        state = self.state
        if state == CircuitState.CLOSED:
            return True
        if state == CircuitState.HALF_OPEN:
            return True
        # OPEN
        self._total_rejected += 1
        return False

    def remaining_recovery_time(self) -> float:
        if self._state != CircuitState.OPEN:
            return 0.0
        elapsed = time.time() - self._last_failure_time
        return max(0.0, self.recovery_timeout - elapsed)

    @asynccontextmanager
    async def call(self):
        """Context manager that raises CircuitBreakerOpen if blocked."""
        if not self.allow_request():
            raise CircuitBreakerOpen(self.name, self.remaining_recovery_time())
        try:
            yield
        except CircuitBreakerOpen:
            raise
        except Exception:
            self.record_failure()
            raise
        else:
            self.record_success()

    def execute(self, fn: Callable, *args: Any, **kwargs: Any) -> Any:
        """Synchronous convenience wrapper (non-async)."""
        if not self.allow_request():
            raise CircuitBreakerOpen(self.name, self.remaining_recovery_time())
        try:
            result = fn(*args, **kwargs)
            self.record_success()
            return result
        except CircuitBreakerOpen:
            raise
        except Exception:
            self.record_failure()
            raise

    async def execute_async(self, fn: Callable, *args: Any, **kwargs: Any) -> Any:
        """Async convenience wrapper."""
        if not self.allow_request():
            raise CircuitBreakerOpen(self.name, self.remaining_recovery_time())
        try:
            result = await fn(*args, **kwargs)
            self.record_success()
            return result
        except CircuitBreakerOpen:
            raise
        except Exception:
            self.record_failure()
            raise

    def status(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self._failure_count,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout,
            "remaining_recovery_s": round(self.remaining_recovery_time(), 1),
            "total_calls": self._total_calls,
            "total_failures": self._total_failures,
            "total_rejected": self._total_rejected,
        }

    def reset(self) -> None:
        """Force reset to CLOSED."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        logger.info("Circuit breaker '%s' → CLOSED (manual reset)", self.name)


# ─── Global circuit breakers ────────────────────────────────────────────────

_breakers: dict[str, CircuitBreaker] = {}


def get_breaker(
    name: str,
    failure_threshold: int = 3,
    recovery_timeout: float = 30.0,
) -> CircuitBreaker:
    """Get or create a named circuit breaker (singleton per name)."""
    if name not in _breakers:
        _breakers[name] = CircuitBreaker(
            name,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
        )
    return _breakers[name]


def all_breakers_status() -> dict[str, dict[str, Any]]:
    """Return status of all registered circuit breakers."""
    return {name: br.status() for name, br in _breakers.items()}
