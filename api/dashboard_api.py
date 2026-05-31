"""Dashboard and control-plane API."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from trading_system.config.models import BacktestRequest, OrderRequest, TradingMode
from trading_system.config.settings import DependencyContainer
from trading_system.registry.registry_service import RegistryService

logger = logging.getLogger(__name__)

# --- RBAC Roles ---
class UserRole(str, Enum):
    VIEWER = "viewer"
    OPERATOR = "operator"
    ADMIN = "admin"

class CurrentUser(BaseModel):
    id: UUID = Field(default_factory=UUID)
    roles: List[UserRole] = Field(default_factory=lambda: [UserRole.VIEWER])

def get_current_user(api_key: str = Depends(Query(alias="api_key"))) -> CurrentUser:
    """Simulate user roles based on API key or other auth (for RBAC testing)."""
    # In a real system, this would come from a JWT or a proper auth service.
    # For now, simple mapping for testing roles.
    if api_key == "admin_key":
        return CurrentUser(roles=[UserRole.ADMIN, UserRole.OPERATOR, UserRole.VIEWER])
    elif api_key == "operator_key":
        return CurrentUser(roles=[UserRole.OPERATOR, UserRole.VIEWER])
    else:
        return CurrentUser(roles=[UserRole.VIEWER])


def create_dashboard_router(container: DependencyContainer, auth_guard: object) -> APIRouter:
    """Create API router for dashboard and execution controls."""
    router = APIRouter(prefix="/api", tags=["dashboard"])

    @router.get("/health")
    async def health() -> Dict[str, Any]:
        trade_db = await container.trade_memory.heartbeat()
        audit_db_ok = await container.audit_memory.verify_chain() # Check audit chain integrity
        return {
            "status": "ok",
            "app": container.settings.app_name,
            "event_bus": container.event_bus.stats(),
            "trade_db": trade_db,
            "audit_chain_valid": audit_db_ok,
            "kill_switch_active": container.execution_engine.kill_switch.is_active,
            "reconciliation_running": container.reconciliation_engine is not None,
            "research_running": container.research_service is not None,
            "validation_running": container.validation_service is not None,
            "registry_running": container.registry_service is not None,
        }

    @router.get("/risk")
    async def risk(
        mode: TradingMode = Query(default=TradingMode.PAPER),
        _auth: None = Depends(auth_guard),
        current_user: CurrentUser = Depends(get_current_user),
    ) -> Dict[str, Any]:
        if UserRole.VIEWER not in current_user.roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view risk.")
        
        snapshot = await container.global_state.snapshot(mode)
        return container.risk_guardian.portfolio_risk_snapshot(
            snapshot=snapshot,
            kill_switch_active=container.execution_engine.kill_switch.is_active,
        )

    @router.get("/positions")
    async def positions(
        mode: TradingMode = Query(default=TradingMode.PAPER),
        _auth: None = Depends(auth_guard),
        current_user: CurrentUser = Depends(get_current_user),
    ) -> Dict[str, Any]:
        if UserRole.VIEWER not in current_user.roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view positions.")
        snapshot = await container.global_state.snapshot(mode)
        return {"mode": mode.value, "positions": snapshot.positions}

    @router.post("/orders")
    async def submit_order(
        order: OrderRequest,
        human_approved: bool = False,
        _auth: None = Depends(auth_guard),
        current_user: CurrentUser = Depends(get_current_user),
    ) -> Dict[str, Any]:
        if UserRole.OPERATOR not in current_user.roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to submit orders.")
        
        result = await container.execution_engine.submit_order(order, human_approved=human_approved)
        return result.model_dump()

    @router.post("/backtest")
    async def backtest(
        request: BacktestRequest,
        _auth: None = Depends(auth_guard),
        current_user: CurrentUser = Depends(get_current_user),
    ) -> Dict[str, Any]:
        if UserRole.OPERATOR not in current_user.roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to run backtests.")
        
        result = await container.boss_agent.backtester.run(request)
        return {
            "request": request.model_dump(),
            "metrics": result.metrics.model_dump(),
            "trades": result.trades[:100],
            "walk_forward": result.walk_forward,
        }

    @router.get("/whales")
    async def whales(
        coin: str = "BTC", 
        _auth: None = Depends(auth_guard),
        current_user: CurrentUser = Depends(get_current_user),
    ) -> Dict[str, Any]:
        if UserRole.VIEWER not in current_user.roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view whale data.")
        return await container.boss_agent.whale_agent.run(coin)

    @router.get("/briefing")
    async def daily_briefing(
        _auth: None = Depends(auth_guard),
        current_user: CurrentUser = Depends(get_current_user),
    ) -> Dict[str, Any]:
        if UserRole.VIEWER not in current_user.roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view briefings.")
            
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
    async def trigger_kill_switch(
        note: str, 
        _auth: None = Depends(auth_guard),
        current_user: CurrentUser = Depends(get_current_user),
    ) -> Dict[str, Any]:
        if UserRole.ADMIN not in current_user.roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to trigger kill switch.")
        
        container.execution_engine.kill_switch.manual_trigger(note)
        return {"active": True, "reason": container.execution_engine.kill_switch.state.reason}

    @router.post("/kill-switch/reset")
    async def reset_kill_switch(
        _auth: None = Depends(auth_guard),
        current_user: CurrentUser = Depends(get_current_user),
    ) -> Dict[str, Any]:
        if UserRole.ADMIN not in current_user.roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to reset kill switch.")
        
        container.execution_engine.kill_switch.reset()
        return {"active": False}

    @router.post("/live-approvals/request")
    async def create_live_approval_ticket(
        order: OrderRequest,
        requested_by: str = "operator",
        _auth: None = Depends(auth_guard),
        current_user: CurrentUser = Depends(get_current_user),
    ) -> Dict[str, Any]:
        if UserRole.OPERATOR not in current_user.roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to request live approvals.")
        
        try:
            ticket = await container.live_approval_manager.create_ticket(order=order, requested_by=requested_by)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        return {"ticket": ticket}

    @router.post("/live-approvals/{ticket_id}/approve")
    async def approve_live_approval_ticket(
        ticket_id: str,
        approved_by: str = "supervisor",
        _auth: None = Depends(auth_guard),
        current_user: CurrentUser = Depends(get_current_user),
    ) -> Dict[str, Any]:
        if UserRole.ADMIN not in current_user.roles: # Only admin can approve
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to approve live approvals.")
        
        try:
            ticket = await container.live_approval_manager.approve_ticket(ticket_id=ticket_id, approved_by=approved_by)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        return {"ticket": ticket}

    @router.get("/live-approvals/{ticket_id}")
    async def get_live_approval_ticket(
        ticket_id: str,
        _auth: None = Depends(auth_guard),
        current_user: CurrentUser = Depends(get_current_user),
    ) -> Dict[str, Any]:
        if UserRole.VIEWER not in current_user.roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view live approval tickets.")
        ticket = await container.live_approval_manager.get_ticket(ticket_id=ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval ticket not found.")
        return {"ticket": ticket}
        
    # --- HERMES v5.2 Registry Endpoints ---
    @router.get("/strategies")
    async def list_strategies(
        status: Optional[str] = Query(None),
        limit: int = Query(100, ge=1, le=1000),
        offset: int = Query(0, ge=0),
        _auth: None = Depends(auth_guard),
        current_user: CurrentUser = Depends(get_current_user),
    ) -> Dict[str, Any]:
        if UserRole.VIEWER not in current_user.roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to list strategies.")
        
        if not container.registry_service:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Registry Service not running.")
        
        strategies = await container.registry_service.list_strategies(status=status, limit=limit, offset=offset)
        total = await container.registry_service.count_strategies(status=status)
        return {"strategies": strategies, "total": total, "limit": limit, "offset": offset}

    @router.post("/strategies/{strategy_id}/approve")
    async def approve_strategy(
        strategy_id: UUID,
        approver_id: UUID = Field(default_factory=UUID), # In real system, this would come from JWT claims
        approver_weight: int = 1, # Default weight for operator, admin would be higher
        signature: str = "UNSIGNED", # Placeholder for Ed25519 HSM signature
        emergency_override: bool = False,
        _auth: None = Depends(auth_guard),
        current_user: CurrentUser = Depends(get_current_user),
    ) -> Dict[str, Any]:
        if UserRole.OPERATOR not in current_user.roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to approve strategies.")
        
        if not container.registry_service:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Registry Service not running.")

        # Admin role gets higher weight by default for this API.
        if UserRole.ADMIN in current_user.roles:
            approver_weight = 2 # Admin weight = 2 as per spec
        
        try:
            approved = await container.registry_service.approve_strategy(
                strategy_id=str(strategy_id),
                approver_id=approver_id,
                approver_weight=approver_weight,
                signature=signature,
            )
            if approved:
                return {"message": f"Strategy {strategy_id} approved successfully."}
            else:
                return {"message": f"Approval for strategy {strategy_id} recorded. Quorum not yet met."}
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        except HTTPException:
            raise
        except Exception as exc:
            logger.exception("Error approving strategy %s: %s", strategy_id, exc)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during approval.") from exc

    @router.post("/strategies/{strategy_id}/rollback")
    async def rollback_strategy(
        strategy_id: UUID,
        target_version_id: UUID,
        reason: str,
        initiator_id: UUID = Field(default_factory=UUID),
        signature: str = "UNSIGNED", # Placeholder for Ed25519 HSM signature
        _auth: None = Depends(auth_guard),
        current_user: CurrentUser = Depends(get_current_user),
    ) -> Dict[str, Any]:
        if UserRole.ADMIN not in current_user.roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to rollback strategies.")
        
        if not container.registry_service:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Registry Service not running.")
        
        try:
            rolled_back = await container.registry_service.rollback_strategy(
                strategy_id=str(strategy_id),
                target_version_id=str(target_version_id),
                reason=reason,
                initiator_id=initiator_id,
                signature=signature,
            )
            if rolled_back:
                return {"message": f"Strategy {strategy_id} rolled back to version {target_version_id}."}
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rollback failed (e.g., invalid version or state).")
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        except HTTPException:
            raise
        except Exception as exc:
            logger.exception("Error rolling back strategy %s: %s", strategy_id, exc)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during rollback.") from exc

    return router
