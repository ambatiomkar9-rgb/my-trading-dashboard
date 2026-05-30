"""Paper execution engine isolated from live exchanges."""

from __future__ import annotations

import logging
import uuid
from typing import Any, Dict

from trading_system.config.models import ExecutionResult, OrderRequest, TradingMode
from trading_system.memory.global_state import GlobalState, Position
from trading_system.memory.trade_memory import TradeMemoryRepository

logger = logging.getLogger(__name__)


class PaperExecutor:
    """Simulated order executor with deterministic fills."""

    def __init__(self, global_state: GlobalState, trade_memory: TradeMemoryRepository) -> None:
        self.global_state = global_state
        self.trade_memory = trade_memory
        self.fee_bps = 2.0
        self.slippage_bps = 2.0

    async def execute(self, order: OrderRequest) -> ExecutionResult:
        """Execute one paper order."""
        if order.mode != TradingMode.PAPER:
            return ExecutionResult(
                accepted=False,
                mode=order.mode,
                broker="paper",
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                status="rejected",
                message="Paper executor only accepts paper mode orders.",
            )
        mark_price = float(order.metadata.get("mark_price", 0.0) or order.limit_price or 100.0)
        fill_price = self._fill_price(mark_price, order.side.value)
        order_id = f"PAPER-{uuid.uuid4().hex[:12]}"

        await self._apply_position(order, fill_price)

        result = ExecutionResult(
            accepted=True,
            mode=TradingMode.PAPER,
            broker="paper",
            order_id=order_id,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            average_price=fill_price,
            status="filled",
            message="Paper order executed in simulation.",
            metadata={"simulated": True},
        )
        await self.trade_memory.log_execution(result)
        return result

    async def _apply_position(self, order: OrderRequest, fill_price: float) -> None:
        """Update global state positions and cash."""
        current = await self.global_state.get_position(order.symbol, TradingMode.PAPER)
        qty = order.quantity
        notional = qty * fill_price
        side = order.side.value

        if side == "buy":
            await self.global_state.adjust_cash_and_balance(mode=TradingMode.PAPER, cash_delta=-notional, pnl_delta=0.0)
            if current and current.side == "buy":
                new_qty = current.quantity + qty
                new_avg = ((current.avg_price * current.quantity) + (fill_price * qty)) / new_qty
                current.quantity = new_qty
                current.avg_price = new_avg
                await self.global_state.upsert_position(current)
            elif current and current.side == "sell":
                close_qty = min(qty, current.quantity)
                pnl = (current.avg_price - fill_price) * close_qty
                current.quantity -= close_qty
                await self.global_state.adjust_cash_and_balance(mode=TradingMode.PAPER, cash_delta=0.0, pnl_delta=pnl)
                if current.quantity <= 0:
                    await self.global_state.remove_position(order.symbol, TradingMode.PAPER)
                else:
                    await self.global_state.upsert_position(current)
            else:
                await self.global_state.upsert_position(
                    Position(
                        symbol=order.symbol,
                        quantity=qty,
                        avg_price=fill_price,
                        side="buy",
                        mode=TradingMode.PAPER,
                    )
                )
            return

        # Sell side
        await self.global_state.adjust_cash_and_balance(mode=TradingMode.PAPER, cash_delta=notional, pnl_delta=0.0)
        if current and current.side == "sell":
            new_qty = current.quantity + qty
            new_avg = ((current.avg_price * current.quantity) + (fill_price * qty)) / new_qty
            current.quantity = new_qty
            current.avg_price = new_avg
            await self.global_state.upsert_position(current)
        elif current and current.side == "buy":
            close_qty = min(qty, current.quantity)
            pnl = (fill_price - current.avg_price) * close_qty
            current.quantity -= close_qty
            await self.global_state.adjust_cash_and_balance(mode=TradingMode.PAPER, cash_delta=0.0, pnl_delta=pnl)
            if current.quantity <= 0:
                await self.global_state.remove_position(order.symbol, TradingMode.PAPER)
            else:
                await self.global_state.upsert_position(current)
        else:
            await self.global_state.upsert_position(
                Position(
                    symbol=order.symbol,
                    quantity=qty,
                    avg_price=fill_price,
                    side="sell",
                    mode=TradingMode.PAPER,
                )
            )

    def _fill_price(self, mark_price: float, side: str) -> float:
        fee = self.fee_bps / 10000
        slip = self.slippage_bps / 10000
        if side == "buy":
            return mark_price * (1 + fee + slip)
        return mark_price * (1 - fee - slip)
