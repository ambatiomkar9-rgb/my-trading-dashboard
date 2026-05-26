from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional


@dataclass(slots=True)
class OrderFingerprint:
    symbol: str
    side: str
    quantity: int


class OrderDeduplicationService:
    """
    Idempotency helper (in-memory).

    For full multi-instance idempotency, persist client_order_id to DB.
    On Render free plan you typically run a single instance, but restarts will clear memory.
    """

    def __init__(self) -> None:
        self.pending_orders: Dict[str, Dict[str, Any]] = {}
        self.completed_orders: Dict[str, Dict[str, Any]] = {}

    def generate_client_order_id(self, symbol: str, side: str, quantity: int) -> str:
        fp = f"{symbol}_{side}_{quantity}_{int(datetime.now().timestamp() * 1000)}"
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, fp))

    def is_duplicate(self, client_order_id: str) -> bool:
        return client_order_id in self.pending_orders or client_order_id in self.completed_orders

    def register_order(self, client_order_id: str, symbol: str, side: str, quantity: int) -> None:
        self.pending_orders[client_order_id] = {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "timestamp": datetime.now(),
        }

    def mark_completed(self, client_order_id: str, broker_order_id: str) -> None:
        if client_order_id in self.pending_orders:
            order = self.pending_orders.pop(client_order_id)
            order["broker_order_id"] = broker_order_id
            order["completed_at"] = datetime.now()
            self.completed_orders[client_order_id] = order

    def cleanup_old_orders(self, hours: int = 24) -> None:
        cutoff = datetime.now() - timedelta(hours=hours)
        self.completed_orders = {
            k: v
            for k, v in self.completed_orders.items()
            if v.get("completed_at", datetime.now()) > cutoff
        }

