"""Local strategy rules engine — evaluates entry/exit conditions against live market data."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class StrategyCondition:
    """A single condition like RSI below 30, or EMA crossover."""
    indicator: str  # rsi, macd, ema_fast, ema_slow, bb_upper, bb_lower, close, volume, stochastic_k, stochastic_d
    operator: str  # above, below, crossover, crossunder, equals, gte, lte
    value: float = 0.0
    compare_to: str = ""  # optional: another indicator name


@dataclass
class StrategyRule:
    """Parsed strategy rule from JSON entry/exit rules."""
    conditions: list[StrategyCondition] = field(default_factory=list)
    logic: str = "and"  # "and" or "or"


def parse_rule(rule_json: str) -> Optional[StrategyRule]:
    """Parse a JSON rule string into a StrategyRule."""
    if not rule_json:
        return None
    try:
        data = json.loads(rule_json) if rule_json.strip().startswith("{") else {}
    except (json.JSONDecodeError, TypeError):
        return None

    if not data:
        return None

    conditions = []
    logic = data.get("logic", "and")

    # Handle simple RSI format: {"rsi": {"below": 30}}
    for key, val in data.items():
        if key in ("logic",):
            continue
        if isinstance(val, dict):
            for op, value in val.items():
                conditions.append(StrategyCondition(
                    indicator=key,
                    operator=op,
                    value=float(value) if isinstance(value, (int, float)) else 0.0,
                ))
        elif isinstance(val, (int, float)):
            # Simple indicator value like {"rsi": 30} -> assume below
            conditions.append(StrategyCondition(
                indicator=key,
                operator="lte",
                value=float(val),
            ))
        elif isinstance(val, str) and val in ("bullish", "bearish"):
            # Trend condition
            conditions.append(StrategyCondition(
                indicator="trend",
                operator="equals",
                value=0.0,
                compare_to=val,
            ))

    return StrategyRule(conditions=conditions, logic=logic) if conditions else None


def evaluate_condition(condition: StrategyCondition, indicators: dict[str, float]) -> bool:
    """Evaluate a single condition against computed indicators."""
    ind_val = indicators.get(condition.indicator, 0.0)
    compare_val = condition.value

    # If compare_to is set, compare against another indicator
    if condition.compare_to:
        compare_val = indicators.get(condition.compare_to, condition.value)

    op = condition.operator.lower()
    if op in ("below", "lt", "less", "under"):
        return ind_val < compare_val
    if op in ("above", "gt", "greater", "over"):
        return ind_val > compare_val
    if op in ("lte", "le", "less_equal"):
        return ind_val <= compare_val
    if op in ("gte", "ge", "greater_equal"):
        return ind_val >= compare_val
    if op in ("equals", "eq", "is"):
        if condition.indicator == "trend":
            return str(condition.compare_to).lower() in str(ind_val).lower()
        return abs(ind_val - compare_val) < 0.001
    if op in ("crossover",):
        # For crossover, we need previous value - use current threshold
        return ind_val > compare_val
    if op in ("crossunder",):
        return ind_val < compare_val
    return False


def evaluate_rule(
    rule: StrategyRule,
    indicators: dict[str, float],
) -> dict[str, Any]:
    """
    Evaluate a parsed strategy rule against live indicators.

    Returns:
        {
            "triggered": bool,
            "conditions_met": int,
            "conditions_total": int,
            "details": [{"indicator": str, "operator": str, "value": float, "met": bool}, ...]
        }
    """
    if not rule or not rule.conditions:
        return {"triggered": False, "conditions_met": 0, "conditions_total": 0, "details": []}

    details = []
    met_count = 0

    for cond in rule.conditions:
        result = evaluate_condition(cond, indicators)
        details.append({
            "indicator": cond.indicator,
            "operator": cond.operator,
            "value": cond.value,
            "current": indicators.get(cond.indicator, 0.0),
            "met": result,
        })
        if result:
            met_count += 1

    total = len(details)
    if rule.logic == "or":
        triggered = met_count > 0
    else:  # "and"
        triggered = met_count == total

    return {
        "triggered": triggered,
        "conditions_met": met_count,
        "conditions_total": total,
        "details": details,
    }


class StrategyEngine:
    """
    Evaluates all strategies against live market data and emits signals.

    Usage:
        engine = StrategyEngine(event_bus)
        await engine.evaluate("RELIANCE", 1500.0, technical_indicators_dict)
    """

    def __init__(self, event_bus: Any) -> None:
        self._bus = event_bus
        self._strategies: dict[str, dict] = {}

    def load_strategies(self, strategies: list[dict]) -> None:
        """Load strategies from DB rows."""
        self._strategies.clear()
        for s in strategies:
            sid = str(s.get("id") or "")
            entry_rule = parse_rule(str(s.get("entry_rule") or ""))
            exit_rule = parse_rule(str(s.get("exit_rule") or ""))
            if entry_rule or exit_rule:
                self._strategies[sid] = {
                    "id": sid,
                    "name": s.get("name", ""),
                    "symbol": str(s.get("symbol") or "").upper(),
                    "timeframe": s.get("timeframe", "1d"),
                    "status": s.get("status", "paused"),
                    "entry_rule": entry_rule,
                    "exit_rule": exit_rule,
                }

    async def evaluate(
        self,
        symbol: str,
        price: float,
        indicators: dict[str, float],
    ) -> list[dict[str, Any]]:
        """
        Evaluate all active strategies for a symbol.

        Returns a list of triggered signals.
        """
        signals = []
        sym = symbol.upper().replace(".NS", "").replace(".BO", "")

        for sid, strat in self._strategies.items():
            if strat["status"] != "running":
                continue
            if strat["symbol"] != sym:
                continue

            entry = strat.get("entry_rule")
            exit_rule = strat.get("exit_rule")

            if entry:
                result = evaluate_rule(entry, indicators)
                if result["triggered"]:
                    signal = {
                        "strategy_id": sid,
                        "strategy_name": strat["name"],
                        "symbol": sym,
                        "side": "buy",
                        "price": price,
                        "confidence": result["conditions_met"] / max(result["conditions_total"], 1),
                        "reason": f"Entry conditions met ({result['conditions_met']}/{result['conditions_total']})",
                        "details": result["details"],
                    }
                    signals.append(signal)
                    await self._bus.publish("strategy.entry_signal", signal)
                    logger.info("Strategy %s ENTRY signal for %s", strat["name"], sym)

            if exit_rule:
                result = evaluate_rule(exit_rule, indicators)
                if result["triggered"]:
                    signal = {
                        "strategy_id": sid,
                        "strategy_name": strat["name"],
                        "symbol": sym,
                        "side": "sell",
                        "price": price,
                        "confidence": result["conditions_met"] / max(result["conditions_total"], 1),
                        "reason": f"Exit conditions met ({result['conditions_met']}/{result['conditions_total']})",
                        "details": result["details"],
                    }
                    signals.append(signal)
                    await self._bus.publish("strategy.exit_signal", signal)
                    logger.info("Strategy %s EXIT signal for %s", strat["name"], sym)

        return signals
