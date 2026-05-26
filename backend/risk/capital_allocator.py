from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(slots=True)
class CapitalConfig:
    """
    Institutional capital allocation rules.

    All percentages are expressed as fractions (0.70 = 70%).
    """

    max_capital_deployment: float = 0.70
    risk_per_trade: float = 0.01
    max_position_size: float = 0.10
    max_open_positions: int = 8
    emergency_reserve: float = 0.20


class CapitalAllocator:
    def __init__(self, config: CapitalConfig | None = None) -> None:
        self.config = config or CapitalConfig()

    def calculate_position_size(
        self,
        account_balance: float,
        entry_price: float,
        stop_loss_price: float,
        current_exposure: float,
        open_positions: int,
    ) -> Dict[str, Any]:
        reserve_capital = account_balance * self.config.emergency_reserve
        max_deployable = account_balance * self.config.max_capital_deployment
        remaining_deployable = max_deployable - current_exposure

        if open_positions >= self.config.max_open_positions:
            return {"allowed": False, "reason": "Maximum open positions reached"}

        stop_distance = abs(entry_price - stop_loss_price)
        if stop_distance <= 0:
            return {"allowed": False, "reason": "Invalid stop loss distance"}

        risk_amount = account_balance * self.config.risk_per_trade
        quantity = int(risk_amount / stop_distance)

        if quantity <= 0:
            return {"allowed": False, "reason": "Calculated quantity is 0 (risk too small or stop too wide)"}

        position_value = quantity * entry_price

        max_position_value = account_balance * self.config.max_position_size
        if position_value > max_position_value:
            quantity = int(max_position_value / entry_price)
            position_value = quantity * entry_price

        if position_value > remaining_deployable:
            return {
                "allowed": False,
                "reason": f"Insufficient deployable capital. Available: {remaining_deployable:.2f}",
            }

        return {
            "allowed": True,
            "quantity": quantity,
            "position_value": round(position_value, 2),
            "risk_amount": round(risk_amount, 2),
            "remaining_capital": round(account_balance - current_exposure - position_value, 2),
            "reserved_capital": round(reserve_capital, 2),
        }

