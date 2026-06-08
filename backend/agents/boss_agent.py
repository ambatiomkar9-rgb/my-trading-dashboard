"""Boss Agent — intent parsing, tool dispatch, and multi-step orchestration.

The boss agent receives user chat messages, determines intent, dispatches to
the appropriate child agent or tool, and synthesizes a final response.
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Optional

import httpx

logger = logging.getLogger(__name__)


# ── Tool definitions ────────────────────────────────────────────────────────

TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "analyze_stock",
            "description": "Run technical analysis on a stock symbol. Returns RSI, MACD, trend, support/resistance, and a signal recommendation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock ticker symbol, e.g. INFY, RELIANCE, TCS"},
                    "timeframe": {"type": "string", "enum": ["1h", "4h", "1d"], "description": "Chart timeframe", "default": "1d"},
                },
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_watchlist",
            "description": "Get the current watchlist with symbols, strategies, and auto-trade settings.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_to_watchlist",
            "description": "Add a symbol to the watchlist for monitoring.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol to add"},
                    "auto_trade": {"type": "boolean", "description": "Enable auto-trading", "default": False},
                    "quantity": {"type": "integer", "description": "Quantity to trade", "default": 1},
                },
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remove_from_watchlist",
            "description": "Remove a symbol from the watchlist.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol to remove"},
                },
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_portfolio",
            "description": "Get current portfolio summary — total value, PnL, open positions.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_positions",
            "description": "Get all active trading positions with entry price, current price, and PnL.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_signals",
            "description": "Get pending trade signals awaiting approval.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_strategy",
            "description": "Generate a trading strategy for a symbol using Hermes AI.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol"},
                    "timeframe": {"type": "string", "enum": ["1h", "4h", "1d"], "default": "1d"},
                },
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_strategies",
            "description": "List all trading strategies with their status, PnL, and win rate.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_market_data",
            "description": "Get current price and recent market data for a symbol.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol"},
                },
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_health",
            "description": "Get system health — agents online, broker status, Ollama status.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_news_sentiment",
            "description": "Get recent news and sentiment for a stock symbol.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol"},
                },
                "required": ["symbol"],
            },
        },
    },
]


# ── Intent classification ───────────────────────────────────────────────────

INTENT_PATTERNS: list[tuple[str, list[str]]] = [
    ("analyze", [r"\banalyze\b", r"\btechnical\b", r"\bchart\b", r"\b indicators?\b", r"\brsi\b", r"\bmacd\b", r"\btrend\b"]),
    ("watchlist", [r"\bwatchlist\b", r"\bwatch\b", r"\bmonitor\b", r"\badd.*watch\b", r"\bremove.*watch\b"]),
    ("portfolio", [r"\bportfolio\b", r"\bholdings?\b", r"\bpositions?\b", r"\bpnl\b", r"\bprofit\b", r"\bloss\b"]),
    ("signals", [r"\bsignals?\b", r"\balerts?\b", r"\bpending\b", r"\bapproval\b"]),
    ("strategy", [r"\bstrateg\w*\b", r"\bgenerate\b", r"\bbacktest\b", r"\bhermes\b", r"\bpinescript\b"]),
    ("market", [r"\bprice\b", r"\bltp\b", r"\bmarket\b", r"\bquote\b", r"\bstock\b.*\bprice\b"]),
    ("system", [r"\bhealth\b", r"\bstatus\b", r"\bagent\b", r"\bollama\b", r"\bbroker\b"]),
    ("news", [r"\bnews\b", r"\bsentiment\b", r"\bheadline\b", r"\bwhat.*happening\b"]),
    ("trade", [r"\btrade\b", r"\bbuy\b", r"\bsell\b", r"\border\b", r"\bexecute\b"]),
    ("help", [r"\bhelp\b", r"\bwhat can\b", r"\bcommands?\b", r"\boption\b"]),
]


def classify_intent(message: str) -> str:
    """Classify user intent from message text."""
    lower = message.lower()
    for intent, patterns in INTENT_PATTERNS:
        for pat in patterns:
            if re.search(pat, lower):
                return intent
    return "chat"


def extract_symbol(message: str) -> Optional[str]:
    """Try to extract a stock symbol from the message."""
    # Look for uppercase ticker patterns
    match = re.search(r"\b([A-Z]{2,10})\b", message)
    if match:
        return match.group(1)
    # Look for common Indian stock name patterns
    name_map = {
        "reliance": "RELIANCE", "tcs": "TCS", "infy": "INFY", "infosys": "INFY",
        "hdfc": "HDFCBANK", "icici": "ICICIBANK", "sbi": "SBIN", "wipro": "WIPRO",
        "tata": "TATAMOTORS", "adani": "ADANIENT", "bajaj": "BAJFINANCE",
        "asian": "ASIANPAINT", "maruti": "MARUTI", "sun": "SUNPHARMA",
        "ntpc": "NTPC", "ongc": "ONGC", "coal": "COALINDIA", "itc": "ITC",
        "lt": "LT", "axis": "AXISBANK", "kotak": "KOTAKBANK",
    }
    lower = message.lower()
    for name, ticker in name_map.items():
        if name in lower:
            return ticker
    return None


# ── Tool execution ──────────────────────────────────────────────────────────

@dataclass
class ToolContext:
    """Runtime context available to tool executors."""
    base_url: str = "http://127.0.0.1:8000"
    token: str = ""
    runtime: Any = None


async def _api_call(ctx: ToolContext, method: str, path: str, body: dict | None = None) -> Any:
    """Make an authenticated API call to the dashboard."""
    headers = {"Authorization": f"Bearer {ctx.token}"} if ctx.token else {}
    url = f"{ctx.base_url}{path}"
    async with httpx.AsyncClient(timeout=15, trust_env=False) as client:
        if method == "GET":
            r = await client.get(url, headers=headers)
        elif method == "POST":
            r = await client.post(url, headers=headers, json=body)
        elif method == "DELETE":
            r = await client.delete(url, headers=headers)
        else:
            r = await client.get(url, headers=headers)
        if r.status_code >= 400:
            return {"error": f"HTTP {r.status_code}: {r.text[:200]}"}
        return r.json()


async def execute_tool(name: str, args: dict, ctx: ToolContext) -> Any:
    """Execute a tool by name with the given arguments."""
    try:
        if name == "analyze_stock":
            symbol = args.get("symbol", "INFY").upper()
            data = await _api_call(ctx, "GET", f"/api/market-data/{symbol}")
            return {
                "symbol": symbol,
                "price": data.get("ltp", data.get("current_price", "N/A")),
                "data": data,
            }

        elif name == "get_watchlist":
            return await _api_call(ctx, "GET", "/api/watchlist")

        elif name == "add_to_watchlist":
            symbol = args.get("symbol", "").upper()
            auto_trade = args.get("auto_trade", False)
            quantity = args.get("quantity", 1)
            return await _api_call(ctx, "POST", "/api/watchlist/add", {
                "symbol": symbol, "strategy_id": "default",
                "auto_trade": auto_trade, "quantity_to_buy": quantity,
            })

        elif name == "remove_from_watchlist":
            symbol = args.get("symbol", "").upper()
            return await _api_call(ctx, "POST", "/api/watchlist/remove", {"symbol": symbol})

        elif name == "get_portfolio":
            return await _api_call(ctx, "GET", "/api/portfolio")

        elif name == "get_positions":
            return await _api_call(ctx, "GET", "/positions")

        elif name == "get_signals":
            return await _api_call(ctx, "GET", "/api/signals/pending")

        elif name == "generate_strategy":
            symbol = args.get("symbol", "INFY").upper()
            timeframe = args.get("timeframe", "1d")
            return await _api_call(ctx, "POST", "/strategy/generate", {
                "symbol": symbol, "timeframe": timeframe,
            })

        elif name == "get_strategies":
            return await _api_call(ctx, "GET", "/strategies")

        elif name == "get_market_data":
            symbol = args.get("symbol", "INFY").upper()
            return await _api_call(ctx, "GET", f"/api/market-data/{symbol}")

        elif name == "get_system_health":
            return await _api_call(ctx, "GET", "/api/system/health")

        elif name == "get_news_sentiment":
            symbol = args.get("symbol", "").upper()
            return await _api_call(ctx, "GET", f"/api/news/{symbol}")

        else:
            return {"error": f"Unknown tool: {name}"}

    except Exception as exc:
        logger.error("Tool %s failed: %s", name, exc)
        return {"error": str(exc)}


# ── Conversation memory ─────────────────────────────────────────────────────

def load_recent_history(limit: int = 10) -> list[dict[str, str]]:
    """Load recent chat history from the database."""
    try:
        from backend.database import SessionLocal, ChatHistory
        session = SessionLocal()
        try:
            rows = (
                session.query(ChatHistory)
                .order_by(ChatHistory.id.desc())
                .limit(limit)
                .all()
            )
            return [{"role": r.role, "content": r.message} for r in reversed(rows)]
        finally:
            session.close()
    except Exception as exc:
        logger.debug("Failed to load chat history: %s", exc)
        return []


# ── Boss Agent ──────────────────────────────────────────────────────────────

@dataclass
class BossAgent:
    """The boss agent that orchestrates chat, tool calling, and agent dispatch."""

    ollama_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen2.5:3b"
    ctx: ToolContext = field(default_factory=ToolContext)

    SYSTEM_PROMPT = (
        "You are the boss agent of a trading dashboard. You can:\n"
        "- Analyze stocks (technical indicators, trends, signals)\n"
        "- Manage the watchlist (add/remove symbols)\n"
        "- View portfolio, positions, and P&L\n"
        "- Generate and manage trading strategies\n"
        "- Check system health and agent status\n"
        "- Get news and market sentiment\n"
        "- Execute trades (paper or live)\n\n"
        "When the user asks to analyze, check, or look at a stock, use the analyze_stock tool.\n"
        "When they want to add/remove from watchlist, use the watchlist tools.\n"
        "When they ask about portfolio or positions, use the portfolio tools.\n"
        "When they want a strategy, use generate_strategy.\n"
        "Always use tools when available — don't just describe what you could do.\n"
        "Be concise and factual. Use bullet points for lists.\n"
    )

    async def process(self, message: str, chat_id: str = "user") -> str:
        """Process a user message and return a response."""
        # Load conversation memory
        history = load_recent_history(limit=10)

        # Build messages for Ollama
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]
        messages.extend(history)
        messages.append({"role": "user", "content": message})

        # Call Ollama with tools
        reply = await self._call_ollama(messages)

        # Parse tool calls from the response
        tool_calls = self._extract_tool_calls(reply)

        if tool_calls:
            # Execute tools and build context
            tool_results = []
            for tc in tool_calls:
                result = await execute_tool(tc["name"], tc.get("args", {}), self.ctx)
                tool_results.append({
                    "tool": tc["name"],
                    "args": tc.get("args", {}),
                    "result": result,
                })

            # Build a follow-up message with tool results
            tool_context = json.dumps(tool_results, indent=2, default=str)
            followup_messages = messages.copy()
            followup_messages.append({
                "role": "assistant",
                "content": f"I'll use these tools to help you:\n{json.dumps([tc['name'] for tc in tool_calls])}",
            })
            followup_messages.append({
                "role": "user",
                "content": f"Tool results:\n{tool_context}\n\nNow answer the user's original question: {message}",
            })

            # Get final response from Ollama with tool context
            final_reply = await self._call_ollama(followup_messages)
            return final_reply or self._format_tool_results(tool_results)

        return reply or self._fallback_response(message)

    async def _call_ollama(self, messages: list[dict]) -> str:
        """Call Ollama with messages and return the response."""
        from backend.infra.circuit_breaker import get_breaker
        breaker = get_breaker("ollama", failure_threshold=3, recovery_timeout=30)

        if not breaker.allow_request():
            logger.warning("Ollama circuit breaker OPEN — using fallback")
            return ""

        try:
            async with httpx.AsyncClient(timeout=60, trust_env=False) as client:
                response = await client.post(
                    f"{self.ollama_url.rstrip('/')}/api/chat",
                    json={
                        "model": self.ollama_model,
                        "messages": messages,
                        "tools": TOOLS,
                        "stream": False,
                    },
                )
                response.raise_for_status()
                payload = response.json()
                content = payload.get("message", {}).get("content", "")
                breaker.record_success()
                return content
        except Exception as exc:
            breaker.record_failure()
            logger.warning("Ollama call failed: %s", exc)
            return ""

    def _extract_tool_calls(self, reply: str) -> list[dict]:
        """Extract tool calls from Ollama response or fallback to intent classification."""
        # Try to parse structured tool calls from the response
        # Ollama may return tool_calls in the message
        # For now, use intent classification as the primary mechanism
        # and try to parse JSON tool calls from the response text

        # Look for JSON tool call patterns in the response
        json_match = re.search(r'\[?\{[^{}]*"name"\s*:\s*"[^"]+"[^{}]*\}?\]', reply)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                if isinstance(parsed, dict):
                    return [parsed]
                elif isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, ValueError):
                pass

        return []

    def _format_tool_results(self, results: list[dict]) -> str:
        """Format tool results into a human-readable response."""
        parts = []
        for r in results:
            tool = r["tool"]
            result = r["result"]
            if isinstance(result, dict) and "error" in result:
                parts.append(f"**{tool}**: Error — {result['error']}")
            elif tool == "analyze_stock":
                symbol = r["args"].get("symbol", "?")
                price = result.get("price", "N/A") if isinstance(result, dict) else "N/A"
                parts.append(f"**{symbol}**: Current price ₹{price}")
            elif tool == "get_watchlist":
                if isinstance(result, list):
                    symbols = [i.get("symbol", "?") for i in result if i.get("status") != "removed"]
                    parts.append(f"**Watchlist** ({len(symbols)}): {', '.join(symbols) if symbols else 'empty'}")
                else:
                    parts.append(f"**Watchlist**: {result}")
            elif tool == "get_portfolio":
                if isinstance(result, dict):
                    val = result.get("total_value", 0)
                    pnl = result.get("total_pnl", 0)
                    parts.append(f"**Portfolio**: ₹{val:.0f} (P&L: {'+' if pnl >= 0 else ''}{pnl:.0f})")
                else:
                    parts.append(f"**Portfolio**: {result}")
            elif tool == "get_positions":
                if isinstance(result, list) and result:
                    parts.append(f"**Positions** ({len(result)}):")
                    for pos in result[:5]:
                        sym = pos.get("symbol", "?")
                        pnl = pos.get("pnl", 0)
                        parts.append(f"  - {sym}: ₹{pnl:.2f}")
                else:
                    parts.append("**Positions**: None")
            elif tool == "get_signals":
                if isinstance(result, list) and result:
                    parts.append(f"**Pending Signals** ({len(result)}):")
                    for sig in result[:3]:
                        parts.append(f"  - {sig.get('symbol', '?')}: {sig.get('approval_status', '?')}")
                else:
                    parts.append("**Signals**: None pending")
            elif tool == "generate_strategy":
                if isinstance(result, dict) and result.get("explanation"):
                    parts.append(f"**Strategy Generated**: {result['explanation']}")
                else:
                    parts.append(f"**Strategy**: {result}")
            elif tool == "get_strategies":
                if isinstance(result, list) and result:
                    parts.append(f"**Strategies** ({len(result)}):")
                    for s in result[:5]:
                        parts.append(f"  - {s.get('name', '?')} ({s.get('symbol', '?')}): {s.get('status', '?')}")
                else:
                    parts.append("**Strategies**: None")
            elif tool == "get_system_health":
                if isinstance(result, dict):
                    parts.append(f"**System**: Agents online: {result.get('agents_online', '?')}, Ollama: {result.get('ollama_status', '?')}")
                else:
                    parts.append(f"**System**: {result}")
            else:
                parts.append(f"**{tool}**: {json.dumps(result, default=str)[:200]}")

        return "\n".join(parts) if parts else "Tools executed successfully."

    def _fallback_response(self, message: str) -> str:
        """Generate a fallback response when Ollama is unavailable."""
        intent = classify_intent(message)
        symbol = extract_symbol(message)
        fallbacks = {
            "analyze": f"I'd analyze {symbol or 'a stock'} but the LLM is currently offline. Try again in a moment.",
            "watchlist": "I'd help with your watchlist but the AI engine is temporarily unavailable.",
            "portfolio": "I'd check your portfolio but the AI engine is temporarily unavailable.",
            "strategy": f"I'd generate a strategy for {symbol or 'a symbol'} but the AI engine is offline.",
            "market": f"I'd get the price for {symbol or 'a stock'} but the AI engine is offline.",
            "system": "I'd check system health but the AI engine is offline. You can check the agent monitor on the left.",
            "help": "I can help with: stock analysis, watchlist management, portfolio, strategies, market data, and more. The AI engine is currently offline — try again shortly.",
            "chat": "The AI engine is temporarily offline. I can help with analysis, watchlist, portfolio, strategies, and more once it's back.",
        }
        return fallbacks.get(intent, fallbacks["chat"])
