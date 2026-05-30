"""System-wide kill switch logic."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class KillSwitchReason(str, Enum):
    """Supported kill switch trigger reasons."""

    ABNORMAL_VOLATILITY = "abnormal_volatility"
    API_FAILURE = "api_failure"
    DRAWDOWN_EXCEEDED = "drawdown_exceeded"
    CONSECUTIVE_LOSSES = "consecutive_losses"
    MANUAL = "manual"


@dataclass(slots=True)
class KillSwitchState:
    """Kill switch state record."""

    active: bool = False
    reason: Optional[KillSwitchReason] = None
    details: Dict[str, Any] | None = None
    triggered_at: Optional[datetime] = None


class KillSwitch:
    """Centralized safety interlock for all execution modes except backtest."""

    def __init__(
        self,
        max_drawdown_pct: float = 10.0,
        max_consecutive_losses: int = 5,
        max_api_failures: int = 5,
        abnormal_volatility_pct: float = 6.0,
    ) -> None:
        self.max_drawdown_pct = max_drawdown_pct
        self.max_consecutive_losses = max_consecutive_losses
        self.max_api_failures = max_api_failures
        self.abnormal_volatility_pct = abnormal_volatility_pct
        self._state = KillSwitchState()
        self._api_failures = 0

    @property
    def is_active(self) -> bool:
        """Whether switch is currently active."""
        return self._state.active

    @property
    def state(self) -> KillSwitchState:
        """Return full state."""
        return self._state

    def trigger(self, reason: KillSwitchReason, details: Optional[Dict[str, Any]] = None) -> None:
        """Trigger and lock the kill switch."""
        if self._state.active:
            return
        self._state = KillSwitchState(
            active=True,
            reason=reason,
            details=details or {},
            triggered_at=datetime.now(timezone.utc),
        )
        logger.error("Kill switch triggered reason=%s details=%s", reason.value, details)

    def reset(self) -> None:
        """Manual reset (human-supervised action)."""
        logger.warning("Kill switch reset requested")
        self._state = KillSwitchState()
        self._api_failures = 0

    def register_api_failure(self, error: str) -> None:
        """Track API failures and trigger if threshold exceeded."""
        self._api_failures += 1
        if self._api_failures >= self.max_api_failures:
            self.trigger(
                KillSwitchReason.API_FAILURE,
                {"api_failures": self._api_failures, "last_error": error},
            )

    def register_success(self) -> None:
        """Reset API failure streak on successful call."""
        self._api_failures = 0

    def evaluate_drawdown(self, peak_equity: float, current_equity: float) -> None:
        """Trigger if drawdown exceeds configured threshold."""
        if peak_equity <= 0:
            return
        drawdown_pct = ((peak_equity - current_equity) / peak_equity) * 100
        if drawdown_pct >= self.max_drawdown_pct:
            self.trigger(
                KillSwitchReason.DRAWDOWN_EXCEEDED,
                {"drawdown_pct": drawdown_pct, "peak_equity": peak_equity, "current_equity": current_equity},
            )

    def evaluate_losses(self, consecutive_losses: int) -> None:
        """Trigger on consecutive losses."""
        if consecutive_losses >= self.max_consecutive_losses:
            self.trigger(
                KillSwitchReason.CONSECUTIVE_LOSSES,
                {"consecutive_losses": consecutive_losses},
            )

    def evaluate_volatility(self, move_pct: float, symbol: str) -> None:
        """Trigger on abnormal volatility spikes."""
        if abs(move_pct) >= self.abnormal_volatility_pct:
            self.trigger(
                KillSwitchReason.ABNORMAL_VOLATILITY,
                {"symbol": symbol, "move_pct": move_pct},
            )

    def manual_trigger(self, note: str) -> None:
        """Manual operator trigger."""
        self.trigger(KillSwitchReason.MANUAL, {"note": note})
