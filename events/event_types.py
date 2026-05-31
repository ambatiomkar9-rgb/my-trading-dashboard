from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


class EventType(str, Enum):
    """Canonical event names for HERMES v5.2."""

    # Core Execution & Safety
    SIGNAL_EMITTED = "SIGNAL_EMITTED"
    RISK_CHECK_REQUESTED = "RISK_CHECK_REQUESTED"
    RISK_APPROVED = "RISK_APPROVED"
    RISK_REJECTED = "RISK_REJECTED"
    EXECUTION_COMMAND = "EXECUTION_COMMAND"
    ORDER_SUBMITTED = "ORDER_SUBMITTED"
    ORDER_FILLED = "ORDER_FILLED"
    ORDER_REJECTED = "ORDER_REJECTED"
    ORDER_MODIFIED = "ORDER_MODIFIED" # Added for completeness
    KILL_SWITCH_TRIGGERED = "KILL_SWITCH_TRIGGERED"
    HEARTBEAT = "HEARTBEAT"
    RECONCILIATION_FAILED = "RECONCILIATION_FAILED" # Added for completeness

    # Research & Validation
    STRATEGY_GENERATED = "STRATEGY_GENERATED"
    VALIDATION_STARTED = "VALIDATION_STARTED"
    VALIDATION_PASSED = "VALIDATION_PASSED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    STRATEGY_APPROVED = "STRATEGY_APPROVED"
    REGISTRY_ROLLBACK = "REGISTRY_ROLLBACK"
    
    # Compliance
    ORDER_TO_TRADE_RATIO_ALERT = "ORDER_TO_TRADE_RATIO_ALERT"
    SEBI_CERTIFICATION_ALERT = "SEBI_CERTIFICATION_ALERT"
    ANNUAL_COMPLIANCE_EXPORT = "ANNUAL_COMPLIANCE_EXPORT"
    PHYSICAL_KILL_SWITCH_TEST = "PHYSICAL_KILL_SWITCH_TEST"
    
    # Legacy / Additional
    WHALE_ALERT = "WhaleAlert"
    MACRO_ALERT = "MacroAlert"
    SYSTEM_HEARTBEAT = "SystemHeartbeat" # Redundant with HEARTBEAT, but keeping for now


@dataclass(slots=True)
class Event:
    """Base event envelope."""

    event_type: EventType
    source: str
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def as_dict(self) -> Dict[str, Any]:
        """Serialize event."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "source": self.source,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "occurred_at": self.occurred_at.isoformat(),
        }


def build_event(
    event_type: EventType,
    source: str,
    payload: Dict[str, Any],
    correlation_id: Optional[str] = None,
) -> Event:
    """Factory helper for typed events."""
    return Event(
        event_type=event_type,
        source=source,
        payload=payload,
        correlation_id=correlation_id,
    )
