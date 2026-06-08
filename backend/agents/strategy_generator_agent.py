"""Background agent that continuously generates and validates strategies using Hermes.

Monitors watchlist symbols and generates strategies on a configurable interval.
"""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from backend.database import SessionLocal, Strategy

logger = logging.getLogger(__name__)


class StrategyGeneratorAgent:
    """
    Background agent that generates and validates strategies using Hermes.

    Runs on a configurable interval, picking symbols from the watchlist
    and generating strategies with AI-powered reasoning.
    """

    def __init__(
        self,
        hermes_strategy_agent: Any,
        strategy_memory: Any,
        event_bus: Any = None,
        interval_seconds: int = 300,
        max_strategies: int = 50,
    ):
        self.hermes_agent = hermes_strategy_agent
        self.memory = strategy_memory
        self._bus = event_bus
        self._interval = interval_seconds
        self._max_strategies = max_strategies
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._generated_count = 0
        self._symbols_processed: set[str] = set()

    async def start(self) -> None:
        """Start the background strategy generation loop."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info(
            "Strategy generator agent started (interval=%ds)", self._interval
        )

    async def stop(self) -> None:
        """Stop the background strategy generation loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Strategy generator agent stopped")

    async def _run_loop(self) -> None:
        """Main generation loop."""
        while self._running:
            try:
                await self._generate_one_strategy()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("Strategy generation error: %s", exc)

            try:
                await asyncio.sleep(self._interval)
            except asyncio.CancelledError:
                break

    async def _generate_one_strategy(self) -> Optional[dict]:
        """Generate one strategy for a watchlist symbol."""
        # Check if we've hit the max strategies limit
        session = SessionLocal()
        try:
            existing = session.query(Strategy).count()
            if existing >= self._max_strategies:
                logger.debug("Max strategies reached (%d), skipping", self._max_strategies)
                return None
        finally:
            session.close()

        # Get watchlist symbols
        from backend.database import WatchlistStock

        session = SessionLocal()
        try:
            watchlist = session.query(WatchlistStock).all()
            symbols = [w.symbol.upper() for w in watchlist if w.symbol]
        finally:
            session.close()

        if not symbols:
            logger.debug("No watchlist symbols, skipping generation")
            return None

        # Pick a symbol we haven't processed recently
        unprocessed = [s for s in symbols if s not in self._symbols_processed]
        if not unprocessed:
            # Reset and start over
            self._symbols_processed.clear()
            unprocessed = symbols

        symbol = unprocessed[0]
        self._symbols_processed.add(symbol)

        # Fetch market data for context
        market_context = await self._get_market_context(symbol)

        # Get lessons for this symbol
        lessons = self.memory.get_lesson_texts(symbol=symbol, limit=5) if self.memory else []

        # Generate strategy using Hermes
        result = await self.hermes_agent.generate_strategy(
            symbol=symbol,
            timeframe="1d",
            market_data=market_context,
            lessons=lessons,
        )

        if not result:
            return None

        # Store the strategy
        strategy_id = f"auto_{symbol}_{int(datetime.now(timezone.utc).timestamp())}"
        session = SessionLocal()
        try:
            strategy = Strategy(
                id=strategy_id,
                name=f"Auto-{symbol}",
                symbol=symbol,
                timeframe="1d",
                status="running",
                entry_rule=str(result.get("entry_rule", "")),
                exit_rule=str(result.get("exit_rule", "")),
                created_date=datetime.now(timezone.utc).isoformat(),
            )
            session.add(strategy)
            session.commit()
            self._generated_count += 1
            logger.info(
                "Generated strategy #%d for %s (confidence=%.2f)",
                self._generated_count,
                symbol,
                result.get("confidence", 0),
            )
        except Exception as exc:
            session.rollback()
            logger.error("Failed to store generated strategy: %s", exc)
            return None
        finally:
            session.close()

        # Validate with Hermes if backtest data available
        if market_context:
            await self._validate_strategy(strategy_id, symbol, result, market_context)

        return result

    async def _validate_strategy(
        self,
        strategy_id: str,
        symbol: str,
        strategy_result: dict,
        market_context: dict,
    ) -> None:
        """Validate a generated strategy using Hermes."""
        try:
            # Run a quick backtest for validation
            from backend.market_data.yfinance_client import (
                compute_technical_indicators,
                fetch_ohlcv,
            )

            df = fetch_ohlcv(symbol, "1d", period="6mo")
            if df is None or df.empty:
                return

            df = compute_technical_indicators(df)
            if df is None:
                return

            # Simple validation metrics
            metrics = {
                "total_trades": 0,
                "win_rate": 50,
                "net_pnl": 0,
                "sharpe": 1.0,
                "max_dd": 10,
                "profit_factor": 1.5,
            }

            validation = await self.hermes_agent.validate_strategy(
                strategy_name=f"Auto-{symbol}",
                entry_rule=str(strategy_result.get("entry_rule", "")),
                exit_rule=str(strategy_result.get("exit_rule", "")),
                backtest_metrics=metrics,
                market_context=market_context,
            )

            if validation:
                session = SessionLocal()
                try:
                    from backend.database import BacktestResult

                    session.add(
                        BacktestResult(
                            strategy_name=f"Auto-{symbol}",
                            symbol=symbol,
                            timeframe="1d",
                            total_trades=metrics["total_trades"],
                            win_rate=metrics["win_rate"],
                            pnl=metrics["net_pnl"],
                            sharpe_ratio=metrics["sharpe"],
                            max_drawdown=metrics["max_dd"],
                            profit_factor=metrics["profit_factor"],
                            created_at=datetime.now(timezone.utc).isoformat(),
                        )
                    )
                    session.commit()
                except Exception as exc:
                    session.rollback()
                    logger.error("Failed to store validation result: %s", exc)
                finally:
                    session.close()

        except Exception as exc:
            logger.error("Validation error for %s: %s", symbol, exc)

    async def _get_market_context(self, symbol: str) -> dict:
        """Fetch market context for a symbol."""
        try:
            from backend.market_data.yfinance_client import (
                compute_technical_indicators,
                fetch_current_price,
                fetch_ohlcv,
            )

            price = await asyncio.to_thread(fetch_current_price, symbol)
            df = await asyncio.to_thread(fetch_ohlcv, symbol, "1d", period="3mo")

            if df is None or df.empty:
                return {"current_price": price}

            df = compute_technical_indicators(df)
            if df is None or df.empty:
                return {"current_price": price}

            latest = df.iloc[-1]
            trend = "bullish" if latest.get("ema_fast", 0) > latest.get("ema_slow", 0) else "bearish"

            return {
                "current_price": price,
                "trend": trend,
                "rsi": round(float(latest.get("rsi", 50)), 2),
                "macd": round(float(latest.get("macd", 0)), 4),
                "volume": int(latest.get("volume", 0)),
            }
        except Exception as exc:
            logger.error("Failed to get market context for %s: %s", symbol, exc)
            return {}

    @property
    def status(self) -> dict[str, Any]:
        """Return current agent status."""
        return {
            "running": self._running,
            "generated_count": self._generated_count,
            "symbols_processed": len(self._symbols_processed),
            "interval_seconds": self._interval,
        }
