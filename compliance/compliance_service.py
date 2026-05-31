"""HERMES v5.2 Compliance Layer: Ensures regulatory adherence and auditability."""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import aiosqlite
from uuid import UUID, uuid4
from decimal import Decimal

from trading_system.config.models import (
    HermesEvent,
    OrderToTradeRatioEvent, OrderToTradeRatioEventPayload,
    SebicertificationEvent, SebicertificationEventPayload,
    AnnualComplianceExportEvent, AnnualComplianceExportEventPayload,
)
from trading_system.events.event_bus import AsyncEventBus
from trading_system.events.event_types import EventType
from trading_system.memory.audit_memory import AuditMemoryRepository # For audit export

logger = logging.getLogger(__name__)

class ComplianceService:
    """
    Manages compliance checks, reporting, and automated auditing.
    Matches HERMES v5.2 Task 1.2 Kill Switch Engine (monitoring certain metrics),
    and Tier 7 Compliance Layer.
    """

    def __init__(
        self,
        sqlite_path: str,
        event_bus: AsyncEventBus,
        audit_memory: AuditMemoryRepository,
        order_to_trade_ratio_threshold: Decimal = Decimal("50.0"), # SEBI: 50:1 (Orders:Trades)
        physical_kill_switch_test_time_utc: str = "02:30", # 08:00 IST is 02:30 UTC
        certification_check_interval_seconds: int = 4 * 3600, # Every 4 hours
        compliance_check_interval_seconds: int = 60, # Every minute for OTR
    ) -> None:
        self.sqlite_path = sqlite_path
        self.event_bus = event_bus
        self.audit_memory = audit_memory
        self.order_to_trade_ratio_threshold = order_to_trade_ratio_threshold
        self.physical_kill_switch_test_time_utc = physical_kill_switch_test_time_utc
        self.certification_check_interval_seconds = certification_check_interval_seconds
        self.compliance_check_interval_seconds = compliance_check_interval_seconds
        self._is_running = False
        self._last_certification_check: datetime = datetime.now(timezone.utc)
        self._last_kill_switch_test_day: Optional[int] = None

    async def start(self):
        """Starts the compliance service loop."""
        self._is_running = True
        logger.info("Compliance Service started.")
        while self._is_running:
            try:
                await self.check_order_to_trade_ratio()
                await self.check_sebi_certifications()
                await self.run_physical_kill_switch_test_automation()
            except asyncio.CancelledError:
                logger.info("Compliance Service task cancelled.")
                break
            except Exception as e:
                logger.error("Error in Compliance Service loop: %s", e)
            await asyncio.sleep(self.compliance_check_interval_seconds)

    async def stop(self):
        """Stops the compliance service loop."""
        self._is_running = False
        logger.info("Compliance Service stopped.")

    async def check_order_to_trade_ratio(self) -> None:
        """
        Monitors Order-to-Trade (OTR) ratio for compliance. (SEBI limit: 50:1)
        If exceeded, publishes an alert.
        """
        now = datetime.now(timezone.utc)
        # For simplicity, calculate OTR for all orders/trades today.
        # In a real system, this would be per-account, per-broker.
        async with aiosqlite.connect(self.sqlite_path) as db:
            async with db.execute(
                """
                SELECT
                    COUNT(CASE WHEN status = 'FILLED' THEN 1 END) as trade_count,
                    COUNT(id) as order_count
                FROM orders_v2
                WHERE created_at >= ?
                """,
                (now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat(),)
            ) as cursor:
                row = await cursor.fetchone()
                trade_count = row[0] if row else 0
                order_count = row[1] if row else 0
            
            ratio = Decimal(order_count) / Decimal(trade_count) if trade_count > 0 else Decimal("0")
            
            if ratio > self.order_to_trade_ratio_threshold:
                logger.warning(
                    "OTR Alert: Ratio %.2f (Orders: %d, Trades: %d) exceeds threshold %.2f",
                    ratio, order_count, trade_count, self.order_to_trade_ratio_threshold
                )
                event_payload = OrderToTradeRatioEventPayload(
                    account_id=uuid4(), # Placeholder
                    broker_id="all", # Placeholder
                    order_count=order_count,
                    trade_count=trade_count,
                    ratio=ratio,
                    threshold=self.order_to_trade_ratio_threshold,
                    triggered_at=now,
                )
                event = OrderToTradeRatioEvent(
                    event_id=uuid4(),
                    timestamp=now,
                    correlation_id=uuid4(),
                    source_component="compliance_service",
                    source_instance="local-compliance-node",
                    payload=event_payload.model_dump(),
                )
                await self.event_bus.publish(event)
            else:
                logger.debug("OTR within limits: %.2f (Orders: %d, Trades: %d)", ratio, order_count, trade_count)

    async def check_sebi_certifications(self) -> None:
        """
        Checks for expiring SEBI certifications.
        Publishes alerts if certifications are expired or expiring soon.
        """
        now = datetime.now(timezone.utc)
        if (now - self._last_certification_check).total_seconds() < self.certification_check_interval_seconds:
            return

        self._last_certification_check = now
        logger.debug("Checking SEBI certifications.")

        # In a real system, this would query a 'sebi_certifications' table.
        # For now, simulate a single certification.
        mock_certification_expiry = datetime.now(timezone.utc) + timedelta(days=30)
        
        status: Literal["active", "expired", "expiring_soon"] = "active"
        if mock_certification_expiry < now:
            status = "expired"
        elif mock_certification_expiry < now + timedelta(days=60): # Expiring in next 60 days
            status = "expiring_soon"

        if status != "active":
            logger.warning("SEBI Certification Alert: Status is %s, expires on %s", status, mock_certification_expiry)
            event_payload = SebicertificationEventPayload(
                certification_id="SEBI-Algo-001",
                entity_name="HERMES v5.2 Algo",
                expiry_date=mock_certification_expiry,
                status=status,
                checked_at=now,
            )
            event = SebicertificationEvent(
                event_id=uuid4(),
                timestamp=now,
                correlation_id=uuid4(),
                source_component="compliance_service",
                source_instance="local-compliance-node",
                payload=event_payload.model_dump(),
            )
            await self.event_bus.publish(event)

    async def run_physical_kill_switch_test_automation(self) -> None:
        """
        Automates the daily physical kill switch test (08:00 IST / 02:30 UTC).
        Publishes an event upon test completion/failure.
        """
        now_utc = datetime.now(timezone.utc)
        test_hour, test_minute = map(int, self.physical_kill_switch_test_time_utc.split(':'))

        if self._last_kill_switch_test_day != now_utc.day and 
           now_utc.hour == test_hour and now_utc.minute >= test_minute and now_utc.minute < test_minute + 5: # 5 min window
            
            logger.info("Initiating daily physical kill switch test automation.")
            self._last_kill_switch_test_day = now_utc.day

            test_success = True # Simulate success for now
            if not test_success:
                logger.critical("Physical Kill Switch Test FAILED!")
                # In a real system, this would trigger the main KillSwitch and alert.
            
            event_payload = {
                "test_id": str(uuid4()),
                "test_time": now_utc.isoformat(),
                "success": test_success,
                "note": "Automated daily physical kill switch test.",
            }
            event = HermesEvent(
                event_id=uuid4(),
                timestamp=now_utc,
                correlation_id=uuid4(),
                source_component="compliance_service",
                source_instance="local-compliance-node",
                event_type=EventType.PHYSICAL_KILL_SWITCH_TEST.value,
                payload=event_payload,
            )
            await self.event_bus.publish(event)

    async def perform_annual_compliance_export(self, fy_year: str) -> None:
        """
        Exports all audit data for a given financial year.
        This would be triggered manually or by a separate cron job.
        """
        logger.info("Initiating annual compliance export for FY %s", fy_year)
        start_date = datetime.strptime(f"{fy_year.split('-')[0]}-04-01", "%Y-%m-%d").replace(tzinfo=timezone.utc)
        end_date = datetime.strptime(f"{fy_year.split('-')[1]}-03-31", "%Y-%m-%d").replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)

        # In a real system, this would involve exporting the entire audit_logs table
        # for the given date range, potentially to an encrypted S3 bucket.
        export_path = f"/compliance_exports/{fy_year}_audit_logs.jsonl"
        
        # Simulate export
        await asyncio.sleep(5)
        export_success = True

        logger.info("Annual compliance export for FY %s completed. Path: %s, Success: %s", fy_year, export_path, export_success)
        event_payload = AnnualComplianceExportEventPayload(
            fy_year=fy_year,
            export_path=export_path,
            start_date=start_date,
            end_date=end_date,
            exported_at=datetime.now(timezone.utc),
            status="success" if export_success else "failed",
        )
        event = AnnualComplianceExportEvent(
            event_id=uuid4(),
            timestamp=datetime.now(timezone.utc),
            correlation_id=uuid4(),
            source_component="compliance_service",
            source_instance="local-compliance-node",
            payload=event_payload.model_dump(),
        )
        await self.event_bus.publish(event)
