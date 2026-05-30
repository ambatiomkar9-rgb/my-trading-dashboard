"""Integration tests for event-driven risk-gated execution."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from trading_system.agents.risk_guardian import RiskGuardian
from trading_system.config.models import OrderRequest, OrderSide, RiskLimits, TradingMode
from trading_system.events.event_bus import AsyncEventBus
from trading_system.events.event_types import EventType
from trading_system.execution.broker_router import BrokerRouter
from trading_system.execution.execution_engine import ExecutionEngine
from trading_system.execution.kill_switch import KillSwitch
from trading_system.execution.live_executor import LiveExecutor
from trading_system.execution.paper_executor import PaperExecutor
from trading_system.memory.global_state import GlobalState
from trading_system.memory.trade_memory import TradeMemoryRepository


@pytest.mark.asyncio
async def test_paper_order_flow_emits_events(tmp_path: Path) -> None:
    db_path = str(tmp_path / "integration.db")
    trade_memory = TradeMemoryRepository(sqlite_path=db_path)
    await trade_memory.initialize()

    event_bus = AsyncEventBus(queue_size=1000, worker_count=1)
    await event_bus.start()
    emitted = []

    async def collector(event):
        emitted.append(event.event_type.value)

    event_bus.subscribe(EventType.RISK_APPROVED, collector)
    event_bus.subscribe(EventType.TRADE_EXECUTED, collector)

    state = GlobalState(initial_balance=100000)
    guardian = RiskGuardian(
        limits=RiskLimits(
            max_daily_loss=5000,
            max_exposure=200000,
            max_leverage=2,
            max_symbol_exposure_pct=50,
            max_slippage_bps=50,
            max_consecutive_losses=5,
            max_correlation=0.9,
        )
    )
    kill_switch = KillSwitch()
    paper = PaperExecutor(global_state=state, trade_memory=trade_memory)
    live = LiveExecutor(broker_router=BrokerRouter(adapters={}), trade_memory=trade_memory)

    engine = ExecutionEngine(
        risk_guardian=guardian,
        kill_switch=kill_switch,
        paper_executor=paper,
        live_executor=live,
        global_state=state,
        trade_memory=trade_memory,
        event_bus=event_bus,
    )

    order = OrderRequest(
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        quantity=0.5,
        mode=TradingMode.PAPER,
        broker="paper",
        stop_loss=95000,
        metadata={"mark_price": 100000},
    )
    result = await engine.submit_order(order)
    await asyncio.sleep(0.1)
    await event_bus.stop()

    assert result.accepted is True
    assert "RiskApproved" in emitted
    assert "TradeExecuted" in emitted


@pytest.mark.asyncio
async def test_risk_rejects_without_stop_loss(tmp_path: Path) -> None:
    db_path = str(tmp_path / "integration2.db")
    trade_memory = TradeMemoryRepository(sqlite_path=db_path)
    await trade_memory.initialize()
    event_bus = AsyncEventBus(queue_size=1000, worker_count=1)
    await event_bus.start()
    state = GlobalState(initial_balance=100000)
    guardian = RiskGuardian(limits=RiskLimits())
    engine = ExecutionEngine(
        risk_guardian=guardian,
        kill_switch=KillSwitch(),
        paper_executor=PaperExecutor(global_state=state, trade_memory=trade_memory),
        live_executor=LiveExecutor(broker_router=BrokerRouter(adapters={}), trade_memory=trade_memory),
        global_state=state,
        trade_memory=trade_memory,
        event_bus=event_bus,
    )
    order = OrderRequest(
        symbol="ETH/USDT",
        side=OrderSide.BUY,
        quantity=1,
        mode=TradingMode.PAPER,
        broker="paper",
        metadata={"mark_price": 3000},
    )
    result = await engine.submit_order(order)
    await event_bus.stop()
    assert result.accepted is False
    assert "Risk rejected" in result.message
