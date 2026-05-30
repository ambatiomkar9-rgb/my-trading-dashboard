"""Natural-language command parsing and routing helpers."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, Optional

from trading_system.config.models import CommandIntent, CommandIntentType, OrderSide, TradingMode

logger = logging.getLogger(__name__)

CommandHandler = Callable[[CommandIntent], Awaitable[Dict[str, Any]]]


@dataclass(slots=True)
class ParsedCommand:
    """Formatted chatbot response wrapper."""

    intent: CommandIntent
    response: str
    payload: Dict[str, Any]


class ChatbotCommandParser:
    """
    Parse natural language trading commands.

    Examples:
      - Analyze INFY 4h
      - Backtest BTC strategy for 6 months
      - Buy RELIANCE 10 shares paper mode
      - Show whale activity
      - What is current risk?
    """

    # Accept either a ticker-like symbol (INFY, BTC-USD, BTC/USDT, TATAMOTORS.NS)
    # or a company/name phrase ("tata motors"). Name phrases are resolved later.
    ANALYZE_RE = re.compile(r"analy[sz]e\s+(?P<symbol>.+?)(?:\s+(?P<tf>\d+[mhdw]))?$", re.I)
    BACKTEST_RE = re.compile(
        r"backtest\s+(?P<symbol>.+?)(?:\s+strategy)?(?:\s+for\s+(?P<period>\d+\s*(?:day|days|week|weeks|month|months|year|years)))?$",
        re.I,
    )
    ORDER_RE = re.compile(
        r"(?P<side>buy|sell)\s+(?P<symbol>[A-Za-z0-9._/-]+)\s+(?P<qty>\d+(?:\.\d+)?)\s*(?:shares|units)?(?:\s+(?P<mode>paper|live)\s+mode)?",
        re.I,
    )
    APPROVE_RE = re.compile(r"approve\s+(?P<ticket>LIVEAP-[A-Za-z0-9]+)", re.I)

    def parse(self, command: str) -> CommandIntent:
        """Parse raw command into structured intent."""
        text = command.strip()
        lower = text.lower()

        analyze = self.ANALYZE_RE.search(text)
        if analyze:
            return CommandIntent(
                intent=CommandIntentType.ANALYZE,
                raw_command=text,
                symbol=analyze.group("symbol").strip().upper(),
                timeframe=(analyze.group("tf") or "1d").lower(),
            )

        backtest = self.BACKTEST_RE.search(text)
        if backtest:
            period = backtest.group("period") or "6 months"
            return CommandIntent(
                intent=CommandIntentType.BACKTEST,
                raw_command=text,
                symbol=backtest.group("symbol").strip().upper(),
                lookback=period.lower(),
                strategy="ema_crossover",
            )

        order = self.ORDER_RE.search(text)
        if order:
            mode_str = (order.group("mode") or "paper").lower()
            return CommandIntent(
                intent=CommandIntentType.PLACE_ORDER,
                raw_command=text,
                symbol=order.group("symbol").upper(),
                quantity=float(order.group("qty")),
                mode=TradingMode(mode_str),
                side=OrderSide(order.group("side").lower()),
            )

        approve = self.APPROVE_RE.search(text)
        if approve:
            return CommandIntent(
                intent=CommandIntentType.APPROVE_LIVE,
                raw_command=text,
                extra={"ticket_id": approve.group("ticket").strip()},
            )

        if "whale" in lower:
            return CommandIntent(intent=CommandIntentType.WHALE_ACTIVITY, raw_command=text)
        if "current risk" in lower or "risk" == lower:
            return CommandIntent(intent=CommandIntentType.CURRENT_RISK, raw_command=text)

        return CommandIntent(intent=CommandIntentType.UNKNOWN, raw_command=text)

    async def route(
        self,
        command: str,
        handlers: Dict[CommandIntentType, CommandHandler],
    ) -> ParsedCommand:
        """Parse command and route to handler."""
        intent = self.parse(command)
        handler = handlers.get(intent.intent)
        if not handler:
            response = (
                "I could not map that command. Try: "
                "`Analyze INFY 4h`, `Backtest BTC for 6 months`, or `Buy RELIANCE 10 shares paper mode`."
            )
            return ParsedCommand(intent=intent, response=response, payload={})
        try:
            payload = await handler(intent)
            response = self._format_response(intent, payload)
            return ParsedCommand(intent=intent, response=response, payload=payload)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Command route failed intent=%s", intent.intent.value)
            return ParsedCommand(
                intent=intent,
                response=f"Command failed safely: {type(exc).__name__}",
                payload={"error": str(exc)},
            )

    def _format_response(self, intent: CommandIntent, payload: Dict[str, Any]) -> str:
        """Format normalized response by intent."""
        if intent.intent == CommandIntentType.ANALYZE:
            return (
                f"Analysis for {intent.symbol} ({intent.timeframe}): "
                f"trend={payload.get('trend')} rsi={payload.get('rsi')} signal={payload.get('signal')}"
            )
        if intent.intent == CommandIntentType.BACKTEST:
            metrics = payload.get("metrics", {})
            return (
                f"Backtest {intent.symbol}: win_rate={metrics.get('win_rate', 0):.2f}% "
                f"sharpe={metrics.get('sharpe_ratio', 0):.2f} "
                f"max_dd={metrics.get('max_drawdown', 0):.2%} "
                f"profit_factor={metrics.get('profit_factor', 0):.2f}"
            )
        if intent.intent == CommandIntentType.PLACE_ORDER:
            return f"Order status: {payload.get('status')} | id={payload.get('order_id')} | mode={intent.mode.value}"
        if intent.intent == CommandIntentType.WHALE_ACTIVITY:
            return (
                f"Whale sentiment={payload.get('sentiment')} "
                f"alerts={len(payload.get('alerts', []))}"
            )
        if intent.intent == CommandIntentType.CURRENT_RISK:
            return (
                f"Risk: exposure={payload.get('gross_exposure')} "
                f"daily_pnl={payload.get('daily_realized_pnl')} "
                f"kill_switch={payload.get('kill_switch_active')}"
            )
        if intent.intent == CommandIntentType.APPROVE_LIVE:
            return f"Live approval: {payload.get('status')} | ticket={intent.extra.get('ticket_id')}"
        return "No response formatter configured."
