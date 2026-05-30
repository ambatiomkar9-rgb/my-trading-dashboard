"""Dedicated trade execution agent.

Responsibilities:
- Poll cloud dashboard for APPROVED signals.
- Compute sizing, brokerage estimate, and tick rounding.
- Run a RiskGuardian pre-check (hard veto).
- Create a live approval ticket (shared via SQLite so Boss/Telegram can approve).
- Send a Telegram approval request containing the ticket id.
- Only after approval: execute via ExecutionEngine (paper/live).
- Mark the signal as executed in the cloud dashboard (prevents double fills).
"""

from __future__ import annotations

import asyncio
import json
import logging
import math
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv

# Ensure `import trading_system.*` works when running this file directly.
_PKG_DIR = Path(__file__).resolve().parents[1]  # .../trading_system
_REPO_ROOT = _PKG_DIR.parent
sys.path.insert(0, str(_REPO_ROOT))
load_dotenv(_PKG_DIR / ".env")

_LOGS_DIR = _PKG_DIR / "logs"
_LOGS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(str(_LOGS_DIR / f"agent_{datetime.now().strftime('%Y%m%d')}.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("trade_execution_agent")

from trading_system.config.models import (  # noqa: E402
    OrderRequest,
    OrderSide,
    OrderType,
    RiskDecision,
    TradingMode,
)
from trading_system.main import build_container  # noqa: E402


DASHBOARD_URL = os.getenv("DASHBOARD_URL", "https://my-trading-dashboard-8.onrender.com").rstrip("/")
DASHBOARD_TIMEOUT = int(os.getenv("DASHBOARD_TIMEOUT", "15"))
POLL_INTERVAL = int(os.getenv("EXECUTION_AGENT_POLL_INTERVAL", "5"))

DEFAULT_STOP_LOSS_PCT = float(os.getenv("DEFAULT_STOP_LOSS_PCT", "2.0"))
DEFAULT_TAKE_PROFIT_PCT = float(os.getenv("DEFAULT_TAKE_PROFIT_PCT", "5.0"))

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()


def _get_json(url: str, timeout: int = 15) -> Dict[str, Any]:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body) if body else {}


def _post_json(url: str, payload: dict, timeout: int = 15) -> Dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body) if body else {}


def _round_to_tick(price: float, tick: float) -> float:
    if tick <= 0:
        return float(price)
    return round(round(price / tick) * tick, 10)


def _infer_tick_size(symbol: str) -> float:
    sym = symbol.upper()
    if sym.endswith(".NS"):
        return 0.05
    if "/" in sym:
        return 0.01
    return 0.01


def _infer_broker(symbol: str) -> str:
    sym = symbol.upper()
    if "/" in sym:
        return "binance"
    if sym.endswith(".NS"):
        return "upstox"
    return "alpaca"


def _estimate_brokerage(notional: float, broker: str) -> float:
    """Very conservative brokerage estimate (placeholder).

    Real charges vary by broker/segment; this is used only for previews.
    """
    b = broker.lower()
    if b == "binance":
        return notional * 0.001  # 0.10%
    if b == "alpaca":
        return 0.0
    if b == "upstox":
        return min(20.0, notional * 0.0003)  # cap at 20 INR-equivalent preview
    return notional * 0.001


async def _send_telegram(text: str) -> None:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as _:
            return
    except Exception as exc:  # noqa: BLE001
        logger.warning("Telegram send failed: %s", exc)


async def _poll_approved_signals() -> list[dict]:
    try:
        data = _get_json(f"{DASHBOARD_URL}/api/signals/approved?include_executed=false", timeout=DASHBOARD_TIMEOUT)
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


async def _poll_watchlist() -> list[dict]:
    try:
        data = _get_json(f"{DASHBOARD_URL}/api/watchlist", timeout=DASHBOARD_TIMEOUT)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and isinstance(data.get("items"), list):
            return data["items"]
        return []
    except Exception:
        return []


def _qty_from_watchlist(symbol: str, watchlist: list[dict]) -> int:
    sym = symbol.upper()
    for item in watchlist:
        if str(item.get("symbol", "")).upper() == sym:
            q = item.get("quantity_to_buy") or item.get("quantity") or 0
            try:
                return max(1, int(q))
            except Exception:
                return 1
    return 1


async def main() -> None:
    container = await build_container()
    await container.event_bus.start()

    exec_engine = container.execution_engine
    risk_guardian = container.risk_guardian
    global_state = container.global_state
    approval_manager = container.live_approval_manager

    mode = TradingMode(os.getenv("TRADING_MODE", "paper").lower())

    logger.info("TradeExecutionAgent started mode=%s dashboard=%s", mode.value, DASHBOARD_URL)

    seen: Dict[str, str] = {}  # signal_id -> last_state
    while True:
        try:
            watchlist = await _poll_watchlist()
            signals = await _poll_approved_signals()
            for sig in signals:
                signal_id = str(sig.get("id") or "").strip()
                if not signal_id:
                    continue
                if sig.get("order_id"):
                    continue  # already executed

                state_key = f"{sig.get('approval_status')}|{sig.get('signal_price')}"
                if seen.get(signal_id) == state_key:
                    continue
                seen[signal_id] = state_key

                symbol = str(sig.get("symbol") or "").strip().upper()
                signal_type = str(sig.get("signal_type") or "buy").lower().strip()
                price = float(sig.get("signal_price") or 0.0)
                if not symbol or price <= 0:
                    continue

                broker = _infer_broker(symbol)
                tick = _infer_tick_size(symbol)
                qty_target = _qty_from_watchlist(symbol, watchlist)

                side = OrderSide.BUY if signal_type == "buy" else OrderSide.SELL
                stop_loss = price * (1 - (DEFAULT_STOP_LOSS_PCT / 100.0)) if side == OrderSide.BUY else price * (1 + (DEFAULT_STOP_LOSS_PCT / 100.0))
                take_profit = price * (1 + (DEFAULT_TAKE_PROFIT_PCT / 100.0)) if side == OrderSide.BUY else price * (1 - (DEFAULT_TAKE_PROFIT_PCT / 100.0))

                stop_loss = _round_to_tick(stop_loss, tick)
                take_profit = _round_to_tick(take_profit, tick)
                limit_price = _round_to_tick(price, tick)

                # Sizing cap: don't exceed MAX_POSITION_SIZE * available_cash (best-effort).
                snapshot = await global_state.snapshot(mode)
                max_pos_frac = float(os.getenv("MAX_POSITION_SIZE", "0.03"))
                budget = max(0.0, float(snapshot.available_cash)) * max_pos_frac
                max_qty_by_budget = int(math.floor(budget / max(limit_price, 1e-9))) if budget > 0 else qty_target
                qty = max(1, min(qty_target, max_qty_by_budget or qty_target))

                order = OrderRequest(
                    symbol=symbol,
                    side=side,
                    quantity=float(qty),
                    mode=mode,
                    broker=broker,
                    order_type=OrderType.MARKET,
                    limit_price=None,
                    stop_loss=float(stop_loss),
                    take_profit=float(take_profit),
                    signal_id=signal_id,
                    metadata={
                        "mark_price": limit_price,
                        "signal": sig,
                        "tick_size": tick,
                        "brokerage_estimate": _estimate_brokerage(limit_price * qty, broker),
                    },
                )

                # Risk pre-check before we even ask for approval.
                risk = risk_guardian.validate_order(order=order, snapshot=snapshot, correlation_context=None, kill_switch_active=False)
                if risk.decision == RiskDecision.REJECTED:
                    logger.warning("Risk veto signal_id=%s symbol=%s reasons=%s", signal_id, symbol, risk.reasons)
                    continue

                if mode == TradingMode.LIVE:
                    ticket = await approval_manager.create_ticket(order, requested_by="trade_execution_agent")
                    order.metadata["approval_ticket_id"] = ticket["ticket_id"]
                    preview = order.model_dump(mode="json")
                    msg = (
                        f"LIVE TRADE APPROVAL REQUIRED\n"
                        f"symbol={symbol}\n"
                        f"side={side.value}\n"
                        f"qty={qty}\n"
                        f"price~{limit_price}\n"
                        f"stop_loss={stop_loss} take_profit={take_profit}\n"
                        f"broker={broker}\n"
                        f"ticket={ticket['ticket_id']}\n\n"
                        f"Approve by sending:\n"
                        f"approve {ticket['ticket_id']}\n"
                        f"(in Dashboard Chat or Telegram)\n"
                    )
                    await _send_telegram(msg)
                    logger.info("Approval requested signal_id=%s ticket=%s", signal_id, ticket["ticket_id"])

                    # Wait for approval up to TTL.
                    deadline = datetime.now(timezone.utc).timestamp() + 300
                    while datetime.now(timezone.utc).timestamp() < deadline:
                        t = await approval_manager.get_ticket(ticket["ticket_id"])
                        if t and t.get("approved"):
                            break
                        await asyncio.sleep(2)

                # Execute (paper/live). ExecutionEngine will enforce ticket validity in live mode.
                result = await exec_engine.submit_order(order=order, human_approved=(mode == TradingMode.LIVE))
                if not result.accepted:
                    logger.warning("Execution rejected signal_id=%s status=%s msg=%s", signal_id, result.status, result.message)
                    continue

                # Mark executed in dashboard to prevent duplicates.
                try:
                    _post_json(
                        f"{DASHBOARD_URL}/api/signal/mark-executed",
                        {
                            "signal_id": signal_id,
                            "order_id": result.order_id or f"{broker.upper()}-{datetime.now(timezone.utc).timestamp()}",
                            "execution_price": result.average_price,
                            "broker": broker,
                        },
                        timeout=DASHBOARD_TIMEOUT,
                    )
                except Exception:
                    pass

                logger.info("Executed signal_id=%s symbol=%s order_id=%s", signal_id, symbol, result.order_id)

        except Exception as exc:  # noqa: BLE001
            logger.exception("TradeExecutionAgent loop error: %s", exc)

        await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())

