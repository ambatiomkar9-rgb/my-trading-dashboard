"""Chaos Test: Reconciliation Mismatch Trigger."""

import asyncio
import logging
from unittest.mock import MagicMock, AsyncMock
from trading_system.execution.reconciliation_engine import ReconciliationEngine
from trading_system.execution.kill_switch import KillSwitch, KillSwitchReason

logger = logging.getLogger(__name__)

async def run_chaos_reconciliation():
    """
    Simulates a position mismatch between broker and DB (Task 7.2 Chaos Test #4).
    Verifies that the Kill Switch is triggered after 2 failures.
    """
    logger.info("Starting Chaos Test: Reconciliation Mismatch Trigger")
    
    broker_router = AsyncMock()
    # Broker says we have 100 shares
    broker_router.get_positions.return_value = [{"symbol": "INFY", "quantity": 100}]
    
    kill_switch = KillSwitch()
    sqlite_path = "C:\\Users\\ambat\\Documents\\Codex\\2026-05-18\\files-mentioned-by-the-user-multi\\trading_system\\data\\trading_system.db"
    
    engine = ReconciliationEngine(
        broker_router=broker_router,
        sqlite_path=sqlite_path,
        kill_switch=kill_switch,
        interval_seconds=1
    )
    
    # Mock _get_db_positions to return 90 shares (mismatch)
    engine._get_db_positions = AsyncMock(return_value={"INFY": 90.0})
    
    # First reconciliation cycle (should warn and log)
    logger.info("Running first reconciliation cycle (expect mismatch)...")
    await engine.reconcile_account("test_acc", "alpaca")
    assert kill_switch.is_active is False
    
    # Second reconciliation cycle (should trigger kill switch)
    logger.info("Running second reconciliation cycle (expect mismatch and kill)...")
    await engine.reconcile_account("test_acc", "alpaca")
    
    assert kill_switch.is_active is True
    assert kill_switch.state.reason == KillSwitchReason.API_FAILURE
    
    logger.info("Chaos Test: Reconciliation Mismatch Trigger Passed")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_chaos_reconciliation())
