from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict


class TradeSegment(str, Enum):
    intraday = "intraday"
    delivery = "delivery"


@dataclass(slots=True)
class ChargesEngine:
    """
    Upstox-style pre-trade charges estimate with a profitability filter.

    Notes:
    - Rates vary by broker and can change; keep these values configurable if needed.
    - This engine is used for "reject unprofitable trades" logic (profit >= ratio * charges).
    """

    min_profitability_ratio: float = 3.0

    # Defaults (documented as "as of 2024" in the user spec).
    GST_PERCENT: float = 0.18
    API_ORDER_CHARGE: float = 10.0  # per order

    INTRADAY_BROKERAGE_PERCENT: float = 0.0005  # 0.05%
    INTRADAY_MAX_BROKERAGE: float = 20.0
    INTRADAY_STT_PERCENT: float = 0.00025  # on sell
    INTRADAY_STAMP_DUTY_PERCENT: float = 0.00003  # on buy

    DELIVERY_BROKERAGE: float = 20.0  # flat
    DELIVERY_DP_CHARGE: float = 20.0  # per scrip
    DELIVERY_STT_PERCENT: float = 0.001  # on sell
    DELIVERY_STAMP_DUTY_PERCENT: float = 0.00015  # on buy

    SEBI_PERCENT: float = 0.000001
    EXCHANGE_TRANSACTION_PERCENT: float = 0.0000322

    def calculate_charges(
        self,
        segment: TradeSegment,
        buy_price: float,
        sell_price: float,
        quantity: int,
        using_api: bool = True,
    ) -> Dict[str, Any]:
        gross_profit = (sell_price - buy_price) * quantity

        buy_value = buy_price * quantity
        sell_value = sell_price * quantity
        turnover = buy_value + sell_value

        if segment == TradeSegment.intraday:
            brokerage = min(turnover * self.INTRADAY_BROKERAGE_PERCENT, self.INTRADAY_MAX_BROKERAGE)
        else:
            brokerage = self.DELIVERY_BROKERAGE

        api_charge = (self.API_ORDER_CHARGE * 2) if using_api else 0.0  # buy + sell

        if segment == TradeSegment.intraday:
            stt = sell_value * self.INTRADAY_STT_PERCENT
            stamp_duty = buy_value * self.INTRADAY_STAMP_DUTY_PERCENT
        else:
            stt = sell_value * self.DELIVERY_STT_PERCENT
            stamp_duty = buy_value * self.DELIVERY_STAMP_DUTY_PERCENT

        exchange_charges = turnover * self.EXCHANGE_TRANSACTION_PERCENT
        sebi_charges = turnover * self.SEBI_PERCENT

        gst_base = brokerage + exchange_charges + api_charge
        gst = gst_base * self.GST_PERCENT

        dp_charge = self.DELIVERY_DP_CHARGE if segment == TradeSegment.delivery else 0.0

        total_charges = (
            brokerage
            + api_charge
            + stt
            + stamp_duty
            + exchange_charges
            + sebi_charges
            + gst
            + dp_charge
        )

        net_profit = gross_profit - total_charges
        breakeven_move = (total_charges / quantity) if quantity else 0.0
        profitability_ratio = (gross_profit / total_charges) if total_charges > 0 else float("inf")
        should_execute = profitability_ratio >= self.min_profitability_ratio

        return {
            "gross_profit": round(gross_profit, 2),
            "total_charges": round(total_charges, 2),
            "net_profit": round(net_profit, 2),
            "breakeven_move": round(breakeven_move, 4),
            "profitability_ratio": round(profitability_ratio, 2) if profitability_ratio != float("inf") else float("inf"),
            "should_execute": bool(should_execute),
            "breakdown": {
                "brokerage": round(brokerage, 2),
                "api_charge": round(api_charge, 2),
                "stt": round(stt, 2),
                "stamp_duty": round(stamp_duty, 2),
                "exchange_charges": round(exchange_charges, 2),
                "sebi_charges": round(sebi_charges, 2),
                "gst": round(gst, 2),
                "dp_charge": round(dp_charge, 2),
            },
        }

