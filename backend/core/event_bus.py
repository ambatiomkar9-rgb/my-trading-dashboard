"""Async in-process event bus for market, signal, and execution events."""
from __future__ import annotations

import asyncio
import inspect
import logging
from collections import defaultdict
from typing import Any, Awaitable, Callable, DefaultDict, Optional

try:
    from backend.core.event_store import EventStore  # type: ignore
except ModuleNotFoundError:  # noqa: BLE001
    from core.event_store import EventStore  # type: ignore

logger = logging.getLogger(__name__)

EventCallback = Callable[[Any], Awaitable[None] | None]


class AsyncEventBus:
    """Minimal async pub/sub bus with optional persistence to the event store."""

    def __init__(self, event_store: Optional[EventStore] = None):
        self._event_store = event_store
        self._subscribers: DefaultDict[str, list[EventCallback]] = defaultdict(list)

    def subscribe(self, event_name: str, callback: EventCallback) -> None:
        """Register a callback for an event name."""
        name = str(event_name).strip()
        if not name or callback in self._subscribers[name]:
            return
        self._subscribers[name].append(callback)

    def unsubscribe(self, event_name: str, callback: EventCallback) -> None:
        """Remove a callback from an event name."""
        name = str(event_name).strip()
        if not name:
            return
        callbacks = self._subscribers.get(name)
        if not callbacks:
            return
        self._subscribers[name] = [cb for cb in callbacks if cb != callback]
        if not self._subscribers[name]:
            self._subscribers.pop(name, None)

    async def publish(self, event_name: str, payload: Any, source: str = "event_bus") -> None:
        """Publish an event to all subscribers and optionally persist it."""
        try:
            name = str(event_name).strip()
            if not name:
                return

            if self._event_store is not None:
                for attempt in range(3):
                    try:
                        await asyncio.to_thread(
                            self._event_store.store_event,
                            name,
                            payload if isinstance(payload, dict) else {"value": payload},
                            source=source,
                        )
                        break
                    except Exception as exc:  # noqa: BLE001
                        if attempt < 2:
                            logger.warning("Event persist attempt %d failed for %s: %s", attempt + 1, name, exc)
                            await asyncio.sleep(0.5 * (attempt + 1))
                        else:
                            logger.error("Event %s lost after 3 attempts: %s", name, exc)

            callbacks = list(self._subscribers.get(name, []))
            if not callbacks:
                return

            awaitables: list[Awaitable[None]] = []
            for callback in callbacks:
                try:
                    result = callback(payload)
                    if inspect.isawaitable(result):
                        awaitables.append(result)
                except Exception as exc:  # noqa: BLE001
                    logger.error("Event callback error for %s: %s", name, exc)

            if awaitables:
                results = await asyncio.gather(*awaitables, return_exceptions=True)
                for result in results:
                    if isinstance(result, Exception):
                        logger.error("Event callback raised: %s", result)
        except Exception as exc:  # noqa: BLE001
            logger.error("publish(%s) failed: %s", event_name, exc)


def build_event_bus(event_store: Optional[EventStore] = None) -> AsyncEventBus:
    """Create an event bus instance."""
    return AsyncEventBus(event_store=event_store)
