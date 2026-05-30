"""Reusable event handlers for logging and state updates."""

from __future__ import annotations

import logging
from typing import Awaitable, Callable

from trading_system.events.event_bus import AsyncEventBus
from trading_system.events.event_types import Event, EventType
from trading_system.memory.global_state import GlobalState
from trading_system.memory.trade_memory import TradeMemoryRepository
from trading_system.memory.audit_memory import AuditMemoryRepository

logger = logging.getLogger(__name__)


async def log_all_events(event: Event) -> None:
    """Structured event logging handler."""
    logger.info("Event=%s source=%s payload=%s", event.event_type.value, event.source, event.payload)


async def on_kill_switch(event: Event) -> None:
    """Escalation logging for kill switch triggers."""
    logger.error("KILL SWITCH TRIGGERED: %s", event.payload)


def register_default_handlers(
    bus: AsyncEventBus,
    state: GlobalState,
    trade_memory: TradeMemoryRepository,
    audit_memory: AuditMemoryRepository,
) -> None:
    """Register default handlers used by orchestration layer."""

    async def audit_logger(event: Event) -> None:
        """WORM audit logger with hash chaining."""
        try:
            await audit_memory.log_event(
                event_id=event.event_id,
                event_type=event.event_type.value,
                source_component=event.source,
                source_instance="local-main", # Placeholder
                correlation_id=event.correlation_id or "NONE",
                payload=event.payload
            )
        except Exception:
            logger.exception("Failed to write to audit chain")

    async def trade_executed_handler(event: Event) -> None:
        logger.info("Trade executed event received: %s", event.payload.get("order_id"))

    # Register Audit Logger for ALL events
    for etype in EventType:
        bus.subscribe(etype, audit_logger)

    bus.subscribe(EventType.SIGNAL_EMITTED, log_all_events)
    bus.subscribe(EventType.RISK_APPROVED, log_all_events)
    bus.subscribe(EventType.RISK_REJECTED, log_all_events)
    bus.subscribe(EventType.TRADE_EXECUTED, trade_executed_handler)
    bus.subscribe(EventType.KILL_SWITCH_TRIGGERED, on_kill_switch)
