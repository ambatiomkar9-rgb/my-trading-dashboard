"""Skill wrapper for broker routing decisions."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from trading_system.config.models import OrderRequest, TradingMode

logger = logging.getLogger(__name__)


class CCXTBrokerRouterSkill:
    """Resolve best broker/exchange route for a normalized order request."""

    def __init__(self, default_live_broker: str = "binance") -> None:
        self.default_live_broker = default_live_broker

    def route(self, request: OrderRequest) -> Dict[str, Any]:
        """
        Decide route target without executing.

        Paper mode always routes to paper executor.
        Live mode routes by explicit broker or default broker.
        """
        if request.mode == TradingMode.PAPER:
            return {"route": "paper", "reason": "paper mode isolation"}
        if request.mode == TradingMode.BACKTEST:
            return {"route": "none", "reason": "backtest never routes to brokers"}
        broker = request.broker or self.default_live_broker
        return {"route": broker, "reason": "live execution route"}

    def normalize_symbol(self, symbol: str, broker: str) -> str:
        """Normalize symbol by broker conventions."""
        symbol = symbol.upper().replace("-", "/")
        if broker == "binance" and "/" not in symbol:
            if symbol.endswith("USDT"):
                return f"{symbol[:-4]}/USDT"
            return f"{symbol}/USDT"
        return symbol
