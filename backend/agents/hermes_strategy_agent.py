"""Hermes-powered strategy generation, validation, tuning, and explanation.

Uses the Hermes Agent CLI for AI-driven strategy reasoning while maintaining
read-only access to the trading system (portfolio, signals, watchlist).
"""
from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class StrategyContext:
    """Read-only context about the current system state for Hermes prompts."""

    symbol: str
    timeframe: str
    current_price: Optional[float] = None
    portfolio_value: Optional[float] = None
    open_positions: Optional[list] = None
    recent_signals: Optional[list] = None
    lessons: Optional[list] = None


class HermesStrategyAgent:
    """
    Hermes-powered strategy agent for generation, validation, tuning, and explanation.

    Uses read-only access to the trading system. All Hermes calls are async via to_thread.
    Gracefully degrades if Hermes is unavailable.
    """

    def __init__(self, hermes_client: Any = None, event_bus: Any = None):
        from backend.integrations.hermes_client import HermesClient

        self.hermes = hermes_client or HermesClient()
        self._bus = event_bus
        self._available: Optional[bool] = None

    async def is_available(self) -> bool:
        """Check if Hermes is available (cached after first check)."""
        if self._available is not None:
            return self._available
        try:
            ok, info = await asyncio.to_thread(self.hermes.healthcheck)
            self._available = ok
            if ok:
                logger.info("Hermes strategy agent connected: %s", info)
            else:
                logger.warning("Hermes unavailable: %s", info)
        except Exception:
            self._available = False
        return self._available

    async def generate_strategy(
        self,
        symbol: str,
        timeframe: str = "1d",
        market_data: Optional[dict] = None,
        lessons: Optional[list] = None,
    ) -> dict[str, Any]:
        """
        Generate a trading strategy for the given symbol using Hermes reasoning.

        Returns:
            dict with keys: entry_rule, exit_rule, explanation, confidence, reasoning
        """
        if not await self.is_available():
            return self._fallback_generate(symbol, timeframe)

        context_parts = [
            f"Symbol: {symbol}",
            f"Timeframe: {timeframe}",
        ]

        if market_data:
            context_parts.append(f"Current Price: {market_data.get('current_price', 'N/A')}")
            context_parts.append(f"Trend: {market_data.get('trend', 'N/A')}")
            context_parts.append(f"RSI: {market_data.get('rsi', 'N/A')}")
            context_parts.append(f"Volume: {market_data.get('volume', 'N/A')}")

        if lessons:
            context_parts.append("\nPast lessons learned:")
            for lesson in lessons[:5]:
                context_parts.append(f"- {lesson}")

        context = "\n".join(context_parts)

        prompt = (
            "You are an expert quantitative trading strategist. Generate a trading strategy.\n\n"
            f"{context}\n\n"
            "Respond in JSON only (no markdown, no explanation outside JSON):\n"
            '{\n'
            '  "entry_rule": "<descriptive entry conditions or JSON object>",\n'
            '  "exit_rule": "<descriptive exit conditions or JSON object>",\n'
            '  "explanation": "<2-3 sentence plain English explanation>",\n'
            '  "confidence": <0.0-1.0>,\n'
            '  "reasoning": "<brief reasoning for why these conditions>"\n'
            "}\n\n"
            "Rules:\n"
            "- Entry rules should use technical indicators (RSI, EMA, MACD, Bollinger, Volume)\n"
            "- Include risk management (stop loss, take profit)\n"
            "- Be specific with thresholds\n"
            "- Consider the timeframe\n"
        )

        try:
            answer = await asyncio.to_thread(self.hermes.query, prompt)
            if not answer or answer.startswith("HERMES_ERROR") or answer == "HERMES_TIMEOUT":
                logger.warning("Hermes generate failed: %s", answer)
                return self._fallback_generate(symbol, timeframe)

            # Parse JSON from response
            result = self._parse_json(answer)
            if result:
                return {
                    "entry_rule": result.get("entry_rule", ""),
                    "exit_rule": result.get("exit_rule", ""),
                    "explanation": result.get("explanation", ""),
                    "confidence": float(result.get("confidence", 0.5)),
                    "reasoning": result.get("reasoning", ""),
                    "source": "hermes",
                }
            return self._fallback_generate(symbol, timeframe)

        except Exception as exc:
            logger.error("Hermes generate_strategy error: %s", exc)
            return self._fallback_generate(symbol, timeframe)

    async def validate_strategy(
        self,
        strategy_name: str,
        entry_rule: str,
        exit_rule: str,
        backtest_metrics: dict,
        market_context: Optional[dict] = None,
    ) -> dict[str, Any]:
        """
        Validate a strategy using Hermes reasoning based on backtest results.

        Returns:
            dict with keys: score, reasoning, suggestions, verdict
        """
        if not await self.is_available():
            return self._fallback_validate(backtest_metrics)

        context_parts = [
            f"Strategy: {strategy_name}",
            f"Entry Rule: {entry_rule}",
            f"Exit Rule: {exit_rule}",
            f"Backtest Metrics:",
            f"  Total Trades: {backtest_metrics.get('total_trades', 0)}",
            f"  Win Rate: {backtest_metrics.get('win_rate', 0)}%",
            f"  Net P&L: {backtest_metrics.get('net_pnl', 0)}",
            f"  Sharpe Ratio: {backtest_metrics.get('sharpe', 0)}",
            f"  Max Drawdown: {backtest_metrics.get('max_dd', 0)}",
            f"  Profit Factor: {backtest_metrics.get('profit_factor', 0)}",
        ]

        if market_context:
            context_parts.append(f"\nMarket Context: {json.dumps(market_context)}")

        context = "\n".join(context_parts)

        prompt = (
            "You are a strategy validation expert. Evaluate this trading strategy.\n\n"
            f"{context}\n\n"
            "Respond in JSON only:\n"
            '{\n'
            '  "score": <0-100>,\n'
            '  "verdict": "<APPROVED|NEEDS_IMPROVEMENT|REJECTED>",\n'
            '  "reasoning": "<2-3 sentences explaining the score>",\n'
            '  "suggestions": ["<suggestion 1>", "<suggestion 2>"]\n'
            "}\n\n"
            "Scoring criteria:\n"
            "- Win rate > 55%: good, < 45%: poor\n"
            "- Sharpe > 1.5: excellent, > 1.0: good, < 0.5: poor\n"
            "- Max drawdown < 10%: excellent, < 20%: acceptable, > 30%: poor\n"
            "- Profit factor > 2.0: excellent, > 1.5: good, < 1.0: losing\n"
            "- Risk/reward ratio must be favorable\n"
        )

        try:
            answer = await asyncio.to_thread(self.hermes.query, prompt)
            if not answer or answer.startswith("HERMES_ERROR") or answer == "HERMES_TIMEOUT":
                return self._fallback_validate(backtest_metrics)

            result = self._parse_json(answer)
            if result:
                return {
                    "score": int(result.get("score", 50)),
                    "verdict": result.get("verdict", "NEEDS_IMPROVEMENT"),
                    "reasoning": result.get("reasoning", ""),
                    "suggestions": result.get("suggestions", []),
                    "source": "hermes",
                }
            return self._fallback_validate(backtest_metrics)

        except Exception as exc:
            logger.error("Hermes validate_strategy error: %s", exc)
            return self._fallback_validate(backtest_metrics)

    async def tune_strategy(
        self,
        strategy_name: str,
        current_params: dict,
        backtest_metrics: dict,
    ) -> dict[str, Any]:
        """
        Ask Hermes to suggest ONE parameter improvement.

        Returns:
            dict with keys: param, value, reasoning
        """
        if not await self.is_available():
            return self._fallback_tune(strategy_name, current_params)

        prompt = (
            "You are tuning a trading strategy backtest.\n"
            "Propose ONE parameter change to improve total return.\n"
            "Return JSON only: {\"param\": \"name\", \"value\": number, \"reasoning\": \"why\"}\n\n"
            f"Strategy: {strategy_name}\n"
            f"Current params: {json.dumps(current_params)}\n"
            f"Metrics: {json.dumps(backtest_metrics)}\n"
        )

        try:
            answer = await asyncio.to_thread(self.hermes.query, prompt)
            if not answer or answer.startswith("HERMES_ERROR") or answer == "HERMES_TIMEOUT":
                return self._fallback_tune(strategy_name, current_params)

            result = self._parse_json(answer)
            if result and "param" in result:
                return {
                    "param": result["param"],
                    "value": result.get("value"),
                    "reasoning": result.get("reasoning", "Hermes suggestion"),
                    "source": "hermes",
                }
            return self._fallback_tune(strategy_name, current_params)

        except Exception as exc:
            logger.error("Hermes tune_strategy error: %s", exc)
            return self._fallback_tune(strategy_name, current_params)

    async def explain_strategy(
        self,
        strategy_name: str,
        entry_rule: str,
        exit_rule: str,
        metrics: Optional[dict] = None,
    ) -> str:
        """
        Generate a natural language explanation of the strategy.

        Returns:
            Plain English explanation string
        """
        if not await self.is_available():
            return self._fallback_explain(strategy_name, entry_rule, exit_rule)

        context_parts = [
            f"Strategy: {strategy_name}",
            f"Entry Rule: {entry_rule}",
            f"Exit Rule: {exit_rule}",
        ]
        if metrics:
            context_parts.append(f"Performance: {json.dumps(metrics)}")

        context = "\n".join(context_parts)

        prompt = (
            "Explain this trading strategy in plain English for a retail trader.\n\n"
            f"{context}\n\n"
            "Include:\n"
            "1. What the strategy tries to do\n"
            "2. When it buys and sells\n"
            "3. Key risks\n"
            "4. Best market conditions\n\n"
            "Keep it concise (3-5 sentences).\n"
        )

        try:
            answer = await asyncio.to_thread(self.hermes.query, prompt)
            if not answer or answer.startswith("HERMES_ERROR") or answer == "HERMES_TIMEOUT":
                return self._fallback_explain(strategy_name, entry_rule, exit_rule)
            return answer
        except Exception as exc:
            logger.error("Hermes explain_strategy error: %s", exc)
            return self._fallback_explain(strategy_name, entry_rule, exit_rule)

    async def generate_lesson(
        self,
        strategy_name: str,
        symbol: str,
        outcome: str,
        pnl: float,
        metrics: dict,
    ) -> str:
        """
        Generate a lesson learned from a trade outcome.

        Returns:
            Lesson text string
        """
        if not await self.is_available():
            return f"Trade {outcome} with {pnl:.2f} P&L on {symbol}"

        prompt = (
            "Generate a concise trading lesson from this outcome.\n\n"
            f"Strategy: {strategy_name}\n"
            f"Symbol: {symbol}\n"
            f"Outcome: {outcome}\n"
            f"P&L: {pnl:.2f}\n"
            f"Metrics: {json.dumps(metrics)}\n\n"
            "Write one sentence that captures the key takeaway.\n"
        )

        try:
            answer = await asyncio.to_thread(self.hermes.query, prompt)
            if not answer or answer.startswith("HERMES_ERROR") or answer == "HERMES_TIMEOUT":
                return f"Trade {outcome} with {pnl:.2f} P&L on {symbol}"
            return answer.strip()
        except Exception as exc:
            logger.error("Hermes generate_lesson error: %s", exc)
            return f"Trade {outcome} with {pnl:.2f} P&L on {symbol}"

    def _parse_json(self, text: str) -> Optional[dict]:
        """Extract JSON from Hermes response text."""
        text = text.strip()
        # Try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        # Try to find JSON in markdown code block
        if "```" in text:
            parts = text.split("```")
            for part in parts[1::2]:
                try:
                    return json.loads(part.strip())
                except json.JSONDecodeError:
                    continue
        # Try to find JSON object in text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
        return None

    # ── Fallback methods (when Hermes is unavailable) ──────────────────────

    def _fallback_generate(self, symbol: str, timeframe: str) -> dict[str, Any]:
        """Deterministic fallback strategy generation."""
        return {
            "entry_rule": json.dumps({
                "condition": "ema_crossover",
                "fast_period": 12,
                "slow_period": 26,
                "rsi_filter": {"below": 40},
                "volume_confirm": True,
            }),
            "exit_rule": json.dumps({
                "condition": "ema_crossunder",
                "fast_period": 12,
                "slow_period": 26,
                "rsi_exit": {"above": 70},
                "stop_loss_pct": 2.0,
                "take_profit_pct": 5.0,
            }),
            "explanation": f"EMA crossover strategy for {symbol} on {timeframe} timeframe.",
            "confidence": 0.5,
            "reasoning": "Fallback: Hermes unavailable, using default EMA crossover.",
            "source": "fallback",
        }

    def _fallback_validate(self, metrics: dict) -> dict[str, Any]:
        """Deterministic fallback validation."""
        score = 50
        win_rate = metrics.get("win_rate", 0)
        sharpe = metrics.get("sharpe", 0)
        max_dd = metrics.get("max_dd", 0)
        pf = metrics.get("profit_factor", 0)

        if win_rate > 55:
            score += 15
        elif win_rate < 45:
            score -= 15
        if sharpe > 1.5:
            score += 15
        elif sharpe > 1.0:
            score += 10
        if max_dd < 10:
            score += 10
        elif max_dd > 30:
            score -= 15
        if pf > 2.0:
            score += 10
        elif pf < 1.0:
            score -= 10

        score = max(0, min(100, score))
        verdict = "APPROVED" if score >= 70 else "NEEDS_IMPROVEMENT" if score >= 40 else "REJECTED"

        return {
            "score": score,
            "verdict": verdict,
            "reasoning": f"Automated validation: win_rate={win_rate}%, sharpe={sharpe}, max_dd={max_dd}%",
            "suggestions": [],
            "source": "fallback",
        }

    def _fallback_tune(self, strategy_name: str, params: dict) -> dict[str, Any]:
        """Deterministic fallback tuning."""
        # Simple heuristic: adjust first numeric parameter
        for key, val in params.items():
            if isinstance(val, (int, float)):
                return {
                    "param": key,
                    "value": val - 1 if isinstance(val, int) else round(val * 0.95, 2),
                    "reasoning": "Fallback: slight decrease to reduce sensitivity",
                    "source": "fallback",
                }
        return {"param": "fast_period", "value": 10, "reasoning": "Fallback default", "source": "fallback"}

    def _fallback_explain(self, name: str, entry: str, exit_: str) -> str:
        """Deterministic fallback explanation."""
        return f"Strategy '{name}' enters when {entry} and exits when {exit_}."
