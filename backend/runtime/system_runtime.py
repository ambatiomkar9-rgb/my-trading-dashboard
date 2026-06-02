"""Coordinates market data, signal execution, news, and Telegram polling at startup."""
from __future__ import annotations

import asyncio
import importlib
import logging
import os
from typing import Any, Optional

try:
    from backend.agents.news_sentiment_agent import NewsSentimentAgent  # type: ignore
    from backend.agents.trade_execution_agent import TradeExecutionAgent  # type: ignore
    from backend.agents.macro_intelligence_agent import MacroIntelligenceAgent  # type: ignore
    from backend.agents.whale_intelligence_agent import WhaleIntelligenceAgent  # type: ignore
    from backend.brokers.paper_broker import PaperBroker, PaperBrokerRouter  # type: ignore
    from backend.execution.auth.broker_auth_manager import BrokerAuthManager  # type: ignore
    from backend.market_data.market_data_engine import MarketDataEngine  # type: ignore
    from backend.notifications.telegram_bot import TelegramCallbackPoller  # type: ignore
    from backend.portfolio.position_manager import PositionManager  # type: ignore
    from backend.brokerage.charges_engine import ChargesEngine  # type: ignore
    from backend.risk.risk_guardian import RiskGuardian  # type: ignore
    from backend.database import SessionLocal, WatchlistStock  # type: ignore
except ModuleNotFoundError:  # noqa: BLE001
    from agents.news_sentiment_agent import NewsSentimentAgent  # type: ignore
    from agents.trade_execution_agent import TradeExecutionAgent  # type: ignore
    from agents.macro_intelligence_agent import MacroIntelligenceAgent  # type: ignore
    from agents.whale_intelligence_agent import WhaleIntelligenceAgent  # type: ignore
    from brokers.paper_broker import PaperBroker, PaperBrokerRouter  # type: ignore
    from execution.auth.broker_auth_manager import BrokerAuthManager  # type: ignore
    from market_data.market_data_engine import MarketDataEngine  # type: ignore
    from notifications.telegram_bot import TelegramCallbackPoller  # type: ignore
    from portfolio.position_manager import PositionManager  # type: ignore
    from brokerage.charges_engine import ChargesEngine  # type: ignore
    from risk.risk_guardian import RiskGuardian  # type: ignore
    from database import SessionLocal, WatchlistStock  # type: ignore

logger = logging.getLogger(__name__)


def _normalize_symbol(symbol: str) -> str:
    return str(symbol or "").upper().replace(".NS", "").replace(".BO", "").strip()


def _flag_enabled(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


class TradingSystemRuntime:
    """Starts and stops the agents that make the dashboard behave like a trading system."""

    def __init__(
        self,
        event_bus: Any,
        symbol_master: Any,
        live_broker: Any | None = None,
        trading_mode: str = "paper",
    ) -> None:
        self.event_bus = event_bus
        self.symbol_master = symbol_master
        self.live_broker = live_broker
        self.trading_mode = str(trading_mode or "paper").lower().strip()
        self.is_shadow = self.trading_mode == "shadow"
        self.broker_mode = "live" if self.trading_mode == "live" and self.live_broker is not None else "paper"
        self.position_manager = PositionManager()
        self.charges_engine = ChargesEngine(min_profitability_ratio=float(os.getenv("MIN_PROFITABILITY_RATIO", "3.0")))
        self.risk_guardian = RiskGuardian(self.charges_engine)
        self.market_data: MarketDataEngine | None = None
        self.news_agent: NewsSentimentAgent | None = None
        self.macro_agent: MacroIntelligenceAgent | None = None
        self.whale_agent: WhaleIntelligenceAgent | None = None
        self.telegram_poller: TelegramCallbackPoller | None = None
        self.technical_agent: Any | None = None
        self._tasks: dict[str, asyncio.Task[Any]] = {}
        self._running = False
        self._watchlist_symbols: list[str] = []
        self._market_data_enabled = _flag_enabled("ENABLE_MARKET_DATA") or self.trading_mode in ("live", "shadow")
        self._paper_router = PaperBrokerRouter({"upstox": PaperBroker(broker_name="upstox")})
        self.broker_adapter = self.live_broker if self.broker_mode == "live" and self.live_broker is not None else self._paper_router
        if self.broker_mode == "paper" and self.live_broker is None and self.trading_mode == "live":
            logger.warning("Live trading was requested but no live broker is available. Falling back to paper mode.")
        self.trade_agent = TradeExecutionAgent(
            broker_router=self.broker_adapter,
            risk_guardian=self.risk_guardian,
            charges_engine=self.charges_engine,
            position_manager=self.position_manager,
            event_bus=self.event_bus,
        )

    def _load_watchlist_symbols(self) -> list[str]:
        symbols: set[str] = set()
        try:
            db = SessionLocal()
            try:
                rows = db.query(WatchlistStock).filter(WatchlistStock.status == "active").all()
            finally:
                db.close()
            for row in rows:
                sym = _normalize_symbol(getattr(row, "symbol", ""))
                if sym:
                    symbols.add(sym)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not load watchlist symbols: %s", exc)
        return sorted(symbols)

    async def refresh_watchlist(self) -> list[str]:
        """Reload the active watchlist from the database and sync live agents."""
        try:
            latest = self._load_watchlist_symbols()
            added = [symbol for symbol in latest if symbol not in self._watchlist_symbols]
            removed = [symbol for symbol in self._watchlist_symbols if symbol not in latest]
            self._watchlist_symbols = latest

            if self.technical_agent is not None and hasattr(self.technical_agent, "set_watchlist"):
                try:
                    self.technical_agent.set_watchlist(latest)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Technical watchlist sync failed: %s", exc)

            if self.news_agent is not None and hasattr(self.news_agent, "set_watchlist"):
                try:
                    self.news_agent.set_watchlist(latest)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("News watchlist sync failed: %s", exc)

            if self.market_data is not None and added:
                try:
                    await self.market_data.subscribe(added)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Market data resubscribe failed: %s", exc)

            logger.info("Watchlist refreshed: %d active, %d added, %d removed", len(latest), len(added), len(removed))
            return latest
        except Exception as exc:  # noqa: BLE001
            logger.error("refresh_watchlist failed: %s", exc)
            return list(self._watchlist_symbols)

    def _build_optional_technical_agent(self, watchlist: list[str]) -> Any | None:
        """Load an optional technical-analysis agent if the user's laptop copy provides one."""
        for module_name in (
            "backend.agents.technical_analysis_agent",
            "agents.technical_analysis_agent",
        ):
            try:
                module = importlib.import_module(module_name)
            except Exception:
                continue
            agent_cls = getattr(module, "TechnicalAnalysisAgent", None) or getattr(module, "TechnicalAgent", None)
            if agent_cls is None:
                continue

            keyword_variants = (
                {
                    "event_bus": self.event_bus,
                    "watchlist": watchlist,
                    "symbol_master": self.symbol_master,
                    "market_data_engine": self.market_data,
                },
                {
                    "event_bus": self.event_bus,
                    "watchlist": watchlist,
                    "symbol_master": self.symbol_master,
                    "market_data": self.market_data,
                },
                {"event_bus": self.event_bus, "watchlist": watchlist},
                {"event_bus": self.event_bus},
            )
            positional_variants = (
                (self.event_bus, watchlist),
                (self.event_bus,),
            )

            for kwargs in keyword_variants:
                try:
                    return agent_cls(**kwargs)
                except TypeError:
                    continue
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Technical agent init failed: %s", exc)
                    return None

            for args in positional_variants:
                try:
                    return agent_cls(*args)
                except TypeError:
                    continue
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Technical agent init failed: %s", exc)
                    return None

            logger.warning("Technical analysis agent found, but no known constructor signature matched.")
            return None
        return None

    def _spawn(self, name: str, coro: Any) -> None:
        task = asyncio.create_task(coro)
        def _log_task_result(done: asyncio.Task[Any]) -> None:
            try:
                exc = done.exception()
                if exc is not None:
                    logger.error("%s task failed: %s", name, exc)
            except asyncio.CancelledError:
                pass
            except Exception as exc:  # noqa: BLE001
                logger.error("%s task inspection failed: %s", name, exc)

        task.add_done_callback(_log_task_result)
        self._tasks[name] = task

    def status(self) -> dict[str, Any]:
        """Return a snapshot of the runtime state for health checks."""
        snapshot: dict[str, Any] = {
            "running": self._running,
            "mode": self.trading_mode,
            "is_shadow": self.is_shadow,
            "broker_mode": self.broker_mode,
            "watchlist_symbols": list(self._watchlist_symbols),
            "watchlist_count": len(self._watchlist_symbols),
            "market_data_enabled": self._market_data_enabled,
            "market_data_online": self.market_data is not None,
            "news_agent_online": self.news_agent is not None,
            "macro_agent_online": self.macro_agent is not None,
            "whale_agent_online": self.whale_agent is not None,
            "telegram_online": self.telegram_poller is not None,
            "technical_agent_online": self.technical_agent is not None,
            "tasks": {name: not task.done() for name, task in self._tasks.items()},
            "paper_snapshot": self._paper_router.snapshot() if self.broker_mode == "paper" else None,
        }
        return snapshot

    async def start(self) -> None:
        """Start all configured agents without blocking the FastAPI app startup."""
        try:
            if self._running:
                return
            self._running = True
            self._watchlist_symbols = await self.refresh_watchlist()

            async def _handle_market_tick(payload: dict[str, Any]) -> None:
                try:
                    symbol = _normalize_symbol(str(payload.get("symbol") or ""))
                    ltp = float(payload.get("ltp") or 0.0)
                    if symbol and ltp > 0:
                        await self.position_manager.on_price_update(symbol, ltp)
                except Exception as exc:  # noqa: BLE001
                    logger.error("Position tick handler failed: %s", exc)

            self.event_bus.subscribe("market.tick", _handle_market_tick)

            if self._market_data_enabled:
                try:
                    self.market_data = MarketDataEngine(self.event_bus, BrokerAuthManager("upstox"))
                    await self.market_data.start()
                    if self._watchlist_symbols:
                        await self.market_data.subscribe(self._watchlist_symbols)
                    logger.info("Market data runtime started")
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Market data startup failed: %s", exc)

            self.technical_agent = self._build_optional_technical_agent(self._watchlist_symbols)
            if self.technical_agent is not None and hasattr(self.technical_agent, "start"):
                self._spawn("technical", self.technical_agent.start())

            if self._watchlist_symbols and os.getenv("NEWSAPI_KEY", "").strip():
                self.news_agent = NewsSentimentAgent(self.event_bus, self._watchlist_symbols)
                self._spawn("news", self.news_agent.start())

            self._spawn("trade", self.trade_agent.start())

            # Start macro intelligence agent (always runs — provides market-wide context)
            self.macro_agent = MacroIntelligenceAgent(self.event_bus)
            self._spawn("macro", self.macro_agent.start())

            # Start whale intelligence agent (always runs — tracks institutional flows)
            self.whale_agent = WhaleIntelligenceAgent(self.event_bus)
            self._spawn("whale", self.whale_agent.start())

            telegram_disabled = os.getenv("TELEGRAM_DISABLED", "").strip().lower() in {"1", "true", "yes", "on"}
            if not telegram_disabled and os.getenv("TELEGRAM_BOT_TOKEN", "").strip() and os.getenv("DASHBOARD_API_TOKEN", "").strip():
                self.telegram_poller = TelegramCallbackPoller()
                self._spawn("telegram", self.telegram_poller.start())

            logger.info(
                "Runtime started (mode=%s, broker_mode=%s, watchlist=%d, market_data=%s)",
                self.trading_mode,
                self.broker_mode,
                len(self._watchlist_symbols),
                "on" if self.market_data is not None else "off",
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("TradingSystemRuntime start failed: %s", exc)

    async def stop(self) -> None:
        """Stop the agents and cancel background tasks."""
        try:
            self._running = False
            for agent in (self.telegram_poller, self.news_agent, self.trade_agent, self.market_data, self.technical_agent, self.macro_agent, self.whale_agent):
                try:
                    stop = getattr(agent, "stop", None)
                    if stop is not None:
                        result = stop()
                        if asyncio.iscoroutine(result):
                            await result
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Agent stop failed: %s", exc)

            for name, task in list(self._tasks.items()):
                if not task.done():
                    task.cancel()
            if self._tasks:
                await asyncio.gather(*self._tasks.values(), return_exceptions=True)
            self._tasks.clear()
        except Exception as exc:  # noqa: BLE001
            logger.error("TradingSystemRuntime stop failed: %s", exc)


def build_runtime(
    event_bus: Any,
    symbol_master: Any,
    live_broker: Any | None = None,
    trading_mode: str = "paper",
) -> TradingSystemRuntime:
    """Factory used by the FastAPI app to bootstrap the agent runtime."""
    return TradingSystemRuntime(
        event_bus=event_bus,
        symbol_master=symbol_master,
        live_broker=live_broker,
        trading_mode=trading_mode,
    )
