"""Live technical-analysis agent that turns market ticks into approval-ready trade signals."""
from __future__ import annotations

import asyncio
import logging
import os
import time
import uuid
from collections import defaultdict, deque
from datetime import datetime, timezone, timedelta
from typing import Any, Optional

try:
    from backend.database import SessionLocal, TradeSignal, WatchlistStock  # type: ignore
    from backend.notifications.telegram_bot import send_approval_request, send_message  # type: ignore
except ModuleNotFoundError:  # noqa: BLE001
    from database import SessionLocal, TradeSignal, WatchlistStock  # type: ignore
    from notifications.telegram_bot import send_approval_request, send_message  # type: ignore

logger = logging.getLogger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))


def _is_market_hours() -> bool:
    """Check if current time is within Indian market hours (9:15 AM - 3:30 PM IST)."""
    now = datetime.now(IST)
    if now.weekday() >= 5:
        return False
    market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
    return market_open <= now <= market_close


def _normalize_symbol(symbol: str) -> str:
    return str(symbol or "").upper().replace(".NS", "").replace(".BO", "").strip()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class TechnicalAnalysisAgent:
    """
    Simple momentum-based technical agent.

    It listens to `market.tick` events, keeps a rolling price window per symbol,
    and creates pending `trade_signals` rows when a bullish/bearish crossover appears.
    """

    def __init__(
        self,
        event_bus: Any,
        watchlist: list[str] | None = None,
        symbol_master: Any | None = None,
        market_data_engine: Any | None = None,
        market_data: Any | None = None,
        lookback: int = 20,
        signal_cooldown_sec: int | None = None,
    ) -> None:
        self._bus = event_bus
        self._symbol_master = symbol_master
        self._market_data = market_data_engine or market_data
        self._watchlist: set[str] = {_normalize_symbol(sym) for sym in (watchlist or []) if _normalize_symbol(sym)}
        self._lookback = max(8, int(lookback or 20))
        self._cooldown_sec = int(signal_cooldown_sec or os.getenv("TECH_SIGNAL_COOLDOWN_SEC", "900"))
        self._histories: dict[str, deque[float]] = defaultdict(lambda: deque(maxlen=self._lookback))
        self._last_signal_at: dict[str, float] = {}
        self._running = False
        self._task: asyncio.Task | None = None

        if self._bus is not None and hasattr(self._bus, "subscribe"):
            try:
                self._bus.subscribe("market.tick", self._on_market_tick)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Could not subscribe technical agent to market.tick: %s", exc)

    def set_watchlist(self, symbols: list[str]) -> None:
        """Replace the active watchlist in memory."""
        self._watchlist = {_normalize_symbol(sym) for sym in symbols if _normalize_symbol(sym)}

    def add_symbol(self, symbol: str) -> None:
        """Add one symbol to the active watchlist."""
        sym = _normalize_symbol(symbol)
        if sym:
            self._watchlist.add(sym)

    def remove_symbol(self, symbol: str) -> None:
        """Remove one symbol from the active watchlist."""
        sym = _normalize_symbol(symbol)
        if sym in self._watchlist:
            self._watchlist.remove(sym)

    async def start(self) -> None:
        """Keep the agent alive and ready to process ticks."""
        try:
            self._running = True
            logger.info("TechnicalAnalysisAgent started")
            while self._running:
                await asyncio.sleep(60)
        except Exception as exc:  # noqa: BLE001
            logger.error("TechnicalAnalysisAgent start failed: %s", exc)

    async def stop(self) -> None:
        """Stop the keepalive loop."""
        try:
            self._running = False
            if self._task and not self._task.done():
                self._task.cancel()
        except Exception as exc:  # noqa: BLE001
            logger.error("TechnicalAnalysisAgent stop failed: %s", exc)

    async def _on_market_tick(self, payload: dict[str, Any]) -> None:
        """Process each incoming market tick and emit a signal when conditions align."""
        try:
            if not _is_market_hours():
                return
            symbol = _normalize_symbol(str(payload.get("symbol") or ""))
            if not symbol or not self._watchlist or symbol not in self._watchlist:
                return

            price = float(payload.get("ltp") or payload.get("price") or 0.0)
            if price <= 0:
                return

            history = self._histories[symbol]
            history.append(price)
            if len(history) < min(8, self._lookback):
                return

            prices = list(history)
            fast_len = min(5, len(prices) // 2)
            slow_len = min(15, len(prices) - 1)
            fast_window = prices[-fast_len:]
            slow_window = prices[-slow_len:]
            fast_avg = sum(fast_window) / len(fast_window)
            slow_avg = sum(slow_window) / len(slow_window)
            momentum = ((prices[-1] - prices[0]) / prices[0]) * 100 if prices[0] else 0.0
            trend_strength = ((fast_avg - slow_avg) / slow_avg) * 100 if slow_avg else 0.0

            signal_type = "buy" if fast_avg > slow_avg and momentum > 0 else "sell" if fast_avg < slow_avg and momentum < 0 else "hold"
            if signal_type == "hold":
                return

            now = time.time()
            last_time = float(self._last_signal_at.get(symbol, 0.0))
            if last_time and (now - last_time) < self._cooldown_sec:
                return

            technical_score = max(0.0, min(100.0, 50.0 + (trend_strength * 3.0) + (momentum * 2.0)))
            await self._create_signal(
                symbol=symbol,
                signal_type=signal_type,
                price=price,
                technical_score=technical_score,
                reason="EMA/momentum crossover",
            )
            self._last_signal_at[symbol] = now
        except Exception as exc:  # noqa: BLE001
            logger.error("Technical tick handling failed: %s", exc)

    async def _create_signal(
        self,
        symbol: str,
        signal_type: str,
        price: float,
        technical_score: float,
        reason: str,
    ) -> None:
        """Persist a pending trade signal and ask Telegram for approval."""
        try:
            session = SessionLocal()
            try:
                watch = session.query(WatchlistStock).filter(WatchlistStock.symbol == symbol).first()
                quantity = int(getattr(watch, "quantity_to_buy", 1) or 1) if watch else 1
                strategy_id = str(getattr(watch, "strategy_id", "default") or "default") if watch else "default"
                auto_trade = bool(getattr(watch, "auto_trade", False)) if watch else False

                signal_id = uuid.uuid4().hex
                row = TradeSignal(
                    id=signal_id,
                    symbol=symbol,
                    strategy_id=strategy_id,
                    signal_type=signal_type,
                    signal_price=float(price),
                    signal_time=_utc_now(),
                    technical_score=float(technical_score),
                    news_score=0.0,
                    fundamental_score=0.0,
                    risk_score=0.0,
                    overall_score=float(technical_score),
                    approval_status="approved" if auto_trade else "pending",
                    approval_reason=reason,
                )
                session.add(row)

                if watch is None:
                    watch = WatchlistStock(symbol=symbol, strategy_id=strategy_id, auto_trade=False, quantity_to_buy=quantity)
                    session.add(watch)

                watch.last_signal = signal_type
                watch.last_signal_price = float(price)
                watch.last_checked = _utc_now()
                session.commit()
            finally:
                session.close()

            atr = 0.0
            if len(prices) >= 14:
                highs = prices[-14:]
                avg_range = (max(highs) - min(highs)) / len(highs)
                atr = avg_range if avg_range > 0 else price * 0.02
            else:
                atr = price * 0.02

            payload = {
                "id": signal_id,
                "symbol": symbol,
                "side": signal_type,
                "signal_type": signal_type,
                "quantity": quantity,
                "quantity_to_buy": quantity,
                "price": float(price),
                "signal_price": float(price),
                "score": round(float(technical_score), 1),
                "technical_score": round(float(technical_score), 1),
                "news_score": 0.0,
                "fundamental_score": 0.0,
                "risk_score": 0.0,
                "overall_score": round(float(technical_score), 1),
                "reason": reason,
                "approval_reason": reason,
                "approval_status": "approved" if auto_trade else "pending",
                "broker": "upstox",
                "trade_segment": "intraday",
                "expected_exit": round(float(price) + (2.0 * atr if signal_type == "buy" else -2.0 * atr), 2),
                "stop_loss": round(float(price) - (1.5 * atr if signal_type == "buy" else -1.5 * atr), 2),
                "atr": round(atr, 2),
            }

            if self._bus is not None and hasattr(self._bus, "publish"):
                await self._bus.publish("signal.created", payload)

            if os.getenv("TELEGRAM_BOT_TOKEN", "").strip() and os.getenv("TELEGRAM_CHAT_ID", "").strip():
                if auto_trade:
                    side_upper = signal_type.upper()
                    await send_message(
                        f"*AUTO-EXECUTING {side_upper} {symbol}*\n"
                        f"Price: Rs {price:.2f}\n"
                        f"Qty: {quantity}\n"
                        f"Score: {technical_score:.1f}/100\n"
                        f"Reason: {reason}\n"
                        f"Executing automatically per your strategy..."
                    )
                else:
                    await send_approval_request(payload)

            logger.info("Technical signal created: %s %s @ %.2f (auto_trade=%s)", signal_type.upper(), symbol, price, auto_trade)
        except Exception as exc:  # noqa: BLE001
            logger.error("Signal creation failed for %s: %s", symbol, exc)
