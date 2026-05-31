"""HERMES v5.2 Registry Service: Immutable approved strategy storage, versioning, approval gate."""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import aiosqlite
import json
from uuid import UUID, uuid4
from decimal import Decimal

from trading_system.config.models import (
    HermesEvent,
    StrategyGeneratedPayload, # For reading from outbox payload
    ValidationPassed,
    ValidationPassedPayload,
    StrategyApproved,
    StrategyApprovedPayload,
    RegistryRollback,
    RegistryRollbackPayload,
    ApproverRecord,
)
from trading_system.events.event_bus import AsyncEventBus
from trading_system.events.event_types import EventType
from trading_system.integrations.hermes_client import HermesClient # For HSM signatures, etc.

logger = logging.getLogger(__name__)

class RegistryService:
    """
    Manages the lifecycle of trading strategies, including approval via multi-signature.
    Matches HERMES v5.2 Task 1.2 Registry Service responsibilities.
    """

    def __init__(
        self,
        sqlite_path: str,
        event_bus: AsyncEventBus,
        hermes_client: HermesClient, # For HSM Ed25519 signatures
        interval_seconds: int = 5, # Polling interval for outbox and strategy expiration
        required_approval_weight: int = 3,
        approval_ttl_seconds: int = 4 * 3600, # 4 hours
        emergency_bot_schedule_seconds: int = 24 * 3600, # 24 hours
    ) -> None:
        self.sqlite_path = sqlite_path
        self.event_bus = event_bus
        self.hermes_client = hermes_client
        self.interval_seconds = interval_seconds
        self.required_approval_weight = required_approval_weight
        self.approval_ttl = timedelta(seconds=approval_ttl_seconds)
        self.emergency_bot_schedule = timedelta(seconds=emergency_bot_schedule_seconds)
        self._is_running = False

    async def start(self):
        """Starts the registry service loop."""
        self._is_running = True
        logger.info("Registry Service started.")
        self._register_event_handlers()
        while self._is_running:
            try:
                await self.process_outbox() # Poll from Validation Service
                await self.check_pending_approvals()
            except asyncio.CancelledError:
                logger.info("Registry Service task cancelled.")
                break
            except Exception as e:
                logger.error("Error in Registry Service loop: %s", e)
            await asyncio.sleep(self.interval_seconds)

    async def stop(self):
        """Stops the registry service loop."""
        self._is_running = False
        logger.info("Registry Service stopped.")

    async def list_strategies(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """List strategies with optional filtering."""
        async with aiosqlite.connect(self.sqlite_path) as db:
            query = "SELECT * FROM strategies"
            params = []
            if status:
                query += " WHERE status = ?"
                params.append(status)
            query += f" LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            db.row_factory = aiosqlite.Row # To get dict-like rows
            async with db.execute(query, params) as cursor:
                strategies = [dict(row) for row in await cursor.fetchall()]
                # Convert JSON strings back to dicts
                for s in strategies:
                    s["regime_params_json"] = json.loads(s["regime_params_json"])
                    s["validation_passed_payload_json"] = json.loads(s["validation_passed_payload_json"])
                return strategies

    async def count_strategies(self, status: Optional[str] = None) -> int:
        """Count total strategies with optional filtering."""
        async with aiosqlite.connect(self.sqlite_path) as db:
            query = "SELECT COUNT(*) FROM strategies"
            params = []
            if status:
                query += " WHERE status = ?"
                params.append(status)
            async with db.execute(query, params) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    def _register_event_handlers(self) -> None:
        """Subscribe to relevant events from Validation Service."""
        self.event_bus.subscribe(EventType.VALIDATION_PASSED, self._handle_validation_passed)
        self.event_bus.subscribe(EventType.VALIDATION_FAILED, self._handle_validation_failed)

    async def _handle_validation_passed(self, event: HermesEvent) -> None:
        """Process VALIDATION_PASSED events to create pending strategies."""
        try:
            payload = ValidationPassedPayload(**event.payload)
            logger.info("Received VALIDATION_PASSED for genome_hash=%s", payload.genome_hash)
            await self.create_pending_strategy(payload, event.correlation_id)
        except Exception as e:
            logger.error("Error handling VALIDATION_PASSED event: %s", e)

    async def _handle_validation_failed(self, event: HermesEvent) -> None:
        """Log VALIDATION_FAILED events."""
        try:
            payload = ValidationFailedPayload(**event.payload)
            logger.warning("Received VALIDATION_FAILED for genome_hash=%s, reason=%s", 
                           payload.genome_hash, payload.failure_reason)
            # Future: Update strategies table to mark as 'failed' if it exists.
        except Exception as e:
            logger.error("Error handling VALIDATION_FAILED event: %s", e)

    async def process_outbox(self):
        """Polls the outbox (from Research DB) for new validated strategies."""
        # For HERMES v5.2, Registry Service would poll Research PostgreSQL outbox directly
        # For this local setup, we simulate by directly receiving VALIDATION_PASSED events.
        pass

    async def create_pending_strategy(self, payload: ValidationPassedPayload, correlation_id: UUID) -> None:
        """
        Creates a new strategy entry in 'strategies' table with 'pending_approval' status.
        """
        async with aiosqlite.connect(self.sqlite_path) as db:
            # First, fetch the original strategy details from the outbox (Research DB context)
            # This is a simplification; in a real scenario, this would involve a separate
            # read from the Research DB or passing more data in ValidationPassed event.
            async with db.execute(
                "SELECT payload_json FROM outbox WHERE genome_hash = ? AND consumed = 1 ORDER BY created_at DESC LIMIT 1",
                (payload.genome_hash,)
            ) as cursor:
                outbox_row = await cursor.fetchone()
                if not outbox_row:
                    logger.error("Original strategy genome not found in outbox for hash: %s", payload.genome_hash)
                    return
                original_payload = StrategyGeneratedPayload(**json.loads(outbox_row[0]))

            strategy_id = str(uuid4())
            now = datetime.now(timezone.utc)
            expires_at = now + self.approval_ttl
            
            await db.execute(
                """
                INSERT INTO strategies (
                    id, genome_hash, status, version, bytecode, bytecode_checksum,
                    ed25519_signature, regime_params_json, max_capacity_rupees,
                    sector, category, approved_at, created_at, updated_at,
                    validation_passed_payload_json, correlation_id, expires_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    strategy_id,
                    payload.genome_hash,
                    "pending_approval", # Initial status
                    1, # First version
                    original_payload.genome, # Use genome as bytecode for now
                    original_payload.genome_hash, # Checksum = genome_hash
                    "UNSIGNED", # Placeholder for real signature
                    json.dumps({"normal": {}, "crisis": {}}), # Placeholder for regime_params
                    float(1000000), # Default max capacity
                    original_payload.sector,
                    original_payload.category,
                    None,
                    now.isoformat(),
                    now.isoformat(),
                    json.dumps(payload.model_dump(), default=str), # Store validation results
                    str(correlation_id),
                    expires_at.isoformat(),
                )
            )
            await db.commit()
            logger.info("Created pending strategy %s with genome_hash %s", strategy_id, payload.genome_hash)

    async def check_pending_approvals(self) -> None:
        """
        Checks for expired pending approvals and schedules emergency bot action.
        This also implicitly checks for strategies that have reached required weight.
        """
        now = datetime.now(timezone.utc)
        async with aiosqlite.connect(self.sqlite_path) as db:
            async with db.execute(
                """
                SELECT id, genome_hash, correlation_id, validation_passed_payload_json, expires_at FROM strategies
                WHERE status = 'pending_approval'
                """
            ) as cursor:
                async for row in cursor:
                    strategy_id, genome_hash, correlation_id, validation_payload_json, expires_at_str = row
                    expires_at = datetime.fromisoformat(expires_at_str)

                    # Check for expired approvals
                    if now > expires_at:
                        # Future: Schedule emergency bot after self.emergency_bot_schedule
                        logger.warning("Pending approval for strategy %s expired at %s", strategy_id, expires_at_str)
                        # For now, just mark as failed
                        await db.execute(
                            "UPDATE strategies SET status = 'failed', retired_reason = ? WHERE id = ?",
                            (f"Approval expired: {expires_at_str}", strategy_id)
                        )
                        await db.commit()
                        logger.info("Strategy %s marked as 'failed' due to expired approval.", strategy_id)
                        continue

                    # Check if strategy is approved (simplification for now - will be multi-sig)
                    # This is where the actual multi-sig logic would go.
                    # For now, we'll assume a direct API call or manual approval sets status to 'approved'
                    # and an event will trigger that.

    async def approve_strategy(self, strategy_id: str, approver_id: UUID, approver_weight: int, signature: str) -> bool:
        """
        Records an approval for a strategy and transitions its status if quorum is met.
        Matches HERMES v5.2 Task 4.1 API Contracts: POST /strategies/{id}/approve.
        """
        async with aiosqlite.connect(self.sqlite_path) as db:
            # Fetch current strategy and approvals
            async with db.execute(
                "SELECT id, status, genome_hash, correlation_id, validation_passed_payload_json FROM strategies WHERE id = ?",
                (strategy_id,)
            ) as cursor:
                strategy_row = await cursor.fetchone()
                if not strategy_row:
                    logger.warning("Strategy %s not found for approval.", strategy_id)
                    return False
                current_status = strategy_row[1]
                genome_hash = strategy_row[2]
                correlation_id = UUID(strategy_row[3])
                validation_passed_payload_json = strategy_row[4]

            if current_status != "pending_approval":
                logger.warning("Strategy %s is not in 'pending_approval' status (current: %s).", strategy_id, current_status)
                return False

            # Record approval
            now = datetime.now(timezone.utc)
            approver_record = ApproverRecord(
                approver_id=approver_id,
                weight=approver_weight,
                timestamp=now,
                signature=signature,
            )
            
            # Store approval record (in a separate 'approvals' table in real PostgreSQL)
            # For SQLite, we'll simplify and just update the strategy status directly for now.
            # In a real system, there would be an 'approvals' table.

            # Simulate quorum reached (e.g., if one approval is enough for now)
            if approver_weight >= self.required_approval_weight: # Simplified: direct approval
                validation_payload = ValidationPassedPayload(**json.loads(validation_passed_payload_json))
                strategy_approved_payload = StrategyApprovedPayload(
                    strategy_id=UUID(strategy_id),
                    genome_hash=genome_hash,
                    version=1, # Assuming first version approval
                    bytecode="BASE64_ENCODED_BYTECODE", # Placeholder
                    bytecode_checksum=genome_hash,
                    regime_params={"normal": {}, "crisis": {}}, # Placeholder
                    max_capacity_rupees=Decimal("1000000"),
                    sector=validation_payload.sector, # This would be from initial StrategyGeneratedPayload
                    category=validation_payload.category, # This would be from initial StrategyGeneratedPayload
                    approved_at=now,
                    approvers=[approver_record],
                    quorum_weight=approver_weight,
                    required_weight=self.required_approval_weight,
                    hot_swap=False,
                )
                
                strategy_approved_event = StrategyApproved(
                    event_id=uuid4(),
                    timestamp=now,
                    correlation_id=correlation_id,
                    source_component="registry_service",
                    source_instance="local-registry-node",
                    payload=strategy_approved_payload.model_dump(),
                    signature="HSM_SIGNED_EVENT" # Placeholder for real HSM signature
                )

                await db.execute(
                    "UPDATE strategies SET status = ?, approved_at = ?, updated_at = ? WHERE id = ?",
                    ("approved", now.isoformat(), now.isoformat(), strategy_id)
                )
                await db.commit()
                await self.event_bus.publish(strategy_approved_event)
                logger.info("Strategy %s APPROVED. Event published.", strategy_id)
                return True
            else:
                logger.info("Approval for strategy %s recorded. Quorum not yet met.", strategy_id)
                # In a real system, store approver_record and check total weight
                return False

    async def rollback_strategy(
        self,
        strategy_id: str,
        target_version_id: str,
        reason: str,
        initiator_id: UUID,
        signature: str,
    ) -> bool:
        """
        Rolls back a strategy to a previous valid version.
        Matches HERMES v5.2 Task 4.1 API Contracts: POST /strategies/{id}/rollback.
        """
        async with aiosqlite.connect(self.sqlite_path) as db:
            async with db.execute(
                "SELECT id, status, version, genome_hash, correlation_id FROM strategies WHERE id = ?",
                (strategy_id,)
            ) as cursor:
                strategy_row = await cursor.fetchone()
                if not strategy_row:
                    logger.warning("Strategy %s not found for rollback.", strategy_id)
                    return False
                current_status = strategy_row[1]
                current_version = strategy_row[2]
                current_genome_hash = strategy_row[3]
                correlation_id = UUID(strategy_row[4])

            if current_status not in ["approved", "full_live", "small_live", "paper_trading"]:
                logger.warning("Strategy %s cannot be rolled back from current status: %s", strategy_id, current_status)
                return False

            # For simplicity, we assume target_version_id refers to a previous ID
            # In a real system, strategy_versions table would be queried for lineage.
            async with db.execute(
                "SELECT id, genome_hash, bytecode FROM strategies WHERE id = ? AND status = 'approved'",
                (target_version_id,)
            ) as cursor:
                target_version_row = await cursor.fetchone()
                if not target_version_row:
                    logger.warning("Target version %s not found or not approved for strategy %s.", target_version_id, strategy_id)
                    return False
                
            # Simulate atomic rollback
            now = datetime.now(timezone.utc)
            rollback_payload = RegistryRollbackPayload(
                strategy_id=UUID(strategy_id),
                previous_version_id=UUID(strategy_id), # Simplified, should be actual previous version ID
                new_version_id=UUID(target_version_id),
                reason=reason,
                rolled_back_at=now,
                hot_swap=True,
            )
            rollback_event = RegistryRollback(
                event_id=uuid4(),
                timestamp=now,
                correlation_id=correlation_id,
                source_component="registry_service",
                source_instance="local-registry-node",
                payload=rollback_payload.model_dump(),
                signature="HSM_SIGNED_EVENT" # Placeholder for real HSM signature
            )
            
            await db.execute(
                "UPDATE strategies SET status = 'rolled_back', retired_reason = ?, updated_at = ? WHERE id = ?",
                (f"Rolled back to {target_version_id} due to: {reason}", now.isoformat(), strategy_id)
            )
            await db.execute(
                "UPDATE strategies SET status = 'approved', updated_at = ? WHERE id = ?",
                (now.isoformat(), target_version_id)
            )
            await db.commit()
            await self.event_bus.publish(rollback_event)
            logger.info("Strategy %s rolled back to version %s. Event published.", strategy_id, target_version_id)
            return True
