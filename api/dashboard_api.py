"""Dashboard and control-plane API."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query

from trading_system.config.models import BacktestRequest, OrderRequest, TradingMode
from trading_system.config.settings import DependencyContainer

logger = logging.getLogger(__name__)


def create_dashboard_router(container: DependencyContainer, auth_guard: object) -> APIRouter:
    """Create API router for dashboard and execution controls."""
    router = APIRouter(prefix="/api", tags=["dashboard"])

    @router.get("/health")
    async def health() -> Dict[str, Any]:
        trade_db = await container.trade_memory.heartbeat()
        return {
            "status": "ok",
            "app": container.settings.app_name,
            "event_bus": container.event_bus.stats(),
            "trade_db": trade_db,
            "kill_switch_active": container.execution_engine.kill_switch.is_active,
        }

    @router.get("/risk")
    async def risk(
        mode: TradingMode = Query(default=TradingMode.PAPER),
        _auth: None = Depends(auth_guard),
    ) -> Dict[str, Any]:
        snapshot = await container.global_state.snapshot(mode)
        return container.risk_guardian.portfolio_risk_snapshot(
            snapshot=snapshot,
            kill_switch_active=container.execution_engine.kill_switch.is_active,
        )

    @router.get("/positions")
    async def positions(
        mode: TradingMode = Query(default=TradingMode.PAPER),
        _auth: None = Depends(auth_guard),
    ) -> Dict[str, Any]:
        snapshot = await container.global_state.snapshot(mode)
        return {"mode": mode.value, "positions": snapshot.positions}

    @router.post("/orders")
    async def submit_order(
        order: OrderRequest,
        human_approved: bool = False,
        _auth: None = Depends(auth_guard),
    ) -> Dict[str, Any]:
        result = await container.execution_engine.submit_order(order, human_approved=human_approved)
        return result.model_dump()

    @router.post("/backtest")
    async def backtest(
        request: BacktestRequest,
        _auth: None = Depends(auth_guard),
    ) -> Dict[str, Any]:
        result = await container.boss_agent.backtester.run(request)
        return {
            "request": request.model_dump(),
            "metrics": result.metrics.model_dump(),
            "trades": result.trades[:100],
            "walk_forward": result.walk_forward,
        }

    @router.get("/whales")
    async def whales(coin: str = "BTC", _auth: None = Depends(auth_guard)) -> Dict[str, Any]:
        return await container.boss_agent.whale_agent.run(coin)

    @router.get("/briefing")
    async def daily_briefing(_auth: None = Depends(auth_guard)) -> Dict[str, Any]:
        """
        Daily briefing generator for operations reviews.
        """
        watchlist = container.settings.watchlist
        research = await asyncio.gather(
            *(container.boss_agent.technical_agent.run(symbol=s, timeframe="1d") for s in watchlist),
            return_exceptions=True,
        )
        items: List[Dict[str, Any]] = []
        for symbol, result in zip(watchlist, research):
            if isinstance(result, Exception):
                items.append({"symbol": symbol, "error": str(result)})
            else:
                items.append(result)
        risk_snapshot = await container.global_state.snapshot(TradingMode.PAPER)
        risk = container.risk_guardian.portfolio_risk_snapshot(
            snapshot=risk_snapshot,
            kill_switch_active=container.execution_engine.kill_switch.is_active,
        )
        whale = await container.boss_agent.whale_agent.run("BTC")
        macro = await container.boss_agent.macro_agent.run()
        return {
            "research": items,
            "macro": macro,
            "whale": whale,
            "risk": risk,
        }

    @router.post("/kill-switch/trigger")
    async def trigger_kill_switch(note: str, _auth: None = Depends(auth_guard)) -> Dict[str, Any]:
        container.execution_engine.kill_switch.manual_trigger(note)
        return {"active": True, "reason": container.execution_engine.kill_switch.state.reason}

    @router.post("/kill-switch/reset")
    async def reset_kill_switch(_auth: None = Depends(auth_guard)) -> Dict[str, Any]:
        container.execution_engine.kill_switch.reset()
        return {"active": False}

    @router.post("/live-approvals/request")
    async def create_live_approval_ticket(
        order: OrderRequest,
        requested_by: str = "operator",
        _auth: None = Depends(auth_guard),
    ) -> Dict[str, Any]:
        try:
            ticket = await container.live_approval_manager.create_ticket(order=order, requested_by=requested_by)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"ticket": ticket}

    @router.post("/live-approvals/{ticket_id}/approve")
    async def approve_live_approval_ticket(
        ticket_id: str,
        approved_by: str = "supervisor",
        _auth: None = Depends(auth_guard),
    ) -> Dict[str, Any]:
        try:
            ticket = await container.live_approval_manager.approve_ticket(ticket_id=ticket_id, approved_by=approved_by)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"ticket": ticket}

    @router.get("/live-approvals/{ticket_id}")
    async def get_live_approval_ticket(
        ticket_id: str,
        _auth: None = Depends(auth_guard),
    ) -> Dict[str, Any]:
        ticket = await container.live_approval_manager.get_ticket(ticket_id=ticket_id)
        if not ticket:
            return {"ticket": None}
        return {"ticket": ticket}

    return router
