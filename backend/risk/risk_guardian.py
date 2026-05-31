"""Async risk guard that validates basic order sanity before execution."""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

try:
    from backend.brokerage.charges_engine import ChargesEngine, TradeSegment  # type: ignore
except ModuleNotFoundError:  # noqa: BLE001
    from brokerage.charges_engine import ChargesEngine, TradeSegment  # type: ignore

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class RiskGuardian:
    """Basic guardrails used by the execution agent."""

    charges_engine: ChargesEngine
    max_quantity: int = int(os.getenv("MAX_RISK_QTY", "5000"))
    max_order_value: float = float(os.getenv("MAX_RISK_ORDER_VALUE", "2500000"))

    async def evaluate(self, order: dict[str, Any]) -> dict[str, Any]:
        """Approve or reject an order based on simple risk checks and charges."""
        try:
            symbol = str(order.get("symbol") or "").upper().strip()
            side = str(order.get("side") or "buy").lower().strip()
            qty = int(order.get("quantity") or order.get("qty") or 0)
            price = float(order.get("price") or order.get("entry_price") or 0.0)
            expected_exit = float(order.get("expected_exit") or order.get("take_profit") or 0.0)
            segment_name = str(order.get("trade_segment") or "intraday").lower().strip()
            segment = TradeSegment.delivery if segment_name == "delivery" else TradeSegment.intraday

            if not symbol or side not in {"buy", "sell"}:
                return {"action": "REJECT", "reason": "invalid_order_side"}
            if qty <= 0 or price <= 0 or expected_exit <= 0:
                return {"action": "REJECT", "reason": "invalid_order_values"}
            if qty > self.max_quantity:
                return {"action": "REJECT", "reason": f"qty_over_limit_{self.max_quantity}"}
            if price * qty > self.max_order_value:
                return {"action": "REJECT", "reason": f"order_value_over_limit_{self.max_order_value:.0f}"}

            if side == "sell":
                buy_price = expected_exit
                sell_price = price
            else:
                buy_price = price
                sell_price = expected_exit

            charges = self.charges_engine.calculate_charges(
                segment,
                buy_price=buy_price,
                sell_price=sell_price,
                quantity=qty,
                using_api=True,
            )
            if not charges.get("should_execute", True):
                return {
                    "action": "REJECT",
                    "reason": (
                        f"ratio_{charges.get('profitability_ratio', 0)}x_below_min_{self.charges_engine.min_profitability_ratio}x"
                    ),
                    "charges": charges,
                }

            return {"action": "APPROVE", "reason": "ok", "charges": charges}
        except Exception as exc:  # noqa: BLE001
            logger.error("Risk evaluation failed: %s", exc)
            return {"action": "REJECT", "reason": f"risk_error:{exc}"}

