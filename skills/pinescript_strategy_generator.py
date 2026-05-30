"""Pine Script generation with multi-model routing and safety validation."""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import aiohttp

from trading_system.config.models import BacktestRequest, ModelRouteDecision, ModelRouteRequest
from trading_system.config.settings import ModelProviderSettings, ModelRoutingSettings
from trading_system.skills.backtesting_skill import BacktestingSkill

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ValidationResult:
    """Syntax and bias validation output."""

    valid: bool
    issues: List[str]


class MultiModelRouter:
    """Route prompts across local and external providers."""

    def __init__(self, routing: ModelRoutingSettings) -> None:
        self.routing = routing

    def choose(self, request: ModelRouteRequest) -> ModelRouteDecision:
        """Choose model based on preference and configured availability."""
        providers = [p for p in self.routing.providers if p.enabled]
        if request.prefer_local and self.routing.local_first:
            for provider in providers:
                if provider.name == "ollama":
                    return ModelRouteDecision(provider=provider.name, model=provider.model, reason="local-first")
        for provider in providers:
            if provider.name == "claude":
                return ModelRouteDecision(provider=provider.name, model=provider.model, reason="primary fallback")
        for provider in providers:
            if provider.name == "openai":
                return ModelRouteDecision(provider=provider.name, model=provider.model, reason="optional fallback")
        if providers:
            provider = providers[0]
            return ModelRouteDecision(provider=provider.name, model=provider.model, reason="first enabled provider")
        raise RuntimeError("No enabled model providers configured")

    async def infer(self, request: ModelRouteRequest) -> str:
        """Run inference through selected provider with fallback chain."""
        providers = [p for p in self.routing.providers if p.enabled]
        if request.prefer_local and self.routing.local_first:
            providers = sorted(providers, key=lambda p: 0 if p.name == "ollama" else 1)

        last_error: Optional[Exception] = None
        for provider in providers:
            try:
                return await self._infer_provider(provider, request)
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                logger.warning(
                    "Model provider failed provider=%s model=%s error=%r type=%s",
                    provider.name,
                    provider.model,
                    exc,
                    type(exc).__name__,
                )
                continue
        raise RuntimeError(f"All model providers failed: {last_error}")

    async def _infer_provider(self, provider: ModelProviderSettings, request: ModelRouteRequest) -> str:
        """Provider-specific inference request."""
        if provider.name == "ollama":
            return await self._ollama_infer(provider, request)
        if provider.name == "claude":
            return await self._claude_infer(provider, request)
        if provider.name == "openai":
            return await self._openai_infer(provider, request)
        raise ValueError(f"Unsupported provider: {provider.name}")

    async def _ollama_infer(self, provider: ModelProviderSettings, request: ModelRouteRequest) -> str:
        base_url = (provider.base_url or "http://localhost:11434").rstrip("/")
        # If a user accidentally sets OLLAMA_URL to ".../api", avoid "/api/api/generate" 404s.
        if base_url.endswith("/api"):
            base_url = base_url[: -len("/api")]
        payload = {
            "model": provider.model,
            "prompt": request.prompt,
            "stream": False,
            "options": {"temperature": request.temperature, "num_predict": request.max_tokens},
        }
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=provider.timeout_sec)) as session:
            async with session.post(f"{base_url}/api/generate", json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                return str(data.get("response", ""))

    async def _claude_infer(self, provider: ModelProviderSettings, request: ModelRouteRequest) -> str:
        api_key = os.getenv(provider.api_key_env or "ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("Claude API key not configured")
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": provider.model,
            "max_tokens": request.max_tokens,
            "messages": [{"role": "user", "content": request.prompt}],
        }
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=provider.timeout_sec)) as session:
            async with session.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                content = data.get("content", [])
                if content and isinstance(content, list):
                    return str(content[0].get("text", ""))
                return str(data)

    async def _openai_infer(self, provider: ModelProviderSettings, request: ModelRouteRequest) -> str:
        api_key = os.getenv(provider.api_key_env or "OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OpenAI API key not configured")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": provider.model,
            "messages": [{"role": "user", "content": request.prompt}],
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
        }
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=provider.timeout_sec)) as session:
            async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                choices = data.get("choices", [])
                if not choices:
                    return ""
                return str(choices[0].get("message", {}).get("content", ""))


class PineScriptStrategyGenerator:
    """Generate, validate, refine, and backtest Pine Script strategies."""

    LOOKAHEAD_PATTERNS = [
        r"barmerge\.lookahead_on",
        r"request\.security\([^)]*lookahead\s*=\s*barmerge\.lookahead_on",
        r"strategy\.opentrades\[\-",
    ]

    def __init__(self, router: MultiModelRouter, backtester: Optional[BacktestingSkill] = None) -> None:
        self.router = router
        self.backtester = backtester or BacktestingSkill()

    def build_prompt(self, indicators: List[str], objective: str) -> str:
        """Construct structured strategy prompt."""
        indicator_lines = "\n".join(f"- {i}" for i in indicators)
        return (
            "You are a Pine Script v5 quant developer.\n"
            "Create a complete strategy() script with:\n"
            "1) clear entry and exit logic\n"
            "2) risk controls (stop loss + take profit)\n"
            "3) comments explaining each block\n"
            "4) no lookahead bias\n"
            "5) valid Pine Script v5 syntax\n\n"
            f"Indicators:\n{indicator_lines}\n\n"
            f"Objective:\n{objective}\n\n"
            "Output only Pine Script code."
        )

    def validate_syntax(self, script: str) -> ValidationResult:
        """Validate minimal Pine syntax and anti-bias constraints."""
        issues: List[str] = []
        if "strategy(" not in script:
            issues.append("Missing strategy() declaration.")
        if "if" not in script:
            issues.append("No conditional logic found.")
        if "strategy.entry" not in script:
            issues.append("No strategy.entry calls found.")
        issues.extend(self.detect_lookahead_bias(script))
        return ValidationResult(valid=not issues, issues=issues)

    def detect_lookahead_bias(self, script: str) -> List[str]:
        """Detect known lookahead bias patterns."""
        found: List[str] = []
        lower = script.lower()
        for pattern in self.LOOKAHEAD_PATTERNS:
            if re.search(pattern, lower):
                found.append(f"Lookahead risk pattern detected: {pattern}")
        return found

    async def indicator_to_strategy(
        self,
        indicators: List[str],
        objective: str,
        symbol: str = "BTC-USD",
        timeframe: str = "1d",
        lookback_days: int = 180,
        max_refine_rounds: int = 2,
    ) -> Dict[str, Any]:
        """Generate and auto-refine a Pine Script strategy and run a backtest."""
        prompt = self.build_prompt(indicators, objective)
        script = await self.router.infer(
            ModelRouteRequest(task="pinescript_generation", prompt=prompt, prefer_local=True, max_tokens=600)
        )
        validation = self.validate_syntax(script)

        rounds = 0
        while not validation.valid and rounds < max_refine_rounds:
            refine_prompt = (
                "Fix the Pine Script issues below while keeping strategy logic intact.\n"
                f"Issues: {validation.issues}\n\n"
                "Return corrected Pine Script v5 only."
            )
            script = await self.router.infer(
                ModelRouteRequest(
                    task="pinescript_refine",
                    prompt=refine_prompt + "\n\n" + script,
                    prefer_local=True,
                    max_tokens=600,
                )
            )
            validation = self.validate_syntax(script)
            rounds += 1

        backtest_request = BacktestRequest(
            symbols=[symbol],
            timeframe=timeframe,
            lookback_days=lookback_days,
            strategy_name="custom_pinescript",
            strategy_params={},
        )
        backtest_result = await self.backtester.run(backtest_request, pinescript_source=script)
        return {
            "script": script,
            "validation": {"valid": validation.valid, "issues": validation.issues},
            "backtest_metrics": backtest_result.metrics.model_dump(),
            "backtest_summary": {
                "total_trades": backtest_result.metrics.total_trades,
                "win_rate": backtest_result.metrics.win_rate,
                "sharpe_ratio": backtest_result.metrics.sharpe_ratio,
                "max_drawdown": backtest_result.metrics.max_drawdown,
            },
        }
