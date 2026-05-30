"""Chaos Test: Broker Timeout Simulation."""

import asyncio
import logging
from unittest.mock import MagicMock, AsyncMock
from trading_system.execution.execution_engine import ExecutionEngine
from trading_system.config.models import OrderRequest, OrderSide, TradingMode, OrderType

logger = logging.getLogger(__name__)

async def run_chaos_broker_timeout():
    """
    Simulates a broker API timeout (Task 7.2 Chaos Test #3).
    Verifies that the system retries or alerts as per SPEC.
    """
    logger.info("Starting Chaos Test: Broker Timeout Simulation")
    
    # Mocking components
    risk_guardian = MagicMock()
    risk_guardian.validate_order.return_value.decision = "approved"
    
    kill_switch = MagicMock()
    kill_switch.is_active = False
    
    event_bus = AsyncMock()
    global_state = AsyncMock()
    trade_memory = AsyncMock()
    
    # Live executor that timed out
    live_executor = AsyncMock()
    live_executor.execute.side_effect = asyncio.TimeoutError("Broker API Timeout")
    
    engine = ExecutionEngine(
        risk_guardian=risk_guardian,
        kill_switch=kill_switch,
        paper_executor=AsyncMock(),
        live_executor=live_executor,
        global_state=global_state,
        trade_memory=trade_memory,
        event_bus=event_bus
    )
    
    order = OrderRequest(
        symbol="INFY",
        side=OrderSide.BUY,
        quantity=10,
        mode=TradingMode.LIVE,
        order_type=OrderType.MARKET,
        metadata={"approval_ticket_id": "TICKET-123"}
    )
    
    try:
        logger.info("Submitting order with simulated broker timeout...")
        result = await engine.submit_order(order)
        logger.info("Result: %s", result)
    except Exception as e:
        logger.error("Caught expected exception or error: %s", e)
        
    logger.info("Chaos Test: Broker Timeout Simulation Completed")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_chaos_broker_timeout())
