"""Tamper-proof audit logging with cryptographic hash-chaining."""

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import aiosqlite

logger = logging.getLogger(__name__)

class AuditMemoryRepository:
    """
    WORM-like audit log with SHA-256 hash chaining.
    Matches HERMES v5.2 Task 4.3 Audit Logs.
    """

    def __init__(self, sqlite_path: str) -> None:
        self.sqlite_path = sqlite_path

    async def log_event(
        self,
        event_id: str,
        event_type: str,
        source_component: str,
        source_instance: str,
        correlation_id: str,
        payload: Dict[str, Any],
        signature: Optional[str] = None
    ) -> int:
        """
        Append an event to the audit log and update the hash chain.
        """
        async with aiosqlite.connect(self.sqlite_path) as db:
            # 1. Get the current hash of the last entry
            async with db.execute(
                "SELECT current_hash FROM audit_logs ORDER BY id DESC LIMIT 1"
            ) as cursor:
                row = await cursor.fetchone()
                previous_hash = row[0] if row else "GENESIS"

            # 2. Compute payload hash
            payload_json = json.dumps(payload, sort_keys=True)
            payload_hash = hashlib.sha256(payload_json.encode()).hexdigest()
            
            # 3. Compute current hash (linking to previous)
            timestamp = datetime.now(timezone.utc).isoformat()
            chain_data = f"{previous_hash}{payload_hash}{timestamp}{event_id}"
            current_hash = hashlib.sha256(chain_data.encode()).hexdigest()

            # 4. Insert
            cursor = await db.execute(
                """
                INSERT INTO audit_logs (
                    event_id, event_type, timestamp, source_component, 
                    source_instance, correlation_id, payload_json, 
                    previous_hash, payload_hash, current_hash, signature
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event_id, event_type, timestamp, source_component,
                    source_instance, correlation_id, payload_json,
                    previous_hash, payload_hash, current_hash, signature
                )
            )
            await db.commit()
            return int(cursor.lastrowid)

    async def verify_chain(self) -> bool:
        """
        Verify the integrity of the entire audit chain.
        """
        async with aiosqlite.connect(self.sqlite_path) as db:
            async with db.execute(
                "SELECT id, event_id, payload_json, timestamp, previous_hash, current_hash FROM audit_logs ORDER BY id ASC"
            ) as cursor:
                last_calculated_hash = "GENESIS"
                async for row in cursor:
                    rid, eid, p_json, ts, prev_h, curr_h = row
                    
                    if prev_h != last_calculated_hash:
                        logger.error("Audit chain broken at ID %d: Previous hash mismatch", rid)
                        return False
                    
                    p_hash = hashlib.sha256(p_json.encode()).hexdigest()
                    calc_h = hashlib.sha256(f"{prev_h}{p_hash}{ts}{eid}".encode()).hexdigest()
                    
                    if curr_h != calc_h:
                        logger.error("Audit chain broken at ID %d: Current hash mismatch", rid)
                        return False
                    
                    last_calculated_hash = curr_h
        return True
