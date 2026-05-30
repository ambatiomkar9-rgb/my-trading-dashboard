"""Unit tests for chatbot command parser."""

from __future__ import annotations

from trading_system.config.models import CommandIntentType, TradingMode
from trading_system.skills.chatbot_command_parser import ChatbotCommandParser


def test_parse_analyze_command() -> None:
    parser = ChatbotCommandParser()
    intent = parser.parse("Analyze INFY 4h")
    assert intent.intent == CommandIntentType.ANALYZE
    assert intent.symbol == "INFY"
    assert intent.timeframe == "4h"


def test_parse_backtest_command() -> None:
    parser = ChatbotCommandParser()
    intent = parser.parse("Backtest BTC strategy for 6 months")
    assert intent.intent == CommandIntentType.BACKTEST
    assert intent.symbol == "BTC"


def test_parse_order_command() -> None:
    parser = ChatbotCommandParser()
    intent = parser.parse("Buy RELIANCE 10 shares paper mode")
    assert intent.intent == CommandIntentType.PLACE_ORDER
    assert intent.symbol == "RELIANCE"
    assert intent.quantity == 10
    assert intent.mode == TradingMode.PAPER


def test_parse_risk_command() -> None:
    parser = ChatbotCommandParser()
    intent = parser.parse("What is current risk?")
    assert intent.intent == CommandIntentType.CURRENT_RISK
