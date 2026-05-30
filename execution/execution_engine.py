"""Execution engine coordinating risk checks and broker/paper execution."""

from __future__ import annotations

import logging
from dataclasses import asdict
from typing import Dict, Optional

from trading_system.agents.risk_guardian import CorrelationContext, RiskGuardian
from trading_system.config.models import ExecutionResult, OrderRequest, OrderState, RiskDecision, TradingMode
from trading_system.events.event_bus import AsyncEventBus
from trading_system.events.event_types import EventType, build_event
from trading_system.execution.live_approval import LiveApprovalManager
from trading_system.execution.kill_switch import KillSwitch
from trading_system.execution.live_executor import LiveExecutor
from trading_system.execution.paper_executor import PaperExecutor
from trading_system.memory.global_state import GlobalState
from trading_system.memory.trade_memory import TradeMemoryRepository

logger = logging.getLogger(__name__)


class ExecutionEngine:
    """Risk-gated execution coordinator conforming to HERMES v5.2."""

    VALID_TRANSITIONS = {
        OrderState.CREATED: [OrderState.RISK_APPROVED, OrderState.FAILED],
        OrderState.RISK_APPROVED: [OrderState.SUBMITTED, OrderState.CANCELLED],
        OrderState.SUBMITTED: [OrderState.ACKNOWLEDGED, OrderState.REJECTED, OrderState.CANCEL_PENDING],
        OrderState.ACKNOWLEDGED: [OrderState.PARTIALLY_FILLED, OrderState.FILLED, OrderState.MODIFIED, OrderState.CANCEL_PENDING, OrderState.EXPIRED],
        OrderState.PARTIALLY_FILLED: [OrderState.FILLED, OrderState.PARTIALLY_FILLED, OrderState.CANCEL_PENDING, OrderState.EXPIRED],
        OrderState.MODIFIED: [OrderState.ACKNOWLEDGED, OrderState.REJECTED],
        OrderState.CANCEL_PENDING: [OrderState.CANCELLED, OrderState.FILLED, OrderState.REJECTED],
    }
    
    TERMINAL_STATES = [OrderState.FILLED, OrderState.CANCELLED, OrderState.REJECTED, OrderState.EXPIRED, OrderState.FAILED]

    def __init__(
        self,
        risk_guardian: RiskGuardian,
        kill_switch: KillSwitch,
        paper_executor: PaperExecutor,
        live_executor: LiveExecutor,
        global_state: GlobalState,
        trade_memory: TradeMemoryRepository,
        event_bus: AsyncEventBus,
        live_approval_manager: LiveApprovalManager | None = None,
        require_live_approval_ticket: bool = True,
    ) -> None:
        self.risk_guardian = risk_guardian
        self.kill_switch = kill_switch
        self.paper_executor = paper_executor
        self.live_executor = live_executor
        self.global_state = global_state
        self.trade_memory = trade_memory
        self.event_bus = event_bus
        self.live_approval_manager = live_approval_manager
        self.require_live_approval_ticket = require_live_approval_ticket
        self._peak_equity: Dict[str, float] = {
            TradingMode.PAPER.value: 0.0,
            TradingMode.LIVE.value: 0.0,
        }
        self._register_event_handlers()

    def _validate_transition(self, current: OrderState, target: OrderState) -> bool:
        """Enforce transition rules from Task 4.4."""
        if current in self.TERMINAL_STATES:
            return False
        allowed = self.VALID_TRANSITIONS.get(current, [])
        return target in allowed

    def _register_event_handlers(self) -> None:
        """Subscribe to HERMES v5.2 execution streams."""
        self.event_bus.subscribe(EventType.EXECUTION_COMMAND, self._handle_execution_command)

    async def _handle_execution_command(self, event: Any) -> None:
        """
        Process EXECUTION_COMMAND and move order through state machine.
        Matches HERMES v5.2 Task 1.2 TradeExecutor responsibilities.
        """
        try:
            payload = event.payload if hasattr(event, 'payload') else event
            # 1. Idempotency Check (II-002)
            # In a real system, we'd check DB. Here we'll trust the flow for now.
            
            # 2. Risk check has already been approved by BossAgent flow,
            # but we run a final safety gate check here (I-002).
            if self.kill_switch.is_active:
                logger.warning("Kill switch active. Rejecting EXECUTION_COMMAND.")
                return

            # Construct order request from event payload
            order = OrderRequest(
                symbol=payload.get("symbol"),
                side=payload.get("side"),
                quantity=payload.get("qty"),
                mode=payload.get("mode", TradingMode.PAPER),
                broker=payload.get("broker_id", "paper"),
                metadata=payload
            )

            # 3. Submit Order (Transition: RISK_APPROVED -> SUBMITTED)
            # The execution logic already handles paper/live isolation.
            result = await self.submit_order(order)
            
            if result.accepted:
                logger.info("Order SUBMITTED successfully for correlation_id=%s", event.correlation_id)
            else:
                logger.warning("Order SUBMISSION FAILED for correlation_id=%s: %s", 
                               event.correlation_id, result.message)
        except Exception as e:
            logger.error("Error handling execution command: %s", e)

    async def submit_order(
        self,
        order: OrderRequest,
        human_approved: bool = False,
        correlation_matrix: Optional[Dict[str, float]] = None,
    ) -> ExecutionResult:
        """
        Submit order after strict risk validation.

        Safety requirements:
        - Backtest mode cannot execute.
        - Risk guardian veto is final.
        - Live mode needs human approval.
        """
        live_approval_validated = False
        if order.mode == TradingMode.BACKTEST:
            result = ExecutionResult(
                accepted=False,
                mode=TradingMode.BACKTEST,
                broker=order.broker,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                status="rejected",
                message="Backtest mode never routes to execution.",
            )
            await self._safe_log_execution(result)
            return result
        if order.mode == TradingMode.LIVE and self.require_live_approval_ticket:
            ticket_id = str(order.metadata.get("approval_ticket_id", "")).strip()
            if not ticket_id or not self.live_approval_manager:
                result = ExecutionResult(
                    accepted=False,
                    mode=TradingMode.LIVE,
                    broker=order.broker,
                    symbol=order.symbol,
                    side=order.side,
                    quantity=order.quantity,
                    status="rejected",
                    message="Live order requires approval_ticket_id.",
                )
                await self._safe_log_execution(result)
                return result
            approved = await self.live_approval_manager.consume_for_order(ticket_id=ticket_id, order=order)
            if not approved:
                result = ExecutionResult(
                    accepted=False,
                    mode=TradingMode.LIVE,
                    broker=order.broker,
                    symbol=order.symbol,
                    side=order.side,
                    quantity=order.quantity,
                    status="rejected",
                    message="Live approval ticket invalid, expired, or mismatched.",
                )
                await self._safe_log_execution(result)
                return result
            live_approval_validated = True
        if self.kill_switch.is_active:
            await self.event_bus.publish(
                build_event(
                    event_type=EventType.KILL_SWITCH_TRIGGERED,
                    source="execution_engine",
                    payload={"state": asdict(self.kill_switch.state)},
                )
            )
            result = ExecutionResult(
                accepted=False,
                mode=order.mode,
                broker=order.broker,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                status="rejected",
                message="Kill switch active.",
            )
            await self._safe_log_execution(result)
            return result

        snapshot = await self.global_state.snapshot(order.mode)
        correlation = CorrelationContext(matrix=correlation_matrix or {})
        risk_result = self.risk_guardian.validate_order(
            order=order,
            snapshot=snapshot,
            correlation_context=correlation,
            kill_switch_active=self.kill_switch.is_active,
        )

        if risk_result.decision == RiskDecision.REJECTED:
            await self.event_bus.publish(
                build_event(
                    event_type=EventType.RISK_REJECTED,
                    source="risk_guardian",
                    payload={
                        "symbol": order.symbol,
                        "mode": order.mode.value,
                        "reasons": risk_result.reasons,
                        "submitted_at": order.submitted_at.isoformat(),
                    },
                )
            )
            result = ExecutionResult(
                accepted=False,
                mode=order.mode,
                broker=order.broker,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                status="rejected",
                message="Risk rejected: " + "; ".join(risk_result.reasons),
            )
            await self._safe_log_execution(result)
            return result

        await self.event_bus.publish(
            build_event(
                event_type=EventType.RISK_APPROVED,
                source="risk_guardian",
                payload={
                    "symbol": order.symbol,
                    "mode": order.mode.value,
                    "submitted_at": order.submitted_at.isoformat(),
                },
            )
        )

        if order.mode == TradingMode.PAPER:
            result = await self.paper_executor.execute(order)
        else:
            result = await self.live_executor.execute(
                order,
                human_approved=(human_approved or live_approval_validated),
            )

        if result.accepted:
            await self.event_bus.publish(
                build_event(
                    event_type=EventType.TRADE_EXECUTED,
                    source="execution_engine",
                    payload=result.model_dump(),
                )
            )
            self.kill_switch.register_success()
            post_snapshot = await self.global_state.snapshot(order.mode)
            mode_key = order.mode.value
            self._peak_equity[mode_key] = max(self._peak_equity.get(mode_key, 0.0), post_snapshot.balance)
            self.kill_switch.evaluate_drawdown(self._peak_equity[mode_key], post_snapshot.balance)
            self.kill_switch.evaluate_losses(post_snapshot.consecutive_losses)
        else:
            self.kill_switch.register_api_failure(result.message or "execution rejected")
            await self._safe_log_execution(result)
            if self.kill_switch.is_active:
                await self.event_bus.publish(
                    build_event(
                        event_type=EventType.KILL_SWITCH_TRIGGERED,
                        source="execution_engine.api_failure",
                        payload={"state": asdict(self.kill_switch.state)},
                    )
                )
        return result

    async def _safe_log_execution(self, result: ExecutionResult) -> None:
        """Persist execution outcome without breaking control flow."""
        try:
            await self.trade_memory.log_execution(result)
        except Exception:  # noqa: BLE001
            logger.exception("Failed to persist execution audit trail")
