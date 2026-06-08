"""WebSocket reconnect helper with backoff, heartbeat checks, and resubscribe support."""
from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))


def _is_market_hours() -> bool:
    """Check if current time is within Indian market hours (9:15 AM - 3:30 PM IST)."""
    now = datetime.now(IST)
    if now.weekday() >= 5:
        return False
    market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
    return market_open <= now <= market_close


class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"


class ReconnectManager:
    MAX_DELAY = 60
    MAX_RETRIES = 20
    DAILY_RETRY_RESET = 86400  # Reset retry counter after 24 hours

    def __init__(
        self,
        ws_url: str,
        get_headers: Callable[[], Awaitable[dict[str, str]]],
        on_message: Callable[[Any], Awaitable[None]],
        heartbeat_interval: int = 30,
    ) -> None:
        self.ws_url = ws_url
        self.get_headers = get_headers
        self.on_message = on_message
        self.heartbeat_interval = heartbeat_interval
        self.state = ConnectionState.DISCONNECTED
        self._ws: Any = None
        self._retries = 0
        self._last_msg_at = 0.0
        self._last_connected_at: float = 0.0
        self._last_daily_reset_at: float = 0.0
        self._subscriptions: list[dict[str, Any]] = []
        self._running = False
        self._listen_task: asyncio.Task | None = None
        self._heartbeat_task: asyncio.Task | None = None

    def is_healthy(self) -> bool:
        """Return True if the connection is alive or recently was."""
        if self.state in (ConnectionState.CONNECTED, ConnectionState.CONNECTING):
            return True
        # Allow a grace period for transient disconnects (max 120s since last good message)
        if self._last_msg_at > 0 and (time.time() - self._last_msg_at) < 120:
            return True
        return False

    def _maybe_daily_reset(self) -> None:
        """Reset retry counter once per day so overnight disconnects don't block morning reconnection."""
        now = time.time()
        if self._last_daily_reset_at == 0:
            self._last_daily_reset_at = now
            return
        if now - self._last_daily_reset_at >= self.DAILY_RETRY_RESET:
            if self._retries > 0:
                logger.info(
                    "Daily retry reset: clearing %d retries (was in state %s)",
                    self._retries, self.state.value,
                )
                self._retries = 0
                self._last_daily_reset_at = now
                # If we were FAILED, allow reconnection
                if self.state == ConnectionState.FAILED:
                    self.state = ConnectionState.DISCONNECTED

    async def connect(self) -> None:
        """Start the reconnect loop. Runs until close() is called."""
        try:
            self._running = True
            await self._loop()
        except Exception as exc:  # noqa: BLE001
            logger.error("ReconnectManager.connect failed: %s", exc)
            self.state = ConnectionState.FAILED

    async def send(self, message: dict[str, Any]) -> None:
        """Send a JSON message and keep it for future resubscribe."""
        try:
            if message not in self._subscriptions:
                self._subscriptions.append(message)
            if self._ws and self.state == ConnectionState.CONNECTED:
                await self._ws.send(json.dumps(message))
        except Exception as exc:  # noqa: BLE001
            logger.error("Send failed: %s", exc)

    async def close(self) -> None:
        """Stop reconnecting and close the active socket."""
        try:
            self._running = False
            self._cancel_tasks()
            if self._ws:
                try:
                    await self._ws.close()
                except Exception:  # noqa: BLE001
                    pass
            self.state = ConnectionState.DISCONNECTED
        except Exception as exc:  # noqa: BLE001
            logger.error("Close failed: %s", exc)

    async def _loop(self) -> None:
        try:
            import websockets
        except ImportError as exc:  # pragma: no cover - dependency issue
            raise RuntimeError("Run: pip install websockets>=12.0") from exc

        while self._running:
            # Check daily reset before entering retry logic
            self._maybe_daily_reset()

            self.state = ConnectionState.CONNECTING
            try:
                headers = await self.get_headers()
                self._ws = await websockets.connect(
                    self.ws_url,
                    extra_headers=headers,
                    ping_interval=20,
                    ping_timeout=10,
                    close_timeout=5,
                )
                self.state = ConnectionState.CONNECTED
                self._retries = 0
                self._last_msg_at = time.time()
                self._last_connected_at = time.time()
                logger.info("WebSocket connected")

                await self._resubscribe()

                self._listen_task = asyncio.create_task(self._listen())
                self._heartbeat_task = asyncio.create_task(self._heartbeat())
                await self._listen_task
            except Exception as exc:  # noqa: BLE001
                logger.warning("WebSocket error: %s", exc)
            finally:
                self._cancel_tasks()
                self.state = ConnectionState.DISCONNECTED

            if not self._running:
                break

            self._retries += 1
            if self._retries > self.MAX_RETRIES:
                self.state = ConnectionState.FAILED
                logger.error("Max retries exceeded. Stopping.")
                return

            if _is_market_hours():
                delay = min(2 ** (self._retries - 1), self.MAX_DELAY)
                self.state = ConnectionState.RECONNECTING
                logger.info("Reconnecting in %ds (attempt %d)", delay, self._retries)
                await asyncio.sleep(delay)
            else:
                # After hours: fixed 5-minute delay to avoid burning retries overnight
                self.state = ConnectionState.RECONNECTING
                logger.info("After hours: waiting 300s before reconnect (attempt %d)", self._retries)
                await asyncio.sleep(300)

    async def _listen(self) -> None:
        try:
            async for raw in self._ws:
                self._last_msg_at = time.time()
                try:
                    await self.on_message(raw)
                except Exception as exc:  # noqa: BLE001
                    logger.error("on_message error: %s", exc)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            logger.warning("Listen ended: %s", exc)

    async def _heartbeat(self) -> None:
        try:
            while self._running and self.state == ConnectionState.CONNECTED:
                await asyncio.sleep(self.heartbeat_interval)
                stale = time.time() - self._last_msg_at
                if stale > self.heartbeat_interval * 2:
                    logger.warning("Stale WS (%.0fs). Forcing reconnect.", stale)
                    if self._listen_task and not self._listen_task.done():
                        self._listen_task.cancel()
                    if self._ws:
                        try:
                            await self._ws.close()
                        except Exception:  # noqa: BLE001
                            pass
                    return
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            logger.warning("Heartbeat ended: %s", exc)

    async def _resubscribe(self) -> None:
        try:
            for sub in self._subscriptions:
                try:
                    if self._ws:
                        await self._ws.send(json.dumps(sub))
                    await asyncio.sleep(0.05)
                except Exception as exc:  # noqa: BLE001
                    logger.error("Resubscribe error: %s", exc)
        except Exception as exc:  # noqa: BLE001
            logger.error("Resubscribe loop failed: %s", exc)

    def _cancel_tasks(self) -> None:
        for task in (self._listen_task, self._heartbeat_task):
            if task and not task.done():
                task.cancel()
        self._listen_task = None
        self._heartbeat_task = None

