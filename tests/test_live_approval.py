"""Unit tests for live approval ticket workflow."""

from __future__ import annotations

import pytest

from trading_system.agents.risk_guardian import RiskGuardian
from trading_system.config.models import OrderRequest, OrderSide, RiskLimits, TradingMode
from trading_system.events.event_bus import AsyncEventBus
from trading_system.execution.broker_router import BrokerRouter
from trading_system.execution.execution_engine import ExecutionEngine
from trading_system.execution.kill_switch import KillSwitch
from trading_system.execution.live_approval import LiveApprovalManager
from trading_system.execution.live_executor import LiveExecutor
from trading_system.execution.paper_executor import PaperExecutor
from trading_system.memory.global_state import GlobalState
from trading_system.memory.trade_memory import TradeMemoryRepository


def _live_order() -> OrderRequest:
    return OrderRequest(
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        quantity=0.01,
        mode=TradingMode.LIVE,
        broker="binance",
        stop_loss=95000,
        metadata={"mark_price": 100000},
    )


@pytest.mark.asyncio
async def test_live_ticket_lifecycle() -> None:
    manager = LiveApprovalManager(ttl_seconds=60)
    order = _live_order()
    ticket = await manager.create_ticket(order, requested_by="alice")
    assert ticket["approved"] is False
    approved = await manager.approve_ticket(ticket["ticket_id"], approved_by="bob")
    assert approved["approved"] is True
    consumed = await manager.consume_for_order(ticket["ticket_id"], order)
    assert consumed is True
    replay = await manager.consume_for_order(ticket["ticket_id"], order)
    assert replay is False


@pytest.mark.asyncio
async def test_execution_engine_rejects_live_without_ticket(tmp_path) -> None:
    db_path = str(tmp_path / "approval.db")
    trade_memory = TradeMemoryRepository(db_path)
    await trade_memory.initialize()
    event_bus = AsyncEventBus(worker_count=1)
    await event_bus.start()
    state = GlobalState(initial_balance=100000)
    manager = LiveApprovalManager(ttl_seconds=60)
    engine = ExecutionEngine(
        risk_guardian=RiskGuardian(RiskLimits()),
        kill_switch=KillSwitch(),
        paper_executor=PaperExecutor(state, trade_memory),
        live_executor=LiveExecutor(BrokerRouter(adapters={}), trade_memory),
        global_state=state,
        trade_memory=trade_memory,
        event_bus=event_bus,
        live_approval_manager=manager,
        require_live_approval_ticket=True,
    )
    result = await engine.submit_order(_live_order())
    await event_bus.stop()
    assert result.accepted is False
    assert "approval_ticket_id" in result.message
