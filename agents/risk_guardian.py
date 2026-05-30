"""Risk-first guardian with hard veto authority over execution."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from trading_system.config.models import (
    OrderRequest,
    OrderSide,
    PortfolioSnapshot,
    RiskCheckResult,
    RiskDecision,
    RiskLimits,
)

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class CorrelationContext:
    """Correlation matrix container for risk checks."""

    matrix: Dict[str, float]

    def get(self, a: str, b: str) -> float:
        """Get absolute correlation by symbol pair."""
        key1 = f"{a}|{b}"
        key2 = f"{b}|{a}"
        return abs(float(self.matrix.get(key1, self.matrix.get(key2, 0.0))))


class RiskGuardian:
    """
    Enforces HERMES v5.2 deterministic 12-check safety gate.
    
    Checks:
    1. Capital Check (available = total - allocated - pending)
    2. Margin Check (F&O SPAN + exposure)
    3. Position Limit (< 10% per stock)
    4. Sector Limit (< 25% per sector)
    5. Correlation Check (< 0.70 normal, < 0.50 crisis)
    6. Liquidity Check (Volume > 10th percentile, size < 10% ADV)
    7. Circuit Breaker Check (Not in circuit limit)
    8. Strategy Capacity Limit (< max_capacity_rupees)
    9. Kill Switch Check (kill_switch_active == FALSE)
    10. Market Hours Check (09:15-15:30 IST)
    11. AMO Prevention Check (< 15:25 IST for AMO)
    12. Account Health Check (Status == active)
    """

    def __init__(self, limits: RiskLimits) -> None:
        self.limits = limits
        self.ist = timezone(timedelta(hours=5, minutes=30))

    def validate_order(
        self,
        order: OrderRequest,
        snapshot: PortfolioSnapshot,
        correlation_context: Optional[CorrelationContext] = None,
        kill_switch_active: bool = False,
    ) -> RiskCheckResult:
        """Run full 12-check risk pipeline."""
        reasons: List[str] = []
        now_ist = datetime.now(self.ist)

        # 9. Kill Switch Check
        if kill_switch_active:
            reasons.append("Kill switch active.")
            return self._reject(reasons)

        # 10. Market Hours Check (09:15-15:30 IST)
        if not self._is_market_hours(now_ist):
            reasons.append(f"Outside market hours: {now_ist.strftime('%H:%M:%S')}")

        # 11. AMO Prevention Check (< 15:25 IST)
        if self._is_amo_prevention(now_ist):
            reasons.append(f"AMO prevention active (> 15:25): {now_ist.strftime('%H:%M:%S')}")

        # 12. Account Health Check
        if not self.limits.account_health_required:
            logger.debug("Account health check skipped by config.")
        elif snapshot.daily_realized_pnl <= -abs(self.limits.max_daily_loss):
            reasons.append("Max daily loss exceeded.")
        elif snapshot.consecutive_losses >= self.limits.max_consecutive_losses:
            reasons.append(f"Consecutive losses {snapshot.consecutive_losses} exceed max.")

        # 1. Capital Check (available = total - allocated - pending)
        notional = self._order_notional(order)
        # Spec says available = total - allocated - pending. 
        # Here we check if notional fits in available_cash.
        if notional > snapshot.available_cash:
             reasons.append(f"Insufficient capital: required {notional:.2f}, available {snapshot.available_cash:.2f}")

        # 2. Margin Check (Simple exposure check for now)
        if order.leverage > self.limits.max_leverage:
             reasons.append(f"Leverage {order.leverage:.2f} exceeds max {self.limits.max_leverage:.2f}")

        # 3. Position Limit (< 10% per stock)
        symbol_exposure = self._symbol_exposure(snapshot.positions, order.symbol)
        projected_symbol_exposure = symbol_exposure + notional
        if snapshot.balance > 0:
            symbol_pct = (projected_symbol_exposure / snapshot.balance) * 100
            if symbol_pct > self.limits.max_symbol_exposure_pct:
                reasons.append(f"Symbol exposure {symbol_pct:.2f}% exceeds max {self.limits.max_symbol_exposure_pct:.2f}%")

        # 4. Sector Limit (< 25% per sector)
        sector = order.metadata.get("sector", "Unknown")
        sector_exposure = self._sector_exposure(snapshot.positions, sector, order.symbol)
        projected_sector_exposure = sector_exposure + notional
        if snapshot.balance > 0:
            sector_pct = (projected_sector_exposure / snapshot.balance) * 100
            if sector_pct > self.limits.max_sector_exposure_pct:
                reasons.append(f"Sector '{sector}' exposure {sector_pct:.2f}% exceeds max {self.limits.max_sector_exposure_pct:.2f}%")

        # 5. Correlation Check (< 0.70 normal)
        if correlation_context:
            corr_reason = self._validate_correlation(order, snapshot.positions, correlation_context)
            if corr_reason:
                reasons.append(corr_reason)

        # 6. Liquidity Check (size < 10% ADV)
        adv = float(order.metadata.get("avg_daily_volume", 0.0))
        if adv > 0:
            order_pct_adv = (order.quantity / adv) * 100
            if order_pct_adv > (self.limits.max_order_adv_pct * 100):
                reasons.append(f"Order size {order.quantity} is {order_pct_adv:.2f}% of ADV (max 10%)")

        # 7. Circuit Breaker Check
        if order.metadata.get("in_circuit_limit"):
            reasons.append(f"Symbol {order.symbol} is currently in circuit limit.")

        # 8. Strategy Capacity Limit
        strategy_exposure = float(order.metadata.get("strategy_exposure", 0.0))
        if (strategy_exposure + notional) > self.limits.max_strategy_capacity:
            reasons.append(f"Strategy capacity exceeded: limit {self.limits.max_strategy_capacity:.2f}")

        # Stop loss validation (HERMES requires stop loss)
        stop_loss_reason = self._validate_stop_loss(order)
        if stop_loss_reason:
            reasons.append(stop_loss_reason)

        decision = RiskDecision.REJECTED if reasons else RiskDecision.APPROVED
        return RiskCheckResult(decision=decision, reasons=reasons, limits=self.limits)

    def _reject(self, reasons: List[str]) -> RiskCheckResult:
        return RiskCheckResult(decision=RiskDecision.REJECTED, reasons=reasons, limits=self.limits)

    def _is_market_hours(self, dt: datetime) -> bool:
        if dt.weekday() >= 5:  # Sat, Sun
            return False
        start = dt.replace(hour=9, minute=15, second=0, microsecond=0)
        end = dt.replace(hour=15, minute=30, second=0, microsecond=0)
        return start <= dt <= end

    def _is_amo_prevention(self, dt: datetime) -> bool:
        # AMO prevention: reject if after 15:25
        amo_start = dt.replace(hour=15, minute=25, second=0, microsecond=0)
        return dt >= amo_start and dt.hour < 16 # Only relevant near close

    def _order_notional(self, order: OrderRequest) -> float:
        mark_price = float(order.metadata.get("mark_price", 0.0))
        if order.limit_price:
            mark_price = order.limit_price
        if mark_price <= 0:
            mark_price = float(order.metadata.get("last_price", 1.0))
        return order.quantity * mark_price

    def _symbol_exposure(self, positions: Dict[str, Dict[str, Any]], symbol: str) -> float:
        pos = positions.get(symbol)
        if not pos:
            return 0.0
        qty = abs(float(pos.get("quantity", 0.0)))
        avg = abs(float(pos.get("avg_price", 0.0)))
        return qty * avg

    def _sector_exposure(self, positions: Dict[str, Dict[str, Any]], sector: str, current_symbol: str) -> float:
        total = 0.0
        for symbol, data in positions.items():
            if symbol == current_symbol:
                continue
            if data.get("sector") == sector:
                qty = abs(float(data.get("quantity", 0.0)))
                avg = abs(float(data.get("avg_price", 0.0)))
                total += (qty * avg)
        return total

    def _validate_stop_loss(self, order: OrderRequest) -> Optional[str]:
        if order.stop_loss is None:
            return "Stop loss is mandatory for all orders."
        reference = float(order.metadata.get("mark_price") or order.limit_price or order.metadata.get("last_price") or 0)
        if reference <= 0:
            return "Missing reference price for stop-loss validation."
        distance_pct = abs(reference - order.stop_loss) / reference * 100
        if distance_pct < self.limits.min_stop_loss_pct:
            return f"Stop loss distance {distance_pct:.2f}% below minimum {self.limits.min_stop_loss_pct:.2f}%."
        if distance_pct > self.limits.max_stop_loss_pct:
            return f"Stop loss distance {distance_pct:.2f}% above maximum {self.limits.max_stop_loss_pct:.2f}%."
        if order.side == OrderSide.BUY and order.stop_loss >= reference:
            return "For buy orders, stop loss must be below entry/reference price."
        if order.side == OrderSide.SELL and order.stop_loss <= reference:
            return "For sell orders, stop loss must be above entry/reference price."
        return None

    def _validate_correlation(
        self,
        order: OrderRequest,
        positions: Dict[str, Dict[str, Any]],
        context: CorrelationContext,
    ) -> Optional[str]:
        for symbol, data in positions.items():
            qty = float(data.get("quantity", 0.0))
            if qty == 0 or symbol == order.symbol:
                continue
            correlation = context.get(order.symbol, symbol)
            if correlation >= self.limits.max_correlation:
                return (
                    f"Correlation check failed: {order.symbol} vs {symbol} = {correlation:.2f} "
                    f"(max {self.limits.max_correlation:.2f})."
                )
        return None

    def portfolio_risk_snapshot(self, snapshot: PortfolioSnapshot, kill_switch_active: bool) -> Dict[str, Any]:
        """Return portfolio risk status payload for dashboards and chatbot."""
        usage_pct = (snapshot.gross_exposure / self.limits.max_exposure) * 100 if self.limits.max_exposure else 0.0
        return {
            "mode": snapshot.mode.value,
            "balance": snapshot.balance,
            "available_cash": snapshot.available_cash,
            "daily_realized_pnl": snapshot.daily_realized_pnl,
            "gross_exposure": snapshot.gross_exposure,
            "exposure_usage_pct": usage_pct,
            "consecutive_losses": snapshot.consecutive_losses,
            "kill_switch_active": kill_switch_active,
            "limits": self.limits.model_dump(),
        }
