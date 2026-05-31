"""Paper broker adapters used to simulate order placement in local paper-mode tests."""
from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


def _normalize_symbol(symbol: str) -> str:
    return str(symbol or "").upper().replace(".NS", "").replace(".BO", "").strip()


@dataclass(slots=True)
class PaperBroker:
    """Very small in-memory broker that fills orders immediately."""

    broker_name: str = "upstox"
    starting_cash: float = 1_000_000.0
    _cash: float = field(init=False, repr=False)
    _orders: dict[str, dict[str, Any]] = field(init=False, repr=False)
    _positions: dict[str, dict[str, Any]] = field(init=False, repr=False)
    _lock: asyncio.Lock = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._cash = float(self.starting_cash)
        self._orders = {}
        self._positions = {}
        self._lock = asyncio.Lock()

    def snapshot(self) -> dict[str, Any]:
        """Return a compact broker snapshot for status endpoints."""
        positions_value = 0.0
        for pos in self._positions.values():
            qty = int(pos.get("quantity") or 0)
            last_price = float(pos.get("last_price") or pos.get("avg_price") or 0.0)
            positions_value += abs(qty) * last_price
        return {
            "broker_name": self.broker_name,
            "cash_balance": round(self._cash, 2),
            "positions_value": round(positions_value, 2),
            "equity": round(self._cash + positions_value, 2),
            "positions": list(self._positions.values()),
            "orders": len(self._orders),
        }

    async def close(self) -> None:
        """Paper broker does not hold network resources."""
        return

    async def place_order(
        self,
        symbol: str,
        side: str,
        quantity: int,
        client_order_id: Optional[str] = None,
        order_type: str = "MARKET",
        price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        product: str = "I",
        validity: str = "DAY",
        exchange: str = "NSE",
        segment: str = "EQ",
        broker_name: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create an order and mark it complete immediately."""
        try:
            sym = _normalize_symbol(symbol)
            qty = max(1, int(quantity))
            fill_price = float(
                price
                if price is not None and float(price) > 0
                else kwargs.get("execution_price")
                or kwargs.get("signal_price")
                or kwargs.get("entry_price")
                or kwargs.get("last_price")
                or 0.0
            )
            if fill_price <= 0:
                fill_price = 100.0

            order_id = str(client_order_id or f"paper-{uuid.uuid4().hex}")
            direction = "BUY" if str(side).lower().strip() == "buy" else "SELL"

            async with self._lock:
                position = self._positions.get(
                    sym,
                    {
                        "symbol": sym,
                        "quantity": 0,
                        "avg_price": 0.0,
                        "last_price": fill_price,
                        "side": "flat",
                        "broker": self.broker_name,
                    },
                )

                current_qty = int(position.get("quantity") or 0)
                avg_price = float(position.get("avg_price") or fill_price)
                if direction == "BUY":
                    new_qty = current_qty + qty
                    if current_qty >= 0:
                        avg_price = ((current_qty * avg_price) + (qty * fill_price)) / new_qty if new_qty else fill_price
                    else:
                        avg_price = fill_price if new_qty > 0 else avg_price
                    self._cash -= fill_price * qty
                else:
                    new_qty = current_qty - qty
                    if current_qty <= 0:
                        avg_price = ((abs(current_qty) * avg_price) + (qty * fill_price)) / abs(new_qty) if new_qty else fill_price
                    else:
                        avg_price = fill_price if new_qty < 0 else avg_price
                    self._cash += fill_price * qty

                position.update(
                    {
                        "quantity": int(new_qty),
                        "avg_price": round(float(avg_price), 4),
                        "last_price": round(fill_price, 4),
                        "side": "long" if new_qty > 0 else "short" if new_qty < 0 else "flat",
                        "updated_at": int(time.time()),
                    }
                )
                self._positions[sym] = position

                order = {
                    "order_id": order_id,
                    "client_order_id": client_order_id or order_id,
                    "symbol": sym,
                    "side": str(side).lower().strip(),
                    "quantity": qty,
                    "order_type": order_type,
                    "price": fill_price,
                    "average_price": fill_price,
                    "filled_quantity": qty,
                    "status": "complete",
                    "broker": broker_name or self.broker_name,
                    "product": product,
                    "validity": validity,
                    "exchange": exchange,
                    "segment": segment,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                }
                self._orders[order_id] = order

            return {"order_id": order_id, "status": "complete", "data": order}
        except Exception as exc:  # noqa: BLE001
            logger.error("Paper order placement failed: %s", exc)
            raise

    async def get_order_status(self, order_id: str) -> dict[str, Any]:
        """Return the stored paper order status."""
        try:
            async with self._lock:
                order = self._orders.get(str(order_id))
                if not order:
                    return {"status": "not_found", "order_id": order_id}
                return dict(order)
        except Exception as exc:  # noqa: BLE001
            logger.error("Paper order status failed: %s", exc)
            raise

    async def get_profile(self) -> dict[str, Any]:
        """Return a lightweight paper profile."""
        try:
            async with self._lock:
                snapshot = self.snapshot()
            return {
                "status": "ok",
                "client_name": "paper-trader",
                "broker": self.broker_name,
                "cash_balance": snapshot["cash_balance"],
                "equity": snapshot["equity"],
                "positions_count": len(snapshot["positions"]),
            }
        except Exception as exc:  # noqa: BLE001
            logger.error("Paper profile failed: %s", exc)
            raise

    async def get_funds_and_margin(self) -> dict[str, Any]:
        """Return mock margin data for dashboard UI calls."""
        try:
            async with self._lock:
                cash = round(self._cash, 2)
                snapshot = self.snapshot()
            return {
                "status": "ok",
                "available_cash": cash,
                "available_margin": cash,
                "used_margin": 0.0,
                "equity": snapshot["equity"],
            }
        except Exception as exc:  # noqa: BLE001
            logger.error("Paper funds failed: %s", exc)
            raise

    async def get_positions(self) -> list[dict[str, Any]]:
        """Return the simulated broker positions."""
        try:
            async with self._lock:
                return [dict(pos) for pos in self._positions.values()]
        except Exception as exc:  # noqa: BLE001
            logger.error("Paper positions failed: %s", exc)
            raise


@dataclass(slots=True)
class PaperBrokerRouter:
    """Routes orders to one or more paper broker instances."""

    brokers: dict[str, PaperBroker]
    default_broker_name: str = "upstox"

    def __post_init__(self) -> None:
        if self.default_broker_name not in self.brokers and self.brokers:
            self.default_broker_name = next(iter(self.brokers))

    def _resolve(self, broker_name: str | None = None) -> PaperBroker:
        name = str(broker_name or self.default_broker_name).lower().strip()
        broker = self.brokers.get(name)
        if broker is None:
            broker = next(iter(self.brokers.values()))
        return broker

    async def place_order(self, broker_name: str = "upstox", **kwargs: Any) -> dict[str, Any]:
        """Place an order on the selected paper broker."""
        return await self._resolve(broker_name).place_order(broker_name=broker_name, **kwargs)

    async def get_profile(self, broker_name: str = "upstox") -> dict[str, Any]:
        return await self._resolve(broker_name).get_profile()

    async def get_funds_and_margin(self, broker_name: str = "upstox") -> dict[str, Any]:
        return await self._resolve(broker_name).get_funds_and_margin()

    async def get_positions(self, broker_name: str = "upstox") -> list[dict[str, Any]]:
        return await self._resolve(broker_name).get_positions()

    def snapshot(self, broker_name: str = "upstox") -> dict[str, Any]:
        return self._resolve(broker_name).snapshot()

