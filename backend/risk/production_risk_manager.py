"""Production risk management: position sizing, portfolio heat, drawdown, fat-finger checks."""
from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class RiskConfig:
    """All risk parameters in one place. Loaded from env with sane defaults."""
    # Position sizing
    risk_per_trade_pct: float = 0.01          # 1% of equity per trade
    max_position_pct: float = 0.10            # 10% of equity per position
    max_open_positions: int = 10
    max_sector_pct: float = 0.25              # 25% per sector

    # Portfolio heat
    max_portfolio_heat_pct: float = 0.05      # 5% total risk

    # Drawdown limits
    max_drawdown_pct: float = 0.15            # 15% from peak
    max_daily_loss_pct: float = 0.03          # 3% daily
    max_weekly_loss_pct: float = 0.07         # 7% weekly
    max_monthly_loss_pct: float = 0.15        # 15% monthly

    # Fat-finger
    max_price_deviation_pct: float = 0.05     # 5% from last price

    # Trade frequency
    max_trades_per_day: int = 20
    min_signal_confidence: float = 0.70

    # Kill switch
    kill_switch_cooldown_sec: int = 1800      # 30 minutes

    @classmethod
    def from_env(cls) -> "RiskConfig":
        return cls(
            risk_per_trade_pct=float(os.getenv("RISK_PER_TRADE_PCT", "0.01")),
            max_position_pct=float(os.getenv("MAX_POSITION_PCT", "0.10")),
            max_open_positions=int(os.getenv("MAX_OPEN_POSITIONS", "10")),
            max_sector_pct=float(os.getenv("MAX_SECTOR_PCT", "0.25")),
            max_portfolio_heat_pct=float(os.getenv("MAX_PORTFOLIO_HEAT_PCT", "0.05")),
            max_drawdown_pct=float(os.getenv("MAX_DRAWDOWN_PCT", "0.15")),
            max_daily_loss_pct=float(os.getenv("MAX_DAILY_LOSS_PCT", "0.03")),
            max_weekly_loss_pct=float(os.getenv("MAX_WEEKLY_LOSS_PCT", "0.07")),
            max_monthly_loss_pct=float(os.getenv("MAX_MONTHLY_LOSS_PCT", "0.15")),
            max_price_deviation_pct=float(os.getenv("MAX_PRICE_DEVIATION_PCT", "0.05")),
            max_trades_per_day=int(os.getenv("MAX_TRADES_PER_DAY", "20")),
            min_signal_confidence=float(os.getenv("MIN_SIGNAL_CONFIDENCE", "0.70")),
            kill_switch_cooldown_sec=int(os.getenv("KILL_SWITCH_COOLDOWN_SEC", "1800")),
        )


class PositionSizer:
    """Fixed-fractional position sizing: risk X% of equity per trade."""

    def __init__(self, config: RiskConfig) -> None:
        self._config = config

    def calculate_quantity(
        self,
        equity: float,
        entry_price: float,
        stop_price: float,
        lot_size: int = 1,
    ) -> int:
        """Returns the number of shares to buy, rounded down to lot size."""
        if entry_price <= 0 or stop_price <= 0 or equity <= 0:
            return 0

        risk_amount = equity * self._config.risk_per_trade_pct
        risk_per_share = abs(entry_price - stop_price)

        if risk_per_share <= 0:
            # No stop distance defined — use max position size
            max_notional = equity * self._config.max_position_pct
            qty = int(max_notional / entry_price)
        else:
            qty = int(risk_amount / risk_per_share)

        # Cap at max position value
        max_notional = equity * self._config.max_position_pct
        max_qty = int(max_notional / entry_price) if entry_price > 0 else 0
        qty = min(qty, max_qty)

        # Round down to lot size
        if lot_size > 1:
            qty = (qty // lot_size) * lot_size

        return max(qty, 0)


class PortfolioHeatTracker:
    """Tracks total portfolio risk as a fraction of equity."""

    def __init__(self, config: RiskConfig) -> None:
        self._config = config

    def calculate_heat(
        self,
        positions: list[dict],
        equity: float,
    ) -> float:
        """Returns current portfolio heat as a fraction (0.0 to 1.0+)."""
        if equity <= 0:
            return 1.0  # Max heat if no equity

        total_risk = 0.0
        for pos in positions:
            qty = abs(int(pos.get("quantity", 0)))
            entry = float(pos.get("avg_entry", 0) or pos.get("avg_entry_price", 0))
            stop = float(pos.get("stop_price", 0) or entry * 0.95)  # Default 5% stop
            if qty > 0 and entry > 0:
                total_risk += qty * abs(entry - stop)

        return total_risk / equity

    def can_add_position(
        self,
        positions: list[dict],
        equity: float,
        new_risk: float,
    ) -> tuple[bool, str]:
        """Check if adding a new position would exceed heat limit."""
        current_heat = self.calculate_heat(positions, equity)
        new_heat = current_heat + (new_risk / equity if equity > 0 else 1.0)

        if new_heat > self._config.max_portfolio_heat_pct:
            return False, f"Portfolio heat {current_heat:.1%} + {new_risk/equity:.1%} > {self._config.max_portfolio_heat_pct:.1%}"
        return True, "ok"


class DrawdownMonitor:
    """Tracks drawdown including unrealized P&L."""

    def __init__(self, config: RiskConfig) -> None:
        self._config = config
        self._peak_equity: float = 0.0
        self._daily_pnl: float = 0.0
        self._weekly_pnl: float = 0.0
        self._monthly_pnl: float = 0.0
        self._last_reset_day: str = ""
        self._last_reset_week: str = ""
        self._last_reset_month: str = ""
        self._kill_switch_triggered: bool = False
        self._kill_switch_time: float = 0.0
        self._trades_today: int = 0
        self._last_trade_day: str = ""

    def update_peak(self, current_equity: float) -> None:
        """Update peak equity watermark."""
        if current_equity > self._peak_equity:
            self._peak_equity = current_equity

    def get_drawdown(self, current_equity: float) -> float:
        """Returns current drawdown as a fraction (0.0 = at peak, positive = losing)."""
        if self._peak_equity <= 0:
            return 0.0
        return max(0.0, (self._peak_equity - current_equity) / self._peak_equity)

    def record_trade_pnl(self, pnl: float) -> None:
        """Record a closed trade PnL for daily/weekly/monthly tracking."""
        today = time.strftime("%Y-%m-%d")
        self._reset_if_needed(today)

        self._daily_pnl += pnl
        self._weekly_pnl += pnl
        self._monthly_pnl += pnl
        self._trades_today += 1

    def _reset_if_needed(self, today: str) -> None:
        """Reset daily/weekly/monthly counters when the period rolls."""
        if today != self._last_reset_day:
            self._daily_pnl = 0.0
            self._trades_today = 0
            self._last_reset_day = today

        # Week reset (Monday)
        import datetime
        dt = datetime.datetime.strptime(today, "%Y-%m-%d")
        week_key = dt.strftime("%Y-W%W")
        if week_key != self._last_reset_week:
            self._weekly_pnl = 0.0
            self._last_reset_week = week_key

        # Month reset
        month_key = today[:7]
        if month_key != self._last_reset_month:
            self._monthly_pnl = 0.0
            self._last_reset_month = month_key

    def check_halt_conditions(
        self,
        current_equity: float,
        realized_pnl: float,
    ) -> tuple[bool, str]:
        """Check if any halt condition is met. Returns (should_halt, reason)."""
        # Kill switch cooldown check
        if self._kill_switch_triggered:
            elapsed = time.time() - self._kill_switch_time
            if elapsed < self._config.kill_switch_cooldown_sec:
                remaining = int(self._config.kill_switch_cooldown_sec - elapsed)
                return True, f"Kill switch active, {remaining}s cooldown remaining"
            else:
                self._kill_switch_triggered = False
                logger.info("Kill switch cooldown expired")

        self.update_peak(current_equity)

        # Max drawdown
        dd = self.get_drawdown(current_equity)
        if dd >= self._config.max_drawdown_pct:
            self._trigger_kill_switch()
            return True, f"Max drawdown breached: {dd:.1%} >= {self._config.max_drawdown_pct:.1%}"

        # Daily loss
        if self._daily_pnl < 0 and abs(self._daily_pnl) >= current_equity * self._config.max_daily_loss_pct:
            self._trigger_kill_switch()
            return True, f"Daily loss limit: {self._daily_pnl:.2f} >= {current_equity * self._config.max_daily_loss_pct:.2f}"

        # Weekly loss
        if self._weekly_pnl < 0 and abs(self._weekly_pnl) >= current_equity * self._config.max_weekly_loss_pct:
            self._trigger_kill_switch()
            return True, f"Weekly loss limit: {self._weekly_pnl:.2f} >= {current_equity * self._config.max_weekly_loss_pct:.2f}"

        # Monthly loss
        if self._monthly_pnl < 0 and abs(self._monthly_pnl) >= current_equity * self._config.max_monthly_loss_pct:
            self._trigger_kill_switch()
            return True, f"Monthly loss limit: {self._monthly_pnl:.2f} >= {current_equity * self._config.max_monthly_loss_pct:.2f}"

        # Trade frequency
        today = time.strftime("%Y-%m-%d")
        self._reset_if_needed(today)
        if self._trades_today >= self._config.max_trades_per_day:
            return True, f"Max trades per day: {self._trades_today} >= {self._config.max_trades_per_day}"

        return False, "ok"

    def _trigger_kill_switch(self) -> None:
        self._kill_switch_triggered = True
        self._kill_switch_time = time.time()
        logger.critical("KILL SWITCH TRIGGERED")

    def reset_kill_switch(self) -> str:
        """Manual reset with cooldown enforcement."""
        if self._kill_switch_triggered:
            elapsed = time.time() - self._kill_switch_time
            if elapsed < self._config.kill_switch_cooldown_sec:
                remaining = int(self._config.kill_switch_cooldown_sec - elapsed)
                return f"Cannot reset yet. {remaining}s cooldown remaining."
        self._kill_switch_triggered = False
        self._kill_switch_time = 0.0
        return "Kill switch reset"

    @property
    def is_halted(self) -> bool:
        return self._kill_switch_triggered

    def get_state(self) -> dict:
        return {
            "peak_equity": self._peak_equity,
            "daily_pnl": self._daily_pnl,
            "weekly_pnl": self._weekly_pnl,
            "monthly_pnl": self._monthly_pnl,
            "trades_today": self._trades_today,
            "kill_switch_triggered": self._kill_switch_triggered,
        }


class FatFingerGuard:
    """Rejects orders with unrealistic prices."""

    def __init__(self, config: RiskConfig) -> None:
        self._config = config

    def check_price(self, order_price: float, last_price: float, symbol: str) -> tuple[bool, str]:
        """Returns (is_valid, reason)."""
        if last_price <= 0 or order_price <= 0:
            return True, "no last price to compare"

        deviation = abs(order_price - last_price) / last_price
        if deviation > self._config.max_price_deviation_pct:
            return False, f"Fat-finger rejected: {symbol} order={order_price:.2f} vs last={last_price:.2f} ({deviation:.1%} > {self._config.max_price_deviation_pct:.1%})"
        return True, "ok"

    def check_short_sell(self, side: str, position_qty: int) -> tuple[bool, str]:
        """Reject naked short selling."""
        if side == "sell" and position_qty <= 0:
            return False, f"Naked short sell rejected: no existing position to sell"
        return True, "ok"


class ProductionRiskManager:
    """Unified risk management facade."""

    def __init__(self) -> None:
        self.config = RiskConfig.from_env()
        self.sizer = PositionSizer(self.config)
        self.heat = PortfolioHeatTracker(self.config)
        self.drawdown = DrawdownMonitor(self.config)
        self.fat_finger = FatFingerGuard(self.config)
        self._initialized = True
        logger.info(
            "RiskManager loaded: risk_per_trade=%.1f%%, max_positions=%d, max_heat=%.1f%%, max_dd=%.1f%%",
            self.config.risk_per_trade_pct * 100,
            self.config.max_open_positions,
            self.config.max_portfolio_heat_pct * 100,
            self.config.max_drawdown_pct * 100,
        )

    async def validate_order(
        self,
        side: str,
        symbol: str,
        quantity: int,
        price: float,
        stop_price: float,
        entry_price: float,
        positions: list[dict],
        equity: float,
        last_price: float,
        confidence: float = 1.0,
        current_price: float = 0.0,
    ) -> dict[str, Any]:
        """
        Full pre-trade risk check. Returns {"action": "APPROVE"|"REJECT", "reason": str, "adjusted_qty": int}.
        """
        reasons = []

        # 1. Confidence threshold
        if confidence < self.config.min_signal_confidence:
            return {"action": "REJECT", "reason": f"Confidence {confidence:.2f} < {self.config.min_signal_confidence:.2f}", "adjusted_qty": 0}

        # 2. Max open positions
        open_count = sum(1 for p in positions if abs(int(p.get("quantity", 0))) > 0)
        if side == "buy" and open_count >= self.config.max_open_positions:
            return {"action": "REJECT", "reason": f"Max positions reached: {open_count}/{self.config.max_open_positions}", "adjusted_qty": 0}

        # 3. Fat-finger check
        check_last = last_price if last_price > 0 else (current_price if current_price > 0 else price)
        is_valid, reason = self.fat_finger.check_price(price, check_last, symbol)
        if not is_valid:
            return {"action": "REJECT", "reason": reason, "adjusted_qty": 0}

        # 4. Short-selling check
        pos_qty = 0
        for p in positions:
            if p.get("symbol", "").upper() == symbol.upper():
                pos_qty = int(p.get("quantity", 0))
                break
        is_valid, reason = self.fat_finger.check_short_sell(side, pos_qty)
        if not is_valid:
            return {"action": "REJECT", "reason": reason, "adjusted_qty": 0}

        # 5. Drawdown check
        should_halt, reason = self.drawdown.check_halt_conditions(equity, 0.0)
        if should_halt:
            return {"action": "REJECT", "reason": reason, "adjusted_qty": 0}

        # 6. Position sizing
        adj_qty = self.sizer.calculate_quantity(equity, entry_price, stop_price)
        if adj_qty <= 0:
            return {"action": "REJECT", "reason": "Position sizer returned 0", "adjusted_qty": 0}
        if adj_qty < quantity:
            reasons.append(f"Size adjusted: {quantity} -> {adj_qty}")

        # 7. Portfolio heat
        risk_per_share = abs(entry_price - stop_price) if stop_price > 0 else entry_price * 0.05
        new_risk = adj_qty * risk_per_share
        can_add, heat_reason = self.heat.can_add_position(positions, equity, new_risk)
        if not can_add:
            return {"action": "REJECT", "reason": heat_reason, "adjusted_qty": 0}

        return {
            "action": "APPROVE",
            "reason": "; ".join(reasons) if reasons else "All risk checks passed",
            "adjusted_qty": adj_qty,
        }
