"""Chaos Test: Kill Switch Trigger Verification."""

import asyncio
import logging
from unittest.mock import MagicMock, AsyncMock
from trading_system.execution.execution_engine import ExecutionEngine
from trading_system.config.models import OrderRequest, OrderSide, TradingMode, OrderType
from trading_system.events.event_types import EventType

from trading_system.execution.kill_switch import KillSwitchState, KillSwitchReason

logger = logging.getLogger(__name__)

async def run_chaos_kill_switch():
    """
    Simulates a Kill Switch trigger and verifies execution halt (Task 7.2 Chaos Test #4).
    """
    logger.info("Starting Chaos Test: Kill Switch Trigger Verification")
    
    # Mocking components
    risk_guardian = MagicMock()
    kill_switch = MagicMock()
    kill_switch.is_active = True # Force active
    kill_switch.state = KillSwitchState(
        active=True, 
        reason=KillSwitchReason.MANUAL, 
        details={"note": "Chaos Test"}
    )
    
    event_bus = AsyncMock()
    global_state = AsyncMock()
    trade_memory = AsyncMock()
    
    engine = ExecutionEngine(
        risk_guardian=risk_guardian,
        kill_switch=kill_switch,
        paper_executor=AsyncMock(),
        live_executor=AsyncMock(),
        global_state=global_state,
        trade_memory=trade_memory,
        event_bus=event_bus
    )
    
    order = OrderRequest(
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        quantity=0.01,
        mode=TradingMode.PAPER,
        order_type=OrderType.MARKET
    )
    
    logger.info("Attempting to submit order with Kill Switch active...")
    result = await engine.submit_order(order)
    
    logger.info("Result status: %s", result.status)
    logger.info("Result message: %s", result.message)
    
    # Verify rejection
    assert result.accepted is False
    assert "Kill switch active" in result.message
    
    # Verify KILL_SWITCH_TRIGGERED event was published
    published_types = [call.args[0].event_type for call in event_bus.publish.call_args_list]
    assert EventType.KILL_SWITCH_TRIGGERED in published_types
    
    logger.info("Chaos Test: Kill Switch Trigger Verification Passed")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_chaos_kill_switch())
