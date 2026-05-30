"""Live execution adapter requiring explicit human approval."""

from __future__ import annotations

import logging

from trading_system.config.models import ExecutionResult, OrderRequest, TradingMode
from trading_system.execution.broker_router import BrokerRouter
from trading_system.memory.trade_memory import TradeMemoryRepository

logger = logging.getLogger(__name__)


class LiveExecutor:
    """Thin wrapper over broker router with approval gate."""

    def __init__(self, broker_router: BrokerRouter, trade_memory: TradeMemoryRepository) -> None:
        self.broker_router = broker_router
        self.trade_memory = trade_memory

    async def execute(self, order: OrderRequest, human_approved: bool) -> ExecutionResult:
        """Execute a live order after approval verification."""
        if order.mode != TradingMode.LIVE:
            return ExecutionResult(
                accepted=False,
                mode=order.mode,
                broker=order.broker,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                status="rejected",
                message="Live executor only accepts live mode orders.",
            )
        if not human_approved:
            return ExecutionResult(
                accepted=False,
                mode=TradingMode.LIVE,
                broker=order.broker,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                status="pending_approval",
                message="Live mode requires explicit human approval.",
            )
        result = await self.broker_router.execute_live_order(order)
        await self.trade_memory.log_execution(result)
        return result
