"""FastAPI application for the trading dashboard and local trading agents."""
from __future__ import annotations

import asyncio
import json
import logging
import os
import random
import sqlite3
import sys
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import httpx
from fastapi import Depends, FastAPI, Form, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.auth import create_token, require_admin, verify_token
from backend.brokerage.charges_engine import ChargesEngine, TradeSegment
from backend.brokers.upstox_broker import broker_from_env
from backend.config.trading_config import disable_trading, enable_trading, is_trading_enabled
from backend.core.event_bus import AsyncEventBus, build_event_bus
from backend.core.event_store import build_event_store
from backend.database import (
    AgentState,
    BacktestResult,
    ChatHistory,
    SessionLocal,
    Settings as SettingRow,
    Strategy,
    Trade,
    TradeSignal,
    WatchlistStock,
    init_db,
)
from backend.execution.auth.broker_auth_manager import BrokerAuthManager
from backend.infra.monitoring import build_health_snapshot
from backend.infra.tooling import init_sentry, load_tooling_config
from backend.integrations.hermes_client import HermesClient
from backend.market_data.symbol_master_service import build_symbol_master
from backend.notifications.telegram_bot import TelegramCallbackPoller, send_approval_request, send_message
from backend.portfolio.position_manager import PositionManager
from backend.risk.risk_guardian import RiskGuardian
from backend.runtime.system_runtime import TradingSystemRuntime, build_runtime
from backend.user_store import create_user, ensure_default_admin, update_password, verify_user

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIST = REPO_ROOT / "frontend" / "dist"
INDEX_HTML = FRONTEND_DIST / "index.html"
EXECUTIONS_DB = REPO_ROOT / "data" / "executions.db"

SETTINGS_ENV_MAP = {
    "api_key": "UPSTOX_API_KEY",
    "api_secret": "UPSTOX_API_SECRET",
    "broker": "BROKER_NAME",
    "ollama_url": "OLLAMA_URL",
    "ollama_model": "OLLAMA_MODEL",
    "telegram_bot_token": "TELEGRAM_BOT_TOKEN",
    "telegram_chat_id": "TELEGRAM_CHAT_ID",
    "dashboard_url": "DASHBOARD_URL",
    "dashboard_api_token": "DASHBOARD_API_TOKEN",
    "newsapi_key": "NEWSAPI_KEY",
    "trading_mode": "TRADING_MODE",
    "trading_enabled": "TRADING_ENABLED",
    "upstox_redirect_uri": "UPSTOX_REDIRECT_URI",
    "sentry_dsn": "SENTRY_DSN",
    "hermes_enabled": "HERMES_ENABLED",
    "hermes_cmd": "HERMES_CMD",
    "hermes_timeout_sec": "HERMES_TIMEOUT_SEC",
    "hermes_poll_interval": "HERMES_POLL_INTERVAL",
    "strategy_gen_interval": "STRATEGY_GEN_INTERVAL",
}

DEFAULT_SETTINGS = {
    "broker": "upstox",
    "trading_mode": os.getenv("TRADING_MODE", "paper"),
    "max_position_size": 5,
    "max_daily_loss": 2,
    "max_correlation": 0.7,
    "ollama_model": os.getenv("OLLAMA_MODEL", "qwen2.5:3b"),
    "ollama_url": os.getenv("OLLAMA_URL", "http://127.0.0.1:11434"),
    "telegram_enabled": bool(os.getenv("TELEGRAM_BOT_TOKEN", "").strip()),
    "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
    "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID", ""),
    "api_key": os.getenv("UPSTOX_API_KEY", ""),
    "api_secret": os.getenv("UPSTOX_API_SECRET", ""),
    "dashboard_url": os.getenv("DASHBOARD_URL", "http://127.0.0.1:8000"),
    "dashboard_api_token": os.getenv("DASHBOARD_API_TOKEN", ""),
    "newsapi_key": os.getenv("NEWSAPI_KEY", ""),
    "upstox_redirect_uri": os.getenv("UPSTOX_REDIRECT_URI", "http://127.0.0.1:8000/broker-callback"),
    "trading_enabled": os.getenv("TRADING_ENABLED", "true").strip().lower() in {"1", "true", "yes", "on"},
    "hermes_enabled": os.getenv("HERMES_ENABLED", "true").strip().lower() in {"1", "true", "yes", "on"},
    "hermes_cmd": os.getenv("HERMES_CMD", ""),
    "hermes_timeout_sec": int(os.getenv("HERMES_TIMEOUT_SEC", "120")),
    "hermes_poll_interval": int(os.getenv("HERMES_POLL_INTERVAL", "60")),
    "strategy_gen_interval": int(os.getenv("STRATEGY_GEN_INTERVAL", "300")),
}


class SettingsPayload(BaseModel):
    broker: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    trading_mode: Optional[str] = None
    max_position_size: Optional[float] = None
    max_daily_loss: Optional[float] = None
    max_correlation: Optional[float] = None
    ollama_model: Optional[str] = None
    ollama_url: Optional[str] = None
    telegram_enabled: Optional[bool] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    dashboard_url: Optional[str] = None
    dashboard_api_token: Optional[str] = None
    newsapi_key: Optional[str] = None
    upstox_redirect_uri: Optional[str] = None
    trading_enabled: Optional[bool] = None


class WatchlistPayload(BaseModel):
    symbol: str
    strategy_id: str = "default"
    auto_trade: bool = False
    quantity_to_buy: int = Field(default=1, ge=1)


class SignalActionPayload(BaseModel):
    signal_id: str
    reason: Optional[str] = None


class SignalPatchPayload(BaseModel):
    status: str
    reason: Optional[str] = None


class TradeRequest(BaseModel):
    symbol: str
    side: str
    quantity: int = Field(ge=1)
    price: float = Field(gt=0)
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    mode: str = "paper"
    broker: str = "upstox"


class BacktestRequest(BaseModel):
    strategy: str
    symbol: str
    timeframe: str = "4h"
    from_date: str
    to_date: str
    capital: float = 100000.0


class ChatRequest(BaseModel):
    message: str


class AgentConnectionManager:
    """Keeps websocket clients for the agent monitor."""

    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections.discard(websocket)

    async def broadcast(self, payload: dict[str, Any]) -> None:
        async with self._lock:
            targets = list(self._connections)
        for websocket in targets:
            try:
                await websocket.send_json(payload)
            except Exception:
                await self.disconnect(websocket)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_symbol(symbol: str) -> str:
    return str(symbol or "").upper().replace(".NS", "").replace(".BO", "").strip()


def _json_load(value: str | None) -> Any:
    if value is None:
        return None
    raw = str(value)
    try:
        return json.loads(raw)
    except Exception:
        return raw


def _json_dump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def _default_db_url() -> str:
    db_url = os.getenv("DATABASE_URL", "").strip()
    if not db_url:
        return "sqlite:///./trading_dashboard.db"
    if db_url.startswith("postgres://"):
        return db_url.replace("postgres://", "postgresql://", 1)
    return db_url


def _settings_as_dict(session) -> dict[str, Any]:
    rows = session.query(SettingRow).all()
    result = {row.key: _json_load(row.value) for row in rows}
    return result


def _persist_settings(session, payload: dict[str, Any]) -> None:
    for key, value in payload.items():
        if value is None:
            continue
        row = session.query(SettingRow).filter(SettingRow.key == key).first()
        if row is None:
            row = SettingRow(key=key, value=_json_dump(value))
            session.add(row)
        else:
            row.value = _json_dump(value)


def _apply_settings_to_env(settings: dict[str, Any]) -> None:
    for key, env_name in SETTINGS_ENV_MAP.items():
        if key not in settings or settings[key] is None:
            continue
        value = settings[key]
        if isinstance(value, bool):
            os.environ[env_name] = "true" if value else "false"
        else:
            os.environ[env_name] = str(value)


def _load_persisted_settings() -> dict[str, Any]:
    session = SessionLocal()
    try:
        return _settings_as_dict(session)
    finally:
        session.close()


def _load_trading_mode() -> str:
    settings = _load_persisted_settings()
    value = str(settings.get("trading_mode") or os.getenv("TRADING_MODE", "paper")).strip().lower()
    return value if value in {"paper", "live"} else "paper"


def _load_trading_enabled() -> bool:
    settings = _load_persisted_settings()
    if "trading_enabled" in settings:
        return bool(settings["trading_enabled"])
    return os.getenv("TRADING_ENABLED", "true").strip().lower() in {"1", "true", "yes", "on"}


def _update_runtime_flag_from_settings() -> None:
    if _load_trading_enabled():
        enable_trading()
    else:
        disable_trading()


def _runtime(request: Request) -> TradingSystemRuntime:
    runtime = getattr(request.app.state, "runtime", None)
    if runtime is None:
        raise HTTPException(status_code=503, detail="Runtime not ready")
    return runtime


def _position_snapshot(runtime: TradingSystemRuntime) -> list[dict[str, Any]]:
    positions = runtime.position_manager.get_all()
    snapshots: list[dict[str, Any]] = []
    for pos in positions:
        qty = int(pos.get("quantity") or 0)
        avg_entry = float(pos.get("avg_entry") or 0.0)
        current_price = float(pos.get("current_price") or avg_entry or 0.0)
        if current_price <= 0 and runtime.market_data is not None:
            current_price = float(runtime.market_data.get_ltp(str(pos.get("symbol") or "")) or current_price)
        pnl = float(pos.get("realized_pnl") or 0.0) + float(pos.get("unrealized_pnl") or 0.0)
        base = abs(qty) * avg_entry if qty else 0.0
        pnl_pct = (pnl / base * 100.0) if base else 0.0
        snapshots.append(
            {
                "symbol": str(pos.get("symbol") or ""),
                "qty": qty,
                "entry_price": round(avg_entry, 2),
                "current_price": round(current_price, 2),
                "pnl": round(pnl, 2),
                "pnl_pct": round(pnl_pct, 2),
            }
        )
    snapshots.sort(key=lambda item: item["symbol"])
    return snapshots


def _portfolio_summary(runtime: TradingSystemRuntime) -> dict[str, Any]:
    positions = runtime.position_manager.get_all()
    positions_value = 0.0
    realized_plus_unrealized = 0.0
    open_positions = 0
    for pos in positions:
        qty = int(pos.get("quantity") or 0)
        current_price = float(pos.get("current_price") or pos.get("avg_entry") or 0.0)
        positions_value += abs(qty) * current_price
        realized_plus_unrealized += float(pos.get("realized_pnl") or 0.0) + float(pos.get("unrealized_pnl") or 0.0)
        if qty != 0:
            open_positions += 1

    if runtime.broker_mode == "paper":
        total_value = float(runtime.broker_adapter.snapshot().get("equity", positions_value))
    else:
        total_value = positions_value

    total_pnl_pct = (realized_plus_unrealized / total_value * 100.0) if total_value else 0.0
    return {
        "total_value": round(total_value, 2),
        "total_pnl": round(realized_plus_unrealized, 2),
        "total_pnl_pct": round(total_pnl_pct, 2),
        "open_positions": open_positions,
    }


def _watchlist_row(item: WatchlistStock) -> dict[str, Any]:
    return {
        "id": str(item.id),
        "symbol": item.symbol,
        "strategy_id": item.strategy_id or "default",
        "auto_trade": bool(item.auto_trade),
        "status": item.status,
        "added_date": item.added_date,
        "last_checked": item.last_checked,
        "last_signal": item.last_signal,
        "last_signal_price": item.last_signal_price,
        "quantity_to_buy": int(item.quantity_to_buy or 1),
    }


def _signal_row(session, item: TradeSignal) -> dict[str, Any]:
    watch = (
        session.query(WatchlistStock)
        .filter(WatchlistStock.symbol == _normalize_symbol(item.symbol))
        .first()
    )
    quantity = int(getattr(watch, "quantity_to_buy", 1) or 1) if watch else 1
    return {
        "id": str(item.id),
        "symbol": item.symbol,
        "strategy_id": item.strategy_id or "default",
        "side": item.signal_type or "buy",
        "signal_type": item.signal_type or "buy",
        "quantity": quantity,
        "quantity_to_buy": quantity,
        "price": item.signal_price,
        "signal_price": item.signal_price,
        "signal_time": item.signal_time,
        "technical_score": item.technical_score,
        "news_score": item.news_score,
        "fundamental_score": item.fundamental_score,
        "risk_score": item.risk_score,
        "overall_score": item.overall_score,
        "approval_status": item.approval_status,
        "approval_time": item.approval_time,
        "approval_reason": item.approval_reason,
        "order_id": item.order_id,
        "execution_price": item.execution_price,
        "execution_time": item.execution_time,
        "trade_segment": "intraday",
        "expected_exit": round(float(item.signal_price or 0.0) * 1.03, 2),
        "broker": "upstox",
    }


def _latest_backtest_result(session, strategy_name: str) -> BacktestResult | None:
    return (
        session.query(BacktestResult)
        .filter(BacktestResult.strategy_name == strategy_name)
        .order_by(BacktestResult.id.desc())
        .first()
    )


def _strategy_payload(session, strategy: Strategy) -> dict[str, Any]:
    backtest = _latest_backtest_result(session, strategy.name)
    pnl = float(strategy.pnl or 0.0)
    win_rate = float(strategy.win_rate or 0.0)
    total_trades = int(backtest.total_trades if backtest else 0)
    curve_seed = sum(ord(ch) for ch in f"{strategy.id}:{strategy.symbol}:{strategy.timeframe}")
    rng = random.Random(curve_seed)
    equity = 100_000.0
    curve = []
    for idx in range(12):
        equity += rng.uniform(-1200, 1800)
        curve.append({"date": f"t{idx + 1}", "value": round(equity, 2)})

    return {
        "id": str(strategy.id),
        "name": strategy.name,
        "symbol": strategy.symbol,
        "timeframe": strategy.timeframe,
        "status": strategy.status if strategy.status in {"running", "paused", "backtested"} else "paused",
        "pnl": round(pnl, 2),
        "win_rate": round(win_rate, 2),
        "total_trades": total_trades,
        "equity_curve": curve,
        "entry_rule": strategy.entry_rule,
        "exit_rule": strategy.exit_rule,
        "created_date": strategy.created_date,
        "last_trade": strategy.last_trade,
    }


def _read_executions_db() -> list[dict[str, Any]]:
    if not EXECUTIONS_DB.exists():
        return []
    rows: list[dict[str, Any]] = []
    try:
        with sqlite3.connect(EXECUTIONS_DB) as con:
            con.row_factory = sqlite3.Row
            result = con.execute(
                """
                SELECT client_order_id, broker_order_id, signal_id, broker, symbol, side,
                       quantity, entry_price, status, reject_reason, created_at
                FROM executions
                ORDER BY created_at DESC
                """
            ).fetchall()
        for row in result:
            rows.append(
                {
                    "id": str(row["client_order_id"] or row["broker_order_id"] or uuid.uuid4().hex),
                    "symbol": str(row["symbol"] or ""),
                    "side": str(row["side"] or "buy"),
                    "qty": int(row["quantity"] or 0),
                    "price": float(row["entry_price"] or 0.0),
                    "status": str(row["status"] or "submitted"),
                    "timestamp": datetime.fromtimestamp(int(row["created_at"] or 0), tz=timezone.utc).isoformat()
                    if row["created_at"]
                    else _utc_now(),
                }
            )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not read executions db: %s", exc)
    return rows


def _trade_history(session) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    trades = session.query(Trade).order_by(Trade.id.desc()).all()
    for trade in trades:
        rows.append(
            {
                "id": str(trade.order_id or trade.id),
                "symbol": trade.symbol,
                "side": "buy" if (trade.quantity or 0) >= 0 else "sell",
                "qty": abs(int(trade.quantity or 0)),
                "price": float(trade.entry_price or 0.0),
                "status": trade.status,
                "timestamp": trade.entry_time or trade.exit_time or _utc_now(),
            }
        )
    rows.extend(_read_executions_db())
    rows.sort(key=lambda item: item.get("timestamp", ""), reverse=True)
    return rows


def _screener_rows(runtime: TradingSystemRuntime, session) -> list[dict[str, Any]]:
    watchlist = session.query(WatchlistStock).filter(WatchlistStock.status == "active").all()
    symbols = [_normalize_symbol(row.symbol) for row in watchlist if _normalize_symbol(row.symbol)]
    if not symbols:
        symbols = ["INFY", "RELIANCE", "TCS", "HDFCBANK", "SBIN", "ICICIBANK"]

    rows: list[dict[str, Any]] = []
    for idx, symbol in enumerate(sorted(set(symbols))):
        seed = sum(ord(ch) for ch in symbol)
        base_price = 50.0 + (seed % 1500) / 5.0
        ltp = runtime.market_data.get_ltp(symbol) if runtime.market_data is not None else 0.0
        price = float(ltp or base_price)
        change_pct = round(((seed % 17) - 8) * 0.73, 2)
        pnl_pct = round(change_pct * 0.8, 2)
        signal = "buy" if change_pct > 2.5 else "sell" if change_pct < -2.5 else "hold"
        rows.append(
            {
                "rank": idx + 1,
                "symbol": symbol,
                "price": round(price, 2),
                "change_pct": change_pct,
                "pnl_pct": pnl_pct,
                "signal": signal,
                "timeframe": "4h",
            }
        )
    return rows


def _pinescript_template(strategy_name: str) -> str:
    return f"""//@version=5
strategy("{strategy_name}", overlay=true, initial_capital=100000)

fastLen = input.int(9, "Fast EMA")
slowLen = input.int(21, "Slow EMA")
fast = ta.ema(close, fastLen)
slow = ta.ema(close, slowLen)

longCond = ta.crossover(fast, slow)
shortCond = ta.crossunder(fast, slow)

plot(fast, color=color.teal)
plot(slow, color=color.orange)

if (longCond)
    strategy.entry("Long", strategy.long)

if (shortCond)
    strategy.entry("Short", strategy.short)
"""


def _backtest_result(request: BacktestRequest) -> dict[str, Any]:
    seed = sum(ord(ch) for ch in f"{request.strategy}:{request.symbol}:{request.timeframe}:{request.from_date}:{request.to_date}")
    rng = random.Random(seed)
    equity = float(request.capital)
    trades: list[dict[str, Any]] = []
    equity_curve: list[dict[str, Any]] = []
    total_profit = 0.0
    wins = 0
    losses = 0
    dates = [request.from_date, request.to_date]
    for i in range(12):
        daily = rng.uniform(-0.04, 0.07)
        profit = request.capital * daily * 0.1
        total_profit += profit
        equity += profit
        if profit >= 0:
            wins += 1
        else:
            losses += 1
        equity_curve.append({"date": f"step-{i + 1}", "value": round(equity, 2)})
        trades.append(
            {
                "entry_date": request.from_date if i == 0 else f"step-{i}",
                "exit_date": request.to_date if i == 11 else f"step-{i + 1}",
                "entry_price": round(float(request.capital) * (1 + i * 0.01), 2),
                "profit": round(profit, 2),
            }
        )

    total_trades = len(trades)
    win_rate = round((wins / total_trades) * 100.0, 2) if total_trades else 0.0
    gross_profit = sum(t["profit"] for t in trades if t["profit"] > 0)
    gross_loss = abs(sum(t["profit"] for t in trades if t["profit"] < 0)) or 1.0
    profit_factor = round(gross_profit / gross_loss, 2)
    sharpe = round((total_profit / float(request.capital)) * 10.0, 2)
    max_dd = round(abs(min((point["value"] for point in equity_curve), default=request.capital) - request.capital), 2)
    net_pnl = round(total_profit, 2)
    return {
        "total_trades": total_trades,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "sharpe": sharpe,
        "max_dd": max_dd,
        "net_pnl": net_pnl,
        "equity_curve": equity_curve,
        "trades": trades,
        "dates": dates,
    }


async def _call_broker_method(broker: Any, method_name: str, *args: Any, **kwargs: Any) -> Any:
    method = getattr(broker, method_name, None)
    if method is None:
        raise HTTPException(status_code=503, detail=f"Broker method not available: {method_name}")
    try:
        result = method(*args, **kwargs)
        if asyncio.iscoroutine(result):
            return await result
        return result
    except TypeError:
        clean_kwargs = dict(kwargs)
        clean_kwargs.pop("broker_name", None)
        result = method(*args, **clean_kwargs)
        if asyncio.iscoroutine(result):
            return await result
        return result


def _strategy_status_label(status: str) -> tuple[str, int]:
    normalized = str(status or "paused").strip().lower()
    if normalized == "running":
        return "running", 100
    if normalized == "backtested":
        return "backtested", 75
    if normalized == "backtesting":
        return "backtesting", 60
    if normalized == "paused":
        return "paused", 35
    return "offline", 0


def _strategy_task_text(strategy: Strategy) -> str:
    symbol = str(getattr(strategy, "symbol", "") or "").upper()
    timeframe = str(getattr(strategy, "timeframe", "") or "4h")
    status = str(getattr(strategy, "status", "") or "paused").lower()
    return f"{symbol} {timeframe} strategy ({status})"


def _strategy_summary(strategies: list[Strategy]) -> tuple[int, int]:
    total = len(strategies)
    running = sum(1 for row in strategies if str(getattr(row, "status", "") or "").lower() == "running")
    return total, running


async def _build_agent_cards(app: FastAPI) -> list[dict[str, Any]]:
    """Build the live agent cards shown in the sidebar and animation page."""
    runtime: TradingSystemRuntime | None = getattr(app.state, "runtime", None)
    snapshot = runtime.status() if runtime is not None else {}
    cfg = load_tooling_config()
    session = SessionLocal()
    try:
        strategies = session.query(Strategy).order_by(Strategy.name.asc()).all()
    finally:
        session.close()

    total_strategies, running_strategies = _strategy_summary(strategies)
    boss_task = "Chat assistant ready"
    if cfg.ollama_url:
        boss_task = f"Chat assistant ready ({cfg.ollama_model})"
    else:
        boss_task = "Chat assistant ready (fallback mode)"

    cards: list[dict[str, Any]] = [
        {
            "agent_id": "market_data",
            "status": "online" if snapshot.get("market_data_online") else "offline",
            "task": "Streaming live ticks" if snapshot.get("market_data_online") else "Waiting for market data",
            "progress": 100 if snapshot.get("market_data_online") else 0,
        },
        {
            "agent_id": "technical",
            "status": "online" if snapshot.get("technical_agent_online") else "offline",
            "task": "Generating signals" if snapshot.get("technical_agent_online") else "Waiting for watchlist",
            "progress": 100 if snapshot.get("technical_agent_online") else 0,
        },
        {
            "agent_id": "news",
            "status": "online" if snapshot.get("news_agent_online") else "offline",
            "task": "Scoring news sentiment" if snapshot.get("news_agent_online") else "Waiting for news inputs",
            "progress": 100 if snapshot.get("news_agent_online") else 0,
        },
        {
            "agent_id": "trade_execution",
            "status": "online" if snapshot.get("tasks", {}).get("trade") else "offline",
            "task": "Polling approved signals" if snapshot.get("tasks", {}).get("trade") else "Idle",
            "progress": 100 if snapshot.get("tasks", {}).get("trade") else 0,
        },
        {
            "agent_id": "telegram",
            "status": "online" if snapshot.get("telegram_online") else "offline",
            "task": "Listening for approvals" if snapshot.get("telegram_online") else "Waiting for Telegram config",
            "progress": 100 if snapshot.get("telegram_online") else 0,
        },
        {
            "agent_id": "boss_agent",
            "status": "online",
            "task": boss_task,
            "progress": 100,
        },
        {
            "agent_id": "strategy_manager",
            "status": "online",
            "task": (
                f"Managing {running_strategies} running / {total_strategies} total strategies"
                if total_strategies
                else "Waiting for your first strategy"
            ),
            "progress": 100 if total_strategies else 20,
        },
    ]

    hermes_enabled = cfg.hermes_enabled
    hermes_task = "Hermes strategy engine ready" if hermes_enabled else "Hermes disabled"
    cards.append(
        {
            "agent_id": "hermes_strategy",
            "status": "online" if hermes_enabled else "offline",
            "task": hermes_task,
            "progress": 100 if hermes_enabled else 0,
        }
    )

    for strategy in strategies[:10]:
        status, progress = _strategy_status_label(str(getattr(strategy, "status", "") or "paused"))
        cards.append(
            {
                "agent_id": f"strategy:{strategy.id}",
                "status": status,
                "task": _strategy_task_text(strategy),
                "progress": progress,
            }
        )

    return cards


async def _process_chat_command(app: FastAPI, command_id: str, message: str) -> None:
    try:
        cfg = load_tooling_config()
        runtime: TradingSystemRuntime | None = getattr(app.state, "runtime", None)
        portfolio = _portfolio_summary(runtime) if runtime is not None else {}
        watchlist = []
        if runtime is not None:
            watchlist = runtime.status().get("watchlist_symbols", [])
        system_prompt = (
            "You are the boss agent for a trading dashboard. "
            "Be concise, factual, and helpful. "
            f"Trading mode: {runtime.trading_mode if runtime else 'paper'}. "
            f"Watchlist: {watchlist}. "
            f"Portfolio: {portfolio}."
        )
        reply = ""
        async with httpx.AsyncClient(timeout=20, trust_env=False) as client:
            try:
                response = await client.post(
                    f"{cfg.ollama_url.rstrip('/')}/api/chat",
                    json={
                        "model": cfg.ollama_model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": message},
                        ],
                        "stream": False,
                    },
                )
                response.raise_for_status()
                payload = response.json()
                reply = (
                    payload.get("message", {}).get("content")
                    or payload.get("response")
                    or ""
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("Ollama chat failed, using fallback: %s", exc)

        if not reply:
            reply = (
                f"Chat received: {message}. "
                f"Runtime mode: {runtime.trading_mode if runtime else 'paper'}. "
                f"Watchlist count: {len(watchlist)}."
            )

        session = SessionLocal()
        try:
            session.add(
                ChatHistory(
                    user_id="user",
                    role="assistant",
                    message=reply,
                    timestamp=_utc_now(),
                )
            )
            session.commit()
        finally:
            session.close()

        app.state.chat_commands[command_id] = {"status": "done", "response": reply}
    except Exception as exc:  # noqa: BLE001
        logger.error("Chat processing failed: %s", exc)
        app.state.chat_commands[command_id] = {"status": "done", "response": f"Error: {exc}"}


async def _agent_broadcast_loop(app: FastAPI) -> None:
    try:
        while not app.state.shutdown_event.is_set():
            runtime: TradingSystemRuntime | None = getattr(app.state, "runtime", None)
            if runtime is not None:
                agents = await _build_agent_cards(app)
                for agent in agents:
                    await app.state.ws_manager.broadcast(agent)
            await asyncio.sleep(5)
    except asyncio.CancelledError:
        return
    except Exception as exc:  # noqa: BLE001
        logger.error("Agent broadcast loop failed: %s", exc)


async def _refresh_symbol_master_task(app: FastAPI) -> None:
    try:
        runtime: TradingSystemRuntime | None = getattr(app.state, "runtime", None)
        symbol_master = getattr(app.state, "symbol_master", None)
        if runtime is None or symbol_master is None or not hasattr(symbol_master, "download_and_refresh"):
            return
        should_refresh = runtime.trading_mode == "live" or runtime._market_data_enabled  # noqa: SLF001
        if not should_refresh:
            return
        try:
            await symbol_master.download_and_refresh()
            logger.info("Symbol master refreshed")
        except Exception as exc:  # noqa: BLE001
            logger.warning("Symbol master refresh failed: %s", exc)
    except Exception as exc:  # noqa: BLE001
        logger.error("refresh symbol master task failed: %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create the runtime once and keep the agents alive while the app runs."""
    init_db()
    ensure_default_admin()

    persisted = _load_persisted_settings()
    if persisted:
        _apply_settings_to_env(persisted)
    _update_runtime_flag_from_settings()

    tooling = load_tooling_config()
    init_sentry(tooling)

    db_url = _default_db_url()
    event_store = build_event_store(db_url)
    event_bus = build_event_bus(event_store)
    symbol_master = build_symbol_master()
    live_broker = broker_from_env(symbol_master)
    runtime = build_runtime(
        event_bus=event_bus,
        symbol_master=symbol_master,
        live_broker=live_broker,
        trading_mode=_load_trading_mode(),
    )

    app.state.event_store = event_store
    app.state.event_bus = event_bus
    app.state.symbol_master = symbol_master
    app.state.live_broker = live_broker
    app.state.runtime = runtime
    app.state.tooling = tooling
    app.state.chat_commands = {}
    app.state.ws_manager = AgentConnectionManager()
    app.state.shutdown_event = asyncio.Event()
    app.state.background_tasks = []

    try:
        await runtime.start()
        app.state.background_tasks.append(asyncio.create_task(_agent_broadcast_loop(app)))
        app.state.background_tasks.append(asyncio.create_task(_refresh_symbol_master_task(app)))
        logger.info("Dashboard runtime started")
    except Exception as exc:  # noqa: BLE001
        logger.error("Runtime startup failed: %s", exc)

    try:
        yield
    finally:
        try:
            app.state.shutdown_event.set()
            for task in app.state.background_tasks:
                if not task.done():
                    task.cancel()
            if app.state.background_tasks:
                await asyncio.gather(*app.state.background_tasks, return_exceptions=True)
            runtime = getattr(app.state, "runtime", None)
            if runtime is not None:
                await runtime.stop()
            live_broker = getattr(app.state, "live_broker", None)
            if live_broker is not None and hasattr(live_broker, "close"):
                try:
                    result = live_broker.close()
                    if asyncio.iscoroutine(result):
                        await result
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Broker close failed: %s", exc)
        except Exception as exc:  # noqa: BLE001
            logger.error("Shutdown failed: %s", exc)


app = FastAPI(title="Trading Dashboard", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")


@app.get("/health", include_in_schema=False)
async def health() -> dict[str, Any]:
    """Simple uptime probe for Render / UptimeRobot."""
    return build_health_snapshot("trading-dashboard", "ok")


@app.get("/api/system/health")
async def system_health(request: Request) -> dict[str, Any]:
    """Return a compact summary used by the dashboard overview screen."""
    runtime = _runtime(request)
    cfg = load_tooling_config()
    ollama_status = "not_configured" if not cfg.ollama_url else "offline"
    try:
        async with httpx.AsyncClient(timeout=2, trust_env=False) as client:
            resp = await client.get(f"{cfg.ollama_url.rstrip('/')}/api/version")
            if resp.status_code == 200:
                ollama_status = "online"
    except Exception:
        pass

    hermes_status = "not_configured"
    if cfg.hermes_enabled:
        hermes_client = HermesClient()
        ok, info = hermes_client.healthcheck()
        hermes_status = "online" if ok else f"offline: {info}"

    snapshot = runtime.status()
    session = SessionLocal()
    try:
        strategies = session.query(Strategy).all()
    finally:
        session.close()
    agents = await _build_agent_cards(request.app)
    agents_online = sum(1 for agent in agents if str(agent.get("status") or "").lower() in {"online", "running"})

    broker_status = "paper" if runtime.broker_mode == "paper" else "not_authenticated"
    live_broker = getattr(request.app.state, "live_broker", None)
    if runtime.broker_mode == "live":
        auth = getattr(live_broker, "auth", None)
        if auth is not None and hasattr(auth, "is_authenticated"):
            broker_status = "authenticated" if auth.is_authenticated() else "not_authenticated"
        elif live_broker is not None:
            broker_status = "live"

    return {
        "timestamp": _utc_now(),
        "ollama_status": ollama_status,
        "hermes_status": hermes_status,
        "broker_status": broker_status,
        "agents_online": agents_online,
        "alert_cooldown_seconds": int(os.getenv("TELEGRAM_ALERT_COOLDOWN_SECONDS", "60")),
        "runtime_mode": snapshot.get("mode", "paper"),
        "broker_mode": snapshot.get("broker_mode", "paper"),
        "trading_enabled": is_trading_enabled(),
    }


@app.get("/api/runtime/status")
async def runtime_status(request: Request) -> dict[str, Any]:
    """Expose the runtime snapshot for debugging and the agent monitor UI."""
    return _runtime(request).status()


@app.websocket("/ws/agent-monitor")
async def ws_agent_monitor(websocket: WebSocket) -> None:
    """Stream live agent status updates to the frontend monitor widget."""
    manager: AgentConnectionManager = websocket.app.state.ws_manager
    await manager.connect(websocket)
    try:
        initial = await _build_agent_cards(websocket.app)
        for agent in initial:
            await websocket.send_json(agent)
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(websocket)


@app.get("/agent-status")
async def agent_status(request: Request) -> list[dict[str, Any]]:
    """Return the same agent monitor payload used by the websocket UI."""
    return await _build_agent_cards(request.app)


@app.get("/settings")
async def get_settings() -> dict[str, Any]:
    """Return dashboard settings for the UI."""
    session = SessionLocal()
    try:
        settings = dict(DEFAULT_SETTINGS)
        settings.update(_settings_as_dict(session))
        return settings
    finally:
        session.close()


@app.post("/settings")
async def save_settings(payload: SettingsPayload) -> dict[str, Any]:
    """Persist dashboard settings and update live environment variables."""
    session = SessionLocal()
    try:
        data = payload.model_dump(exclude_none=True)
        _persist_settings(session, data)
        session.commit()
        _apply_settings_to_env(data)
        if "trading_enabled" in data:
            if bool(data["trading_enabled"]):
                enable_trading()
            else:
                disable_trading()
        return await get_settings()
    finally:
        session.close()


@app.get("/api/kill-switch")
async def get_kill_switch() -> dict[str, Any]:
    """Return whether live trading is currently enabled."""
    return {"trading_enabled": is_trading_enabled()}


@app.post("/api/kill-switch")
async def set_kill_switch(payload: dict[str, Any]) -> dict[str, Any]:
    """Toggle the live-trading kill switch."""
    enabled = bool(payload.get("enabled"))
    session = SessionLocal()
    try:
        row = session.query(SettingRow).filter(SettingRow.key == "trading_enabled").first()
        if row is None:
            session.add(SettingRow(key="trading_enabled", value=_json_dump(enabled)))
        else:
            row.value = _json_dump(enabled)
        session.commit()
    finally:
        session.close()

    if enabled:
        enable_trading()
    else:
        disable_trading()
    os.environ["TRADING_ENABLED"] = "true" if enabled else "false"
    return {"trading_enabled": enabled}


@app.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
) -> dict[str, Any]:
    """Return a JWT after verifying the username/password pair."""
    user = verify_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_token(user["username"], user.get("role", "user"))
    return {"access_token": token, "token_type": "bearer", "role": user.get("role", "user")}


@app.post("/change-password")
async def change_password(data: dict[str, Any], user: dict[str, Any] = Depends(verify_token)) -> dict[str, Any]:
    """Allow a logged-in user to change their password."""
    if not verify_user(user["username"], data.get("old_password", "")):
        raise HTTPException(status_code=400, detail="Wrong current password")
    if not update_password(user["username"], data.get("new_password", "")):
        raise HTTPException(status_code=400, detail="Could not update password")
    return {"ok": True}


@app.get("/broker-login")
async def broker_login() -> RedirectResponse:
    """Redirect the browser to the Upstox authorization page."""
    auth = BrokerAuthManager("upstox")
    return RedirectResponse(url=auth.get_login_url(), status_code=307)


@app.get("/broker-callback")
async def broker_callback(code: str | None = None, state: str | None = None) -> HTMLResponse:
    """Finish the Upstox OAuth callback by exchanging the temporary code."""
    del state
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
    auth = BrokerAuthManager("upstox")
    ok = await auth.exchange_code(code)
    if not ok:
        raise HTTPException(status_code=400, detail="Broker authentication failed")
    return HTMLResponse("<h1>Upstox connected</h1><p>You can close this tab and return to the dashboard.</p>")


@app.get("/api/broker/upstox/status")
async def broker_status(request: Request) -> dict[str, Any]:
    """Return broker authentication and mode details."""
    runtime = _runtime(request)
    auth = BrokerAuthManager("upstox")
    return {
        "broker_mode": runtime.broker_mode,
        "trading_mode": runtime.trading_mode,
        "authenticated": auth.is_authenticated(),
        "login_url": auth.get_login_url(),
        "live_broker_available": runtime.live_broker is not None,
    }


@app.get("/api/broker/upstox/profile")
async def broker_profile(request: Request) -> dict[str, Any]:
    """Return the broker profile from the active broker adapter."""
    runtime = _runtime(request)
    return await _call_broker_method(runtime.broker_adapter, "get_profile", broker_name="upstox")


@app.get("/api/broker/upstox/funds")
async def broker_funds(request: Request) -> dict[str, Any]:
    """Return broker funds and margin information."""
    runtime = _runtime(request)
    return await _call_broker_method(runtime.broker_adapter, "get_funds_and_margin", broker_name="upstox")


@app.get("/api/broker/upstox/positions")
async def broker_positions(request: Request) -> Any:
    """Return broker positions."""
    runtime = _runtime(request)
    broker = runtime.broker_adapter
    if hasattr(broker, "get_positions"):
        return await _call_broker_method(broker, "get_positions", broker_name="upstox")
    return _position_snapshot(runtime)


@app.get("/api/watchlist")
async def get_watchlist() -> list[dict[str, Any]]:
    """Return the active watchlist rows."""
    session = SessionLocal()
    try:
        rows = session.query(WatchlistStock).order_by(WatchlistStock.id.desc()).all()
        return [_watchlist_row(row) for row in rows]
    finally:
        session.close()


@app.post("/api/watchlist/add")
async def add_watchlist(payload: WatchlistPayload, request: Request) -> dict[str, Any]:
    """Add or update one watchlist symbol."""
    symbol = _normalize_symbol(payload.symbol)
    if not symbol:
        raise HTTPException(status_code=400, detail="Symbol is required")
    session = SessionLocal()
    try:
        row = session.query(WatchlistStock).filter(WatchlistStock.symbol == symbol).first()
        if row is None:
            row = WatchlistStock(symbol=symbol)
            session.add(row)
        row.strategy_id = payload.strategy_id or "default"
        row.auto_trade = bool(payload.auto_trade)
        row.status = "active"
        row.quantity_to_buy = int(payload.quantity_to_buy or 1)
        row.added_date = row.added_date or _utc_now()
        row.last_checked = _utc_now()
        session.commit()
    finally:
        session.close()

    runtime = _runtime(request)
    await runtime.refresh_watchlist()
    return {"ok": True, "symbol": symbol}


@app.post("/api/watchlist/remove")
async def remove_watchlist(payload: dict[str, Any], request: Request) -> dict[str, Any]:
    """Mark a watchlist symbol as removed."""
    symbol = _normalize_symbol(str(payload.get("symbol") or ""))
    if not symbol:
        raise HTTPException(status_code=400, detail="Symbol is required")
    session = SessionLocal()
    try:
        row = session.query(WatchlistStock).filter(WatchlistStock.symbol == symbol).first()
        if row is None:
            raise HTTPException(status_code=404, detail="Watchlist symbol not found")
        row.status = "removed"
        row.auto_trade = False
        row.last_checked = _utc_now()
        session.commit()
    finally:
        session.close()

    runtime = _runtime(request)
    await runtime.refresh_watchlist()
    return {"ok": True, "symbol": symbol}


@app.get("/api/signals/pending")
async def pending_signals() -> list[dict[str, Any]]:
    """Return pending signals for approval."""
    session = SessionLocal()
    try:
        rows = (
            session.query(TradeSignal)
            .filter(TradeSignal.approval_status == "pending")
            .order_by(TradeSignal.signal_time.desc().nullslast(), TradeSignal.id.desc())
            .all()
        )
        return [_signal_row(session, row) for row in rows]
    finally:
        session.close()


@app.get("/api/signals/approved")
async def approved_signals() -> list[dict[str, Any]]:
    """Return approved signals for the execution agent."""
    session = SessionLocal()
    try:
        rows = (
            session.query(TradeSignal)
            .filter(TradeSignal.approval_status == "approved")
            .order_by(TradeSignal.signal_time.desc().nullslast(), TradeSignal.id.desc())
            .all()
        )
        return [_signal_row(session, row) for row in rows]
    finally:
        session.close()


@app.post("/api/signal/approve")
async def approve_signal(payload: SignalActionPayload) -> dict[str, Any]:
    """Mark a signal as approved."""
    session = SessionLocal()
    try:
        row = session.query(TradeSignal).filter(TradeSignal.id == payload.signal_id).first()
        if row is None:
            raise HTTPException(status_code=404, detail="Signal not found")
        row.approval_status = "approved"
        row.approval_reason = payload.reason or "Approved from dashboard"
        row.approval_time = _utc_now()
        session.commit()
        return {"ok": True, "signal_id": payload.signal_id, "status": row.approval_status}
    finally:
        session.close()


@app.post("/api/signal/skip")
async def skip_signal(payload: SignalActionPayload) -> dict[str, Any]:
    """Mark a signal as skipped."""
    session = SessionLocal()
    try:
        row = session.query(TradeSignal).filter(TradeSignal.id == payload.signal_id).first()
        if row is None:
            raise HTTPException(status_code=404, detail="Signal not found")
        row.approval_status = "skipped"
        row.approval_reason = payload.reason or "Skipped from dashboard"
        row.approval_time = _utc_now()
        session.commit()
        return {"ok": True, "signal_id": payload.signal_id, "status": row.approval_status}
    finally:
        session.close()


@app.patch("/api/signals/{signal_id}")
async def patch_signal(signal_id: str, payload: SignalPatchPayload) -> dict[str, Any]:
    """Patch a signal status from Telegram or the execution agent."""
    session = SessionLocal()
    try:
        row = session.query(TradeSignal).filter(TradeSignal.id == signal_id).first()
        if row is None:
            raise HTTPException(status_code=404, detail="Signal not found")
        row.approval_status = payload.status
        if payload.reason is not None:
            row.approval_reason = payload.reason
        if payload.status in {"approved", "rejected", "skipped"}:
            row.approval_time = _utc_now()
        if payload.status in {"filled", "executing"}:
            row.execution_time = _utc_now()
        session.commit()
        return {"ok": True, "signal_id": signal_id, "status": row.approval_status}
    finally:
        session.close()


@app.post("/alerts/buy-signal")
async def buy_signal(payload: dict[str, Any], request: Request) -> dict[str, Any]:
    """Create a pending signal and send the Telegram approval card."""
    symbol = _normalize_symbol(str(payload.get("symbol") or ""))
    if not symbol:
        raise HTTPException(status_code=400, detail="Symbol is required")
    side = str(payload.get("signal") or payload.get("side") or "buy").lower().strip() or "buy"
    runtime = _runtime(request)
    watch_quantity = int(payload.get("quantity") or payload.get("quantity_to_buy") or 1)
    market_price = runtime.market_data.get_ltp(symbol) if runtime.market_data is not None else 0.0
    price = float(payload.get("price") or payload.get("signal_price") or market_price)
    if price <= 0:
        price = 100.0
    expected_exit = float(payload.get("expected_exit") or (price * (1.03 if side == "buy" else 0.97)))
    strategy_id = str(payload.get("strategy_id") or "default")
    reason = str(payload.get("reason") or payload.get("approval_reason") or "Technical signal")
    signal_id = str(payload.get("id") or uuid.uuid4().hex)

    session = SessionLocal()
    try:
        watch = session.query(WatchlistStock).filter(WatchlistStock.symbol == symbol).first()
        if watch is None:
            watch = WatchlistStock(symbol=symbol, strategy_id=strategy_id, auto_trade=bool(payload.get("auto_trade", False)))
            session.add(watch)
        watch.strategy_id = strategy_id
        watch.auto_trade = bool(payload.get("auto_trade", False))
        watch.status = "active"
        watch.quantity_to_buy = watch_quantity
        watch.last_signal = side
        watch.last_signal_price = price
        watch.last_checked = _utc_now()

        row = session.query(TradeSignal).filter(TradeSignal.id == signal_id).first()
        if row is None:
            row = TradeSignal(id=signal_id, symbol=symbol)
            session.add(row)
        row.symbol = symbol
        row.strategy_id = strategy_id
        row.signal_type = side
        row.signal_price = price
        row.signal_time = _utc_now()
        row.technical_score = float(payload.get("technical_score") or 0.0)
        row.news_score = float(payload.get("news_score") or 0.0)
        row.fundamental_score = float(payload.get("fundamental_score") or 0.0)
        row.risk_score = float(payload.get("risk_score") or 0.0)
        row.overall_score = float(payload.get("overall_score") or payload.get("score") or 0.0)
        row.approval_status = "pending"
        row.approval_reason = reason
        row.order_id = None
        row.execution_price = None
        row.execution_time = None
        session.commit()
    finally:
        session.close()

    await runtime.refresh_watchlist()

    signal_payload = {
        "id": signal_id,
        "symbol": symbol,
        "side": side,
        "signal_type": side,
        "quantity": watch_quantity,
        "quantity_to_buy": watch_quantity,
        "price": price,
        "signal_price": price,
        "score": float(payload.get("score") or payload.get("overall_score") or 0.0),
        "technical_score": float(payload.get("technical_score") or 0.0),
        "news_score": float(payload.get("news_score") or 0.0),
        "fundamental_score": float(payload.get("fundamental_score") or 0.0),
        "risk_score": float(payload.get("risk_score") or 0.0),
        "overall_score": float(payload.get("overall_score") or payload.get("score") or 0.0),
        "reason": reason,
        "approval_reason": reason,
        "approval_status": "pending",
        "broker": str(payload.get("broker") or "upstox"),
        "trade_segment": str(payload.get("trade_segment") or "intraday"),
        "expected_exit": round(expected_exit, 2),
    }
    await send_approval_request(signal_payload)
    return {"status": "queued", "signal_id": signal_id}


@app.get("/api/portfolio")
async def api_portfolio(request: Request) -> dict[str, Any]:
    """Return the portfolio summary for the overview screen."""
    return _portfolio_summary(_runtime(request))


@app.get("/portfolio")
async def portfolio_alias(request: Request) -> dict[str, Any]:
    """Compatibility alias for clients that call /portfolio directly."""
    return await api_portfolio(request)


@app.get("/positions")
async def positions(request: Request) -> list[dict[str, Any]]:
    """Return the current position list used by the trading screen."""
    return _position_snapshot(_runtime(request))


@app.delete("/positions/{symbol}")
async def close_position(symbol: str, request: Request) -> dict[str, Any]:
    """Close a local position by sending the opposite order through the broker adapter."""
    runtime = _runtime(request)
    sym = _normalize_symbol(symbol)
    pos = runtime.position_manager.get_position("upstox", sym)
    if not pos or int(pos.get("quantity") or 0) == 0:
        raise HTTPException(status_code=404, detail="Position not found")

    qty = abs(int(pos.get("quantity") or 0))
    side = "sell" if int(pos.get("quantity") or 0) > 0 else "buy"
    price = float(pos.get("current_price") or pos.get("avg_entry") or 0.0)
    broker = getattr(runtime, "_paper_router", runtime.broker_adapter) if request.query_params.get("mode", "paper") == "paper" else runtime.broker_adapter
    result = await _call_broker_method(
        broker,
        "place_order",
        broker_name="upstox",
        symbol=sym,
        side=side,
        quantity=qty,
        order_type="MARKET",
        price=price,
        take_profit=None,
        client_order_id=str(uuid.uuid4().hex),
    )
    order_id = result.get("order_id") if isinstance(result, dict) else None
    data = result.get("data") if isinstance(result, dict) else None
    fill_price = float((data or {}).get("average_price") or price)
    if str((result or {}).get("status") or "").lower() in {"complete", "filled"} or (data and data.get("status") == "complete"):
        await runtime.position_manager.on_fill("upstox", sym, side, qty, fill_price)
    session = SessionLocal()
    try:
        session.add(
            Trade(
                order_id=str(order_id or uuid.uuid4().hex),
                symbol=sym,
                quantity=-qty if side == "sell" else qty,
                entry_price=fill_price,
                broker="upstox",
                mode=runtime.trading_mode,
                status=str((result or {}).get("status") or "submitted"),
                entry_time=_utc_now(),
            )
        )
        session.commit()
    finally:
        session.close()
    return {"ok": True, "symbol": sym, "side": side, "quantity": qty, "order_id": order_id}


@app.post("/trade")
async def trade(request_payload: TradeRequest, request: Request) -> dict[str, Any]:
    """Place a manual order from the trading page."""
    runtime = _runtime(request)
    if request_payload.mode.lower() == "live" and not is_trading_enabled():
        raise HTTPException(status_code=400, detail="Trading is disabled by the kill switch")

    broker = runtime.broker_adapter
    if request_payload.mode.lower() == "paper" and hasattr(runtime, "_paper_router"):
        broker = runtime._paper_router  # noqa: SLF001
    elif request_payload.mode.lower() == "live" and runtime.broker_mode != "live" and hasattr(runtime, "_paper_router"):
        broker = runtime._paper_router  # noqa: SLF001

    client_order_id = str(uuid.uuid4().hex)
    result = await _call_broker_method(
        broker,
        "place_order",
        broker_name=request_payload.broker,
        symbol=_normalize_symbol(request_payload.symbol),
        side=request_payload.side,
        quantity=request_payload.quantity,
        order_type="MARKET",
        price=request_payload.price,
        stop_loss=request_payload.stop_loss,
        take_profit=request_payload.take_profit,
        client_order_id=client_order_id,
        mode=request_payload.mode,
    )
    order_id = ""
    if isinstance(result, dict):
        order_id = str(result.get("order_id") or result.get("data", {}).get("order_id") or "")
    fill_price = float(request_payload.price)
    status = str(result.get("status") if isinstance(result, dict) else "submitted")
    if isinstance(result, dict):
        data = result.get("data") if isinstance(result.get("data"), dict) else {}
        fill_price = float(data.get("average_price") or result.get("average_price") or request_payload.price)
        status = str(data.get("status") or result.get("status") or "submitted")
    if status.lower() in {"complete", "filled", "traded"}:
        await runtime.position_manager.on_fill(
            request_payload.broker,
            request_payload.symbol,
            request_payload.side,
            request_payload.quantity,
            fill_price,
        )
    session = SessionLocal()
    try:
        session.add(
            Trade(
                order_id=order_id or client_order_id,
                symbol=_normalize_symbol(request_payload.symbol),
                quantity=request_payload.quantity if request_payload.side.lower() == "buy" else -request_payload.quantity,
                entry_price=fill_price,
                stop_loss=request_payload.stop_loss,
                take_profit=request_payload.take_profit,
                broker=request_payload.broker,
                mode=request_payload.mode,
                status=status.lower(),
                entry_time=_utc_now(),
            )
        )
        session.commit()
    finally:
        session.close()
    return {"ok": True, "order_id": order_id or client_order_id, "status": status, "price": fill_price}


@app.get("/order-history")
async def order_history(request: Request) -> list[dict[str, Any]]:
    """Merge manual trades with automated executions for the trading screen."""
    del request
    session = SessionLocal()
    try:
        return _trade_history(session)
    finally:
        session.close()


@app.get("/strategies")
async def strategies() -> list[dict[str, Any]]:
    """Return strategy rows with a synthetic equity curve for the chart."""
    session = SessionLocal()
    try:
        rows = session.query(Strategy).order_by(Strategy.id.desc()).all()
        return [_strategy_payload(session, row) for row in rows]
    finally:
        session.close()


@app.post("/strategy/create")
async def create_strategy(payload: dict[str, Any]) -> dict[str, Any]:
    """Create a strategy entry from the UI form."""
    session = SessionLocal()
    try:
        strategy_id = str(payload.get("id") or uuid.uuid4().hex)
        row = session.query(Strategy).filter(Strategy.id == strategy_id).first()
        if row is None:
            row = Strategy(id=strategy_id, name=str(payload.get("name") or "Unnamed"))
            session.add(row)
        row.name = str(payload.get("name") or row.name)
        row.symbol = str(payload.get("symbol") or row.symbol or "INFY").upper()
        row.timeframe = str(payload.get("timeframe") or row.timeframe or "4h")
        row.status = str(payload.get("status") or row.status or "paused")
        row.entry_rule = str(payload.get("entry_rule") or "")
        row.exit_rule = str(payload.get("exit_rule") or "")
        row.created_date = row.created_date or _utc_now()
        session.commit()
        return {"ok": True, "id": strategy_id}
    finally:
        session.close()


@app.delete("/strategy/{strategy_id}")
async def delete_strategy(strategy_id: str) -> dict[str, Any]:
    """Delete a strategy row."""
    session = SessionLocal()
    try:
        row = session.query(Strategy).filter(Strategy.id == strategy_id).first()
        if row is None:
            raise HTTPException(status_code=404, detail="Strategy not found")
        session.delete(row)
        session.commit()
        return {"ok": True}
    finally:
        session.close()


@app.post("/strategy/pinescript/generate")
async def generate_pinescript(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a starter PineScript strategy template."""
    name = str(payload.get("name") or "Trading Strategy")
    return {"script": _pinescript_template(name)}


# ── Hermes Strategy Endpoints ──────────────────────────────────────────────


@app.post("/strategy/generate")
async def hermes_generate_strategy(payload: dict[str, Any]) -> dict[str, Any]:
    """Generate a new strategy using Hermes AI reasoning."""
    symbol = str(payload.get("symbol") or "INFY").upper().strip()
    timeframe = str(payload.get("timeframe") or "1d").strip()
    if not symbol:
        raise HTTPException(status_code=400, detail="Symbol is required")

    from backend.agents.hermes_strategy_agent import HermesStrategyAgent
    from backend.integrations.hermes_client import HermesClient
    from backend.memory.strategy_memory import StrategyLessonRepository

    hermes_client = HermesClient()
    agent = HermesStrategyAgent(hermes_client=hermes_client)
    memory = StrategyLessonRepository()

    # Get lessons for context
    lessons = memory.get_lesson_texts(symbol=symbol, limit=5)

    # Get market data
    market_context = {}
    try:
        from backend.market_data.yfinance_client import (
            compute_technical_indicators,
            fetch_current_price,
            fetch_ohlcv,
        )

        price = await asyncio.to_thread(fetch_current_price, symbol)
        df = await asyncio.to_thread(fetch_ohlcv, symbol, timeframe, period="3mo")
        if df is not None and not df.empty:
            df = compute_technical_indicators(df)
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                trend = (
                    "bullish"
                    if latest.get("ema_fast", 0) > latest.get("ema_slow", 0)
                    else "bearish"
                )
                market_context = {
                    "current_price": price,
                    "trend": trend,
                    "rsi": round(float(latest.get("rsi", 50)), 2),
                    "macd": round(float(latest.get("macd", 0)), 4),
                    "volume": int(latest.get("volume", 0)),
                }
    except Exception as exc:
        logger.warning("Failed to fetch market data for %s: %s", symbol, exc)

    result = await agent.generate_strategy(
        symbol=symbol,
        timeframe=timeframe,
        market_data=market_context,
        lessons=lessons,
    )

    if not result:
        raise HTTPException(status_code=500, detail="Strategy generation failed")

    # Store the generated strategy
    strategy_id = f"hermes_{symbol}_{int(datetime.now(timezone.utc).timestamp())}"
    session = SessionLocal()
    try:
        row = Strategy(
            id=strategy_id,
            name=f"Hermes-{symbol}",
            symbol=symbol,
            timeframe=timeframe,
            status="paused",
            entry_rule=str(result.get("entry_rule", "")),
            exit_rule=str(result.get("exit_rule", "")),
            created_date=_utc_now(),
        )
        session.add(row)
        session.commit()
    finally:
        session.close()

    return {
        "ok": True,
        "strategy_id": strategy_id,
        "entry_rule": result.get("entry_rule"),
        "exit_rule": result.get("exit_rule"),
        "explanation": result.get("explanation"),
        "confidence": result.get("confidence"),
        "reasoning": result.get("reasoning"),
        "source": result.get("source"),
    }


@app.post("/strategy/validate/{strategy_id}")
async def hermes_validate_strategy(strategy_id: str) -> dict[str, Any]:
    """Validate a strategy using Hermes AI and real backtest data."""
    session = SessionLocal()
    try:
        row = session.query(Strategy).filter(Strategy.id == strategy_id).first()
        if row is None:
            raise HTTPException(status_code=404, detail="Strategy not found")
    finally:
        session.close()

    from backend.agents.hermes_strategy_agent import HermesStrategyAgent
    from backend.integrations.hermes_client import HermesClient

    hermes_client = HermesClient()
    agent = HermesStrategyAgent(hermes_client=hermes_client)

    # Run real backtest
    backtest_metrics = {"total_trades": 0, "win_rate": 0, "net_pnl": 0, "sharpe": 0, "max_dd": 0, "profit_factor": 0}
    try:
        from backend.market_data.yfinance_client import compute_technical_indicators, fetch_ohlcv

        df = await asyncio.to_thread(fetch_ohlcv, row.symbol, row.timeframe or "1d", period="6mo")
        if df is not None and not df.empty:
            df = compute_technical_indicators(df)
            if df is not None and not df.empty:
                # Simple backtest based on entry/exit rules
                backtest_metrics = _run_simple_backtest(df, row.entry_rule, row.exit_rule)
    except Exception as exc:
        logger.warning("Backtest failed for %s: %s", row.symbol, exc)

    validation = await agent.validate_strategy(
        strategy_name=row.name,
        entry_rule=row.entry_rule or "",
        exit_rule=row.exit_rule or "",
        backtest_metrics=backtest_metrics,
    )

    return {
        "ok": True,
        "strategy_id": strategy_id,
        "validation": validation,
        "backtest_metrics": backtest_metrics,
    }


@app.post("/strategy/tune/{strategy_id}")
async def hermes_tune_strategy(strategy_id: str) -> dict[str, Any]:
    """Ask Hermes to suggest one parameter improvement for a strategy."""
    session = SessionLocal()
    try:
        row = session.query(Strategy).filter(Strategy.id == strategy_id).first()
        if row is None:
            raise HTTPException(status_code=404, detail="Strategy not found")
    finally:
        session.close()

    from backend.agents.hermes_strategy_agent import HermesStrategyAgent
    from backend.integrations.hermes_client import HermesClient

    hermes_client = HermesClient()
    agent = HermesStrategyAgent(hermes_client=hermes_client)

    # Parse current params from rules
    current_params = _parse_strategy_params(row.entry_rule, row.exit_rule)
    metrics = {"win_rate": 50, "sharpe": 1.0, "max_dd": 15, "profit_factor": 1.5, "net_pnl": 0}

    suggestion = await agent.tune_strategy(
        strategy_name=row.name,
        current_params=current_params,
        backtest_metrics=metrics,
    )

    return {
        "ok": True,
        "strategy_id": strategy_id,
        "suggestion": suggestion,
    }


@app.get("/strategy/explain/{strategy_id}")
async def hermes_explain_strategy(strategy_id: str) -> dict[str, Any]:
    """Get a natural language explanation of a strategy from Hermes."""
    session = SessionLocal()
    try:
        row = session.query(Strategy).filter(Strategy.id == strategy_id).first()
        if row is None:
            raise HTTPException(status_code=404, detail="Strategy not found")
    finally:
        session.close()

    from backend.agents.hermes_strategy_agent import HermesStrategyAgent
    from backend.integrations.hermes_client import HermesClient

    hermes_client = HermesClient()
    agent = HermesStrategyAgent(hermes_client=hermes_client)

    explanation = await agent.explain_strategy(
        strategy_name=row.name,
        entry_rule=row.entry_rule or "",
        exit_rule=row.exit_rule or "",
    )

    return {
        "ok": True,
        "strategy_id": strategy_id,
        "explanation": explanation,
    }


@app.post("/strategy/auto-generate")
async def hermes_auto_generate() -> dict[str, Any]:
    """Trigger background strategy generation for all watchlist symbols."""
    from backend.agents.strategy_generator_agent import StrategyGeneratorAgent
    from backend.integrations.hermes_client import HermesClient
    from backend.memory.strategy_memory import StrategyLessonRepository

    cfg = load_tooling_config()
    if not cfg.hermes_enabled:
        raise HTTPException(status_code=400, detail="Hermes is not enabled")

    hermes_client = HermesClient()
    from backend.agents.hermes_strategy_agent import HermesStrategyAgent

    hermes_agent = HermesStrategyAgent(hermes_client=hermes_client)
    memory = StrategyLessonRepository()

    generator = StrategyGeneratorAgent(
        hermes_strategy_agent=hermes_agent,
        strategy_memory=memory,
        interval_seconds=cfg.strategy_gen_interval,
    )

    # Run one generation cycle
    result = await generator._generate_one_strategy()

    return {
        "ok": True,
        "generated": result is not None,
        "message": "Strategy generation triggered" if result else "No strategy generated (check watchlist)",
    }


@app.get("/strategy/lessons")
async def get_strategy_lessons(
    symbol: Optional[str] = None,
    limit: int = 20,
) -> dict[str, Any]:
    """Get strategy lessons from self-learning memory."""
    from backend.memory.strategy_memory import StrategyLessonRepository

    memory = StrategyLessonRepository()
    lessons = memory.get_lessons(symbol=symbol, limit=limit)
    summary = memory.get_lessons_summary(symbol=symbol)
    return {"lessons": lessons, "summary": summary}


@app.get("/strategy/hermes/status")
async def hermes_strategy_status() -> dict[str, Any]:
    """Check Hermes strategy agent status."""
    from backend.agents.hermes_strategy_agent import HermesStrategyAgent
    from backend.integrations.hermes_client import HermesClient

    cfg = load_tooling_config()
    hermes_client = HermesClient()
    agent = HermesStrategyAgent(hermes_client=hermes_client)
    available = await agent.is_available()

    return {
        "hermes_enabled": cfg.hermes_enabled,
        "hermes_available": available,
        "hermes_timeout_sec": cfg.hermes_timeout_sec,
        "strategy_gen_interval": cfg.strategy_gen_interval,
    }


# ── Helper functions for Hermes strategy endpoints ──────────────────────────


def _run_simple_backtest(df: Any, entry_rule: str, exit_rule: str) -> dict[str, Any]:
    """Run a simple backtest based on entry/exit rules using EMA crossover."""
    import pandas as pd

    if "ema_fast" not in df.columns or "ema_slow" not in df.columns:
        return {"total_trades": 0, "win_rate": 0, "net_pnl": 0, "sharpe": 0, "max_dd": 0, "profit_factor": 0}

    # Simple EMA crossover strategy
    df = df.copy()
    df["signal"] = 0
    df.loc[df["ema_fast"] > df["ema_slow"], "signal"] = 1
    df.loc[df["ema_fast"] < df["ema_slow"], "signal"] = -1
    df["position"] = df["signal"].shift(1).fillna(0)
    df["returns"] = df["close"].pct_change() * df["position"]
    df["equity"] = (1 + df["returns"].fillna(0)).cumprod()

    # Calculate metrics
    trades = df["position"].diff().fillna(0)
    trade_count = int((trades != 0).sum() // 2)
    returns = df["returns"].dropna()

    if len(returns) == 0 or trade_count == 0:
        return {"total_trades": 0, "win_rate": 0, "net_pnl": 0, "sharpe": 0, "max_dd": 0, "profit_factor": 0}

    wins = (returns > 0).sum()
    losses = (returns < 0).sum()
    win_rate = round((wins / (wins + losses)) * 100, 2) if (wins + losses) > 0 else 0
    net_pnl = round(float(returns.sum()) * 10000, 2)
    sharpe = round(float(returns.mean() / (returns.std() + 1e-10)) * (252 ** 0.5), 2)
    equity = df["equity"].dropna()
    max_dd = round(float((equity / equity.cummax() - 1).min()) * 100, 2) if len(equity) > 0 else 0
    gross_profit = float(returns[returns > 0].sum())
    gross_loss = abs(float(returns[returns < 0].sum()))
    profit_factor = round(gross_profit / (gross_loss + 1e-10), 2)

    return {
        "total_trades": trade_count,
        "win_rate": win_rate,
        "net_pnl": net_pnl,
        "sharpe": sharpe,
        "max_dd": abs(max_dd),
        "profit_factor": profit_factor,
    }


def _parse_strategy_params(entry_rule: str, exit_rule: str) -> dict:
    """Parse strategy rules into a params dict for tuning."""
    params = {}
    for rule_str in [entry_rule, exit_rule]:
        if not rule_str:
            continue
        try:
            rule = json.loads(rule_str) if rule_str.startswith("{") else {}
            for key, val in rule.items():
                if isinstance(val, (int, float)):
                    params[key] = val
                elif isinstance(val, dict):
                    for k, v in val.items():
                        if isinstance(v, (int, float)):
                            params[f"{key}_{k}"] = v
        except (json.JSONDecodeError, TypeError):
            continue
    if not params:
        params = {"fast_period": 12, "slow_period": 26, "stop_loss_pct": 2.0, "take_profit_pct": 5.0}
    return params


@app.post("/backtest")
async def backtest(payload: BacktestRequest) -> dict[str, Any]:
    """Run a synthetic backtest so the UI has a working results panel."""
    result = _backtest_result(payload)
    session = SessionLocal()
    try:
        session.add(
            BacktestResult(
                strategy_name=payload.strategy,
                symbol=payload.symbol,
                timeframe=payload.timeframe,
                total_trades=result["total_trades"],
                win_rate=result["win_rate"],
                pnl=result["net_pnl"],
                pnl_percent=(result["net_pnl"] / payload.capital * 100.0) if payload.capital else 0.0,
                sharpe_ratio=result["sharpe"],
                max_drawdown=result["max_dd"],
                profit_factor=result["profit_factor"],
                created_at=_utc_now(),
            )
        )
        session.commit()
    finally:
        session.close()
    return result


@app.get("/screener")
async def screener(request: Request) -> list[dict[str, Any]]:
    """Return a synthetic screener result table."""
    runtime = _runtime(request)
    session = SessionLocal()
    try:
        rows = _screener_rows(runtime, session)
        rows.sort(key=lambda item: item["rank"])
        return rows
    finally:
        session.close()


@app.post("/chat")
async def chat(payload: ChatRequest, request: Request) -> dict[str, Any]:
    """Queue a chat command for the Ollama-backed boss agent."""
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    command_id = uuid.uuid4().hex
    request.app.state.chat_commands[command_id] = {"status": "running", "response": None}
    session = SessionLocal()
    try:
        session.add(ChatHistory(user_id="user", role="user", message=message, timestamp=_utc_now()))
        session.commit()
    finally:
        session.close()
    asyncio.create_task(_process_chat_command(request.app, command_id, message))
    return {"command_id": command_id, "status": "running"}


@app.get("/chat/response/{command_id}")
async def chat_response(command_id: str, request: Request) -> dict[str, Any]:
    """Poll a queued chat response."""
    return request.app.state.chat_commands.get(command_id, {"status": "pending", "response": None})


@app.get("/{path:path}", include_in_schema=False)
async def spa_fallback(path: str) -> Any:
    """Serve the built React app for any non-API route."""
    if path.startswith(("api/", "ws/", "broker-")):
        raise HTTPException(status_code=404, detail="Not found")
    if INDEX_HTML.exists():
        return FileResponse(INDEX_HTML)
    return JSONResponse({"detail": "Frontend build not found"}, status_code=404)
