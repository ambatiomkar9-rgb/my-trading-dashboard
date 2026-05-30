"""Capital integrity verification — broker positions vs Live DB."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import aiosqlite

from trading_system.config.models import TradingMode
from trading_system.execution.broker_router import BrokerRouter
from trading_system.execution.kill_switch import KillSwitch, KillSwitchReason

logger = logging.getLogger(__name__)

class ReconciliationEngine:
    """
    Poller that compares broker positions with local database.
    Matches HERMES v5.2 Task 1.2 Reconciliation Engine responsibilities.
    """

    def __init__(
        self,
        broker_router: BrokerRouter,
        sqlite_path: str,
        kill_switch: KillSwitch,
        interval_seconds: int = 30
    ) -> None:
        self.broker_router = broker_router
        self.sqlite_path = sqlite_path
        self.kill_switch = kill_switch
        self.interval_seconds = interval_seconds
        self._consecutive_failures: Dict[str, int] = {} # account_id|broker_id -> count

    async def start(self):
        """Start the reconciliation loop."""
        logger.info("Reconciliation Engine started (interval=%ds)", self.interval_seconds)
        while True:
            try:
                if self.kill_switch.is_active:
                    logger.debug("Kill switch active, skipping reconciliation cycle.")
                else:
                    await self.reconcile_all()
            except Exception as e:
                logger.error("Error in reconciliation cycle: %s", e)
            await asyncio.sleep(self.interval_seconds)

    async def reconcile_all(self):
        """Reconcile positions for all active accounts."""
        # For simplicity, we'll assume a set of accounts/brokers to check.
        # In a real system, these would be fetched from the 'accounts' table.
        # Here we'll check the brokers configured in the router.
        for broker_id in self.broker_router.adapters.keys():
            await self.reconcile_account("primary_account", broker_id)

    async def reconcile_account(self, account_id: str, broker_id: str):
        """Perform reconciliation for a single account/broker pair."""
        key = f"{account_id}|{broker_id}"
        
        try:
            # 1. Fetch positions from Broker
            broker_raw = await self.broker_router.get_positions(broker_id)
            broker_positions = self._normalize_broker_positions(broker_raw, broker_id)
            
            # 2. Fetch positions from DB
            db_positions = await self._get_db_positions(account_id, broker_id)
            
            # 3. Compare
            mismatches = self._compare_positions(broker_positions, db_positions)
            
            if not mismatches:
                self._consecutive_failures[key] = 0
                logger.debug("Reconciliation PASSED for %s", key)
                return

            # 4. Handle Mismatch
            self._consecutive_failures[key] = self._consecutive_failures.get(key, 0) + 1
            logger.warning("Reconciliation MISMATCH detected for %s (fail count=%d): %s", 
                           key, self._consecutive_failures[key], mismatches)
            
            await self._log_mismatch(account_id, broker_id, mismatches)
            
            # 5. Trigger Kill Switch if consecutive failures > threshold (F-011)
            if self._consecutive_failures[key] >= 2:
                self.kill_switch.trigger(
                    KillSwitchReason.API_FAILURE, # Spec says trigger kill switch on mismatch
                    {"account_id": account_id, "broker_id": broker_id, "mismatches": mismatches}
                )
                logger.critical("GLOBAL KILL TRIGGERED due to reconciliation mismatch on %s", key)

        except Exception as e:
            logger.error("Reconciliation failed for %s: %s", key, e)

    def _normalize_broker_positions(self, raw: List[Dict[str, Any]], broker_id: str) -> Dict[str, float]:
        """Normalize broker-specific position formats to {symbol: quantity}."""
        normalized = {}
        for pos in raw:
            symbol = pos.get("symbol") or pos.get("instrument")
            # CCXT format or Alpaca/Oanda format
            qty = pos.get("quantity") or pos.get("qty") or pos.get("units")
            if symbol and qty is not None:
                normalized[str(symbol).upper()] = abs(float(qty))
        return normalized

    async def _get_db_positions(self, account_id: str, broker_id: str) -> Dict[str, float]:
        """Fetch expected positions from the local database."""
        positions = {}
        async with aiosqlite.connect(self.sqlite_path) as db:
            async with db.execute(
                "SELECT symbol, quantity FROM positions WHERE account_id = ? AND broker_id = ?",
                (account_id, broker_id)
            ) as cursor:
                async for row in cursor:
                    positions[str(row[0]).upper()] = float(row[1])
        return positions

    def _compare_positions(self, broker: Dict[str, float], db: Dict[str, float]) -> List[Dict[str, Any]]:
        """Identify mismatches between broker and DB."""
        mismatches = []
        all_symbols = set(broker.keys()) | set(db.keys())
        
        for symbol in all_symbols:
            b_qty = broker.get(symbol, 0.0)
            d_qty = db.get(symbol, 0.0)
            
            if abs(b_qty - d_qty) > 0.0001: # Small epsilon
                diff_pct = (abs(b_qty - d_qty) / d_qty * 100) if d_qty > 0 else 100.0
                if diff_pct > 0.1: # 0.1% threshold as per Task 2.11
                    mismatches.append({
                        "symbol": symbol,
                        "broker_qty": b_qty,
                        "db_qty": d_qty,
                        "diff_pct": diff_pct
                    })
        return mismatches

    async def _log_mismatch(self, account_id: str, broker_id: str, mismatches: List[Dict[str, Any]]):
        """Persist mismatch event for audit."""
        async with aiosqlite.connect(self.sqlite_path) as db:
            for m in mismatches:
                await db.execute(
                    """
                    INSERT INTO reconciliation_events (
                        account_id, broker_id, mismatch_type, broker_value, 
                        db_value, difference_pct, consecutive_failures, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        account_id, broker_id, "position_qty", m["broker_qty"],
                        m["db_qty"], m["diff_pct"], self._consecutive_failures.get(f"{account_id}|{broker_id}", 0),
                        datetime.now(timezone.utc).isoformat()
                    )
                )
            await db.commit()
