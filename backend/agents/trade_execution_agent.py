"""Signal-to-broker execution agent with charge filtering and fill tracking."""
from __future__ import annotations

import asyncio
import inspect
import logging
import os
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Optional

import httpx

try:
    from backend.brokerage.charges_engine import TradeSegment  # type: ignore
    from backend.portfolio.position_manager import PositionManager  # type: ignore
    from backend.config.trading_config import is_trading_enabled  # type: ignore
except ModuleNotFoundError:  # noqa: BLE001
    from brokerage.charges_engine import TradeSegment  # type: ignore
    from portfolio.position_manager import PositionManager  # type: ignore
    from config.trading_config import is_trading_enabled  # type: ignore

logger = logging.getLogger(__name__)
DB_PATH = Path(os.getenv("EXECUTIONS_DB_PATH", "data/executions.db"))


def _normalize_dashboard_url(raw_url: str | None) -> str:
    """Prefer a loopback-safe dashboard URL for local paper-mode tests."""
    url = str(raw_url or "").strip().rstrip("/")
    if not url:
        return "http://127.0.0.1:8000"
    if url.startswith("http://localhost"):
        return url.replace("localhost", "127.0.0.1", 1)
    if url.startswith("https://localhost"):
        return url.replace("localhost", "127.0.0.1", 1)
    return url


def _dashboard_url() -> str:
    return _normalize_dashboard_url(os.getenv("DASHBOARD_URL"))


class TradeExecutionAgent:
    """Polls approved dashboard signals, executes them, and monitors fills."""

    def __init__(
        self,
        broker_router: Any,
        risk_guardian: Any,
        charges_engine: Any,
        position_manager: PositionManager,
        event_bus: Any,
    ) -> None:
        self.broker = broker_router
        self.risk = risk_guardian
        self.charges = charges_engine
        self.positions = position_manager
        self.bus = event_bus
        self._running = False
        self._placed: dict[str, str] = {}
        self._init_db()
        self._load_existing_orders()

    def _init_db(self) -> None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(DB_PATH) as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_order_id TEXT UNIQUE,
                    broker_order_id TEXT,
                    signal_id TEXT,
                    broker TEXT,
                    symbol TEXT,
                    side TEXT,
                    quantity INTEGER,
                    entry_price REAL,
                    status TEXT DEFAULT 'submitted',
                    reject_reason TEXT,
                    created_at INTEGER
                )
                """
            )

    def _load_existing_orders(self) -> None:
        try:
            with sqlite3.connect(DB_PATH) as con:
                rows = con.execute(
                    """
                    SELECT client_order_id, broker_order_id
                    FROM executions
                    WHERE broker_order_id IS NOT NULL AND broker_order_id != ''
                    """
                ).fetchall()
            self._placed = {str(row[0]): str(row[1]) for row in rows}
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not load existing executions: %s", exc)

    async def start(self) -> None:
        """Run the polling and order-monitoring loops forever."""
        try:
            self._running = True
            logger.info("TradeExecutionAgent started")
            await asyncio.gather(self._poll_approved_signals(), self._monitor_open_orders())
        except Exception as exc:  # noqa: BLE001
            logger.error("TradeExecutionAgent start failed: %s", exc)

    async def stop(self) -> None:
        """Stop the agent loops."""
        try:
            self._running = False
        except Exception as exc:  # noqa: BLE001
            logger.error("TradeExecutionAgent stop failed: %s", exc)

    def _auth_headers(self) -> dict[str, str]:
        token = os.getenv("DASHBOARD_API_TOKEN", "").strip()
        if token:
            return {"Authorization": f"Bearer {token}"}
        admin_key = os.getenv("ADMIN_API_KEY", "").strip()
        return {"X-Admin-Key": admin_key} if admin_key else {}

    def _resolve_broker(self, broker_name: str) -> Any:
        if hasattr(self.broker, "brokers") and isinstance(getattr(self.broker, "brokers"), dict):
            return self.broker.brokers.get(broker_name)
        return self.broker

    @staticmethod
    def _extract_order_id(result: Any) -> str:
        if isinstance(result, dict):
            nested = result.get("data") if isinstance(result.get("data"), dict) else None
            if nested and nested.get("order_id"):
                return str(nested["order_id"])
            if result.get("order_id"):
                return str(result["order_id"])
        return ""

    async def _poll_approved_signals(self) -> None:
        """Poll dashboard every few seconds for approved signals."""
        try:
            async with httpx.AsyncClient(timeout=10, trust_env=False) as client:
                while self._running:
                    try:
                        resp = await client.get(f"{_dashboard_url()}/api/signals/approved", headers=self._auth_headers())
                        if resp.status_code == 200:
                            payload = resp.json()
                            signals = payload if isinstance(payload, list) else payload.get("signals", [])
                            for signal in signals:
                                await self._execute_signal(signal)
                    except Exception as exc:  # noqa: BLE001
                        logger.warning("Poll error: %s", exc)
                    await asyncio.sleep(5)
        except Exception as exc:  # noqa: BLE001
            logger.error("_poll_approved_signals failed: %s", exc)

    async def _execute_signal(self, signal: dict[str, Any]) -> None:
        """Validate a signal and push it through risk, charges, and broker execution."""
        try:
            if not is_trading_enabled():
                signal_id = str(signal.get("id") or signal.get("signal_id") or "unknown")
                symbol = str(signal.get("symbol") or "").upper().strip()
                reason = "kill_switch_disabled"
                await self._update_signal_status(signal_id, "skipped", reason)
                await self._save_execution(
                    str(uuid.uuid5(uuid.NAMESPACE_DNS, f"skipped_{signal_id}")),
                    None,
                    signal_id,
                    str(signal.get("broker") or "upstox"),
                    symbol,
                    str(signal.get("side") or signal.get("signal_type") or "buy").lower().strip(),
                    int(signal.get("quantity") or signal.get("qty") or signal.get("quantity_to_buy") or 0),
                    float(signal.get("price") or signal.get("signal_price") or 0),
                    "skipped",
                    reason,
                )
                logger.warning("Trading is disabled; skipped signal %s", signal_id)
                return

            signal_id = str(signal.get("id") or signal.get("signal_id") or "unknown")
            symbol = str(signal.get("symbol") or "").upper().strip()
            side = str(signal.get("side") or signal.get("signal_type") or "buy").lower().strip()
            quantity = int(signal.get("quantity") or signal.get("qty") or signal.get("quantity_to_buy") or 0)
            price = float(signal.get("price") or signal.get("signal_price") or signal.get("entry_price") or 0)
            target = float(signal.get("expected_exit") or signal.get("take_profit") or (price * 1.03))
            broker_name = str(signal.get("broker") or "upstox").lower().strip()
            trade_segment = str(signal.get("trade_segment") or "intraday").lower().strip()
            segment = TradeSegment.delivery if trade_segment == "delivery" else TradeSegment.intraday

            if not symbol or quantity <= 0 or price <= 0:
                logger.warning("Skipping malformed signal: %s", signal)
                return

            client_order_id = str(
                uuid.uuid5(uuid.NAMESPACE_DNS, f"{symbol}_{side}_{quantity}_{signal_id}")
            )
            if client_order_id in self._placed:
                logger.info("Duplicate signal %s skipped", signal_id)
                return

            if side == "sell":
                buy_price = target
                sell_price = price
            else:
                buy_price = price
                sell_price = target

            charges = self.charges.calculate_charges(
                segment,
                buy_price=buy_price,
                sell_price=sell_price,
                quantity=quantity,
                using_api=True,
            )
            if not charges.get("should_execute", False):
                reason = f"Charges reject: ratio={charges.get('profitability_ratio')}x"
                logger.warning(reason)
                await self._save_execution(
                    client_order_id,
                    None,
                    signal_id,
                    broker_name,
                    symbol,
                    side,
                    quantity,
                    price,
                    "rejected_charges",
                    reason,
                )
                await self._update_signal_status(signal_id, "rejected", reason)
                return

            risk_result = await self.risk.evaluate(
                {
                    "symbol": symbol,
                    "side": side,
                    "quantity": quantity,
                    "price": price,
                    "expected_exit": target,
                }
            )
            if risk_result.get("action") == "REJECT":
                reason = str(risk_result.get("reason") or "risk_reject")
                logger.warning("Risk reject: %s", reason)
                await self._save_execution(
                    client_order_id,
                    None,
                    signal_id,
                    broker_name,
                    symbol,
                    side,
                    quantity,
                    price,
                    "rejected_risk",
                    reason,
                )
                await self._update_signal_status(signal_id, "rejected", reason)
                return

            # Mark the signal as in-progress before placing the order to avoid duplicate loops.
            await self._update_signal_status(signal_id, "executing", None)

            broker = self._resolve_broker(broker_name)
            if not broker:
                raise RuntimeError(f"Broker not available: {broker_name}")

            try:
                if hasattr(self.broker, "brokers"):
                    result = await self.broker.place_order(
                        broker_name=broker_name,
                        symbol=symbol,
                        side=side,
                        quantity=quantity,
                        order_type="MARKET",
                        price=price,
                        take_profit=target,
                        client_order_id=client_order_id,
                    )
                else:
                    result = await broker.place_order(
                        symbol=symbol,
                        side=side,
                        quantity=quantity,
                        client_order_id=client_order_id,
                        order_type="MARKET",
                        price=price,
                        stop_loss=None,
                        take_profit=target,
                        product=str(signal.get("product") or "I"),
                        validity=str(signal.get("validity") or "DAY"),
                    )
            except TypeError:
                result = await broker.place_order(symbol=symbol, side=side, quantity=quantity, order_type="MARKET")

            broker_oid = self._extract_order_id(result)
            if not broker_oid:
                reason = f"No order_id returned: {result}"
                await self._save_execution(
                    client_order_id,
                    None,
                    signal_id,
                    broker_name,
                    symbol,
                    side,
                    quantity,
                    price,
                    "no_order_id",
                    reason,
                )
                await self._update_signal_status(signal_id, "rejected", reason)
                return

            self._placed[client_order_id] = broker_oid
            await self._save_execution(
                client_order_id,
                broker_oid,
                signal_id,
                broker_name,
                symbol,
                side,
                quantity,
                price,
                "submitted",
                None,
            )
            await self.bus.publish(
                "order.placed",
                {
                    "client_order_id": client_order_id,
                    "broker_order_id": broker_oid,
                    "signal_id": signal_id,
                    "symbol": symbol,
                    "side": side,
                    "quantity": quantity,
                    "broker": broker_name,
                },
            )
            asyncio.create_task(
                self._monitor_fill(
                    broker_name=broker_name,
                    broker_oid=broker_oid,
                    client_oid=client_order_id,
                    signal_id=signal_id,
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                )
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("_execute_signal failed: %s", exc)

    async def _monitor_fill(
        self,
        broker_name: str,
        broker_oid: str,
        client_oid: str,
        signal_id: str,
        symbol: str,
        side: str,
        quantity: int,
    ) -> None:
        """Poll order status until the broker reports a final state."""
        try:
            deadline = time.time() + 120
            broker = self._resolve_broker(broker_name)
            if not broker:
                return

            while self._running and time.time() < deadline:
                await asyncio.sleep(5)
                try:
                    status = await broker.get_order_status(broker_oid)
                    state = str(status.get("status") or status.get("order_status") or "").lower()
                    if state in ("complete", "filled", "traded", "fully_executed"):
                        fill_price = float(status.get("average_price") or status.get("avg_price") or 0.0)
                        filled_qty = int(status.get("filled_quantity") or status.get("quantity") or quantity)
                        await self.positions.on_fill(broker_name, symbol, side, filled_qty, fill_price)
                        await self._update_execution_status(client_oid, "filled", fill_price)
                        await self._update_signal_status(signal_id, "filled", None)
                        await self.bus.publish(
                            "order.filled",
                            {
                                "client_order_id": client_oid,
                                "broker_order_id": broker_oid,
                                "signal_id": signal_id,
                                "symbol": symbol,
                                "side": side,
                                "filled_qty": filled_qty,
                                "fill_price": fill_price,
                            },
                        )
                        logger.info("Order filled: %s %s @ %.2f", symbol, side, fill_price)
                        return
                    if state in ("rejected", "cancelled", "canceled", "expired"):
                        await self._update_execution_status(client_oid, state, None)
                        await self._update_signal_status(signal_id, state, state)
                        await self.bus.publish(
                            "order.rejected",
                            {"client_order_id": client_oid, "symbol": symbol, "reason": state},
                        )
                        logger.warning("Order %s: %s", state, broker_oid)
                        return
                except Exception as exc:  # noqa: BLE001
                    logger.error("Monitor fill error: %s", exc)
            logger.warning("Order monitoring timeout: %s", broker_oid)
        except Exception as exc:  # noqa: BLE001
            logger.error("_monitor_fill failed: %s", exc)

    async def _monitor_open_orders(self) -> None:
        """Catch missed fills by periodically rechecking older submitted orders."""
        try:
            while self._running:
                await asyncio.sleep(60)
                with sqlite3.connect(DB_PATH) as con:
                    rows = con.execute(
                        """
                        SELECT client_order_id, broker_order_id, broker, signal_id, symbol, side, quantity
                        FROM executions
                        WHERE status='submitted' AND created_at < ?
                        """,
                        (int(time.time()) - 120,),
                    ).fetchall()
                for row in rows:
                    asyncio.create_task(
                        self._monitor_fill(
                            broker_name=str(row[2]),
                            broker_oid=str(row[1]),
                            client_oid=str(row[0]),
                            signal_id=str(row[3] or ""),
                            symbol=str(row[4]),
                            side=str(row[5]),
                            quantity=int(row[6] or 0),
                        )
                    )
        except Exception as exc:  # noqa: BLE001
            logger.error("_monitor_open_orders failed: %s", exc)

    async def _save_execution(
        self,
        client_oid: str,
        broker_oid: Optional[str],
        signal_id: str,
        broker: str,
        symbol: str,
        side: str,
        qty: int,
        price: float,
        status: str,
        reason: Optional[str],
    ) -> None:
        try:
            with sqlite3.connect(DB_PATH) as con:
                con.execute(
                    """
                    INSERT INTO executions (
                        client_order_id, broker_order_id, signal_id, broker, symbol,
                        side, quantity, entry_price, status, reject_reason, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(client_order_id) DO UPDATE SET
                        broker_order_id=excluded.broker_order_id,
                        signal_id=excluded.signal_id,
                        broker=excluded.broker,
                        symbol=excluded.symbol,
                        side=excluded.side,
                        quantity=excluded.quantity,
                        entry_price=excluded.entry_price,
                        status=excluded.status,
                        reject_reason=excluded.reject_reason
                    """,
                    (
                        client_oid,
                        broker_oid,
                        signal_id,
                        broker,
                        symbol,
                        side,
                        int(qty),
                        float(price),
                        status,
                        reason,
                        int(time.time()),
                    ),
                )
        except Exception as exc:  # noqa: BLE001
            logger.error("_save_execution failed: %s", exc)

    async def _update_execution_status(self, client_oid: str, status: str, fill_price: Optional[float]) -> None:
        try:
            with sqlite3.connect(DB_PATH) as con:
                if fill_price is not None:
                    con.execute(
                        "UPDATE executions SET status=?, entry_price=? WHERE client_order_id=?",
                        (status, float(fill_price), client_oid),
                    )
                else:
                    con.execute("UPDATE executions SET status=? WHERE client_order_id=?", (status, client_oid))
        except Exception as exc:  # noqa: BLE001
            logger.error("_update_execution_status failed: %s", exc)

    async def _update_signal_status(self, signal_id: str, status: str, reason: Optional[str]) -> None:
        """Update the dashboard signal row through the API."""
        try:
            async with httpx.AsyncClient(timeout=10, trust_env=False) as client:
                resp = await client.patch(
                    f"{_dashboard_url()}/api/signals/{signal_id}",
                    json={"status": status, "reason": reason},
                    headers=self._auth_headers(),
                )
                if resp.status_code >= 400:
                    logger.warning("Signal update failed: %s %s", resp.status_code, resp.text)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not update signal status: %s", exc)
