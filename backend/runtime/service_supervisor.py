"""Service Supervisor — manages agent lifecycle with health checks, auto-restart, and dependency ordering.

This is the single entry point that starts, monitors, and restarts all agents.
It replaces the ad-hoc task spawning in TradingSystemRuntime.
"""
from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Coroutine, Optional

logger = logging.getLogger(__name__)


class AgentState(str, Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    RESTARTING = "restarting"
    FAILED = "failed"


@dataclass
class AgentDescriptor:
    """Metadata about a managed agent."""
    name: str
    state: AgentState = AgentState.STOPPED
    task: Optional[asyncio.Task[Any]] = field(default=None, repr=False)
    restart_count: int = 0
    last_healthy_at: float = 0.0
    last_started_at: float = 0.0
    last_error: Optional[str] = None
    depends_on: list[str] = field(default_factory=list)
    health_check: Optional[Callable[[], Coroutine[Any, Any, bool]]] = field(default=None, repr=False)
    start_fn: Optional[Callable[[], Coroutine[Any, Any, None]]] = field(default=None, repr=False)
    stop_fn: Optional[Callable[[], Coroutine[Any, Any, None]]] = field(default=None, repr=False)
    max_restarts: int = 5
    health_interval: float = 30.0
    required: bool = False


class ServiceSupervisor:
    """Manages agent lifecycle with health checks, auto-restart, and dependency ordering.

    Usage:
        supervisor = ServiceSupervisor()
        supervisor.register("technical", start_fn=start, stop_fn=stop, health_check=check)
        supervisor.register("news", start_fn=start, depends_on=["technical"])
        await supervisor.start_all()
        # ... later ...
        await supervisor.stop_all()
    """

    def __init__(self) -> None:
        self._agents: dict[str, AgentDescriptor] = {}
        self._health_task: Optional[asyncio.Task[None]] = None
        self._running = False

    def register(
        self,
        name: str,
        start_fn: Optional[Callable[[], Coroutine[Any, Any, None]]] = None,
        stop_fn: Optional[Callable[[], Coroutine[Any, Any, None]]] = None,
        health_check: Optional[Callable[[], Coroutine[Any, Any, bool]]] = None,
        depends_on: Optional[list[str]] = None,
        max_restarts: int = 5,
        health_interval: float = 30.0,
        required: bool = False,
    ) -> None:
        self._agents[name] = AgentDescriptor(
            name=name,
            start_fn=start_fn,
            stop_fn=stop_fn,
            health_check=health_check,
            depends_on=depends_on or [],
            max_restarts=max_restarts,
            health_interval=health_interval,
            required=required,
        )

    def _topological_order(self) -> list[str]:
        """Return agent names in dependency order (dependencies first)."""
        visited: set[str] = set()
        order: list[str] = []

        def _visit(name: str) -> None:
            if name in visited:
                return
            visited.add(name)
            agent = self._agents.get(name)
            if agent is None:
                return
            for dep in agent.depends_on:
                _visit(dep)
            order.append(name)

        for name in self._agents:
            _visit(name)
        return order

    async def start_all(self) -> None:
        """Start all registered agents in dependency order."""
        self._running = True
        order = self._topological_order()
        logger.info("ServiceSupervisor starting %d agents: %s", len(order), order)

        for name in order:
            agent = self._agents.get(name)
            if agent is None or agent.start_fn is None:
                continue

            # Check dependencies are healthy
            deps_ok = all(
                self._agents.get(dep) is not None
                and self._agents[dep].state in (AgentState.RUNNING, AgentState.HEALTHY)
                for dep in agent.depends_on
            )
            if not deps_ok:
                logger.warning("Skipping %s: dependencies not healthy", name)
                agent.state = AgentState.FAILED
                agent.last_error = "dependencies not healthy"
                continue

            await self._start_agent(agent)

        # Start health monitor
        self._health_task = asyncio.create_task(self._health_monitor_loop())
        logger.info("ServiceSupervisor started all agents")

    async def _start_agent(self, agent: AgentDescriptor) -> None:
        """Start a single agent with restart logic."""
        try:
            agent.state = AgentState.STARTING
            agent.last_started_at = time.time()
            logger.info("Starting agent: %s", agent.name)

            if agent.start_fn is not None:
                await agent.start_fn()

            agent.state = AgentState.RUNNING
            agent.restart_count = 0
            agent.last_error = None
            logger.info("Agent started: %s", agent.name)
        except Exception as exc:
            agent.state = AgentState.FAILED
            agent.last_error = str(exc)[:500]
            logger.error("Agent %s failed to start: %s", agent.name, exc)

            if agent.required and agent.restart_count < agent.max_restarts:
                agent.restart_count += 1
                agent.state = AgentState.RESTARTING
                logger.info("Auto-restarting required agent %s (attempt %d)", agent.name, agent.restart_count)
                await asyncio.sleep(2 ** agent.restart_count)  # Exponential backoff
                await self._start_agent(agent)

    async def _health_monitor_loop(self) -> None:
        """Periodically check agent health and restart unhealthy agents."""
        while self._running:
            try:
                await asyncio.sleep(10)
                now = time.time()

                for name, agent in self._agents.items():
                    if agent.state in (AgentState.STOPPED, AgentState.FAILED):
                        continue
                    if agent.health_check is None:
                        continue
                    if now - agent.last_healthy_at < agent.health_interval:
                        continue

                    try:
                        healthy = await agent.health_check()
                        if healthy:
                            agent.state = AgentState.HEALTHY
                            agent.last_healthy_at = now
                        else:
                            agent.state = AgentState.UNHEALTHY
                            agent.last_error = "health check returned false"
                            logger.warning("Agent %s is unhealthy", name)
                            if agent.restart_count < agent.max_restarts:
                                await self._restart_agent(agent)
                    except Exception as exc:
                        agent.state = AgentState.UNHEALTHY
                        agent.last_error = str(exc)[:500]
                        logger.warning("Agent %s health check failed: %s", name, exc)
                        if agent.restart_count < agent.max_restarts:
                            await self._restart_agent(agent)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("Health monitor error: %s", exc)

    async def _restart_agent(self, agent: AgentDescriptor) -> None:
        """Stop and restart an agent."""
        agent.state = AgentState.RESTARTING
        agent.restart_count += 1
        logger.info("Restarting agent %s (attempt %d)", agent.name, agent.restart_count)

        if agent.stop_fn is not None:
            try:
                await agent.stop_fn()
            except Exception as exc:
                logger.warning("Agent %s stop failed during restart: %s", agent.name, exc)

        if agent.task is not None and not agent.task.done():
            agent.task.cancel()

        await asyncio.sleep(min(2 ** agent.restart_count, 30))  # Exponential backoff, max 30s
        await self._start_agent(agent)

    async def stop_all(self) -> None:
        """Stop all agents in reverse dependency order."""
        self._running = False
        if self._health_task is not None:
            self._health_task.cancel()
            try:
                await self._health_task
            except asyncio.CancelledError:
                pass

        order = list(reversed(self._topological_order()))
        logger.info("ServiceSupervisor stopping %d agents", len(order))

        for name in order:
            agent = self._agents.get(name)
            if agent is None:
                continue
            if agent.stop_fn is not None:
                try:
                    await agent.stop_fn()
                except Exception as exc:
                    logger.warning("Agent %s stop failed: %s", name, exc)
            if agent.task is not None and not agent.task.done():
                agent.task.cancel()
            agent.state = AgentState.STOPPED

    def status(self) -> dict[str, Any]:
        """Return status snapshot of all agents."""
        return {
            name: {
                "state": agent.state.value,
                "restart_count": agent.restart_count,
                "last_error": agent.last_error,
                "last_healthy_at": agent.last_healthy_at,
                "depends_on": agent.depends_on,
                "required": agent.required,
            }
            for name, agent in self._agents.items()
        }
