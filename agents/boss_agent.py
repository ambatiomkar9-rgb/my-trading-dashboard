"""Boss agent: plans work, delegates to specialist agents, verifies, stores, responds.

This agent is the orchestrator for dashboard chat commands.

High-level flow for "analyze X":
1) Parse command -> intent.
2) Plan which agents/data providers to use.
3) Fetch real data (market data, technical, news, macro).
4) Verify consistency (basic sanity checks).
5) Ask AnalysisAgent (with Hermes) to produce a report.
6) Store the report/inputs in local storage (reflexion DB) for reuse.
7) Reply back to the dashboard via /chat/submit-response.

For "backtest X":
1) Plan data + strategy.
2) Run backtest.
3) Use Hermes-guided tuning loop to iterate parameters (self-learning).
4) Store results and lessons.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, TYPE_CHECKING

from dotenv import load_dotenv

if TYPE_CHECKING:
    from trading_system.execution.execution_engine import ExecutionEngine
    from trading_system.agents.risk_guardian import RiskGuardian

# Ensure `import trading_system.*` works when running this file directly.
_PKG_DIR = Path(__file__).resolve().parents[1]  # .../trading_system
_REPO_ROOT = _PKG_DIR.parent
sys.path.insert(0, str(_REPO_ROOT))
load_dotenv(_PKG_DIR / ".env")

_LOGS_DIR = _PKG_DIR / "logs"
_LOGS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(str(_LOGS_DIR / f"agent_{datetime.now().strftime('%Y%m%d')}.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

from trading_system.agents.analysis_agent import AnalysisAgent, AnalysisBundle
from trading_system.agents.backtesting_agent import BacktestingAgent, BacktestTuningSpec
from trading_system.agents.macro_agent import MacroIntelligenceAgent
from trading_system.agents.news_agent import NewsSentimentAgent
from trading_system.agents.technical_agent import TechnicalAnalysisAgent
from trading_system.agents.whale_agent import WhaleIntelligenceAgent
from trading_system.config.models import (
    CommandIntent,
    CommandIntentType,
    ExecutionCommand,
    OrderRequest,
    RiskApproved,
    RiskCheckRequested,
    RiskRejected,
    SignalEmitted,
    TradingMode,
)
from trading_system.events.event_bus import AsyncEventBus
from trading_system.events.event_types import EventType
from trading_system.execution.persistent_live_approval import PersistentLiveApprovalManager
from trading_system.integrations.hermes_client import HermesClient
from trading_system.memory.global_state import GlobalState
from trading_system.memory.reflexion_memory import ReflexionEntry, ReflexionMemoryRepository
from trading_system.skills.chatbot_command_parser import ChatbotCommandParser
from trading_system.skills.market_data_router import MarketDataRouter
from trading_system.skills.news_intelligence_skill import NewsIntelligenceSkill
from trading_system.skills.symbol_resolver import SymbolResolver
from trading_system.skills.technical_analysis_skill import TechnicalAnalysisSkill
from trading_system.skills.whale_tracker_skill import WhaleTrackerSkill

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
OLLAMA_FALLBACK = os.getenv("OLLAMA_FALLBACK", "deepseek-r1:7b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")

DASHBOARD_URL = os.getenv("DASHBOARD_URL", "https://my-trading-dashboard-8.onrender.com").rstrip("/")
POLL_INTERVAL = int(os.getenv("AGENT_POLL_INTERVAL", "3"))
_DASHBOARD_ERR_THROTTLE_SEC = int(os.getenv("DASHBOARD_ERROR_THROTTLE_SEC", "60"))
_last_dashboard_err_at = 0.0

LOCAL_DB_PATH = os.getenv(
    "TRADING_LOCAL_SQLITE_PATH",
    str((_PKG_DIR / "data" / "trading_system.db").resolve()),
)


def _post_json(url: str, payload: dict, timeout: int = 15) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body) if body else {}


def _get_json(url: str, timeout: int = 15) -> dict:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body) if body else {}


def post_agent_status(status: str, task: str = "", progress: int = 0) -> None:
    payload = {
        "agent_id": "boss_agent",
        "status": status,
        "task": task,
        "progress": progress,
        "skills": ["analysis", "backtesting", "orchestration", "execution"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    try:
        _post_json(f"{DASHBOARD_URL}/agent-status", payload, timeout=10)
    except Exception as exc:  # noqa: BLE001
        global _last_dashboard_err_at
        now = time.time()
        if now - _last_dashboard_err_at >= _DASHBOARD_ERR_THROTTLE_SEC:
            _last_dashboard_err_at = now
            logger.warning("Dashboard unreachable for agent-status url=%s error=%s", DASHBOARD_URL, exc)


def get_pending_command() -> Optional[Dict[str, Any]]:
    try:
        data = _get_json(f"{DASHBOARD_URL}/chat/pending-commands", timeout=10)
        cmds = data.get("commands", [])
        return cmds[0] if cmds else None
    except Exception as exc:  # noqa: BLE001
        global _last_dashboard_err_at
        now = time.time()
        if now - _last_dashboard_err_at >= _DASHBOARD_ERR_THROTTLE_SEC:
            _last_dashboard_err_at = now
            logger.warning("Dashboard unreachable for pending-commands url=%s error=%s", DASHBOARD_URL, exc)
        return None


def submit_response(command_id: str, response_text: str) -> None:
    try:
        _post_json(f"{DASHBOARD_URL}/chat/submit-response", {"command_id": command_id, "response": response_text}, timeout=20)
    except Exception as exc:  # noqa: BLE001
        global _last_dashboard_err_at
        now = time.time()
        if now - _last_dashboard_err_at >= _DASHBOARD_ERR_THROTTLE_SEC:
            _last_dashboard_err_at = now
            logger.warning("Dashboard unreachable for submit-response url=%s error=%s", DASHBOARD_URL, exc)


@dataclass(slots=True)
class OllamaClient:
    base_url: str = OLLAMA_URL
    model: str = OLLAMA_MODEL
    fallback: str = OLLAMA_FALLBACK
    timeout_sec: int = int(os.getenv("OLLAMA_TIMEOUT_SEC", "180"))

    def generate(self, prompt: str, model: Optional[str] = None) -> str:
        m = model or self.model
        try:
            resp = _post_json(
                f"{self.base_url}/api/generate",
                {"model": m, "prompt": prompt, "stream": False},
                timeout=self.timeout_sec,
            )
            return str(resp.get("response", "")).strip()
        except Exception as exc:
            logger.warning("Ollama failed model=%s error=%s", m, exc)
            if m != self.fallback:
                return self.generate(prompt, model=self.fallback)
            return "Error: LLM unavailable"


class BossAgent:
    """Orchestrator agent for both chat commands and execution orchestration."""

    def __init__(
        self,
        parser: Optional[ChatbotCommandParser] = None,
        technical_agent: Optional[TechnicalAnalysisAgent] = None,
        whale_agent: Optional[WhaleIntelligenceAgent] = None,
        macro_agent: Optional[MacroIntelligenceAgent] = None,
        news_agent: Optional[NewsSentimentAgent] = None,
        analysis_agent: Optional[AnalysisAgent] = None,
        backtesting_agent: Optional[BacktestingAgent] = None,
        market_data: Optional[MarketDataRouter] = None,
        hermes: Optional[HermesClient] = None,
        approval_manager: Optional[PersistentLiveApprovalManager] = None,
        reflexion_repo: Optional[ReflexionMemoryRepository] = None,
        execution_engine: Optional[ExecutionEngine] = None,
        risk_guardian: Optional[RiskGuardian] = None,
        global_state: Optional[GlobalState] = None,
        event_bus: Optional[AsyncEventBus] = None,
        backtester: Optional[BacktestingSkill] = None,
    ) -> None:
        self.instance_id = f"boss-agent-{os.getpid()}"
        self.parser = parser or ChatbotCommandParser()
        self.symbol_resolver = SymbolResolver()
        self.market_data = market_data or MarketDataRouter()
        self.hermes = hermes or HermesClient()
        self.ollama = OllamaClient()

        self.technical_agent = technical_agent or TechnicalAnalysisAgent(TechnicalAnalysisSkill())
        self.whale_agent = whale_agent or WhaleIntelligenceAgent(WhaleTrackerSkill())
        self.macro_agent = macro_agent or MacroIntelligenceAgent()
        self.news_agent = news_agent or NewsSentimentAgent(NewsIntelligenceSkill())
        self.analysis_agent = analysis_agent or AnalysisAgent(self.hermes)
        self.backtesting_agent = backtesting_agent or BacktestingAgent(hermes=self.hermes)
        self.backtester_skill = backtester # Store for main.py compatibility

        self.execution_engine = execution_engine
        self.risk_guardian = risk_guardian
        self.global_state = global_state
        self.event_bus = event_bus

        approvals_sqlite = os.getenv(
            "LIVE_APPROVAL_SQLITE_PATH",
            str((_PKG_DIR / "data" / "live_approvals.db").resolve()),
        ).strip()
        if approvals_sqlite and not Path(approvals_sqlite).is_absolute():
            approvals_sqlite = str((_PKG_DIR / approvals_sqlite).resolve())
        self.approval_manager = approval_manager or PersistentLiveApprovalManager(
            sqlite_path=approvals_sqlite,
            ttl_seconds=int(os.getenv("LIVE_APPROVAL_TTL_SECONDS", "300")),
        )

        self.reflexion_repo = reflexion_repo or ReflexionMemoryRepository(sqlite_path=LOCAL_DB_PATH)
        self._repo_initialized = False

        if self.event_bus:
            self._register_event_handlers()

        # Hermes preflight
        ok, info = self.hermes.healthcheck()
        if ok:
            logger.info("Hermes connected: %s", info)
        else:
            logger.warning("Hermes unavailable: %s", info)

    def _register_event_handlers(self) -> None:
        """Subscribe to HERMES v5.2 event streams."""
        if not self.event_bus:
            return
        self.event_bus.subscribe(EventType.SIGNAL_EMITTED, self._handle_signal_emitted)
        self.event_bus.subscribe(EventType.RISK_APPROVED, self._handle_risk_approved)
        self.event_bus.subscribe(EventType.RISK_REJECTED, self._handle_risk_rejected)

    async def _handle_signal_emitted(self, event: Any) -> None:
        """
        Consume SIGNAL_EMITTED and publish RISK_CHECK_REQUESTED.
        Matches HERMES v5.2 Task 1.2 BossAgent responsibilities.
        """
        # Validate TTL (Check III-001)
        # Assuming event is an AsyncEventBus Event wrapper, or the SignalEmitted model
        try:
            payload = event.payload if hasattr(event, 'payload') else event
            timestamp = payload.get("timestamp")
            if isinstance(timestamp, str):
                 timestamp = datetime.fromisoformat(timestamp)
            
            if timestamp and (datetime.now(timezone.utc) - timestamp).total_seconds() > 30:
                logger.warning("Signal TTL exceeded. Dropping signal_id=%s", event.event_id)
                return

            # Build RISK_CHECK_REQUESTED
            risk_request = RiskCheckRequested(
                correlation_id=event.correlation_id,
                source_component="boss_agent",
                source_instance=self.instance_id,
                payload=payload
            )
            
            if self.event_bus:
                await self.event_bus.publish(risk_request)
                logger.info("Published RISK_CHECK_REQUESTED for symbol=%s", payload.get("symbol"))
        except Exception as e:
            logger.error("Error handling signal emitted: %s", e)

    async def _handle_risk_approved(self, event: Any) -> None:
        """
        Consume RISK_APPROVED and publish EXECUTION_COMMAND.
        """
        try:
            # Build EXECUTION_COMMAND
            exec_command = ExecutionCommand(
                correlation_id=event.correlation_id,
                source_component="boss_agent",
                source_instance=self.instance_id,
                payload=event.payload
            )
            
            if self.event_bus:
                await self.event_bus.publish(exec_command)
                logger.info("Published EXECUTION_COMMAND for correlation_id=%s", event.correlation_id)
        except Exception as e:
            logger.error("Error handling risk approved: %s", e)

    async def _handle_risk_rejected(self, event: Any) -> None:
        """Log and alert on risk rejections."""
        logger.warning("Risk REJECTED for correlation_id=%s reasons=%s", 
                       event.correlation_id, event.payload.get("reasons"))

    async def _ensure_repo(self) -> None:
        if self._repo_initialized:
            return
        Path(LOCAL_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
        await self.reflexion_repo.initialize()
        self._repo_initialized = True

    async def handle_command(self, command: str):
        """Parse + route command into specialist handlers."""
        await self._ensure_repo()

        handlers = {
            CommandIntentType.ANALYZE: self._handle_analyze,
            CommandIntentType.BACKTEST: self._handle_backtest,
            CommandIntentType.WHALE_ACTIVITY: self._handle_whale,
            CommandIntentType.APPROVE_LIVE: self._handle_approve_live,
        }
        parsed = await self.parser.route(command, handlers=handlers)
        # Persist assistant response into reflexion memory for later retrieval.
        try:
            entry = ReflexionEntry(
                symbol=(parsed.intent.symbol or "GLOBAL"),
                strategy_id=(parsed.intent.strategy or "default"),
                outcome="analysis",
                pnl=0.0,
                lesson=parsed.response[:2000],
                created_at=datetime.now(timezone.utc),
            )
            await self.reflexion_repo.add_entry(entry)
        except Exception:
            pass
        return parsed

    async def _handle_analyze(self, intent: CommandIntent) -> Dict[str, Any]:
        raw_symbol = (intent.symbol or "").strip()
        resolved = self.symbol_resolver.resolve(raw_symbol)
        timeframe = (intent.timeframe or "1d").lower()

        # Plan: for equities -> technical + news + macro; for crypto -> technical + whale + macro + news.
        plan = {"symbol": resolved, "timeframe": timeframe, "steps": ["market_data", "technical", "news", "macro", "compose_report"]}

        # Real market price from best provider.
        price, price_meta = await self.market_data.get_latest_price(resolved)

        technical = await self.technical_agent.run(resolved, timeframe=timeframe, lookback="6mo")
        news = await self.news_agent.run(resolved)
        macro = await self.macro_agent.run()

        # Basic verification checks.
        warnings = []
        if price <= 0:
            warnings.append("invalid_price")
        if not isinstance(technical, dict) or "signal" not in technical:
            warnings.append("technical_missing")
        if not isinstance(news, dict):
            warnings.append("news_missing")

        bundle = AnalysisBundle(
            symbol=resolved,
            timeframe=timeframe,
            market_data={"price": price, "provider": price_meta.get("provider")},
            technical=technical,
            news=news,
            macro=macro,
        )
        analysis = await self.analysis_agent.analyze(bundle)

        # Store "raw inputs" in reflexion memory as context for self-learning.
        try:
            entry = ReflexionEntry(
                symbol=resolved,
                strategy_id="analysis",
                outcome="context",
                pnl=0.0,
                lesson=json.dumps({"plan": plan, "warnings": warnings, "bundle": analysis}, ensure_ascii=True)[:2000],
                created_at=datetime.now(timezone.utc),
            )
            await self.reflexion_repo.add_entry(entry)
        except Exception:
            pass

        return {
            "plan": plan,
            "warnings": warnings,
            "price": analysis.get("price"),
            "trend": analysis.get("trend"),
            "rsi": technical.get("rsi"),
            "signal": analysis.get("signal"),
            "news_sentiment": analysis.get("news_sentiment"),
            "report": analysis.get("report"),
        }

    async def _handle_backtest(self, intent: CommandIntent) -> Dict[str, Any]:
        raw_symbol = (intent.symbol or "").strip()
        resolved = self.symbol_resolver.resolve(raw_symbol)
        timeframe = (intent.timeframe or "1d").lower()

        # Translate "6 months" to days (basic).
        lookback = (intent.lookback or "6 months").lower()
        lookback_days = 180
        if "year" in lookback:
            lookback_days = 365
        elif "month" in lookback:
            try:
                num = int("".join(ch for ch in lookback if ch.isdigit()) or "6")
                lookback_days = max(30, min(3650, num * 30))
            except Exception:
                lookback_days = 180

        strategy = (intent.strategy or "ema_crossover").strip().lower()
        params: Dict[str, Any] = {}
        if strategy in {"ema_crossover", "ema", "ema_cross"}:
            params = {"fast": 21, "slow": 55}
        elif strategy in {"rsi", "rsi_reversion"}:
            params = {"oversold": 30, "exit": 55}

        plan = {
            "symbol": resolved,
            "timeframe": timeframe,
            "lookback_days": lookback_days,
            "strategy": strategy,
            "steps": ["load_history", "backtest", "hermes_tuning"],
        }

        tuning = await self.backtesting_agent.run_with_learning(
            symbol=resolved,
            timeframe=timeframe,
            lookback_days=lookback_days,
            strategy_name=strategy,
            strategy_params=params,
            spec=BacktestTuningSpec(success_return_pct=5.0, failure_return_pct=-2.0, max_rounds=6),
        )

        best = tuning["best"]
        metrics = best["metrics"]

        # Store best result + tuning history.
        try:
            entry = ReflexionEntry(
                symbol=resolved,
                strategy_id=strategy,
                outcome="backtest",
                pnl=float(metrics.get("net_profit") or 0.0),
                lesson=json.dumps({"plan": plan, "best": best, "history": tuning["history"]}, ensure_ascii=True)[:2000],
                created_at=datetime.now(timezone.utc),
            )
            await self.reflexion_repo.add_entry(entry)
        except Exception:
            pass

        return {"plan": plan, "metrics": metrics, "best_params": best["params"], "rounds": len(tuning["history"])}

    async def _handle_whale(self, intent: CommandIntent) -> Dict[str, Any]:
        # Default BTC for whale checks unless specified in raw command.
        symbol = self.symbol_resolver.resolve(intent.symbol or "BTC")
        return await self.whale_agent.run(symbol)

    async def _handle_approve_live(self, intent: CommandIntent) -> Dict[str, Any]:
        ticket_id = str((intent.extra or {}).get("ticket_id") or "").strip()
        if not ticket_id:
            return {"status": "error", "message": "Missing ticket id"}
        try:
            ticket = await self.approval_manager.approve_ticket(ticket_id=ticket_id, approved_by="dashboard_operator")
            return {"status": "approved", "ticket": ticket}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}


async def _poll_loop() -> None:
    agent = BossAgent()
    while True:
        post_agent_status("online", "Waiting for dashboard commands", 0)
        cmd = get_pending_command()
        if cmd:
            cid = cmd.get("command_id")
            msg = cmd.get("message", "")
            post_agent_status("processing", f"Planning: {msg[:60]}", 35)
            try:
                parsed = await agent.handle_command(msg)
                # If analysis payload includes a richer report, prefer that.
                response_text = parsed.response
                if isinstance(parsed.payload, dict) and parsed.payload.get("report"):
                    response_text = str(parsed.payload.get("report"))
                submit_response(str(cid), response_text)
                post_agent_status("idle", "Command complete", 100)
                logger.info("Processed command %s intent=%s", cid, parsed.intent.intent.value)
            except Exception as exc:
                logger.error("Boss loop error: %s", exc, exc_info=True)
                submit_response(str(cid), f"Error: {exc}")
                post_agent_status("error", str(exc), 0)
        await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(_poll_loop())
