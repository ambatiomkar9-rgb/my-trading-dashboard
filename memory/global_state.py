"""Shared, thread-safe global state manager."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from trading_system.config.models import PortfolioSnapshot, TradingMode

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class Position:
    """Canonical in-memory position object."""

    symbol: str
    quantity: float
    avg_price: float
    side: str
    mode: TradingMode
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    opened_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class GlobalState:
    """
    Shared state manager used by all agents and execution components.

    Unit-test example:
        >>> state = GlobalState(initial_balance=100000)
        >>> snapshot = asyncio.run(state.snapshot(TradingMode.PAPER))
        >>> snapshot.balance
        100000.0
    """

    def __init__(self, initial_balance: float = 100000.0) -> None:
        self._lock = asyncio.Lock()
        self._initial_balance = initial_balance
        self._balances: Dict[TradingMode, float] = {
            TradingMode.PAPER: initial_balance,
            TradingMode.LIVE: initial_balance,
            TradingMode.BACKTEST: initial_balance,
        }
        self._available_cash: Dict[TradingMode, float] = dict(self._balances)
        self._daily_realized_pnl: Dict[TradingMode, float] = {
            TradingMode.PAPER: 0.0,
            TradingMode.LIVE: 0.0,
            TradingMode.BACKTEST: 0.0,
        }
        self._consecutive_losses: Dict[TradingMode, int] = {
            TradingMode.PAPER: 0,
            TradingMode.LIVE: 0,
            TradingMode.BACKTEST: 0,
        }
        self._positions: Dict[TradingMode, Dict[str, Position]] = {
            TradingMode.PAPER: {},
            TradingMode.LIVE: {},
            TradingMode.BACKTEST: {},
        }

    async def snapshot(self, mode: TradingMode) -> PortfolioSnapshot:
        """Return a copy-safe snapshot for the selected mode."""
        async with self._lock:
            positions = {
                symbol: asdict(position) for symbol, position in self._positions[mode].items()
            }
            gross_exposure = sum(abs(p.quantity * p.avg_price) for p in self._positions[mode].values())
            return PortfolioSnapshot(
                mode=mode,
                balance=self._balances[mode],
                available_cash=self._available_cash[mode],
                daily_realized_pnl=self._daily_realized_pnl[mode],
                gross_exposure=gross_exposure,
                positions=positions,
                consecutive_losses=self._consecutive_losses[mode],
            )

    async def upsert_position(self, position: Position) -> None:
        """Insert or update a position."""
        async with self._lock:
            position.updated_at = datetime.now(timezone.utc)
            self._positions[position.mode][position.symbol] = position
            logger.debug("Position upserted for %s (%s)", position.symbol, position.mode.value)

    async def remove_position(self, symbol: str, mode: TradingMode) -> None:
        """Remove a position if present."""
        async with self._lock:
            self._positions[mode].pop(symbol, None)
            logger.debug("Position removed for %s (%s)", symbol, mode.value)

    async def adjust_cash_and_balance(self, mode: TradingMode, cash_delta: float, pnl_delta: float = 0.0) -> None:
        """Adjust cash and balance atomically."""
        async with self._lock:
            self._available_cash[mode] += cash_delta
            self._balances[mode] += pnl_delta
            self._daily_realized_pnl[mode] += pnl_delta
            if pnl_delta < 0:
                self._consecutive_losses[mode] += 1
            elif pnl_delta > 0:
                self._consecutive_losses[mode] = 0

    async def set_consecutive_losses(self, mode: TradingMode, value: int) -> None:
        """Force-update consecutive loss counter."""
        async with self._lock:
            self._consecutive_losses[mode] = max(0, value)

    async def get_position(self, symbol: str, mode: TradingMode) -> Optional[Position]:
        """Fetch one position by symbol."""
        async with self._lock:
            return self._positions[mode].get(symbol)

    async def update_unrealized_pnl(self, symbol: str, mode: TradingMode, mark_price: float) -> None:
        """Refresh unrealized PnL for one symbol using mark price."""
        async with self._lock:
            position = self._positions[mode].get(symbol)
            if not position:
                return
            if position.side.lower() == "buy":
                position.unrealized_pnl = (mark_price - position.avg_price) * position.quantity
            else:
                position.unrealized_pnl = (position.avg_price - mark_price) * position.quantity
            position.updated_at = datetime.now(timezone.utc)

    async def reset_daily_pnl(self, mode: TradingMode) -> None:
        """Reset daily realized PnL and losses."""
        async with self._lock:
            self._daily_realized_pnl[mode] = 0.0
            self._consecutive_losses[mode] = 0

    async def diagnostics(self) -> Dict[str, Any]:
        """Return a diagnostics snapshot safe for API usage."""
        out: Dict[str, Any] = {}
        for mode in TradingMode:
            snap = await self.snapshot(mode)
            out[mode.value] = {
                "balance": snap.balance,
                "available_cash": snap.available_cash,
                "daily_realized_pnl": snap.daily_realized_pnl,
                "gross_exposure": snap.gross_exposure,
                "positions": snap.positions,
                "consecutive_losses": snap.consecutive_losses,
                "updated_at": snap.updated_at.isoformat(),
            }
        return out
