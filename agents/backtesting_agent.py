"""Backtesting agent with Hermes-guided self-learning loop."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from trading_system.config.models import BacktestRequest
from trading_system.integrations.hermes_client import HermesClient
from trading_system.skills.backtesting_skill import BacktestingSkill

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class BacktestTuningSpec:
    success_return_pct: float = 5.0
    failure_return_pct: float = -2.0
    max_rounds: int = 6


class BacktestingAgent:
    """
    Runs backtests and iteratively tunes one parameter per round.

    Safety:
    - Historical-only (BacktestingSkill).
    - No broker endpoints touched.
    """

    def __init__(self, backtester: Optional[BacktestingSkill] = None, hermes: Optional[HermesClient] = None) -> None:
        self.backtester = backtester or BacktestingSkill()
        self.hermes = hermes or HermesClient()

    async def run_with_learning(
        self,
        symbol: str,
        timeframe: str,
        lookback_days: int,
        strategy_name: str,
        strategy_params: Dict[str, Any],
        spec: Optional[BacktestTuningSpec] = None,
    ) -> Dict[str, Any]:
        spec = spec or BacktestTuningSpec()
        history = []
        current_params = dict(strategy_params)

        for round_idx in range(1, spec.max_rounds + 1):
            req = BacktestRequest(
                symbols=[symbol],
                timeframe=timeframe,
                lookback_days=lookback_days,
                strategy_name=strategy_name,
                strategy_params=current_params,
                initial_capital=100000.0,
            )
            result = await self.backtester.run(req)
            metrics = result.metrics.model_dump()
            total_return = float(metrics.get("total_return_pct") or 0.0)
            decision = "continue"
            if total_return >= spec.success_return_pct:
                decision = "success"
            elif total_return <= spec.failure_return_pct:
                decision = "failure"

            history.append(
                {
                    "round": round_idx,
                    "params": dict(current_params),
                    "metrics": metrics,
                    "decision": decision,
                }
            )

            if decision in {"success", "failure"}:
                break

            # Ask Hermes for one tweak suggestion. If Hermes is unavailable, do a deterministic tweak.
            current_params = await self._next_params(strategy_name, current_params, metrics)

        best = max(history, key=lambda h: float(h["metrics"].get("total_return_pct") or 0.0))
        return {"best": best, "history": history}

    async def _next_params(self, strategy_name: str, params: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
        prompt = (
            "You are tuning a simple trading strategy backtest.\n"
            "Propose ONE parameter change to improve total_return_pct without increasing max_drawdown too much.\n"
            "Return JSON only: {\"param\":\"name\",\"value\":number}.\n\n"
            f"Strategy: {strategy_name}\n"
            f"Current params: {params}\n"
            f"Metrics: {metrics}\n"
        )
        suggestion = await asyncio.to_thread(self.hermes.query, prompt)
        if suggestion and suggestion.strip().startswith("{"):
            try:
                import json

                obj = json.loads(suggestion)
                key = str(obj.get("param") or "").strip()
                value = obj.get("value")
                if key and isinstance(value, (int, float)):
                    nxt = dict(params)
                    nxt[key] = float(value)
                    return nxt
            except Exception:
                pass

        # Fallback deterministic tweaks.
        nxt = dict(params)
        if strategy_name.lower() in {"ema", "ema_crossover", "ema_cross"}:
            nxt["fast"] = max(5.0, float(nxt.get("fast", 21)) - 2.0)
            nxt["slow"] = max(float(nxt["fast"]) + 5.0, float(nxt.get("slow", 55)) - 1.0)
            return nxt
        if strategy_name.lower() in {"rsi", "rsi_reversion"}:
            nxt["oversold"] = max(10.0, float(nxt.get("oversold", 30)) - 1.0)
            return nxt
        return nxt

