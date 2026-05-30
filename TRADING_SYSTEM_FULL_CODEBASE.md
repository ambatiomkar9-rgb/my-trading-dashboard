# TRADING SYSTEM FULL CODEBASE DUMP

Generated on: 30-05-2026 08:51
Root Directory: C:\Users\ambat\Documents\Codex\2026-05-18\files-mentioned-by-the-user-multi\trading_system


--- START FILE: .env ---
# Ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
OLLAMA_FALLBACK=deepseek-r1:7b
OLLAMA_TIMEOUT_SEC=180

# Dashboard
DASHBOARD_URL=https://my-trading-dashboard-8.onrender.com
DASHBOARD_TIMEOUT=15

# Agents
AGENT_POLL_INTERVAL=3
AGENT_STATUS_INTERVAL=5

# Risk - lower limits
TRADING_MODE=paper
MAX_POSITION_SIZE=0.03
MAX_DAILY_LOSS=0.015
MAX_CORRELATION_ALLOWED=0.6

# Telegram
TELEGRAM_BOT_TOKEN=7935173149:AAG95IEX13LL6LB5tl9iHPp-DZ7xko6B7f8
TELEGRAM_CHAT_ID=6409689311
TELEGRAM_ALERT_COOLDOWN_SECONDS=60

# NewsAPI (optional)
NEWSAPI_KEY=095c82378cf94cacb157ba39e856b064
NEWSAPI_TIMEOUT_SEC=4.5

# Brokers (optional)
BINANCE_API_KEY=
BINANCE_API_SECRET=
BINANCE_SANDBOX=true

ALPACA_API_KEY=
ALPACA_API_SECRET=ss
ALPACA_ACCOUNT_ID=
ALPACA_SANDBOX=true

UPSTOX_API_KEY=226da382-6060-466a-a86b-9ebf9c18d2fa
UPSTOX_API_SECRET=bszpl0mknt
UPSTOX_REDIRECT_URI=http://127.0.0.1:8000/callback
UPSTOX_ACCESS_TOKEN=eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI1UEMyRFoiLCJqdGkiOiI2YTEyYTAxMjg3NzljYTRkYjM1NzZhNzciLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc3OTYwNTUyMiwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzc5NjYwMDAwfQ.qiGRVGe_NRJSVGiEONlHGFfd6fefeJ_VB3QxQMH2BxY

# Live approvals shared across agent processes
LIVE_APPROVAL_SQLITE_PATH=./data/live_approvals.db
LIVE_APPROVAL_TTL_SECONDS=300

# Trade execution agent defaults
EXECUTION_AGENT_POLL_INTERVAL=5
DEFAULT_STOP_LOSS_PCT=2.0
DEFAULT_TAKE_PROFIT_PCT=5.0

# Hermes (recommended on this laptop): call Hermes inside WSL directly (no SSH keys needed)
# If you want a specific distro: set HERMES_WSL_DISTRO=Ubuntu-26.04 (example) or set HERMES_CMD.
HERMES_CMD=wsl /home/ambat/.local/bin/hermes
HERMES_WSL_DISTRO=
HERMES_TIMEOUT_SEC=120
HERMES_ACCEPT_HOOKS=true

# Optional SSH bridge (only needed if Hermes is on a separate Ubuntu machine)
HERMES_SSH_HOST=
HERMES_SSH_USER=
HERMES_SSH_PORT=22
HERMES_SSH_IDENTITY_FILE=
HERMES_SSH_CONNECT_TIMEOUT_SEC=6

--- END FILE: .env ---

--- START FILE: .env.example ---
TRADING_ENV=dev
TRADING_MODE=paper
TRADING_DB_URL=sqlite+aiosqlite:///./trading_system/data/trading_system.db
TRADING_DEFAULT_LIVE_BROKER=binance
TRADING_API_HOST=0.0.0.0
TRADING_API_PORT=8000
TRADING_REQUIRE_API_KEY=true
TRADING_API_KEYS=change-me-long-random-key
TRADING_RATE_LIMIT_ENABLED=true
TRADING_RATE_LIMIT_RPM=120
TRADING_LIVE_APPROVAL_TTL_SECONDS=300

BINANCE_API_KEY=
BINANCE_API_SECRET=
BINANCE_SANDBOX=true

ALPACA_API_KEY=
ALPACA_API_SECRET=
ALPACA_ACCOUNT_ID=
ALPACA_SANDBOX=true

OANDA_API_KEY=
OANDA_ACCOUNT_ID=
OANDA_SANDBOX=true

ANTHROPIC_API_KEY=
OPENAI_API_KEY=

TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
TELEGRAM_WEBHOOK_SECRET=

TELEGRAM_ALERT_COOLDOWN_SECONDS=60

# NewsAPI (optional, recommended for NewsSentimentAgent)
NEWSAPI_KEY=
NEWSAPI_TIMEOUT_SEC=4.5

# Hermes
# Recommended on this laptop (Windows + WSL): call Hermes inside WSL directly (no SSH keys needed).
# If Hermes is not on PATH inside non-login shells, use the absolute path.
# If you have multiple distros, set HERMES_WSL_DISTRO to the distro name from: wsl -l -v
HERMES_CMD=wsl /home/ambat/.local/bin/hermes
HERMES_WSL_DISTRO=
HERMES_TIMEOUT_SEC=120
HERMES_ACCEPT_HOOKS=true

# Optional: SSH bridge (only needed if Hermes runs on a separate Ubuntu machine / VM).
# Note: BatchMode requires SSH keys (no password prompts).
HERMES_SSH_HOST=
HERMES_SSH_USER=
HERMES_SSH_PORT=22
# Windows example: C:\\Users\\ambat\\.ssh\\id_ed25519
HERMES_SSH_IDENTITY_FILE=
HERMES_SSH_CONNECT_TIMEOUT_SEC=6

# Upstox (optional) - you will still need to complete OAuth/token wiring
UPSTOX_API_KEY=
UPSTOX_API_SECRET=
UPSTOX_REDIRECT_URI=
UPSTOX_ACCESS_TOKEN=

# Live approvals shared across agents (so Boss can approve tickets for the executor)
LIVE_APPROVAL_SQLITE_PATH=./trading_system/data/live_approvals.db
LIVE_APPROVAL_TTL_SECONDS=300

# Execution agent polling + defaults
EXECUTION_AGENT_POLL_INTERVAL=5
DEFAULT_STOP_LOSS_PCT=2.0
DEFAULT_TAKE_PROFIT_PCT=5.0

--- END FILE: .env.example ---

--- START FILE: .gitignore ---
.env
venv/
__pycache__/
logs/

--- END FILE: .gitignore ---

--- START FILE: aggregate_codebase.py ---
import os

root_dir = r"C:\Users\ambat\Documents\Codex\2026-05-18\files-mentioned-by-the-user-multi\trading_system"
output_file = r"C:\Users\ambat\Documents\Codex\2026-05-18\files-mentioned-by-the-user-multi\trading_system\TRADING_SYSTEM_FULL_CODEBASE.md"

exclude_dirs = {
    "venv", ".venv", "__pycache__", ".git", "node_modules", "logs", "dist", ".github"
}
exclude_extensions = {
    ".db", ".pyc", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".woff", ".woff2", ".ttf", ".eot", ".exe", ".bin"
}
exclude_files = {
    "package-lock.json", ".token_key", "NTUSER.DAT", "ntuser.dat.LOG1", "ntuser.dat.LOG2"
}

with open(output_file, "w", encoding="utf-8") as f_out:
    f_out.write("# TRADING SYSTEM FULL CODEBASE DUMP\n\n")
    f_out.write(f"Generated on: {os.popen('date /t').read().strip()} {os.popen('time /t').read().strip()}\n")
    f_out.write("Root Directory: " + root_dir + "\n\n")
    
    for root, dirs, files in os.walk(root_dir):
        # Filter directories in-place
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in exclude_extensions or file in exclude_files:
                continue
            
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, root_dir)
            
            f_out.write(f"\n--- START FILE: {relative_path} ---\n")
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f_in:
                    content = f_in.read()
                    f_out.write(content)
            except Exception as e:
                f_out.write(f"[ERROR READING FILE: {e}]")
            f_out.write(f"\n--- END FILE: {relative_path} ---\n")

print(f"Aggregation complete. Output saved to: {output_file}")

--- END FILE: aggregate_codebase.py ---

--- START FILE: backend.py ---
"""
Trading Agent Dashboard - FastAPI Server
Connects your existing agents to a web interface
"""

from __future__ import annotations
import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List
import uuid

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========================================
# Initialize Your Agents
# ========================================

def init_agents():
    """Load your existing agents"""
    try:
        from trading_system.agents.technical_agent import TechnicalAnalysisAgent
        from trading_system.agents.whale_agent import WhaleIntelligenceAgent
        from trading_system.agents.macro_agent import MacroIntelligenceAgent
        from trading_system.agents.news_agent import NewsSentimentAgent
        
        return {
            "technical": TechnicalAnalysisAgent(),
            "whale": WhaleIntelligenceAgent(),
            "macro": MacroIntelligenceAgent(),
            "news": None,  # Add when ready
        }
    except ImportError as e:
        logger.warning(f"Could not load all agents: {e}")
        return {}

AGENTS = init_agents()

# ========================================
# WebSocket Manager
# ========================================

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"✅ WebSocket connected ({len(self.active_connections)} total)")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for ws in self.active_connections:
            try:
                await ws.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

# ========================================
# Request Models
# ========================================

class AnalyzeRequest(BaseModel):
    symbol: str = "BTC-USD"
    timeframe: str = "1d"

class WhaleRequest(BaseModel):
    coin: str = "BTC"

# ========================================
# FastAPI App
# ========================================

app = FastAPI(
    title="Trading Agent Dashboard",
    version="1.0.0",
    description="Web dashboard for your multi-agent trading system"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================
# API Endpoints
# ========================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Trading Agent Dashboard API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "✅ Healthy",
        "agents_loaded": len(AGENTS),
        "agent_names": list(AGENTS.keys()),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.post("/api/analyze")
async def analyze_symbol(request: AnalyzeRequest):
    """Analyze a symbol using Technical Agent"""
    try:
        if AGENTS.get("technical"):
            result = await AGENTS["technical"].run(
                symbol=request.symbol,
                timeframe=request.timeframe
            )
            return {"status": "success", "data": result}
        return {"status": "success", "message": "Technical agent not loaded", "data": {}}
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/whale/{coin}")
async def whale_activity(coin: str = "BTC"):
    """Get whale activity for a coin"""
    try:
        if AGENTS.get("whale"):
            result = await AGENTS["whale"].run(coin=coin)
            return {"status": "success", "data": result}
        return {"status": "success", "message": "Whale agent not loaded", "data": {}}
    except Exception as e:
        logger.error(f"Whale error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/macro")
async def macro_data():
    """Get macro indicators"""
    try:
        if AGENTS.get("macro"):
            result = await AGENTS["macro"].run()
            return {"status": "success", "data": result}
        return {"status": "success", "message": "Macro agent not loaded", "data": {}}
    except Exception as e:
        logger.error(f"Macro error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# WebSocket
# ========================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
            else:
                await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ========================================
# Startup
# ========================================

@app.on_event("startup")
async def startup():
    logger.info("🚀 Trading Dashboard API started!")
    logger.info(f"📊 Agents loaded: {list(AGENTS.keys())}")

@app.on_event("shutdown")
async def shutdown():
    logger.info("🛑 Trading Dashboard API stopped!")

--- END FILE: backend.py ---

--- START FILE: backendrequirements.txt.txt ---
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
pydantic>=2.8.0

--- END FILE: backendrequirements.txt.txt ---

--- START FILE: GO_LIVE_CHECKLIST.md ---
# Go-Live Checklist

Use this checklist before enabling `TRADING_MODE=live`.

## Security
- [ ] Rotate all previously exposed API keys and tokens.
- [ ] Set `TRADING_REQUIRE_API_KEY=true`.
- [ ] Set a strong `TRADING_API_KEYS` value (32+ random chars).
- [ ] Set `TELEGRAM_WEBHOOK_SECRET`.
- [ ] Restrict inbound network access to trusted operator IPs.

## Runtime
- [ ] Set `TRADING_ENV=prod`.
- [ ] Set `TRADING_RATE_LIMIT_ENABLED=true` and tuned `TRADING_RATE_LIMIT_RPM`.
- [ ] Configure broker credentials only via environment variables.
- [ ] Verify system starts cleanly and `/api/health` is `ok`.

## Safety
- [ ] Confirm kill switch endpoints work.
- [ ] Confirm risk rejections for:
  - [ ] missing stop-loss
  - [ ] excess leverage
  - [ ] excess slippage
- [ ] Confirm live order rejection without `approval_ticket_id`.
- [ ] Confirm live ticket replay is rejected after first use.

## Validation
- [ ] Run full tests: `pytest trading_system/tests -q`.
- [ ] Run paper trading burn-in for at least 3 market sessions.
- [ ] Compare expected vs actual fills/slippage in paper logs.
- [ ] Dry run alerting and recovery process.

## Activation
- [ ] Request and approve live ticket for a tiny pilot order.
- [ ] Submit first live order with approval ticket.
- [ ] Monitor `risk`, `positions`, and event stream continuously.

--- END FILE: GO_LIVE_CHECKLIST.md ---

--- START FILE: main.py ---
"""Application entry point for the multi-agent trading operating system."""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI

from trading_system.agents.boss_agent import BossAgent
from trading_system.agents.macro_agent import MacroIntelligenceAgent
from trading_system.agents.news_agent import NewsSentimentAgent
from trading_system.agents.pinescript_agent import PineScriptGenerationAgent
from trading_system.agents.reflexion_agent import ReflexionAgent
from trading_system.agents.risk_guardian import RiskGuardian
from trading_system.agents.technical_agent import TechnicalAnalysisAgent
from trading_system.agents.whale_agent import WhaleIntelligenceAgent
from trading_system.api.security import ApiKeyGuard, RateLimitMiddleware
from trading_system.api.dashboard_api import create_dashboard_router
from trading_system.api.telegram_api import create_telegram_router
from trading_system.api.websocket_server import WebSocketBroadcaster, create_websocket_router
from trading_system.config.broker_config import load_broker_configs
from trading_system.config.settings import DependencyContainer, load_settings
from trading_system.events.event_bus import AsyncEventBus
from trading_system.events.event_handlers import register_default_handlers
from trading_system.execution.broker_router import (
    AlpacaAdapter,
    BinanceCcxtAdapter,
    BrokerRouter,
    OandaAdapter,
    UpstoxAdapter,
)
from trading_system.execution.execution_engine import ExecutionEngine
from trading_system.execution.persistent_live_approval import PersistentLiveApprovalManager
from trading_system.execution.kill_switch import KillSwitch
from trading_system.execution.live_executor import LiveExecutor
from trading_system.execution.paper_executor import PaperExecutor
from trading_system.memory.global_state import GlobalState
from trading_system.memory.reflexion_memory import ReflexionMemoryRepository
from trading_system.memory.trade_memory import TradeMemoryRepository
from trading_system.memory.vector_memory import VectorMemory
from trading_system.skills.backtesting_skill import BacktestingSkill
from trading_system.skills.chatbot_command_parser import ChatbotCommandParser
from trading_system.skills.news_intelligence_skill import NewsIntelligenceSkill
from trading_system.skills.pinescript_strategy_generator import MultiModelRouter, PineScriptStrategyGenerator
from trading_system.skills.technical_analysis_skill import TechnicalAnalysisSkill
from trading_system.skills.whale_tracker_skill import WhaleTrackerSkill

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)-35s | %(message)s",
)
logger = logging.getLogger("trading_system.main")


def _sqlite_path_from_url(db_url: str) -> str:
    if db_url.startswith("sqlite+aiosqlite:///"):
        return db_url.replace("sqlite+aiosqlite:///", "", 1)
    if db_url.startswith("sqlite:///"):
        return db_url.replace("sqlite:///", "", 1)
    return "./trading_system/data/trading_system.db"


async def build_container() -> DependencyContainer:
    """Construct dependency graph."""
    settings = load_settings()
    if settings.api.require_api_key and not settings.api.api_keys:
        if settings.env.lower() == "prod":
            raise RuntimeError("TRADING_REQUIRE_API_KEY=true but TRADING_API_KEYS is empty.")
        logger.warning("API key auth is enabled but TRADING_API_KEYS is empty.")
    if settings.env.lower() == "prod" and not settings.api.telegram_webhook_secret:
        logger.warning("Production mode without TELEGRAM_WEBHOOK_SECRET configured.")
    db_path = _sqlite_path_from_url(settings.database.url)
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    event_bus = AsyncEventBus(queue_size=10000, worker_count=4)
    global_state = GlobalState(initial_balance=100000.0)
    trade_memory = TradeMemoryRepository(sqlite_path=db_path)
    reflexion_memory = ReflexionMemoryRepository(sqlite_path=db_path)
    vector_memory = VectorMemory(dimension=128)

    await trade_memory.initialize()
    await reflexion_memory.initialize()

    risk_guardian = RiskGuardian(limits=settings.risk_limits)
    kill_switch = KillSwitch()
    approvals_sqlite = os.getenv(
        "LIVE_APPROVAL_SQLITE_PATH",
        str((Path(db_path).parent / "live_approvals.db").resolve()),
    ).strip()
    if approvals_sqlite and not Path(approvals_sqlite).is_absolute():
        approvals_sqlite = str((Path(db_path).parent / approvals_sqlite).resolve())
    live_approval_manager = PersistentLiveApprovalManager(
        sqlite_path=approvals_sqlite,
        ttl_seconds=settings.api.live_approval_ttl_seconds,
    )

    broker_cfg = load_broker_configs(settings)
    adapters = {
        "binance": BinanceCcxtAdapter(broker_cfg["binance"]),
        "alpaca": AlpacaAdapter(broker_cfg["alpaca"]),
        "oanda": OandaAdapter(broker_cfg["oanda"]),
        "upstox": UpstoxAdapter(broker_cfg["upstox"]),
    }
    broker_router = BrokerRouter(adapters=adapters)

    paper_executor = PaperExecutor(global_state=global_state, trade_memory=trade_memory)
    live_executor = LiveExecutor(broker_router=broker_router, trade_memory=trade_memory)
    execution_engine = ExecutionEngine(
        risk_guardian=risk_guardian,
        kill_switch=kill_switch,
        paper_executor=paper_executor,
        live_executor=live_executor,
        global_state=global_state,
        trade_memory=trade_memory,
        event_bus=event_bus,
        live_approval_manager=live_approval_manager,
        require_live_approval_ticket=True,
    )

    # Skills
    parser = ChatbotCommandParser()
    technical_skill = TechnicalAnalysisSkill()
    whale_skill = WhaleTrackerSkill()
    news_skill = NewsIntelligenceSkill()
    backtester = BacktestingSkill()
    model_router = MultiModelRouter(settings.model_routing)
    pinescript_generator = PineScriptStrategyGenerator(router=model_router, backtester=backtester)

    # Agents
    technical_agent = TechnicalAnalysisAgent(technical_skill)
    whale_agent = WhaleIntelligenceAgent(whale_skill)
    macro_agent = MacroIntelligenceAgent()
    news_agent = NewsSentimentAgent(news_skill)
    _ = PineScriptGenerationAgent(generator=pinescript_generator)
    _ = ReflexionAgent(repo=reflexion_memory, vector_memory=vector_memory)

    boss_agent = BossAgent(
        parser=parser,
        technical_agent=technical_agent,
        whale_agent=whale_agent,
        macro_agent=macro_agent,
        news_agent=news_agent,
        backtester=backtester,
        execution_engine=execution_engine,
        risk_guardian=risk_guardian,
        global_state=global_state,
        event_bus=event_bus,
    )

    register_default_handlers(event_bus, global_state, trade_memory)

    return DependencyContainer(
        settings=settings,
        event_bus=event_bus,
        global_state=global_state,
        trade_memory=trade_memory,
        reflexion_memory=reflexion_memory,
        vector_memory=vector_memory,
        risk_guardian=risk_guardian,
        execution_engine=execution_engine,
        boss_agent=boss_agent,
        live_approval_manager=live_approval_manager,
    )


async def auto_recovery_loop(container: DependencyContainer, stop_event: asyncio.Event) -> None:
    """Background monitor for bus/worker health."""
    while not stop_event.is_set():
        try:
            stats = container.event_bus.stats()
            if stats["worker_count"] == 0:
                logger.warning("Event bus workers missing; restarting bus")
                await container.event_bus.start()
            removed = await container.live_approval_manager.cleanup_expired()
            if removed:
                logger.info("Cleaned %s expired live approval tickets", removed)
            await asyncio.sleep(5)
        except asyncio.CancelledError:
            return
        except Exception:  # noqa: BLE001
            logger.exception("Auto-recovery loop error")
            await asyncio.sleep(5)


def create_app() -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI(title="Institutional Multi-Agent Trading OS", version="1.0.0")
    preview_settings = load_settings()
    app.add_middleware(
        RateLimitMiddleware,
        enabled=preview_settings.api.rate_limit_enabled,
        requests_per_minute=preview_settings.api.rate_limit_requests_per_minute,
        exempt_paths={"/api/health"},
    )
    app.state.container = None
    app.state.stop_event = asyncio.Event()
    app.state.recovery_task = None

    @app.on_event("startup")
    async def on_startup() -> None:
        container = await build_container()
        app.state.container = container
        auth_guard = ApiKeyGuard(container.settings)
        await container.event_bus.start()

        broadcaster = WebSocketBroadcaster(container.event_bus)
        broadcaster.register_bus_handlers()
        app.include_router(create_websocket_router(broadcaster))
        app.include_router(create_dashboard_router(container, auth_guard=auth_guard))
        app.include_router(create_telegram_router(container.settings, container.boss_agent, auth_guard=auth_guard))

        app.state.recovery_task = asyncio.create_task(auto_recovery_loop(container, app.state.stop_event))
        logger.info("Trading system startup completed")

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        app.state.stop_event.set()
        recovery_task = app.state.recovery_task
        if recovery_task:
            recovery_task.cancel()
            await asyncio.gather(recovery_task, return_exceptions=True)
        container = app.state.container
        if container:
            await container.event_bus.stop()
        logger.info("Trading system shutdown completed")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("trading_system.main:app", host="0.0.0.0", port=8000, reload=False)

--- END FILE: main.py ---

--- START FILE: postcss.config.js.py ---
module.exports = {
  plugins: {
    '@tailwindcss/postcss': {},
  },
}
--- END FILE: postcss.config.js.py ---

--- START FILE: README.md ---
# Institutional Multi-Agent Trading OS

Production-grade modular, event-driven, risk-first AI trading platform with paper/live/backtest isolation.

## 1) Implementation Order
1. Architecture foundation (`config/`, typed models, DI container)
2. Shared state + memory (`memory/`)
3. Event bus + event contracts (`events/`)
4. Risk guardian (`agents/risk_guardian.py`)
5. Backtesting engine (`skills/backtesting_skill.py`)
6. Chatbot parser (`skills/chatbot_command_parser.py`)
7. Broker router + execution (`execution/`)
8. Whale tracker (`skills/whale_tracker_skill.py`)
9. PineScript generator + model router (`skills/pinescript_strategy_generator.py`)
10. Boss orchestration + APIs (`agents/boss_agent.py`, `api/`, `main.py`)

## 2) Environment Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r trading_system/requirements.txt
```

Create env vars (examples):
```bash
TRADING_MODE=paper
TRADING_DB_URL=sqlite+aiosqlite:///./trading_system/data/trading_system.db
TRADING_DEFAULT_LIVE_BROKER=upstox
TRADING_REQUIRE_API_KEY=true
TRADING_API_KEYS=change-me-long-random-key
TRADING_RATE_LIMIT_ENABLED=true
TRADING_RATE_LIMIT_RPM=120
TRADING_LIVE_APPROVAL_TTL_SECONDS=300
BINANCE_API_KEY=...
BINANCE_API_SECRET=...
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
TELEGRAM_WEBHOOK_SECRET=...
UPSTOX_API_KEY=...
UPSTOX_ACCESS_TOKEN=...
```

## 3) Run
```bash
python -m trading_system.main
```

API base: `http://localhost:8000`

## 4) Test
```bash
pytest trading_system/tests -q
```

## 5) Example API Usage
Health:
```bash
curl http://localhost:8000/api/health
```

Risk snapshot:
```bash
curl "http://localhost:8000/api/risk?mode=paper"
```

If API-key auth is enabled, add header:
```bash
-H "x-api-key: change-me-long-random-key"
```

Paper order:
```bash
curl -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -H "x-api-key: change-me-long-random-key" \
  -d '{
    "symbol":"BTC/USDT",
    "side":"buy",
    "quantity":0.01,
    "mode":"paper",
    "broker":"paper",
    "stop_loss":95000,
    "metadata":{"mark_price":100000}
  }'
```

Backtest:
```bash
curl -X POST http://localhost:8000/api/backtest \
  -H "Content-Type: application/json" \
  -H "x-api-key: change-me-long-random-key" \
  -d '{
    "symbols":["BTC-USD"],
    "timeframe":"1d",
    "lookback_days":180,
    "strategy_name":"ema_crossover",
    "walk_forward_windows":3
  }'
```

## 6) Example Telegram Commands
- `Analyze INFY 4h`
- `Backtest BTC strategy for 6 months`
- `Buy RELIANCE 10 shares paper mode`
- `Show whale activity`
- `What is current risk?`

Use local command endpoint for testing:
```bash
curl -X POST http://localhost:8000/telegram/command \
  -H "Content-Type: application/json" \
  -H "x-api-key: change-me-long-random-key" \
  -d '{"text":"Analyze INFY 4h"}'
```

## 7) Example Paper Trading Flow
1. User/agent submits order intent via chatbot/API.
2. `BossAgent` normalizes intent into `OrderRequest`.
3. `ExecutionEngine` calls `RiskGuardian` (veto authority).
4. On approval, emits `RiskApproved`.
5. `PaperExecutor` simulates fill and updates `GlobalState`.
6. `ExecutionEngine` emits `TradeExecuted`.
7. Trade persisted in `TradeMemoryRepository`.
8. Dashboards/WebSockets reflect position and risk changes.

## 8) Example Live Approval Flow (Mandatory)
1. Build live order payload (`mode=live`).
2. Request approval ticket:
```bash
curl -X POST http://localhost:8000/api/live-approvals/request \
  -H "Content-Type: application/json" \
  -H "x-api-key: change-me-long-random-key" \
  -d '{
    "symbol":"BTC/USDT",
    "side":"buy",
    "quantity":0.01,
    "mode":"live",
    "broker":"binance",
    "stop_loss":95000,
    "metadata":{"mark_price":100000}
  }'
```
3. Approve ticket:
```bash
curl -X POST "http://localhost:8000/api/live-approvals/<TICKET_ID>/approve?approved_by=supervisor" \
  -H "x-api-key: change-me-long-random-key"
```
4. Submit same order with `metadata.approval_ticket_id=<TICKET_ID>`.
5. `ExecutionEngine` consumes ticket once; replay is rejected.

## 9) Safety Guarantees
- Backtests never touch exchange routes.
- Paper orders never hit real brokers.
- Live orders require one-time ticket-based approval plus executor approval path.
- Risk Guardian cannot be bypassed by execution APIs.
- Kill switch can halt all execution paths.
- Secrets are never logged in plain text.

Go-live runbook: `trading_system/GO_LIVE_CHECKLIST.md`

--- END FILE: README.md ---

--- START FILE: requirements.txt ---
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
pydantic>=2.8.0
langgraph>=0.2.0
langchain>=0.2.0
aiohttp>=3.10.0
aiosqlite>=0.20.0
ccxt>=4.4.0
yfinance>=0.2.54
pandas>=2.2.0
numpy>=1.26.0
pytest>=8.3.0
pytest-asyncio>=0.24.0

--- END FILE: requirements.txt ---

--- START FILE: run_trading_stack.ps1 ---
param(
    [int]$FrontendPort = 5173,
    [int]$BackendPort = 8000
)

$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$FrontendDir = Join-Path $RootDir "frontend"
$LogsDir = Join-Path $RootDir "logs"
$PidFile = Join-Path $LogsDir "stack_pids.json"

New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null

function Stop-TrackedProcesses {
    if (-not (Test-Path $PidFile)) {
        return
    }
    try {
        $tracked = Get-Content $PidFile -Raw | ConvertFrom-Json
        foreach ($name in @("backend_pid", "frontend_pid")) {
            $pid = $tracked.$name
            if ($pid) {
                Stop-Process -Id ([int]$pid) -Force -ErrorAction SilentlyContinue
            }
        }
    } catch {
        # Ignore malformed pid file.
    }
}

function Stop-Ports([int[]]$Ports) {
    foreach ($port in $Ports) {
        $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
        foreach ($conn in $conns) {
            Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
        }
    }
}

function Stop-ViteProcesses {
    $nodeProcs = Get-CimInstance Win32_Process -Filter "Name = 'node.exe'" -ErrorAction SilentlyContinue
    foreach ($proc in $nodeProcs) {
        $cmd = $proc.CommandLine
        if ($cmd -and $cmd -match "vite" -and $cmd -match [regex]::Escape($FrontendDir)) {
            Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
        }
    }
}

function Resolve-Python {
    $venvPython = Join-Path $RootDir "venv\Scripts\python.exe"
    $bundledPython = "C:\Users\ambat\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

    function Test-Python([string]$Candidate) {
        if (-not $Candidate) { return $false }
        if ($Candidate -ne "python" -and -not (Test-Path $Candidate)) { return $false }
        try {
            & $Candidate -c "import sys" | Out-Null
            return ($LASTEXITCODE -eq 0)
        } catch {
            return $false
        }
    }

    if ($env:VIRTUAL_ENV) {
        $activePython = Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"
        if (Test-Python $activePython) { return $activePython }
    }
    if (Test-Python $bundledPython) { return $bundledPython }
    if (Test-Python $venvPython) { return $venvPython }
    if (Test-Python "python") { return "python" }
    throw "No usable Python interpreter found."
}

function Wait-ForPort([int]$Port, [int]$TimeoutSec = 20) {
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
        $listen = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        if ($listen) { return $true }
        Start-Sleep -Milliseconds 400
    }
    return $false
}

Stop-TrackedProcesses
Stop-Ports -Ports @(5173, 5174, 5175, $BackendPort)
Stop-ViteProcesses

$pythonExe = Resolve-Python
$WorkspaceDir = Split-Path -Parent $RootDir

$backendCmd = "Set-Location -LiteralPath '$WorkspaceDir'; `$Host.UI.RawUI.WindowTitle='Trading Backend'; & '$pythonExe' -m uvicorn trading_system.main:app --host 127.0.0.1 --port $BackendPort"
$frontendCmd = "Set-Location -LiteralPath '$FrontendDir'; `$Host.UI.RawUI.WindowTitle='Trading Frontend'; cmd /c npm run dev -- --host 127.0.0.1 --port $FrontendPort --strictPort"

$backendProc = Start-Process `
    -FilePath "powershell.exe" `
    -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $backendCmd) `
    -WorkingDirectory $WorkspaceDir `
    -PassThru

$frontendProc = Start-Process `
    -FilePath "powershell.exe" `
    -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $frontendCmd) `
    -WorkingDirectory $FrontendDir `
    -PassThru

@{
    backend_pid = $backendProc.Id
    frontend_pid = $frontendProc.Id
    started_at = (Get-Date).ToString("o")
    frontend_url = "http://localhost:$FrontendPort/"
    backend_url = "http://127.0.0.1:$BackendPort/"
} | ConvertTo-Json | Set-Content -Path $PidFile -Encoding UTF8

$frontendReady = Wait-ForPort -Port $FrontendPort
$backendReady = Wait-ForPort -Port $BackendPort

if (-not $frontendReady -or -not $backendReady) {
    Write-Host "Stack start incomplete. Check the opened Trading Backend/Trading Frontend windows for errors."
    exit 1
}

Write-Host "Trading stack started successfully."
Write-Host "Frontend: http://localhost:$FrontendPort/"
Write-Host "Backend : http://127.0.0.1:$BackendPort/"
Write-Host "To stop everything: powershell -ExecutionPolicy Bypass -File .\stop_trading_stack.ps1"

--- END FILE: run_trading_stack.ps1 ---

--- START FILE: start_all_agents.bat ---
@echo off
setlocal
pushd "%~dp0"

if not exist "logs" mkdir "logs"

rem Prefer venv python if present to avoid PATH issues.
set PY=
if exist "venv\\Scripts\\python.exe" set PY=venv\\Scripts\\python.exe
if "%PY%"=="" (
  where python >nul 2>&1 && set PY=python
)
if "%PY%"=="" (
  where py >nul 2>&1 && set PY=py
)
if "%PY%"=="" (
  echo ERROR: Python not found. Install Python or activate venv.
  popd
  exit /b 1
)

rem Each agent writes its own logs so failures don't disappear when a window closes.
start "boss_agent" cmd /c "%PY% agents\\boss_agent.py 1>>logs\\boss_agent.out.log 2>>logs\\boss_agent.err.log"
start "technical_agent" cmd /c "%PY% agents\\technical_agent.py 1>>logs\\technical_agent.out.log 2>>logs\\technical_agent.err.log"
start "whale_agent" cmd /c "%PY% agents\\whale_agent.py 1>>logs\\whale_agent.out.log 2>>logs\\whale_agent.err.log"
start "macro_agent" cmd /c "%PY% agents\\macro_agent.py 1>>logs\\macro_agent.out.log 2>>logs\\macro_agent.err.log"
start "news_agent" cmd /c "%PY% agents\\news_agent.py 1>>logs\\news_agent.out.log 2>>logs\\news_agent.err.log"
start "pinescript_agent" cmd /c "%PY% agents\\pinescript_agent.py 1>>logs\\pinescript_agent.out.log 2>>logs\\pinescript_agent.err.log"
start "watchlist_executor" cmd /c "%PY% agents\\watchlist_executor.py 1>>logs\\watchlist_executor.out.log 2>>logs\\watchlist_executor.err.log"
start "hermes_advisor_agent" cmd /c "%PY% agents\\hermes_advisor_agent.py 1>>logs\\hermes_advisor_agent.out.log 2>>logs\\hermes_advisor_agent.err.log"
start "trade_execution_agent" cmd /c "%PY% agents\\trade_execution_agent.py 1>>logs\\trade_execution_agent.out.log 2>>logs\\trade_execution_agent.err.log"

popd

--- END FILE: start_all_agents.bat ---

--- START FILE: stop_trading_stack.ps1 ---
$ErrorActionPreference = "SilentlyContinue"

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogsDir = Join-Path $RootDir "logs"
$PidFile = Join-Path $LogsDir "stack_pids.json"

function Stop-Ports([int[]]$Ports) {
    foreach ($port in $Ports) {
        $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
        foreach ($conn in $conns) {
            Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
        }
    }
}

if (Test-Path $PidFile) {
    try {
        $tracked = Get-Content $PidFile -Raw | ConvertFrom-Json
        foreach ($name in @("backend_pid", "frontend_pid")) {
            $pid = $tracked.$name
            if ($pid) {
                Stop-Process -Id ([int]$pid) -Force -ErrorAction SilentlyContinue
            }
        }
    } catch { }
}

Stop-Ports @(5173, 5174, 5175, 8000)
Write-Host "Trading stack stopped."

--- END FILE: stop_trading_stack.ps1 ---

--- START FILE: tailwind.config.js.py ---
@"
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
"@ | Out-File -FilePath "tailwind.config.js" -Encoding utf8

--- END FILE: tailwind.config.js.py ---

--- START FILE: TRADING_SYSTEM_FULL_CODEBASE.md ---
# TRADING SYSTEM FULL CODEBASE DUMP

Generated on: 30-05-2026 08:51
Root Directory: C:\Users\ambat\Documents\Codex\2026-05-18\files-mentioned-by-the-user-multi\trading_system


--- START FILE: .env ---
# Ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
OLLAMA_FALLBACK=deepseek-r1:7b
OLLAMA_TIMEOUT_SEC=180

# Dashboard
DASHBOARD_URL=https://my-trading-dashboard-8.onrender.com
DASHBOARD_TIMEOUT=15

# Agents
AGENT_POLL_INTERVAL=3
AGENT_STATUS_INTERVAL=5

# Risk - lower limits
TRADING_MODE=paper
MAX_POSITION_SIZE=0.03
MAX_DAILY_LOSS=0.015
MAX_CORRELATION_ALLOWED=0.6

# Telegram
TELEGRAM_BOT_TOKEN=7935173149:AAG95IEX13LL6LB5tl9iHPp-DZ7xko6B7f8
TELEGRAM_CHAT_ID=6409689311
TELEGRAM_ALERT_COOLDOWN_SECONDS=60

# NewsAPI (optional)
NEWSAPI_KEY=095c82378cf94cacb157ba39e856b064
NEWSAPI_TIMEOUT_SEC=4.5

# Brokers (optional)
BINANCE_API_KEY=
BINANCE_API_SECRET=
BINANCE_SANDBOX=true

ALPACA_API_KEY=
ALPACA_API_SECRET=ss
ALPACA_ACCOUNT_ID=
ALPACA_SANDBOX=true

UPSTOX_API_KEY=226da382-6060-466a-a86b-9ebf9c18d2fa
UPSTOX_API_SECRET=bszpl0mknt
UPSTOX_REDIRECT_URI=http://127.0.0.1:8000/callback
UPSTOX_ACCESS_TOKEN=eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI1UEMyRFoiLCJqdGkiOiI2YTEyYTAxMjg3NzljYTRkYjM1NzZhNzciLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc3OTYwNTUyMiwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzc5NjYwMDAwfQ.qiGRVGe_NRJSVGiEONlHGFfd6fefeJ_VB3QxQMH2BxY

# Live approvals shared across agent processes
LIVE_APPROVAL_SQLITE_PATH=./data/live_approvals.db
LIVE_APPROVAL_TTL_SECONDS=300

# Trade execution agent defaults
EXECUTION_AGENT_POLL_INTERVAL=5
DEFAULT_STOP_LOSS_PCT=2.0
DEFAULT_TAKE_PROFIT_PCT=5.0

# Hermes (recommended on this laptop): call Hermes inside WSL directly (no SSH keys needed)
# If you want a specific distro: set HERMES_WSL_DISTRO=Ubuntu-26.04 (example) or set HERMES_CMD.
HERMES_CMD=wsl /home/ambat/.local/bin/hermes
HERMES_WSL_DISTRO=
HERMES_TIMEOUT_SEC=120
HERMES_ACCEPT_HOOKS=true

# Optional SSH bridge (only needed if Hermes is on a separate Ubuntu machine)
HERMES_SSH_HOST=
HERMES_SSH_USER=
HERMES_SSH_PORT=22
HERMES_SSH_IDENTITY_FILE=
HERMES_SSH_CONNECT_TIMEOUT_SEC=6

--- END FILE: .env ---

--- START FILE: .env.example ---
TRADING_ENV=dev
TRADING_MODE=paper
TRADING_DB_URL=sqlite+aiosqlite:///./trading_system/data/trading_system.db
TRADING_DEFAULT_LIVE_BROKER=binance
TRADING_API_HOST=0.0.0.0
TRADING_API_PORT=8000
TRADING_REQUIRE_API_KEY=true
TRADING_API_KEYS=change-me-long-random-key
TRADING_RATE_LIMIT_ENABLED=true
TRADING_RATE_LIMIT_RPM=120
TRADING_LIVE_APPROVAL_TTL_SECONDS=300

BINANCE_API_KEY=
BINANCE_API_SECRET=
BINANCE_SANDBOX=true

ALPACA_API_KEY=
ALPACA_API_SECRET=
ALPACA_ACCOUNT_ID=
ALPACA_SANDBOX=true

OANDA_API_KEY=
OANDA_ACCOUNT_ID=
OANDA_SANDBOX=true

ANTHROPIC_API_KEY=
OPENAI_API_KEY=

TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
TELEGRAM_WEBHOOK_SECRET=

TELEGRAM_ALERT_COOLDOWN_SECONDS=60

# NewsAPI (optional, recommended for NewsSentimentAgent)
NEWSAPI_KEY=
NEWSAPI_TIMEOUT_SEC=4.5

# Hermes
# Recommended on this laptop (Windows + WSL): call Hermes inside WSL directly (no SSH keys needed).
# If Hermes is not on PATH inside non-login shells, use the absolute path.
# If you have multiple distros, set HERMES_WSL_DISTRO to the distro name from: wsl -l -v
HERMES_CMD=wsl /home/ambat/.local/bin/hermes
HERMES_WSL_DISTRO=
HERMES_TIMEOUT_SEC=120
HERMES_ACCEPT_HOOKS=true

# Optional: SSH bridge (only needed if Hermes runs on a separate Ubuntu machine / VM).
# Note: BatchMode requires SSH keys (no password prompts).
HERMES_SSH_HOST=
HERMES_SSH_USER=
HERMES_SSH_PORT=22
# Windows example: C:\\Users\\ambat\\.ssh\\id_ed25519
HERMES_SSH_IDENTITY_FILE=
HERMES_SSH_CONNECT_TIMEOUT_SEC=6

# Upstox (optional) - you will still need to complete OAuth/token wiring
UPSTOX_API_KEY=
UPSTOX_API_SECRET=
UPSTOX_REDIRECT_URI=
UPSTOX_ACCESS_TOKEN=

# Live approvals shared across agents (so Boss can approve tickets for the executor)
LIVE_APPROVAL_SQLITE_PATH=./trading_system/data/live_approvals.db
LIVE_APPROVAL_TTL_SECONDS=300

# Execution agent polling + defaults
EXECUTION_AGENT_POLL_INTERVAL=5
DEFAULT_STOP_LOSS_PCT=2.0
DEFAULT_TAKE_PROFIT_PCT=5.0

--- END FILE: .env.example ---

--- START FILE: .gitignore ---
.env
venv/
__pycache__/
logs/

--- END FILE: .gitignore ---

--- START FILE: aggregate_codebase.py ---
import os

root_dir = r"C:\Users\ambat\Documents\Codex\2026-05-18\files-mentioned-by-the-user-multi\trading_system"
output_file = r"C:\Users\ambat\Documents\Codex\2026-05-18\files-mentioned-by-the-user-multi\trading_system\TRADING_SYSTEM_FULL_CODEBASE.md"

exclude_dirs = {
    "venv", ".venv", "__pycache__", ".git", "node_modules", "logs", "dist", ".github"
}
exclude_extensions = {
    ".db", ".pyc", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".woff", ".woff2", ".ttf", ".eot", ".exe", ".bin"
}
exclude_files = {
    "package-lock.json", ".token_key", "NTUSER.DAT", "ntuser.dat.LOG1", "ntuser.dat.LOG2"
}

with open(output_file, "w", encoding="utf-8") as f_out:
    f_out.write("# TRADING SYSTEM FULL CODEBASE DUMP\n\n")
    f_out.write(f"Generated on: {os.popen('date /t').read().strip()} {os.popen('time /t').read().strip()}\n")
    f_out.write("Root Directory: " + root_dir + "\n\n")
    
    for root, dirs, files in os.walk(root_dir):
        # Filter directories in-place
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in exclude_extensions or file in exclude_files:
                continue
            
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, root_dir)
            
            f_out.write(f"\n--- START FILE: {relative_path} ---\n")
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f_in:
                    content = f_in.read()
                    f_out.write(content)
            except Exception as e:
                f_out.write(f"[ERROR READING FILE: {e}]")
            f_out.write(f"\n--- END FILE: {relative_path} ---\n")

print(f"Aggregation complete. Output saved to: {output_file}")

--- END FILE: aggregate_codebase.py ---

--- START FILE: backend.py ---
"""
Trading Agent Dashboard - FastAPI Server
Connects your existing agents to a web interface
"""

from __future__ import annotations
import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List
import uuid

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========================================
# Initialize Your Agents
# ========================================

def init_agents():
    """Load your existing agents"""
    try:
        from trading_system.agents.technical_agent import TechnicalAnalysisAgent
        from trading_system.agents.whale_agent import WhaleIntelligenceAgent
        from trading_system.agents.macro_agent import MacroIntelligenceAgent
        from trading_system.agents.news_agent import NewsSentimentAgent
        
        return {
            "technical": TechnicalAnalysisAgent(),
            "whale": WhaleIntelligenceAgent(),
            "macro": MacroIntelligenceAgent(),
            "news": None,  # Add when ready
        }
    except ImportError as e:
        logger.warning(f"Could not load all agents: {e}")
        return {}

AGENTS = init_agents()

# ========================================
# WebSocket Manager
# ========================================

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"✅ WebSocket connected ({len(self.active_connections)} total)")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for ws in self.active_connections:
            try:
                await ws.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

# ========================================
# Request Models
# ========================================

class AnalyzeRequest(BaseModel):
    symbol: str = "BTC-USD"
    timeframe: str = "1d"

class WhaleRequest(BaseModel):
    coin: str = "BTC"

# ========================================
# FastAPI App
# ========================================

app = FastAPI(
    title="Trading Agent Dashboard",
    version="1.0.0",
    description="Web dashboard for your multi-agent trading system"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================
# API Endpoints
# ========================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Trading Agent Dashboard API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "✅ Healthy",
        "agents_loaded": len(AGENTS),
        "agent_names": list(AGENTS.keys()),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.post("/api/analyze")
async def analyze_symbol(request: AnalyzeRequest):
    """Analyze a symbol using Technical Agent"""
    try:
        if AGENTS.get("technical"):
            result = await AGENTS["technical"].run(
                symbol=request.symbol,
                timeframe=request.timeframe
            )
            return {"status": "success", "data": result}
        return {"status": "success", "message": "Technical agent not loaded", "data": {}}
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/whale/{coin}")
async def whale_activity(coin: str = "BTC"):
    """Get whale activity for a coin"""
    try:
        if AGENTS.get("whale"):
            result = await AGENTS["whale"].run(coin=coin)
            return {"status": "success", "data": result}
        return {"status": "success", "message": "Whale agent not loaded", "data": {}}
    except Exception as e:
        logger.error(f"Whale error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/macro")
async def macro_data():
    """Get macro indicators"""
    try:
        if AGENTS.get("macro"):
            result = await AGENTS["macro"].run()
            return {"status": "success", "data": result}
        return {"status": "success", "message": "Macro agent not loaded", "data": {}}
    except Exception as e:
        logger.error(f"Macro error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# WebSocket
# ========================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
            else:
                await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ========================================
# Startup
# ========================================

@app.on_event("startup")
async def startup():
    logger.info("🚀 Trading Dashboard API started!")
    logger.info(f"📊 Agents loaded: {list(AGENTS.keys())}")

@app.on_event("shutdown")
async def shutdown():
    logger.info("🛑 Trading Dashboard API stopped!")

--- END FILE: backend.py ---

--- START FILE: backendrequirements.txt.txt ---
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
pydantic>=2.8.0

--- END FILE: backendrequirements.txt.txt ---

--- START FILE: GO_LIVE_CHECKLIST.md ---
# Go-Live Checklist

Use this checklist before enabling `TRADING_MODE=live`.

## Security
- [ ] Rotate all previously exposed API keys and tokens.
- [ ] Set `TRADING_REQUIRE_API_KEY=true`.
- [ ] Set a strong `TRADING_API_KEYS` value (32+ random chars).
- [ ] Set `TELEGRAM_WEBHOOK_SECRET`.
- [ ] Restrict inbound network access to trusted operator IPs.

## Runtime
- [ ] Set `TRADING_ENV=prod`.
- [ ] Set `TRADING_RATE_LIMIT_ENABLED=true` and tuned `TRADING_RATE_LIMIT_RPM`.
- [ ] Configure broker credentials only via environment variables.
- [ ] Verify system starts cleanly and `/api/health` is `ok`.

## Safety
- [ ] Confirm kill switch endpoints work.
- [ ] Confirm risk rejections for:
  - [ ] missing stop-loss
  - [ ] excess leverage
  - [ ] excess slippage
- [ ] Confirm live order rejection without `approval_ticket_id`.
- [ ] Confirm live ticket replay is rejected after first use.

## Validation
- [ ] Run full tests: `pytest trading_system/tests -q`.
- [ ] Run paper trading burn-in for at least 3 market sessions.
- [ ] Compare expected vs actual fills/slippage in paper logs.
- [ ] Dry run alerting and recovery process.

## Activation
- [ ] Request and approve live ticket for a tiny pilot order.
- [ ] Submit first live order with approval ticket.
- [ ] Monitor `risk`, `positions`, and event stream continuously.

--- END FILE: GO_LIVE_CHECKLIST.md ---

--- START FILE: main.py ---
"""Application entry point for the multi-agent trading operating system."""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI

from trading_system.agents.boss_agent import BossAgent
from trading_system.agents.macro_agent import MacroIntelligenceAgent
from trading_system.agents.news_agent import NewsSentimentAgent
from trading_system.agents.pinescript_agent import PineScriptGenerationAgent
from trading_system.agents.reflexion_agent import ReflexionAgent
from trading_system.agents.risk_guardian import RiskGuardian
from trading_system.agents.technical_agent import TechnicalAnalysisAgent
from trading_system.agents.whale_agent import WhaleIntelligenceAgent
from trading_system.api.security import ApiKeyGuard, RateLimitMiddleware
from trading_system.api.dashboard_api import create_dashboard_router
from trading_system.api.telegram_api import create_telegram_router
from trading_system.api.websocket_server import WebSocketBroadcaster, create_websocket_router
from trading_system.config.broker_config import load_broker_configs
from trading_system.config.settings import DependencyContainer, load_settings
from trading_system.events.event_bus import AsyncEventBus
from trading_system.events.event_handlers import register_default_handlers
from trading_system.execution.broker_router import (
    AlpacaAdapter,
    BinanceCcxtAdapter,
    BrokerRouter,
    OandaAdapter,
    UpstoxAdapter,
)
from trading_system.execution.execution_engine import ExecutionEngine
from trading_system.execution.persistent_live_approval import PersistentLiveApprovalManager
from trading_system.execution.kill_switch import KillSwitch
from trading_system.execution.live_executor import LiveExecutor
from trading_system.execution.paper_executor import PaperExecutor
from trading_system.memory.global_state import GlobalState
from trading_system.memory.reflexion_memory import ReflexionMemoryRepository
from trading_system.memory.trade_memory import TradeMemoryRepository
from trading_system.memory.vector_memory import VectorMemory
from trading_system.skills.backtesting_skill import BacktestingSkill
from trading_system.skills.chatbot_command_parser import ChatbotCommandParser
from trading_system.skills.news_intelligence_skill import NewsIntelligenceSkill
from trading_system.skills.pinescript_strategy_generator import MultiModelRouter, PineScriptStrategyGenerator
from trading_system.skills.technical_analysis_skill import TechnicalAnalysisSkill
from trading_system.skills.whale_tracker_skill import WhaleTrackerSkill

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)-35s | %(message)s",
)
logger = logging.getLogger("trading_system.main")


def _sqlite_path_from_url(db_url: str) -> str:
    if db_url.startswith("sqlite+aiosqlite:///"):
        return db_url.replace("sqlite+aiosqlite:///", "", 1)
    if db_url.startswith("sqlite:///"):
        return db_url.replace("sqlite:///", "", 1)
    return "./trading_system/data/trading_system.db"


async def build_container() -> DependencyContainer:
    """Construct dependency graph."""
    settings = load_settings()
    if settings.api.require_api_key and not settings.api.api_keys:
        if settings.env.lower() == "prod":
            raise RuntimeError("TRADING_REQUIRE_API_KEY=true but TRADING_API_KEYS is empty.")
        logger.warning("API key auth is enabled but TRADING_API_KEYS is empty.")
    if settings.env.lower() == "prod" and not settings.api.telegram_webhook_secret:
        logger.warning("Production mode without TELEGRAM_WEBHOOK_SECRET configured.")
    db_path = _sqlite_path_from_url(settings.database.url)
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    event_bus = AsyncEventBus(queue_size=10000, worker_count=4)
    global_state = GlobalState(initial_balance=100000.0)
    trade_memory = TradeMemoryRepository(sqlite_path=db_path)
    reflexion_memory = ReflexionMemoryRepository(sqlite_path=db_path)
    vector_memory = VectorMemory(dimension=128)

    await trade_memory.initialize()
    await reflexion_memory.initialize()

    risk_guardian = RiskGuardian(limits=settings.risk_limits)
    kill_switch = KillSwitch()
    approvals_sqlite = os.getenv(
        "LIVE_APPROVAL_SQLITE_PATH",
        str((Path(db_path).parent / "live_approvals.db").resolve()),
    ).strip()
    if approvals_sqlite and not Path(approvals_sqlite).is_absolute():
        approvals_sqlite = str((Path(db_path).parent / approvals_sqlite).resolve())
    live_approval_manager = PersistentLiveApprovalManager(
        sqlite_path=approvals_sqlite,
        ttl_seconds=settings.api.live_approval_ttl_seconds,
    )

    broker_cfg = load_broker_configs(settings)
    adapters = {
        "binance": BinanceCcxtAdapter(broker_cfg["binance"]),
        "alpaca": AlpacaAdapter(broker_cfg["alpaca"]),
        "oanda": OandaAdapter(broker_cfg["oanda"]),
        "upstox": UpstoxAdapter(broker_cfg["upstox"]),
    }
    broker_router = BrokerRouter(adapters=adapters)

    paper_executor = PaperExecutor(global_state=global_state, trade_memory=trade_memory)
    live_executor = LiveExecutor(broker_router=broker_router, trade_memory=trade_memory)
    execution_engine = ExecutionEngine(
        risk_guardian=risk_guardian,
        kill_switch=kill_switch,
        paper_executor=paper_executor,
        live_executor=live_executor,
        global_state=global_state,
        trade_memory=trade_memory,
        event_bus=event_bus,
        live_approval_manager=live_approval_manager,
        require_live_approval_ticket=True,
    )

    # Skills
    parser = ChatbotCommandParser()
    technical_skill = TechnicalAnalysisSkill()
    whale_skill = WhaleTrackerSkill()
    news_skill = NewsIntelligenceSkill()
    backtester = BacktestingSkill()
    model_router = MultiModelRouter(settings.model_routing)
    pinescript_generator = PineScriptStrategyGenerator(router=model_router, backtester=backtester)

    # Agents
    technical_agent = TechnicalAnalysisAgent(technical_skill)
    whale_agent = WhaleIntelligenceAgent(whale_skill)
    macro_agent = MacroIntelligenceAgent()
    news_agent = NewsSentimentAgent(news_skill)
    _ = PineScriptGenerationAgent(generator=pinescript_generator)
    _ = ReflexionAgent(repo=reflexion_memory, vector_memory=vector_memory)

    boss_agent = BossAgent(
        parser=parser,
        technical_agent=technical_agent,
        whale_agent=whale_agent,
        macro_agent=macro_agent,
        news_agent=news_agent,
        backtester=backtester,
        execution_engine=execution_engine,
        risk_guardian=risk_guardian,
        global_state=global_state,
        event_bus=event_bus,
    )

    register_default_handlers(event_bus, global_state, trade_memory)

    return DependencyContainer(
        settings=settings,
        event_bus=event_bus,
        global_state=global_state,
        trade_memory=trade_memory,
        reflexion_memory=reflexion_memory,
        vector_memory=vector_memory,
        risk_guardian=risk_guardian,
        execution_engine=execution_engine,
        boss_agent=boss_agent,
        live_approval_manager=live_approval_manager,
    )


async def auto_recovery_loop(container: DependencyContainer, stop_event: asyncio.Event) -> None:
    """Background monitor for bus/worker health."""
    while not stop_event.is_set():
        try:
            stats = container.event_bus.stats()
            if stats["worker_count"] == 0:
                logger.warning("Event bus workers missing; restarting bus")
                await container.event_bus.start()
            removed = await container.live_approval_manager.cleanup_expired()
            if removed:
                logger.info("Cleaned %s expired live approval tickets", removed)
            await asyncio.sleep(5)
        except asyncio.CancelledError:
            return
        except Exception:  # noqa: BLE001
            logger.exception("Auto-recovery loop error")
            await asyncio.sleep(5)


def create_app() -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI(title="Institutional Multi-Agent Trading OS", version="1.0.0")
    preview_settings = load_settings()
    app.add_middleware(
        RateLimitMiddleware,
        enabled=preview_settings.api.rate_limit_enabled,
        requests_per_minute=preview_settings.api.rate_limit_requests_per_minute,
        exempt_paths={"/api/health"},
    )
    app.state.container = None
    app.state.stop_event = asyncio.Event()
    app.state.recovery_task = None

    @app.on_event("startup")
    async def on_startup() -> None:
        container = await build_container()
        app.state.container = container
        auth_guard = ApiKeyGuard(container.settings)
        await container.event_bus.start()

        broadcaster = WebSocketBroadcaster(container.event_bus)
        broadcaster.register_bus_handlers()
        app.include_router(create_websocket_router(broadcaster))
        app.include_router(create_dashboard_router(container, auth_guard=auth_guard))
        app.include_router(create_telegram_router(container.settings, container.boss_agent, auth_guard=auth_guard))

        app.state.recovery_task = asyncio.create_task(auto_recovery_loop(container, app.state.stop_event))
        logger.info("Trading system startup completed")

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        app.state.stop_event.set()
        recovery_task = app.state.recovery_task
        if recovery_task:
            recovery_task.cancel()
            await asyncio.gather(recovery_task, return_exceptions=True)
        container = app.state.container
        if container:
            await container.event_bus.stop()
        logger.info("Trading system shutdown completed")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("trading_system.main:app", host="0.0.0.0", port=8000, reload=False)

--- END FILE: main.py ---

--- START FILE: postcss.config.js.py ---
module.exports = {
  plugins: {
    '@tailwindcss/postcss': {},
  },
}
--- END FILE: postcss.config.js.py ---

--- START FILE: README.md ---
# Institutional Multi-Agent Trading OS

Production-grade modular, event-driven, risk-first AI trading platform with paper/live/backtest isolation.

## 1) Implementation Order
1. Architecture foundation (`config/`, typed models, DI container)
2. Shared state + memory (`memory/`)
3. Event bus + event contracts (`events/`)
4. Risk guardian (`agents/risk_guardian.py`)
5. Backtesting engine (`skills/backtesting_skill.py`)
6. Chatbot parser (`skills/chatbot_command_parser.py`)
7. Broker router + execution (`execution/`)
8. Whale tracker (`skills/whale_tracker_skill.py`)
9. PineScript generator + model router (`skills/pinescript_strategy_generator.py`)
10. Boss orchestration + APIs (`agents/boss_agent.py`, `api/`, `main.py`)

## 2) Environment Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r trading_system/requirements.txt
```

Create env vars (examples):
```bash
TRADING_MODE=paper
TRADING_DB_URL=sqlite+aiosqlite:///./trading_system/data/trading_system.db
TRADING_DEFAULT_LIVE_BROKER=upstox
TRADING_REQUIRE_API_KEY=true
TRADING_API_KEYS=change-me-long-random-key
TRADING_RATE_LIMIT_ENABLED=true
TRADING_RATE_LIMIT_RPM=120
TRADING_LIVE_APPROVAL_TTL_SECONDS=300
BINANCE_API_KEY=...
BINANCE_API_SECRET=...
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
TELEGRAM_WEBHOOK_SECRET=...
UPSTOX_API_KEY=...
UPSTOX_ACCESS_TOKEN=...
```

## 3) Run
```bash
python -m trading_system.main
```

API base: `http://localhost:8000`

## 4) Test
```bash
pytest trading_system/tests -q
```

## 5) Example API Usage
Health:
```bash
curl http://localhost:8000/api/health
```

Risk snapshot:
```bash
curl "http://localhost:8000/api/risk?mode=paper"
```

If API-key auth is enabled, add header:
```bash
-H "x-api-key: change-me-long-random-key"
```

Paper order:
```bash
curl -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -H "x-api-key: change-me-long-random-key" \
  -d '{
    "symbol":"BTC/USDT",
    "side":"buy",
    "quantity":0.01,
    "mode":"paper",
    "broker":"paper",
    "stop_loss":95000,
    "metadata":{"mark_price":100000}
  }'
```

Backtest:
```bash
curl -X POST http://localhost:8000/api/backtest \
  -H "Content-Type: application/json" \
  -H "x-api-key: change-me-long-random-key" \
  -d '{
    "symbols":["BTC-USD"],
    "timeframe":"1d",
    "lookback_days":180,
    "strategy_name":"ema_crossover",
    "walk_forward_windows":3
  }'
```

## 6) Example Telegram Commands
- `Analyze INFY 4h`
- `Backtest BTC strategy for 6 months`
- `Buy RELIANCE 10 shares paper mode`
- `Show whale activity`
- `What is current risk?`

Use local command endpoint for testing:
```bash
curl -X POST http://localhost:8000/telegram/command \
  -H "Content-Type: application/json" \
  -H "x-api-key: change-me-long-random-key" \
  -d '{"text":"Analyze INFY 4h"}'
```

## 7) Example Paper Trading Flow
1. User/agent submits order intent via chatbot/API.
2. `BossAgent` normalizes intent into `OrderRequest`.
3. `ExecutionEngine` calls `RiskGuardian` (veto authority).
4. On approval, emits `RiskApproved`.
5. `PaperExecutor` simulates fill and updates `GlobalState`.
6. `ExecutionEngine` emits `TradeExecuted`.
7. Trade persisted in `TradeMemoryRepository`.
8. Dashboards/WebSockets reflect position and risk changes.

## 8) Example Live Approval Flow (Mandatory)
1. Build live order payload (`mode=live`).
2. Request approval ticket:
```bash
curl -X POST http://localhost:8000/api/live-approvals/request \
  -H "Content-Type: application/json" \
  -H "x-api-key: change-me-long-random-key" \
  -d '{
    "symbol":"BTC/USDT",
    "side":"buy",
    "quantity":0.01,
    "mode":"live",
    "broker":"binance",
    "stop_loss":95000,
    "metadata":{"mark_price":100000}
  }'
```
3. Approve ticket:
```bash
curl -X POST "http://localhost:8000/api/live-approvals/<TICKET_ID>/approve?approved_by=supervisor" \
  -H "x-api-key: change-me-long-random-key"
```
4. Submit same order with `metadata.approval_ticket_id=<TICKET_ID>`.
5. `ExecutionEngine` consumes ticket once; replay is rejected.

## 9) Safety Guarantees
- Backtests never touch exchange routes.
- Paper orders never hit real brokers.
- Live orders require one-time ticket-based approval plus executor approval path.
- Risk Guardian cannot be bypassed by execution APIs.
- Kill switch can halt all execution paths.
- Secrets are never logged in plain text.

Go-live runbook: `trading_system/GO_LIVE_CHECKLIST.md`

--- END FILE: README.md ---

--- START FILE: requirements.txt ---
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
pydantic>=2.8.0
langgraph>=0.2.0
langchain>=0.2.0
aiohttp>=3.10.0
aiosqlite>=0.20.0
ccxt>=4.4.0
yfinance>=0.2.54
pandas>=2.2.0
numpy>=1.26.0
pytest>=8.3.0
pytest-asyncio>=0.24.0

--- END FILE: requirements.txt ---

--- START FILE: run_trading_stack.ps1 ---
param(
    [int]$FrontendPort = 5173,
    [int]$BackendPort = 8000
)

$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$FrontendDir = Join-Path $RootDir "frontend"
$LogsDir = Join-Path $RootDir "logs"
$PidFile = Join-Path $LogsDir "stack_pids.json"

New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null

function Stop-TrackedProcesses {
    if (-not (Test-Path $PidFile)) {
        return
    }
    try {
        $tracked = Get-Content $PidFile -Raw | ConvertFrom-Json
        foreach ($name in @("backend_pid", "frontend_pid")) {
            $pid = $tracked.$name
            if ($pid) {
                Stop-Process -Id ([int]$pid) -Force -ErrorAction SilentlyContinue
            }
        }
    } catch {
        # Ignore malformed pid file.
    }
}

function Stop-Ports([int[]]$Ports) {
    foreach ($port in $Ports) {
        $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
        foreach ($conn in $conns) {
            Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
        }
    }
}

function Stop-ViteProcesses {
    $nodeProcs = Get-CimInstance Win32_Process -Filter "Name = 'node.exe'" -ErrorAction SilentlyContinue
    foreach ($proc in $nodeProcs) {
        $cmd = $proc.CommandLine
        if ($cmd -and $cmd -match "vite" -and $cmd -match [regex]::Escape($FrontendDir)) {
            Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
        }
    }
}

function Resolve-Python {
    $venvPython = Join-Path $RootDir "venv\Scripts\python.exe"
    $bundledPython = "C:\Users\ambat\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

    function Test-Python([string]$Candidate) {
        if (-not $Candidate) { return $false }
        if ($Candidate -ne "python" -and -not (Test-Path $Candidate)) { return $false }
        try {
            & $Candidate -c "import sys" | Out-Null
            return ($LASTEXITCODE -eq 0)
        } catch {
            return $false
        }
    }

    if ($env:VIRTUAL_ENV) {
        $activePython = Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"
        if (Test-Python $activePython) { return $activePython }
    }
    if (Test-Python $bundledPython) { return $bundledPython }
    if (Test-Python $venvPython) { return $venvPython }
    if (Test-Python "python") { return "python" }
    throw "No usable Python interpreter found."
}

function Wait-ForPort([int]$Port, [int]$TimeoutSec = 20) {
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
        $listen = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        if ($listen) { return $true }
        Start-Sleep -Milliseconds 400
    }
    return $false
}

Stop-TrackedProcesses
Stop-Ports -Ports @(5173, 5174, 5175, $BackendPort)
Stop-ViteProcesses

$pythonExe = Resolve-Python
$WorkspaceDir = Split-Path -Parent $RootDir

$backendCmd = "Set-Location -LiteralPath '$WorkspaceDir'; `$Host.UI.RawUI.WindowTitle='Trading Backend'; & '$pythonExe' -m uvicorn trading_system.main:app --host 127.0.0.1 --port $BackendPort"
$frontendCmd = "Set-Location -LiteralPath '$FrontendDir'; `$Host.UI.RawUI.WindowTitle='Trading Frontend'; cmd /c npm run dev -- --host 127.0.0.1 --port $FrontendPort --strictPort"

$backendProc = Start-Process `
    -FilePath "powershell.exe" `
    -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $backendCmd) `
    -WorkingDirectory $WorkspaceDir `
    -PassThru

$frontendProc = Start-Process `
    -FilePath "powershell.exe" `
    -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $frontendCmd) `
    -WorkingDirectory $FrontendDir `
    -PassThru

@{
    backend_pid = $backendProc.Id
    frontend_pid = $frontendProc.Id
    started_at = (Get-Date).ToString("o")
    frontend_url = "http://localhost:$FrontendPort/"
    backend_url = "http://127.0.0.1:$BackendPort/"
} | ConvertTo-Json | Set-Content -Path $PidFile -Encoding UTF8

$frontendReady = Wait-ForPort -Port $FrontendPort
$backendReady = Wait-ForPort -Port $BackendPort

if (-not $frontendReady -or -not $backendReady) {
    Write-Host "Stack start incomplete. Check the opened Trading Backend/Trading Frontend windows for errors."
    exit 1
}

Write-Host "Trading stack started successfully."
Write-Host "Frontend: http://localhost:$FrontendPort/"
Write-Host "Backend : http://127.0.0.1:$BackendPort/"
Write-Host "To stop everything: powershell -ExecutionPolicy Bypass -File .\stop_trading_stack.ps1"

--- END FILE: TRADING_SYSTEM_FULL_CODEBASE.md ---

--- START FILE: ULTRA_MASTER_SYSTEM_CONTEXT.md ---
# ULTRA MASTER SYSTEM CONTEXT (Reverse Engineered)

Generated: 2026-05-25 (Asia/Calcutta)
Last Updated: 2026-05-27 (Asia/Calcutta)

Scope: This document reconstructs the *implemented* system found on disk in:

- `C:\Users\ambat\Documents\Codex\2026-05-18\files-mentioned-by-the-user-multi\trading_system`
- `...\trading_system\trading-dashboard` (cloud dashboard repo deployed on Render)

Accuracy policy:
- **VERIFIED IMPLEMENTATION**: confirmed by file existence + code inspection in this workspace.
- **INFERRED IMPLEMENTATION**: inferred from naming, partial code, or runtime/log evidence.
- **PARTIAL IMPLEMENTATION**: exists but incomplete / stubbed / not production complete.
- **MISSING IMPLEMENTATION**: requested in conversation but not present in code.

No systems/files are invented. When uncertain, it is labeled explicitly.

---

## CHANGELOG (Session Addenda)

### 2026-05-27 Addendum (VERIFIED): Dashboard "Phase A Foundation" Rollout + Render Stabilization
This session implemented and deployed a set of "Phase A" execution-safety building blocks in the **cloud dashboard repo**
(`trading-dashboard/`) and resolved multiple Render deploy failures. These changes are **verified on disk** in the repo and
were deployed via successive GitHub pushes (Render auto-deploy).

Key themes:
- Render default Python version drift required pinning Python 3.11.
- SQLite schema/index drift required removing duplicate index declarations and adding a boot-safety guard.
- Dataclass `slots=True` required explicit field declarations for attributes set during `__post_init__`.
- Frontend build behavior on Render was inconsistent with expectations; a "no-rebuild" **UI hotfix injector** was added to
  `frontend/dist/index.html` so the Kill Switch UI can appear even when the TS bundle isn't rebuilt.

## 1. COMPLETE SYSTEM OVERVIEW

### VERIFIED IMPLEMENTATION: What The System Actually Is
This workspace contains **two related systems**:

1. **Local Multi-Agent Trading OS** (runs on the user's laptop)
   - Python multi-agent system implementing:
     - Boss/orchestrator agent
     - Specialist research agents (technical, whale, macro, news)
     - PineScript strategy generator agent (LLM-assisted)
     - Learning/analysis agents (AnalysisAgent, BacktestingAgent)
     - Execution pipeline: RiskGuardian → ExecutionEngine → Paper/Live executor → BrokerRouter
     - Memory: local SQLite repositories + in-memory state + lightweight vector memory
     - Telegram webhook endpoint (local) for command relay
   - Primary entrypoint: `main.py` (FastAPI app factory) and also individual `agents/*.py` runners.

2. **Cloud Trading Dashboard** (deployed on Render)
   - A combined React frontend + FastAPI backend.
   - Provides:
     - Chat UI (command queue + responses)
     - Agent monitor (websocket)
     - Trading/Strategies/Backtesting/Screener/Settings/Watchlist/Signals pages
     - Simple DB-backed watchlist + signal approval storage (SQLite or Postgres via `DATABASE_URL`)
   - Repo root: `trading-dashboard/`
   - Deployment: Render auto-deploy on GitHub push.
   - Live URL (from env/docs): `https://my-trading-dashboard-8.onrender.com`

### VERIFIED IMPLEMENTATION: Designed To Do
Overall system goal:
- Enable a human-in-the-loop trading workflow where a **cloud dashboard** collects user commands and shows system state, while **local agents** fetch real data and do analysis/backtesting/strategy generation, and optionally execute trades (paper/live with strict gating).

### Architectural Philosophy / Engineering Principles (VERIFIED + INFERRED)
- **Risk-first, veto-based execution**: `RiskGuardian` can reject any order before it reaches brokers.
- **Isolation by mode**: `TradingMode` enum: `paper`, `live`, `backtest`. Backtest cannot execute trades; paper cannot hit brokers; live requires explicit approval.
- **Event-driven internal plumbing**: `AsyncEventBus` publishes typed events (risk approved/rejected, trade executed, kill switch triggered).
- **Separation of concerns**:
  - Skills: pure-ish computation/data fetching (`skills/`)
  - Agents: coordination + decision logic (`agents/`)
  - Execution: broker routing + approvals (`execution/`)
  - Memory: persistence and state snapshots (`memory/`)
  - APIs: FastAPI routers (`api/`)
  - Cloud dashboard: separate runtime and persistence boundary (`trading-dashboard/`)
- **Local models for reasoning** (conversation requirement): Ollama is used for reasoning/LLM tasks; real market data is fetched via APIs (yfinance/ccxt/etc).

### Current Maturity Level (VERIFIED)
- Cloud dashboard is functional and deployed, but deployment stability required changes:
  - Render blueprint was adjusted to be more robust (see `trading-dashboard/render.yaml`, `trading-dashboard/build.sh`).
- Local multi-agent system is functional for analysis/backtest/pinescript generation and dashboard chat integration, but:
  - Hermes integration is **present but operationally sensitive** (WSL/SSH path and auth).
  - Live execution supports Binance/Alpaca/OANDA; **Upstox is stubbed**.
  - Some workflows depend on the cloud dashboard being reachable; connectivity errors can degrade user experience.

### Intended Production Scale (INFERRED)
This system is built for a single operator (you) and a single dashboard instance, with the ability to add more symbols/strategies and more agents. It is not (yet) designed for multi-tenant use, high-frequency trading, or regulated execution with exchange-grade compliance.

---

## 2. COMPLETE TECH STACK ANALYSIS

This section lists technologies found in the repositories and what they do here.

### Frontend (Cloud Dashboard)
- **React 18 + TypeScript + Vite** (VERIFIED: `trading-dashboard/frontend`)
  - Purpose: SPA dashboard UI.
  - Advantages: fast dev + strong TS typing.
  - Disadvantages: needs build pipeline; deployed as static `dist/`.
  - Integration: fetch calls to backend endpoints; websocket for agent monitor.
- **Tailwind CSS** (VERIFIED by code usage)
  - Purpose: consistent dark theme and layout.
  - Impact: fast iteration; relies on build tooling for CSS.
- **Recharts** (VERIFIED by components e.g. `BacktestingPage.tsx`, `StrategiesPage.tsx`)
  - Purpose: charts for equity curves and metrics.
  - Tradeoffs: client-side rendering and potential perf issues for huge series.

### Cloud Backend (Dashboard)
- **FastAPI** (VERIFIED: `trading-dashboard/backend/main.py`)
  - Purpose: API endpoints, websocket endpoint, serving static frontend.
  - Integration: receives agent status updates; stores chat commands; serves watchlist/signals; provides mocks for trading pages.
- **WebSockets** (VERIFIED: `/ws/agent-monitor`)
  - Purpose: real-time agent monitor updates in UI.
  - Impact: simple push-based state; needs connection handling.
- **SQLAlchemy** (VERIFIED: `trading-dashboard/backend/database.py`)
  - Purpose: DB models and persistence for watchlist + signals + alerts + strategies + etc.
  - Deployment: SQLite in dev; Postgres supported via `DATABASE_URL` fix.

### Local Agent System (Trading OS)
- **FastAPI** (VERIFIED: `main.py` / `api/*`)
  - Purpose: local API for orders/backtests/risk snapshot + telegram webhook.
  - Note: this is separate from cloud dashboard backend.
- **asyncio** (VERIFIED across agents and event bus)
  - Purpose: concurrency and background loops.
- **aiohttp** (VERIFIED dependency, used in broker adapters and telegram send)
  - Purpose: async HTTP calls.
- **yfinance** (VERIFIED: skills/agents)
  - Purpose: market data and news fallback.
  - Risk: rate limits, occasional MultiIndex column shapes.
- **pandas** (VERIFIED: `skills/technical_analysis_skill.py`)
  - Purpose: indicator computation.
- **ccxt (async_support)** (VERIFIED: `execution/broker_router.py`)
  - Purpose: Binance live execution via exchange API.
  - Tradeoffs: heavy dependency; needs API keys; error-prone; network sensitive.
- **Ollama (local LLM)** (VERIFIED by env + code: `boss_agent.py` and `skills/pinescript_strategy_generator.py`)
  - Purpose: reasoning / text generation tasks.
  - Integration: HTTP calls to `OLLAMA_URL`.
  - Operational impact: needs ollama server running; can be slow on low RAM.
- **Hermes Agent** (VERIFIED integration wrapper: `integrations/hermes_client.py`)
  - Purpose: additional reasoning + self-learning copilot.
  - Integration: via CLI shellout (WSL or SSH).
  - Operational risk: PATH issues, WSL/SSH configuration, non-interactive environment.

### Databases / Storage (Local)
- **SQLite** (VERIFIED usage in `memory/trade_memory.py`, `memory/reflexion_memory.py`, persistent live approval DB)
  - Purpose: persistent storage of:
    - trade execution audit trail
    - reflexion/lessons
    - approval tickets (to share between processes)
- **VectorMemory (in-memory)** (VERIFIED: `memory/vector_memory.py`)
  - Purpose: local vector storage; likely lightweight embeddings placeholder.
  - Status: present; embeddings pipeline not fully defined in this session.

### Deployment
- **Render** (VERIFIED: `trading-dashboard/render.yaml`, `build.sh`)
  - Purpose: cloud hosting of dashboard.
  - Integration: GitHub auto-deploy.
  - Known fragility: runtime environment selection (node vs python) and frontend build.

---

## 3. COMPLETE AI SYSTEM REVERSE ENGINEERING (The “Brain”)

This is a multi-agent *workflow system*, not a single monolithic agent. Reasoning is split across:

- Boss orchestration logic
- Specialist agents returning structured results
- Optional LLM/Hermes summarization and iterative tuning
- Risk/Execution gates that prevent unsafe actions

### VERIFIED IMPLEMENTATION: Core Reasoning Flow
In local system `agents/boss_agent.py`, the Boss agent:
1. Receives a user command (polled from cloud dashboard).
2. Parses intent via `skills/chatbot_command_parser.py`:
   - regex-based parsing
   - intents: analyze, backtest, place_order, whale_activity, current_risk, approve_live, unknown
3. Resolves symbol phrases via `skills/symbol_resolver.py`.
4. Builds a “plan” (a dict returned to caller; not a formal planning framework).
5. Delegates to specialist agents for data:
   - TechnicalAnalysisAgent (calls TechnicalAnalysisSkill; yfinance indicators)
   - NewsSentimentAgent (calls NewsIntelligenceSkill; NewsAPI or yfinance)
   - MacroIntelligenceAgent (yfinance macro tickers)
   - WhaleIntelligenceAgent (calls WhaleTrackerSkill)
6. Performs basic sanity checks (VERIFIED in code via fallback behavior and type conversions).
7. Calls AnalysisAgent to turn the data bundle into a report (Hermes-assisted if Hermes works; otherwise local fallback behavior depends on agent code).
8. Stores “reflexion entry” in local SQLite for future reuse (`memory/reflexion_memory.py`).
9. Sends response back to cloud dashboard via `/chat/submit-response`.

### Verified LLM / Model Routing
- BossAgent includes an `OllamaClient` class that calls:
  - `POST {OLLAMA_URL}/api/generate` with `{model, prompt, stream:false}`
  - fallback model if primary fails
- PineScript generation uses `skills/pinescript_strategy_generator.py` which implements a router (`MultiModelRouter`) reading `config/settings.py` model routing settings.

### Hallucination Reduction / Validation (PARTIAL)
There is no dedicated “truth enforcement” framework. Instead:
- Data is fetched from APIs and structured into dicts.
- Some type coercions and shape normalization exist (e.g. yfinance MultiIndex close series conversion in `technical_analysis_skill.py` and macro agent).
- Execution path is validated by strict model validators (`pydantic` in `config/models.py`).
- RiskGuardian imposes mandatory stop loss and exposure constraints.

### Retry Logic / Failure Handling (VERIFIED)
Multiple layers:
- BrokerRouter has a retry policy and backoff.
- Agents wrap loops in try/except and post error status.
- HermesClient returns sentinel strings on timeout/errors.
- NewsAPI calls now have a short timeout + fallback.

### Context Building / Memory Use (PARTIAL)
- BossAgent stores reflexion entries after analyze/backtest.
- There is no verified retrieval/ranking pipeline used for every command (some repos exist but not confirmed integrated into Boss flow beyond “store entry”).

---

## 4. COMPLETE MULTI-AGENT SYSTEM ANALYSIS

### VERIFIED AGENT LIST (Local)
Location: `agents/`

- `BossAgent` (`agents/boss_agent.py`)
- `TechnicalAnalysisAgent` (`agents/technical_agent.py`)
- `NewsSentimentAgent` (`agents/news_agent.py`)
- `MacroIntelligenceAgent` (`agents/macro_agent.py`)
- `WhaleIntelligenceAgent` (`agents/whale_agent.py`)
- `PineScriptGenerationAgent` (`agents/pinescript_agent.py`)
- `AnalysisAgent` (`agents/analysis_agent.py`)
- `BacktestingAgent` (`agents/backtesting_agent.py`)
- `HermesAdvisorAgent` (`agents/hermes_advisor_agent.py`)
- `ReflexionAgent` (`agents/reflexion_agent.py`) (present, not deeply analyzed here)
- `RiskGuardian` (`agents/risk_guardian.py`) (acts as a “policy agent”)
- `WatchlistExecutor` (`agents/watchlist_executor.py`)
- `TradeExecutionAgent` (`agents/trade_execution_agent.py`)
- `orchestration_runner.py` (runs multiple agents concurrently in one process; used for dev)

#### BossAgent
- Role: Orchestrator / planner / validator / persistence.
- Inputs: chat commands (cloud dashboard queue).
- Outputs: response text to dashboard, reflexion entries, approvals for live tickets.
- Tools:
  - HTTP polling/posting to dashboard endpoints
  - calls to other local agents (method calls)
  - HermesClient + OllamaClient
  - SQLite reflexion repository
- Lifecycle: infinite poll loop in `__main__`.

#### TechnicalAnalysisAgent
- Role: compute indicators and signal bias.
- Depends on `TechnicalAnalysisSkill` which fetches OHLCV via yfinance and computes EMA/RSI.
- Output: dict with trend, rsi, price close, signal, etc.

#### NewsSentimentAgent
- Role: fetch news + compute lexicon sentiment.
- Depends on `NewsIntelligenceSkill`.
- News sources:
  - NewsAPI if `NEWSAPI_KEY` set (short timeout)
  - fallback to yfinance ticker news

#### MacroIntelligenceAgent
- Role: periodic macro indicator monitor using yfinance tickers (DXY, VIX, etc).
- Output: series last values and alerts on large moves.

#### WhaleIntelligenceAgent
- Role: whale activity summary via `WhaleTrackerSkill` (exact data source depends on skill).

#### PineScriptGenerationAgent
- Role: generate PineScript strategies via LLM router and run validations.
- Known historical failure: calling nonexistent coder models; corrected by routing to installed models.

#### AnalysisAgent
- Role: produce final “analysis report” from a structured bundle.
- Uses HermesClient (if available) for improved reasoning.
- Output: report text + derived signal summary.

#### BacktestingAgent
- Role: run backtest and optionally do Hermes-guided tuning loop.
- Success/failure thresholds implemented in tuning spec:
  - success >= +5% return
  - failure <= -2% return
  - max rounds set in spec

#### HermesAdvisorAgent
- Role: monitors pending signals and asks Hermes for advice (stored locally).
- Status: present; effectiveness depends on Hermes connectivity.

#### WatchlistExecutor
- Role: polls cloud watchlist, runs research checks, posts buy-signal alerts to dashboard with cooldown.

#### TradeExecutionAgent
- Role: polls cloud for APPROVED signals, computes quantity caps, tick rounding, brokerage estimate, uses RiskGuardian pre-check, requests live approval ticket, executes via ExecutionEngine, marks executed in cloud.
- Production safety:
  - live requires ticket approval (PersistentLiveApprovalManager shared DB)
  - risk veto before approval request

### Agent Hierarchy (VERIFIED)
- BossAgent is top-level orchestrator for user commands.
- Specialist agents are subordinate and stateless (compute & return).
- Execution agents form a separate loop (watchlist + approved signals).

### Communication Channels (VERIFIED)
- Cloud Dashboard ⟷ Local BossAgent:
  - `/chat` command store (cloud)
  - Boss polls `/chat/pending-commands`
  - Boss posts to `/chat/submit-response`
- Local agents → Cloud dashboard:
  - `/agent-status` (agent state heartbeats)
  - `/alerts/buy-signal` for buy alerts (with cooldown)
- Cloud UI gets agent status via websocket `/ws/agent-monitor`.

---

## 5. COMPLETE MEMORY SYSTEM ANALYSIS

### VERIFIED COMPONENTS
Location: `memory/`

- `global_state.py`:
  - in-memory portfolio state for paper/live snapshots
  - used by RiskGuardian and ExecutionEngine
- `trade_memory.py`:
  - SQLite persistence for execution audit trail
- `reflexion_memory.py`:
  - SQLite persistence for “lessons” / analysis/backtest outputs
- `vector_memory.py`:
  - in-memory vector store placeholder (dimension set in `main.py` to 128)

### PersistentLiveApproval (VERIFIED)
Location: `execution/persistent_live_approval.py`
- SQLite table `live_approval_tickets`
- Purpose: share approvals across separate Python processes (BossAgent approving a ticket created by TradeExecutionAgent).
- Why: in-memory approvals cannot be shared across processes.

### Retrieval / RAG (PARTIAL / MISSING)
- No verified embedding model or retrieval ranking pipeline is present in this session.
- VectorMemory exists but it is not proven to be used for retrieval in BossAgent flows.
- Impact: memory acts mostly as persistence/logging, not active retrieval augmented generation.

---

## 6. COMPLETE PROMPT ENGINEERING ANALYSIS

### VERIFIED PROMPTS / Templates
Prompts exist primarily inside:
- `skills/pinescript_strategy_generator.py` (LLM prompts for generating code and validation loops)
- `agents/analysis_agent.py` (likely constructs analysis prompts)
- `agents/backtesting_agent.py` (Hermes-guided tuning prompt)

### MISSING IMPLEMENTATION: Centralized Prompt Registry
There is no single “prompt catalog” file; prompts are embedded in skills/agents.
Impact: harder to audit and standardize.

### Instruction Hierarchy (VERIFIED)
- Code-level intent parsing via regex is the first “prompt” layer.
- LLM is used only after data collection, not as primary data fetcher.

---

## 7. COMPLETE FRONTEND REVERSE ENGINEERING (Cloud Dashboard)

### VERIFIED
Location: `trading-dashboard/frontend/src/components`

Key components:
- `ChatInterface.tsx`:
  - POST `/chat` then polls `/chat/response/{command_id}`
  - has a 240*0.5s = 120s polling window and returns “Agent timed out…” otherwise
- `AgentMonitor.tsx` + websocket:
  - real-time agent status display
- Pages:
  - `TradingPage.tsx`
  - `StrategiesPage.tsx`
  - `BacktestingPage.tsx`
  - `StockScreener.tsx`
  - `SettingsPage.tsx`
  - `WatchlistPage.tsx`
  - `SignalsPage.tsx`
  - `PortfolioPage.tsx`
  - `OverviewPage.tsx`
  - `AgentAnimation.tsx`
- `ErrorBoundary.tsx`

### Data Lifecycle (VERIFIED)
- Uses fetch against same-origin endpoints; `API_URL` is empty string → same domain.
- Websocket used for agent monitor.

### Missing / Partial
- Authentication in cloud dashboard is not enforced for user UI endpoints.
- Settings keys are stored server-side in `settings_store` dict and (partially) env; not a secure secrets vault.

---

## 8. COMPLETE BACKEND REVERSE ENGINEERING

### Cloud Dashboard Backend (VERIFIED)
Location: `trading-dashboard/backend/main.py`
Capabilities:
- health: `/health`
- agent status ingestion: `/agent-status`, `/api/agent-status`
- websocket broadcast: `/ws/agent-monitor`
- chat command queue:
  - `/chat` (stores command, returns command_id)
  - `/chat/pending-commands` (agents poll)
  - `/chat/submit-response`
  - `/chat/response/{command_id}`
- trading mocks:
  - `/positions`, `/trade`, `/order-history`
- strategies:
  - `/strategies`, `/strategy/create`, `/strategy/{id}/metrics`, `/strategy/pinescript/generate`
- backtest: `/backtest`
- screener: `/screener`
- settings endpoints: `/settings`, `/settings/keys`, `/settings/mode`, `/settings/risk`, `/settings/ollama`
- watchlist DB-backed endpoints:
  - `/api/watchlist`, `/api/watchlist/add`, `/api/watchlist/remove`
  - aliases `/watchlist` etc.
- signals endpoints:
  - `/api/signals/pending`
  - `/api/signals` (filter by approval_status)
  - `/api/signals/approved`
  - `/api/signal/approve`
  - `/api/signal/skip`
  - `/api/signal/mark-executed`
  - aliases `/signals/approved`, etc.
- static hosting:
  - mounts `frontend/dist` at `/` if exists

Cloud DB models: `trading-dashboard/backend/database.py`
Includes tables:
- AgentState, Strategy, BacktestResult, Trade, ApiKey, ChatHistory, ScreenerResult, Settings
- WatchlistStock, TradeSignal, WatchlistAlert

### Local Trading OS Backend (VERIFIED)
Location: root `main.py` (FastAPI factory) + `api/*`
Routers:
- `/api/*` dashboard control plane (`api/dashboard_api.py`)
- `/telegram/*` webhook and command endpoint (`api/telegram_api.py`)
- websocket router (`api/websocket_server.py`)
Middleware:
- rate limit (`api/security.py`: `RateLimitMiddleware`)
- API key guard (`ApiKeyGuard`)

---

## 9. COMPLETE EXECUTION FLOW ANALYSIS

### A) Chat/Analysis Flow (VERIFIED)
User → Cloud UI → Cloud backend → Local Boss → Specialists → AnalysisAgent → Cloud UI

1. User types in cloud Chat UI.
2. Frontend POST `/chat`.
3. Cloud backend stores pending command id in `pending_commands`.
4. Local BossAgent polls `/chat/pending-commands`.
5. Boss parses intent + symbol.
6. Boss calls technical/news/macro/whale as needed.
7. Boss calls AnalysisAgent for report.
8. Boss stores reflexion entry.
9. Boss POST `/chat/submit-response`.
10. Frontend polls `/chat/response/{command_id}` until done.

### B) Watchlist Signal Flow (VERIFIED)
Cloud watchlist DB → WatchlistExecutor polls → posts `/alerts/buy-signal` (cooldown) → Cloud stores signal/alert

### C) Approved Signal Execution Flow (VERIFIED)
Cloud approved signals → TradeExecutionAgent polls → risk check → live ticket request → human approval → execute → mark executed

Key enforcement points:
- RiskGuardian veto.
- PersistentLiveApprovalManager ticket: approve + consume.
- ExecutionEngine mode isolation.

---

## 10. COMPLETE FILE STRUCTURE

### VERIFIED TOP-LEVEL TREE (selected)
Root: `...\trading_system\`

- `agents/` local multi-agent processes
- `api/` local FastAPI routers (dashboard, telegram, websocket, security)
- `config/` settings + models + broker configs
- `events/` async event bus + event contracts + handlers
- `execution/` execution engine + broker routing + approvals + kill switch
- `integrations/` Hermes CLI bridge
- `memory/` state + sqlite repositories + vector memory
- `skills/` indicator/news/backtest/pinescript utilities
- `tools/` helper scripts (Hermes bridge test)
- `trading-dashboard/` cloud dashboard repo (React + FastAPI + SQLAlchemy + Render configs)

### NOTE
There is also a `trading_system/` directory under root with many files (VERIFIED by listing). This appears to be a Python package directory (possibly a nested package). This document focuses on the code paths actually referenced/imported by entrypoints inspected in this session. If you want a full audit of that nested folder too, run a deeper tree extraction and we will extend this doc.

---

## 11. COMPLETE DATABASE & STORAGE ANALYSIS

### Cloud dashboard DB (VERIFIED)
SQLAlchemy models in `trading-dashboard/backend/database.py`.
Supports SQLite by default, Postgres on Render via `DATABASE_URL`.
Watchlist + signals used by local agents.

### Local DB (VERIFIED)
SQLite file path is configured by `TRADING_LOCAL_SQLITE_PATH` or defaults:
- `...\trading_system\data\trading_system.db` (reflexion/trade memories)
- `...\trading_system\data\live_approvals.db` (approval tickets)

Schema details are implemented directly in repository code and not centralized into migrations.

### MISSING IMPLEMENTATION
- No Alembic migrations for schema evolution.
- No encryption-at-rest for local DBs.

---

## 12. COMPLETE TOOL ECOSYSTEM ANALYSIS

### External APIs / Tools (VERIFIED)
- Ollama HTTP API: `{OLLAMA_URL}/api/generate`
- NewsAPI HTTP API: `https://newsapi.org/v2/everything` (if key configured)
- Telegram Bot API: `https://api.telegram.org/bot<TOKEN>/sendMessage`
- Binance: via CCXT (async)
- Alpaca: REST API (paper/live URLs)
- OANDA: REST API adapter exists
- yfinance: market data & news

### Local Tools (VERIFIED)
- `start_all_agents.bat`: starts each agent and logs stdout/stderr to `logs/*.log`
- `tools/test_hermes_bridge.ps1`: validates Hermes connectivity via `HERMES_CMD` or SSH

### Tool selection logic (VERIFIED)
- HermesClient chooses:
  - explicit `HERMES_CMD` if set
  - else SSH if `HERMES_SSH_HOST`
  - else local hermes / WSL

---

## 13. COMPLETE DEVELOPMENT HISTORY (Reconstructed)

### VERIFIED FROM CHANGES + FILES
- Initial system had a deployed dashboard stub and only boss_agent running.
- Major issues existed:
  - import/path failures across local agents
  - chat integration incomplete
  - missing dashboard pages
  - circular imports / missing exports
  - PineScript generator defaulted to non-installed models
- Changes applied during this Codex session included:
  - adding missing endpoints to cloud backend (`/api/signals`, `/api/signals/approved`, mark executed)
  - adding DB-backed watchlist/signals on cloud
  - adding local orchestration architecture (Boss delegates and stores results)
  - adding persistent approval tickets shared across processes
  - adding TradeExecutionAgent
  - improving `start_all_agents.bat` to log per agent and prefer venv python
  - hardening NewsAPI with timeout + fallback
  - Render deploy stability: python env, optional frontend build, robust imports
  - Hermes integration hardening (HERMES_CMD path issues; WSL path usage)

### INFERRED
- Some older scripts/files exist (`backend.py`, `run_trading_stack.ps1`) suggesting earlier experiments.

---

## 14. COMPLETE SECURITY ANALYSIS

### VERIFIED IMPLEMENTATION
- Local API includes:
  - API key guard (`x-api-key`) optional but supported.
  - rate limit middleware.
  - Telegram webhook secret token validation.
- Execution safety:
  - RiskGuardian mandatory stop loss, exposure limits.
  - KillSwitch can stop execution paths.
  - Live approvals must match order fingerprint and are one-time consumable.

### RISKS / PARTIAL
- Cloud dashboard stores settings in-memory (`settings_store`) and may accept keys via `/settings/keys`.
  - This is not a secure secret management design.
- No user authentication on cloud dashboard endpoints (open CORS).
- Hermes CLI execution could be a security risk if prompts can trigger tool hooks; mitigated by `HERMES_ACCEPT_HOOKS=true` design but still needs careful policy.

---

## 15. COMPLETE PERFORMANCE ANALYSIS

### Verified optimizations
- Async concurrency used in event bus and some research fetches.
- BrokerRouter retries with exponential backoff.
- NewsAPI has a short timeout to prevent blocking.
- Chat UI polls with backoff (500ms loop).

### Bottlenecks / Risks
- Ollama on low RAM: high latency; requires timeout tuning.
- yfinance/NewsAPI: network flakiness.
- Cloud dashboard chat uses polling not websocket streaming.

---

## 16. COMPLETE DEPLOYMENT & INFRASTRUCTURE ANALYSIS

### Cloud dashboard (VERIFIED)
- Deployed on Render via repo `my-trading-dashboard`.
- `render.yaml` declares a single web service.
- `build.sh` installs deps and optionally builds frontend (depends on npm presence).
- Static assets are served from `frontend/dist` by FastAPI.

### Local agents (VERIFIED)
- Run via Windows PowerShell `.\start_all_agents.bat`.
- Hermes currently expected via WSL path (as configured by `HERMES_CMD`).

---

## 17. COMPLETE CURRENT STATE ANALYSIS

### Fully working (VERIFIED / LIKELY)
- Cloud dashboard endpoints and UI pages exist.
- Local agents run in loops and post agent statuses.
- PineScript generator works when using installed Ollama models.
- RiskGuardian + ExecutionEngine + paper execution pipeline.

### Partially working
- Hermes: integrated but requires correct WSL/SSH configuration and PATH.
- Live execution:
  - Binance/Alpaca/OANDA adapters exist.
  - Local Upstox adapter is **stubbed** (cannot execute real trades from the local OS).
  - Cloud dashboard includes an **optional** async Upstox REST client (`trading-dashboard/backend/brokers/upstox_broker.py`),
    gated behind `ENABLE_LIVE_BROKER=true` and `UPSTOX_ACCESS_TOKEN` (not recommended for live trading due to cloud secrets).

### Broken / Missing
- Full broker-based “real data” ingestion for Indian equities via Upstox is missing.
- A full strategy engine + database schema described in user prompt is not fully implemented as a cohesive module in local trading OS (cloud has partial watchlist/signals storage).

---

### 2026-05-27 Addendum: Cloud Dashboard Phase A Foundation (VERIFIED)
These items were implemented inside `trading-dashboard/` and deployed to Render.

Backend modules added (VERIFIED on disk):
- `trading-dashboard/backend/brokerage/charges_engine.py`: Charges estimate + profitability ratio threshold (default 3.0x).
- `trading-dashboard/backend/risk/capital_allocator.py`: position sizing with reserve + risk-per-trade caps.
- `trading-dashboard/backend/config/trading_config.py`: kill switch defaults (env + runtime flag).
- `trading-dashboard/backend/execution/order_deduplication.py`: client-side idempotency helper (in-memory).
- `trading-dashboard/backend/core/event_store.py`: persistent audit event store in the same DB URL as the dashboard.
- `trading-dashboard/backend/market_data/symbol_master_service.py`: Upstox instruments cache (separate sqlite file).
- `trading-dashboard/backend/brokers/upstox_broker.py`: async httpx client for Upstox REST.
- `trading-dashboard/backend/security/jwt_auth.py`: minimal HS256 JWT (optional; enabled only if `JWT_SECRET_KEY` is set).

Backend wiring changes (VERIFIED in `trading-dashboard/backend/main.py`):
- `/trade` now enforces:
  - kill switch (DB setting key `TRADING_ENABLED`),
  - capital allocator sizing (feature flag `ENFORCE_CAPITAL_ALLOCATOR`, default true),
  - charges profitability filter (flag `ENFORCE_CHARGES_FILTER`, default true; buy-side uses take-profit as expected exit),
  - persistent idempotency (`IdempotencyKey` table; `client_order_id`).
- Added endpoints:
  - `GET /api/kill-switch`, `POST /api/kill-switch` (admin gate: JWT admin or `X-Admin-Key` matching `ADMIN_API_KEY`).
  - `POST /api/calculate-charges`
  - `GET /api/events`
  - `POST /api/symbol-master/refresh`, `GET /api/symbol-master/search`
  - `GET /api/broker/upstox/status`, `GET /api/broker/upstox/profile`, `GET /api/broker/upstox/funds`

Cloud DB schema changes (VERIFIED in `trading-dashboard/backend/database.py`):
- Added: `IdempotencyKey`, `Position` models.
- `init_db()` boot-safety: tolerates SQLite "index already exists" to avoid deploy failures due to index drift.

Render deployment stabilization (VERIFIED):
- Python version pinned to 3.11.11 via `.python-version` and `render.yaml` env var `PYTHON_VERSION`.
- Startup fixes:
  - `EventStore` and `UpstoxBroker` declare fields required by `@dataclass(slots=True)`.

Frontend Kill Switch visibility (VERIFIED):
- Source UI exists in `trading-dashboard/frontend/src/components/SettingsPage.tsx`.
- A production hotfix injector exists in `trading-dashboard/frontend/dist/index.html` that inserts the Kill Switch section
  at runtime even if the TS bundle isn't rebuilt (workaround for deploys that only run Python build steps).

## 18. COMPLETE REBUILD GUIDE (From Scratch)

VERIFIED high-level rebuild steps:
1. Deploy cloud dashboard:
   - Use `trading-dashboard/` repo.
   - Ensure Render service runs Python and serves `frontend/dist`.
2. Run local agents:
   - Install Python deps (local requirements).
   - Start Ollama server.
   - Configure `.env` (DASHBOARD_URL, OLLAMA_URL, keys).
   - Run `.\start_all_agents.bat`.
3. Verify:
   - Dashboard shows agent statuses.
   - Chat commands are processed and responses appear.
   - Watchlist executor posts buy signals.
   - Approve signals in dashboard, trade_execution_agent requests approvals and (paper/live) executes.

For a truly clean rebuild, add:
- Alembic migrations
- secret vault for cloud dashboard keys
- integration tests for chat + signals + execution pipeline

---

## 19. COMPLETE ARCHITECTURE DIAGRAMS

### AI + Orchestration (VERIFIED)
```mermaid
flowchart TD
  U["User (Dashboard Chat)"] -->|POST /chat| CB["Cloud Backend (FastAPI)"]
  CB -->|GET /chat/pending-commands| BA["BossAgent (local)"]
  BA --> TA["TechnicalAgent"]
  BA --> NA["NewsAgent"]
  BA --> MA["MacroAgent"]
  BA --> WA["WhaleAgent"]
  TA --> BA
  NA --> BA
  MA --> BA
  WA --> BA
  BA --> AA["AnalysisAgent (Hermes/Ollama)"]
  AA --> BA
  BA -->|POST /chat/submit-response| CB
  CB -->|GET /chat/response| U
```

### Signal → Approval → Execution (VERIFIED)
```mermaid
flowchart TD
  WL["Cloud Watchlist DB"] --> WE["WatchlistExecutor (local loop)"]
  WE -->|POST /alerts/buy-signal| CB["Cloud Backend"]
  CB --> SIGDB["Cloud TradeSignal (approved/pending)"]
  SIGDB -->|approve in dashboard| SIGOK["approved"]
  SIGOK --> TE["TradeExecutionAgent (local loop)"]
  TE --> RG["RiskGuardian (veto)"]
  RG -->|approved| LAM["PersistentLiveApprovalManager (SQLite)"]
  LAM -->|ticket id| HUMAN["Human approves: 'approve LIVEAP-...'"]
  HUMAN --> BA["BossAgent approves ticket"]
  TE --> EE["ExecutionEngine"]
  EE --> BR["BrokerRouter (binance/alpaca/oanda/upstox stub)"]
  TE -->|POST /api/signal/mark-executed| CB
```

### Cloud Dashboard (VERIFIED)
```mermaid
flowchart LR
  FE["React Frontend (Vite build)"] <--> BE["FastAPI Backend"]
  BE <--> DB["SQLite/Postgres (SQLAlchemy)"]
  Agents["Local Agents"] -->|POST /agent-status| BE
  BE -->|WS /ws/agent-monitor| FE
```

---

## 20. FINAL SYSTEM INTELLIGENCE SUMMARY

### Capabilities (VERIFIED)
- Cloud dashboard UI for:
  - chat, monitoring, trading pages, strategies/backtests/screener/settings
- Local agent orchestration:
  - analysis and backtesting flows coordinated by BossAgent
- Risk-first execution system with:
  - mandatory stop loss
  - kill switch
  - ticket-based live approvals
- PineScript strategy generation assisted by local LLM routing.

### Limitations (VERIFIED)
- Upstox live trading is not implemented (stub adapter).
- Hermes integration works only when WSL/SSH invocation is correct and non-interactive.
- Memory is persistence-first; not a fully developed retrieval + RAG system.
- Cloud secrets handling is not hardened; CORS is open.

---

## 21. TRUTH ENFORCEMENT & FALLBACK DETECTION

### MISSING IMPLEMENTATION: Full “strategy engine” described in user prompt
Requested: DB-stored buy/sell conditions, scoring, telegram approval buttons, broker execution integration.
Implemented instead:
- Cloud DB has watchlist + trade_signals tables, approval status changes.
- Local TradeExecutionAgent polls “approved” signals and executes.
Impact:
- Strategy logic is not fully modeled as first-class DB-driven rules in local system.
- Scaling strategy definitions requires new modules and DB schema/migrations.

### MISSING IMPLEMENTATION: Upstox live execution
Implemented instead:
- `UpstoxAdapter` exists but returns `not_implemented`.
Impact:
- Indian equities execution cannot go live until OAuth + order endpoints are implemented.

### PARTIAL IMPLEMENTATION: Hermes “self-learning”
Implemented:
- HermesClient CLI bridge; AnalysisAgent/BacktestingAgent can call it.
Not implemented:
- A robust, always-on Hermes MCP server integration or toolhook policy enforcement.
Impact:
- Operational fragility; requires environment correctness.

--- END FILE: ULTRA_MASTER_SYSTEM_CONTEXT.md ---

--- START FILE: __init__.py ---

--- END FILE: __init__.py ---

--- START FILE: agents\analysis_agent.py ---
"""Analysis agent: turns real market data + other agent outputs into an explanation."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from trading_system.integrations.hermes_client import HermesClient

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class AnalysisBundle:
    symbol: str
    timeframe: str
    market_data: Dict[str, Any]
    technical: Dict[str, Any]
    news: Dict[str, Any]
    macro: Optional[Dict[str, Any]] = None


class AnalysisAgent:
    """Compose an analysis narrative with Hermes support."""

    def __init__(self, hermes: Optional[HermesClient] = None) -> None:
        self.hermes = hermes or HermesClient()

    async def analyze(self, bundle: AnalysisBundle) -> Dict[str, Any]:
        # Minimal structured output; boss agent formats for user.
        sentiment = (bundle.news.get("sentiment") or {}).get("label", "unknown")
        tech_signal = bundle.technical.get("signal", "hold")
        trend = bundle.technical.get("trend", "unknown")
        price = float(bundle.market_data.get("price") or 0.0)

        prompt = (
            "You are a trading analyst. Given the data, write a concise report with:\n"
            "1) Trend + technical signal\n"
            "2) News sentiment\n"
            "3) Key levels / risks\n"
            "4) A one-line plan (entry/stop/targets) for paper trading only\n\n"
            f"Symbol: {bundle.symbol}\n"
            f"Timeframe: {bundle.timeframe}\n"
            f"Price: {price}\n"
            f"Technical: {bundle.technical}\n"
            f"News: {bundle.news}\n"
            f"Macro: {bundle.macro or {}}\n"
        )
        # Hermes is a helper; if unavailable, fall back to a deterministic summary.
        text = await _maybe_to_thread(self.hermes.query, prompt)
        if not text or text.startswith("HERMES_"):
            text = (
                f"{bundle.symbol} ({bundle.timeframe}) price={price:.2f}\n"
                f"trend={trend} signal={tech_signal}\n"
                f"news_sentiment={sentiment}\n"
                "Note: Hermes unavailable; this is a minimal summary."
            )

        return {
            "symbol": bundle.symbol,
            "timeframe": bundle.timeframe,
            "price": price,
            "trend": trend,
            "signal": tech_signal,
            "news_sentiment": sentiment,
            "report": text,
        }


async def _maybe_to_thread(fn, *args):
    import asyncio

    return await asyncio.to_thread(fn, *args)


--- END FILE: agents\analysis_agent.py ---

--- START FILE: agents\backtesting_agent.py ---
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


--- END FILE: agents\backtesting_agent.py ---

--- START FILE: agents\boss_agent.py ---
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
from typing import Any, Dict, Optional

from dotenv import load_dotenv

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
from trading_system.config.models import CommandIntent, CommandIntentType, OrderRequest, TradingMode
from trading_system.execution.persistent_live_approval import PersistentLiveApprovalManager
from trading_system.integrations.hermes_client import HermesClient
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
    """Orchestrator agent used by both dashboard polling loop and API server."""

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
    ) -> None:
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

        # Hermes preflight: log once so production ops can see if the SSH bridge is working.
        ok, info = self.hermes.healthcheck()
        if ok:
            logger.info("Hermes connected: %s", info)
        else:
            logger.warning("Hermes unavailable (will fall back to Ollama/local logic): %s", info)

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

--- END FILE: agents\boss_agent.py ---

--- START FILE: agents\hermes_advisor_agent.py ---
"""Hermes advisor agent.

Uses Hermes Agent (installed in Ubuntu/WSL) to produce self-learning notes that
help improve strategy rules over time.

Workflow:
1) Poll cloud dashboard for pending signals.
2) Ask Hermes for a short "lesson" + suggested rule improvements.
3) Store the lesson in ReflexionMemory (SQLite) so other agents can retrieve it.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Set

from dotenv import load_dotenv

# Ensure `import trading_system.*` works no matter where we launch from.
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

from trading_system.integrations.hermes_client import HermesClient
from trading_system.memory.reflexion_memory import ReflexionEntry, ReflexionMemoryRepository

DASHBOARD_URL = os.getenv("DASHBOARD_URL", "https://my-trading-dashboard-8.onrender.com").rstrip("/")
POLL_SECONDS = int(os.getenv("HERMES_POLL_INTERVAL", "30"))
DB_PATH = os.getenv("TRADING_LOCAL_SQLITE_PATH", str((_PKG_DIR / "data" / "trading_system.db").resolve()))


def _safe_json(resp: urllib.response.addinfourl) -> Any:
    body = resp.read().decode("utf-8")
    return json.loads(body) if body else {}


def _get_json(url: str, timeout: int = 15) -> Any:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return _safe_json(resp)


def _post_json(url: str, payload: dict, timeout: int = 15) -> Any:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return _safe_json(resp)


def post_status(status: str, task: str = "", progress: int = 0) -> None:
    payload = {
        "agent_id": "hermes_advisor",
        "status": status,
        "task": task,
        "progress": progress,
        "timestamp": datetime.now().isoformat(),
    }
    try:
        _post_json(f"{DASHBOARD_URL}/agent-status", payload, timeout=10)
    except Exception:
        pass


def _prompt_for_signal(signal: Dict[str, Any]) -> str:
    symbol = str(signal.get("symbol") or "UNKNOWN")
    price = float(signal.get("signal_price") or 0.0)
    tech = float(signal.get("technical_score") or 0.0)
    news = float(signal.get("news_score") or 0.0)
    fund = float(signal.get("fundamental_score") or 0.0)
    risk = float(signal.get("risk_score") or 0.0)
    overall = float(signal.get("overall_score") or 0.0)
    strategy_id = str(signal.get("strategy_id") or "default")
    return (
        "You are a trading assistant helping improve a rule-based strategy.\n"
        "Given this pending BUY signal, produce:\n"
        "1) Decision: APPROVE or SKIP\n"
        "2) 3 bullet reasons\n"
        "3) A short 'lesson learned' sentence to improve future signals\n"
        "4) Suggested rule tweaks (as plain text, not code)\n\n"
        f"Symbol: {symbol}\n"
        f"Strategy: {strategy_id}\n"
        f"Price: {price}\n"
        f"Scores (0-100): technical={tech}, news={news}, fundamentals={fund}, risk={risk}, overall={overall}\n\n"
        "Keep it concise."
    )


class HermesAdvisorAgent:
    def __init__(self, hermes: HermesClient, repo: ReflexionMemoryRepository) -> None:
        self.hermes = hermes
        self.repo = repo
        self.seen: Set[str] = set()

    async def run_once(self) -> Optional[Dict[str, Any]]:
        signals = _get_json(f"{DASHBOARD_URL}/api/signals/pending", timeout=20) or []
        if not isinstance(signals, list) or not signals:
            return None

        # Only process one per cycle to keep CPU/network low.
        signal = signals[0]
        sid = str(signal.get("id") or "")
        if not sid or sid in self.seen:
            return None

        prompt = _prompt_for_signal(signal)
        answer = await asyncio.to_thread(self.hermes.query, prompt)
        if not answer or answer.startswith("HERMES_ERROR") or answer == "HERMES_TIMEOUT":
            raise RuntimeError(answer or "Hermes returned empty response")

        symbol = str(signal.get("symbol") or "UNKNOWN")
        strategy_id = str(signal.get("strategy_id") or "default")
        entry = ReflexionEntry(
            symbol=symbol,
            strategy_id=strategy_id,
            outcome="advice",
            pnl=0.0,
            lesson=answer[:2000],
            created_at=datetime.utcnow(),
        )
        row_id = await self.repo.add_entry(entry)
        self.seen.add(sid)
        return {"signal_id": sid, "reflexion_id": row_id, "symbol": symbol}


async def main() -> None:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    repo = ReflexionMemoryRepository(sqlite_path=DB_PATH)
    await repo.initialize()
    agent = HermesAdvisorAgent(hermes=HermesClient(), repo=repo)

    while True:
        try:
            post_status("online", "Waiting for pending signals", 0)
            res = await agent.run_once()
            if res:
                post_status("idle", f"Learned from signal {res['signal_id']}", 100)
                logger.info("Hermes advice stored signal_id=%s reflexion_id=%s", res["signal_id"], res["reflexion_id"])
            else:
                post_status("idle", "No pending signals", 100)
        except Exception as exc:
            logger.error("Hermes advisor error: %s", exc, exc_info=True)
            post_status("error", str(exc), 0)
        await asyncio.sleep(POLL_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())


--- END FILE: agents\hermes_advisor_agent.py ---

--- START FILE: agents\macro_agent.py ---
"""Macro intelligence research agent."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import yfinance as yf
from dotenv import load_dotenv

# Ensure `import trading_system.*` works no matter where we launch from.
_PKG_DIR = Path(__file__).resolve().parents[1]  # .../trading_system
_REPO_ROOT = _PKG_DIR.parent
sys.path.insert(0, str(_REPO_ROOT))
load_dotenv(_PKG_DIR / ".env")

_LOGS_DIR = Path(__file__).resolve().parents[1] / "logs"
_LOGS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(_LOGS_DIR / f'agent_{datetime.now().strftime("%Y%m%d")}.log')),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

DASHBOARD_URL = os.getenv('DASHBOARD_URL', 'https://my-trading-dashboard-8.onrender.com')


def post_status(status: str, task: str = '', progress: int = 0):
    payload = {'agent_id': 'macro_agent', 'status': status, 'task': task, 'progress': progress, 'timestamp': datetime.now().isoformat()}
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(f'{DASHBOARD_URL}/agent-status', data=data, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass


class MacroIntelligenceAgent:
    DEFAULT_MACRO_SYMBOLS = {
        'dxy': 'DX-Y.NYB',
        'us10y': '^TNX',
        'oil': 'CL=F',
        'gold': 'GC=F',
        'vix': '^VIX',
    }

    async def run(self, symbols: Dict[str, str] | None = None) -> Dict[str, Any]:
        symbols = symbols or self.DEFAULT_MACRO_SYMBOLS
        output: Dict[str, Any] = {'series': {}, 'alerts': []}
        for label, ticker in symbols.items():
            try:
                frame = await asyncio.to_thread(
                    yf.download,
                    tickers=ticker,
                    period='5d',
                    interval='1d',
                    progress=False,
                    auto_adjust=False,
                )
            except Exception as exc:
                logger.exception('Macro fetch failed label=%s', label)
                output['series'][label] = {'error': str(exc)}
                continue
            if frame.empty:
                output['series'][label] = {'error': 'no_data'}
                continue

            if 'Close' not in frame:
                output['series'][label] = {'error': 'missing_close'}
                continue

            close = frame['Close']
            # yfinance can return a DataFrame for Close; collapse to one numeric Series.
            if hasattr(close, 'columns'):
                close = close.iloc[:, 0]
            close = close.dropna()
            if len(close) < 2:
                output['series'][label] = {'error': 'insufficient_data'}
                continue
            prev_close = float(close.iloc[-2])
            last_close = float(close.iloc[-1])
            if prev_close == 0:
                output['series'][label] = {'error': 'invalid_prev_close'}
                continue
            pct_change = float((last_close - prev_close) / prev_close * 100)
            output['series'][label] = {'last': last_close, 'daily_pct': pct_change}
            if abs(pct_change) >= 2.0:
                output['alerts'].append({'label': label, 'daily_pct': pct_change, 'severity': 'high'})
        return output


async def main():
    agent = MacroIntelligenceAgent()
    while True:
        try:
            post_status('processing', 'Analyzing macro indicators', 50)
            result = await agent.run()
            post_status('idle', f"Macro alerts: {len(result.get('alerts', []))}", 100)
            logger.info('Macro cycle complete alerts=%s', len(result.get('alerts', [])))
        except Exception as e:
            logger.error('Agent error: %s', e, exc_info=True)
            post_status('error', str(e), 0)
        await asyncio.sleep(10)


if __name__ == '__main__':
    asyncio.run(main())

--- END FILE: agents\macro_agent.py ---

--- START FILE: agents\news_agent.py ---
"""News and sentiment research agent."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Ensure `import trading_system.*` works no matter where we launch from.
_PKG_DIR = Path(__file__).resolve().parents[1]  # .../trading_system
_REPO_ROOT = _PKG_DIR.parent
sys.path.insert(0, str(_REPO_ROOT))
load_dotenv(_PKG_DIR / ".env")

_LOGS_DIR = Path(__file__).resolve().parents[1] / "logs"
_LOGS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(_LOGS_DIR / f'agent_{datetime.now().strftime("%Y%m%d")}.log')),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

from trading_system.skills.news_intelligence_skill import NewsIntelligenceSkill

DASHBOARD_URL = os.getenv('DASHBOARD_URL', 'https://my-trading-dashboard-8.onrender.com')


def post_status(status: str, task: str = '', progress: int = 0):
    payload = {'agent_id': 'news_agent', 'status': status, 'task': task, 'progress': progress, 'timestamp': datetime.now().isoformat()}
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(f'{DASHBOARD_URL}/agent-status', data=data, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass


class NewsSentimentAgent:
    def __init__(self, skill: NewsIntelligenceSkill):
        self.skill = skill

    async def run(self, symbol: str):
        return await self.skill.analyze(symbol)


async def main():
    agent = NewsSentimentAgent(NewsIntelligenceSkill())
    while True:
        try:
            post_status('processing', 'Analyzing INFY sentiment', 50)
            result = await agent.run('INFY')
            sentiment = result.get('sentiment', {}).get('label', 'unknown') if isinstance(result, dict) else 'unknown'
            post_status('idle', f'Sentiment: {sentiment}', 100)
            logger.info('News sentiment: %s', sentiment)
        except Exception as e:
            logger.error('Agent error: %s', e, exc_info=True)
            post_status('error', str(e), 0)
        await asyncio.sleep(8)


if __name__ == '__main__':
    asyncio.run(main())

--- END FILE: agents\news_agent.py ---

--- START FILE: agents\orchestration_runner.py ---
import os
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime

import requests
from dotenv import load_dotenv

# Ensure package imports like `trading_system.*` work when running this file directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
load_dotenv(Path(__file__).parent.parent / '.env')

_LOGS_DIR = Path(__file__).resolve().parents[1] / "logs"
_LOGS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler(str(_LOGS_DIR / f"agent_{datetime.now().strftime('%Y%m%d')}.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

from trading_system.agents.macro_agent import MacroIntelligenceAgent
from trading_system.agents.technical_agent import TechnicalAnalysisAgent
from trading_system.agents.whale_agent import WhaleIntelligenceAgent
from trading_system.agents.news_agent import NewsSentimentAgent
from trading_system.agents.pinescript_agent import PineScriptGenerationAgent
from trading_system.skills.technical_analysis_skill import TechnicalAnalysisSkill
from trading_system.skills.whale_tracker_skill import WhaleTrackerSkill
from trading_system.skills.news_intelligence_skill import NewsIntelligenceSkill
from trading_system.skills.pinescript_strategy_generator import PineScriptStrategyGenerator, MultiModelRouter
from trading_system.skills.backtesting_skill import BacktestingSkill
from trading_system.config.settings import ModelProviderSettings, ModelRoutingSettings, load_settings

DASHBOARD_URL = os.getenv('DASHBOARD_URL', 'https://my-trading-dashboard-8.onrender.com')


def post_status(agent_id: str, status: str, task: str, progress: int):
    try:
        requests.post(f"{DASHBOARD_URL}/agent-status", json={"agent_id": agent_id, "status": status, "task": task, "progress": progress, "timestamp": datetime.now().isoformat()}, timeout=10)
    except Exception:
        pass


async def run_macro():
    agent = MacroIntelligenceAgent()
    while True:
        try:
            post_status('macro_agent', 'processing', 'Analyzing macro', 50)
            await agent.run()
            post_status('macro_agent', 'idle', 'Ready', 100)
        except Exception as e:
            logger.error('macro_agent error: %s', e, exc_info=True)
            post_status('macro_agent', 'error', str(e), 0)
        await asyncio.sleep(5)


async def run_tech():
    agent = TechnicalAnalysisAgent(TechnicalAnalysisSkill())
    while True:
        try:
            post_status('technical_agent', 'processing', 'Analyzing INFY', 50)
            res = await agent.run('INFY', '4h')
            sig = str(res.get('signal', ''))
            if sig == 'buy_bias':
                requests.post(f"{DASHBOARD_URL}/alerts/buy-signal", json={"symbol": 'INFY', "signal": 'buy'}, timeout=10)
            post_status('technical_agent', 'idle', f"Signal: {sig}", 100)
        except Exception as e:
            logger.error('technical_agent error: %s', e, exc_info=True)
            post_status('technical_agent', 'error', str(e), 0)
        await asyncio.sleep(5)


async def run_whale():
    agent = WhaleIntelligenceAgent(WhaleTrackerSkill())
    while True:
        try:
            post_status('whale_agent', 'processing', 'Tracking BTC whales', 50)
            await agent.run('BTC')
            post_status('whale_agent', 'idle', 'Ready', 100)
        except Exception as e:
            logger.error('whale_agent error: %s', e, exc_info=True)
            post_status('whale_agent', 'error', str(e), 0)
        await asyncio.sleep(8)


async def run_news():
    agent = NewsSentimentAgent(NewsIntelligenceSkill())
    while True:
        try:
            post_status('news_agent', 'processing', 'Analyzing INFY sentiment', 50)
            await agent.run('INFY')
            post_status('news_agent', 'idle', 'Ready', 100)
        except Exception as e:
            logger.error('news_agent error: %s', e, exc_info=True)
            post_status('news_agent', 'error', str(e), 0)
        await asyncio.sleep(8)


async def run_pine():
    # Force PineScript routing to models actually installed in Ollama.
    # This avoids failures from stale defaults like `deepseek-coder:*` or `qwen2.5-coder:*`.
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    primary = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    fallback = os.getenv("OLLAMA_FALLBACK", "deepseek-r1:7b")
    timeout_sec = int(os.getenv("OLLAMA_TIMEOUT_SEC", "180"))
    routing = ModelRoutingSettings(
        local_first=True,
        providers=[
            ModelProviderSettings(name="ollama", model=primary, enabled=True, base_url=ollama_url, timeout_sec=timeout_sec),
            ModelProviderSettings(name="ollama", model=fallback, enabled=True, base_url=ollama_url, timeout_sec=timeout_sec),
        ],
    )
    router = MultiModelRouter(routing)
    agent = PineScriptGenerationAgent(PineScriptStrategyGenerator(router=router, backtester=BacktestingSkill()))
    while True:
        try:
            post_status('pinescript_agent', 'processing', 'Generating strategy', 50)
            await agent.run(indicators=['ema', 'rsi'], objective='momentum')
            post_status('pinescript_agent', 'idle', 'Ready', 100)
        except Exception as e:
            logger.error('pinescript_agent error: %s', e, exc_info=True)
            post_status('pinescript_agent', 'error', str(e), 0)
        await asyncio.sleep(10)


async def main():
    await asyncio.gather(run_macro(), run_tech(), run_whale(), run_news(), run_pine())


if __name__ == '__main__':
    asyncio.run(main())

--- END FILE: agents\orchestration_runner.py ---

--- START FILE: agents\pinescript_agent.py ---
"""PineScript generation research agent."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv

# Ensure `import trading_system.*` works no matter where we launch from.
_PKG_DIR = Path(__file__).resolve().parents[1]  # .../trading_system
_REPO_ROOT = _PKG_DIR.parent
sys.path.insert(0, str(_REPO_ROOT))
load_dotenv(_PKG_DIR / ".env")

_LOGS_DIR = Path(__file__).resolve().parents[1] / "logs"
_LOGS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(_LOGS_DIR / f'agent_{datetime.now().strftime("%Y%m%d")}.log')),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

from trading_system.config.settings import load_settings
from trading_system.skills.backtesting_skill import BacktestingSkill
from trading_system.skills.pinescript_strategy_generator import MultiModelRouter, PineScriptStrategyGenerator

DASHBOARD_URL = os.getenv('DASHBOARD_URL', 'https://my-trading-dashboard-8.onrender.com')


def post_status(status: str, task: str = '', progress: int = 0):
    payload = {'agent_id': 'pinescript_agent', 'status': status, 'task': task, 'progress': progress, 'timestamp': datetime.now().isoformat()}
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(f'{DASHBOARD_URL}/agent-status', data=data, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass


class PineScriptGenerationAgent:
    def __init__(self, generator: PineScriptStrategyGenerator) -> None:
        self.generator = generator

    async def run(
        self,
        indicators: List[str],
        objective: str,
        symbol: str = 'BTC-USD',
        timeframe: str = '1d',
        lookback_days: int = 180,
    ) -> Dict[str, Any]:
        result = await self.generator.indicator_to_strategy(
            indicators=indicators,
            objective=objective,
            symbol=symbol,
            timeframe=timeframe,
            lookback_days=lookback_days,
        )
        logger.info('PineScript generation complete symbol=%s valid=%s', symbol, result['validation']['valid'])
        return result


async def main():
    settings = load_settings()
    router = MultiModelRouter(settings.model_routing)
    agent = PineScriptGenerationAgent(PineScriptStrategyGenerator(router=router, backtester=BacktestingSkill()))
    while True:
        try:
            post_status('processing', 'Generating Pine strategy', 50)
            await agent.run(indicators=['ema', 'rsi'], objective='momentum', symbol='INFY')
            post_status('idle', 'Pine strategy ready', 100)
        except Exception as e:
            logger.error('Agent error: %s', e, exc_info=True)
            post_status('error', str(e), 0)
        await asyncio.sleep(12)


if __name__ == '__main__':
    asyncio.run(main())

--- END FILE: agents\pinescript_agent.py ---

--- START FILE: agents\reflexion_agent.py ---
"""Reflexion/learning agent for continuous system improvement."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from trading_system.memory.reflexion_memory import ReflexionEntry, ReflexionMemoryRepository
from trading_system.memory.vector_memory import VectorMemory

logger = logging.getLogger(__name__)


class ReflexionAgent:
    """Derives and stores lessons after outcomes."""

    def __init__(self, repo: ReflexionMemoryRepository, vector_memory: VectorMemory) -> None:
        self.repo = repo
        self.vector_memory = vector_memory

    async def reflect_trade(
        self,
        symbol: str,
        strategy_id: str,
        pnl: float,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create and persist one reflexion entry."""
        context = context or {}
        if pnl > 0:
            outcome = "win"
            lesson = "Conditions aligned with strategy edge; preserve setup filters."
        elif pnl < 0:
            outcome = "loss"
            lesson = "Loss likely from regime mismatch; tighten filters or reduce size."
        else:
            outcome = "flat"
            lesson = "No edge realized; avoid overtrading this setup."

        entry = ReflexionEntry(
            symbol=symbol,
            strategy_id=strategy_id,
            outcome=outcome,
            pnl=pnl,
            lesson=lesson,
            created_at=datetime.now(timezone.utc),
        )
        row_id = await self.repo.add_entry(entry)
        vec_text = f"{symbol} {strategy_id} {outcome} {lesson} context={context}"
        self.vector_memory.upsert(record_id=f"reflexion:{row_id}", text=vec_text, metadata={"symbol": symbol})
        logger.info("Reflexion saved symbol=%s pnl=%.2f", symbol, pnl)
        return {"id": row_id, "symbol": symbol, "strategy_id": strategy_id, "outcome": outcome, "lesson": lesson}

    async def latest(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Return recent reflexion items and summary."""
        lessons = await self.repo.recent_lessons(symbol=symbol, limit=10)
        summary = await self.repo.summarize(symbol=symbol)
        return {"lessons": lessons, "summary": summary}

--- END FILE: agents\reflexion_agent.py ---

--- START FILE: agents\risk_guardian.py ---
"""Risk-first guardian with hard veto authority over execution."""

from __future__ import annotations

import logging
from dataclasses import dataclass
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
    Enforces risk controls before any order reaches execution.

    Guarantees:
    - Backtests and paper modes cannot bypass risk checks.
    - Live mode requires explicit approval by execution layer after risk approval.
    """

    def __init__(self, limits: RiskLimits) -> None:
        self.limits = limits

    def validate_order(
        self,
        order: OrderRequest,
        snapshot: PortfolioSnapshot,
        correlation_context: Optional[CorrelationContext] = None,
        kill_switch_active: bool = False,
    ) -> RiskCheckResult:
        """Run full risk pipeline and return veto/approval decision."""
        reasons: List[str] = []
        if kill_switch_active:
            reasons.append("Kill switch active.")
            return RiskCheckResult(decision=RiskDecision.REJECTED, reasons=reasons, limits=self.limits)

        notional_estimate = self._order_notional(order)
        current_exposure = snapshot.gross_exposure
        symbol_exposure = self._symbol_exposure(snapshot.positions, order.symbol)
        projected_exposure = current_exposure + notional_estimate
        projected_symbol_exposure = symbol_exposure + notional_estimate

        if snapshot.daily_realized_pnl <= -abs(self.limits.max_daily_loss):
            reasons.append("Max daily loss exceeded.")
        if projected_exposure > self.limits.max_exposure:
            reasons.append(
                f"Projected exposure {projected_exposure:.2f} exceeds max {self.limits.max_exposure:.2f}."
            )
        if snapshot.balance > 0:
            symbol_pct = (projected_symbol_exposure / snapshot.balance) * 100
            if symbol_pct > self.limits.max_symbol_exposure_pct:
                reasons.append(
                    f"Projected symbol exposure {symbol_pct:.2f}% exceeds max {self.limits.max_symbol_exposure_pct:.2f}%."
                )
        if order.leverage > self.limits.max_leverage:
            reasons.append(f"Leverage {order.leverage:.2f} exceeds max {self.limits.max_leverage:.2f}.")
        if order.expected_slippage_bps > self.limits.max_slippage_bps:
            reasons.append(
                f"Expected slippage {order.expected_slippage_bps:.2f}bps exceeds max {self.limits.max_slippage_bps:.2f}bps."
            )
        if snapshot.consecutive_losses >= self.limits.max_consecutive_losses:
            reasons.append(
                f"Consecutive losses {snapshot.consecutive_losses} exceed max {self.limits.max_consecutive_losses}."
            )

        stop_loss_reason = self._validate_stop_loss(order)
        if stop_loss_reason:
            reasons.append(stop_loss_reason)

        if correlation_context:
            corr_reason = self._validate_correlation(order, snapshot.positions, correlation_context)
            if corr_reason:
                reasons.append(corr_reason)

        decision = RiskDecision.REJECTED if reasons else RiskDecision.APPROVED
        return RiskCheckResult(decision=decision, reasons=reasons, limits=self.limits)

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

--- END FILE: agents\risk_guardian.py ---

--- START FILE: agents\technical_agent.py ---
"""Technical analysis research agent."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Ensure `import trading_system.*` works no matter where we launch from.
_PKG_DIR = Path(__file__).resolve().parents[1]  # .../trading_system
_REPO_ROOT = _PKG_DIR.parent
sys.path.insert(0, str(_REPO_ROOT))
load_dotenv(_PKG_DIR / ".env")

_LOGS_DIR = Path(__file__).resolve().parents[1] / "logs"
_LOGS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(_LOGS_DIR / f'agent_{datetime.now().strftime("%Y%m%d")}.log')),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

from trading_system.skills.technical_analysis_skill import TechnicalAnalysisSkill

DASHBOARD_URL = os.getenv('DASHBOARD_URL', 'https://my-trading-dashboard-8.onrender.com')


def post_status(status: str, task: str = '', progress: int = 0):
    payload = {'agent_id': 'technical_agent', 'status': status, 'task': task, 'progress': progress, 'timestamp': datetime.now().isoformat()}
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(f'{DASHBOARD_URL}/agent-status', data=data, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass


class TechnicalAnalysisAgent:
    def __init__(self, skill: TechnicalAnalysisSkill):
        self.skill = skill

    async def run(self, symbol: str, timeframe: str = '1d', lookback: str = '6mo'):
        r = await self.skill.analyze_symbol(symbol=symbol, timeframe=timeframe, lookback=lookback)
        return {
            'symbol': r.symbol,
            'timeframe': r.timeframe,
            'price': r.close,
            'ema_fast': r.ema_fast,
            'ema_slow': r.ema_slow,
            'rsi': r.rsi,
            'signal': r.signal,
            'trend': r.trend,
        }


async def main():
    agent = TechnicalAnalysisAgent(TechnicalAnalysisSkill())
    while True:
        try:
            post_status('processing', 'Analyzing INFY', 50)
            result = await agent.run('INFY', '4h')
            post_status('idle', f"Signal: {result.get('signal')}", 100)
            logger.info('Technical signal: %s', result.get('signal'))
        except Exception as e:
            logger.error('Agent error: %s', e, exc_info=True)
            post_status('error', str(e), 0)
        await asyncio.sleep(5)


if __name__ == '__main__':
    asyncio.run(main())

--- END FILE: agents\technical_agent.py ---

--- START FILE: agents\trade_execution_agent.py ---
"""Dedicated trade execution agent.

Responsibilities:
- Poll cloud dashboard for APPROVED signals.
- Compute sizing, brokerage estimate, and tick rounding.
- Run a RiskGuardian pre-check (hard veto).
- Create a live approval ticket (shared via SQLite so Boss/Telegram can approve).
- Send a Telegram approval request containing the ticket id.
- Only after approval: execute via ExecutionEngine (paper/live).
- Mark the signal as executed in the cloud dashboard (prevents double fills).
"""

from __future__ import annotations

import asyncio
import json
import logging
import math
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv

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
logger = logging.getLogger("trade_execution_agent")

from trading_system.config.models import (  # noqa: E402
    OrderRequest,
    OrderSide,
    OrderType,
    RiskDecision,
    TradingMode,
)
from trading_system.main import build_container  # noqa: E402


DASHBOARD_URL = os.getenv("DASHBOARD_URL", "https://my-trading-dashboard-8.onrender.com").rstrip("/")
DASHBOARD_TIMEOUT = int(os.getenv("DASHBOARD_TIMEOUT", "15"))
POLL_INTERVAL = int(os.getenv("EXECUTION_AGENT_POLL_INTERVAL", "5"))

DEFAULT_STOP_LOSS_PCT = float(os.getenv("DEFAULT_STOP_LOSS_PCT", "2.0"))
DEFAULT_TAKE_PROFIT_PCT = float(os.getenv("DEFAULT_TAKE_PROFIT_PCT", "5.0"))

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()


def _get_json(url: str, timeout: int = 15) -> Dict[str, Any]:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body) if body else {}


def _post_json(url: str, payload: dict, timeout: int = 15) -> Dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body) if body else {}


def _round_to_tick(price: float, tick: float) -> float:
    if tick <= 0:
        return float(price)
    return round(round(price / tick) * tick, 10)


def _infer_tick_size(symbol: str) -> float:
    sym = symbol.upper()
    if sym.endswith(".NS"):
        return 0.05
    if "/" in sym:
        return 0.01
    return 0.01


def _infer_broker(symbol: str) -> str:
    sym = symbol.upper()
    if "/" in sym:
        return "binance"
    if sym.endswith(".NS"):
        return "upstox"
    return "alpaca"


def _estimate_brokerage(notional: float, broker: str) -> float:
    """Very conservative brokerage estimate (placeholder).

    Real charges vary by broker/segment; this is used only for previews.
    """
    b = broker.lower()
    if b == "binance":
        return notional * 0.001  # 0.10%
    if b == "alpaca":
        return 0.0
    if b == "upstox":
        return min(20.0, notional * 0.0003)  # cap at 20 INR-equivalent preview
    return notional * 0.001


async def _send_telegram(text: str) -> None:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as _:
            return
    except Exception as exc:  # noqa: BLE001
        logger.warning("Telegram send failed: %s", exc)


async def _poll_approved_signals() -> list[dict]:
    try:
        data = _get_json(f"{DASHBOARD_URL}/api/signals/approved?include_executed=false", timeout=DASHBOARD_TIMEOUT)
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


async def _poll_watchlist() -> list[dict]:
    try:
        data = _get_json(f"{DASHBOARD_URL}/api/watchlist", timeout=DASHBOARD_TIMEOUT)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and isinstance(data.get("items"), list):
            return data["items"]
        return []
    except Exception:
        return []


def _qty_from_watchlist(symbol: str, watchlist: list[dict]) -> int:
    sym = symbol.upper()
    for item in watchlist:
        if str(item.get("symbol", "")).upper() == sym:
            q = item.get("quantity_to_buy") or item.get("quantity") or 0
            try:
                return max(1, int(q))
            except Exception:
                return 1
    return 1


async def main() -> None:
    container = await build_container()
    await container.event_bus.start()

    exec_engine = container.execution_engine
    risk_guardian = container.risk_guardian
    global_state = container.global_state
    approval_manager = container.live_approval_manager

    mode = TradingMode(os.getenv("TRADING_MODE", "paper").lower())

    logger.info("TradeExecutionAgent started mode=%s dashboard=%s", mode.value, DASHBOARD_URL)

    seen: Dict[str, str] = {}  # signal_id -> last_state
    while True:
        try:
            watchlist = await _poll_watchlist()
            signals = await _poll_approved_signals()
            for sig in signals:
                signal_id = str(sig.get("id") or "").strip()
                if not signal_id:
                    continue
                if sig.get("order_id"):
                    continue  # already executed

                state_key = f"{sig.get('approval_status')}|{sig.get('signal_price')}"
                if seen.get(signal_id) == state_key:
                    continue
                seen[signal_id] = state_key

                symbol = str(sig.get("symbol") or "").strip().upper()
                signal_type = str(sig.get("signal_type") or "buy").lower().strip()
                price = float(sig.get("signal_price") or 0.0)
                if not symbol or price <= 0:
                    continue

                broker = _infer_broker(symbol)
                tick = _infer_tick_size(symbol)
                qty_target = _qty_from_watchlist(symbol, watchlist)

                side = OrderSide.BUY if signal_type == "buy" else OrderSide.SELL
                stop_loss = price * (1 - (DEFAULT_STOP_LOSS_PCT / 100.0)) if side == OrderSide.BUY else price * (1 + (DEFAULT_STOP_LOSS_PCT / 100.0))
                take_profit = price * (1 + (DEFAULT_TAKE_PROFIT_PCT / 100.0)) if side == OrderSide.BUY else price * (1 - (DEFAULT_TAKE_PROFIT_PCT / 100.0))

                stop_loss = _round_to_tick(stop_loss, tick)
                take_profit = _round_to_tick(take_profit, tick)
                limit_price = _round_to_tick(price, tick)

                # Sizing cap: don't exceed MAX_POSITION_SIZE * available_cash (best-effort).
                snapshot = await global_state.snapshot(mode)
                max_pos_frac = float(os.getenv("MAX_POSITION_SIZE", "0.03"))
                budget = max(0.0, float(snapshot.available_cash)) * max_pos_frac
                max_qty_by_budget = int(math.floor(budget / max(limit_price, 1e-9))) if budget > 0 else qty_target
                qty = max(1, min(qty_target, max_qty_by_budget or qty_target))

                order = OrderRequest(
                    symbol=symbol,
                    side=side,
                    quantity=float(qty),
                    mode=mode,
                    broker=broker,
                    order_type=OrderType.MARKET,
                    limit_price=None,
                    stop_loss=float(stop_loss),
                    take_profit=float(take_profit),
                    signal_id=signal_id,
                    metadata={
                        "mark_price": limit_price,
                        "signal": sig,
                        "tick_size": tick,
                        "brokerage_estimate": _estimate_brokerage(limit_price * qty, broker),
                    },
                )

                # Risk pre-check before we even ask for approval.
                risk = risk_guardian.validate_order(order=order, snapshot=snapshot, correlation_context=None, kill_switch_active=False)
                if risk.decision == RiskDecision.REJECTED:
                    logger.warning("Risk veto signal_id=%s symbol=%s reasons=%s", signal_id, symbol, risk.reasons)
                    continue

                if mode == TradingMode.LIVE:
                    ticket = await approval_manager.create_ticket(order, requested_by="trade_execution_agent")
                    order.metadata["approval_ticket_id"] = ticket["ticket_id"]
                    preview = order.model_dump(mode="json")
                    msg = (
                        f"LIVE TRADE APPROVAL REQUIRED\n"
                        f"symbol={symbol}\n"
                        f"side={side.value}\n"
                        f"qty={qty}\n"
                        f"price~{limit_price}\n"
                        f"stop_loss={stop_loss} take_profit={take_profit}\n"
                        f"broker={broker}\n"
                        f"ticket={ticket['ticket_id']}\n\n"
                        f"Approve by sending:\n"
                        f"approve {ticket['ticket_id']}\n"
                        f"(in Dashboard Chat or Telegram)\n"
                    )
                    await _send_telegram(msg)
                    logger.info("Approval requested signal_id=%s ticket=%s", signal_id, ticket["ticket_id"])

                    # Wait for approval up to TTL.
                    deadline = datetime.now(timezone.utc).timestamp() + 300
                    while datetime.now(timezone.utc).timestamp() < deadline:
                        t = await approval_manager.get_ticket(ticket["ticket_id"])
                        if t and t.get("approved"):
                            break
                        await asyncio.sleep(2)

                # Execute (paper/live). ExecutionEngine will enforce ticket validity in live mode.
                result = await exec_engine.submit_order(order=order, human_approved=(mode == TradingMode.LIVE))
                if not result.accepted:
                    logger.warning("Execution rejected signal_id=%s status=%s msg=%s", signal_id, result.status, result.message)
                    continue

                # Mark executed in dashboard to prevent duplicates.
                try:
                    _post_json(
                        f"{DASHBOARD_URL}/api/signal/mark-executed",
                        {
                            "signal_id": signal_id,
                            "order_id": result.order_id or f"{broker.upper()}-{datetime.now(timezone.utc).timestamp()}",
                            "execution_price": result.average_price,
                            "broker": broker,
                        },
                        timeout=DASHBOARD_TIMEOUT,
                    )
                except Exception:
                    pass

                logger.info("Executed signal_id=%s symbol=%s order_id=%s", signal_id, symbol, result.order_id)

        except Exception as exc:  # noqa: BLE001
            logger.exception("TradeExecutionAgent loop error: %s", exc)

        await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())


--- END FILE: agents\trade_execution_agent.py ---

--- START FILE: agents\watchlist_executor.py ---
"""Watchlist executor: polls the cloud dashboard watchlist and emits signals.

Design notes:
- Runs locally on the laptop (next to Ollama and agents).
- Stores watchlist + pending approvals in the cloud dashboard (Render).
- Uses existing local skills (technical/news) and posts a BUY signal when conditions match.
- Cooldown is enforced server-side via /alerts/buy-signal (default 60s).
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv

# Ensure `import trading_system.*` works no matter where we launch from.
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
        logging.FileHandler(str(_LOGS_DIR / f"watchlist_executor_{datetime.now().strftime('%Y%m%d')}.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

from trading_system.skills.news_intelligence_skill import NewsIntelligenceSkill
from trading_system.skills.technical_analysis_skill import TechnicalAnalysisSkill

DASHBOARD_URL = os.getenv("DASHBOARD_URL", "https://my-trading-dashboard-8.onrender.com").rstrip("/")
CHECK_INTERVAL_SECONDS = int(os.getenv("WATCHLIST_CHECK_INTERVAL_SEC", "300"))  # 5 minutes default


def _safe_json(res: urllib.response.addinfourl) -> Any:
    body = res.read().decode("utf-8")
    return json.loads(body) if body else {}


def _get_json(url: str, timeout: int = 15) -> Any:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return _safe_json(resp)


def _post_json(url: str, payload: dict, timeout: int = 15) -> Any:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return _safe_json(resp)


def post_status(status: str, task: str = "", progress: int = 0) -> None:
    payload = {
        "agent_id": "watchlist_executor",
        "status": status,
        "task": task,
        "progress": progress,
        "timestamp": datetime.now().isoformat(),
    }
    try:
        _post_json(f"{DASHBOARD_URL}/agent-status", payload, timeout=10)
    except Exception:
        pass


def _score_technical(snapshot: Any) -> float:
    # Very lightweight: treat buy_bias as stronger, else neutral.
    sig = str(getattr(snapshot, "signal", "")).lower()
    if sig == "buy_bias":
        return 80.0
    if sig == "sell_bias":
        return 20.0
    return 50.0


def _score_news(sentiment: Dict[str, Any]) -> float:
    label = str(sentiment.get("label") or "neutral").lower()
    agg = float(sentiment.get("aggregate_score") or 0.0)
    if label == "positive":
        return min(90.0, 60.0 + agg * 5.0)
    if label == "negative":
        return max(10.0, 40.0 + agg * 5.0)
    return 50.0


def _overall(tech: float, news: float, fund: float, risk: float) -> float:
    return (tech + news + fund + risk) / 4.0


async def _analyze_symbol(symbol: str, timeframe: str) -> Tuple[Optional[float], Dict[str, Any]]:
    tech_skill = TechnicalAnalysisSkill()
    news_skill = NewsIntelligenceSkill()

    snapshot = await tech_skill.analyze_symbol(symbol=symbol, timeframe=timeframe, lookback="6mo")
    tech_score = _score_technical(snapshot)

    news = await news_skill.analyze(symbol)
    news_score = _score_news(news.get("sentiment") or {})

    # Fundamentals + risk placeholders (wire later to your real portfolio/broker state).
    fundamental_score = 55.0
    risk_score = 70.0

    price = float(snapshot.close)
    overall_score = _overall(tech_score, news_score, fundamental_score, risk_score)

    return price, {
        "technical_score": tech_score,
        "news_score": news_score,
        "fundamental_score": fundamental_score,
        "risk_score": risk_score,
        "overall_score": overall_score,
        "signal": str(snapshot.signal),
        "trend": str(snapshot.trend),
    }


async def main() -> None:
    logger.info("Watchlist executor started dashboard=%s interval_sec=%s", DASHBOARD_URL, CHECK_INTERVAL_SECONDS)

    while True:
        post_status("online", "Polling watchlist", 0)
        try:
            items: List[Dict[str, Any]] = _get_json(f"{DASHBOARD_URL}/api/watchlist", timeout=20) or []
            active = [i for i in items if str(i.get("status") or "active") != "removed"]
            logger.info("Loaded watchlist count=%s", len(active))

            for idx, item in enumerate(active, start=1):
                symbol = str(item.get("symbol") or "").upper().strip()
                if not symbol:
                    continue
                timeframe = str(item.get("timeframe") or "1d")
                strategy_id = str(item.get("strategy_id") or "default")

                post_status("processing", f"Analyzing {symbol}", int(idx / max(len(active), 1) * 100))
                price, scores = await _analyze_symbol(symbol, timeframe)

                # Simple rule: only emit BUY when technical says buy_bias AND overall_score >= 60.
                is_buy = str(scores.get("signal", "")).lower() == "buy_bias" and float(scores.get("overall_score") or 0) >= 60.0
                if is_buy:
                    payload = {
                        "symbol": symbol,
                        "signal": "buy",
                        "strategy_id": strategy_id,
                        "price": float(price or 0.0),
                        "technical_score": float(scores["technical_score"]),
                        "news_score": float(scores["news_score"]),
                        "fundamental_score": float(scores["fundamental_score"]),
                        "risk_score": float(scores["risk_score"]),
                        "overall_score": float(scores["overall_score"]),
                    }
                    try:
                        res = _post_json(f"{DASHBOARD_URL}/alerts/buy-signal", payload, timeout=20)
                        logger.info("Posted BUY signal symbol=%s status=%s", symbol, res.get("status"))
                    except Exception as exc:
                        logger.warning("Failed posting signal symbol=%s error=%s", symbol, exc)
                else:
                    logger.info("No buy signal symbol=%s signal=%s overall=%.1f", symbol, scores.get("signal"), float(scores.get("overall_score") or 0))

            post_status("idle", "Cycle complete", 100)
        except Exception as exc:
            logger.error("Executor error: %s", exc, exc_info=True)
            post_status("error", str(exc), 0)

        await asyncio.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())


--- END FILE: agents\watchlist_executor.py ---

--- START FILE: agents\whale_agent.py ---
"""Whale intelligence research agent."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Ensure `import trading_system.*` works no matter where we launch from.
_PKG_DIR = Path(__file__).resolve().parents[1]  # .../trading_system
_REPO_ROOT = _PKG_DIR.parent
sys.path.insert(0, str(_REPO_ROOT))
load_dotenv(_PKG_DIR / ".env")

_LOGS_DIR = Path(__file__).resolve().parents[1] / "logs"
_LOGS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(_LOGS_DIR / f'agent_{datetime.now().strftime("%Y%m%d")}.log')),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

from trading_system.skills.whale_tracker_skill import WhaleTrackerSkill

DASHBOARD_URL = os.getenv('DASHBOARD_URL', 'https://my-trading-dashboard-8.onrender.com')


def post_status(status: str, task: str = '', progress: int = 0):
    payload = {'agent_id': 'whale_agent', 'status': status, 'task': task, 'progress': progress, 'timestamp': datetime.now().isoformat()}
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(f'{DASHBOARD_URL}/agent-status', data=data, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass


class WhaleIntelligenceAgent:
    def __init__(self, skill: WhaleTrackerSkill):
        self.skill = skill

    async def run(self, coin: str = 'BTC'):
        return await self.skill.analyze_whale_activity(coin=coin)


async def main():
    agent = WhaleIntelligenceAgent(WhaleTrackerSkill())
    while True:
        try:
            post_status('processing', 'Tracking BTC whales', 50)
            result = await agent.run('BTC')
            post_status('idle', 'Whale scan complete', 100)
            logger.info('Whale sentiment: %s', result.get('sentiment'))
        except Exception as e:
            logger.error('Agent error: %s', e, exc_info=True)
            post_status('error', str(e), 0)
        await asyncio.sleep(8)


if __name__ == '__main__':
    asyncio.run(main())

--- END FILE: agents\whale_agent.py ---

--- START FILE: agents\__init__.py ---
from .technical_agent import TechnicalAnalysisAgent
from .whale_agent import WhaleIntelligenceAgent
from .macro_agent import MacroIntelligenceAgent
from .news_agent import NewsSentimentAgent
from .boss_agent import BossAgent
from .hermes_advisor_agent import HermesAdvisorAgent
from .analysis_agent import AnalysisAgent
from .backtesting_agent import BacktestingAgent

__all__ = [
    "TechnicalAnalysisAgent",
    "WhaleIntelligenceAgent",
    "MacroIntelligenceAgent",
    "NewsSentimentAgent",
    "BossAgent",
    "HermesAdvisorAgent",
    "AnalysisAgent",
    "BacktestingAgent",
]

--- END FILE: agents\__init__.py ---

--- START FILE: api\dashboard_api.py ---
"""Dashboard and control-plane API."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query

from trading_system.config.models import BacktestRequest, OrderRequest, TradingMode
from trading_system.config.settings import DependencyContainer

logger = logging.getLogger(__name__)


def create_dashboard_router(container: DependencyContainer, auth_guard: object) -> APIRouter:
    """Create API router for dashboard and execution controls."""
    router = APIRouter(prefix="/api", tags=["dashboard"])

    @router.get("/health")
    async def health() -> Dict[str, Any]:
        trade_db = await container.trade_memory.heartbeat()
        return {
            "status": "ok",
            "app": container.settings.app_name,
            "event_bus": container.event_bus.stats(),
            "trade_db": trade_db,
            "kill_switch_active": container.execution_engine.kill_switch.is_active,
        }

    @router.get("/risk")
    async def risk(
        mode: TradingMode = Query(default=TradingMode.PAPER),
        _auth: None = Depends(auth_guard),
    ) -> Dict[str, Any]:
        snapshot = await container.global_state.snapshot(mode)
        return container.risk_guardian.portfolio_risk_snapshot(
            snapshot=snapshot,
            kill_switch_active=container.execution_engine.kill_switch.is_active,
        )

    @router.get("/positions")
    async def positions(
        mode: TradingMode = Query(default=TradingMode.PAPER),
        _auth: None = Depends(auth_guard),
    ) -> Dict[str, Any]:
        snapshot = await container.global_state.snapshot(mode)
        return {"mode": mode.value, "positions": snapshot.positions}

    @router.post("/orders")
    async def submit_order(
        order: OrderRequest,
        human_approved: bool = False,
        _auth: None = Depends(auth_guard),
    ) -> Dict[str, Any]:
        result = await container.execution_engine.submit_order(order, human_approved=human_approved)
        return result.model_dump()

    @router.post("/backtest")
    async def backtest(
        request: BacktestRequest,
        _auth: None = Depends(auth_guard),
    ) -> Dict[str, Any]:
        result = await container.boss_agent.backtester.run(request)
        return {
            "request": request.model_dump(),
            "metrics": result.metrics.model_dump(),
            "trades": result.trades[:100],
            "walk_forward": result.walk_forward,
        }

    @router.get("/whales")
    async def whales(coin: str = "BTC", _auth: None = Depends(auth_guard)) -> Dict[str, Any]:
        return await container.boss_agent.whale_agent.run(coin)

    @router.get("/briefing")
    async def daily_briefing(_auth: None = Depends(auth_guard)) -> Dict[str, Any]:
        """
        Daily briefing generator for operations reviews.
        """
        watchlist = container.settings.watchlist
        research = await asyncio.gather(
            *(container.boss_agent.technical_agent.run(symbol=s, timeframe="1d") for s in watchlist),
            return_exceptions=True,
        )
        items: List[Dict[str, Any]] = []
        for symbol, result in zip(watchlist, research):
            if isinstance(result, Exception):
                items.append({"symbol": symbol, "error": str(result)})
            else:
                items.append(result)
        risk_snapshot = await container.global_state.snapshot(TradingMode.PAPER)
        risk = container.risk_guardian.portfolio_risk_snapshot(
            snapshot=risk_snapshot,
            kill_switch_active=container.execution_engine.kill_switch.is_active,
        )
        whale = await container.boss_agent.whale_agent.run("BTC")
        macro = await container.boss_agent.macro_agent.run()
        return {
            "research": items,
            "macro": macro,
            "whale": whale,
            "risk": risk,
        }

    @router.post("/kill-switch/trigger")
    async def trigger_kill_switch(note: str, _auth: None = Depends(auth_guard)) -> Dict[str, Any]:
        container.execution_engine.kill_switch.manual_trigger(note)
        return {"active": True, "reason": container.execution_engine.kill_switch.state.reason}

    @router.post("/kill-switch/reset")
    async def reset_kill_switch(_auth: None = Depends(auth_guard)) -> Dict[str, Any]:
        container.execution_engine.kill_switch.reset()
        return {"active": False}

    @router.post("/live-approvals/request")
    async def create_live_approval_ticket(
        order: OrderRequest,
        requested_by: str = "operator",
        _auth: None = Depends(auth_guard),
    ) -> Dict[str, Any]:
        try:
            ticket = await container.live_approval_manager.create_ticket(order=order, requested_by=requested_by)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"ticket": ticket}

    @router.post("/live-approvals/{ticket_id}/approve")
    async def approve_live_approval_ticket(
        ticket_id: str,
        approved_by: str = "supervisor",
        _auth: None = Depends(auth_guard),
    ) -> Dict[str, Any]:
        try:
            ticket = await container.live_approval_manager.approve_ticket(ticket_id=ticket_id, approved_by=approved_by)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"ticket": ticket}

    @router.get("/live-approvals/{ticket_id}")
    async def get_live_approval_ticket(
        ticket_id: str,
        _auth: None = Depends(auth_guard),
    ) -> Dict[str, Any]:
        ticket = await container.live_approval_manager.get_ticket(ticket_id=ticket_id)
        if not ticket:
            return {"ticket": None}
        return {"ticket": ticket}

    return router

--- END FILE: api\dashboard_api.py ---

--- START FILE: api\security.py ---
"""API authentication and request throttling controls."""

from __future__ import annotations

import hmac
import logging
import time
from collections import defaultdict, deque
from typing import Deque, Dict, Iterable, Optional

from fastapi import Header, HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from trading_system.config.settings import AppSettings

logger = logging.getLogger(__name__)


class ApiKeyGuard:
    """Header-based API key guard."""

    def __init__(self, settings: AppSettings) -> None:
        self.require_api_key = settings.api.require_api_key
        self.keys = [k for k in settings.api.api_keys if k]

    async def __call__(self, x_api_key: Optional[str] = Header(default=None)) -> None:
        if not self.require_api_key:
            return
        if not self.keys:
            raise HTTPException(status_code=503, detail="API key auth enabled but no keys configured.")
        incoming = x_api_key or ""
        if not any(hmac.compare_digest(incoming, valid) for valid in self.keys):
            raise HTTPException(status_code=401, detail="Invalid API key.")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory per-IP token bucket by minute."""

    def __init__(
        self,
        app: object,
        enabled: bool = True,
        requests_per_minute: int = 120,
        exempt_paths: Iterable[str] | None = None,
    ) -> None:
        super().__init__(app)
        self.enabled = enabled
        self.requests_per_minute = max(1, int(requests_per_minute))
        self.exempt_paths = set(exempt_paths or [])
        self._windows: Dict[str, Deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        if not self.enabled:
            return await call_next(request)
        path = request.url.path
        if path in self.exempt_paths:
            return await call_next(request)
        ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = self._windows[ip]
        cutoff = now - 60.0
        while window and window[0] < cutoff:
            window.popleft()
        if len(window) >= self.requests_per_minute:
            logger.warning("Rate limit exceeded ip=%s path=%s", ip, path)
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded."})
        window.append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.requests_per_minute - len(window)))
        return response

--- END FILE: api\security.py ---

--- START FILE: api\telegram_api.py ---
"""Telegram webhook and command API."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import aiohttp
from fastapi import APIRouter, Depends, Header, HTTPException, Request

from trading_system.agents.boss_agent import BossAgent
from trading_system.config.settings import AppSettings

logger = logging.getLogger(__name__)


class TelegramService:
    """Telegram send-message helper."""

    def __init__(self, token: Optional[str], chat_id: Optional[str]) -> None:
        self.token = token
        self.chat_id = chat_id

    async def send_message(self, text: str, chat_id: Optional[str] = None) -> None:
        """Send message to Telegram chat."""
        if not self.token:
            logger.debug("Telegram token missing; message not sent")
            return
        target_chat = chat_id or self.chat_id
        if not target_chat:
            logger.debug("Telegram chat_id missing; message not sent")
            return
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {"chat_id": target_chat, "text": text}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status >= 400:
                    body = await response.text()
                    logger.warning("Telegram send failed status=%s body=%s", response.status, body)


def create_telegram_router(settings: AppSettings, boss_agent: BossAgent, auth_guard: object) -> APIRouter:
    """Create Telegram router with webhook and local command endpoint."""
    router = APIRouter(prefix="/telegram", tags=["telegram"])
    service = TelegramService(
        token=os.getenv("TELEGRAM_BOT_TOKEN"),
        chat_id=os.getenv("TELEGRAM_CHAT_ID"),
    )

    @router.post("/webhook")
    async def telegram_webhook(
        request: Request,
        x_telegram_bot_api_secret_token: Optional[str] = Header(default=None),
    ) -> Dict[str, Any]:
        expected_secret = settings.api.telegram_webhook_secret
        if expected_secret and x_telegram_bot_api_secret_token != expected_secret:
            raise HTTPException(status_code=403, detail="Invalid webhook secret")

        payload = await request.json()
        message = payload.get("message", {}) or payload.get("edited_message", {})
        text = message.get("text", "")
        chat = message.get("chat", {})
        chat_id = str(chat.get("id")) if chat else None
        if not text:
            return {"ok": True, "ignored": "no_text"}

        parsed = await boss_agent.handle_command(text)
        await service.send_message(parsed.response, chat_id=chat_id)
        return {"ok": True, "intent": parsed.intent.model_dump(), "response": parsed.response}

    @router.post("/command")
    async def local_command(payload: Dict[str, str], _auth: None = Depends(auth_guard)) -> Dict[str, Any]:
        """Local endpoint useful for testing Telegram command flow."""
        text = payload.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="Missing text")
        parsed = await boss_agent.handle_command(text)
        return {"intent": parsed.intent.model_dump(), "response": parsed.response, "payload": parsed.payload}

    return router

--- END FILE: api\telegram_api.py ---

--- START FILE: api\websocket_server.py ---
"""WebSocket manager for streaming events to dashboard clients."""

from __future__ import annotations

import json
import logging
from typing import List, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from trading_system.events.event_bus import AsyncEventBus
from trading_system.events.event_types import Event, EventType

logger = logging.getLogger(__name__)


class WebSocketBroadcaster:
    """Broadcast bus events to connected websocket clients."""

    def __init__(self, event_bus: AsyncEventBus) -> None:
        self.event_bus = event_bus
        self._clients: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._clients.add(websocket)
        logger.info("WebSocket client connected count=%s", len(self._clients))

    def disconnect(self, websocket: WebSocket) -> None:
        self._clients.discard(websocket)
        logger.info("WebSocket client disconnected count=%s", len(self._clients))

    async def broadcast(self, event: Event) -> None:
        if not self._clients:
            return
        dead: List[WebSocket] = []
        message = json.dumps(event.as_dict(), default=str)
        for ws in self._clients:
            try:
                await ws.send_text(message)
            except Exception:  # noqa: BLE001
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    def register_bus_handlers(self) -> None:
        """Subscribe broadcaster to all event types."""
        for event_type in EventType:
            self.event_bus.subscribe(event_type, self.broadcast)


def create_websocket_router(broadcaster: WebSocketBroadcaster) -> APIRouter:
    """Create websocket router."""
    router = APIRouter()

    @router.websocket("/ws/events")
    async def events_websocket(websocket: WebSocket) -> None:
        await broadcaster.connect(websocket)
        try:
            while True:
                # Keep connection alive by reading messages (ignored).
                await websocket.receive_text()
        except WebSocketDisconnect:
            broadcaster.disconnect(websocket)
        except Exception:
            broadcaster.disconnect(websocket)

    return router

--- END FILE: api\websocket_server.py ---

--- START FILE: api\__init__.py ---

--- END FILE: api\__init__.py ---

--- START FILE: config\broker_config.py ---
"""Broker adapter configuration and factory helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from trading_system.config.settings import AppSettings, BrokerCredentials


@dataclass(slots=True)
class BrokerAdapterConfig:
    """Runtime broker adapter configuration."""

    name: str
    credentials: BrokerCredentials
    supports_spot: bool = True
    supports_margin: bool = False
    supports_forex: bool = False
    supports_equities: bool = False
    ccxt_exchange_id: str | None = None


def load_broker_configs(settings: AppSettings) -> Dict[str, BrokerAdapterConfig]:
    """Build normalized adapter configs from app settings."""
    brokers = settings.brokers.brokers
    return {
        "binance": BrokerAdapterConfig(
            name="binance",
            credentials=brokers.get("binance", BrokerCredentials()),
            supports_spot=True,
            supports_margin=True,
            ccxt_exchange_id="binance",
        ),
        "alpaca": BrokerAdapterConfig(
            name="alpaca",
            credentials=brokers.get("alpaca", BrokerCredentials()),
            supports_equities=True,
            supports_spot=False,
            ccxt_exchange_id=None,
        ),
        "oanda": BrokerAdapterConfig(
            name="oanda",
            credentials=brokers.get("oanda", BrokerCredentials()),
            supports_forex=True,
            supports_spot=False,
            ccxt_exchange_id=None,
        ),
        # Upstox adapter currently a stub (execution will be rejected with a clear message)
        # until OAuth + order endpoints are wired.
        "upstox": BrokerAdapterConfig(
            name="upstox",
            credentials=brokers.get("upstox", BrokerCredentials()),
            supports_equities=True,
            supports_spot=False,
            ccxt_exchange_id=None,
        ),
    }

--- END FILE: config\broker_config.py ---

--- START FILE: config\models.py ---
"""Domain models for the trading operating system."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class TradingMode(str, Enum):
    """Execution mode for hard isolation of environments."""

    BACKTEST = "backtest"
    PAPER = "paper"
    LIVE = "live"


class OrderSide(str, Enum):
    """Side of an order."""

    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    """Supported order types."""

    MARKET = "market"
    LIMIT = "limit"


class RiskDecision(str, Enum):
    """Decision returned by Risk Guardian."""

    APPROVED = "approved"
    REJECTED = "rejected"


class CommandIntentType(str, Enum):
    """Supported natural-language command intents."""

    ANALYZE = "analyze"
    BACKTEST = "backtest"
    PLACE_ORDER = "place_order"
    WHALE_ACTIVITY = "whale_activity"
    CURRENT_RISK = "current_risk"
    APPROVE_LIVE = "approve_live"
    UNKNOWN = "unknown"


class RiskLimits(BaseModel):
    """Hard risk limits with conservative defaults."""

    max_daily_loss: float = Field(default=50.0, gt=0)
    max_exposure: float = Field(default=100.0, gt=0)
    max_leverage: float = Field(default=2.0, ge=1.0)
    max_symbol_exposure_pct: float = Field(default=20.0, gt=0, le=100)
    max_slippage_bps: float = Field(default=35.0, gt=0)
    max_consecutive_losses: int = Field(default=4, gt=0)
    max_correlation: float = Field(default=0.85, ge=0, le=1)
    min_stop_loss_pct: float = Field(default=0.2, gt=0)
    max_stop_loss_pct: float = Field(default=8.0, gt=0)


class Signal(BaseModel):
    """Trading signal emitted by research/strategy layers."""

    symbol: str
    timeframe: str
    direction: OrderSide
    confidence: float = Field(ge=0, le=1)
    source_agent: str
    reason: str
    price: float = Field(gt=0)
    strategy_id: str = Field(default="default")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OrderRequest(BaseModel):
    """Canonical order request model used across all brokers."""

    symbol: str
    side: OrderSide
    quantity: float = Field(gt=0)
    mode: TradingMode
    broker: str = Field(default="paper")
    order_type: OrderType = Field(default=OrderType.MARKET)
    limit_price: Optional[float] = Field(default=None, gt=0)
    stop_loss: Optional[float] = Field(default=None, gt=0)
    take_profit: Optional[float] = Field(default=None, gt=0)
    leverage: float = Field(default=1.0, ge=1.0)
    expected_slippage_bps: float = Field(default=10.0, ge=0)
    signal_id: Optional[str] = None
    correlation_group: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("limit_price")
    @classmethod
    def validate_limit_price_for_limit_orders(
        cls, value: Optional[float], info: Any
    ) -> Optional[float]:
        """Ensure limit price exists for limit orders."""
        order_type = info.data.get("order_type")
        if order_type == OrderType.LIMIT and value is None:
            raise ValueError("limit_price is required for limit orders")
        return value


class RiskCheckResult(BaseModel):
    """Result of risk evaluation for an order request."""

    decision: RiskDecision
    reasons: List[str] = Field(default_factory=list)
    limits: RiskLimits
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExecutionResult(BaseModel):
    """Order execution output for paper/live brokers."""

    accepted: bool
    mode: TradingMode
    broker: str
    order_id: Optional[str] = None
    symbol: str
    side: OrderSide
    quantity: float
    average_price: Optional[float] = None
    status: str = "rejected"
    message: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)
    executed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CommandIntent(BaseModel):
    """Structured intent parsed from natural-language command."""

    intent: CommandIntentType
    raw_command: str
    symbol: Optional[str] = None
    timeframe: Optional[str] = None
    lookback: Optional[str] = None
    quantity: Optional[float] = None
    mode: Optional[TradingMode] = None
    side: Optional[OrderSide] = None
    strategy: Optional[str] = None
    extra: Dict[str, Any] = Field(default_factory=dict)


class BacktestRequest(BaseModel):
    """Backtest request shape."""

    symbols: List[str]
    timeframe: str = "1d"
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    lookback_days: int = Field(default=180, gt=10)
    strategy_name: str = "ema_crossover"
    strategy_params: Dict[str, Any] = Field(default_factory=dict)
    initial_capital: float = Field(default=100000.0, gt=0)
    walk_forward_windows: int = Field(default=3, gt=0)


class BacktestMetrics(BaseModel):
    """Standard performance metrics for evaluation."""

    total_trades: int = 0
    win_rate: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    profit_factor: float = 0.0
    expectancy: float = 0.0
    net_profit: float = 0.0
    total_return_pct: float = 0.0


class BacktestResult(BaseModel):
    """Backtest result container."""

    request: BacktestRequest
    metrics: BacktestMetrics
    trades: List[Dict[str, Any]] = Field(default_factory=list)
    equity_curve: List[float] = Field(default_factory=list)
    walk_forward: List[Dict[str, Any]] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelRouteRequest(BaseModel):
    """Prompt routing input for multi-model dispatch."""

    task: str
    prompt: str
    prefer_local: bool = True
    max_tokens: int = 1200
    temperature: float = 0.1


class ModelRouteDecision(BaseModel):
    """Selected model/provider."""

    provider: str
    model: str
    reason: str


@dataclass(slots=True)
class PortfolioSnapshot:
    """Shared snapshot for risk checks and reporting."""

    mode: TradingMode
    balance: float
    available_cash: float
    daily_realized_pnl: float
    gross_exposure: float
    positions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    consecutive_losses: int = 0
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def redact_secret(value: str, visible: int = 4) -> str:
    """Redact secrets for safe logs."""
    if not value:
        return ""
    if len(value) <= visible:
        return "*" * len(value)
    hidden = "*" * (len(value) - visible)
    return f"{hidden}{value[-visible:]}"

--- END FILE: config\models.py ---

--- START FILE: config\settings.py ---
"""Application settings and dependency-safe configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from trading_system.config.models import RiskLimits, TradingMode, redact_secret


class DatabaseSettings(BaseModel):
    """Database configuration."""

    url: str = Field(default="sqlite+aiosqlite:///./trading_system/data/trading_system.db")


class RedisSettings(BaseModel):
    """Optional Redis configuration."""

    enabled: bool = False
    url: str = "redis://localhost:6379/0"


class BrokerCredentials(BaseModel):
    """Credential bag for a broker account."""

    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    passphrase: Optional[str] = None
    account_id: Optional[str] = None
    sandbox: bool = True

    def safe_dict(self) -> Dict[str, Optional[str]]:
        """Return redacted credentials for diagnostics."""
        return {
            "api_key": redact_secret(self.api_key or ""),
            "api_secret": redact_secret(self.api_secret or ""),
            "passphrase": redact_secret(self.passphrase or ""),
            "account_id": redact_secret(self.account_id or ""),
            "sandbox": str(self.sandbox),
        }


class BrokerSettings(BaseModel):
    """Top-level broker settings."""

    default_live_broker: str = "binance"
    brokers: Dict[str, BrokerCredentials] = Field(default_factory=dict)


class ModelProviderSettings(BaseModel):
    """Provider configuration for model routing."""

    name: str
    model: str
    enabled: bool = True
    base_url: Optional[str] = None
    api_key_env: Optional[str] = None
    # Local models on low-RAM laptops can take time; default to 2 minutes.
    timeout_sec: int = int(os.getenv("OLLAMA_TIMEOUT_SEC", "120"))


class ModelRoutingSettings(BaseModel):
    """Ordered routing preference."""

    local_first: bool = True
    providers: List[ModelProviderSettings] = Field(
        default_factory=lambda: [
            ModelProviderSettings(
                name="ollama",
                model=os.getenv("OLLAMA_MODEL", "qwen2.5:3b"),
                enabled=True,
                base_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
            ),
            ModelProviderSettings(
                name="ollama",
                model=os.getenv("OLLAMA_FALLBACK", "deepseek-r1:7b"),
                enabled=True,
                base_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
            ),
            ModelProviderSettings(
                name="claude", model="claude-3-5-sonnet-latest", enabled=False, api_key_env="ANTHROPIC_API_KEY"
            ),
            ModelProviderSettings(
                name="openai", model="gpt-4o-mini", enabled=False, api_key_env="OPENAI_API_KEY"
            ),
        ]
    )


class ApiSettings(BaseModel):
    """API runtime settings."""

    host: str = "0.0.0.0"
    port: int = 8000
    telegram_webhook_secret: Optional[str] = None
    require_api_key: bool = False
    api_keys: List[str] = Field(default_factory=list)
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 120
    live_approval_ttl_seconds: int = 300


class AppSettings(BaseModel):
    """Global application settings."""

    app_name: str = "Institutional Multi-Agent Trading OS"
    env: str = "dev"
    default_mode: TradingMode = TradingMode.PAPER
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    brokers: BrokerSettings = Field(default_factory=BrokerSettings)
    risk_limits: RiskLimits = Field(default_factory=RiskLimits)
    model_routing: ModelRoutingSettings = Field(default_factory=ModelRoutingSettings)
    api: ApiSettings = Field(default_factory=ApiSettings)
    watchlist: List[str] = Field(default_factory=lambda: ["BTC/USDT", "ETH/USDT", "INFY.NS"])


def _env_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.lower() in {"1", "true", "yes", "on"}


def load_settings() -> AppSettings:
    """Load settings from environment variables with safe defaults."""
    env = os.getenv("TRADING_ENV", "dev")
    default_mode = TradingMode(os.getenv("TRADING_MODE", "paper"))
    db_url = os.getenv("TRADING_DB_URL", "sqlite+aiosqlite:///./trading_system/data/trading_system.db")
    redis_enabled = _env_bool("TRADING_REDIS_ENABLED", False)
    redis_url = os.getenv("TRADING_REDIS_URL", "redis://localhost:6379/0")

    broker_settings = BrokerSettings(
        default_live_broker=os.getenv("TRADING_DEFAULT_LIVE_BROKER", "binance"),
        brokers={
            "binance": BrokerCredentials(
                api_key=os.getenv("BINANCE_API_KEY"),
                api_secret=os.getenv("BINANCE_API_SECRET"),
                sandbox=_env_bool("BINANCE_SANDBOX", True),
            ),
            "alpaca": BrokerCredentials(
                api_key=os.getenv("ALPACA_API_KEY"),
                api_secret=os.getenv("ALPACA_API_SECRET"),
                account_id=os.getenv("ALPACA_ACCOUNT_ID"),
                sandbox=_env_bool("ALPACA_SANDBOX", True),
            ),
            "oanda": BrokerCredentials(
                api_key=os.getenv("OANDA_API_KEY"),
                account_id=os.getenv("OANDA_ACCOUNT_ID"),
                sandbox=_env_bool("OANDA_SANDBOX", True),
            ),
            # Upstox credentials are present for future integration.
            # Store access token in passphrase field for now.
            "upstox": BrokerCredentials(
                api_key=os.getenv("UPSTOX_API_KEY"),
                api_secret=os.getenv("UPSTOX_API_SECRET"),
                passphrase=os.getenv("UPSTOX_ACCESS_TOKEN"),
                sandbox=False,
            ),
        },
    )

    return AppSettings(
        env=env,
        default_mode=default_mode,
        database=DatabaseSettings(url=db_url),
        redis=RedisSettings(enabled=redis_enabled, url=redis_url),
        brokers=broker_settings,
        api=ApiSettings(
            host=os.getenv("TRADING_API_HOST", "0.0.0.0"),
            port=int(os.getenv("TRADING_API_PORT", "8000")),
            telegram_webhook_secret=os.getenv("TELEGRAM_WEBHOOK_SECRET"),
            require_api_key=_env_bool("TRADING_REQUIRE_API_KEY", False),
            api_keys=[k.strip() for k in os.getenv("TRADING_API_KEYS", "").split(",") if k.strip()],
            rate_limit_enabled=_env_bool("TRADING_RATE_LIMIT_ENABLED", True),
            rate_limit_requests_per_minute=int(os.getenv("TRADING_RATE_LIMIT_RPM", "120")),
            live_approval_ttl_seconds=int(os.getenv("TRADING_LIVE_APPROVAL_TTL_SECONDS", "300")),
        ),
    )


@dataclass(slots=True)
class DependencyContainer:
    """Simple dependency injection container."""

    settings: AppSettings
    event_bus: object
    global_state: object
    trade_memory: object
    reflexion_memory: object
    vector_memory: object
    risk_guardian: object
    execution_engine: object
    boss_agent: object
    live_approval_manager: object

--- END FILE: config\settings.py ---

--- START FILE: config\__init__.py ---

--- END FILE: config\__init__.py ---

--- START FILE: events\event_bus.py ---
"""Async event bus with retry-safe dispatch."""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import Awaitable, Callable, DefaultDict, Dict, List, Optional

from trading_system.events.event_types import Event, EventType

logger = logging.getLogger(__name__)

EventHandler = Callable[[Event], Awaitable[None]]


class AsyncEventBus:
    """
    Event bus for decoupled agent communication.

    Unit-test example:
        >>> bus = AsyncEventBus()
        >>> async def handler(event): pass
        >>> bus.subscribe(EventType.SYSTEM_HEARTBEAT, handler)
    """

    def __init__(self, queue_size: int = 10000, worker_count: int = 4) -> None:
        self._handlers: DefaultDict[EventType, List[EventHandler]] = defaultdict(list)
        self._queue: asyncio.Queue[Event] = asyncio.Queue(maxsize=queue_size)
        self._worker_count = worker_count
        self._workers: List[asyncio.Task[None]] = []
        self._running = False

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Register event handler."""
        self._handlers[event_type].append(handler)
        logger.debug("Subscribed handler=%s event=%s", handler.__name__, event_type.value)

    async def publish(self, event: Event) -> None:
        """Publish event to queue with backpressure."""
        if not self._running:
            logger.warning("Event bus not running; event queued lazily event=%s", event.event_type.value)
        await self._queue.put(event)

    async def start(self) -> None:
        """Start worker tasks."""
        if self._running:
            return
        self._running = True
        self._workers = [asyncio.create_task(self._worker_loop(i)) for i in range(self._worker_count)]
        logger.info("Event bus started workers=%s", self._worker_count)

    async def stop(self) -> None:
        """Stop worker tasks gracefully."""
        if not self._running:
            return
        self._running = False
        for _ in self._workers:
            await self._queue.put(
                Event(
                    event_type=EventType.SYSTEM_HEARTBEAT,
                    source="event_bus.stop",
                    payload={"stop": True},
                )
            )
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
        logger.info("Event bus stopped")

    async def _worker_loop(self, worker_id: int) -> None:
        """Background event dispatcher loop."""
        while True:
            event = await self._queue.get()
            try:
                if not self._running and event.payload.get("stop"):
                    return
                await self._dispatch(event)
            except Exception:
                logger.exception("Event dispatch failed event=%s worker=%s", event.event_type.value, worker_id)
            finally:
                self._queue.task_done()

    async def _dispatch(self, event: Event) -> None:
        """Dispatch event to all handlers concurrently."""
        handlers = self._handlers.get(event.event_type, [])
        if not handlers:
            logger.debug("No handlers for event=%s", event.event_type.value)
            return
        await asyncio.gather(*(handler(event) for handler in handlers), return_exceptions=False)

    def stats(self) -> Dict[str, int]:
        """Queue metrics."""
        return {"queue_size": self._queue.qsize(), "worker_count": len(self._workers)}

--- END FILE: events\event_bus.py ---

--- START FILE: events\event_handlers.py ---
"""Reusable event handlers for logging and state updates."""

from __future__ import annotations

import logging
from typing import Awaitable, Callable

from trading_system.events.event_bus import AsyncEventBus
from trading_system.events.event_types import Event, EventType
from trading_system.memory.global_state import GlobalState
from trading_system.memory.trade_memory import TradeMemoryRepository

logger = logging.getLogger(__name__)


async def log_all_events(event: Event) -> None:
    """Structured event logging handler."""
    logger.info("Event=%s source=%s payload=%s", event.event_type.value, event.source, event.payload)


async def on_kill_switch(event: Event) -> None:
    """Escalation logging for kill switch triggers."""
    logger.error("KILL SWITCH TRIGGERED: %s", event.payload)


def register_default_handlers(
    bus: AsyncEventBus,
    state: GlobalState,
    trade_memory: TradeMemoryRepository,
) -> None:
    """Register default handlers used by orchestration layer."""

    async def trade_executed_handler(event: Event) -> None:
        logger.info("Trade executed event received: %s", event.payload.get("order_id"))

    async def position_closed_handler(event: Event) -> None:
        logger.info("Position closed: %s", event.payload.get("symbol"))

    bus.subscribe(EventType.SIGNAL_DETECTED, log_all_events)
    bus.subscribe(EventType.RISK_APPROVED, log_all_events)
    bus.subscribe(EventType.RISK_REJECTED, log_all_events)
    bus.subscribe(EventType.TRADE_EXECUTED, trade_executed_handler)
    bus.subscribe(EventType.POSITION_CLOSED, position_closed_handler)
    bus.subscribe(EventType.WHALE_ALERT, log_all_events)
    bus.subscribe(EventType.MACRO_ALERT, log_all_events)
    bus.subscribe(EventType.KILL_SWITCH_TRIGGERED, on_kill_switch)

--- END FILE: events\event_handlers.py ---

--- START FILE: events\event_types.py ---
"""Event contracts for the system event bus."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


class EventType(str, Enum):
    """Canonical event names."""

    SIGNAL_DETECTED = "SignalDetected"
    RISK_APPROVED = "RiskApproved"
    TRADE_EXECUTED = "TradeExecuted"
    POSITION_CLOSED = "PositionClosed"
    KILL_SWITCH_TRIGGERED = "KillSwitchTriggered"
    WHALE_ALERT = "WhaleAlert"
    MACRO_ALERT = "MacroAlert"
    RISK_REJECTED = "RiskRejected"
    SYSTEM_HEARTBEAT = "SystemHeartbeat"


@dataclass(slots=True)
class Event:
    """Base event envelope."""

    event_type: EventType
    source: str
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def as_dict(self) -> Dict[str, Any]:
        """Serialize event."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "source": self.source,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "occurred_at": self.occurred_at.isoformat(),
        }


def build_event(
    event_type: EventType,
    source: str,
    payload: Dict[str, Any],
    correlation_id: Optional[str] = None,
) -> Event:
    """Factory helper for typed events."""
    return Event(
        event_type=event_type,
        source=source,
        payload=payload,
        correlation_id=correlation_id,
    )

--- END FILE: events\event_types.py ---

--- START FILE: events\__init__.py ---

--- END FILE: events\__init__.py ---

--- START FILE: execution\broker_router.py ---
"""Multi-broker execution routing with retries and balance checks."""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol

import aiohttp

from trading_system.config.broker_config import BrokerAdapterConfig
from trading_system.config.models import ExecutionResult, OrderRequest, TradingMode

logger = logging.getLogger(__name__)


class BrokerAdapter(Protocol):
    """Protocol for broker implementations."""

    async def get_balance(self) -> Dict[str, Any]:
        """Return account balance payload."""

    async def place_order(self, order: OrderRequest) -> ExecutionResult:
        """Place order and return normalized result."""

    async def fetch_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Fetch order status."""


@dataclass(slots=True)
class RetryPolicy:
    """Retry policy for broker calls."""

    retries: int = 3
    initial_backoff_sec: float = 0.5


class BinanceCcxtAdapter:
    """CCXT adapter for Binance."""

    def __init__(self, config: BrokerAdapterConfig) -> None:
        self.config = config
        self._exchange: Any = None

    async def _ensure_exchange(self) -> Any:
        if self._exchange is not None:
            return self._exchange
        try:
            import ccxt.async_support as ccxt_async  # type: ignore
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError("ccxt is required for Binance live execution") from exc
        exchange_cls = getattr(ccxt_async, self.config.ccxt_exchange_id or "binance")
        self._exchange = exchange_cls(
            {
                "apiKey": self.config.credentials.api_key,
                "secret": self.config.credentials.api_secret,
                "enableRateLimit": True,
            }
        )
        if self.config.credentials.sandbox:
            await self._exchange.set_sandbox_mode(True)
        return self._exchange

    async def get_balance(self) -> Dict[str, Any]:
        ex = await self._ensure_exchange()
        return await ex.fetch_balance()

    async def place_order(self, order: OrderRequest) -> ExecutionResult:
        ex = await self._ensure_exchange()
        if order.order_type.value == "limit":
            response = await ex.create_limit_order(
                symbol=order.symbol,
                side=order.side.value,
                amount=order.quantity,
                price=order.limit_price,
            )
        else:
            response = await ex.create_market_order(
                symbol=order.symbol,
                side=order.side.value,
                amount=order.quantity,
            )
        return ExecutionResult(
            accepted=True,
            mode=order.mode,
            broker="binance",
            order_id=str(response.get("id")),
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            average_price=float(response.get("average") or response.get("price") or 0.0),
            status=str(response.get("status") or "submitted"),
            message="Live order submitted via Binance",
            metadata={"raw": response},
        )

    async def fetch_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        ex = await self._ensure_exchange()
        return await ex.fetch_order(order_id, symbol)


class AlpacaAdapter:
    """REST adapter for Alpaca."""

    BASE_URL = "https://paper-api.alpaca.markets"
    LIVE_URL = "https://api.alpaca.markets"

    def __init__(self, config: BrokerAdapterConfig) -> None:
        self.config = config

    @property
    def _url(self) -> str:
        return self.BASE_URL if self.config.credentials.sandbox else self.LIVE_URL

    def _headers(self) -> Dict[str, str]:
        return {
            "APCA-API-KEY-ID": self.config.credentials.api_key or "",
            "APCA-API-SECRET-KEY": self.config.credentials.api_secret or "",
            "Content-Type": "application/json",
        }

    async def get_balance(self) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self._url}/v2/account", headers=self._headers()) as response:
                response.raise_for_status()
                return await response.json()

    async def place_order(self, order: OrderRequest) -> ExecutionResult:
        payload = {
            "symbol": order.symbol.replace("/", ""),
            "qty": str(order.quantity),
            "side": order.side.value,
            "type": order.order_type.value,
            "time_in_force": "day",
        }
        if order.order_type.value == "limit":
            payload["limit_price"] = str(order.limit_price)
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self._url}/v2/orders", headers=self._headers(), json=payload) as response:
                response.raise_for_status()
                data = await response.json()
        return ExecutionResult(
            accepted=True,
            mode=order.mode,
            broker="alpaca",
            order_id=str(data.get("id")),
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            average_price=float(data.get("filled_avg_price") or 0.0),
            status=str(data.get("status") or "submitted"),
            message="Live order submitted via Alpaca",
            metadata={"raw": data},
        )

    async def fetch_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self._url}/v2/orders/{order_id}", headers=self._headers()) as response:
                response.raise_for_status()
                return await response.json()


class UpstoxAdapter:
    """Upstox adapter (stub).

    Upstox requires OAuth and an access token. Until the order + positions
    endpoints are wired, we fail safely with a clear message.
    """

    def __init__(self, config: BrokerAdapterConfig) -> None:
        self.config = config

    async def get_balance(self) -> Dict[str, Any]:
        # Placeholder: return unknown. BrokerRouter balance guard will not block
        # when available cash cannot be inferred.
        return {"available": None, "message": "Upstox balance not implemented"}

    async def place_order(self, order: OrderRequest) -> ExecutionResult:
        token = (self.config.credentials.passphrase or "").strip()
        if not (self.config.credentials.api_key and token):
            return ExecutionResult(
                accepted=False,
                mode=TradingMode.LIVE,
                broker="upstox",
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                status="rejected",
                message="Upstox credentials missing. Set UPSTOX_API_KEY and UPSTOX_ACCESS_TOKEN in .env.",
            )
        return ExecutionResult(
            accepted=False,
            mode=TradingMode.LIVE,
            broker="upstox",
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            status="not_implemented",
            message="Upstox adapter not implemented yet (OAuth + order endpoints required).",
            metadata={"hint": "Use broker=binance or broker=alpaca for live execution until wired."},
        )

    async def fetch_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        return {
            "status": "unknown",
            "message": "Upstox fetch_order not implemented",
            "order_id": order_id,
            "symbol": symbol,
        }


class OandaAdapter:
    """REST adapter for OANDA."""

    PRACTICE_URL = "https://api-fxpractice.oanda.com"
    LIVE_URL = "https://api-fxtrade.oanda.com"

    def __init__(self, config: BrokerAdapterConfig) -> None:
        self.config = config

    @property
    def _url(self) -> str:
        return self.PRACTICE_URL if self.config.credentials.sandbox else self.LIVE_URL

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.config.credentials.api_key or ''}",
            "Content-Type": "application/json",
        }

    async def get_balance(self) -> Dict[str, Any]:
        account_id = self.config.credentials.account_id or ""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self._url}/v3/accounts/{account_id}/summary", headers=self._headers()) as response:
                response.raise_for_status()
                return await response.json()

    async def place_order(self, order: OrderRequest) -> ExecutionResult:
        account_id = self.config.credentials.account_id or ""
        payload = {
            "order": {
                "type": "MARKET" if order.order_type.value == "market" else "LIMIT",
                "instrument": order.symbol.replace("/", "_"),
                "units": str(order.quantity if order.side.value == "buy" else -order.quantity),
                "timeInForce": "FOK",
                "positionFill": "DEFAULT",
            }
        }
        if order.order_type.value == "limit":
            payload["order"]["price"] = str(order.limit_price)
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self._url}/v3/accounts/{account_id}/orders",
                headers=self._headers(),
                json=payload,
            ) as response:
                response.raise_for_status()
                data = await response.json()
        fill = data.get("orderFillTransaction", {})
        return ExecutionResult(
            accepted=True,
            mode=order.mode,
            broker="oanda",
            order_id=str(fill.get("id", data.get("orderCreateTransaction", {}).get("id"))),
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            average_price=float(fill.get("price") or 0.0),
            status="filled" if fill else "submitted",
            message="Live order submitted via OANDA",
            metadata={"raw": data},
        )

    async def fetch_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        account_id = self.config.credentials.account_id or ""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self._url}/v3/accounts/{account_id}/orders/{order_id}",
                headers=self._headers(),
            ) as response:
                response.raise_for_status()
                return await response.json()


class BrokerRouter:
    """Route live orders to target broker adapters with retry and tracking."""

    def __init__(
        self,
        adapters: Dict[str, BrokerAdapter],
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        self.adapters = adapters
        self.retry_policy = retry_policy or RetryPolicy()
        self.order_registry: Dict[str, Dict[str, Any]] = {}

    async def execute_live_order(self, order: OrderRequest) -> ExecutionResult:
        """Execute order on selected live broker."""
        broker = order.broker.lower()
        adapter = self.adapters.get(broker)
        if not adapter:
            return ExecutionResult(
                accepted=False,
                mode=TradingMode.LIVE,
                broker=broker,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                status="rejected",
                message=f"Unsupported broker: {broker}",
            )
        balance_ok, reason = await self._check_balance(adapter, order)
        if not balance_ok:
            return ExecutionResult(
                accepted=False,
                mode=TradingMode.LIVE,
                broker=broker,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                status="rejected",
                message=reason,
            )

        backoff = self.retry_policy.initial_backoff_sec
        last_error: Optional[Exception] = None
        for _ in range(self.retry_policy.retries):
            try:
                result = await adapter.place_order(order)
                order_id = result.order_id or f"LIVE-{uuid.uuid4().hex[:10]}"
                self.order_registry[order_id] = {
                    "broker": broker,
                    "symbol": order.symbol,
                    "submitted_at": order.submitted_at.isoformat(),
                    "status": result.status,
                }
                return result
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                logger.exception("Live order attempt failed broker=%s symbol=%s", broker, order.symbol)
                await asyncio.sleep(backoff)
                backoff *= 2
        return ExecutionResult(
            accepted=False,
            mode=TradingMode.LIVE,
            broker=broker,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            status="error",
            message=f"Live order failed after retries: {last_error}",
        )

    async def order_status(self, broker: str, order_id: str, symbol: str) -> Dict[str, Any]:
        """Get order status from broker."""
        adapter = self.adapters.get(broker.lower())
        if not adapter:
            return {"status": "unknown", "message": "Unsupported broker"}
        return await adapter.fetch_order(order_id=order_id, symbol=symbol)

    async def _check_balance(self, adapter: BrokerAdapter, order: OrderRequest) -> tuple[bool, str]:
        """Balance check guard before order placement."""
        try:
            balance = await adapter.get_balance()
        except Exception as exc:  # noqa: BLE001
            return False, f"Balance check failed: {exc}"
        # Heuristic fields across brokers.
        possible = [
            balance.get("free", {}).get("USDT"),
            balance.get("cash"),
            balance.get("available"),
            balance.get("account", {}).get("cash"),
            balance.get("account", {}).get("NAV"),
        ]
        available = next((float(v) for v in possible if v is not None), None)
        est_notional = float(order.metadata.get("mark_price", 0) or order.limit_price or 0) * order.quantity
        if order.side.value == "buy" and available is not None and est_notional > available:
            return False, f"Insufficient balance. available={available:.2f} required~{est_notional:.2f}"
        return True, "ok"

--- END FILE: execution\broker_router.py ---

--- START FILE: execution\execution_engine.py ---
"""Execution engine coordinating risk checks and broker/paper execution."""

from __future__ import annotations

import logging
from dataclasses import asdict
from typing import Dict, Optional

from trading_system.agents.risk_guardian import CorrelationContext, RiskGuardian
from trading_system.config.models import ExecutionResult, OrderRequest, RiskDecision, TradingMode
from trading_system.events.event_bus import AsyncEventBus
from trading_system.events.event_types import EventType, build_event
from trading_system.execution.live_approval import LiveApprovalManager
from trading_system.execution.kill_switch import KillSwitch
from trading_system.execution.live_executor import LiveExecutor
from trading_system.execution.paper_executor import PaperExecutor
from trading_system.memory.global_state import GlobalState
from trading_system.memory.trade_memory import TradeMemoryRepository

logger = logging.getLogger(__name__)


class ExecutionEngine:
    """Risk-gated execution coordinator."""

    def __init__(
        self,
        risk_guardian: RiskGuardian,
        kill_switch: KillSwitch,
        paper_executor: PaperExecutor,
        live_executor: LiveExecutor,
        global_state: GlobalState,
        trade_memory: TradeMemoryRepository,
        event_bus: AsyncEventBus,
        live_approval_manager: LiveApprovalManager | None = None,
        require_live_approval_ticket: bool = True,
    ) -> None:
        self.risk_guardian = risk_guardian
        self.kill_switch = kill_switch
        self.paper_executor = paper_executor
        self.live_executor = live_executor
        self.global_state = global_state
        self.trade_memory = trade_memory
        self.event_bus = event_bus
        self.live_approval_manager = live_approval_manager
        self.require_live_approval_ticket = require_live_approval_ticket
        self._peak_equity: Dict[str, float] = {
            TradingMode.PAPER.value: 0.0,
            TradingMode.LIVE.value: 0.0,
        }

    async def submit_order(
        self,
        order: OrderRequest,
        human_approved: bool = False,
        correlation_matrix: Optional[Dict[str, float]] = None,
    ) -> ExecutionResult:
        """
        Submit order after strict risk validation.

        Safety requirements:
        - Backtest mode cannot execute.
        - Risk guardian veto is final.
        - Live mode needs human approval.
        """
        live_approval_validated = False
        if order.mode == TradingMode.BACKTEST:
            result = ExecutionResult(
                accepted=False,
                mode=TradingMode.BACKTEST,
                broker=order.broker,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                status="rejected",
                message="Backtest mode never routes to execution.",
            )
            await self._safe_log_execution(result)
            return result
        if order.mode == TradingMode.LIVE and self.require_live_approval_ticket:
            ticket_id = str(order.metadata.get("approval_ticket_id", "")).strip()
            if not ticket_id or not self.live_approval_manager:
                result = ExecutionResult(
                    accepted=False,
                    mode=TradingMode.LIVE,
                    broker=order.broker,
                    symbol=order.symbol,
                    side=order.side,
                    quantity=order.quantity,
                    status="rejected",
                    message="Live order requires approval_ticket_id.",
                )
                await self._safe_log_execution(result)
                return result
            approved = await self.live_approval_manager.consume_for_order(ticket_id=ticket_id, order=order)
            if not approved:
                result = ExecutionResult(
                    accepted=False,
                    mode=TradingMode.LIVE,
                    broker=order.broker,
                    symbol=order.symbol,
                    side=order.side,
                    quantity=order.quantity,
                    status="rejected",
                    message="Live approval ticket invalid, expired, or mismatched.",
                )
                await self._safe_log_execution(result)
                return result
            live_approval_validated = True
        if self.kill_switch.is_active:
            await self.event_bus.publish(
                build_event(
                    event_type=EventType.KILL_SWITCH_TRIGGERED,
                    source="execution_engine",
                    payload={"state": asdict(self.kill_switch.state)},
                )
            )
            result = ExecutionResult(
                accepted=False,
                mode=order.mode,
                broker=order.broker,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                status="rejected",
                message="Kill switch active.",
            )
            await self._safe_log_execution(result)
            return result

        snapshot = await self.global_state.snapshot(order.mode)
        correlation = CorrelationContext(matrix=correlation_matrix or {})
        risk_result = self.risk_guardian.validate_order(
            order=order,
            snapshot=snapshot,
            correlation_context=correlation,
            kill_switch_active=self.kill_switch.is_active,
        )

        if risk_result.decision == RiskDecision.REJECTED:
            await self.event_bus.publish(
                build_event(
                    event_type=EventType.RISK_REJECTED,
                    source="risk_guardian",
                    payload={
                        "symbol": order.symbol,
                        "mode": order.mode.value,
                        "reasons": risk_result.reasons,
                        "submitted_at": order.submitted_at.isoformat(),
                    },
                )
            )
            result = ExecutionResult(
                accepted=False,
                mode=order.mode,
                broker=order.broker,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                status="rejected",
                message="Risk rejected: " + "; ".join(risk_result.reasons),
            )
            await self._safe_log_execution(result)
            return result

        await self.event_bus.publish(
            build_event(
                event_type=EventType.RISK_APPROVED,
                source="risk_guardian",
                payload={
                    "symbol": order.symbol,
                    "mode": order.mode.value,
                    "submitted_at": order.submitted_at.isoformat(),
                },
            )
        )

        if order.mode == TradingMode.PAPER:
            result = await self.paper_executor.execute(order)
        else:
            result = await self.live_executor.execute(
                order,
                human_approved=(human_approved or live_approval_validated),
            )

        if result.accepted:
            await self.event_bus.publish(
                build_event(
                    event_type=EventType.TRADE_EXECUTED,
                    source="execution_engine",
                    payload=result.model_dump(),
                )
            )
            self.kill_switch.register_success()
            post_snapshot = await self.global_state.snapshot(order.mode)
            mode_key = order.mode.value
            self._peak_equity[mode_key] = max(self._peak_equity.get(mode_key, 0.0), post_snapshot.balance)
            self.kill_switch.evaluate_drawdown(self._peak_equity[mode_key], post_snapshot.balance)
            self.kill_switch.evaluate_losses(post_snapshot.consecutive_losses)
        else:
            self.kill_switch.register_api_failure(result.message or "execution rejected")
            await self._safe_log_execution(result)
            if self.kill_switch.is_active:
                await self.event_bus.publish(
                    build_event(
                        event_type=EventType.KILL_SWITCH_TRIGGERED,
                        source="execution_engine.api_failure",
                        payload={"state": asdict(self.kill_switch.state)},
                    )
                )
        return result

    async def _safe_log_execution(self, result: ExecutionResult) -> None:
        """Persist execution outcome without breaking control flow."""
        try:
            await self.trade_memory.log_execution(result)
        except Exception:  # noqa: BLE001
            logger.exception("Failed to persist execution audit trail")

--- END FILE: execution\execution_engine.py ---

--- START FILE: execution\kill_switch.py ---
"""System-wide kill switch logic."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class KillSwitchReason(str, Enum):
    """Supported kill switch trigger reasons."""

    ABNORMAL_VOLATILITY = "abnormal_volatility"
    API_FAILURE = "api_failure"
    DRAWDOWN_EXCEEDED = "drawdown_exceeded"
    CONSECUTIVE_LOSSES = "consecutive_losses"
    MANUAL = "manual"


@dataclass(slots=True)
class KillSwitchState:
    """Kill switch state record."""

    active: bool = False
    reason: Optional[KillSwitchReason] = None
    details: Dict[str, Any] | None = None
    triggered_at: Optional[datetime] = None


class KillSwitch:
    """Centralized safety interlock for all execution modes except backtest."""

    def __init__(
        self,
        max_drawdown_pct: float = 10.0,
        max_consecutive_losses: int = 5,
        max_api_failures: int = 5,
        abnormal_volatility_pct: float = 6.0,
    ) -> None:
        self.max_drawdown_pct = max_drawdown_pct
        self.max_consecutive_losses = max_consecutive_losses
        self.max_api_failures = max_api_failures
        self.abnormal_volatility_pct = abnormal_volatility_pct
        self._state = KillSwitchState()
        self._api_failures = 0

    @property
    def is_active(self) -> bool:
        """Whether switch is currently active."""
        return self._state.active

    @property
    def state(self) -> KillSwitchState:
        """Return full state."""
        return self._state

    def trigger(self, reason: KillSwitchReason, details: Optional[Dict[str, Any]] = None) -> None:
        """Trigger and lock the kill switch."""
        if self._state.active:
            return
        self._state = KillSwitchState(
            active=True,
            reason=reason,
            details=details or {},
            triggered_at=datetime.now(timezone.utc),
        )
        logger.error("Kill switch triggered reason=%s details=%s", reason.value, details)

    def reset(self) -> None:
        """Manual reset (human-supervised action)."""
        logger.warning("Kill switch reset requested")
        self._state = KillSwitchState()
        self._api_failures = 0

    def register_api_failure(self, error: str) -> None:
        """Track API failures and trigger if threshold exceeded."""
        self._api_failures += 1
        if self._api_failures >= self.max_api_failures:
            self.trigger(
                KillSwitchReason.API_FAILURE,
                {"api_failures": self._api_failures, "last_error": error},
            )

    def register_success(self) -> None:
        """Reset API failure streak on successful call."""
        self._api_failures = 0

    def evaluate_drawdown(self, peak_equity: float, current_equity: float) -> None:
        """Trigger if drawdown exceeds configured threshold."""
        if peak_equity <= 0:
            return
        drawdown_pct = ((peak_equity - current_equity) / peak_equity) * 100
        if drawdown_pct >= self.max_drawdown_pct:
            self.trigger(
                KillSwitchReason.DRAWDOWN_EXCEEDED,
                {"drawdown_pct": drawdown_pct, "peak_equity": peak_equity, "current_equity": current_equity},
            )

    def evaluate_losses(self, consecutive_losses: int) -> None:
        """Trigger on consecutive losses."""
        if consecutive_losses >= self.max_consecutive_losses:
            self.trigger(
                KillSwitchReason.CONSECUTIVE_LOSSES,
                {"consecutive_losses": consecutive_losses},
            )

    def evaluate_volatility(self, move_pct: float, symbol: str) -> None:
        """Trigger on abnormal volatility spikes."""
        if abs(move_pct) >= self.abnormal_volatility_pct:
            self.trigger(
                KillSwitchReason.ABNORMAL_VOLATILITY,
                {"symbol": symbol, "move_pct": move_pct},
            )

    def manual_trigger(self, note: str) -> None:
        """Manual operator trigger."""
        self.trigger(KillSwitchReason.MANUAL, {"note": note})

--- END FILE: execution\kill_switch.py ---

--- START FILE: execution\live_approval.py ---
"""Human-supervised one-time live order approvals."""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from trading_system.config.models import OrderRequest, TradingMode

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class LiveApprovalTicket:
    """Approval ticket bound to one live order fingerprint."""

    ticket_id: str
    fingerprint: str
    order_preview: Dict[str, Any]
    requested_by: str
    requested_at: datetime
    expires_at: datetime
    approved: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    consumed: bool = False
    consumed_at: Optional[datetime] = None


class LiveApprovalManager:
    """Manages issue/approve/consume lifecycle for live order tickets."""

    def __init__(self, ttl_seconds: int = 300) -> None:
        self.ttl_seconds = ttl_seconds
        self._tickets: Dict[str, LiveApprovalTicket] = {}
        self._lock = asyncio.Lock()

    def fingerprint(self, order: OrderRequest) -> str:
        """Create stable order fingerprint used by approval tickets."""
        payload = {
            "symbol": order.symbol,
            "side": order.side.value,
            "quantity": round(float(order.quantity), 10),
            "mode": order.mode.value,
            "broker": order.broker.lower(),
            "order_type": order.order_type.value,
            "limit_price": order.limit_price,
            "stop_loss": order.stop_loss,
            "take_profit": order.take_profit,
            "leverage": round(float(order.leverage), 8),
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    async def create_ticket(self, order: OrderRequest, requested_by: str = "operator") -> Dict[str, Any]:
        """Create one approval ticket for a live order."""
        if order.mode != TradingMode.LIVE:
            raise ValueError("Live approval tickets can only be created for live orders.")
        now = datetime.now(timezone.utc)
        ticket_id = f"LIVEAP-{uuid.uuid4().hex[:12]}"
        ticket = LiveApprovalTicket(
            ticket_id=ticket_id,
            fingerprint=self.fingerprint(order),
            order_preview=order.model_dump(mode="json"),
            requested_by=requested_by,
            requested_at=now,
            expires_at=now + timedelta(seconds=self.ttl_seconds),
        )
        async with self._lock:
            self._tickets[ticket_id] = ticket
        return self._ticket_dict(ticket)

    async def approve_ticket(self, ticket_id: str, approved_by: str = "supervisor") -> Dict[str, Any]:
        """Approve a pending ticket."""
        async with self._lock:
            ticket = self._tickets.get(ticket_id)
            if not ticket:
                raise ValueError("Approval ticket not found.")
            if self._expired(ticket):
                raise ValueError("Approval ticket expired.")
            if ticket.consumed:
                raise ValueError("Approval ticket already consumed.")
            ticket.approved = True
            ticket.approved_by = approved_by
            ticket.approved_at = datetime.now(timezone.utc)
            return self._ticket_dict(ticket)

    async def consume_for_order(self, ticket_id: str, order: OrderRequest) -> bool:
        """Consume ticket if approved and order fingerprint matches exactly."""
        expected = self.fingerprint(order)
        async with self._lock:
            ticket = self._tickets.get(ticket_id)
            if not ticket:
                return False
            if self._expired(ticket) or ticket.consumed or not ticket.approved:
                return False
            if not hmac.compare_digest(ticket.fingerprint, expected):
                return False
            ticket.consumed = True
            ticket.consumed_at = datetime.now(timezone.utc)
            return True

    async def get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Get ticket by id."""
        async with self._lock:
            ticket = self._tickets.get(ticket_id)
            if not ticket:
                return None
            return self._ticket_dict(ticket)

    async def cleanup_expired(self) -> int:
        """Delete expired tickets to bound memory."""
        removed = 0
        now = datetime.now(timezone.utc)
        async with self._lock:
            stale = [k for k, v in self._tickets.items() if v.expires_at <= now]
            for key in stale:
                self._tickets.pop(key, None)
                removed += 1
        return removed

    def _expired(self, ticket: LiveApprovalTicket) -> bool:
        return ticket.expires_at <= datetime.now(timezone.utc)

    def _ticket_dict(self, ticket: LiveApprovalTicket) -> Dict[str, Any]:
        return {
            "ticket_id": ticket.ticket_id,
            "fingerprint": ticket.fingerprint,
            "requested_by": ticket.requested_by,
            "requested_at": ticket.requested_at.isoformat(),
            "expires_at": ticket.expires_at.isoformat(),
            "approved": ticket.approved,
            "approved_by": ticket.approved_by,
            "approved_at": ticket.approved_at.isoformat() if ticket.approved_at else None,
            "consumed": ticket.consumed,
            "consumed_at": ticket.consumed_at.isoformat() if ticket.consumed_at else None,
            "order_preview": ticket.order_preview,
        }

--- END FILE: execution\live_approval.py ---

--- START FILE: execution\live_executor.py ---
"""Live execution adapter requiring explicit human approval."""

from __future__ import annotations

import logging

from trading_system.config.models import ExecutionResult, OrderRequest, TradingMode
from trading_system.execution.broker_router import BrokerRouter
from trading_system.memory.trade_memory import TradeMemoryRepository

logger = logging.getLogger(__name__)


class LiveExecutor:
    """Thin wrapper over broker router with approval gate."""

    def __init__(self, broker_router: BrokerRouter, trade_memory: TradeMemoryRepository) -> None:
        self.broker_router = broker_router
        self.trade_memory = trade_memory

    async def execute(self, order: OrderRequest, human_approved: bool) -> ExecutionResult:
        """Execute a live order after approval verification."""
        if order.mode != TradingMode.LIVE:
            return ExecutionResult(
                accepted=False,
                mode=order.mode,
                broker=order.broker,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                status="rejected",
                message="Live executor only accepts live mode orders.",
            )
        if not human_approved:
            return ExecutionResult(
                accepted=False,
                mode=TradingMode.LIVE,
                broker=order.broker,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                status="pending_approval",
                message="Live mode requires explicit human approval.",
            )
        result = await self.broker_router.execute_live_order(order)
        await self.trade_memory.log_execution(result)
        return result

--- END FILE: execution\live_executor.py ---

--- START FILE: execution\paper_executor.py ---
"""Paper execution engine isolated from live exchanges."""

from __future__ import annotations

import logging
import uuid
from typing import Any, Dict

from trading_system.config.models import ExecutionResult, OrderRequest, TradingMode
from trading_system.memory.global_state import GlobalState, Position
from trading_system.memory.trade_memory import TradeMemoryRepository

logger = logging.getLogger(__name__)


class PaperExecutor:
    """Simulated order executor with deterministic fills."""

    def __init__(self, global_state: GlobalState, trade_memory: TradeMemoryRepository) -> None:
        self.global_state = global_state
        self.trade_memory = trade_memory
        self.fee_bps = 2.0
        self.slippage_bps = 2.0

    async def execute(self, order: OrderRequest) -> ExecutionResult:
        """Execute one paper order."""
        if order.mode != TradingMode.PAPER:
            return ExecutionResult(
                accepted=False,
                mode=order.mode,
                broker="paper",
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                status="rejected",
                message="Paper executor only accepts paper mode orders.",
            )
        mark_price = float(order.metadata.get("mark_price", 0.0) or order.limit_price or 100.0)
        fill_price = self._fill_price(mark_price, order.side.value)
        order_id = f"PAPER-{uuid.uuid4().hex[:12]}"

        await self._apply_position(order, fill_price)

        result = ExecutionResult(
            accepted=True,
            mode=TradingMode.PAPER,
            broker="paper",
            order_id=order_id,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            average_price=fill_price,
            status="filled",
            message="Paper order executed in simulation.",
            metadata={"simulated": True},
        )
        await self.trade_memory.log_execution(result)
        return result

    async def _apply_position(self, order: OrderRequest, fill_price: float) -> None:
        """Update global state positions and cash."""
        current = await self.global_state.get_position(order.symbol, TradingMode.PAPER)
        qty = order.quantity
        notional = qty * fill_price
        side = order.side.value

        if side == "buy":
            await self.global_state.adjust_cash_and_balance(mode=TradingMode.PAPER, cash_delta=-notional, pnl_delta=0.0)
            if current and current.side == "buy":
                new_qty = current.quantity + qty
                new_avg = ((current.avg_price * current.quantity) + (fill_price * qty)) / new_qty
                current.quantity = new_qty
                current.avg_price = new_avg
                await self.global_state.upsert_position(current)
            elif current and current.side == "sell":
                close_qty = min(qty, current.quantity)
                pnl = (current.avg_price - fill_price) * close_qty
                current.quantity -= close_qty
                await self.global_state.adjust_cash_and_balance(mode=TradingMode.PAPER, cash_delta=0.0, pnl_delta=pnl)
                if current.quantity <= 0:
                    await self.global_state.remove_position(order.symbol, TradingMode.PAPER)
                else:
                    await self.global_state.upsert_position(current)
            else:
                await self.global_state.upsert_position(
                    Position(
                        symbol=order.symbol,
                        quantity=qty,
                        avg_price=fill_price,
                        side="buy",
                        mode=TradingMode.PAPER,
                    )
                )
            return

        # Sell side
        await self.global_state.adjust_cash_and_balance(mode=TradingMode.PAPER, cash_delta=notional, pnl_delta=0.0)
        if current and current.side == "sell":
            new_qty = current.quantity + qty
            new_avg = ((current.avg_price * current.quantity) + (fill_price * qty)) / new_qty
            current.quantity = new_qty
            current.avg_price = new_avg
            await self.global_state.upsert_position(current)
        elif current and current.side == "buy":
            close_qty = min(qty, current.quantity)
            pnl = (fill_price - current.avg_price) * close_qty
            current.quantity -= close_qty
            await self.global_state.adjust_cash_and_balance(mode=TradingMode.PAPER, cash_delta=0.0, pnl_delta=pnl)
            if current.quantity <= 0:
                await self.global_state.remove_position(order.symbol, TradingMode.PAPER)
            else:
                await self.global_state.upsert_position(current)
        else:
            await self.global_state.upsert_position(
                Position(
                    symbol=order.symbol,
                    quantity=qty,
                    avg_price=fill_price,
                    side="sell",
                    mode=TradingMode.PAPER,
                )
            )

    def _fill_price(self, mark_price: float, side: str) -> float:
        fee = self.fee_bps / 10000
        slip = self.slippage_bps / 10000
        if side == "buy":
            return mark_price * (1 + fee + slip)
        return mark_price * (1 - fee - slip)

--- END FILE: execution\paper_executor.py ---

--- START FILE: execution\persistent_live_approval.py ---
"""SQLite-backed live approval tickets shared across agent processes.

Why:
- The original LiveApprovalManager keeps tickets in memory, so approvals made in
  one process (BossAgent) are invisible to another (TradeExecutionAgent).
- This manager persists tickets in a local SQLite DB so multiple processes can
  create/approve/consume the same ticket safely.
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from trading_system.config.models import OrderRequest, TradingMode

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class LiveApprovalTicket:
    ticket_id: str
    fingerprint: str
    order_preview: Dict[str, Any]
    requested_by: str
    requested_at: datetime
    expires_at: datetime
    approved: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    consumed: bool = False
    consumed_at: Optional[datetime] = None


class PersistentLiveApprovalManager:
    """DB-backed implementation of the live approval workflow."""

    def __init__(self, sqlite_path: str, ttl_seconds: int = 300) -> None:
        self.sqlite_path = str(Path(sqlite_path))
        self.ttl_seconds = ttl_seconds
        self._lock = asyncio.Lock()
        self._ensure_db()

    def fingerprint(self, order: OrderRequest) -> str:
        payload = {
            "symbol": order.symbol,
            "side": order.side.value,
            "quantity": round(float(order.quantity), 10),
            "mode": order.mode.value,
            "broker": order.broker.lower(),
            "order_type": order.order_type.value,
            "limit_price": order.limit_price,
            "stop_loss": order.stop_loss,
            "take_profit": order.take_profit,
            "leverage": round(float(order.leverage), 8),
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    async def create_ticket(self, order: OrderRequest, requested_by: str = "operator") -> Dict[str, Any]:
        if order.mode != TradingMode.LIVE:
            raise ValueError("Live approval tickets can only be created for live orders.")
        now = datetime.now(timezone.utc)
        ticket_id = f"LIVEAP-{uuid.uuid4().hex[:12]}"
        ticket = LiveApprovalTicket(
            ticket_id=ticket_id,
            fingerprint=self.fingerprint(order),
            order_preview=order.model_dump(mode="json"),
            requested_by=requested_by,
            requested_at=now,
            expires_at=now + timedelta(seconds=self.ttl_seconds),
        )
        async with self._lock:
            self._upsert(ticket)
        return self._ticket_dict(ticket)

    async def approve_ticket(self, ticket_id: str, approved_by: str = "supervisor") -> Dict[str, Any]:
        async with self._lock:
            ticket = self._get(ticket_id)
            if not ticket:
                raise ValueError("Approval ticket not found.")
            if self._expired(ticket):
                raise ValueError("Approval ticket expired.")
            if ticket.consumed:
                raise ValueError("Approval ticket already consumed.")
            ticket.approved = True
            ticket.approved_by = approved_by
            ticket.approved_at = datetime.now(timezone.utc)
            self._upsert(ticket)
            return self._ticket_dict(ticket)

    async def consume_for_order(self, ticket_id: str, order: OrderRequest) -> bool:
        expected = self.fingerprint(order)
        async with self._lock:
            ticket = self._get(ticket_id)
            if not ticket:
                return False
            if self._expired(ticket) or ticket.consumed or not ticket.approved:
                return False
            if not hmac.compare_digest(ticket.fingerprint, expected):
                return False
            ticket.consumed = True
            ticket.consumed_at = datetime.now(timezone.utc)
            self._upsert(ticket)
            return True

    async def get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        async with self._lock:
            ticket = self._get(ticket_id)
            return self._ticket_dict(ticket) if ticket else None

    async def cleanup_expired(self) -> int:
        removed = 0
        now = datetime.now(timezone.utc)
        async with self._lock:
            conn = self._connect()
            try:
                cur = conn.execute("DELETE FROM live_approval_tickets WHERE expires_at <= ?", (now.isoformat(),))
                removed = int(cur.rowcount or 0)
                conn.commit()
            finally:
                conn.close()
        return removed

    def _ensure_db(self) -> None:
        Path(self.sqlite_path).parent.mkdir(parents=True, exist_ok=True)
        conn = self._connect()
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS live_approval_tickets (
                    ticket_id TEXT PRIMARY KEY,
                    fingerprint TEXT NOT NULL,
                    order_preview_json TEXT NOT NULL,
                    requested_by TEXT NOT NULL,
                    requested_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    approved INTEGER NOT NULL DEFAULT 0,
                    approved_by TEXT,
                    approved_at TEXT,
                    consumed INTEGER NOT NULL DEFAULT 0,
                    consumed_at TEXT
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS ix_live_approval_expires ON live_approval_tickets(expires_at)")
            conn.commit()
        finally:
            conn.close()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.sqlite_path, timeout=30)

    def _upsert(self, ticket: LiveApprovalTicket) -> None:
        conn = self._connect()
        try:
            conn.execute(
                """
                INSERT INTO live_approval_tickets (
                    ticket_id, fingerprint, order_preview_json, requested_by, requested_at, expires_at,
                    approved, approved_by, approved_at, consumed, consumed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(ticket_id) DO UPDATE SET
                    fingerprint=excluded.fingerprint,
                    order_preview_json=excluded.order_preview_json,
                    requested_by=excluded.requested_by,
                    requested_at=excluded.requested_at,
                    expires_at=excluded.expires_at,
                    approved=excluded.approved,
                    approved_by=excluded.approved_by,
                    approved_at=excluded.approved_at,
                    consumed=excluded.consumed,
                    consumed_at=excluded.consumed_at
                """,
                (
                    ticket.ticket_id,
                    ticket.fingerprint,
                    json.dumps(ticket.order_preview, ensure_ascii=True, separators=(",", ":")),
                    ticket.requested_by,
                    ticket.requested_at.isoformat(),
                    ticket.expires_at.isoformat(),
                    1 if ticket.approved else 0,
                    ticket.approved_by,
                    ticket.approved_at.isoformat() if ticket.approved_at else None,
                    1 if ticket.consumed else 0,
                    ticket.consumed_at.isoformat() if ticket.consumed_at else None,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def _get(self, ticket_id: str) -> Optional[LiveApprovalTicket]:
        conn = self._connect()
        try:
            row = conn.execute(
                """
                SELECT
                    ticket_id, fingerprint, order_preview_json, requested_by, requested_at, expires_at,
                    approved, approved_by, approved_at, consumed, consumed_at
                FROM live_approval_tickets
                WHERE ticket_id = ?
                """,
                (ticket_id,),
            ).fetchone()
            if not row:
                return None
            order_preview = json.loads(row[2])
            return LiveApprovalTicket(
                ticket_id=row[0],
                fingerprint=row[1],
                order_preview=order_preview,
                requested_by=row[3],
                requested_at=datetime.fromisoformat(row[4]),
                expires_at=datetime.fromisoformat(row[5]),
                approved=bool(row[6]),
                approved_by=row[7],
                approved_at=datetime.fromisoformat(row[8]) if row[8] else None,
                consumed=bool(row[9]),
                consumed_at=datetime.fromisoformat(row[10]) if row[10] else None,
            )
        finally:
            conn.close()

    def _expired(self, ticket: LiveApprovalTicket) -> bool:
        return ticket.expires_at <= datetime.now(timezone.utc)

    def _ticket_dict(self, ticket: LiveApprovalTicket) -> Dict[str, Any]:
        return {
            "ticket_id": ticket.ticket_id,
            "fingerprint": ticket.fingerprint,
            "requested_by": ticket.requested_by,
            "requested_at": ticket.requested_at.isoformat(),
            "expires_at": ticket.expires_at.isoformat(),
            "approved": ticket.approved,
            "approved_by": ticket.approved_by,
            "approved_at": ticket.approved_at.isoformat() if ticket.approved_at else None,
            "consumed": ticket.consumed,
            "consumed_at": ticket.consumed_at.isoformat() if ticket.consumed_at else None,
            "order_preview": ticket.order_preview,
        }


--- END FILE: execution\persistent_live_approval.py ---

--- START FILE: execution\__init__.py ---

--- END FILE: execution\__init__.py ---

--- START FILE: frontend\.gitignore ---
# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

node_modules
dist
dist-ssr
*.local

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

--- END FILE: frontend\.gitignore ---

--- START FILE: frontend\eslint.config.js ---
import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import tseslint from 'typescript-eslint'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      tseslint.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      globals: globals.browser,
    },
  },
])

--- END FILE: frontend\eslint.config.js ---

--- START FILE: frontend\index.html ---
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>frontend</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>

--- END FILE: frontend\index.html ---

--- START FILE: frontend\package.json ---
{
  "name": "frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "eslint .",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^19.2.6",
    "react-dom": "^19.2.6"
  },
  "devDependencies": {
    "@eslint/js": "^10.0.1",
    "@tailwindcss/postcss": "^4.3.0",
    "@types/node": "^24.12.3",
    "@types/react": "^19.2.14",
    "@types/react-dom": "^19.2.3",
    "@vitejs/plugin-react": "^6.0.1",
    "autoprefixer": "^10.5.0",
    "eslint": "^10.3.0",
    "eslint-plugin-react-hooks": "^7.1.1",
    "eslint-plugin-react-refresh": "^0.5.2",
    "globals": "^17.6.0",
    "postcss": "^8.5.14",
    "tailwindcss": "^4.3.0",
    "typescript": "~6.0.2",
    "typescript-eslint": "^8.59.2",
    "vite": "^8.0.12"
  }
}

--- END FILE: frontend\package.json ---

--- START FILE: frontend\postcss.config.js ---
﻿export default {
  plugins: {
    '@tailwindcss/postcss': {},
    autoprefixer: {},
  },
}

--- END FILE: frontend\postcss.config.js ---

--- START FILE: frontend\README.md ---
# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

--- END FILE: frontend\README.md ---

--- START FILE: frontend\tailwind.config.js ---
﻿/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          900: '#0f172a',
          800: '#1e293b',
          700: '#334155',
        },
        accent: {
          green: '#10b981',
          red: '#ef4444',
          blue: '#3b82f6',
        }
      }
    },
  },
  plugins: [],
}

--- END FILE: frontend\tailwind.config.js ---

--- START FILE: frontend\tsconfig.app.json ---
{
  "compilerOptions": {
    "tsBuildInfoFile": "./node_modules/.tmp/tsconfig.app.tsbuildinfo",
    "target": "es2023",
    "lib": ["ES2023", "DOM"],
    "module": "esnext",
    "types": ["vite/client"],
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "verbatimModuleSyntax": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "react-jsx",

    /* Linting */
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "erasableSyntaxOnly": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"]
}

--- END FILE: frontend\tsconfig.app.json ---

--- START FILE: frontend\tsconfig.json ---
{
  "files": [],
  "references": [
    { "path": "./tsconfig.app.json" },
    { "path": "./tsconfig.node.json" }
  ]
}

--- END FILE: frontend\tsconfig.json ---

--- START FILE: frontend\tsconfig.node.json ---
{
  "compilerOptions": {
    "tsBuildInfoFile": "./node_modules/.tmp/tsconfig.node.tsbuildinfo",
    "target": "es2023",
    "lib": ["ES2023"],
    "module": "esnext",
    "types": ["node"],
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "verbatimModuleSyntax": true,
    "moduleDetection": "force",
    "noEmit": true,

    /* Linting */
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "erasableSyntaxOnly": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["vite.config.ts"]
}

--- END FILE: frontend\tsconfig.node.json ---

--- START FILE: frontend\vite.config.ts ---
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
})

--- END FILE: frontend\vite.config.ts ---

--- START FILE: frontend\src\App.css ---
.counter {
  font-size: 16px;
  padding: 5px 10px;
  border-radius: 5px;
  color: var(--accent);
  background: var(--accent-bg);
  border: 2px solid transparent;
  transition: border-color 0.3s;
  margin-bottom: 24px;

  &:hover {
    border-color: var(--accent-border);
  }
  &:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }
}

.hero {
  position: relative;

  .base,
  .framework,
  .vite {
    inset-inline: 0;
    margin: 0 auto;
  }

  .base {
    width: 170px;
    position: relative;
    z-index: 0;
  }

  .framework,
  .vite {
    position: absolute;
  }

  .framework {
    z-index: 1;
    top: 34px;
    height: 28px;
    transform: perspective(2000px) rotateZ(300deg) rotateX(44deg) rotateY(39deg)
      scale(1.4);
  }

  .vite {
    z-index: 0;
    top: 107px;
    height: 26px;
    width: auto;
    transform: perspective(2000px) rotateZ(300deg) rotateX(40deg) rotateY(39deg)
      scale(0.8);
  }
}

#center {
  display: flex;
  flex-direction: column;
  gap: 25px;
  place-content: center;
  place-items: center;
  flex-grow: 1;

  @media (max-width: 1024px) {
    padding: 32px 20px 24px;
    gap: 18px;
  }
}

#next-steps {
  display: flex;
  border-top: 1px solid var(--border);
  text-align: left;

  & > div {
    flex: 1 1 0;
    padding: 32px;
    @media (max-width: 1024px) {
      padding: 24px 20px;
    }
  }

  .icon {
    margin-bottom: 16px;
    width: 22px;
    height: 22px;
  }

  @media (max-width: 1024px) {
    flex-direction: column;
    text-align: center;
  }
}

#docs {
  border-right: 1px solid var(--border);

  @media (max-width: 1024px) {
    border-right: none;
    border-bottom: 1px solid var(--border);
  }
}

#next-steps ul {
  list-style: none;
  padding: 0;
  display: flex;
  gap: 8px;
  margin: 32px 0 0;

  .logo {
    height: 18px;
  }

  a {
    color: var(--text-h);
    font-size: 16px;
    border-radius: 6px;
    background: var(--social-bg);
    display: flex;
    padding: 6px 12px;
    align-items: center;
    gap: 8px;
    text-decoration: none;
    transition: box-shadow 0.3s;

    &:hover {
      box-shadow: var(--shadow);
    }
    .button-icon {
      height: 18px;
      width: 18px;
    }
  }

  @media (max-width: 1024px) {
    margin-top: 20px;
    flex-wrap: wrap;
    justify-content: center;

    li {
      flex: 1 1 calc(50% - 8px);
    }

    a {
      width: 100%;
      justify-content: center;
      box-sizing: border-box;
    }
  }
}

#spacer {
  height: 88px;
  border-top: 1px solid var(--border);
  @media (max-width: 1024px) {
    height: 48px;
  }
}

.ticks {
  position: relative;
  width: 100%;

  &::before,
  &::after {
    content: '';
    position: absolute;
    top: -4.5px;
    border: 5px solid transparent;
  }

  &::before {
    left: 0;
    border-left-color: var(--border);
  }
  &::after {
    right: 0;
    border-right-color: var(--border);
  }
}

--- END FILE: frontend\src\App.css ---

--- START FILE: frontend\src\App.tsx ---
import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <section id="center">
        <div className="hero">
          <img src={heroImg} className="base" width="170" height="179" alt="" />
          <img src={reactLogo} className="framework" alt="React logo" />
          <img src={viteLogo} className="vite" alt="Vite logo" />
        </div>
        <div>
          <h1>Get started</h1>
          <p>
            Edit <code>src/App.tsx</code> and save to test <code>HMR</code>
          </p>
        </div>
        <button
          type="button"
          className="counter"
          onClick={() => setCount((count) => count + 1)}
        >
          Count is {count}
        </button>
      </section>

      <div className="ticks"></div>

      <section id="next-steps">
        <div id="docs">
          <svg className="icon" role="presentation" aria-hidden="true">
            <use href="/icons.svg#documentation-icon"></use>
          </svg>
          <h2>Documentation</h2>
          <p>Your questions, answered</p>
          <ul>
            <li>
              <a href="https://vite.dev/" target="_blank">
                <img className="logo" src={viteLogo} alt="" />
                Explore Vite
              </a>
            </li>
            <li>
              <a href="https://react.dev/" target="_blank">
                <img className="button-icon" src={reactLogo} alt="" />
                Learn more
              </a>
            </li>
          </ul>
        </div>
        <div id="social">
          <svg className="icon" role="presentation" aria-hidden="true">
            <use href="/icons.svg#social-icon"></use>
          </svg>
          <h2>Connect with us</h2>
          <p>Join the Vite community</p>
          <ul>
            <li>
              <a href="https://github.com/vitejs/vite" target="_blank">
                <svg
                  className="button-icon"
                  role="presentation"
                  aria-hidden="true"
                >
                  <use href="/icons.svg#github-icon"></use>
                </svg>
                GitHub
              </a>
            </li>
            <li>
              <a href="https://chat.vite.dev/" target="_blank">
                <svg
                  className="button-icon"
                  role="presentation"
                  aria-hidden="true"
                >
                  <use href="/icons.svg#discord-icon"></use>
                </svg>
                Discord
              </a>
            </li>
            <li>
              <a href="https://x.com/vite_js" target="_blank">
                <svg
                  className="button-icon"
                  role="presentation"
                  aria-hidden="true"
                >
                  <use href="/icons.svg#x-icon"></use>
                </svg>
                X.com
              </a>
            </li>
            <li>
              <a href="https://bsky.app/profile/vite.dev" target="_blank">
                <svg
                  className="button-icon"
                  role="presentation"
                  aria-hidden="true"
                >
                  <use href="/icons.svg#bluesky-icon"></use>
                </svg>
                Bluesky
              </a>
            </li>
          </ul>
        </div>
      </section>

      <div className="ticks"></div>
      <section id="spacer"></section>
    </>
  )
}

export default App

--- END FILE: frontend\src\App.tsx ---

--- START FILE: frontend\src\index.css ---
﻿@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
  line-height: 1.5;
  font-weight: 400;
  color-scheme: dark;
  color: #e2e8f0;
  background-color: #0f172a;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  min-height: 100vh;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #1e293b;
}

::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #64748b;
}

--- END FILE: frontend\src\index.css ---

--- START FILE: frontend\src\main.tsx ---
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

--- END FILE: frontend\src\main.tsx ---

--- START FILE: integrations\hermes_client.py ---
"""Hermes Agent CLI bridge.

This lets our Python agents use Hermes as a reasoning + self-learning copilot.

Production target for Windows laptops:
- Hermes runs on an Ubuntu box (your laptop/VM/server) with SSH enabled.
- Windows agents call Hermes over SSH (non-interactive, key-based auth).

We still support:
- Native `hermes` on the same machine.
- WSL `wsl hermes` as a fallback.
"""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from typing import List, Optional, Tuple


def _env_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class HermesClient:
    """
    Minimal Hermes CLI wrapper.

    Env:
    - HERMES_CMD: override executable, e.g. "hermes" or "wsl hermes"
    - HERMES_TIMEOUT_SEC: subprocess timeout (default 120)
    - HERMES_ACCEPT_HOOKS: if "true", sets HERMES_ACCEPT_HOOKS=1 for Hermes
    """

    timeout_sec: int = int(os.getenv("HERMES_TIMEOUT_SEC", "120"))
    cmd: Optional[str] = os.getenv("HERMES_CMD")
    ssh_host: str = os.getenv("HERMES_SSH_HOST", "").strip()
    ssh_user: str = os.getenv("HERMES_SSH_USER", "").strip()
    ssh_port: int = int(os.getenv("HERMES_SSH_PORT", "22"))
    ssh_identity_file: str = os.getenv("HERMES_SSH_IDENTITY_FILE", "").strip()
    ssh_connect_timeout_sec: int = int(os.getenv("HERMES_SSH_CONNECT_TIMEOUT_SEC", "6"))

    def _resolve_base_cmd(self) -> List[str]:
        # 1) Explicit override (highest priority)
        if self.cmd:
            # Allow "ssh ... hermes" or "wsl hermes" etc.
            return shlex.split(self.cmd, posix=(os.name != "nt"))

        # 2) SSH bridge (production on Windows)
        if self.ssh_host:
            return self._build_ssh_cmd()

        # Prefer native hermes if available.
        if shutil.which("hermes"):
            return ["hermes"]

        # Windows: assume Hermes is installed in WSL.
        if os.name == "nt" and shutil.which("wsl"):
            distro = os.getenv("HERMES_WSL_DISTRO", "").strip()
            if distro:
                return ["wsl", "-d", distro, "hermes"]
            return ["wsl", "hermes"]

        # Fallback: still try.
        return ["hermes"]

    def _build_ssh_cmd(self) -> List[str]:
        # Use BatchMode to prevent password prompts (production safety).
        # Use -T to avoid allocating a TTY, which can hang in some setups.
        dest = self.ssh_host
        if self.ssh_user:
            dest = f"{self.ssh_user}@{self.ssh_host}"
        cmd: List[str] = [
            "ssh",
            "-T",
            "-o",
            "BatchMode=yes",
            "-o",
            f"ConnectTimeout={self.ssh_connect_timeout_sec}",
            "-p",
            str(self.ssh_port),
        ]
        if self.ssh_identity_file:
            cmd += ["-i", self.ssh_identity_file]
        cmd += [dest, "hermes"]
        return cmd

    def query(self, prompt: str) -> str:
        """
        Run one-shot Hermes prompt and return stdout.

        Uses: `hermes chat -q "<prompt>"` (non-interactive).
        """
        base = self._resolve_base_cmd()
        args = base + ["chat", "-q", prompt]
        env = os.environ.copy()
        env.setdefault("NO_COLOR", "1")
        # Keep Hermes from waiting on interactive confirmations for shell hooks.
        if _env_bool("HERMES_ACCEPT_HOOKS", False):
            # Some Hermes versions use this env var; also helps with tools.
            env["HERMES_ACCEPT_HOOKS"] = "1"
        try:
            proc = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=self.timeout_sec,
                env=env,
            )
        except subprocess.TimeoutExpired:
            return "HERMES_TIMEOUT"

        out = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()
        if proc.returncode != 0 and not out:
            return f"HERMES_ERROR: {err[:4000]}"
        return out or err

    def healthcheck(self) -> Tuple[bool, str]:
        """Fast connectivity check. Never raises."""
        base = self._resolve_base_cmd()
        env = os.environ.copy()
        env.setdefault("NO_COLOR", "1")
        try:
            proc = subprocess.run(
                base + ["--version"],
                capture_output=True,
                text=True,
                timeout=min(15, self.timeout_sec),
                env=env,
            )
        except Exception as exc:  # noqa: BLE001
            return False, f"hermes check failed: {exc}"
        out = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()
        if proc.returncode != 0:
            return False, (err or out or f"exit={proc.returncode}")
        return True, (out or err)

--- END FILE: integrations\hermes_client.py ---

--- START FILE: integrations\__init__.py ---
"""External integration helpers (Hermes, Telegram, brokers, etc)."""


--- END FILE: integrations\__init__.py ---

--- START FILE: market_data\__init__.py ---
"""Market data and instrument master utilities."""


--- END FILE: market_data\__init__.py ---

--- START FILE: memory\global_state.py ---
"""Shared, thread-safe global state manager."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from trading_system.config.models import PortfolioSnapshot, TradingMode

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class Position:
    """Canonical in-memory position object."""

    symbol: str
    quantity: float
    avg_price: float
    side: str
    mode: TradingMode
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    opened_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class GlobalState:
    """
    Shared state manager used by all agents and execution components.

    Unit-test example:
        >>> state = GlobalState(initial_balance=100000)
        >>> snapshot = asyncio.run(state.snapshot(TradingMode.PAPER))
        >>> snapshot.balance
        100000.0
    """

    def __init__(self, initial_balance: float = 100000.0) -> None:
        self._lock = asyncio.Lock()
        self._initial_balance = initial_balance
        self._balances: Dict[TradingMode, float] = {
            TradingMode.PAPER: initial_balance,
            TradingMode.LIVE: initial_balance,
            TradingMode.BACKTEST: initial_balance,
        }
        self._available_cash: Dict[TradingMode, float] = dict(self._balances)
        self._daily_realized_pnl: Dict[TradingMode, float] = {
            TradingMode.PAPER: 0.0,
            TradingMode.LIVE: 0.0,
            TradingMode.BACKTEST: 0.0,
        }
        self._consecutive_losses: Dict[TradingMode, int] = {
            TradingMode.PAPER: 0,
            TradingMode.LIVE: 0,
            TradingMode.BACKTEST: 0,
        }
        self._positions: Dict[TradingMode, Dict[str, Position]] = {
            TradingMode.PAPER: {},
            TradingMode.LIVE: {},
            TradingMode.BACKTEST: {},
        }

    async def snapshot(self, mode: TradingMode) -> PortfolioSnapshot:
        """Return a copy-safe snapshot for the selected mode."""
        async with self._lock:
            positions = {
                symbol: asdict(position) for symbol, position in self._positions[mode].items()
            }
            gross_exposure = sum(abs(p.quantity * p.avg_price) for p in self._positions[mode].values())
            return PortfolioSnapshot(
                mode=mode,
                balance=self._balances[mode],
                available_cash=self._available_cash[mode],
                daily_realized_pnl=self._daily_realized_pnl[mode],
                gross_exposure=gross_exposure,
                positions=positions,
                consecutive_losses=self._consecutive_losses[mode],
            )

    async def upsert_position(self, position: Position) -> None:
        """Insert or update a position."""
        async with self._lock:
            position.updated_at = datetime.now(timezone.utc)
            self._positions[position.mode][position.symbol] = position
            logger.debug("Position upserted for %s (%s)", position.symbol, position.mode.value)

    async def remove_position(self, symbol: str, mode: TradingMode) -> None:
        """Remove a position if present."""
        async with self._lock:
            self._positions[mode].pop(symbol, None)
            logger.debug("Position removed for %s (%s)", symbol, mode.value)

    async def adjust_cash_and_balance(self, mode: TradingMode, cash_delta: float, pnl_delta: float = 0.0) -> None:
        """Adjust cash and balance atomically."""
        async with self._lock:
            self._available_cash[mode] += cash_delta
            self._balances[mode] += pnl_delta
            self._daily_realized_pnl[mode] += pnl_delta
            if pnl_delta < 0:
                self._consecutive_losses[mode] += 1
            elif pnl_delta > 0:
                self._consecutive_losses[mode] = 0

    async def set_consecutive_losses(self, mode: TradingMode, value: int) -> None:
        """Force-update consecutive loss counter."""
        async with self._lock:
            self._consecutive_losses[mode] = max(0, value)

    async def get_position(self, symbol: str, mode: TradingMode) -> Optional[Position]:
        """Fetch one position by symbol."""
        async with self._lock:
            return self._positions[mode].get(symbol)

    async def update_unrealized_pnl(self, symbol: str, mode: TradingMode, mark_price: float) -> None:
        """Refresh unrealized PnL for one symbol using mark price."""
        async with self._lock:
            position = self._positions[mode].get(symbol)
            if not position:
                return
            if position.side.lower() == "buy":
                position.unrealized_pnl = (mark_price - position.avg_price) * position.quantity
            else:
                position.unrealized_pnl = (position.avg_price - mark_price) * position.quantity
            position.updated_at = datetime.now(timezone.utc)

    async def reset_daily_pnl(self, mode: TradingMode) -> None:
        """Reset daily realized PnL and losses."""
        async with self._lock:
            self._daily_realized_pnl[mode] = 0.0
            self._consecutive_losses[mode] = 0

    async def diagnostics(self) -> Dict[str, Any]:
        """Return a diagnostics snapshot safe for API usage."""
        out: Dict[str, Any] = {}
        for mode in TradingMode:
            snap = await self.snapshot(mode)
            out[mode.value] = {
                "balance": snap.balance,
                "available_cash": snap.available_cash,
                "daily_realized_pnl": snap.daily_realized_pnl,
                "gross_exposure": snap.gross_exposure,
                "positions": snap.positions,
                "consecutive_losses": snap.consecutive_losses,
                "updated_at": snap.updated_at.isoformat(),
            }
        return out

--- END FILE: memory\global_state.py ---

--- START FILE: memory\reflexion_memory.py ---
"""Reflexion memory store for continuous learning feedback."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import aiosqlite

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ReflexionEntry:
    """Learning record generated after trade outcomes."""

    symbol: str
    strategy_id: str
    outcome: str
    pnl: float
    lesson: str
    created_at: datetime


class ReflexionMemoryRepository:
    """Simple SQLite repository for reflexion entries."""

    def __init__(self, sqlite_path: str) -> None:
        self.sqlite_path = sqlite_path

    async def initialize(self) -> None:
        """Create schema."""
        async with aiosqlite.connect(self.sqlite_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS reflexions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    strategy_id TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    pnl REAL NOT NULL,
                    lesson TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            await db.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_reflexions_symbol_strategy
                ON reflexions(symbol, strategy_id)
                """
            )
            await db.commit()

    async def add_entry(self, entry: ReflexionEntry) -> int:
        """Insert reflexion entry."""
        async with aiosqlite.connect(self.sqlite_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO reflexions (symbol, strategy_id, outcome, pnl, lesson, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.symbol,
                    entry.strategy_id,
                    entry.outcome,
                    entry.pnl,
                    entry.lesson,
                    entry.created_at.isoformat(),
                ),
            )
            await db.commit()
            row_id = int(cursor.lastrowid)
            logger.info("Reflexion logged id=%s symbol=%s", row_id, entry.symbol)
            return row_id

    async def recent_lessons(self, symbol: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch recent lessons globally or by symbol."""
        async with aiosqlite.connect(self.sqlite_path) as db:
            if symbol:
                cursor = await db.execute(
                    """
                    SELECT symbol, strategy_id, outcome, pnl, lesson, created_at
                    FROM reflexions
                    WHERE symbol = ?
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (symbol, limit),
                )
            else:
                cursor = await db.execute(
                    """
                    SELECT symbol, strategy_id, outcome, pnl, lesson, created_at
                    FROM reflexions
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (limit,),
                )
            rows = await cursor.fetchall()
            return [
                {
                    "symbol": row[0],
                    "strategy_id": row[1],
                    "outcome": row[2],
                    "pnl": row[3],
                    "lesson": row[4],
                    "created_at": row[5],
                }
                for row in rows
            ]

    async def summarize(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Return simple learning summary stats."""
        async with aiosqlite.connect(self.sqlite_path) as db:
            if symbol:
                cursor = await db.execute(
                    """
                    SELECT
                        COUNT(*) AS total,
                        SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) AS wins,
                        SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) AS losses,
                        COALESCE(AVG(pnl), 0) AS avg_pnl
                    FROM reflexions
                    WHERE symbol = ?
                    """,
                    (symbol,),
                )
            else:
                cursor = await db.execute(
                    """
                    SELECT
                        COUNT(*) AS total,
                        SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) AS wins,
                        SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) AS losses,
                        COALESCE(AVG(pnl), 0) AS avg_pnl
                    FROM reflexions
                    """
                )
            row = await cursor.fetchone()
            return {
                "total": int(row[0] or 0),
                "wins": int(row[1] or 0),
                "losses": int(row[2] or 0),
                "avg_pnl": float(row[3] or 0.0),
            }

--- END FILE: memory\reflexion_memory.py ---

--- START FILE: memory\trade_memory.py ---
"""SQLite-backed trade repository."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import aiosqlite

from trading_system.config.models import ExecutionResult, TradingMode

logger = logging.getLogger(__name__)


class TradeMemoryRepository:
    """
    Trade memory repository with append-only execution logging.

    Unit-test example:
        >>> repo = TradeMemoryRepository(':memory:')
        >>> asyncio.run(repo.initialize())
    """

    def __init__(self, sqlite_path: str) -> None:
        self.sqlite_path = sqlite_path

    async def initialize(self) -> None:
        """Initialize schema."""
        async with aiosqlite.connect(self.sqlite_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT,
                    mode TEXT NOT NULL,
                    broker TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    average_price REAL,
                    status TEXT NOT NULL,
                    accepted INTEGER NOT NULL,
                    message TEXT,
                    metadata_json TEXT,
                    pnl REAL DEFAULT 0,
                    created_at TEXT NOT NULL
                )
                """
            )
            await db.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_trades_mode_symbol
                ON trades(mode, symbol)
                """
            )
            await db.commit()

    async def log_execution(self, result: ExecutionResult) -> int:
        """Persist one execution event."""
        async with aiosqlite.connect(self.sqlite_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO trades (
                    order_id, mode, broker, symbol, side, quantity,
                    average_price, status, accepted, message, metadata_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result.order_id,
                    result.mode.value,
                    result.broker,
                    result.symbol,
                    result.side.value,
                    result.quantity,
                    result.average_price,
                    result.status,
                    1 if result.accepted else 0,
                    result.message,
                    str(result.metadata),
                    result.executed_at.isoformat(),
                ),
            )
            await db.commit()
            row_id = int(cursor.lastrowid)
            logger.info("Trade logged id=%s symbol=%s mode=%s", row_id, result.symbol, result.mode.value)
            return row_id

    async def update_trade_pnl(self, trade_id: int, pnl: float) -> None:
        """Update PnL for a closed trade row."""
        async with aiosqlite.connect(self.sqlite_path) as db:
            await db.execute("UPDATE trades SET pnl = ? WHERE id = ?", (pnl, trade_id))
            await db.commit()

    async def recent_trades(self, mode: TradingMode, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch recent trades."""
        async with aiosqlite.connect(self.sqlite_path) as db:
            cursor = await db.execute(
                """
                SELECT id, order_id, mode, broker, symbol, side, quantity, average_price,
                       status, accepted, message, metadata_json, pnl, created_at
                FROM trades
                WHERE mode = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (mode.value, limit),
            )
            rows = await cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "order_id": row[1],
                    "mode": row[2],
                    "broker": row[3],
                    "symbol": row[4],
                    "side": row[5],
                    "quantity": row[6],
                    "average_price": row[7],
                    "status": row[8],
                    "accepted": bool(row[9]),
                    "message": row[10],
                    "metadata_json": row[11],
                    "pnl": row[12],
                    "created_at": row[13],
                }
                for row in rows
            ]

    async def trade_stats(self, mode: TradingMode) -> Dict[str, float]:
        """Aggregate win/loss counters for risk checks."""
        async with aiosqlite.connect(self.sqlite_path) as db:
            cursor = await db.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) AS wins,
                    SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) AS losses,
                    COALESCE(SUM(pnl), 0) AS net_pnl
                FROM trades
                WHERE mode = ?
                """,
                (mode.value,),
            )
            row = await cursor.fetchone()
            total = int(row[0] or 0)
            wins = int(row[1] or 0)
            losses = int(row[2] or 0)
            net_pnl = float(row[3] or 0.0)
            return {
                "total": total,
                "wins": wins,
                "losses": losses,
                "win_rate": (wins / total) if total else 0.0,
                "net_pnl": net_pnl,
            }

    async def count_consecutive_losses(self, mode: TradingMode, lookback: int = 20) -> int:
        """Count consecutive losing trades from latest backward."""
        async with aiosqlite.connect(self.sqlite_path) as db:
            cursor = await db.execute(
                """
                SELECT pnl
                FROM trades
                WHERE mode = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (mode.value, lookback),
            )
            rows = await cursor.fetchall()
            streak = 0
            for (pnl,) in rows:
                if pnl < 0:
                    streak += 1
                else:
                    break
            return streak

    async def heartbeat(self) -> Dict[str, Any]:
        """Simple health endpoint payload."""
        return {"db": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

--- END FILE: memory\trade_memory.py ---

--- START FILE: memory\vector_memory.py ---
"""Lightweight vector memory with deterministic local embeddings."""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from typing import Any, Dict, List

import numpy as np

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class VectorRecord:
    """Vector record container."""

    record_id: str
    text: str
    metadata: Dict[str, Any]
    vector: np.ndarray


class VectorMemory:
    """
    In-process vector memory for retrieval support.

    This intentionally avoids external embedding dependencies by using
    a deterministic hash-based embedding for portability.
    """

    def __init__(self, dimension: int = 128) -> None:
        self.dimension = dimension
        self._records: Dict[str, VectorRecord] = {}

    def _embed(self, text: str) -> np.ndarray:
        """Create deterministic dense vector from text."""
        vec = np.zeros(self.dimension, dtype=np.float32)
        tokens = text.lower().split()
        for token in tokens:
            h = hashlib.sha256(token.encode("utf-8")).hexdigest()
            idx = int(h[:8], 16) % self.dimension
            vec[idx] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def upsert(self, record_id: str, text: str, metadata: Dict[str, Any] | None = None) -> None:
        """Insert or update one vector record."""
        metadata = metadata or {}
        vector = self._embed(text)
        self._records[record_id] = VectorRecord(record_id=record_id, text=text, metadata=metadata, vector=vector)
        logger.debug("Vector record upserted id=%s", record_id)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search memory by cosine similarity."""
        if not self._records:
            return []
        q = self._embed(query)
        scored: List[Dict[str, Any]] = []
        for rec in self._records.values():
            score = float(np.dot(q, rec.vector))
            scored.append(
                {
                    "record_id": rec.record_id,
                    "score": score,
                    "text": rec.text,
                    "metadata": rec.metadata,
                }
            )
        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:top_k]

    def all_records(self) -> List[Dict[str, Any]]:
        """Return all records."""
        return [
            {"record_id": r.record_id, "text": r.text, "metadata": r.metadata}
            for r in self._records.values()
        ]

--- END FILE: memory\vector_memory.py ---

--- START FILE: memory\__init__.py ---

--- END FILE: memory\__init__.py ---

--- START FILE: skills\backtesting_skill.py ---
"""Historical-only backtesting engine isolated from live execution."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import yfinance as yf

from trading_system.config.models import BacktestMetrics, BacktestRequest, BacktestResult

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class SimTrade:
    """One simulated trade record."""

    symbol: str
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    return_pct: float
    strategy: str


class BacktestingSkill:
    """
    Backtesting engine supporting EMA, RSI, and custom Pine-like strategies.

    Safety:
    - Uses only historical data providers.
    - Never calls broker/exchange endpoints.
    """

    def __init__(self, fee_bps: float = 5.0, slippage_bps: float = 3.0) -> None:
        self.fee_bps = fee_bps
        self.slippage_bps = slippage_bps

    async def run(
        self,
        request: BacktestRequest,
        pinescript_source: Optional[str] = None,
    ) -> BacktestResult:
        """Run full backtest including walk-forward testing."""
        historical = await self._load_multi_asset_data(request)
        if not historical:
            raise ValueError("No historical data loaded for requested symbols")

        trades: List[SimTrade] = []
        equity_curve: List[float] = [request.initial_capital]
        capital_per_symbol = request.initial_capital / max(len(historical), 1)

        for symbol, frame in historical.items():
            symbol_trades, symbol_equity = self._simulate_symbol(
                symbol=symbol,
                frame=frame,
                strategy_name=request.strategy_name,
                strategy_params=request.strategy_params,
                starting_capital=capital_per_symbol,
                pinescript_source=pinescript_source,
            )
            trades.extend(symbol_trades)
            equity_curve.extend(
                [
                    (equity_curve[-1] + (e - capital_per_symbol))
                    for e in symbol_equity[1:]
                ]
            )

        metrics = self._compute_metrics(
            trades=trades,
            equity_curve=equity_curve,
            initial_capital=request.initial_capital,
        )
        walk_forward = self._walk_forward_report(
            historical=historical,
            request=request,
            pinescript_source=pinescript_source,
        )

        return BacktestResult(
            request=request,
            metrics=metrics,
            trades=[asdict(t) for t in trades],
            equity_curve=equity_curve,
            walk_forward=walk_forward,
        )

    async def _load_multi_asset_data(self, request: BacktestRequest) -> Dict[str, pd.DataFrame]:
        """Load historical bars for all symbols."""
        end = request.end or datetime.now(timezone.utc)
        start = request.start or (end - timedelta(days=request.lookback_days))
        tasks = [
            asyncio.to_thread(
                yf.download,
                tickers=symbol,
                start=start,
                end=end,
                interval=request.timeframe,
                auto_adjust=False,
                progress=False,
            )
            for symbol in request.symbols
        ]
        data = await asyncio.gather(*tasks, return_exceptions=True)
        output: Dict[str, pd.DataFrame] = {}
        for symbol, frame in zip(request.symbols, data):
            if isinstance(frame, Exception):
                logger.exception("Failed loading historical data symbol=%s", symbol, exc_info=frame)
                continue
            if frame.empty:
                logger.warning("No historical bars for symbol=%s", symbol)
                continue
            normalized = self._normalize_yfinance_frame(frame)
            output[symbol] = normalized.dropna().copy()
        return output

    def _normalize_yfinance_frame(self, frame: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize yfinance output into a single-index column DataFrame with a numeric Close series.

        yfinance can return MultiIndex columns or a Close DataFrame; both break float(row["Close"]).
        """
        df = frame.copy()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [str(col[0]) for col in df.columns]
        if "Close" not in df:
            raise ValueError("Historical frame missing Close column.")
        close_obj = df["Close"]
        if isinstance(close_obj, pd.DataFrame):
            close_obj = close_obj.iloc[:, 0]
        close = pd.to_numeric(close_obj, errors="coerce")
        if close.empty:
            raise ValueError("Historical frame Close series is empty.")
        df = df.loc[close.dropna().index].copy()
        df["Close"] = close.loc[df.index]
        return df

    def _simulate_symbol(
        self,
        symbol: str,
        frame: pd.DataFrame,
        strategy_name: str,
        strategy_params: Dict[str, Any],
        starting_capital: float,
        pinescript_source: Optional[str],
    ) -> Tuple[List[SimTrade], List[float]]:
        """Run one-symbol historical simulation."""
        df = frame.copy()
        signals = self._build_signals(df, strategy_name, strategy_params, pinescript_source)
        # Execute at next bar close to reduce lookahead bias.
        signals["entry"] = signals["entry"].shift(1).fillna(False)
        signals["exit"] = signals["exit"].shift(1).fillna(False)

        capital = starting_capital
        equity_curve = [capital]
        trades: List[SimTrade] = []
        position_qty = 0.0
        entry_price = 0.0
        entry_time: Optional[datetime] = None

        for idx, row in signals.iterrows():
            close_val = row["Close"]
            if isinstance(close_val, pd.Series):
                close_val = close_val.iloc[0]
            close_price = float(close_val)
            if position_qty == 0 and bool(row["entry"]):
                qty = max(capital // close_price, 0)
                if qty <= 0:
                    equity_curve.append(capital)
                    continue
                executed_price = self._apply_costs(close_price, side="buy")
                position_qty = float(qty)
                entry_price = executed_price
                entry_time = pd.Timestamp(idx).to_pydatetime()
            elif position_qty > 0 and bool(row["exit"]):
                executed_price = self._apply_costs(close_price, side="sell")
                gross_pnl = (executed_price - entry_price) * position_qty
                capital += gross_pnl
                trade = SimTrade(
                    symbol=symbol,
                    entry_time=entry_time or pd.Timestamp(idx).to_pydatetime(),
                    exit_time=pd.Timestamp(idx).to_pydatetime(),
                    entry_price=entry_price,
                    exit_price=executed_price,
                    quantity=position_qty,
                    pnl=gross_pnl,
                    return_pct=(gross_pnl / (entry_price * position_qty)) * 100 if position_qty else 0.0,
                    strategy=strategy_name,
                )
                trades.append(trade)
                position_qty = 0.0
                entry_price = 0.0
                entry_time = None
            # Mark-to-market equity.
            if position_qty > 0:
                mtm = capital + (close_price - entry_price) * position_qty
                equity_curve.append(float(mtm))
            else:
                equity_curve.append(float(capital))

        # Force close at final bar if still open.
        if position_qty > 0:
            tail_close = signals["Close"].iloc[-1]
            if isinstance(tail_close, pd.Series):
                tail_close = tail_close.iloc[0]
            final_price = self._apply_costs(float(tail_close), side="sell")
            gross_pnl = (final_price - entry_price) * position_qty
            capital += gross_pnl
            trades.append(
                SimTrade(
                    symbol=symbol,
                    entry_time=entry_time or signals.index[-1].to_pydatetime(),
                    exit_time=signals.index[-1].to_pydatetime(),
                    entry_price=entry_price,
                    exit_price=final_price,
                    quantity=position_qty,
                    pnl=gross_pnl,
                    return_pct=(gross_pnl / (entry_price * position_qty)) * 100 if position_qty else 0.0,
                    strategy=strategy_name,
                )
            )
            equity_curve[-1] = capital

        return trades, equity_curve

    def _build_signals(
        self,
        df: pd.DataFrame,
        strategy_name: str,
        strategy_params: Dict[str, Any],
        pinescript_source: Optional[str],
    ) -> pd.DataFrame:
        """Create entry/exit boolean signals."""
        signals = df.copy()
        strategy = strategy_name.lower().strip()

        if strategy == "ema" or strategy == "ema_crossover":
            fast = int(strategy_params.get("fast", 21))
            slow = int(strategy_params.get("slow", 55))
            signals["ema_fast"] = signals["Close"].ewm(span=fast, adjust=False).mean()
            signals["ema_slow"] = signals["Close"].ewm(span=slow, adjust=False).mean()
            signals["entry"] = (signals["ema_fast"] > signals["ema_slow"]) & (
                signals["ema_fast"].shift(1) <= signals["ema_slow"].shift(1)
            )
            signals["exit"] = (signals["ema_fast"] < signals["ema_slow"]) & (
                signals["ema_fast"].shift(1) >= signals["ema_slow"].shift(1)
            )
            return signals

        if strategy == "rsi" or strategy == "rsi_reversion":
            period = int(strategy_params.get("period", 14))
            oversold = float(strategy_params.get("oversold", 30))
            mean_exit = float(strategy_params.get("exit", 55))
            rsi = self._rsi(signals["Close"], period=period)
            signals["rsi"] = rsi
            signals["entry"] = rsi < oversold
            signals["exit"] = rsi > mean_exit
            return signals

        if strategy in {"pinescript", "custom_pinescript"}:
            return self._pinescript_to_signals(signals, pinescript_source or "")

        raise ValueError(f"Unsupported strategy: {strategy_name}")

    def _pinescript_to_signals(self, frame: pd.DataFrame, script: str) -> pd.DataFrame:
        """
        Convert simple PineScript indicator patterns into entry/exit signals.

        This intentionally supports a constrained subset for deterministic backtests.
        """
        script_lower = script.lower()
        out = frame.copy()
        out["entry"] = False
        out["exit"] = False

        uses_ema = "ta.ema" in script_lower or "ema(" in script_lower
        uses_rsi = "ta.rsi" in script_lower or "rsi(" in script_lower

        if uses_ema:
            out["ema_fast"] = out["Close"].ewm(span=21, adjust=False).mean()
            out["ema_slow"] = out["Close"].ewm(span=55, adjust=False).mean()
            out["entry"] = (out["ema_fast"] > out["ema_slow"]) & (
                out["ema_fast"].shift(1) <= out["ema_slow"].shift(1)
            )
            out["exit"] = (out["ema_fast"] < out["ema_slow"]) & (
                out["ema_fast"].shift(1) >= out["ema_slow"].shift(1)
            )

        if uses_rsi:
            out["rsi"] = self._rsi(out["Close"], period=14)
            rsi_entry = out["rsi"] < 30
            rsi_exit = out["rsi"] > 60
            out["entry"] = out["entry"] | rsi_entry
            out["exit"] = out["exit"] | rsi_exit

        if not uses_ema and not uses_rsi:
            # Fallback rule if script has no known indicator.
            out["sma_short"] = out["Close"].rolling(10).mean()
            out["sma_long"] = out["Close"].rolling(30).mean()
            out["entry"] = out["sma_short"] > out["sma_long"]
            out["exit"] = out["sma_short"] < out["sma_long"]
        return out

    def _walk_forward_report(
        self,
        historical: Dict[str, pd.DataFrame],
        request: BacktestRequest,
        pinescript_source: Optional[str],
    ) -> List[Dict[str, Any]]:
        """Perform walk-forward evaluation by rolling windows."""
        windows = max(request.walk_forward_windows, 1)
        reports: List[Dict[str, Any]] = []
        for symbol, frame in historical.items():
            if len(frame) < windows * 20:
                continue
            split_size = len(frame) // windows
            for i in range(1, windows):
                train = frame.iloc[: i * split_size]
                test = frame.iloc[i * split_size : (i + 1) * split_size]
                if test.empty:
                    continue
                _, eq = self._simulate_symbol(
                    symbol=symbol,
                    frame=test,
                    strategy_name=request.strategy_name,
                    strategy_params=request.strategy_params,
                    starting_capital=request.initial_capital / max(len(historical), 1),
                    pinescript_source=pinescript_source,
                )
                ret = ((eq[-1] - eq[0]) / eq[0]) * 100 if eq and eq[0] else 0.0
                reports.append(
                    {
                        "symbol": symbol,
                        "window": i,
                        "train_bars": len(train),
                        "test_bars": len(test),
                        "test_return_pct": ret,
                    }
                )
        return reports

    def _compute_metrics(
        self,
        trades: List[SimTrade],
        equity_curve: List[float],
        initial_capital: float,
    ) -> BacktestMetrics:
        """Calculate required performance metrics."""
        if not trades:
            return BacktestMetrics()
        pnl_values = np.array([t.pnl for t in trades], dtype=float)
        wins = pnl_values[pnl_values > 0]
        losses = pnl_values[pnl_values < 0]
        total_trades = len(trades)
        win_rate = float((len(wins) / total_trades) * 100)
        gross_profit = float(wins.sum()) if len(wins) else 0.0
        gross_loss = float(abs(losses.sum())) if len(losses) else 0.0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")
        expectancy = float(np.mean(pnl_values))
        net_profit = float(pnl_values.sum())

        eq = np.array(equity_curve, dtype=float)
        returns = np.diff(eq) / np.where(eq[:-1] == 0, 1, eq[:-1])
        sharpe = 0.0
        if returns.size > 1 and np.std(returns) > 0:
            sharpe = float((np.mean(returns) / np.std(returns)) * np.sqrt(252))

        running_max = np.maximum.accumulate(eq)
        drawdowns = (eq - running_max) / np.where(running_max == 0, 1, running_max)
        max_drawdown = float(abs(np.min(drawdowns))) if drawdowns.size else 0.0
        total_return_pct = ((eq[-1] - initial_capital) / initial_capital) * 100 if initial_capital else 0.0

        return BacktestMetrics(
            total_trades=total_trades,
            win_rate=win_rate,
            sharpe_ratio=sharpe,
            max_drawdown=max_drawdown,
            profit_factor=profit_factor,
            expectancy=expectancy,
            net_profit=net_profit,
            total_return_pct=total_return_pct,
        )

    def _rsi(self, close: pd.Series, period: int = 14) -> pd.Series:
        """RSI implementation."""
        delta = close.diff()
        up = delta.clip(lower=0)
        down = (-delta).clip(lower=0)
        avg_up = up.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        avg_down = down.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        rs = avg_up / avg_down.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)

    def _apply_costs(self, price: float, side: str) -> float:
        """Apply fee and slippage costs to execution price."""
        fee = self.fee_bps / 10000
        slippage = self.slippage_bps / 10000
        if side == "buy":
            return price * (1 + fee + slippage)
        return price * (1 - fee - slippage)

--- END FILE: skills\backtesting_skill.py ---

--- START FILE: skills\ccxt_broker_router.py ---
"""Skill wrapper for broker routing decisions."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from trading_system.config.models import OrderRequest, TradingMode

logger = logging.getLogger(__name__)


class CCXTBrokerRouterSkill:
    """Resolve best broker/exchange route for a normalized order request."""

    def __init__(self, default_live_broker: str = "binance") -> None:
        self.default_live_broker = default_live_broker

    def route(self, request: OrderRequest) -> Dict[str, Any]:
        """
        Decide route target without executing.

        Paper mode always routes to paper executor.
        Live mode routes by explicit broker or default broker.
        """
        if request.mode == TradingMode.PAPER:
            return {"route": "paper", "reason": "paper mode isolation"}
        if request.mode == TradingMode.BACKTEST:
            return {"route": "none", "reason": "backtest never routes to brokers"}
        broker = request.broker or self.default_live_broker
        return {"route": broker, "reason": "live execution route"}

    def normalize_symbol(self, symbol: str, broker: str) -> str:
        """Normalize symbol by broker conventions."""
        symbol = symbol.upper().replace("-", "/")
        if broker == "binance" and "/" not in symbol:
            if symbol.endswith("USDT"):
                return f"{symbol[:-4]}/USDT"
            return f"{symbol}/USDT"
        return symbol

--- END FILE: skills\ccxt_broker_router.py ---

--- START FILE: skills\chatbot_command_parser.py ---
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

--- END FILE: skills\chatbot_command_parser.py ---

--- START FILE: skills\market_data_router.py ---
"""Market data router for agents.

Goal: fetch *real* market data from the best available source.

Order of preference:
1) Exchange/broker public market data (e.g. Binance OHLCV via CCXT for crypto).
2) yfinance as universal fallback (equities, indices, crypto tickers like BTC-USD).

This is read-only market data. Trading/execution stays in execution layer.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


def _normalize_yfinance(frame: pd.DataFrame) -> pd.DataFrame:
    df = frame.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [str(col[0]) for col in df.columns]
    if "Close" not in df:
        raise ValueError("yfinance frame missing Close column")
    close_obj = df["Close"]
    if isinstance(close_obj, pd.DataFrame):
        close_obj = close_obj.iloc[:, 0]
    df["Close"] = pd.to_numeric(close_obj, errors="coerce")
    return df.dropna().copy()


async def _yf_download(symbol: str, lookback_days: int, interval: str) -> pd.DataFrame:
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=lookback_days)
    frame = await asyncio.to_thread(
        yf.download,
        tickers=symbol,
        start=start,
        end=end,
        interval=interval,
        auto_adjust=False,
        progress=False,
    )
    if frame.empty:
        raise ValueError(f"No yfinance data for symbol={symbol} interval={interval}")
    return _normalize_yfinance(frame)


async def _ccxt_ohlcv(exchange_id: str, symbol: str, timeframe: str, limit: int) -> pd.DataFrame:
    try:
        import ccxt.async_support as ccxt_async  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("ccxt is required for exchange market data") from exc

    ex_cls = getattr(ccxt_async, exchange_id)
    ex = ex_cls({"enableRateLimit": True})
    try:
        bars = await ex.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    finally:
        try:
            await ex.close()
        except Exception:
            pass
    # bars: [timestamp, open, high, low, close, volume]
    df = pd.DataFrame(bars, columns=["ts", "Open", "High", "Low", "Close", "Volume"])
    df["Date"] = pd.to_datetime(df["ts"], unit="ms", utc=True)
    df = df.drop(columns=["ts"]).set_index("Date")
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
    return df.dropna().copy()


@dataclass(slots=True)
class MarketDataRouter:
    """Market data router with best-effort provider selection."""

    crypto_exchange_id: str = "binance"

    def _is_ccxt_symbol(self, symbol: str) -> bool:
        return "/" in symbol and len(symbol.split("/")) == 2

    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1d",
        lookback_days: int = 180,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Return (dataframe, meta) where dataframe contains at least Close.
        """
        if self._is_ccxt_symbol(symbol):
            # Approximate limit for daily/hours.
            limit = min(max(int(lookback_days * 2), 50), 1000)
            df = await _ccxt_ohlcv(self.crypto_exchange_id, symbol, timeframe, limit=limit)
            return df, {"provider": f"ccxt:{self.crypto_exchange_id}"}
        df = await _yf_download(symbol, lookback_days=lookback_days, interval=timeframe)
        return df, {"provider": "yfinance"}

    async def get_latest_price(self, symbol: str) -> Tuple[float, Dict[str, Any]]:
        df, meta = await self.get_ohlcv(symbol, timeframe="1d", lookback_days=10)
        close = df["Close"].iloc[-1]
        if isinstance(close, pd.Series):
            close = close.iloc[0]
        return float(close), meta


--- END FILE: skills\market_data_router.py ---

--- START FILE: skills\news_intelligence_skill.py ---
"""News and sentiment intelligence skill."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import urllib.parse
import urllib.request
from typing import Any, Dict, List

import yfinance as yf

logger = logging.getLogger(__name__)


class NewsIntelligenceSkill:
    """Fetch ticker news and compute lightweight sentiment."""

    POSITIVE_WORDS = {"beat", "growth", "upgrade", "surge", "profit", "record", "bullish", "strong"}
    NEGATIVE_WORDS = {"miss", "downgrade", "decline", "loss", "lawsuit", "bearish", "weak", "drop"}

    async def fetch_news(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch news via NewsAPI (if configured) or yfinance fallback."""
        key = os.getenv("NEWSAPI_KEY", "").strip()
        if key:
            try:
                return await asyncio.to_thread(
                    lambda: self._fetch_newsapi(symbol=symbol, limit=limit, api_key=key)
                )
            except Exception as exc:  # noqa: BLE001
                # Never block the agents on NewsAPI flakiness; fall back to yfinance.
                logger.warning("NewsAPI fetch failed; falling back to yfinance symbol=%s error=%s", symbol, exc)
        ticker = yf.Ticker(symbol)
        news = await asyncio.to_thread(lambda: ticker.news)
        if not news:
            return []
        return news[:limit]

    def _fetch_newsapi(self, symbol: str, limit: int, api_key: str) -> List[Dict[str, Any]]:
        # NewsAPI does not like exchange suffixes; keep a readable query.
        query = symbol.replace(".NS", "").replace("-USD", "").replace("/", " ")
        params = {
            "q": query,
            "pageSize": str(max(1, min(50, int(limit)))),
            "sortBy": "publishedAt",
            "language": "en",
            "apiKey": api_key,
        }
        url = "https://newsapi.org/v2/everything?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, method="GET")
        # Keep this very short so agents stay responsive.
        timeout_sec = float(os.getenv("NEWSAPI_TIMEOUT_SEC", "4.5"))
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            body = resp.read().decode("utf-8")
        data = json.loads(body) if body else {}
        articles = data.get("articles") or []
        out: List[Dict[str, Any]] = []
        for a in articles[:limit]:
            out.append(
                {
                    "title": a.get("title") or "",
                    "link": a.get("url") or "",
                    "source": (a.get("source") or {}).get("name"),
                    "publishedAt": a.get("publishedAt"),
                }
            )
        return out

    def score_sentiment(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Lexicon sentiment score for headlines."""
        score = 0
        analyzed: List[Dict[str, Any]] = []
        for item in items:
            title = (item.get("title") or "").lower()
            words = set(title.split())
            pos_hits = len(words & self.POSITIVE_WORDS)
            neg_hits = len(words & self.NEGATIVE_WORDS)
            item_score = pos_hits - neg_hits
            score += item_score
            analyzed.append({"title": item.get("title", ""), "score": item_score, "link": item.get("link")})
        label = "neutral"
        if score > 2:
            label = "positive"
        elif score < -2:
            label = "negative"
        return {"label": label, "aggregate_score": score, "items": analyzed}

    async def analyze(self, symbol: str) -> Dict[str, Any]:
        """Fetch and score sentiment for a symbol."""
        try:
            items = await self.fetch_news(symbol)
            sentiment = self.score_sentiment(items)
            return {"symbol": symbol, "count": len(items), "sentiment": sentiment}
        except Exception as exc:  # noqa: BLE001
            logger.exception("News analysis failed symbol=%s", symbol)
            return {"symbol": symbol, "error": str(exc), "count": 0, "sentiment": {"label": "unknown"}}

--- END FILE: skills\news_intelligence_skill.py ---

--- START FILE: skills\pinescript_strategy_generator.py ---
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

--- END FILE: skills\pinescript_strategy_generator.py ---

--- START FILE: skills\symbol_resolver.py ---
"""Resolve human-friendly names into tradable symbols/tickers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict


def _canon(text: str) -> str:
    t = text.strip().lower()
    t = re.sub(r"[^a-z0-9]+", " ", t).strip()
    t = re.sub(r"\s+", " ", t)
    if t.startswith("the "):
        t = t[4:]
    return t


@dataclass(slots=True)
class SymbolResolver:
    """
    Resolve phrases like "tata motors" to ticker symbols like "TATAMOTORS.NS".

    This is intentionally conservative and small; expand as needed.
    """

    mapping: Dict[str, str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.mapping is None:
            self.mapping = {
                "tata motors": "TATAMOTORS.NS",
                "tata moters": "TATAMOTORS.NS",
                "tata motor": "TATAMOTORS.NS",
                "tatamotors": "TATAMOTORS.NS",
                "tata steel": "TATASTEEL.NS",
                "tata steeel": "TATASTEEL.NS",
                "tatasteel": "TATASTEEL.NS",
                "infosys": "INFY.NS",
                "infy": "INFY.NS",
                "reliance": "RELIANCE.NS",
                "nifty": "^NSEI",
                "bank nifty": "^NSEBANK",
                "btc": "BTC-USD",
                "bitcoin": "BTC-USD",
                "eth": "ETH-USD",
                "ethereum": "ETH-USD",
            }

    def resolve(self, raw: str) -> str:
        """Return best-effort resolved ticker."""
        text = raw.strip()
        if not text:
            return text
        # If it already looks like a ticker, keep it.
        if " " not in text:
            return text
        key = _canon(text)
        return self.mapping.get(key, text.replace(" ", ""))

--- END FILE: skills\symbol_resolver.py ---

--- START FILE: skills\technical_analysis_skill.py ---
"""Technical analysis utilities for research agents."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Dict, List
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class TechnicalSnapshot:
    """Indicator snapshot for a symbol/timeframe."""

    symbol: str
    timeframe: str
    close: float
    ema_fast: float
    ema_slow: float
    rsi: float
    trend: str
    signal: str


class TechnicalAnalysisSkill:
    """
    Multi-timeframe technical analysis skill.

    Unit-test example:
        >>> skill = TechnicalAnalysisSkill()
        >>> isinstance(skill._compute_rsi(pd.Series([1,2,3,2,4])), pd.Series)
        True
    """

    def __init__(self, ema_fast: int = 21, ema_slow: int = 55, rsi_period: int = 14) -> None:
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow
        self.rsi_period = rsi_period

    async def analyze_symbol(self, symbol: str, timeframe: str = "1d", lookback: str = "6mo") -> TechnicalSnapshot:
        """Download OHLCV and compute indicator snapshot."""
        frame = await asyncio.to_thread(
            yf.download,
            tickers=symbol,
            period=lookback,
            interval=timeframe,
            auto_adjust=False,
            progress=False,
        )
        if frame.empty:
            raise ValueError(f"No data returned for symbol={symbol} timeframe={timeframe}")
        frame = self._normalize_columns(frame).copy()
        close = self._extract_close(frame)
        frame = frame.loc[close.dropna().index].copy()
        close = close.loc[frame.index]
        frame["Close"] = close
        frame["ema_fast"] = close.ewm(span=self.ema_fast, adjust=False).mean()
        frame["ema_slow"] = close.ewm(span=self.ema_slow, adjust=False).mean()
        frame["rsi"] = self._compute_rsi(close)
        last = frame.iloc[-1]
        ema_fast = self._as_scalar(last["ema_fast"])
        ema_slow = self._as_scalar(last["ema_slow"])
        rsi = self._as_scalar(last["rsi"])
        close_last = self._as_scalar(last["Close"])
        trend = "bullish" if ema_fast > ema_slow else "bearish"
        signal = "hold"
        if trend == "bullish" and rsi < 70:
            signal = "buy_bias"
        elif trend == "bearish" and rsi > 30:
            signal = "sell_bias"
        return TechnicalSnapshot(
            symbol=symbol,
            timeframe=timeframe,
            close=close_last,
            ema_fast=ema_fast,
            ema_slow=ema_slow,
            rsi=rsi,
            trend=trend,
            signal=signal,
        )

    async def analyze_multi_asset(
        self, symbols: List[str], timeframe: str = "1d", lookback: str = "6mo"
    ) -> Dict[str, TechnicalSnapshot]:
        """Analyze multiple symbols concurrently."""
        tasks = [self.analyze_symbol(symbol=s, timeframe=timeframe, lookback=lookback) for s in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        output: Dict[str, TechnicalSnapshot] = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                logger.exception("Technical analysis failed for symbol=%s", symbol, exc_info=result)
                continue
            output[symbol] = result
        return output

    def _compute_rsi(self, close: pd.Series) -> pd.Series:
        """Compute RSI with Wilder smoothing."""
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)
        avg_gain = gain.ewm(alpha=1 / self.rsi_period, min_periods=self.rsi_period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / self.rsi_period, min_periods=self.rsi_period, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, pd.NA)
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50.0)

    def _normalize_columns(self, frame: pd.DataFrame) -> pd.DataFrame:
        """Flatten yfinance multi-index columns to single level."""
        if isinstance(frame.columns, pd.MultiIndex):
            frame = frame.copy()
            frame.columns = [str(col[0]) for col in frame.columns]
        return frame

    def _extract_close(self, frame: pd.DataFrame) -> pd.Series:
        """Extract one numeric close series from dataframe."""
        close_obj = frame["Close"]
        if isinstance(close_obj, pd.DataFrame):
            close_obj = close_obj.iloc[:, 0]
        close = pd.to_numeric(close_obj, errors="coerce")
        if close.empty:
            raise ValueError("No valid close series available for analysis.")
        return close

    def _as_scalar(self, value: object) -> float:
        """Convert pandas scalar/1-item series to float safely."""
        if isinstance(value, pd.Series):
            if value.empty:
                raise ValueError("Received empty series where scalar was expected.")
            value = value.iloc[0]
        return float(value)

--- END FILE: skills\technical_analysis_skill.py ---

--- START FILE: skills\whale_tracker_skill.py ---
"""Hyperliquid whale tracking and smart-money analytics."""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import aiohttp

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class WhaleAlert:
    """Large transaction or flow regime alert."""

    coin: str
    side: str
    notional_usd: float
    reason: str
    tx_hash: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class WhaleTrackerSkill:
    """
    Whale tracking with Hyperliquid market data.

    Features:
    - Whale accumulation detection
    - Smart money sentiment
    - Direction change tracking
    - Large transaction alerts
    """

    def __init__(
        self,
        info_url: str = "https://api.hyperliquid.xyz/info",
        large_tx_threshold_usd: float = 250_000.0,
        accumulation_threshold_usd: float = 1_000_000.0,
        timeout_sec: int = 20,
    ) -> None:
        self.info_url = info_url
        self.large_tx_threshold_usd = large_tx_threshold_usd
        self.accumulation_threshold_usd = accumulation_threshold_usd
        self.timeout_sec = timeout_sec
        self._last_direction: Dict[str, str] = {}

    async def fetch_recent_trades(self, coin: str) -> List[Dict[str, Any]]:
        """Fetch recent trades from Hyperliquid."""
        payload = {"type": "recentTrades", "coin": coin.upper()}
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout_sec)) as session:
            async with session.post(self.info_url, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                if not isinstance(data, list):
                    raise ValueError("Unexpected Hyperliquid recentTrades response")
                return data

    async def fetch_context(self, coin: str) -> Dict[str, Any]:
        """Fetch market context for normalization."""
        payload = {"type": "metaAndAssetCtxs"}
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout_sec)) as session:
            async with session.post(self.info_url, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                if not isinstance(data, list) or len(data) < 2:
                    return {"coin": coin.upper(), "context_available": False}
                return {"coin": coin.upper(), "context_available": True, "raw": data}

    async def analyze_whale_activity(self, coin: str = "BTC") -> Dict[str, Any]:
        """Compute whale flow analytics and alerts."""
        try:
            trades = await self.fetch_recent_trades(coin)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Whale tracker fetch failed coin=%s", coin)
            return {"coin": coin.upper(), "error": str(exc), "alerts": [], "sentiment": "unknown"}

        alerts = self._detect_large_transactions(coin.upper(), trades)
        accumulation = self._detect_accumulation(coin.upper(), trades)
        sentiment = self._smart_money_sentiment(trades)
        direction_change = self._track_direction_change(coin.upper(), sentiment["direction"])

        if accumulation["detected"]:
            alerts.append(
                WhaleAlert(
                    coin=coin.upper(),
                    side=accumulation["side"],
                    notional_usd=accumulation["net_notional_usd"],
                    reason="whale_accumulation_detected",
                )
            )
        if direction_change["changed"]:
            alerts.append(
                WhaleAlert(
                    coin=coin.upper(),
                    side=direction_change["to"],
                    notional_usd=abs(accumulation["net_notional_usd"]),
                    reason=f"direction_change_{direction_change['from']}_to_{direction_change['to']}",
                )
            )

        return {
            "coin": coin.upper(),
            "trade_count": len(trades),
            "sentiment": sentiment["label"],
            "direction": sentiment["direction"],
            "net_notional_usd": accumulation["net_notional_usd"],
            "accumulation": accumulation,
            "direction_change": direction_change,
            "alerts": [asdict(a) for a in alerts],
        }

    def _detect_large_transactions(self, coin: str, trades: List[Dict[str, Any]]) -> List[WhaleAlert]:
        """Flag large notional transactions."""
        alerts: List[WhaleAlert] = []
        for trade in trades:
            try:
                px = float(trade.get("px") or trade.get("price") or 0)
                sz = float(trade.get("sz") or trade.get("size") or 0)
                side = "buy" if bool(trade.get("side", "B").lower().startswith("b")) else "sell"
                notional = px * sz
            except Exception:
                continue
            if notional >= self.large_tx_threshold_usd:
                alerts.append(
                    WhaleAlert(
                        coin=coin,
                        side=side,
                        notional_usd=notional,
                        reason="large_transaction",
                        tx_hash=trade.get("hash") or trade.get("txHash"),
                    )
                )
        return alerts

    def _detect_accumulation(self, coin: str, trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect buy/sell imbalance as accumulation or distribution."""
        buy_notional = 0.0
        sell_notional = 0.0
        for trade in trades:
            try:
                px = float(trade.get("px") or trade.get("price") or 0)
                sz = float(trade.get("sz") or trade.get("size") or 0)
                side = "buy" if bool(trade.get("side", "B").lower().startswith("b")) else "sell"
                n = px * sz
            except Exception:
                continue
            if side == "buy":
                buy_notional += n
            else:
                sell_notional += n
        net = buy_notional - sell_notional
        detected = abs(net) >= self.accumulation_threshold_usd
        side = "buy" if net > 0 else "sell"
        return {
            "coin": coin,
            "buy_notional_usd": buy_notional,
            "sell_notional_usd": sell_notional,
            "net_notional_usd": net,
            "detected": detected,
            "side": side,
        }

    def _smart_money_sentiment(self, trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate sentiment from flow imbalance."""
        buy_notional = 0.0
        sell_notional = 0.0
        for trade in trades:
            try:
                px = float(trade.get("px") or trade.get("price") or 0)
                sz = float(trade.get("sz") or trade.get("size") or 0)
                side = "buy" if bool(trade.get("side", "B").lower().startswith("b")) else "sell"
                notional = px * sz
            except Exception:
                continue
            if side == "buy":
                buy_notional += notional
            else:
                sell_notional += notional
        total = buy_notional + sell_notional
        if total <= 0:
            return {"label": "neutral", "direction": "neutral", "score": 0.0}
        ratio = (buy_notional - sell_notional) / total
        if ratio > 0.2:
            label = "bullish_whales"
            direction = "up"
        elif ratio < -0.2:
            label = "bearish_whales"
            direction = "down"
        else:
            label = "neutral_whales"
            direction = "neutral"
        return {"label": label, "direction": direction, "score": ratio}

    def _track_direction_change(self, coin: str, direction: str) -> Dict[str, Any]:
        """Track directional regime transitions."""
        previous = self._last_direction.get(coin, "unknown")
        changed = previous != "unknown" and previous != direction
        self._last_direction[coin] = direction
        return {"coin": coin, "from": previous, "to": direction, "changed": changed}

--- END FILE: skills\whale_tracker_skill.py ---

--- START FILE: skills\__init__.py ---
from .technical_analysis_skill import TechnicalAnalysisSkill
from .whale_tracker_skill import WhaleTrackerSkill
from .news_intelligence_skill import NewsIntelligenceSkill
from .backtesting_skill import BacktestingSkill
from .pinescript_strategy_generator import PineScriptStrategyGenerator
from .market_data_router import MarketDataRouter
from .symbol_resolver import SymbolResolver

__all__ = [
    "TechnicalAnalysisSkill",
    "WhaleTrackerSkill",
    "NewsIntelligenceSkill",
    "BacktestingSkill",
    "PineScriptStrategyGenerator",
    "MarketDataRouter",
    "SymbolResolver",
]

--- END FILE: skills\__init__.py ---

--- START FILE: tests\integration_tests.py ---
"""Integration tests for event-driven risk-gated execution."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from trading_system.agents.risk_guardian import RiskGuardian
from trading_system.config.models import OrderRequest, OrderSide, RiskLimits, TradingMode
from trading_system.events.event_bus import AsyncEventBus
from trading_system.events.event_types import EventType
from trading_system.execution.broker_router import BrokerRouter
from trading_system.execution.execution_engine import ExecutionEngine
from trading_system.execution.kill_switch import KillSwitch
from trading_system.execution.live_executor import LiveExecutor
from trading_system.execution.paper_executor import PaperExecutor
from trading_system.memory.global_state import GlobalState
from trading_system.memory.trade_memory import TradeMemoryRepository


@pytest.mark.asyncio
async def test_paper_order_flow_emits_events(tmp_path: Path) -> None:
    db_path = str(tmp_path / "integration.db")
    trade_memory = TradeMemoryRepository(sqlite_path=db_path)
    await trade_memory.initialize()

    event_bus = AsyncEventBus(queue_size=1000, worker_count=1)
    await event_bus.start()
    emitted = []

    async def collector(event):
        emitted.append(event.event_type.value)

    event_bus.subscribe(EventType.RISK_APPROVED, collector)
    event_bus.subscribe(EventType.TRADE_EXECUTED, collector)

    state = GlobalState(initial_balance=100000)
    guardian = RiskGuardian(
        limits=RiskLimits(
            max_daily_loss=5000,
            max_exposure=200000,
            max_leverage=2,
            max_symbol_exposure_pct=50,
            max_slippage_bps=50,
            max_consecutive_losses=5,
            max_correlation=0.9,
        )
    )
    kill_switch = KillSwitch()
    paper = PaperExecutor(global_state=state, trade_memory=trade_memory)
    live = LiveExecutor(broker_router=BrokerRouter(adapters={}), trade_memory=trade_memory)

    engine = ExecutionEngine(
        risk_guardian=guardian,
        kill_switch=kill_switch,
        paper_executor=paper,
        live_executor=live,
        global_state=state,
        trade_memory=trade_memory,
        event_bus=event_bus,
    )

    order = OrderRequest(
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        quantity=0.5,
        mode=TradingMode.PAPER,
        broker="paper",
        stop_loss=95000,
        metadata={"mark_price": 100000},
    )
    result = await engine.submit_order(order)
    await asyncio.sleep(0.1)
    await event_bus.stop()

    assert result.accepted is True
    assert "RiskApproved" in emitted
    assert "TradeExecuted" in emitted


@pytest.mark.asyncio
async def test_risk_rejects_without_stop_loss(tmp_path: Path) -> None:
    db_path = str(tmp_path / "integration2.db")
    trade_memory = TradeMemoryRepository(sqlite_path=db_path)
    await trade_memory.initialize()
    event_bus = AsyncEventBus(queue_size=1000, worker_count=1)
    await event_bus.start()
    state = GlobalState(initial_balance=100000)
    guardian = RiskGuardian(limits=RiskLimits())
    engine = ExecutionEngine(
        risk_guardian=guardian,
        kill_switch=KillSwitch(),
        paper_executor=PaperExecutor(global_state=state, trade_memory=trade_memory),
        live_executor=LiveExecutor(broker_router=BrokerRouter(adapters={}), trade_memory=trade_memory),
        global_state=state,
        trade_memory=trade_memory,
        event_bus=event_bus,
    )
    order = OrderRequest(
        symbol="ETH/USDT",
        side=OrderSide.BUY,
        quantity=1,
        mode=TradingMode.PAPER,
        broker="paper",
        metadata={"mark_price": 3000},
    )
    result = await engine.submit_order(order)
    await event_bus.stop()
    assert result.accepted is False
    assert "Risk rejected" in result.message

--- END FILE: tests\integration_tests.py ---

--- START FILE: tests\test_backtesting.py ---
"""Unit tests for backtesting skill."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest

from trading_system.config.models import BacktestRequest
from trading_system.skills.backtesting_skill import BacktestingSkill


def _synthetic_frame(rows: int = 180) -> pd.DataFrame:
    ts = pd.date_range(end=datetime.now(timezone.utc), periods=rows, freq="D")
    close = pd.Series([100 + i * 0.2 + (i % 7) for i in range(rows)], index=ts)
    return pd.DataFrame(
        {
            "Open": close * 0.995,
            "High": close * 1.01,
            "Low": close * 0.99,
            "Close": close,
            "Volume": 1000,
        }
    )


@pytest.mark.asyncio
async def test_backtest_ema_metrics() -> None:
    backtester = BacktestingSkill()

    async def fake_loader(request: BacktestRequest):
        return {"BTC-USD": _synthetic_frame(220)}

    backtester._load_multi_asset_data = fake_loader  # type: ignore[method-assign]
    req = BacktestRequest(
        symbols=["BTC-USD"],
        timeframe="1d",
        strategy_name="ema_crossover",
        lookback_days=180,
        walk_forward_windows=3,
    )
    result = await backtester.run(req)
    assert result.metrics.total_trades >= 0
    assert result.metrics.max_drawdown >= 0
    assert result.metrics.win_rate >= 0
    assert isinstance(result.walk_forward, list)


@pytest.mark.asyncio
async def test_backtest_rsi_strategy() -> None:
    backtester = BacktestingSkill()

    async def fake_loader(request: BacktestRequest):
        frame = _synthetic_frame(250)
        frame["Close"] = frame["Close"].rolling(5).mean().bfill()
        return {"ETH-USD": frame}

    backtester._load_multi_asset_data = fake_loader  # type: ignore[method-assign]
    req = BacktestRequest(
        symbols=["ETH-USD"],
        strategy_name="rsi_reversion",
        strategy_params={"period": 14, "oversold": 35, "exit": 55},
        lookback_days=200,
    )
    result = await backtester.run(req)
    assert result.metrics.total_trades >= 0
    assert result.metrics.profit_factor >= 0

--- END FILE: tests\test_backtesting.py ---

--- START FILE: tests\test_chatbot.py ---
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

--- END FILE: tests\test_chatbot.py ---

--- START FILE: tests\test_live_approval.py ---
"""Unit tests for live approval ticket workflow."""

from __future__ import annotations

import pytest

from trading_system.agents.risk_guardian import RiskGuardian
from trading_system.config.models import OrderRequest, OrderSide, RiskLimits, TradingMode
from trading_system.events.event_bus import AsyncEventBus
from trading_system.execution.broker_router import BrokerRouter
from trading_system.execution.execution_engine import ExecutionEngine
from trading_system.execution.kill_switch import KillSwitch
from trading_system.execution.live_approval import LiveApprovalManager
from trading_system.execution.live_executor import LiveExecutor
from trading_system.execution.paper_executor import PaperExecutor
from trading_system.memory.global_state import GlobalState
from trading_system.memory.trade_memory import TradeMemoryRepository


def _live_order() -> OrderRequest:
    return OrderRequest(
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        quantity=0.01,
        mode=TradingMode.LIVE,
        broker="binance",
        stop_loss=95000,
        metadata={"mark_price": 100000},
    )


@pytest.mark.asyncio
async def test_live_ticket_lifecycle() -> None:
    manager = LiveApprovalManager(ttl_seconds=60)
    order = _live_order()
    ticket = await manager.create_ticket(order, requested_by="alice")
    assert ticket["approved"] is False
    approved = await manager.approve_ticket(ticket["ticket_id"], approved_by="bob")
    assert approved["approved"] is True
    consumed = await manager.consume_for_order(ticket["ticket_id"], order)
    assert consumed is True
    replay = await manager.consume_for_order(ticket["ticket_id"], order)
    assert replay is False


@pytest.mark.asyncio
async def test_execution_engine_rejects_live_without_ticket(tmp_path) -> None:
    db_path = str(tmp_path / "approval.db")
    trade_memory = TradeMemoryRepository(db_path)
    await trade_memory.initialize()
    event_bus = AsyncEventBus(worker_count=1)
    await event_bus.start()
    state = GlobalState(initial_balance=100000)
    manager = LiveApprovalManager(ttl_seconds=60)
    engine = ExecutionEngine(
        risk_guardian=RiskGuardian(RiskLimits()),
        kill_switch=KillSwitch(),
        paper_executor=PaperExecutor(state, trade_memory),
        live_executor=LiveExecutor(BrokerRouter(adapters={}), trade_memory),
        global_state=state,
        trade_memory=trade_memory,
        event_bus=event_bus,
        live_approval_manager=manager,
        require_live_approval_ticket=True,
    )
    result = await engine.submit_order(_live_order())
    await event_bus.stop()
    assert result.accepted is False
    assert "approval_ticket_id" in result.message

--- END FILE: tests\test_live_approval.py ---

--- START FILE: tests\test_router.py ---
"""Unit tests for broker routing skill."""

from __future__ import annotations

from trading_system.config.models import OrderRequest, OrderSide, TradingMode
from trading_system.skills.ccxt_broker_router import CCXTBrokerRouterSkill


def test_ccxt_router_modes() -> None:
    router = CCXTBrokerRouterSkill(default_live_broker="binance")
    paper_req = OrderRequest(
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        quantity=1,
        mode=TradingMode.PAPER,
        stop_loss=95000,
        metadata={"mark_price": 100000},
    )
    live_req = OrderRequest(
        symbol="BTCUSDT",
        side=OrderSide.BUY,
        quantity=1,
        mode=TradingMode.LIVE,
        broker="binance",
        stop_loss=95000,
        metadata={"mark_price": 100000},
    )
    assert router.route(paper_req)["route"] == "paper"
    assert router.route(live_req)["route"] == "binance"
    assert router.normalize_symbol("btcusdt", "binance") == "BTC/USDT"

--- END FILE: tests\test_router.py ---

--- START FILE: tests\test_whale_tracker.py ---
"""Unit tests for whale tracker logic."""

from __future__ import annotations

import pytest

from trading_system.skills.whale_tracker_skill import WhaleTrackerSkill


def _mock_trades():
    return [
        {"px": "65000", "sz": "10", "side": "B", "hash": "tx1"},
        {"px": "64950", "sz": "8", "side": "B", "hash": "tx2"},
        {"px": "65120", "sz": "3", "side": "S", "hash": "tx3"},
    ]


@pytest.mark.asyncio
async def test_whale_detection_without_network() -> None:
    tracker = WhaleTrackerSkill(large_tx_threshold_usd=200000, accumulation_threshold_usd=300000)

    async def fake_recent_trades(coin: str):
        return _mock_trades()

    tracker.fetch_recent_trades = fake_recent_trades  # type: ignore[method-assign]
    report = await tracker.analyze_whale_activity("BTC")
    assert report["coin"] == "BTC"
    assert report["sentiment"] in {"bullish_whales", "bearish_whales", "neutral_whales"}
    assert isinstance(report["alerts"], list)
    assert report["accumulation"]["detected"] is True

--- END FILE: tests\test_whale_tracker.py ---

--- START FILE: tests\__init__.py ---

--- END FILE: tests\__init__.py ---

--- START FILE: tools\test_hermes_bridge.ps1 ---
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$proj = Resolve-Path (Join-Path $root "..")
Set-Location $proj

Write-Host "Project:" $proj

if (Test-Path ".\.env") {
  Write-Host "Loading .env ..."
  Get-Content .\.env | ForEach-Object {
    if ($_ -match "^\s*#") { return }
    if ($_ -match "^\s*$") { return }
    $kv = $_.Split("=", 2)
    if ($kv.Count -eq 2) {
      $name = $kv[0].Trim()
      $val = $kv[1].Trim()
      if ($name) {
        # PowerShell doesn't allow dynamic $env:$name assignment directly.
        # Use the Env: drive instead.
        if ($val.StartsWith('"') -and $val.EndsWith('"')) { $val = $val.Trim('"') }
        if ($val.StartsWith("'") -and $val.EndsWith("'")) { $val = $val.Trim("'") }
        Set-Item -Path ("Env:" + $name) -Value $val
      }
    }
  }
}

if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
  throw "ssh not found. Install OpenSSH Client on Windows."
}

# Helper: run a command array and return @{ out=...; code=... }
function Invoke-CmdArray {
  param([string[]]$CmdArgs)
  if (-not $CmdArgs -or $CmdArgs.Count -lt 1) {
    return @{ out = "No command args provided."; code = 1 }
  }
  if ($CmdArgs.Count -eq 1) {
    $out = & $CmdArgs[0] 2>&1
    return @{ out = $out; code = $LASTEXITCODE }
  }
  $out = & $CmdArgs[0] $CmdArgs[1..($CmdArgs.Count-1)] 2>&1
  return @{ out = $out; code = $LASTEXITCODE }
}

# IMPORTANT: $Host is a built-in, read-only PowerShell variable (case-insensitive).
# Use distinct variable names.
$hermesCmd = $env:HERMES_CMD
$hermesWslDistro = $env:HERMES_WSL_DISTRO
$hermesHost = $env:HERMES_SSH_HOST
$hermesUser = $env:HERMES_SSH_USER
$hermesPort = $env:HERMES_SSH_PORT
$hermesKey  = $env:HERMES_SSH_IDENTITY_FILE

if ($hermesCmd) {
  Write-Host "Using HERMES_CMD from .env:" $hermesCmd
  $args = @()
  $args += ($hermesCmd -split ' ')
  $args += @("--version")
  Write-Host "Running:" ($args -join " ")

  $res = Invoke-CmdArray -CmdArgs $args
  if ($res.code -eq 0) {
    Write-Host $res.out
    Write-Host "OK: Hermes reachable via HERMES_CMD"
    exit 0
  }

  # If user configured "wsl hermes" but Hermes isn't on PATH, attempt safe fallbacks.
  # This prevents the common "/bin/bash: hermes: command not found" issue.
  if ($args[0] -match '^(wsl|wsl\.exe)$') {
    $fallbackHermes = "/home/ambat/.local/bin/hermes"

    $wslArgs = @("wsl")
    if ($hermesWslDistro) { $wslArgs += @("-d", $hermesWslDistro) }
    $wslArgs += @("--", $fallbackHermes, "--version")

    Write-Host "HERMES_CMD failed (exit=$($res.code)). Trying WSL fallback:" ($wslArgs -join " ")
    $res2 = Invoke-CmdArray -CmdArgs $wslArgs
    if ($res2.code -eq 0) {
      Write-Host $res2.out
      Write-Host "OK: Hermes reachable via WSL fallback ($fallbackHermes)"
      exit 0
    }

    # Last resort: run via bash -lc so login PATH is loaded (if Hermes is installed but PATH isn't).
    $bashCmd = "command -v hermes >/dev/null 2>&1 && hermes --version || $fallbackHermes --version"
    $wslArgs3 = @("wsl")
    if ($hermesWslDistro) { $wslArgs3 += @("-d", $hermesWslDistro) }
    $wslArgs3 += @("--", "bash", "-lc", $bashCmd)
    Write-Host "Trying WSL login-shell fallback:" ($wslArgs3 -join " ")
    $res3 = Invoke-CmdArray -CmdArgs $wslArgs3
    if ($res3.code -eq 0) {
      Write-Host $res3.out
      Write-Host "OK: Hermes reachable via WSL login-shell fallback"
      exit 0
    }
  }

  Write-Host $res.out
  Write-Host "Hermes failed via HERMES_CMD (exit=$($res.code))."
  Write-Host "Falling back to SSH mode (if HERMES_SSH_* is configured)..."
}

if (-not $hermesHost) { throw "HERMES_SSH_HOST is empty in .env and HERMES_CMD not set." }
if (-not $hermesUser) { throw "HERMES_SSH_USER is empty in .env" }
if (-not $hermesPort) { $hermesPort = "22" }

$dest = "$hermesUser@$hermesHost"

$args = @(
  "-T",
  "-o", "BatchMode=yes",
  "-o", "ConnectTimeout=6",
  "-o", "StrictHostKeyChecking=accept-new",
  "-p", "$hermesPort"
)
if ($hermesKey) { $args += @("-i", "$hermesKey") }
$args += @("$dest", "hermes", "--version")

Write-Host "Running:" "ssh" ($args -join " ")
$out = & ssh @args 2>&1
$code = $LASTEXITCODE
if ($code -ne 0) {
  Write-Host $out
  throw "SSH/Hermes failed (exit=$code). Fix SSH server/auth and retry."
}
Write-Host $out
Write-Host "OK: Hermes reachable over SSH"

--- END FILE: tools\test_hermes_bridge.ps1 ---

--- START FILE: trading-dashboard\.gitignore ---
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv
pip-log.txt
pip-delete-this-directory.txt
.pytest_cache/
*.egg-info/
build/
*.db
trading.db

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
.DS_Store

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local
--- END FILE: trading-dashboard\.gitignore ---

--- START FILE: trading-dashboard\.python-version ---
3.11.11

--- END FILE: trading-dashboard\.python-version ---

--- START FILE: trading-dashboard\build.sh ---
#!/bin/bash
set -e

if [ "${SKIP_FRONTEND_BUILD}" = "true" ]; then
  echo "SKIP_FRONTEND_BUILD=true; skipping frontend build."
else
  echo "Building frontend..."
  cd frontend
  if [ -f package-lock.json ]; then
    npm ci
  else
    npm install
  fi
  npm run build
  cd ..
fi

echo "Installing Python dependencies..."
python -m pip install -r requirements.txt

echo "Build complete!"

--- END FILE: trading-dashboard\build.sh ---

--- START FILE: trading-dashboard\README ---
# Trading Dashboard

A professional AI-powered trading dashboard with real-time agent monitoring and backtesting.

## Features

- Real-time chatbot interface for natural language commands
- Live agent monitoring sidebar with status updates
- Trading operations (place orders, manage positions)
- Strategy management and ranking by P&L
- Backtesting engine with CSV export
- Stock screener with performance ranking
- Agent workflow visualization
- Settings panel for API keys and risk management

## Tech Stack

- **Frontend:** React 18, TypeScript, Tailwind CSS, Vite
- **Backend:** FastAPI, WebSocket, SQLAlchemy
- **Database:** SQLite
- **Deployment:** Render.com

## Getting Started - Local Development

### Prerequisites
- Python 3.11+
- Node.js 16+
- Git

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend runs on http://localhost:8000

### Frontend Setup (new terminal)

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on http://localhost:5173

## Deployment

Push to GitHub. Render.com auto-deploys on every commit.

## API Endpoints

- **POST /chat** - Send command to agents
- **POST /agent-status** - Agents publish status (WebSocket broadcast)
- **POST /backtest** - Run strategy backtest
- **POST /trade** - Execute order
- **GET /positions** - Get active positions
- **GET /strategies** - List all strategies
- **GET /screener** - Get stock screener results
- **POST /settings/keys** - Save API keys
- **WS /ws/agent-monitor** - Live agent updates via WebSocket
- **GET /health** - Health check

## Agent Integration

Your local agents connect to dashboard by:

1. POSTing to `/agent-status` every 5-10 seconds
2. Sending their status, current task, progress, and skills
3. Dashboard broadcasts updates via WebSocket to frontend

## Usage Examples

### Chat Commands

- "analyze INFY 4h" - Technical analysis
- "backtest RSI strategy" - Run backtest
- "stock screener" - Get ranked stocks
- "buy RELIANCE 100" - Place order (paper/live)

### Agent Startup

```bash
python agents/boss_agent.py
```

This starts all child agents:
- analysis_agent
- strategy_agent
- execution_agent
- risk_agent
- news_agent

## Monitoring

- Open dashboard: https://your-domain.com
- Watch Agent Monitor sidebar for real-time status
- All agents should show as "online" when running

## Support

Check the logs:
- Browser: F12 > Console
- Render: Dashboard > Logs
- Terminal: Check output of agents and backend

## License

MIT
--- END FILE: trading-dashboard\README ---

--- START FILE: trading-dashboard\render.yaml ---
services:
  - type: web
    name: trading-dashboard
    env: python
    plan: free
    buildCommand: bash build.sh
    startCommand: python backend/main.py
    envVars:
      - key: PORT
        value: "8000"
      # Pin Python version to avoid Render default upgrades breaking deps (e.g. SQLAlchemy).
      - key: PYTHON_VERSION
        value: "3.11.11"

--- END FILE: trading-dashboard\render.yaml ---

--- START FILE: trading-dashboard\requirements.txt ---
fastapi==0.104.1
uvicorn==0.24.0
websockets==12.0
sqlalchemy==2.0.23
python-dotenv==1.0.0
aiohttp==3.9.1
requests==2.31.0
gunicorn==21.2.0
httpx==0.27.0
cryptography>=42.0.0
python-multipart>=0.0.9
python-jose[cryptography]>=3.3.0
passlib>=1.7.4
textblob>=0.17.1

--- END FILE: trading-dashboard\requirements.txt ---

--- START FILE: trading-dashboard\tsconfig.node.json ---
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}

--- END FILE: trading-dashboard\tsconfig.node.json ---

--- START FILE: trading-dashboard\backend\auth.py ---
"""Dashboard JWT helpers and FastAPI authentication dependencies."""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

try:
    from backend.security.jwt_auth import JwtAuth, load_jwt_auth  # type: ignore
except ModuleNotFoundError:  # noqa: BLE001
    from security.jwt_auth import JwtAuth, load_jwt_auth  # type: ignore

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


def _get_auth() -> Optional[JwtAuth]:
    try:
        return load_jwt_auth()
    except Exception as exc:  # noqa: BLE001
        logger.error("JWT auth loader failed: %s", exc)
        return None


def create_token(username: str, role: str = "user") -> str:
    """Create a signed JWT for the supplied username."""
    auth = _get_auth()
    if not auth:
        raise RuntimeError("JWT_SECRET_KEY is not configured")
    return auth.create_token(username, role=role)


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT. Returns None if invalid."""
    try:
        auth = _get_auth()
        if not auth:
            return None
        return auth.verify_token(token)
    except Exception as exc:  # noqa: BLE001
        logger.debug("decode_token failed: %s", exc)
        return None


async def verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    """FastAPI dependency that extracts and validates a Bearer token."""
    try:
        if not credentials:
            raise HTTPException(status_code=401, detail="Not authenticated")
        payload = decode_token(credentials.credentials)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return {"username": payload.get("sub", ""), "role": payload.get("role", "user")}
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=401, detail=str(exc)) from exc


async def require_admin(user: dict = Depends(verify_token)) -> dict:
    """Dependency that enforces admin role."""
    if str(user.get("role") or "") != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return user


--- END FILE: trading-dashboard\backend\auth.py ---

--- START FILE: trading-dashboard\backend\database.py ---
"""
Trading Dashboard - Database Models
SQLAlchemy ORM models for all tables
"""
import os
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    Index,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import OperationalError

# ─── Database URL ────────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./trading_dashboard.db")

# Fix for Render PostgreSQL URLs
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ─── Engine ──────────────────────────────────────────────────────────────────
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ─── Models ──────────────────────────────────────────────────────────────────

class AgentState(Base):
    """Stores the latest status of each AI agent."""
    __tablename__ = "agent_states"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # Keep this unique, but avoid double-defining an index with the same name across upgrades.
    agent_id = Column(String(100), unique=True, nullable=False)
    status = Column(String(50), default="offline")  # online | idle | processing | error
    task = Column(String(500), default="Waiting...")
    progress = Column(Integer, default=0)  # 0-100
    skills = Column(Text, default="[]")  # JSON array of skill names
    cpu_percent = Column(Float, default=0.0)
    memory_mb = Column(Float, default=0.0)
    timestamp = Column(String(50), nullable=True)

    # NOTE: Do not define an explicit Index for agent_id here.
    # The unique constraint on agent_id is sufficient for lookups and avoids
    # "index ... already exists" errors on SQLite when schemas evolve.


class Strategy(Base):
    """Trading strategies with their parameters and metrics."""
    __tablename__ = "strategies"

    id = Column(String(100), primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    symbol = Column(String(20), nullable=False)
    timeframe = Column(String(10), default="4h")
    entry_rule = Column(Text, default="")
    exit_rule = Column(Text, default="")
    status = Column(String(50), default="paused")  # running | paused | backtesting
    pnl = Column(Float, default=0.0)
    pnl_percent = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    created_date = Column(String(50), nullable=True)
    last_trade = Column(String(50), nullable=True)

    __table_args__ = (
        Index("ix_strategies_symbol", "symbol"),
        Index("ix_strategies_status", "status"),
    )


class BacktestResult(Base):
    """Backtest execution results."""
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy_name = Column(String(200), nullable=False)
    symbol = Column(String(20), nullable=False)
    timeframe = Column(String(10), default="4h")
    total_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    pnl = Column(Float, default=0.0)
    pnl_percent = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    profit_factor = Column(Float, default=0.0)
    consecutive_losses = Column(Integer, default=0)
    csv_file = Column(String(300), nullable=True)
    created_at = Column(String(50), nullable=True)

    __table_args__ = (
        Index("ix_backtest_results_strategy", "strategy_name"),
        Index("ix_backtest_results_symbol", "symbol"),
    )


class Trade(Base):
    """Executed trades (paper and live)."""
    __tablename__ = "trades_executed"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(50), unique=True, index=True)
    symbol = Column(String(20), nullable=False)
    quantity = Column(Integer, default=0)
    entry_price = Column(Float, default=0.0)
    exit_price = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    broker = Column(String(50), default="upstox")
    mode = Column(String(20), default="paper")  # paper | live
    status = Column(String(50), default="open")  # open | filled | cancelled | rejected
    pnl = Column(Float, nullable=True)
    entry_time = Column(String(50), nullable=True)
    exit_time = Column(String(50), nullable=True)

    __table_args__ = (
        Index("ix_trades_symbol", "symbol"),
        Index("ix_trades_mode", "mode"),
        Index("ix_trades_status", "status"),
    )


class ApiKey(Base):
    """Broker API keys (encoded for storage)."""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    broker = Column(String(50), unique=True, index=True, nullable=False)
    api_key_encoded = Column(Text, nullable=False)
    secret_key_encoded = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    connected_date = Column(String(50), nullable=True)


class ChatHistory(Base):
    """Chat messages between user and AI."""
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), default="user", index=True)
    role = Column(String(20), nullable=False)  # user | assistant
    message = Column(Text, nullable=False)
    timestamp = Column(String(50), nullable=True)

    __table_args__ = (
        Index("ix_chat_history_user", "user_id"),
    )


class ScreenerResult(Base):
    """Stock screener cached results."""
    __tablename__ = "screener_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    pnl = Column(Float, default=0.0)
    pnl_percent = Column(Float, default=0.0)
    in_trade = Column(Boolean, default=False)
    condition = Column(String(20), default="HOLD")  # BUY | HOLD | SELL
    updated_date = Column(String(50), nullable=True)


class Settings(Base):
    """Application settings key-value store."""
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(Text, nullable=True)


class WatchlistStock(Base):
    """
    Watchlist entries stored in the dashboard DB.

    The continuous monitoring loop runs on the user's laptop (agents) and polls
    these records from the cloud dashboard.
    """

    __tablename__ = "watchlist_stocks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(32), unique=True, index=True, nullable=False)
    strategy_id = Column(String(100), default="default")
    auto_trade = Column(Boolean, default=False)
    status = Column(String(20), default="active")  # active | paused | removed
    added_date = Column(String(50), nullable=True)
    last_checked = Column(String(50), nullable=True)
    last_signal = Column(String(20), nullable=True)  # buy | sell | hold
    last_signal_price = Column(Float, nullable=True)
    quantity_to_buy = Column(Integer, default=1)

    __table_args__ = (
        Index("ix_watchlist_stocks_status", "status"),
    )


class TradeSignal(Base):
    """Trade signals pending approval (Telegram + dashboard)."""

    __tablename__ = "trade_signals"

    id = Column(String(64), primary_key=True, index=True)  # UUID string
    symbol = Column(String(32), index=True, nullable=False)
    strategy_id = Column(String(100), default="default")
    signal_type = Column(String(20), default="buy")  # buy | sell
    signal_price = Column(Float, default=0.0)
    signal_time = Column(String(50), nullable=True)

    technical_score = Column(Float, default=0.0)
    news_score = Column(Float, default=0.0)
    fundamental_score = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)

    approval_status = Column(String(20), default="pending")  # pending | approved | skipped | rejected
    approval_time = Column(String(50), nullable=True)
    approval_reason = Column(Text, nullable=True)

    order_id = Column(String(64), nullable=True)
    execution_price = Column(Float, nullable=True)
    execution_time = Column(String(50), nullable=True)

    __table_args__ = (
        Index("ix_trade_signals_approval_status", "approval_status"),
        Index("ix_trade_signals_signal_time", "signal_time"),
    )


class IdempotencyKey(Base):
    """
    Persistent idempotency store for broker orders.

    This prevents accidental duplicate orders when clients retry a request.
    """

    __tablename__ = "idempotency_keys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_order_id = Column(String(80), unique=True, index=True, nullable=False)
    broker = Column(String(50), default="upstox")
    status = Column(String(30), default="pending")  # pending | completed | failed
    broker_order_id = Column(String(80), nullable=True)
    request_payload = Column(Text, nullable=True)
    created_at = Column(String(50), nullable=True)


class Position(Base):
    """Centralized position snapshots (single source of truth for the dashboard)."""

    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    broker = Column(String(50), default="upstox", index=True)
    symbol = Column(String(32), index=True, nullable=False)
    side = Column(String(10), default="long")  # long | short
    quantity = Column(Integer, default=0)
    avg_entry_price = Column(Float, default=0.0)
    current_price = Column(Float, default=0.0)
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    last_updated = Column(String(50), nullable=True)

    __table_args__ = (
        Index("ix_positions_symbol", "symbol"),
        Index("ix_positions_broker_symbol", "broker", "symbol"),
    )


class WatchlistAlert(Base):
    """Alerts emitted by agents and optionally sent to Telegram."""

    __tablename__ = "watchlist_alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(32), index=True, nullable=False)
    alert_type = Column(String(50), default="signal_alert")
    alert_message = Column(Text, nullable=False)
    alert_time = Column(String(50), nullable=True)
    telegram_sent = Column(Boolean, default=False)
    telegram_message_id = Column(String(64), nullable=True)


def init_db() -> None:
    """Create all tables if they don't exist (safe to call on startup)."""
    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError as exc:
        # SQLite in particular can raise "index ... already exists" if schema evolved
        # across deploys and SQLAlchemy's index existence detection is out of sync.
        # This dashboard can tolerate missing/extra indexes; prefer booting.
        msg = str(exc).lower()
        if DATABASE_URL.startswith("sqlite") and "index" in msg and "already exists" in msg:
            return
        raise

--- END FILE: trading-dashboard\backend\database.py ---

--- START FILE: trading-dashboard\backend\main.py ---
import asyncio
import os
import uuid
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

import json
import urllib.request
from fastapi import FastAPI, WebSocket, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

try:
    # When executed as a module (e.g. gunicorn/uvicorn from repo root)
    from backend.database import (  # type: ignore
        SessionLocal,
        Strategy,
        TradeSignal,
        WatchlistAlert,
        WatchlistStock,
        Settings,
        Position,
        IdempotencyKey,
        init_db,
    )
except ModuleNotFoundError:  # noqa: BLE001
    # When executed as a script from within backend/ (python backend/main.py)
    from database import (  # type: ignore
        SessionLocal,
        Strategy,
        TradeSignal,
        WatchlistAlert,
        WatchlistStock,
        Settings,
        Position,
        IdempotencyKey,
        init_db,
    )

try:
    from backend.brokerage.charges_engine import ChargesEngine, TradeSegment  # type: ignore
    from backend.risk.capital_allocator import CapitalAllocator, CapitalConfig  # type: ignore
    from backend.config.trading_config import is_trading_enabled, enable_trading, disable_trading  # type: ignore
    from backend.execution.order_deduplication import OrderDeduplicationService  # type: ignore
    from backend.core.event_store import build_event_store  # type: ignore
    from backend.core.event_bus import build_event_bus  # type: ignore
    from backend.market_data.symbol_master_service import build_symbol_master  # type: ignore
    from backend.brokers.upstox_broker import broker_from_env  # type: ignore
    from backend.security.jwt_auth import load_jwt_auth  # type: ignore
    from backend.execution.auth.broker_auth_manager import BrokerAuthManager  # type: ignore
    from backend.notifications.telegram_bot import send_approval_request, TelegramCallbackPoller  # type: ignore
    from backend.user_store import ensure_default_admin, verify_user, update_password  # type: ignore
    from backend.auth import create_token  # type: ignore
    from backend.runtime.system_runtime import TradingSystemRuntime  # type: ignore
except ModuleNotFoundError:  # noqa: BLE001
    from brokerage.charges_engine import ChargesEngine, TradeSegment  # type: ignore
    from risk.capital_allocator import CapitalAllocator, CapitalConfig  # type: ignore
    from config.trading_config import is_trading_enabled, enable_trading, disable_trading  # type: ignore
    from execution.order_deduplication import OrderDeduplicationService  # type: ignore
    from core.event_store import build_event_store  # type: ignore
    from core.event_bus import build_event_bus  # type: ignore
    from market_data.symbol_master_service import build_symbol_master  # type: ignore
    from brokers.upstox_broker import broker_from_env  # type: ignore
    from security.jwt_auth import load_jwt_auth  # type: ignore
    from execution.auth.broker_auth_manager import BrokerAuthManager  # type: ignore
    from notifications.telegram_bot import send_approval_request, TelegramCallbackPoller  # type: ignore
    from user_store import ensure_default_admin, verify_user, update_password  # type: ignore
    from auth import create_token  # type: ignore
    from runtime.system_runtime import TradingSystemRuntime  # type: ignore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dashboard")

app = FastAPI(title="Trading Dashboard API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

agent_states: Dict[str, Dict[str, Any]] = {}
connected_clients: List[WebSocket] = []
pending_commands: Dict[str, Dict[str, Any]] = {}
command_responses: Dict[str, Dict[str, Any]] = {}
positions: List[Dict[str, Any]] = []
order_history: List[Dict[str, Any]] = []
# Lightweight stores to support the "watchlist/approval" workflow in the extra scripts/UI.
watchlist_items: List[Dict[str, Any]] = []
trade_signals: List[Dict[str, Any]] = []
last_buy_alert_at: Dict[str, datetime] = {}
ALERT_COOLDOWN_SECONDS = int(os.getenv("TELEGRAM_ALERT_COOLDOWN_SECONDS", "60"))

settings_store: Dict[str, Any] = {
    "broker": "upstox",
    "trading_mode": "paper",
    "max_position_size": 5,
    "max_daily_loss": 2,
    "max_correlation": 0.7,
    "ollama_model": "deepseek-r1:7b",
    "ollama_url": "http://localhost:11434",
    "telegram_enabled": True,
    "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
    "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID", ""),
}

# ---------------------------------------------------------------------------
# Upstox OAuth manager (authorization_code + refresh_token)
# ---------------------------------------------------------------------------
_auth_manager = BrokerAuthManager("upstox")

# Ensure DB tables exist (SQLite by default, Postgres if DATABASE_URL is set on Render).
init_db()
ensure_default_admin()

# Phase A foundations (safe defaults: enabled only when explicitly configured)
JWT = load_jwt_auth()
DEDUP = OrderDeduplicationService()
CHARGES = ChargesEngine(min_profitability_ratio=float(os.getenv("MIN_PROFITABILITY_RATIO", "3.0")))
CAPITAL = CapitalAllocator(
    CapitalConfig(
        max_capital_deployment=float(os.getenv("MAX_CAPITAL_DEPLOYMENT", "0.70")),
        risk_per_trade=float(os.getenv("RISK_PER_TRADE", "0.01")),
        max_position_size=float(os.getenv("MAX_POSITION_SIZE_FRAC", "0.10")),
        max_open_positions=int(os.getenv("MAX_OPEN_POSITIONS", "8")),
        emergency_reserve=float(os.getenv("EMERGENCY_RESERVE", "0.20")),
    )
)
SYMBOL_MASTER = build_symbol_master()
EVENTS = build_event_store(os.environ.get("DATABASE_URL", "sqlite:///./trading_dashboard.db"))
EVENT_BUS = build_event_bus(EVENTS)
TELEGRAM_POLLER: TelegramCallbackPoller | None = None
SYSTEM_RUNTIME: TradingSystemRuntime | None = None

# Broker is optional; when missing token or feature flag is off, we keep paper trading behavior.
ENABLE_LIVE_BROKER = os.getenv("ENABLE_LIVE_BROKER", "").strip().lower() in {"1", "true", "yes", "on"}
UPSTOX = broker_from_env(symbol_master=SYMBOL_MASTER) if ENABLE_LIVE_BROKER else None


def _auth_required() -> bool:
    return JWT is not None


def _require_user(authorization: str | None) -> Dict[str, Any]:
    if not JWT:
        return {"sub": "anonymous", "role": "admin"}
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    parts = authorization.strip().split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    try:
        return JWT.verify_token(parts[1])
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=401, detail=str(exc))


def _require_admin(user: Dict[str, Any]) -> None:
    if str(user.get("role") or "") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")


def _service_token() -> str:
    return os.getenv("DASHBOARD_API_TOKEN", "").strip()


def _is_service_bearer(authorization: str | None) -> bool:
    token = _service_token()
    if not authorization or not token:
        return False
    parts = authorization.strip().split(" ", 1)
    return len(parts) == 2 and parts[0].lower() == "bearer" and parts[1].strip() == token


def _require_admin_access(authorization: str | None, admin_key: str | None) -> Dict[str, Any]:
    """
    Admin gate:
    - If JWT is enabled, require Bearer token with role=admin.
    - A configured DASHBOARD_API_TOKEN bearer token is also accepted for service-to-service calls.
    - If JWT is disabled, require X-Admin-Key header matching ADMIN_API_KEY env var.
    """
    if JWT:
        if _is_service_bearer(authorization):
            return {"sub": "service", "role": "admin"}
        user = _require_user(authorization)
        _require_admin(user)
        return user
    if _is_service_bearer(authorization):
        return {"sub": "service", "role": "admin"}
    expected = os.getenv("ADMIN_API_KEY", "").strip()
    if not expected:
        raise HTTPException(status_code=500, detail="ADMIN_API_KEY not configured (and JWT disabled)")
    if not admin_key or admin_key.strip() != expected:
        raise HTTPException(status_code=403, detail="Invalid X-Admin-Key")
    return {"sub": "admin-key", "role": "admin"}


def _normalize_symbol(symbol: str) -> str:
    return str(symbol or "").upper().replace(".NS", "").replace(".BO", "").strip()


def _sync_in_memory_position_from_db(broker: str, symbol: str) -> None:
    """Refresh the fallback in-memory position list from the dashboard DB."""
    try:
        broker_name = str(broker or "upstox").lower().strip()
        sym = _normalize_symbol(symbol)
        db = SessionLocal()
        try:
            row = db.query(Position).filter(Position.broker == broker_name, Position.symbol == sym).first()
        finally:
            db.close()
        if not row:
            return

        existing = next(
            (
                item
                for item in positions
                if str(item.get("symbol") or "").upper() == sym
                and str(item.get("broker") or "upstox").lower().strip() == broker_name
            ),
            None,
        )
        payload = {
            "symbol": sym,
            "qty": int(row.quantity or 0),
            "entry_price": float(row.avg_entry_price or 0.0),
            "current_price": float(row.current_price or row.avg_entry_price or 0.0),
            "pnl": float(row.realized_pnl or 0.0) + float(row.unrealized_pnl or 0.0),
            "pnl_pct": 0.0,
            "broker": broker_name,
        }
        denom = abs(payload["qty"]) * float(payload["entry_price"] or 0.0)
        payload["pnl_pct"] = (payload["pnl"] / denom * 100.0) if denom else 0.0
        if existing:
            existing.update(payload)
        else:
            positions.insert(0, payload)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not refresh in-memory positions: %s", exc)


def _sync_dashboard_position_from_fill(
    broker: str,
    symbol: str,
    side: str,
    quantity: int,
    fill_price: float,
    current_price: float | None = None,
) -> None:
    """Mirror a broker fill into the dashboard's Position table."""
    try:
        broker_name = str(broker or "upstox").lower().strip()
        sym = _normalize_symbol(symbol)
        fill_side = str(side or "buy").lower().strip()
        qty = abs(int(quantity))
        price = float(fill_price)
        mark_price = float(current_price if current_price is not None else fill_price)
        if not sym or qty <= 0 or price <= 0:
            return

        db = SessionLocal()
        try:
            row = db.query(Position).filter(Position.broker == broker_name, Position.symbol == sym).first()
            if not row:
                row = Position(broker=broker_name, symbol=sym)
                db.add(row)

            existing_qty = int(row.quantity or 0)
            avg_entry = float(row.avg_entry_price or price)
            realized = float(row.realized_pnl or 0.0)
            new_qty = existing_qty

            if fill_side == "buy":
                if existing_qty >= 0:
                    new_qty = existing_qty + qty
                    row.avg_entry_price = ((existing_qty * avg_entry) + (qty * price)) / new_qty if new_qty and existing_qty > 0 else price
                    row.side = "long" if new_qty > 0 else "flat"
                else:
                    closed_qty = min(abs(existing_qty), qty)
                    realized += (avg_entry - price) * closed_qty
                    new_qty = existing_qty + qty
                    if new_qty < 0:
                        row.side = "short"
                    elif new_qty == 0:
                        row.side = "flat"
                    else:
                        row.side = "long"
                        row.avg_entry_price = price
            else:
                if existing_qty > 0:
                    closed_qty = min(existing_qty, qty)
                    realized += (price - avg_entry) * closed_qty
                    new_qty = existing_qty - qty
                    if new_qty > 0:
                        row.side = "long"
                    elif new_qty == 0:
                        row.side = "flat"
                    else:
                        row.side = "short"
                        row.avg_entry_price = price
                else:
                    new_qty = existing_qty - qty
                    row.side = "short" if new_qty < 0 else "flat"

            row.quantity = int(new_qty)
            row.current_price = mark_price
            row.realized_pnl = float(realized)
            if row.quantity > 0:
                row.unrealized_pnl = (mark_price - float(row.avg_entry_price or mark_price)) * row.quantity
            elif row.quantity < 0:
                row.unrealized_pnl = (float(row.avg_entry_price or mark_price) - mark_price) * abs(row.quantity)
            else:
                row.unrealized_pnl = 0.0
            row.last_updated = datetime.now().isoformat()
            db.commit()
        finally:
            db.close()

        _sync_in_memory_position_from_db(broker_name, sym)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not sync dashboard position from fill: %s", exc)


def _sync_order_history(payload: dict, status: str) -> None:
    """Mirror order lifecycle updates into the dashboard's in-memory history."""
    try:
        order_id = str(payload.get("broker_order_id") or payload.get("order_id") or payload.get("id") or "").strip()
        client_order_id = str(payload.get("client_order_id") or "").strip()
        symbol = _normalize_symbol(payload.get("symbol") or "")
        side = str(payload.get("side") or "").lower().strip()
        qty = int(payload.get("filled_qty") or payload.get("quantity") or payload.get("qty") or 0)
        price = float(payload.get("fill_price") or payload.get("execution_price") or payload.get("price") or 0.0)
        existing = next(
            (
                item
                for item in order_history
                if str(item.get("id") or item.get("broker_order_id") or "") == order_id
                or (client_order_id and str(item.get("client_order_id") or "") == client_order_id)
            ),
            None,
        )
        if existing:
            existing.update(
                {
                    "broker_order_id": order_id or existing.get("broker_order_id"),
                    "client_order_id": client_order_id or existing.get("client_order_id"),
                    "symbol": symbol or existing.get("symbol"),
                    "side": side or existing.get("side"),
                    "qty": qty or existing.get("qty"),
                    "price": price or existing.get("price"),
                    "status": status,
                    "timestamp": datetime.now().isoformat(),
                }
            )
        else:
            order_history.insert(
                0,
                {
                    "id": order_id or client_order_id or str(uuid.uuid4()),
                    "broker_order_id": order_id,
                    "client_order_id": client_order_id,
                    "symbol": symbol,
                    "side": side,
                    "qty": qty,
                    "price": price,
                    "mode": "live" if ENABLE_LIVE_BROKER else "paper",
                    "status": status,
                    "timestamp": datetime.now().isoformat(),
                },
            )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not sync order history: %s", exc)


def _on_market_tick(payload: dict) -> None:
    try:
        symbol = _normalize_symbol(payload.get("symbol") or "")
        price = float(payload.get("ltp") or 0.0)
        if not symbol or price <= 0:
            return
        _sync_in_memory_position_from_db("upstox", symbol)
        db = SessionLocal()
        try:
            row = db.query(Position).filter(Position.broker == "upstox", Position.symbol == symbol).first()
            if row:
                row.current_price = price
                qty = int(row.quantity or 0)
                if qty > 0:
                    row.unrealized_pnl = (price - float(row.avg_entry_price or price)) * qty
                elif qty < 0:
                    row.unrealized_pnl = (float(row.avg_entry_price or price) - price) * abs(qty)
                else:
                    row.unrealized_pnl = 0.0
                row.last_updated = datetime.now().isoformat()
                db.commit()
        finally:
            db.close()
        _sync_in_memory_position_from_db("upstox", symbol)
    except Exception as exc:  # noqa: BLE001
        logger.warning("market.tick mirror failed: %s", exc)


def _on_order_placed(payload: dict) -> None:
    _sync_order_history(payload, "submitted")


def _on_order_filled(payload: dict) -> None:
    _sync_order_history(payload, "filled")
    broker = str(payload.get("broker") or "upstox")
    symbol = str(payload.get("symbol") or "")
    side = str(payload.get("side") or "buy")
    qty = int(payload.get("filled_qty") or payload.get("quantity") or payload.get("qty") or 0)
    fill_price = float(payload.get("fill_price") or payload.get("execution_price") or payload.get("price") or 0.0)
    if qty > 0 and fill_price > 0:
        _sync_dashboard_position_from_fill(broker, symbol, side, qty, fill_price, current_price=fill_price)


def _on_order_rejected(payload: dict) -> None:
    _sync_order_history(payload, str(payload.get("reason") or "rejected"))


EVENT_BUS.subscribe("market.tick", _on_market_tick)
EVENT_BUS.subscribe("order.placed", _on_order_placed)
EVENT_BUS.subscribe("order.filled", _on_order_filled)
EVENT_BUS.subscribe("order.rejected", _on_order_rejected)


def _db_get_setting(key: str, default: str | None = None) -> str | None:
    db = SessionLocal()
    try:
        row = db.query(Settings).filter(Settings.key == key).first()
        if not row:
            return default
        return row.value
    finally:
        db.close()


def _db_set_setting(key: str, value: str) -> None:
    db = SessionLocal()
    try:
        row = db.query(Settings).filter(Settings.key == key).first()
        if not row:
            row = Settings(key=key, value=value)
            db.add(row)
        else:
            row.value = value
        db.commit()
    finally:
        db.close()


def _kill_switch_enabled() -> bool:
    v = _db_get_setting("TRADING_ENABLED")
    if v is None or str(v).strip() == "":
        return is_trading_enabled()
    return str(v).strip().lower() in {"1", "true", "yes", "on"}

def _db_list_watchlist() -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        rows = (
            db.query(WatchlistStock)
            .order_by(WatchlistStock.id.desc())
            .all()
        )
        return [
            {
                "id": str(r.id),
                "symbol": r.symbol,
                "strategy_id": r.strategy_id,
                "auto_trade": bool(r.auto_trade),
                "status": r.status,
                "added_date": r.added_date,
                "last_checked": r.last_checked,
                "last_signal": r.last_signal,
                "last_signal_price": r.last_signal_price,
                "quantity_to_buy": r.quantity_to_buy,
            }
            for r in rows
        ]
    finally:
        db.close()


def _signal_runtime_details(signal_id: str, symbol: str) -> Dict[str, Any]:
    runtime = next((s for s in trade_signals if str(s.get("id")) == str(signal_id)), None)
    quantity = int((runtime or {}).get("quantity") or (runtime or {}).get("qty") or 0)
    reason = str((runtime or {}).get("reason") or (runtime or {}).get("approval_reason") or "").strip()
    side = str((runtime or {}).get("side") or (runtime or {}).get("signal_type") or "buy").lower().strip() or "buy"
    if not reason:
        try:
            db = SessionLocal()
            try:
                row = db.query(TradeSignal).filter(TradeSignal.id == str(signal_id)).first()
                if row and row.approval_reason:
                    reason = str(row.approval_reason).strip()
            finally:
                db.close()
        except Exception:
            pass
    if quantity <= 0:
        try:
            db = SessionLocal()
            try:
                row = db.query(WatchlistStock).filter(WatchlistStock.symbol == str(symbol).upper()).first()
                if row:
                    quantity = int(row.quantity_to_buy or 1)
            finally:
                db.close()
        except Exception:
            pass
    if quantity <= 0:
        quantity = 1
    return {"quantity": quantity, "reason": reason or None, "side": side}


def _db_upsert_watchlist(payload: dict) -> Dict[str, Any]:
    symbol = str(payload.get("symbol", "")).upper().strip()
    if not symbol:
        raise HTTPException(status_code=400, detail="symbol required")
    db = SessionLocal()
    try:
        row = db.query(WatchlistStock).filter(WatchlistStock.symbol == symbol).first()
        if row and row.status != "removed":
            return {"status": "exists", "symbol": symbol}
        if not row:
            row = WatchlistStock(symbol=symbol)
            db.add(row)
        row.strategy_id = str(payload.get("strategy_id") or row.strategy_id or "default")
        row.auto_trade = bool(payload.get("auto_trade", row.auto_trade))
        row.status = str(payload.get("status") or row.status or "active")
        row.added_date = row.added_date or datetime.now().isoformat()
        row.quantity_to_buy = int(payload.get("quantity_to_buy") or payload.get("quantity") or row.quantity_to_buy or 1)
        db.commit()
        db.refresh(row)
        return {
            "status": "added",
            "item": {
                "id": str(row.id),
                "symbol": row.symbol,
                "strategy_id": row.strategy_id,
                "auto_trade": bool(row.auto_trade),
                "status": row.status,
                "added_date": row.added_date,
                "last_checked": row.last_checked,
                "last_signal": row.last_signal,
                "last_signal_price": row.last_signal_price,
                "quantity_to_buy": row.quantity_to_buy,
            },
        }
    finally:
        db.close()


def _db_remove_watchlist(symbol: str) -> Dict[str, Any]:
    sym = str(symbol).upper().strip()
    if not sym:
        raise HTTPException(status_code=400, detail="symbol required")
    db = SessionLocal()
    try:
        row = db.query(WatchlistStock).filter(WatchlistStock.symbol == sym).first()
        if not row or row.status == "removed":
            return {"status": "not_found", "symbol": sym}
        row.status = "removed"
        db.commit()
        return {"status": "removed", "symbol": sym}
    finally:
        db.close()


def _db_insert_signal(signal_rec: Dict[str, Any]) -> None:
    db = SessionLocal()
    try:
        # De-dupe by id if the caller retries.
        existing = db.query(TradeSignal).filter(TradeSignal.id == str(signal_rec["id"])).first()
        if existing:
            return
        row = TradeSignal(
            id=str(signal_rec["id"]),
            symbol=str(signal_rec.get("symbol") or "UNKNOWN"),
            strategy_id=str(signal_rec.get("strategy_id") or "default"),
            signal_type=str(signal_rec.get("signal_type") or "buy"),
            signal_price=float(signal_rec.get("signal_price") or 0.0),
            signal_time=str(signal_rec.get("signal_time") or datetime.now().isoformat()),
            technical_score=float(signal_rec.get("technical_score") or 0.0),
            news_score=float(signal_rec.get("news_score") or 0.0),
            fundamental_score=float(signal_rec.get("fundamental_score") or 0.0),
            risk_score=float(signal_rec.get("risk_score") or 0.0),
            overall_score=float(signal_rec.get("overall_score") or 0.0),
            approval_status=str(signal_rec.get("approval_status") or "pending"),
            approval_reason=str(signal_rec.get("reason") or signal_rec.get("approval_reason") or "") or None,
        )
        db.add(row)
        db.commit()
    finally:
        db.close()
class ChatMessage(BaseModel):
    message: str

@app.exception_handler(Exception)
async def global_exception_handler(_, exc: Exception):
    error_id = str(uuid.uuid4())
    logger.exception("Unhandled error %s", error_id)
    return JSONResponse(status_code=500, content={"detail": "Internal server error", "error_id": error_id})

@app.get('/health')
async def health():
    return {'status': 'ok', 'timestamp': datetime.now().isoformat()}

@app.post('/agent-status')
async def update_agent_status(data: dict):
    aid = data.get('agent_id')
    if not aid:
        raise HTTPException(status_code=400, detail='agent_id is required')
    agent_states[aid] = data
    await broadcast_agent_update(data)
    return {'status': 'ok'}

# Back-compat for scripts/UI that call /api/agent-status
@app.post('/api/agent-status')
async def update_agent_status_api(data: dict):
    return await update_agent_status(data)

@app.websocket('/ws/agent-monitor')
async def ws_monitor(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        for st in agent_states.values():
            await websocket.send_json(st)
        while True:
            await websocket.receive_text()
            await websocket.send_json({'ack': True})
    finally:
        if websocket in connected_clients:
            connected_clients.remove(websocket)

async def broadcast_agent_update(data: dict):
    for c in connected_clients:
        try:
            await c.send_json(data)
        except Exception:
            pass

@app.post('/chat')
async def chat(message: ChatMessage):
    if not message.message.strip():
        raise HTTPException(status_code=400, detail='Message required')
    cid = str(uuid.uuid4())
    pending_commands[cid] = {'command_id': cid, 'message': message.message, 'timestamp': datetime.now().isoformat(), 'status': 'pending'}
    return {'command_id': cid, 'status': 'queued'}

# Back-compat for older UI patterns that assume an /api prefix.
@app.post('/api/chat')
async def chat_api(message: ChatMessage):
    return await chat(message)

@app.get('/chat/pending-commands')
async def pending():
    return {'commands': [c for c in pending_commands.values() if c.get('status') == 'pending']}

@app.post('/chat/submit-response')
async def submit_response(payload: dict):
    cid = payload.get('command_id')
    response = payload.get('response') or payload.get('response_text')
    if not cid or response is None:
        raise HTTPException(status_code=400, detail='command_id and response required')
    command_responses[cid] = {'command_id': cid, 'response': response, 'timestamp': datetime.now().isoformat()}
    pending_commands.pop(cid, None)
    return {'status': 'ok'}

@app.get('/chat/response/{command_id}')
async def get_response(command_id: str):
    if command_id in command_responses:
        return {'status': 'done', **command_responses[command_id]}
    if command_id in pending_commands:
        return {'status': 'processing', 'command_id': command_id}
    return {'status': 'not_found', 'command_id': command_id}

@app.post('/alerts/buy-signal')
async def buy_signal_alert(payload: dict):
    symbol = str(payload.get('symbol', 'UNKNOWN')).upper()
    signal = str(payload.get('signal', '')).lower()
    if signal not in {'buy', 'buy_bias'}:
        return {'status': 'ignored', 'reason': 'not_buy_signal'}

    now = datetime.utcnow()
    prev = last_buy_alert_at.get(symbol)
    if prev and (now - prev) < timedelta(seconds=ALERT_COOLDOWN_SECONDS):
        remaining = ALERT_COOLDOWN_SECONDS - int((now - prev).total_seconds())
        return {'status': 'cooldown', 'symbol': symbol, 'remaining_seconds': max(0, remaining)}

    # Always register the signal so the dashboard/UI can show it (even if Telegram isn't configured).
    signal_rec = {
        'id': str(uuid.uuid4()),
        'symbol': symbol,
        'strategy_id': str(payload.get('strategy_id') or 'default'),
        'side': 'buy',
        'signal_type': 'buy',
        'signal_price': float(payload.get('price') or payload.get('signal_price') or 0.0),
        'signal_time': datetime.now().isoformat(),
        'quantity': int(payload.get('quantity') or payload.get('qty') or payload.get('quantity_to_buy') or 1),
        'reason': str(payload.get('reason') or payload.get('signal_reason') or 'Technical signal'),
        'technical_score': float(payload.get('technical_score') or 0.0),
        'news_score': float(payload.get('news_score') or 0.0),
        'fundamental_score': float(payload.get('fundamental_score') or 0.0),
        'risk_score': float(payload.get('risk_score') or 0.0),
        'overall_score': float(payload.get('overall_score') or 0.0),
        'approval_status': 'pending',
    }
    trade_signals.insert(0, signal_rec)
    # Persist to DB so the watchlist/signals survive Render restarts (SQLite by default).
    try:
        _db_insert_signal(signal_rec)
        db = SessionLocal()
        try:
            wl = db.query(WatchlistStock).filter(WatchlistStock.symbol == symbol).first()
            if wl:
                wl.last_checked = datetime.now().isoformat()
                wl.last_signal = "buy"
                wl.last_signal_price = float(signal_rec.get("signal_price") or 0.0)
                db.commit()
            db.add(
                WatchlistAlert(
                    symbol=symbol,
                    alert_type="signal_alert",
                    alert_message=f"BUY SIGNAL: {symbol}",
                    alert_time=datetime.now().isoformat(),
                    telegram_sent=False,
                )
            )
            db.commit()
        finally:
            db.close()
    except Exception:
        # Don't fail the alert endpoint if DB is unavailable.
        pass

    try:
        await EVENT_BUS.publish("signal.created", signal_rec)
    except Exception:
        pass

    sent = await send_approval_request(signal_rec)
    if not sent:
        sent = await send_telegram_alert(f"BUY SIGNAL: {symbol}\nSignal: {signal}\nTime: {datetime.now().isoformat()}")
    last_buy_alert_at[symbol] = now
    if not sent:
        return {'status': 'telegram_not_configured_or_failed', 'symbol': symbol, 'cooldown_seconds': ALERT_COOLDOWN_SECONDS, 'signal_id': signal_rec['id']}
    return {'status': 'sent', 'symbol': symbol, 'cooldown_seconds': ALERT_COOLDOWN_SECONDS, 'signal_id': signal_rec['id']}

async def send_telegram_alert(text: str) -> bool:
    if not settings_store.get('telegram_enabled', False):
        return False
    token = settings_store.get('telegram_bot_token') or os.getenv('TELEGRAM_BOT_TOKEN', '')
    chat_id = settings_store.get('telegram_chat_id') or os.getenv('TELEGRAM_CHAT_ID', '')
    if not token or not chat_id:
        return False
    try:
        payload = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return 200 <= resp.status < 300
    except Exception:
        return False

@app.get('/positions')
async def get_positions():
    # Prefer DB-backed position snapshots if present (survive restarts).
    try:
        db = SessionLocal()
        try:
            rows = db.query(Position).all()
        finally:
            db.close()
        if rows:
            out: List[Dict[str, Any]] = []
            for r in rows:
                qty = float(r.quantity or 0)
                entry = float(r.avg_entry_price or 0)
                cur = float(r.current_price or 0) or entry
                pnl = (cur - entry) * qty if qty else 0.0
                pnl_pct = (pnl / (abs(qty) * entry) * 100) if qty and entry else 0.0
                out.append(
                    {
                        "symbol": r.symbol,
                        "qty": qty,
                        "entry_price": entry,
                        "current_price": cur,
                        "pnl": pnl,
                        "pnl_pct": pnl_pct,
                        "broker": r.broker,
                        "last_updated": r.last_updated,
                    }
                )
            return out
    except Exception:
        pass
    return positions

@app.get('/api/positions')
async def get_positions_api():
    return await get_positions()

@app.delete('/positions/{symbol}')
async def close_position(symbol: str):
    global positions
    sym = symbol.upper().strip()
    positions = [p for p in positions if p['symbol'] != sym]
    # Best-effort DB cleanup (set qty to 0).
    try:
        db = SessionLocal()
        try:
            row = db.query(Position).filter(Position.symbol == sym).first()
            if row:
                row.quantity = 0
                row.unrealized_pnl = 0.0
                row.last_updated = datetime.now().isoformat()
                db.commit()
        finally:
            db.close()
    except Exception:
        pass
    return {'status': 'ok'}

@app.post('/trade')
async def place_trade(data: dict):
    if not _kill_switch_enabled():
        raise HTTPException(status_code=403, detail="Trading disabled (kill switch active)")

    symbol = str(data.get('symbol', '')).upper().strip()
    side = str(data.get('side', 'buy')).lower().strip()
    qty_req = float(data.get('quantity', 0) or 0)
    price = float(data.get('price', 0) or 0)

    if side not in {"buy", "sell"}:
        raise HTTPException(status_code=400, detail="side must be buy or sell")
    if not symbol or qty_req <= 0 or price <= 0:
        raise HTTPException(status_code=400, detail='Invalid order payload')

    sl_pct = float(os.getenv("DEFAULT_STOP_LOSS_PCT", "2.0"))
    tp_pct = float(os.getenv("DEFAULT_TAKE_PROFIT_PCT", "5.0"))

    stop_loss = data.get("stop_loss")
    take_profit = data.get("take_profit") or data.get("expected_exit_price")

    try:
        stop_loss = float(stop_loss) if stop_loss is not None and str(stop_loss).strip() != "" else None
    except Exception:
        stop_loss = None
    try:
        take_profit = float(take_profit) if take_profit is not None and str(take_profit).strip() != "" else None
    except Exception:
        take_profit = None

    if stop_loss is None:
        stop_loss = price * (1.0 - sl_pct / 100.0) if side == "buy" else price * (1.0 + sl_pct / 100.0)
    if take_profit is None:
        take_profit = price * (1.0 + tp_pct / 100.0) if side == "buy" else price * (1.0 - tp_pct / 100.0)

    # Persistent idempotency protection (client_order_id).
    client_order_id = str(data.get("client_order_id") or "").strip()
    if not client_order_id:
        client_order_id = DEDUP.generate_client_order_id(symbol, side, int(qty_req))

    db = SessionLocal()
    try:
        existing = db.query(IdempotencyKey).filter(IdempotencyKey.client_order_id == client_order_id).first()
        if existing:
            if (existing.status or "") == "completed" and existing.broker_order_id:
                return {
                    "status": "duplicate",
                    "client_order_id": client_order_id,
                    "order_id": existing.broker_order_id,
                    "message": "Order already completed for this client_order_id",
                }
            raise HTTPException(status_code=409, detail="Duplicate order detected (client_order_id already registered)")

        row = IdempotencyKey(
            client_order_id=client_order_id,
            broker=str(data.get("broker") or settings_store.get("broker") or "upstox"),
            status="pending",
            broker_order_id=None,
            request_payload=json.dumps(data),
            created_at=datetime.now().isoformat(),
        )
        db.add(row)
        db.commit()
    finally:
        db.close()

    def _calc_exposure_and_count() -> tuple[float, int]:
        db2 = SessionLocal()
        try:
            rows = db2.query(Position).all()
            if rows:
                exposure = 0.0
                count = 0
                for r in rows:
                    q = float(r.quantity or 0)
                    cur = float(r.current_price or 0) or float(r.avg_entry_price or 0)
                    if q != 0:
                        count += 1
                        exposure += abs(q) * cur
                return exposure, count
        except Exception:
            pass
        finally:
            db2.close()

        exposure = 0.0
        count = 0
        for p in positions:
            q = float(p.get("qty") or 0)
            cur = float(p.get("current_price") or 0)
            if q != 0:
                count += 1
                exposure += abs(q) * cur
        return exposure, count

    # Institutional capital allocation / reserve enforcement (default ON).
    enforce_capital = os.getenv("ENFORCE_CAPITAL_ALLOCATOR", "true").strip().lower() in {"1", "true", "yes", "on"}
    if enforce_capital:
        bal_raw = _db_get_setting("ACCOUNT_BALANCE", "") or os.getenv("DEFAULT_ACCOUNT_BALANCE", "100000")
        account_balance = float(bal_raw or 100000)
        current_exposure, open_positions = _calc_exposure_and_count()
        allocation = CAPITAL.calculate_position_size(
            account_balance=account_balance,
            entry_price=price,
            stop_loss_price=float(stop_loss),
            current_exposure=current_exposure,
            open_positions=open_positions,
        )
        if not allocation.get("allowed"):
            raise HTTPException(status_code=400, detail=f"CapitalAllocator reject: {allocation.get('reason')}")
        qty_allowed = int(allocation.get("quantity") or 0)
        qty = min(int(qty_req), qty_allowed)
        if qty <= 0:
            raise HTTPException(status_code=400, detail="CapitalAllocator sized quantity to 0")
    else:
        qty = int(qty_req)

    # Charges profitability filter (default ON).
    enforce_charges = os.getenv("ENFORCE_CHARGES_FILTER", "true").strip().lower() in {"1", "true", "yes", "on"}
    if enforce_charges and take_profit is not None and side == "buy":
        segment = str(data.get("trade_segment") or "intraday").lower().strip()
        seg = TradeSegment.delivery if segment == "delivery" else TradeSegment.intraday
        charges = CHARGES.calculate_charges(seg, buy_price=price, sell_price=float(take_profit), quantity=int(qty), using_api=True)
        if not charges.get("should_execute", True):
            EVENTS.store_event(
                "trade_rejected_charges",
                {"symbol": symbol, "side": side, "qty": qty, "price": price, "take_profit": take_profit, "charges": charges},
                source="dashboard",
            )
            raise HTTPException(
                status_code=400,
                detail=f"Unprofitable trade (profit ratio {charges.get('profitability_ratio')}x; need >= {CHARGES.min_profitability_ratio}x).",
            )

    mode = str(data.get("mode") or data.get("trading_mode") or settings_store.get("trading_mode") or "paper").lower().strip()
    broker_order_id: str
    status: str

    # Live execution is only enabled when ENABLE_LIVE_BROKER is set AND UPSTOX token is present.
    if mode == "live" and UPSTOX:
        try:
            resp = await UPSTOX.place_order(
                symbol=symbol,
                side=side,
                quantity=int(qty),
                client_order_id=client_order_id,
                order_type=str(data.get("order_type") or "MARKET").upper(),
                price=price if str(data.get("order_type") or "MARKET").upper() == "LIMIT" else None,
                stop_loss=float(stop_loss),
                take_profit=float(take_profit) if take_profit is not None else None,
            )
            broker_order_id = str(resp.get("data", {}).get("order_id") or resp.get("order_id") or uuid.uuid4())
            status = "submitted"
        except Exception as exc:  # noqa: BLE001
            EVENTS.store_event("trade_live_error", {"symbol": symbol, "error": str(exc)}, source="dashboard")
            raise HTTPException(status_code=502, detail=f"Live broker error: {exc}")
    else:
        broker_order_id = str(uuid.uuid4())
        status = "filled"

    o = {
        'id': broker_order_id,
        'client_order_id': client_order_id,
        'symbol': symbol,
        'side': side,
        'qty': qty,
        'price': price,
        'stop_loss': float(stop_loss),
        'take_profit': float(take_profit) if take_profit is not None else None,
        'mode': mode,
        'status': status,
        'timestamp': datetime.now().isoformat(),
    }
    order_history.insert(0, o)

    if side == "buy":
        positions.append({'symbol': symbol, 'qty': qty, 'entry_price': price, 'current_price': price, 'pnl': 0, 'pnl_pct': 0})

    # Persist position snapshot (best-effort; keeps DB-based portfolio stable across restarts).
    try:
        db3 = SessionLocal()
        try:
            rowp = db3.query(Position).filter(Position.broker == "upstox", Position.symbol == symbol).first()
            if not rowp:
                rowp = Position(broker="upstox", symbol=symbol)
                db3.add(rowp)
            rowp.side = "long" if side == "buy" else "short"
            rowp.quantity = int(rowp.quantity or 0) + (int(qty) if side == "buy" else -int(qty))
            rowp.avg_entry_price = float(price)
            rowp.current_price = float(price)
            rowp.last_updated = datetime.now().isoformat()
            db3.commit()
        finally:
            db3.close()
    except Exception:
        pass

    # Mark idempotency completed.
    try:
        db4 = SessionLocal()
        try:
            row = db4.query(IdempotencyKey).filter(IdempotencyKey.client_order_id == client_order_id).first()
            if row:
                row.status = "completed"
                row.broker_order_id = broker_order_id
                db4.commit()
        finally:
            db4.close()
    except Exception:
        pass

    EVENTS.store_event("trade_placed", o, source="dashboard")
    try:
        await EVENT_BUS.publish("trade.placed", o)
    except Exception:
        pass
    return {'status': 'success', 'order_id': broker_order_id, 'client_order_id': client_order_id, 'mode': mode}

@app.post('/api/trade')
async def place_trade_api(data: dict):
    return await place_trade(data)

@app.get('/order-history')
async def get_order_history():
    return order_history

@app.get('/api/order-history')
async def get_order_history_api():
    return await get_order_history()

@app.get('/strategies')
async def get_strategies():
    # DB-backed strategies. Falls back to seeded mock rows if the DB is empty.
    try:
        db = SessionLocal()
        try:
            rows = db.query(Strategy).order_by(Strategy.created_date.desc().nullslast()).all()
        finally:
            db.close()
        if rows:
            return [
                {
                    "id": r.id,
                    "name": r.name,
                    "symbol": r.symbol,
                    "timeframe": r.timeframe,
                    "status": r.status,
                    "pnl": r.pnl,
                    "win_rate": r.win_rate,
                    "total_trades": 0,
                    "equity_curve": [{"date": r.created_date or datetime.now().date().isoformat(), "value": 100000}],
                }
                for r in rows
            ]
    except Exception:
        pass

    return [
        {
            "id": "1",
            "name": "EMA Cross",
            "symbol": "INFY",
            "timeframe": "4h",
            "status": "running",
            "pnl": 8500,
            "win_rate": 72,
            "total_trades": 45,
            "equity_curve": [{"date": "2026-05-18", "value": 100000}],
        },
        {
            "id": "2",
            "name": "Pine Momentum",
            "symbol": "NIFTY",
            "timeframe": "1h",
            "status": "backtested",
            "pnl": 4200,
            "win_rate": 64,
            "total_trades": 33,
            "equity_curve": [{"date": "2026-05-18", "value": 100000}],
        },
    ]

@app.get('/api/strategies')
async def get_strategies_api():
    return await get_strategies()

@app.post('/strategy/create')
async def create_strategy(payload: dict):
    # Minimal persistence layer (the agent/executor can interpret rules later).
    strategy_id = str(payload.get("strategy_id") or payload.get("id") or uuid.uuid4())
    name = str(payload.get("name") or "New Strategy")
    symbol = str(payload.get("symbol") or "INFY").upper()
    timeframe = str(payload.get("timeframe") or "4h")
    status = str(payload.get("status") or "paused")
    entry_rule = str(payload.get("entry_rule") or payload.get("buy_conditions") or "")
    exit_rule = str(payload.get("exit_rule") or payload.get("sell_conditions") or "")
    try:
        db = SessionLocal()
        try:
            row = db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not row:
                row = Strategy(id=strategy_id, name=name, symbol=symbol, timeframe=timeframe)
                db.add(row)
            row.name = name
            row.symbol = symbol
            row.timeframe = timeframe
            row.status = status
            row.entry_rule = entry_rule
            row.exit_rule = exit_rule
            row.created_date = row.created_date or datetime.now().date().isoformat()
            db.commit()
        finally:
            db.close()
        return {"status": "created", "strategy_id": strategy_id}
    except Exception as exc:
        return {"status": "created", "strategy_id": strategy_id, "warning": f"db_unavailable: {exc}"}

@app.delete('/strategy/{strategy_id}')
async def delete_strategy(strategy_id: str):
    try:
        db = SessionLocal()
        try:
            row = db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if row:
                db.delete(row)
                db.commit()
        finally:
            db.close()
    except Exception:
        pass
    return {'status': 'deleted', 'id': strategy_id}

@app.get('/strategy/{strategy_id}/metrics')
async def metrics(strategy_id: str):
    try:
        db = SessionLocal()
        try:
            row = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        finally:
            db.close()
        if row:
            return {
                "id": row.id,
                "sharpe": row.sharpe_ratio or 0.0,
                "max_dd": 0.0,
                "profit_factor": 0.0,
                "win_rate": row.win_rate or 0.0,
                "pnl": row.pnl or 0.0,
            }
    except Exception:
        pass
    return {'id': strategy_id, 'sharpe': 1.9, 'max_dd': -8.2, 'profit_factor': 2.2}

@app.post('/strategy/pinescript/generate')
async def generate_pinescript(payload: dict):
    name = payload.get('name', 'Generated Strategy')
    script = f"//@version=5\nstrategy(\"{name}\", overlay=true)\nfast=ta.ema(close,9)\nslow=ta.ema(close,21)\nif ta.crossover(fast,slow)\n    strategy.entry(\"Long\",strategy.long)\nif ta.crossunder(fast,slow)\n    strategy.close(\"Long\")\n"
    return {'status': 'ok', 'script': script}

@app.post('/backtest')
async def backtest(_: dict):
    return {'total_trades': 45, 'win_rate': 72, 'profit_factor': 2.3, 'sharpe': 1.87, 'max_dd': -8.5, 'net_pnl': 25000, 'equity_curve': [{'date': '2026-01', 'value': 100000}], 'trades': [{'entry_date': '2026-01-05', 'exit_date': '2026-01-10', 'entry_price': 1950, 'profit': 238}]}

@app.post('/api/backtest')
async def backtest_api(payload: dict):
    return await backtest(payload)

@app.get('/screener')
async def screener():
    return [
        {'rank': 1, 'symbol': 'INFY', 'price': 1955, 'change_pct': 0.24, 'pnl_pct': 12, 'signal': 'buy', 'timeframe': '4h'},
        {'rank': 2, 'symbol': 'BTC', 'price': 43200, 'change_pct': 2.8, 'pnl_pct': 28, 'signal': 'buy', 'timeframe': '1d'}
    ]

@app.get('/api/screener')
async def screener_api():
    return await screener()

@app.get('/settings')
async def get_settings():
    return settings_store

@app.get('/api/settings')
async def get_settings_api():
    return await get_settings()

@app.post('/settings')
async def save_settings(payload: dict):
    settings_store.update(payload)
    return {'status': 'saved', 'settings': settings_store}

@app.post('/api/settings')
async def save_settings_api(payload: dict):
    return await save_settings(payload)

# ---------------------------------------------------------------------------
# Startup / shutdown hooks
# ---------------------------------------------------------------------------


@app.on_event("startup")
async def _startup_hooks() -> None:
    global SYSTEM_RUNTIME
    try:
        ensure_default_admin()
        runtime = TradingSystemRuntime(
            event_bus=EVENT_BUS,
            symbol_master=SYMBOL_MASTER,
            live_broker=UPSTOX,
            trading_mode=str(settings_store.get("trading_mode") or os.getenv("TRADING_MODE", "paper")),
        )
        SYSTEM_RUNTIME = runtime
        app.state.system_runtime = runtime
        app.state.system_runtime_task = asyncio.create_task(runtime.start())
    except Exception as exc:  # noqa: BLE001
        logger.error("Startup hooks failed: %s", exc)


@app.on_event("shutdown")
async def _shutdown_hooks() -> None:
    global SYSTEM_RUNTIME
    try:
        runtime = SYSTEM_RUNTIME or getattr(app.state, "system_runtime", None)
        if runtime is not None:
            await runtime.stop()
        task = getattr(app.state, "system_runtime_task", None)
        if task and not task.done():
            task.cancel()
    except Exception as exc:  # noqa: BLE001
        logger.error("Shutdown hooks failed: %s", exc)
    finally:
        SYSTEM_RUNTIME = None

# ---------------------------------------------------------------------------
# Broker OAuth endpoints (do not remove existing endpoints)
# ---------------------------------------------------------------------------

@app.get("/broker-login")
async def broker_login():
    """Redirect user to Upstox login page."""
    from fastapi.responses import RedirectResponse

    return RedirectResponse(_auth_manager.get_login_url())


@app.get("/broker-callback")
async def broker_callback(code: str):
    """Handle OAuth callback, exchange code for tokens."""
    ok = await _auth_manager.exchange_code(code)
    if ok:
        return {"status": "authenticated", "broker": "upstox"}
    return {"status": "failed", "error": "Token exchange failed"}


@app.get("/broker-status")
async def broker_status():
    """Check if Upstox is authenticated."""
    authed = _auth_manager.is_authenticated()
    return {
        "upstox": {
            "authenticated": authed,
            "login_url": _auth_manager.get_login_url() if not authed else None,
        }
    }


@app.post("/login")
@app.post("/api/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    """Issue a JWT for a verified dashboard user."""
    try:
        user = verify_user(form.username, form.password)
        if not user:
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        token = create_token(str(user["username"]), str(user.get("role") or "user"))
        ttl = int(os.getenv("JWT_ACCESS_TTL_SEC", "28800"))
        return {
            "access_token": token,
            "token_type": "bearer",
            "role": user.get("role", "user"),
            "expires_in": ttl,
        }
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.error("login failed: %s", exc)
        raise HTTPException(status_code=500, detail="Login failed") from exc


@app.post("/change-password")
@app.post("/api/change-password")
async def change_password(
    payload: dict,
    authorization: str | None = Header(default=None, alias="Authorization"),
):
    """Update the authenticated user's password."""
    try:
        user = _require_user(authorization)
        old_password = str(payload.get("old_password") or "")
        new_password = str(payload.get("new_password") or "")
        if not old_password or not new_password:
            raise HTTPException(status_code=400, detail="old_password and new_password are required")
        if not verify_user(str(user.get("username") or user.get("sub") or ""), old_password):
            raise HTTPException(status_code=400, detail="Wrong current password")
        if not update_password(str(user.get("username") or user.get("sub") or ""), new_password):
            raise HTTPException(status_code=500, detail="Password update failed")
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.error("change_password failed: %s", exc)
        raise HTTPException(status_code=500, detail="Password update failed") from exc

# ---------------------------------------------------------------------------
# Phase A: Institutional infra endpoints (safe defaults; admin-gated where needed)
# ---------------------------------------------------------------------------

@app.get("/api/kill-switch")
async def api_kill_switch_state():
    enabled = _kill_switch_enabled()
    return {"trading_enabled": bool(enabled), "auth_required": _auth_required()}

@app.post("/api/kill-switch")
async def api_kill_switch_toggle(
    payload: dict,
    authorization: str | None = Header(default=None, alias="Authorization"),
    admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
):
    _require_admin_access(authorization, admin_key)
    enabled = bool(payload.get("enabled"))
    _db_set_setting("TRADING_ENABLED", "true" if enabled else "false")
    if enabled:
        enable_trading()
    else:
        disable_trading()
    EVENTS.store_event("kill_switch_toggled", {"enabled": enabled}, source="dashboard")
    return {"trading_enabled": enabled}

@app.post("/api/calculate-charges")
async def api_calculate_charges(payload: dict):
    segment = str(payload.get("segment") or "intraday").lower().strip()
    seg = TradeSegment.delivery if segment == "delivery" else TradeSegment.intraday
    buy_price = float(payload.get("buy_price") or 0)
    sell_price = float(payload.get("sell_price") or 0)
    quantity = int(payload.get("quantity") or 0)
    if buy_price <= 0 or sell_price <= 0 or quantity <= 0:
        raise HTTPException(status_code=400, detail="buy_price, sell_price, quantity required")
    return CHARGES.calculate_charges(seg, buy_price=buy_price, sell_price=sell_price, quantity=quantity, using_api=True)

@app.get("/api/events")
async def api_events(event_type: str | None = None, limit: int = 100):
    limit = max(1, min(int(limit or 100), 500))
    return {"events": EVENTS.get_events(event_type=event_type, limit=limit)}

@app.post("/api/symbol-master/refresh")
async def api_symbol_master_refresh(
    authorization: str | None = Header(default=None, alias="Authorization"),
    admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
):
    _require_admin_access(authorization, admin_key)
    # NOTE: On Render, filesystem is ephemeral unless you mount a disk.
    try:
        out = await SYMBOL_MASTER.download_and_refresh()
        EVENTS.store_event("symbol_master_refreshed", out, source="dashboard")
        return out
    except Exception as exc:  # noqa: BLE001
        EVENTS.store_event("symbol_master_refresh_failed", {"error": str(exc)}, source="dashboard")
        raise HTTPException(status_code=502, detail=f"symbol master refresh failed: {exc}")

@app.get("/api/symbol-master/search")
async def api_symbol_master_search(q: str, exchange: str = "NSE", limit: int = 10):
    limit = max(1, min(int(limit or 10), 50))
    return {"results": SYMBOL_MASTER.search_symbols(q, exchange=exchange, limit=limit)}

@app.get("/api/broker/upstox/status")
async def api_upstox_status():
    return {
        "enabled": bool(ENABLE_LIVE_BROKER),
        "token_present": bool(os.getenv("UPSTOX_ACCESS_TOKEN", "").strip()),
        "client_ready": UPSTOX is not None,
    }

@app.get("/api/broker/upstox/profile")
async def api_upstox_profile():
    if not UPSTOX:
        raise HTTPException(status_code=400, detail="Upstox broker not enabled (set ENABLE_LIVE_BROKER + UPSTOX_ACCESS_TOKEN)")
    return await UPSTOX.get_profile()

@app.get("/api/broker/upstox/funds")
async def api_upstox_funds():
    if not UPSTOX:
        raise HTTPException(status_code=400, detail="Upstox broker not enabled (set ENABLE_LIVE_BROKER + UPSTOX_ACCESS_TOKEN)")
    return await UPSTOX.get_funds_and_margin()

# ---------------------------------------------------------------------------
# Watchlist + signal approval endpoints (used by the extra scripts / UI file)
# ---------------------------------------------------------------------------

@app.get('/api/watchlist')
async def api_get_watchlist():
    try:
        return _db_list_watchlist()
    except Exception:
        return watchlist_items

@app.post('/api/watchlist/add')
async def api_add_watchlist(payload: dict):
    try:
        return _db_upsert_watchlist(payload)
    except Exception:
        symbol = str(payload.get('symbol', '')).upper().strip()
        if not symbol:
            raise HTTPException(status_code=400, detail='symbol required')
        if any(item.get('symbol') == symbol and item.get('status', 'active') != 'removed' for item in watchlist_items):
            return {'status': 'exists', 'symbol': symbol}
        item = {
            'id': str(uuid.uuid4()),
            'symbol': symbol,
            'strategy_id': str(payload.get('strategy_id') or 'default'),
            'auto_trade': bool(payload.get('auto_trade', False)),
            'status': 'active',
            'added_date': datetime.now().isoformat(),
            'last_checked': None,
            'last_signal': None,
            'last_signal_price': None,
            'quantity_to_buy': int(payload.get('quantity_to_buy') or payload.get('quantity') or 1),
        }
        watchlist_items.append(item)
        return {'status': 'added', 'item': item}

@app.post('/api/watchlist/remove')
async def api_remove_watchlist(payload: dict):
    symbol = str(payload.get('symbol', '')).upper().strip()
    try:
        return _db_remove_watchlist(symbol)
    except Exception:
        if not symbol:
            raise HTTPException(status_code=400, detail='symbol required')
        for item in watchlist_items:
            if item.get('symbol') == symbol and item.get('status') != 'removed':
                item['status'] = 'removed'
                return {'status': 'removed', 'symbol': symbol}
        return {'status': 'not_found', 'symbol': symbol}

@app.get('/api/signals/pending')
async def api_pending_signals():
    try:
        db = SessionLocal()
        try:
            rows = (
                db.query(TradeSignal)
                .filter(TradeSignal.approval_status == "pending")
                .order_by(TradeSignal.signal_time.desc())
                .all()
            )
            return [
                {
                    "id": r.id,
                    "symbol": r.symbol,
                    "strategy_id": r.strategy_id,
                    "signal_type": r.signal_type,
                    "signal_price": r.signal_price,
                    "signal_time": r.signal_time,
                    "quantity": _signal_runtime_details(r.id, r.symbol)["quantity"],
                    "reason": _signal_runtime_details(r.id, r.symbol)["reason"],
                    "side": _signal_runtime_details(r.id, r.symbol)["side"],
                    "technical_score": r.technical_score,
                    "news_score": r.news_score,
                    "fundamental_score": r.fundamental_score,
                    "risk_score": r.risk_score,
                    "overall_score": r.overall_score,
                    "approval_status": r.approval_status,
                }
                for r in rows
            ]
        finally:
            db.close()
    except Exception:
        return [s for s in trade_signals if s.get('approval_status') == 'pending']


@app.get("/api/signals")
async def api_list_signals(status: str = "pending", include_executed: bool = False):
    """
    List trade signals by approval status.

    status: pending|approved|skipped|rejected|all
    include_executed: when false, hides rows with order_id set (already executed).
    """
    status = str(status or "pending").lower().strip()
    valid = {"pending", "approved", "skipped", "rejected", "all"}
    if status not in valid:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {sorted(valid)}")

    try:
        db = SessionLocal()
        try:
            q = db.query(TradeSignal)
            if status != "all":
                q = q.filter(TradeSignal.approval_status == status)
            if not include_executed:
                q = q.filter((TradeSignal.order_id == None) | (TradeSignal.order_id == ""))  # noqa: E711
            rows = q.order_by(TradeSignal.signal_time.desc()).all()
            return [
                {
                    "id": r.id,
                    "symbol": r.symbol,
                    "strategy_id": r.strategy_id,
                    "signal_type": r.signal_type,
                    "signal_price": r.signal_price,
                    "signal_time": r.signal_time,
                    "quantity": _signal_runtime_details(r.id, r.symbol)["quantity"],
                    "reason": _signal_runtime_details(r.id, r.symbol)["reason"],
                    "side": _signal_runtime_details(r.id, r.symbol)["side"],
                    "technical_score": r.technical_score,
                    "news_score": r.news_score,
                    "fundamental_score": r.fundamental_score,
                    "risk_score": r.risk_score,
                    "overall_score": r.overall_score,
                    "approval_status": r.approval_status,
                    "approval_time": r.approval_time,
                    "order_id": r.order_id,
                    "execution_price": r.execution_price,
                    "execution_time": r.execution_time,
                }
                for r in rows
            ]
        finally:
            db.close()
    except Exception:
        # In-memory fallback (best-effort)
        out = trade_signals
        if status != "all":
            out = [s for s in out if s.get("approval_status") == status]
        if not include_executed:
            out = [s for s in out if not s.get("order_id")]
        return out


@app.get("/api/signals/approved")
async def api_approved_signals(include_executed: bool = False):
    """Convenience endpoint for the trade execution agent."""
    return await api_list_signals(status="approved", include_executed=include_executed)


@app.post("/api/signal/mark-executed")
async def api_mark_signal_executed(payload: dict):
    """
    Mark an approved signal as executed (prevents double-execution).

    Payload:
      signal_id: str
      order_id: str
      execution_price: float (optional)
      broker: str (optional)
    """
    sid = str(payload.get("signal_id") or payload.get("id") or "").strip()
    order_id = str(payload.get("order_id") or "").strip()
    if not sid or not order_id:
        raise HTTPException(status_code=400, detail="signal_id and order_id required")
    exec_price = payload.get("execution_price")
    try:
        exec_price_val = float(exec_price) if exec_price is not None else None
    except Exception:
        exec_price_val = None

    updated = False
    try:
        db = SessionLocal()
        try:
            row = db.query(TradeSignal).filter(TradeSignal.id == sid).first()
            if not row:
                return {"status": "not_found", "signal_id": sid}
            row.order_id = order_id
            row.execution_time = datetime.now().isoformat()
            if exec_price_val is not None:
                row.execution_price = exec_price_val
            db.commit()
            updated = True
        finally:
            db.close()
    except Exception:
        updated = False

    for s in trade_signals:
        if str(s.get("id")) == sid:
            s["order_id"] = order_id
            s["execution_time"] = datetime.now().isoformat()
            if exec_price_val is not None:
                s["execution_price"] = exec_price_val
            updated = True

    return {"status": "executed" if updated else "error", "signal_id": sid, "order_id": order_id}

@app.post('/api/signal/approve')
async def api_approve_signal(payload: dict):
    sid = payload.get('signal_id') or payload.get('id')
    if not sid:
        raise HTTPException(status_code=400, detail='signal_id required')
    # Update DB first (source of truth), then mirror to in-memory list.
    try:
        db = SessionLocal()
        try:
            row = db.query(TradeSignal).filter(TradeSignal.id == str(sid)).first()
            if not row:
                return {'status': 'not_found', 'signal_id': sid}
            row.approval_status = 'approved'
            row.approval_time = datetime.now().isoformat()
            row.approval_reason = str(payload.get('reason') or 'Approved in dashboard')
            db.commit()
            signal_out = {
                "id": row.id,
                "symbol": row.symbol,
                "strategy_id": row.strategy_id,
                "signal_type": row.signal_type,
                "signal_price": row.signal_price,
                "signal_time": row.signal_time,
                "technical_score": row.technical_score,
                "news_score": row.news_score,
                "fundamental_score": row.fundamental_score,
                "risk_score": row.risk_score,
                "overall_score": row.overall_score,
                "approval_status": row.approval_status,
                "approval_time": row.approval_time,
            }
        finally:
            db.close()
        for s in trade_signals:
            if str(s.get('id')) == str(sid):
                s['approval_status'] = 'approved'
                s['approval_time'] = datetime.now().isoformat()
        return {'status': 'approved', 'signal': signal_out}
    except Exception:
        for s in trade_signals:
            if str(s.get('id')) == str(sid):
                s['approval_status'] = 'approved'
                s['approval_time'] = datetime.now().isoformat()
                return {'status': 'approved', 'signal': s}
        return {'status': 'not_found', 'signal_id': sid}

@app.post('/api/signal/skip')
async def api_skip_signal(payload: dict):
    sid = payload.get('signal_id') or payload.get('id')
    if not sid:
        raise HTTPException(status_code=400, detail='signal_id required')
    reason = str(payload.get('reason') or 'Skipped in dashboard')
    try:
        db = SessionLocal()
        try:
            row = db.query(TradeSignal).filter(TradeSignal.id == str(sid)).first()
            if not row:
                return {'status': 'not_found', 'signal_id': sid}
            row.approval_status = 'skipped'
            row.approval_time = datetime.now().isoformat()
            row.approval_reason = reason
            db.commit()
        finally:
            db.close()
        for s in trade_signals:
            if str(s.get('id')) == str(sid):
                s['approval_status'] = 'skipped'
                s['approval_time'] = datetime.now().isoformat()
        return {'status': 'skipped', 'signal_id': sid}
    except Exception:
        for s in trade_signals:
            if str(s.get('id')) == str(sid):
                s['approval_status'] = 'skipped'
                s['approval_time'] = datetime.now().isoformat()
                return {'status': 'skipped', 'signal_id': sid}
        return {'status': 'not_found', 'signal_id': sid}


@app.patch("/api/signals/{signal_id}")
async def api_update_signal(signal_id: str, payload: dict, authorization: str | None = Header(default=None, alias="Authorization"), admin_key: str | None = Header(default=None, alias="X-Admin-Key")):
    """Generic signal status update endpoint used by Telegram and the execution agent."""
    _require_admin_access(authorization, admin_key)
    status = str(payload.get("status") or "").lower().strip()
    reason = payload.get("reason")
    order_id = str(payload.get("order_id") or "").strip() or None
    execution_price = payload.get("execution_price")

    valid = {"pending", "approved", "rejected", "skipped", "executing", "filled", "cancelled", "canceled"}
    if status not in valid:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {sorted(valid)}")

    try:
        exec_price_val = float(execution_price) if execution_price not in (None, "") else None
    except Exception:
        exec_price_val = None

    try:
        db = SessionLocal()
        try:
            row = db.query(TradeSignal).filter(TradeSignal.id == str(signal_id)).first()
            if not row:
                return {"status": "not_found", "signal_id": signal_id}

            current_status = str(row.approval_status or "pending").lower().strip()
            terminal = {"rejected", "skipped", "filled", "cancelled", "canceled"}
            allowed_transitions = {
                "pending": {"approved", "rejected", "skipped", "executing", "cancelled", "canceled"},
                "approved": {"executing", "filled", "cancelled", "canceled"},
                "executing": {"filled", "cancelled", "canceled"},
            }
            if current_status == status:
                return {
                    "status": current_status,
                    "signal": {
                        "id": row.id,
                        "symbol": row.symbol,
                        "strategy_id": row.strategy_id,
                        "signal_type": row.signal_type,
                        "signal_price": row.signal_price,
                        "signal_time": row.signal_time,
                        "quantity": _signal_runtime_details(row.id, row.symbol)["quantity"],
                        "reason": _signal_runtime_details(row.id, row.symbol)["reason"],
                        "side": _signal_runtime_details(row.id, row.symbol)["side"],
                        "approval_status": row.approval_status,
                        "approval_time": row.approval_time,
                        "approval_reason": row.approval_reason,
                        "order_id": row.order_id,
                        "execution_price": row.execution_price,
                        "execution_time": row.execution_time,
                    },
                }
            if current_status in terminal and status != current_status:
                raise HTTPException(status_code=409, detail="Signal already finalized")
            if status not in allowed_transitions.get(current_status, set()) and current_status not in terminal:
                raise HTTPException(status_code=409, detail=f"Invalid transition from {current_status} to {status}")

            row.approval_status = status
            row.approval_time = datetime.now().isoformat()
            if reason is not None:
                row.approval_reason = str(reason)
            if order_id:
                row.order_id = order_id
            if exec_price_val is not None:
                row.execution_price = exec_price_val
            if status in {"filled", "cancelled", "canceled"}:
                row.execution_time = datetime.now().isoformat()
            db.commit()

            signal_out = {
                "id": row.id,
                "symbol": row.symbol,
                "strategy_id": row.strategy_id,
                "signal_type": row.signal_type,
                "signal_price": row.signal_price,
                "signal_time": row.signal_time,
                "quantity": _signal_runtime_details(row.id, row.symbol)["quantity"],
                "reason": _signal_runtime_details(row.id, row.symbol)["reason"],
                "side": _signal_runtime_details(row.id, row.symbol)["side"],
                "approval_status": row.approval_status,
                "approval_time": row.approval_time,
                "approval_reason": row.approval_reason,
                "order_id": row.order_id,
                "execution_price": row.execution_price,
                "execution_time": row.execution_time,
            }
        finally:
            db.close()

        for s in trade_signals:
            if str(s.get("id")) == str(signal_id):
                s["approval_status"] = status
                s["approval_time"] = datetime.now().isoformat()
                if reason is not None:
                    s["reason"] = reason
                if order_id:
                    s["order_id"] = order_id
                if exec_price_val is not None:
                    s["execution_price"] = exec_price_val
                if status in {"filled", "cancelled", "canceled"}:
                    s["execution_time"] = datetime.now().isoformat()
                break

        return {"status": status, "signal": signal_out}
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.error("api_update_signal failed: %s", exc)
        raise HTTPException(status_code=500, detail="Signal update failed") from exc

# ---------------------------------------------------------------------------
# Non-/api aliases for the "production architecture" spec (keeps UI/scripts happy)
# ---------------------------------------------------------------------------

@app.get("/watchlist")
async def get_watchlist_alias():
    return await api_get_watchlist()

@app.post("/watchlist/add")
async def add_watchlist_alias(payload: dict):
    return await api_add_watchlist(payload)

@app.delete("/watchlist/{symbol}")
async def remove_watchlist_alias(symbol: str):
    # Uses the DB helper directly (preferred), falls back to in-memory.
    try:
        return _db_remove_watchlist(symbol)
    except Exception:
        sym = str(symbol).upper().strip()
        for item in watchlist_items:
            if item.get("symbol") == sym and item.get("status") != "removed":
                item["status"] = "removed"
                return {"status": "removed", "symbol": sym}
        return {"status": "not_found", "symbol": sym}

@app.get("/signals/pending")
async def pending_signals_alias():
    return await api_pending_signals()

@app.get("/signals/approved")
async def approved_signals_alias(include_executed: bool = False):
    return await api_approved_signals(include_executed=include_executed)

@app.post("/signal/approve")
async def approve_signal_alias(payload: dict):
    return await api_approve_signal(payload)

@app.post("/signal/skip")
async def skip_signal_alias(payload: dict):
    return await api_skip_signal(payload)

@app.post("/signal/mark-executed")
async def mark_executed_alias(payload: dict):
    return await api_mark_signal_executed(payload)

@app.get('/api/system/health')
async def api_system_health():
    # Minimal health payload for UI; you can expand this later.
    runtime = getattr(app.state, "system_runtime", None)
    return {
        'timestamp': datetime.now().isoformat(),
        'ollama_status': 'unknown',
        'broker_status': 'enabled' if UPSTOX else ('disabled' if ENABLE_LIVE_BROKER else 'paper'),
        'agents_online': len(agent_states),
        'alert_cooldown_seconds': ALERT_COOLDOWN_SECONDS,
        'trading_enabled': _kill_switch_enabled(),
        'auth_required': _auth_required(),
        'enforce_charges_filter': os.getenv("ENFORCE_CHARGES_FILTER", "true").strip().lower() in {"1", "true", "yes", "on"},
        'enforce_capital_allocator': os.getenv("ENFORCE_CAPITAL_ALLOCATOR", "true").strip().lower() in {"1", "true", "yes", "on"},
        'runtime_running': bool(runtime and getattr(runtime, "status", None) and runtime.status().get("running")),
        'runtime_mode': runtime.status().get("mode") if runtime and getattr(runtime, "status", None) else None,
    }


@app.get('/api/runtime/status')
async def api_runtime_status():
    runtime = getattr(app.state, "system_runtime", None)
    if not runtime or not getattr(runtime, "status", None):
        return {"running": False, "mode": "unknown"}
    return runtime.status()

@app.get('/api/portfolio')
async def api_portfolio():
    total_value = 0.0
    total_pnl = 0.0
    for p in await get_positions():
        qty = float(p.get('qty') or 0)
        cur = float(p.get('current_price') or 0)
        total_value += qty * cur
        total_pnl += float(p.get('pnl') or 0)
    total_pnl_pct = (total_pnl / total_value * 100) if total_value else 0.0
    return {
        'total_value': total_value,
        'total_pnl': total_pnl,
        'total_pnl_pct': total_pnl_pct,
        'open_positions': len(positions),
    }

@app.post('/settings/keys')
async def save_settings_keys(payload: dict):
    settings_store['broker'] = payload.get('broker', settings_store.get('broker', 'upstox'))
    settings_store['api_key'] = payload.get('api_key', settings_store.get('api_key', ''))
    settings_store['api_secret'] = payload.get('api_secret', settings_store.get('api_secret', ''))
    return {'status': 'saved', 'settings': settings_store}

@app.post('/settings/mode')
async def save_settings_mode(payload: dict):
    settings_store['trading_mode'] = payload.get('trading_mode', settings_store.get('trading_mode', 'paper'))
    return {'status': 'saved', 'settings': settings_store}

@app.post('/settings/risk')
async def save_settings_risk(payload: dict):
    settings_store['max_position_size'] = payload.get('max_position_size', settings_store.get('max_position_size', 5))
    settings_store['max_daily_loss'] = payload.get('max_daily_loss', settings_store.get('max_daily_loss', 2))
    settings_store['max_correlation'] = payload.get('max_correlation', settings_store.get('max_correlation', 0.7))
    return {'status': 'saved', 'settings': settings_store}

@app.post('/settings/ollama')
async def save_settings_ollama(payload: dict):
    settings_store['ollama_model'] = payload.get('ollama_model', settings_store.get('ollama_model', 'deepseek-r1:7b'))
    settings_store['ollama_url'] = payload.get('ollama_url', settings_store.get('ollama_url', 'http://localhost:11434'))
    return {'status': 'saved', 'settings': settings_store}

BASE_DIR = Path(__file__).parent.parent
frontend_path = BASE_DIR / 'frontend' / 'dist'
if frontend_path.exists():
    app.mount('/', StaticFiles(directory=str(frontend_path), html=True), name='static')

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

--- END FILE: trading-dashboard\backend\main.py ---

--- START FILE: trading-dashboard\backend\requirements.txt ---
fastapi==0.111.0
uvicorn[standard]==0.29.0
sqlalchemy==2.0.30
pydantic==2.5.3
pydantic-core==2.14.6
python-multipart==0.0.9
aiohttp==3.9.5
gunicorn==22.0.0
psycopg2-binary==2.9.9
python-dotenv==1.0.1
httpx==0.27.0
cryptography>=42.0.0
python-multipart>=0.0.9
python-jose[cryptography]>=3.3.0
passlib>=1.7.4
textblob>=0.17.1

--- END FILE: trading-dashboard\backend\requirements.txt ---

--- START FILE: trading-dashboard\backend\user_store.py ---
"""SQLite-backed dashboard user store with password hashing and admin bootstrap."""
from __future__ import annotations

import hashlib
import logging
import os
import secrets
import sqlite3
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)
DB_PATH = Path(os.getenv("USER_DB_PATH", "data/users.db"))
PBKDF2_ITERS = int(os.getenv("PASSWORD_HASH_ITERATIONS", "210000"))


def _normalize_username(username: str) -> str:
    return (username or "").strip().lower()


def _init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at INTEGER,
                last_login INTEGER
            )
            """
        )


def _hash(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERS,
    ).hex()


def create_user(username: str, password: str, role: str = "user") -> bool:
    """Create a user with a salted password hash."""
    _init_db()
    try:
        uname = _normalize_username(username)
        if not uname or not password:
            return False
        salt = secrets.token_hex(16)
        password_hash = _hash(password, salt)
        with sqlite3.connect(DB_PATH) as con:
            con.execute(
                """
                INSERT INTO users (username, password_hash, salt, role, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (uname, password_hash, salt, str(role or "user"), int(time.time())),
            )
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as exc:  # noqa: BLE001
        logger.error("create_user failed: %s", exc)
        return False


def verify_user(username: str, password: str) -> Optional[dict]:
    """Verify a username/password pair and return the user payload on success."""
    _init_db()
    try:
        uname = _normalize_username(username)
        with sqlite3.connect(DB_PATH) as con:
            row = con.execute(
                "SELECT id, password_hash, salt, role FROM users WHERE username=?",
                (uname,),
            ).fetchone()
        if not row:
            return None
        user_id, password_hash, salt, role = row
        if _hash(password, str(salt)) != str(password_hash):
            return None
        with sqlite3.connect(DB_PATH) as con:
            con.execute(
                "UPDATE users SET last_login=? WHERE id=?",
                (int(time.time()), int(user_id)),
            )
        return {"id": int(user_id), "username": uname, "role": str(role or "user")}
    except Exception as exc:  # noqa: BLE001
        logger.error("verify_user failed: %s", exc)
        return None


def update_password(username: str, new_password: str) -> bool:
    """Update an existing user's password."""
    _init_db()
    try:
        uname = _normalize_username(username)
        if not uname or not new_password:
            return False
        salt = secrets.token_hex(16)
        password_hash = _hash(new_password, salt)
        with sqlite3.connect(DB_PATH) as con:
            cur = con.execute(
                "UPDATE users SET password_hash=?, salt=? WHERE username=?",
                (password_hash, salt, uname),
            )
            return bool(cur.rowcount)
    except Exception as exc:  # noqa: BLE001
        logger.error("update_password failed: %s", exc)
        return False


def ensure_default_admin() -> None:
    """Create a default admin user if the database is empty."""
    _init_db()
    try:
        with sqlite3.connect(DB_PATH) as con:
            count = int(con.execute("SELECT COUNT(*) FROM users").fetchone()[0] or 0)
        if count == 0:
            admin_pw = os.getenv("ADMIN_PASSWORD", "change-me-now")
            if create_user("admin", admin_pw, "admin"):
                logger.warning("Default admin created. Set ADMIN_PASSWORD to replace the default password.")
    except Exception as exc:  # noqa: BLE001
        logger.error("ensure_default_admin failed: %s", exc)

--- END FILE: trading-dashboard\backend\user_store.py ---

--- START FILE: trading-dashboard\backend\__init__.py ---
"""Backend package marker for reliable imports on Render."""


--- END FILE: trading-dashboard\backend\__init__.py ---

--- START FILE: trading-dashboard\backend\agents\news_sentiment_agent.py ---
"""NewsAPI-backed sentiment agent that publishes symbol scores to the event bus."""
from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
NEWSAPI_URL = "https://newsapi.org/v2/everything"
CACHE_TTL = 3600


def _score_text(text: str) -> float:
    """Return a sentiment polarity score in the range -1.0..+1.0."""
    if not text:
        return 0.0
    try:
        from textblob import TextBlob

        return float(TextBlob(text).sentiment.polarity)
    except ImportError:
        positive = ["growth", "profit", "record", "beat", "strong", "surge", "gain", "up", "bullish", "buy"]
        negative = ["loss", "decline", "miss", "fall", "weak", "cut", "down", "bearish", "sell", "risk"]
        text_l = text.lower()
        score = sum(1 for word in positive if word in text_l)
        score -= sum(1 for word in negative if word in text_l)
        return max(-1.0, min(1.0, score / 5.0))
    except Exception as exc:  # noqa: BLE001
        logger.debug("Sentiment scoring fallback failed: %s", exc)
        return 0.0


class NewsSentimentAgent:
    """Fetches and caches recent symbol news, then emits sentiment events."""

    def __init__(self, event_bus: Any, watchlist: list[str]):
        self._bus = event_bus
        self._watchlist = [str(symbol).replace(".NS", "").replace(".BO", "").upper() for symbol in watchlist]
        self._cache: dict[str, dict] = {}
        self._running = False

    async def start(self) -> None:
        """Run the periodic sentiment loop."""
        try:
            self._running = True
            while self._running:
                for symbol in self._watchlist:
                    try:
                        await self._analyze(symbol)
                    except Exception as exc:  # noqa: BLE001
                        logger.error("News error for %s: %s", symbol, exc)
                    await asyncio.sleep(2)
                await asyncio.sleep(1800)
        except Exception as exc:  # noqa: BLE001
            logger.error("NewsSentimentAgent start failed: %s", exc)

    async def stop(self) -> None:
        """Stop the periodic loop."""
        try:
            self._running = False
        except Exception as exc:  # noqa: BLE001
            logger.error("NewsSentimentAgent stop failed: %s", exc)

    async def get_sentiment(self, symbol: str) -> Optional[dict]:
        """Return the cached sentiment snapshot, if any."""
        try:
            return self._cache.get(str(symbol).upper())
        except Exception as exc:  # noqa: BLE001
            logger.error("get_sentiment failed: %s", exc)
            return None

    async def _analyze(self, symbol: str) -> None:
        """Fetch headlines, score them, and publish a symbol-level sentiment payload."""
        try:
            sym = str(symbol).upper()
            cached = self._cache.get(sym)
            if cached and (time.time() - float(cached.get("fetched_at", 0))) < CACHE_TTL:
                return

            if not NEWSAPI_KEY:
                logger.warning("NEWSAPI_KEY not set - news agent disabled")
                return

            articles = await self._fetch(sym)
            if not articles:
                return

            scores: list[float] = []
            headlines: list[str] = []
            for article in articles[:10]:
                title = str(article.get("title") or "")
                description = str(article.get("description") or "")
                if title:
                    headlines.append(title)
                scores.append(_score_text(f"{title} {description}"))

            if not scores:
                return

            avg_raw = sum(scores) / len(scores)
            sentiment_100 = round((avg_raw + 1.0) / 2.0 * 100.0, 1)
            result = {
                "symbol": sym,
                "score": sentiment_100,
                "label": "bullish" if sentiment_100 > 60 else "bearish" if sentiment_100 < 40 else "neutral",
                "article_count": len(scores),
                "top_headlines": headlines[:3],
                "fetched_at": time.time(),
            }
            self._cache[sym] = result
            await self._bus.publish("news.sentiment", result)
            logger.info("News sentiment %s: %.1f (%s)", sym, sentiment_100, result["label"])
        except Exception as exc:  # noqa: BLE001
            logger.error("_analyze failed for %s: %s", symbol, exc)

    async def _fetch(self, symbol: str) -> list[dict]:
        """Fetch recent articles for a symbol from NewsAPI."""
        try:
            params = {
                "q": symbol,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 10,
                "apiKey": NEWSAPI_KEY,
            }
            exclude = os.getenv("NEWSAPI_EXCLUDE_DOMAINS", "").strip()
            if exclude:
                params["excludeDomains"] = exclude

            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(NEWSAPI_URL, params=params)
                resp.raise_for_status()
                payload = resp.json()
                return payload.get("articles", []) if isinstance(payload, dict) else []
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 429:
                logger.warning("NewsAPI rate limit hit. Sleeping 1h.")
                await asyncio.sleep(3600)
            elif exc.response.status_code == 401:
                logger.error("NewsAPI key invalid. Check NEWSAPI_KEY env var.")
            return []
        except Exception as exc:  # noqa: BLE001
            logger.error("NewsAPI fetch error: %s", exc)
            return []


--- END FILE: trading-dashboard\backend\agents\news_sentiment_agent.py ---

--- START FILE: trading-dashboard\backend\agents\trade_execution_agent.py ---
"""Signal-to-broker execution agent with charge filtering and fill tracking."""
from __future__ import annotations

import asyncio
import inspect
import logging
import os
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Optional

import httpx

try:
    from backend.brokerage.charges_engine import TradeSegment  # type: ignore
    from backend.portfolio.position_manager import PositionManager  # type: ignore
except ModuleNotFoundError:  # noqa: BLE001
    from brokerage.charges_engine import TradeSegment  # type: ignore
    from portfolio.position_manager import PositionManager  # type: ignore

logger = logging.getLogger(__name__)
DB_PATH = Path(os.getenv("EXECUTIONS_DB_PATH", "data/executions.db"))


def _normalize_dashboard_url(raw_url: str | None) -> str:
    """Prefer a loopback-safe dashboard URL for local paper-mode tests."""
    url = str(raw_url or "").strip().rstrip("/")
    if not url:
        return "http://127.0.0.1:8000"
    if url.startswith("http://localhost"):
        return url.replace("localhost", "127.0.0.1", 1)
    if url.startswith("https://localhost"):
        return url.replace("localhost", "127.0.0.1", 1)
    return url


DASHBOARD_URL = _normalize_dashboard_url(os.getenv("DASHBOARD_URL"))


class TradeExecutionAgent:
    """Polls approved dashboard signals, executes them, and monitors fills."""

    def __init__(
        self,
        broker_router: Any,
        risk_guardian: Any,
        charges_engine: Any,
        position_manager: PositionManager,
        event_bus: Any,
    ) -> None:
        self.broker = broker_router
        self.risk = risk_guardian
        self.charges = charges_engine
        self.positions = position_manager
        self.bus = event_bus
        self._running = False
        self._placed: dict[str, str] = {}
        self._init_db()
        self._load_existing_orders()

    def _init_db(self) -> None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(DB_PATH) as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_order_id TEXT UNIQUE,
                    broker_order_id TEXT,
                    signal_id TEXT,
                    broker TEXT,
                    symbol TEXT,
                    side TEXT,
                    quantity INTEGER,
                    entry_price REAL,
                    status TEXT DEFAULT 'submitted',
                    reject_reason TEXT,
                    created_at INTEGER
                )
                """
            )

    def _load_existing_orders(self) -> None:
        try:
            with sqlite3.connect(DB_PATH) as con:
                rows = con.execute(
                    """
                    SELECT client_order_id, broker_order_id
                    FROM executions
                    WHERE broker_order_id IS NOT NULL AND broker_order_id != ''
                    """
                ).fetchall()
            self._placed = {str(row[0]): str(row[1]) for row in rows}
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not load existing executions: %s", exc)

    async def start(self) -> None:
        """Run the polling and order-monitoring loops forever."""
        try:
            self._running = True
            logger.info("TradeExecutionAgent started")
            await asyncio.gather(self._poll_approved_signals(), self._monitor_open_orders())
        except Exception as exc:  # noqa: BLE001
            logger.error("TradeExecutionAgent start failed: %s", exc)

    async def stop(self) -> None:
        """Stop the agent loops."""
        try:
            self._running = False
        except Exception as exc:  # noqa: BLE001
            logger.error("TradeExecutionAgent stop failed: %s", exc)

    def _auth_headers(self) -> dict[str, str]:
        token = os.getenv("DASHBOARD_API_TOKEN", "").strip()
        if token:
            return {"Authorization": f"Bearer {token}"}
        admin_key = os.getenv("ADMIN_API_KEY", "").strip()
        return {"X-Admin-Key": admin_key} if admin_key else {}

    def _resolve_broker(self, broker_name: str) -> Any:
        if hasattr(self.broker, "brokers") and isinstance(getattr(self.broker, "brokers"), dict):
            return self.broker.brokers.get(broker_name)
        return self.broker

    @staticmethod
    def _extract_order_id(result: Any) -> str:
        if isinstance(result, dict):
            nested = result.get("data") if isinstance(result.get("data"), dict) else None
            if nested and nested.get("order_id"):
                return str(nested["order_id"])
            if result.get("order_id"):
                return str(result["order_id"])
        return ""

    async def _poll_approved_signals(self) -> None:
        """Poll dashboard every few seconds for approved signals."""
        try:
            async with httpx.AsyncClient(timeout=10, trust_env=False) as client:
                while self._running:
                    try:
                        resp = await client.get(f"{DASHBOARD_URL}/api/signals/approved", headers=self._auth_headers())
                        if resp.status_code == 200:
                            payload = resp.json()
                            signals = payload if isinstance(payload, list) else payload.get("signals", [])
                            for signal in signals:
                                await self._execute_signal(signal)
                    except Exception as exc:  # noqa: BLE001
                        logger.warning("Poll error: %s", exc)
                    await asyncio.sleep(5)
        except Exception as exc:  # noqa: BLE001
            logger.error("_poll_approved_signals failed: %s", exc)

    async def _execute_signal(self, signal: dict[str, Any]) -> None:
        """Validate a signal and push it through risk, charges, and broker execution."""
        try:
            signal_id = str(signal.get("id") or signal.get("signal_id") or "unknown")
            symbol = str(signal.get("symbol") or "").upper().strip()
            side = str(signal.get("side") or signal.get("signal_type") or "buy").lower().strip()
            quantity = int(signal.get("quantity") or signal.get("qty") or signal.get("quantity_to_buy") or 0)
            price = float(signal.get("price") or signal.get("signal_price") or signal.get("entry_price") or 0)
            target = float(signal.get("expected_exit") or signal.get("take_profit") or (price * 1.03))
            broker_name = str(signal.get("broker") or "upstox").lower().strip()
            trade_segment = str(signal.get("trade_segment") or "intraday").lower().strip()
            segment = TradeSegment.delivery if trade_segment == "delivery" else TradeSegment.intraday

            if not symbol or quantity <= 0 or price <= 0:
                logger.warning("Skipping malformed signal: %s", signal)
                return

            client_order_id = str(
                uuid.uuid5(uuid.NAMESPACE_DNS, f"{symbol}_{side}_{quantity}_{signal_id}")
            )
            if client_order_id in self._placed:
                logger.info("Duplicate signal %s skipped", signal_id)
                return

            if side == "sell":
                buy_price = target
                sell_price = price
            else:
                buy_price = price
                sell_price = target

            charges = self.charges.calculate_charges(
                segment,
                buy_price=buy_price,
                sell_price=sell_price,
                quantity=quantity,
                using_api=True,
            )
            if not charges.get("should_execute", False):
                reason = f"Charges reject: ratio={charges.get('profitability_ratio')}x"
                logger.warning(reason)
                await self._save_execution(
                    client_order_id,
                    None,
                    signal_id,
                    broker_name,
                    symbol,
                    side,
                    quantity,
                    price,
                    "rejected_charges",
                    reason,
                )
                await self._update_signal_status(signal_id, "rejected", reason)
                return

            risk_result = await self.risk.evaluate(
                {
                    "symbol": symbol,
                    "side": side,
                    "quantity": quantity,
                    "price": price,
                    "expected_exit": target,
                }
            )
            if risk_result.get("action") == "REJECT":
                reason = str(risk_result.get("reason") or "risk_reject")
                logger.warning("Risk reject: %s", reason)
                await self._save_execution(
                    client_order_id,
                    None,
                    signal_id,
                    broker_name,
                    symbol,
                    side,
                    quantity,
                    price,
                    "rejected_risk",
                    reason,
                )
                await self._update_signal_status(signal_id, "rejected", reason)
                return

            # Mark the signal as in-progress before placing the order to avoid duplicate loops.
            await self._update_signal_status(signal_id, "executing", None)

            broker = self._resolve_broker(broker_name)
            if not broker:
                raise RuntimeError(f"Broker not available: {broker_name}")

            try:
                if hasattr(self.broker, "brokers"):
                    result = await self.broker.place_order(
                        broker_name=broker_name,
                        symbol=symbol,
                        side=side,
                        quantity=quantity,
                        order_type="MARKET",
                        price=price,
                        take_profit=target,
                        client_order_id=client_order_id,
                    )
                else:
                    result = await broker.place_order(
                        symbol=symbol,
                        side=side,
                        quantity=quantity,
                        client_order_id=client_order_id,
                        order_type="MARKET",
                        price=price,
                        stop_loss=None,
                        take_profit=target,
                        product=str(signal.get("product") or "I"),
                        validity=str(signal.get("validity") or "DAY"),
                    )
            except TypeError:
                result = await broker.place_order(symbol=symbol, side=side, quantity=quantity, order_type="MARKET")

            broker_oid = self._extract_order_id(result)
            if not broker_oid:
                reason = f"No order_id returned: {result}"
                await self._save_execution(
                    client_order_id,
                    None,
                    signal_id,
                    broker_name,
                    symbol,
                    side,
                    quantity,
                    price,
                    "no_order_id",
                    reason,
                )
                await self._update_signal_status(signal_id, "rejected", reason)
                return

            self._placed[client_order_id] = broker_oid
            await self._save_execution(
                client_order_id,
                broker_oid,
                signal_id,
                broker_name,
                symbol,
                side,
                quantity,
                price,
                "submitted",
                None,
            )
            await self.bus.publish(
                "order.placed",
                {
                    "client_order_id": client_order_id,
                    "broker_order_id": broker_oid,
                    "signal_id": signal_id,
                    "symbol": symbol,
                    "side": side,
                    "quantity": quantity,
                    "broker": broker_name,
                },
            )
            asyncio.create_task(
                self._monitor_fill(
                    broker_name=broker_name,
                    broker_oid=broker_oid,
                    client_oid=client_order_id,
                    signal_id=signal_id,
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                )
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("_execute_signal failed: %s", exc)

    async def _monitor_fill(
        self,
        broker_name: str,
        broker_oid: str,
        client_oid: str,
        signal_id: str,
        symbol: str,
        side: str,
        quantity: int,
    ) -> None:
        """Poll order status until the broker reports a final state."""
        try:
            deadline = time.time() + 120
            broker = self._resolve_broker(broker_name)
            if not broker:
                return

            while self._running and time.time() < deadline:
                await asyncio.sleep(5)
                try:
                    status = await broker.get_order_status(broker_oid)
                    state = str(status.get("status") or status.get("order_status") or "").lower()
                    if state in ("complete", "filled", "traded", "fully_executed"):
                        fill_price = float(status.get("average_price") or status.get("avg_price") or 0.0)
                        filled_qty = int(status.get("filled_quantity") or status.get("quantity") or quantity)
                        await self.positions.on_fill(broker_name, symbol, side, filled_qty, fill_price)
                        await self._update_execution_status(client_oid, "filled", fill_price)
                        await self._update_signal_status(signal_id, "filled", None)
                        await self.bus.publish(
                            "order.filled",
                            {
                                "client_order_id": client_oid,
                                "broker_order_id": broker_oid,
                                "signal_id": signal_id,
                                "symbol": symbol,
                                "side": side,
                                "filled_qty": filled_qty,
                                "fill_price": fill_price,
                            },
                        )
                        logger.info("Order filled: %s %s @ %.2f", symbol, side, fill_price)
                        return
                    if state in ("rejected", "cancelled", "canceled", "expired"):
                        await self._update_execution_status(client_oid, state, None)
                        await self._update_signal_status(signal_id, state, state)
                        await self.bus.publish(
                            "order.rejected",
                            {"client_order_id": client_oid, "symbol": symbol, "reason": state},
                        )
                        logger.warning("Order %s: %s", state, broker_oid)
                        return
                except Exception as exc:  # noqa: BLE001
                    logger.error("Monitor fill error: %s", exc)
            logger.warning("Order monitoring timeout: %s", broker_oid)
        except Exception as exc:  # noqa: BLE001
            logger.error("_monitor_fill failed: %s", exc)

    async def _monitor_open_orders(self) -> None:
        """Catch missed fills by periodically rechecking older submitted orders."""
        try:
            while self._running:
                await asyncio.sleep(60)
                with sqlite3.connect(DB_PATH) as con:
                    rows = con.execute(
                        """
                        SELECT client_order_id, broker_order_id, broker, signal_id, symbol, side, quantity
                        FROM executions
                        WHERE status='submitted' AND created_at < ?
                        """,
                        (int(time.time()) - 120,),
                    ).fetchall()
                for row in rows:
                    asyncio.create_task(
                        self._monitor_fill(
                            broker_name=str(row[2]),
                            broker_oid=str(row[1]),
                            client_oid=str(row[0]),
                            signal_id=str(row[3] or ""),
                            symbol=str(row[4]),
                            side=str(row[5]),
                            quantity=int(row[6] or 0),
                        )
                    )
        except Exception as exc:  # noqa: BLE001
            logger.error("_monitor_open_orders failed: %s", exc)

    async def _save_execution(
        self,
        client_oid: str,
        broker_oid: Optional[str],
        signal_id: str,
        broker: str,
        symbol: str,
        side: str,
        qty: int,
        price: float,
        status: str,
        reason: Optional[str],
    ) -> None:
        try:
            with sqlite3.connect(DB_PATH) as con:
                con.execute(
                    """
                    INSERT INTO executions (
                        client_order_id, broker_order_id, signal_id, broker, symbol,
                        side, quantity, entry_price, status, reject_reason, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(client_order_id) DO UPDATE SET
                        broker_order_id=excluded.broker_order_id,
                        signal_id=excluded.signal_id,
                        broker=excluded.broker,
                        symbol=excluded.symbol,
                        side=excluded.side,
                        quantity=excluded.quantity,
                        entry_price=excluded.entry_price,
                        status=excluded.status,
                        reject_reason=excluded.reject_reason
                    """,
                    (
                        client_oid,
                        broker_oid,
                        signal_id,
                        broker,
                        symbol,
                        side,
                        int(qty),
                        float(price),
                        status,
                        reason,
                        int(time.time()),
                    ),
                )
        except Exception as exc:  # noqa: BLE001
            logger.error("_save_execution failed: %s", exc)

    async def _update_execution_status(self, client_oid: str, status: str, fill_price: Optional[float]) -> None:
        try:
            with sqlite3.connect(DB_PATH) as con:
                if fill_price is not None:
                    con.execute(
                        "UPDATE executions SET status=?, entry_price=? WHERE client_order_id=?",
                        (status, float(fill_price), client_oid),
                    )
                else:
                    con.execute("UPDATE executions SET status=? WHERE client_order_id=?", (status, client_oid))
        except Exception as exc:  # noqa: BLE001
            logger.error("_update_execution_status failed: %s", exc)

    async def _update_signal_status(self, signal_id: str, status: str, reason: Optional[str]) -> None:
        """Update the dashboard signal row through the API."""
        try:
            async with httpx.AsyncClient(timeout=10, trust_env=False) as client:
                resp = await client.patch(
                    f"{DASHBOARD_URL}/api/signals/{signal_id}",
                    json={"status": status, "reason": reason},
                    headers=self._auth_headers(),
                )
                if resp.status_code >= 400:
                    logger.warning("Signal update failed: %s %s", resp.status_code, resp.text)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not update signal status: %s", exc)

--- END FILE: trading-dashboard\backend\agents\trade_execution_agent.py ---

--- START FILE: trading-dashboard\backend\agents\__init__.py ---
"""Agent package for execution, sentiment, and workflow helpers."""


--- END FILE: trading-dashboard\backend\agents\__init__.py ---

--- START FILE: trading-dashboard\backend\brokerage\charges_engine.py ---
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict


class TradeSegment(str, Enum):
    intraday = "intraday"
    delivery = "delivery"


@dataclass(slots=True)
class ChargesEngine:
    """
    Upstox-style pre-trade charges estimate with a profitability filter.

    Notes:
    - Rates vary by broker and can change; keep these values configurable if needed.
    - This engine is used for "reject unprofitable trades" logic (profit >= ratio * charges).
    """

    min_profitability_ratio: float = 3.0

    # Defaults (documented as "as of 2024" in the user spec).
    GST_PERCENT: float = 0.18
    API_ORDER_CHARGE: float = 10.0  # per order

    INTRADAY_BROKERAGE_PERCENT: float = 0.0005  # 0.05%
    INTRADAY_MAX_BROKERAGE: float = 20.0
    INTRADAY_STT_PERCENT: float = 0.00025  # on sell
    INTRADAY_STAMP_DUTY_PERCENT: float = 0.00003  # on buy

    DELIVERY_BROKERAGE: float = 20.0  # flat
    DELIVERY_DP_CHARGE: float = 20.0  # per scrip
    DELIVERY_STT_PERCENT: float = 0.001  # on sell
    DELIVERY_STAMP_DUTY_PERCENT: float = 0.00015  # on buy

    SEBI_PERCENT: float = 0.000001
    EXCHANGE_TRANSACTION_PERCENT: float = 0.0000322

    def calculate_charges(
        self,
        segment: TradeSegment,
        buy_price: float,
        sell_price: float,
        quantity: int,
        using_api: bool = True,
    ) -> Dict[str, Any]:
        gross_profit = (sell_price - buy_price) * quantity

        buy_value = buy_price * quantity
        sell_value = sell_price * quantity
        turnover = buy_value + sell_value

        if segment == TradeSegment.intraday:
            brokerage = min(turnover * self.INTRADAY_BROKERAGE_PERCENT, self.INTRADAY_MAX_BROKERAGE)
        else:
            brokerage = self.DELIVERY_BROKERAGE

        api_charge = (self.API_ORDER_CHARGE * 2) if using_api else 0.0  # buy + sell

        if segment == TradeSegment.intraday:
            stt = sell_value * self.INTRADAY_STT_PERCENT
            stamp_duty = buy_value * self.INTRADAY_STAMP_DUTY_PERCENT
        else:
            stt = sell_value * self.DELIVERY_STT_PERCENT
            stamp_duty = buy_value * self.DELIVERY_STAMP_DUTY_PERCENT

        exchange_charges = turnover * self.EXCHANGE_TRANSACTION_PERCENT
        sebi_charges = turnover * self.SEBI_PERCENT

        gst_base = brokerage + exchange_charges + api_charge
        gst = gst_base * self.GST_PERCENT

        dp_charge = self.DELIVERY_DP_CHARGE if segment == TradeSegment.delivery else 0.0

        total_charges = (
            brokerage
            + api_charge
            + stt
            + stamp_duty
            + exchange_charges
            + sebi_charges
            + gst
            + dp_charge
        )

        net_profit = gross_profit - total_charges
        breakeven_move = (total_charges / quantity) if quantity else 0.0
        profitability_ratio = (gross_profit / total_charges) if total_charges > 0 else float("inf")
        should_execute = profitability_ratio >= self.min_profitability_ratio

        return {
            "gross_profit": round(gross_profit, 2),
            "total_charges": round(total_charges, 2),
            "net_profit": round(net_profit, 2),
            "breakeven_move": round(breakeven_move, 4),
            "profitability_ratio": round(profitability_ratio, 2) if profitability_ratio != float("inf") else float("inf"),
            "should_execute": bool(should_execute),
            "breakdown": {
                "brokerage": round(brokerage, 2),
                "api_charge": round(api_charge, 2),
                "stt": round(stt, 2),
                "stamp_duty": round(stamp_duty, 2),
                "exchange_charges": round(exchange_charges, 2),
                "sebi_charges": round(sebi_charges, 2),
                "gst": round(gst, 2),
                "dp_charge": round(dp_charge, 2),
            },
        }


--- END FILE: trading-dashboard\backend\brokerage\charges_engine.py ---

--- START FILE: trading-dashboard\backend\brokerage\__init__.py ---

--- END FILE: trading-dashboard\backend\brokerage\__init__.py ---

--- START FILE: trading-dashboard\backend\brokers\paper_broker.py ---
"""Paper broker adapters used to simulate order placement in local paper-mode tests."""
from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


def _normalize_symbol(symbol: str) -> str:
    return str(symbol or "").upper().replace(".NS", "").replace(".BO", "").strip()


@dataclass(slots=True)
class PaperBroker:
    """Very small in-memory broker that fills orders immediately."""

    broker_name: str = "upstox"
    starting_cash: float = 1_000_000.0
    _cash: float = field(init=False, repr=False)
    _orders: dict[str, dict[str, Any]] = field(init=False, repr=False)
    _positions: dict[str, dict[str, Any]] = field(init=False, repr=False)
    _lock: asyncio.Lock = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._cash = float(self.starting_cash)
        self._orders = {}
        self._positions = {}
        self._lock = asyncio.Lock()

    def snapshot(self) -> dict[str, Any]:
        """Return a compact broker snapshot for status endpoints."""
        positions_value = 0.0
        for pos in self._positions.values():
            qty = int(pos.get("quantity") or 0)
            last_price = float(pos.get("last_price") or pos.get("avg_price") or 0.0)
            positions_value += abs(qty) * last_price
        return {
            "broker_name": self.broker_name,
            "cash_balance": round(self._cash, 2),
            "positions_value": round(positions_value, 2),
            "equity": round(self._cash + positions_value, 2),
            "positions": list(self._positions.values()),
            "orders": len(self._orders),
        }

    async def close(self) -> None:
        """Paper broker does not hold network resources."""
        return

    async def place_order(
        self,
        symbol: str,
        side: str,
        quantity: int,
        client_order_id: Optional[str] = None,
        order_type: str = "MARKET",
        price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        product: str = "I",
        validity: str = "DAY",
        exchange: str = "NSE",
        segment: str = "EQ",
        broker_name: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create an order and mark it complete immediately."""
        try:
            sym = _normalize_symbol(symbol)
            qty = max(1, int(quantity))
            fill_price = float(
                price
                if price is not None and float(price) > 0
                else kwargs.get("execution_price")
                or kwargs.get("signal_price")
                or kwargs.get("entry_price")
                or kwargs.get("last_price")
                or 0.0
            )
            if fill_price <= 0:
                fill_price = 100.0

            order_id = str(client_order_id or f"paper-{uuid.uuid4().hex}")
            direction = "BUY" if str(side).lower().strip() == "buy" else "SELL"

            async with self._lock:
                position = self._positions.get(
                    sym,
                    {
                        "symbol": sym,
                        "quantity": 0,
                        "avg_price": 0.0,
                        "last_price": fill_price,
                        "side": "flat",
                        "broker": self.broker_name,
                    },
                )

                current_qty = int(position.get("quantity") or 0)
                avg_price = float(position.get("avg_price") or fill_price)
                if direction == "BUY":
                    new_qty = current_qty + qty
                    if current_qty >= 0:
                        avg_price = ((current_qty * avg_price) + (qty * fill_price)) / new_qty if new_qty else fill_price
                    else:
                        avg_price = fill_price if new_qty > 0 else avg_price
                    self._cash -= fill_price * qty
                else:
                    new_qty = current_qty - qty
                    if current_qty <= 0:
                        avg_price = ((abs(current_qty) * avg_price) + (qty * fill_price)) / abs(new_qty) if new_qty else fill_price
                    else:
                        avg_price = fill_price if new_qty < 0 else avg_price
                    self._cash += fill_price * qty

                position.update(
                    {
                        "quantity": int(new_qty),
                        "avg_price": round(float(avg_price), 4),
                        "last_price": round(fill_price, 4),
                        "side": "long" if new_qty > 0 else "short" if new_qty < 0 else "flat",
                        "updated_at": int(time.time()),
                    }
                )
                self._positions[sym] = position

                order = {
                    "order_id": order_id,
                    "client_order_id": client_order_id or order_id,
                    "symbol": sym,
                    "side": str(side).lower().strip(),
                    "quantity": qty,
                    "order_type": order_type,
                    "price": fill_price,
                    "average_price": fill_price,
                    "filled_quantity": qty,
                    "status": "complete",
                    "broker": broker_name or self.broker_name,
                    "product": product,
                    "validity": validity,
                    "exchange": exchange,
                    "segment": segment,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                }
                self._orders[order_id] = order

            return {"order_id": order_id, "status": "complete", "data": order}
        except Exception as exc:  # noqa: BLE001
            logger.error("Paper order placement failed: %s", exc)
            raise

    async def get_order_status(self, order_id: str) -> dict[str, Any]:
        """Return the stored paper order status."""
        try:
            async with self._lock:
                order = self._orders.get(str(order_id))
                if not order:
                    return {"status": "not_found", "order_id": order_id}
                return dict(order)
        except Exception as exc:  # noqa: BLE001
            logger.error("Paper order status failed: %s", exc)
            raise

    async def get_profile(self) -> dict[str, Any]:
        """Return a lightweight paper profile."""
        try:
            async with self._lock:
                snapshot = self.snapshot()
            return {
                "status": "ok",
                "client_name": "paper-trader",
                "broker": self.broker_name,
                "cash_balance": snapshot["cash_balance"],
                "equity": snapshot["equity"],
                "positions_count": len(snapshot["positions"]),
            }
        except Exception as exc:  # noqa: BLE001
            logger.error("Paper profile failed: %s", exc)
            raise

    async def get_funds_and_margin(self) -> dict[str, Any]:
        """Return mock margin data for dashboard UI calls."""
        try:
            async with self._lock:
                cash = round(self._cash, 2)
                snapshot = self.snapshot()
            return {
                "status": "ok",
                "available_cash": cash,
                "available_margin": cash,
                "used_margin": 0.0,
                "equity": snapshot["equity"],
            }
        except Exception as exc:  # noqa: BLE001
            logger.error("Paper funds failed: %s", exc)
            raise

    async def get_positions(self) -> list[dict[str, Any]]:
        """Return the simulated broker positions."""
        try:
            async with self._lock:
                return [dict(pos) for pos in self._positions.values()]
        except Exception as exc:  # noqa: BLE001
            logger.error("Paper positions failed: %s", exc)
            raise


@dataclass(slots=True)
class PaperBrokerRouter:
    """Routes orders to one or more paper broker instances."""

    brokers: dict[str, PaperBroker]
    default_broker_name: str = "upstox"

    def __post_init__(self) -> None:
        if self.default_broker_name not in self.brokers and self.brokers:
            self.default_broker_name = next(iter(self.brokers))

    def _resolve(self, broker_name: str | None = None) -> PaperBroker:
        name = str(broker_name or self.default_broker_name).lower().strip()
        broker = self.brokers.get(name)
        if broker is None:
            broker = next(iter(self.brokers.values()))
        return broker

    async def place_order(self, broker_name: str = "upstox", **kwargs: Any) -> dict[str, Any]:
        """Place an order on the selected paper broker."""
        return await self._resolve(broker_name).place_order(broker_name=broker_name, **kwargs)

    async def get_profile(self, broker_name: str = "upstox") -> dict[str, Any]:
        return await self._resolve(broker_name).get_profile()

    async def get_funds_and_margin(self, broker_name: str = "upstox") -> dict[str, Any]:
        return await self._resolve(broker_name).get_funds_and_margin()

    async def get_positions(self, broker_name: str = "upstox") -> list[dict[str, Any]]:
        return await self._resolve(broker_name).get_positions()

    def snapshot(self, broker_name: str = "upstox") -> dict[str, Any]:
        return self._resolve(broker_name).snapshot()


--- END FILE: trading-dashboard\backend\brokers\paper_broker.py ---

--- START FILE: trading-dashboard\backend\brokers\upstox_broker.py ---
from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import httpx

try:
    # When executed as a module (repo root in sys.path)
    from backend.market_data.symbol_master_service import SymbolMasterService, build_symbol_master  # type: ignore
    from backend.execution.auth.broker_auth_manager import BrokerAuthManager  # type: ignore
except ModuleNotFoundError:  # noqa: BLE001
    # When executed from within backend/
    from market_data.symbol_master_service import SymbolMasterService, build_symbol_master  # type: ignore
    from execution.auth.broker_auth_manager import BrokerAuthManager  # type: ignore


class UpstoxError(RuntimeError):
    pass


@dataclass(slots=True)
class UpstoxBroker:
    """
    Async-first Upstox REST client.

    IMPORTANT:
    - This module is safe to deploy to Render, but you should only ENABLE live broker calls
      if you set secrets as Render environment variables.
    - OAuth refresh is supported when UPSTOX_API_KEY/UPSTOX_API_SECRET are configured and you
      have authenticated via /broker-login → /broker-callback.
    """

    # Backward-compatible token mode (env token). If empty, BrokerAuthManager is used.
    access_token: str = ""
    base_url: str = "https://api.upstox.com/v2"
    timeout_sec: float = 30.0
    connect_timeout_sec: float = 10.0
    max_retries: int = 3
    symbol_master: Optional[SymbolMasterService] = None
    # With slots=True, we must declare attributes we set in __post_init__.
    client: httpx.AsyncClient = field(init=False, repr=False)
    auth: BrokerAuthManager = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout_sec, connect=self.connect_timeout_sec),
            limits=httpx.Limits(max_connections=50, max_keepalive_connections=10),
            http2=True,
        )
        if self.symbol_master is None:
            self.symbol_master = build_symbol_master()
        self.auth = BrokerAuthManager("upstox")

    async def close(self) -> None:
        await self.client.aclose()

    async def _headers(self) -> Dict[str, str]:
        token = self.access_token.strip()
        if not token:
            token = await self.auth.get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def _request(self, method: str, path: str, **kwargs: Any) -> Dict[str, Any]:
        url = self.base_url.rstrip("/") + "/" + path.lstrip("/")
        last_exc: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                r = await self.client.request(method, url, headers=await self._headers(), **kwargs)
                if r.status_code == 401:
                    # If we are in OAuth mode, refresh and retry.
                    if not self.access_token.strip():
                        ok = await self.auth.refresh()
                        if ok:
                            continue
                    raise UpstoxError(
                        "Upstox unauthorized (401). Re-authenticate via /broker-login (or update UPSTOX_ACCESS_TOKEN)."
                    )
                r.raise_for_status()
                return r.json()
            except (httpx.HTTPError, UpstoxError) as exc:
                last_exc = exc
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2**attempt)
                    continue
                break
        raise UpstoxError(f"Upstox request failed: {last_exc}")

    async def get_profile(self) -> Dict[str, Any]:
        return await self._request("GET", "/user/profile")

    async def get_funds_and_margin(self) -> Dict[str, Any]:
        # Upstox docs: /user/get-funds-and-margin
        return await self._request("GET", "/user/get-funds-and-margin")

    async def place_order(
        self,
        symbol: str,
        side: str,
        quantity: int,
        client_order_id: Optional[str] = None,
        order_type: str = "MARKET",
        price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        product: str = "D",
        validity: str = "DAY",
        exchange: str = "NSE",
        segment: str = "EQ",
    ) -> Dict[str, Any]:
        """
        Places an order using instrument_token resolved from the symbol master cache.
        """
        if not self.symbol_master:
            raise UpstoxError("symbol_master not available")
        instrument_key = self.symbol_master.get_instrument_key(symbol, exchange=exchange, segment=segment)
        if not instrument_key:
            raise UpstoxError(f"Unknown symbol in symbol master: {symbol} ({exchange}/{segment}). Refresh master file.")

        transaction_type = "BUY" if side.lower() == "buy" else "SELL"
        payload: Dict[str, Any] = {
            "quantity": int(quantity),
            "product": product,  # D=Delivery, I=Intraday, etc (Upstox)
            "validity": validity,
            "price": price if price is not None else 0,
            "tag": (client_order_id or os.getenv("UPSTOX_ORDER_TAG", "trading-dashboard")),
            "instrument_token": instrument_key,
            "order_type": order_type,
            "transaction_type": transaction_type,
            "disclosed_quantity": 0,
            "trigger_price": stop_loss if stop_loss is not None else 0,
        }
        # take_profit is not a standard Upstox field; it's tracked by our risk/strategy layers.
        return await self._request("POST", "/order/place", json=payload)

    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        return await self._request("GET", f"/order/details?order_id={order_id}")


def broker_from_env(symbol_master: Optional[SymbolMasterService] = None) -> Optional[UpstoxBroker]:
    token = os.getenv("UPSTOX_ACCESS_TOKEN", "").strip()
    if token:
        return UpstoxBroker(access_token=token, symbol_master=symbol_master)
    # OAuth mode: only create broker if required OAuth env vars exist.
    if os.getenv("UPSTOX_API_KEY", "").strip() and os.getenv("UPSTOX_API_SECRET", "").strip():
        return UpstoxBroker(access_token="", symbol_master=symbol_master)
    return None

--- END FILE: trading-dashboard\backend\brokers\upstox_broker.py ---

--- START FILE: trading-dashboard\backend\brokers\__init__.py ---

--- END FILE: trading-dashboard\backend\brokers\__init__.py ---

--- START FILE: trading-dashboard\backend\config\trading_config.py ---
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class TradingFlags:
    """
    Kill switch + safety flags.

    IMPORTANT:
    - Render deployments are stateless across restarts; persist kill switch state in DB if needed.
    - This module provides a process-level default + env override.
    """

    trading_enabled: bool = os.getenv("TRADING_ENABLED", "true").strip().lower() in {"1", "true", "yes", "on"}


FLAGS = TradingFlags()


def is_trading_enabled() -> bool:
    return bool(FLAGS.trading_enabled)


def enable_trading() -> None:
    FLAGS.trading_enabled = True


def disable_trading() -> None:
    FLAGS.trading_enabled = False


--- END FILE: trading-dashboard\backend\config\trading_config.py ---

--- START FILE: trading-dashboard\backend\config\__init__.py ---

--- END FILE: trading-dashboard\backend\config\__init__.py ---

--- START FILE: trading-dashboard\backend\core\event_bus.py ---
"""Async in-process event bus for market, signal, and execution events."""
from __future__ import annotations

import asyncio
import inspect
import logging
from collections import defaultdict
from typing import Any, Awaitable, Callable, DefaultDict, Optional

try:
    from backend.core.event_store import EventStore  # type: ignore
except ModuleNotFoundError:  # noqa: BLE001
    from core.event_store import EventStore  # type: ignore

logger = logging.getLogger(__name__)

EventCallback = Callable[[Any], Awaitable[None] | None]


class AsyncEventBus:
    """Minimal async pub/sub bus with optional persistence to the event store."""

    def __init__(self, event_store: Optional[EventStore] = None):
        self._event_store = event_store
        self._subscribers: DefaultDict[str, list[EventCallback]] = defaultdict(list)

    def subscribe(self, event_name: str, callback: EventCallback) -> None:
        """Register a callback for an event name."""
        name = str(event_name).strip()
        if not name or callback in self._subscribers[name]:
            return
        self._subscribers[name].append(callback)

    def unsubscribe(self, event_name: str, callback: EventCallback) -> None:
        """Remove a callback from an event name."""
        name = str(event_name).strip()
        if not name:
            return
        callbacks = self._subscribers.get(name)
        if not callbacks:
            return
        self._subscribers[name] = [cb for cb in callbacks if cb != callback]
        if not self._subscribers[name]:
            self._subscribers.pop(name, None)

    async def publish(self, event_name: str, payload: Any, source: str = "event_bus") -> None:
        """Publish an event to all subscribers and optionally persist it."""
        try:
            name = str(event_name).strip()
            if not name:
                return

            if self._event_store is not None:
                try:
                    self._event_store.store_event(name, payload if isinstance(payload, dict) else {"value": payload}, source=source)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed to persist event %s: %s", name, exc)

            callbacks = list(self._subscribers.get(name, []))
            if not callbacks:
                return

            awaitables: list[Awaitable[None]] = []
            for callback in callbacks:
                try:
                    result = callback(payload)
                    if inspect.isawaitable(result):
                        awaitables.append(result)
                except Exception as exc:  # noqa: BLE001
                    logger.error("Event callback error for %s: %s", name, exc)

            if awaitables:
                results = await asyncio.gather(*awaitables, return_exceptions=True)
                for result in results:
                    if isinstance(result, Exception):
                        logger.error("Event callback raised: %s", result)
        except Exception as exc:  # noqa: BLE001
            logger.error("publish(%s) failed: %s", event_name, exc)


def build_event_bus(event_store: Optional[EventStore] = None) -> AsyncEventBus:
    """Create an event bus instance."""
    return AsyncEventBus(event_store=event_store)

--- END FILE: trading-dashboard\backend\core\event_bus.py ---

--- START FILE: trading-dashboard\backend\core\event_store.py ---
from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(64), unique=True, index=True)
    event_type = Column(String(100), index=True)
    payload = Column(Text)
    timestamp = Column(DateTime, index=True)
    source = Column(String(100))


@dataclass(slots=True)
class EventStore:
    """
    Persistent event store (SQLite/Postgres depending on EVENT_DB_URL).

    Default uses the same DATABASE_URL as the dashboard so everything is in one place.
    """

    db_url: str
    # With slots=True, we must declare any attributes we set in __post_init__.
    engine: Any = field(init=False, repr=False)
    Session: Any = field(init=False, repr=False)

    def __post_init__(self) -> None:
        connect_args: Dict[str, Any] = {}
        if self.db_url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}
        self.engine = create_engine(self.db_url, connect_args=connect_args, pool_pre_ping=True)
        self.Session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(self.engine)

    def store_event(self, event_type: str, payload: Dict[str, Any], source: str = "system") -> str:
        event_id = uuid.uuid4().hex
        session = self.Session()
        try:
            ev = Event(
                event_id=event_id,
                event_type=event_type,
                payload=json.dumps(payload),
                timestamp=datetime.utcnow(),
                source=source,
            )
            session.add(ev)
            session.commit()
            return event_id
        finally:
            session.close()

    def get_events(
        self,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        session = self.Session()
        try:
            q = session.query(Event)
            if event_type:
                q = q.filter(Event.event_type == event_type)
            rows = q.order_by(Event.timestamp.desc()).limit(limit).all()
            return [
                {
                    "event_id": r.event_id,
                    "event_type": r.event_type,
                    "payload": json.loads(r.payload or "{}"),
                    "timestamp": r.timestamp.isoformat() if r.timestamp else None,
                    "source": r.source,
                }
                for r in rows
            ]
        finally:
            session.close()


def build_event_store(default_db_url: str) -> EventStore:
    db_url = os.getenv("EVENT_DB_URL", "").strip() or default_db_url
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    return EventStore(db_url=db_url)

--- END FILE: trading-dashboard\backend\core\event_store.py ---

--- START FILE: trading-dashboard\backend\core\__init__.py ---

--- END FILE: trading-dashboard\backend\core\__init__.py ---

--- START FILE: trading-dashboard\backend\execution\order_deduplication.py ---
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional


@dataclass(slots=True)
class OrderFingerprint:
    symbol: str
    side: str
    quantity: int


class OrderDeduplicationService:
    """
    Idempotency helper (in-memory).

    For full multi-instance idempotency, persist client_order_id to DB.
    On Render free plan you typically run a single instance, but restarts will clear memory.
    """

    def __init__(self) -> None:
        self.pending_orders: Dict[str, Dict[str, Any]] = {}
        self.completed_orders: Dict[str, Dict[str, Any]] = {}

    def generate_client_order_id(self, symbol: str, side: str, quantity: int) -> str:
        fp = f"{symbol}_{side}_{quantity}_{int(datetime.now().timestamp() * 1000)}"
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, fp))

    def is_duplicate(self, client_order_id: str) -> bool:
        return client_order_id in self.pending_orders or client_order_id in self.completed_orders

    def register_order(self, client_order_id: str, symbol: str, side: str, quantity: int) -> None:
        self.pending_orders[client_order_id] = {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "timestamp": datetime.now(),
        }

    def mark_completed(self, client_order_id: str, broker_order_id: str) -> None:
        if client_order_id in self.pending_orders:
            order = self.pending_orders.pop(client_order_id)
            order["broker_order_id"] = broker_order_id
            order["completed_at"] = datetime.now()
            self.completed_orders[client_order_id] = order

    def cleanup_old_orders(self, hours: int = 24) -> None:
        cutoff = datetime.now() - timedelta(hours=hours)
        self.completed_orders = {
            k: v
            for k, v in self.completed_orders.items()
            if v.get("completed_at", datetime.now()) > cutoff
        }


--- END FILE: trading-dashboard\backend\execution\order_deduplication.py ---

--- START FILE: trading-dashboard\backend\execution\__init__.py ---

--- END FILE: trading-dashboard\backend\execution\__init__.py ---

--- START FILE: trading-dashboard\backend\execution\auth\broker_auth_manager.py ---
from __future__ import annotations

import os

import httpx

from .token_store import TokenStore

UPSTOX_API_KEY = os.getenv("UPSTOX_API_KEY", "")
UPSTOX_API_SECRET = os.getenv("UPSTOX_API_SECRET", "")
UPSTOX_REDIRECT = os.getenv("UPSTOX_REDIRECT_URI", "http://localhost:8000/broker-callback")
UPSTOX_TOKEN_URL = "https://api.upstox.com/v2/login/authorization/token"


class BrokerAuthManager:
    """
    Upstox OAuth helper.

    This manager:
    - Builds the login URL for authorization_code grant
    - Exchanges `code` for access/refresh tokens
    - Refreshes tokens when expired or after 401
    - Stores tokens encrypted at rest
    """

    def __init__(self, broker: str = "upstox"):
        self.broker = (broker or "upstox").strip().lower()
        self._store = TokenStore()

    def get_login_url(self) -> str:
        if not UPSTOX_API_KEY:
            return "https://api.upstox.com/v2/login/authorization/dialog"
        return (
            "https://api.upstox.com/v2/login/authorization/dialog"
            f"?response_type=code"
            f"&client_id={UPSTOX_API_KEY}"
            f"&redirect_uri={UPSTOX_REDIRECT}"
        )

    async def exchange_code(self, code: str) -> bool:
        if not UPSTOX_API_KEY or not UPSTOX_API_SECRET:
            raise RuntimeError("UPSTOX_API_KEY/UPSTOX_API_SECRET not configured")
        code = (code or "").strip()
        if not code:
            return False

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                UPSTOX_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": UPSTOX_API_KEY,
                    "client_secret": UPSTOX_API_SECRET,
                    "redirect_uri": UPSTOX_REDIRECT,
                    "grant_type": "authorization_code",
                },
                headers={"Accept": "application/json"},
            )
            resp.raise_for_status()
            data = resp.json()

        access = data.get("access_token", "") or ""
        refresh = data.get("refresh_token", "") or ""
        exp = int(data.get("expires_in", 86400) or 86400)
        if not access:
            return False

        self._store.save(self.broker, access, refresh, exp)
        return True

    async def refresh(self) -> bool:
        if not UPSTOX_API_KEY or not UPSTOX_API_SECRET:
            raise RuntimeError("UPSTOX_API_KEY/UPSTOX_API_SECRET not configured")

        row = self._store.get(self.broker)
        if not row or not row.get("refresh_token"):
            return False

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                UPSTOX_TOKEN_URL,
                data={
                    "refresh_token": row["refresh_token"],
                    "client_id": UPSTOX_API_KEY,
                    "client_secret": UPSTOX_API_SECRET,
                    "grant_type": "refresh_token",
                },
                headers={"Accept": "application/json"},
            )
            if resp.status_code != 200:
                return False
            data = resp.json()

        access = data.get("access_token", "") or ""
        refresh = data.get("refresh_token", row["refresh_token"]) or row["refresh_token"]
        exp = int(data.get("expires_in", 86400) or 86400)
        if not access:
            return False

        self._store.save(self.broker, access, refresh, exp)
        return True

    async def get_access_token(self) -> str:
        if self._store.is_expired(self.broker):
            ok = await self.refresh()
            if not ok:
                raise RuntimeError(
                    "Upstox token expired and refresh failed. Visit /broker-login to re-authenticate."
                )
        row = self._store.get(self.broker)
        if not row or not row.get("access_token"):
            raise RuntimeError("Upstox not authenticated. Visit /broker-login.")
        return str(row["access_token"])

    def is_authenticated(self) -> bool:
        row = self._store.get(self.broker)
        return bool(row and row.get("access_token"))


--- END FILE: trading-dashboard\backend\execution\auth\broker_auth_manager.py ---

--- START FILE: trading-dashboard\backend\execution\auth\token_store.py ---
from __future__ import annotations

import os
import sqlite3
import time
from pathlib import Path

from cryptography.fernet import Fernet

DB_PATH = Path(os.getenv("BROKER_TOKEN_DB_PATH", "data/broker_tokens.db"))
KEY_PATH = Path(os.getenv("BROKER_TOKEN_KEY_PATH", "data/.token_key"))


class TokenStore:
    """
    Encrypted token store using Fernet.

    Notes:
    - This encrypts tokens at rest. The encryption key is stored on disk (KEY_PATH).
      For production, prefer storing KEY_PATH on a persistent disk and protect it
      with OS permissions / secret management.
    - SQLite is used for simplicity. If you run multiple workers, use a real DB.
    """

    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        KEY_PATH.parent.mkdir(parents=True, exist_ok=True)

        if KEY_PATH.exists():
            self._key = KEY_PATH.read_bytes()
        else:
            self._key = Fernet.generate_key()
            KEY_PATH.write_bytes(self._key)
            try:
                os.chmod(KEY_PATH, 0o600)
            except Exception:
                pass

        self._cipher = Fernet(self._key)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(str(DB_PATH))

    def _init_db(self):
        con = self._connect()
        try:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS broker_tokens (
                    broker      TEXT PRIMARY KEY,
                    access_enc  TEXT NOT NULL,
                    refresh_enc TEXT NOT NULL,
                    expires_at  INTEGER NOT NULL,
                    updated_at  INTEGER NOT NULL
                )
                """
            )
            con.commit()
        finally:
            con.close()

    def save(self, broker: str, access_token: str, refresh_token: str, expires_in: int = 86400):
        broker = (broker or "").strip().lower()
        if not broker:
            raise ValueError("broker is required")
        if not access_token:
            raise ValueError("access_token is required")

        enc_a = self._cipher.encrypt(access_token.encode("utf-8")).decode("utf-8")
        enc_r = self._cipher.encrypt((refresh_token or "").encode("utf-8")).decode("utf-8")
        now = int(time.time())

        con = self._connect()
        try:
            con.execute(
                """
                INSERT INTO broker_tokens (broker, access_enc, refresh_enc, expires_at, updated_at)
                VALUES (?,?,?,?,?)
                ON CONFLICT(broker) DO UPDATE SET
                    access_enc=excluded.access_enc,
                    refresh_enc=excluded.refresh_enc,
                    expires_at=excluded.expires_at,
                    updated_at=excluded.updated_at
                """,
                (broker, enc_a, enc_r, now + int(expires_in or 0), now),
            )
            con.commit()
        finally:
            con.close()

    def get(self, broker: str) -> dict | None:
        broker = (broker or "").strip().lower()
        if not broker:
            return None

        con = self._connect()
        try:
            row = con.execute(
                "SELECT access_enc, refresh_enc, expires_at FROM broker_tokens WHERE broker=?",
                (broker,),
            ).fetchone()
        finally:
            con.close()

        if not row:
            return None

        return {
            "access_token": self._cipher.decrypt(row[0].encode("utf-8")).decode("utf-8"),
            "refresh_token": self._cipher.decrypt(row[1].encode("utf-8")).decode("utf-8"),
            "expires_at": int(row[2]),
        }

    def is_expired(self, broker: str, buffer_sec: int = 300) -> bool:
        row = self.get(broker)
        if not row:
            return True
        return int(time.time()) >= int(row["expires_at"]) - int(buffer_sec or 0)

    def delete(self, broker: str):
        broker = (broker or "").strip().lower()
        if not broker:
            return
        con = self._connect()
        try:
            con.execute("DELETE FROM broker_tokens WHERE broker=?", (broker,))
            con.commit()
        finally:
            con.close()


--- END FILE: trading-dashboard\backend\execution\auth\token_store.py ---

--- START FILE: trading-dashboard\backend\execution\auth\__init__.py ---
"""
Broker authentication helpers.

Currently supports Upstox OAuth token exchange + refresh with encrypted-at-rest
token storage.
"""


--- END FILE: trading-dashboard\backend\execution\auth\__init__.py ---

--- START FILE: trading-dashboard\backend\market_data\market_data_engine.py ---
"""Central market-data hub that caches prices and republishes ticks to the event bus."""
from __future__ import annotations

import logging
from typing import Optional

try:
    from backend.execution.auth.broker_auth_manager import BrokerAuthManager  # type: ignore
    from backend.market_data.upstox_websocket import UpstoxWebSocket  # type: ignore
except ModuleNotFoundError:  # noqa: BLE001
    from execution.auth.broker_auth_manager import BrokerAuthManager  # type: ignore
    from market_data.upstox_websocket import UpstoxWebSocket  # type: ignore

logger = logging.getLogger(__name__)


class MarketDataEngine:
    """Keeps an in-memory quote cache and emits market.tick events."""

    def __init__(self, event_bus, auth_manager: Optional[BrokerAuthManager] = None):
        self._bus = event_bus
        self._auth = auth_manager or BrokerAuthManager("upstox")
        self._ws = UpstoxWebSocket(self._auth)
        self._cache: dict[str, dict] = {}
        self._ws.on_tick(self._on_ticks)

    async def start(self) -> None:
        """Start the WebSocket connection."""
        try:
            logger.info("MarketDataEngine starting")
            await self._ws.connect()
        except Exception as exc:  # noqa: BLE001
            logger.error("MarketDataEngine start failed: %s", exc)

    async def stop(self) -> None:
        """Stop the WebSocket connection."""
        try:
            await self._ws.close()
        except Exception as exc:  # noqa: BLE001
            logger.error("MarketDataEngine stop failed: %s", exc)

    async def subscribe(self, symbols: list[str], mode: str = "full") -> None:
        """Subscribe to a list of symbols."""
        try:
            await self._ws.subscribe(symbols, mode)
        except Exception as exc:  # noqa: BLE001
            logger.error("MarketDataEngine subscribe failed: %s", exc)

    def get_ltp(self, symbol: str) -> float:
        """Return the latest cached last-traded price."""
        return float(self._cache.get((symbol or "").upper(), {}).get("ltp", 0.0) or 0.0)

    def get_snapshot(self, symbol: str) -> dict:
        """Return the full cached tick snapshot."""
        return dict(self._cache.get((symbol or "").upper(), {}))

    async def _on_ticks(self, ticks: list[dict]) -> None:
        try:
            for tick in ticks:
                ikey = str(tick.get("instrument_key", ""))
                symbol = (ikey.split("|")[-1] if "|" in ikey else ikey).upper()
                if not symbol:
                    continue
                self._cache[symbol] = tick
                await self._bus.publish(
                    "market.tick",
                    {
                        "symbol": symbol,
                        "ltp": tick.get("ltp", 0.0),
                        "open": tick.get("open", 0.0),
                        "high": tick.get("high", 0.0),
                        "low": tick.get("low", 0.0),
                        "close": tick.get("close", 0.0),
                        "volume": tick.get("volume", 0),
                        "timestamp": tick.get("ts"),
                    },
                )
        except Exception as exc:  # noqa: BLE001
            logger.error("Tick fan-out failed: %s", exc)


--- END FILE: trading-dashboard\backend\market_data\market_data_engine.py ---

--- START FILE: trading-dashboard\backend\market_data\reconnect_manager.py ---
"""WebSocket reconnect helper with backoff, heartbeat checks, and resubscribe support."""
from __future__ import annotations

import asyncio
import json
import logging
import time
from enum import Enum
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"


class ReconnectManager:
    MAX_DELAY = 60
    MAX_RETRIES = 20

    def __init__(
        self,
        ws_url: str,
        get_headers: Callable[[], Awaitable[dict[str, str]]],
        on_message: Callable[[Any], Awaitable[None]],
        heartbeat_interval: int = 30,
    ) -> None:
        self.ws_url = ws_url
        self.get_headers = get_headers
        self.on_message = on_message
        self.heartbeat_interval = heartbeat_interval
        self.state = ConnectionState.DISCONNECTED
        self._ws: Any = None
        self._retries = 0
        self._last_msg_at = 0.0
        self._subscriptions: list[dict[str, Any]] = []
        self._running = False
        self._listen_task: asyncio.Task | None = None
        self._heartbeat_task: asyncio.Task | None = None

    async def connect(self) -> None:
        """Start the reconnect loop. Runs until close() is called."""
        try:
            self._running = True
            await self._loop()
        except Exception as exc:  # noqa: BLE001
            logger.error("ReconnectManager.connect failed: %s", exc)
            self.state = ConnectionState.FAILED

    async def send(self, message: dict[str, Any]) -> None:
        """Send a JSON message and keep it for future resubscribe."""
        try:
            if message not in self._subscriptions:
                self._subscriptions.append(message)
            if self._ws and self.state == ConnectionState.CONNECTED:
                await self._ws.send(json.dumps(message))
        except Exception as exc:  # noqa: BLE001
            logger.error("Send failed: %s", exc)

    async def close(self) -> None:
        """Stop reconnecting and close the active socket."""
        try:
            self._running = False
            self._cancel_tasks()
            if self._ws:
                try:
                    await self._ws.close()
                except Exception:  # noqa: BLE001
                    pass
            self.state = ConnectionState.DISCONNECTED
        except Exception as exc:  # noqa: BLE001
            logger.error("Close failed: %s", exc)

    async def _loop(self) -> None:
        try:
            import websockets
        except ImportError as exc:  # pragma: no cover - dependency issue
            raise RuntimeError("Run: pip install websockets>=12.0") from exc

        while self._running:
            self.state = ConnectionState.CONNECTING
            try:
                headers = await self.get_headers()
                self._ws = await websockets.connect(
                    self.ws_url,
                    extra_headers=headers,
                    ping_interval=20,
                    ping_timeout=10,
                    close_timeout=5,
                )
                self.state = ConnectionState.CONNECTED
                self._retries = 0
                self._last_msg_at = time.time()
                logger.info("WebSocket connected")

                await self._resubscribe()

                self._listen_task = asyncio.create_task(self._listen())
                self._heartbeat_task = asyncio.create_task(self._heartbeat())
                await self._listen_task
            except Exception as exc:  # noqa: BLE001
                logger.warning("WebSocket error: %s", exc)
            finally:
                self._cancel_tasks()
                self.state = ConnectionState.DISCONNECTED

            if not self._running:
                break

            self._retries += 1
            if self._retries > self.MAX_RETRIES:
                self.state = ConnectionState.FAILED
                logger.error("Max retries exceeded. Stopping.")
                return

            delay = min(2 ** (self._retries - 1), self.MAX_DELAY)
            self.state = ConnectionState.RECONNECTING
            logger.info("Reconnecting in %ds (attempt %d)", delay, self._retries)
            await asyncio.sleep(delay)

    async def _listen(self) -> None:
        try:
            async for raw in self._ws:
                self._last_msg_at = time.time()
                try:
                    await self.on_message(raw)
                except Exception as exc:  # noqa: BLE001
                    logger.error("on_message error: %s", exc)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            logger.warning("Listen ended: %s", exc)

    async def _heartbeat(self) -> None:
        try:
            while self._running and self.state == ConnectionState.CONNECTED:
                await asyncio.sleep(self.heartbeat_interval)
                stale = time.time() - self._last_msg_at
                if stale > self.heartbeat_interval * 2:
                    logger.warning("Stale WS (%.0fs). Forcing reconnect.", stale)
                    if self._listen_task and not self._listen_task.done():
                        self._listen_task.cancel()
                    if self._ws:
                        try:
                            await self._ws.close()
                        except Exception:  # noqa: BLE001
                            pass
                    return
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            logger.warning("Heartbeat ended: %s", exc)

    async def _resubscribe(self) -> None:
        try:
            for sub in self._subscriptions:
                try:
                    if self._ws:
                        await self._ws.send(json.dumps(sub))
                    await asyncio.sleep(0.05)
                except Exception as exc:  # noqa: BLE001
                    logger.error("Resubscribe error: %s", exc)
        except Exception as exc:  # noqa: BLE001
            logger.error("Resubscribe loop failed: %s", exc)

    def _cancel_tasks(self) -> None:
        for task in (self._listen_task, self._heartbeat_task):
            if task and not task.done():
                task.cancel()
        self._listen_task = None
        self._heartbeat_task = None


--- END FILE: trading-dashboard\backend\market_data\reconnect_manager.py ---

--- START FILE: trading-dashboard\backend\market_data\symbol_master_service.py ---
from __future__ import annotations

import gzip
import json
import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx


DEFAULT_MASTER_URL = "https://assets.upstox.com/market-quote/instruments/exchange/complete.json.gz"


def _ensure_dir(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)


@dataclass(slots=True)
class SymbolMasterService:
    """
    Lightweight, DB-backed Upstox instrument master cache.

    We intentionally use sqlite3 directly here to avoid:
    - bloating the main dashboard DB with millions of instrument rows
    - long migrations on Render
    """

    db_path: Path
    master_url: str = DEFAULT_MASTER_URL

    def __post_init__(self) -> None:
        _ensure_dir(self.db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(str(self.db_path))
        con.row_factory = sqlite3.Row
        return con

    def _init_db(self) -> None:
        con = self._connect()
        try:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS instrument_master (
                    instrument_key TEXT PRIMARY KEY,
                    trading_symbol TEXT,
                    name TEXT,
                    exchange TEXT,
                    segment TEXT,
                    instrument_type TEXT,
                    expiry TEXT,
                    strike REAL,
                    option_type TEXT,
                    lot_size INTEGER,
                    tick_size REAL,
                    isin TEXT
                )
                """
            )
            con.execute("CREATE INDEX IF NOT EXISTS ix_inst_symbol ON instrument_master(trading_symbol)")
            con.execute("CREATE INDEX IF NOT EXISTS ix_inst_name ON instrument_master(name)")
            con.execute("CREATE INDEX IF NOT EXISTS ix_inst_exchange_segment ON instrument_master(exchange, segment)")
            con.commit()
        finally:
            con.close()

    async def download_and_refresh(self) -> Dict[str, Any]:
        """
        Downloads the Upstox master file and refreshes the local sqlite cache.
        This can take time; call from a background task or admin endpoint.
        """
        timeout = float(os.getenv("SYMBOL_MASTER_TIMEOUT_SEC", "60"))
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(self.master_url)
            r.raise_for_status()
            raw = r.content

        try:
            decompressed = gzip.decompress(raw)
        except Exception:
            # In case Upstox returns plain JSON in some environments
            decompressed = raw

        instruments = json.loads(decompressed.decode("utf-8"))
        if not isinstance(instruments, list):
            raise ValueError("Instrument master response is not a list")

        con = self._connect()
        try:
            con.execute("DELETE FROM instrument_master")
            con.commit()

            rows = []
            for item in instruments:
                # Defensive parsing: Upstox keys vary by segment/type.
                rows.append(
                    (
                        str(item.get("instrument_key") or ""),
                        str(item.get("trading_symbol") or ""),
                        str(item.get("name") or ""),
                        str(item.get("exchange") or ""),
                        str(item.get("segment") or ""),
                        str(item.get("instrument_type") or ""),
                        item.get("expiry"),
                        item.get("strike"),
                        item.get("option_type"),
                        int(item.get("lot_size") or 1),
                        float(item.get("tick_size") or 0.05),
                        item.get("isin"),
                    )
                )

            con.executemany(
                """
                INSERT INTO instrument_master (
                    instrument_key, trading_symbol, name, exchange, segment, instrument_type,
                    expiry, strike, option_type, lot_size, tick_size, isin
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
            con.commit()
        finally:
            con.close()

        return {"ok": True, "count": len(instruments), "db_path": str(self.db_path)}

    def get_instrument_key(
        self,
        symbol: str,
        exchange: str = "NSE",
        segment: str = "EQ",
    ) -> Optional[str]:
        sym = (symbol or "").strip().upper()
        if not sym:
            return None
        con = self._connect()
        try:
            row = con.execute(
                """
                SELECT instrument_key
                FROM instrument_master
                WHERE trading_symbol = ? AND exchange = ? AND segment = ?
                LIMIT 1
                """,
                (sym, exchange, segment),
            ).fetchone()
            return str(row["instrument_key"]) if row else None
        finally:
            con.close()

    def search_symbols(self, query: str, exchange: str = "NSE", limit: int = 10) -> List[Dict[str, Any]]:
        q = (query or "").strip()
        if not q:
            return []
        like = f"%{q.upper()}%"
        con = self._connect()
        try:
            rows = con.execute(
                """
                SELECT trading_symbol, name, instrument_key, segment
                FROM instrument_master
                WHERE exchange = ?
                  AND (UPPER(trading_symbol) LIKE ? OR UPPER(name) LIKE ?)
                LIMIT ?
                """,
                (exchange, like, like, int(limit)),
            ).fetchall()
            return [
                {
                    "symbol": str(r["trading_symbol"]),
                    "name": str(r["name"]),
                    "instrument_key": str(r["instrument_key"]),
                    "segment": str(r["segment"]),
                }
                for r in rows
            ]
        finally:
            con.close()


def build_symbol_master() -> SymbolMasterService:
    # Default path works on Render (ephemeral FS). For persistence, mount a disk and point to it.
    db_path = Path(os.getenv("SYMBOL_MASTER_DB_PATH", "./data/upstox_instruments.db"))
    return SymbolMasterService(db_path=db_path)


--- END FILE: trading-dashboard\backend\market_data\symbol_master_service.py ---

--- START FILE: trading-dashboard\backend\market_data\upstox_websocket.py ---
"""Upstox market-data WebSocket wrapper with tick parsing and reconnect support."""
from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any, Awaitable, Callable

try:
    from backend.execution.auth.broker_auth_manager import BrokerAuthManager  # type: ignore
    from backend.market_data.reconnect_manager import ReconnectManager  # type: ignore
except ModuleNotFoundError:  # noqa: BLE001
    from execution.auth.broker_auth_manager import BrokerAuthManager  # type: ignore
    from market_data.reconnect_manager import ReconnectManager  # type: ignore

logger = logging.getLogger(__name__)
WS_URL = "wss://api.upstox.com/v2/feed/market-data-feed"


def _parse(raw: bytes | str) -> list[dict[str, Any]]:
    """Parse an Upstox tick frame into normalized tick dictionaries."""
    ticks: list[dict[str, Any]] = []
    try:
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="ignore")
        data = json.loads(raw)
        feeds = data.get("feeds", {})
        if not isinstance(feeds, dict):
            return []
        ts = data.get("currentTs", int(time.time() * 1000))
        for instrument_key, feed in feeds.items():
            if not isinstance(feed, dict):
                continue
            ff = feed.get("ff", {}) if isinstance(feed.get("ff", {}), dict) else {}
            mkt = ff.get("marketFF", {}) if isinstance(ff.get("marketFF", {}), dict) else {}
            ltpc = mkt.get("ltpc", {}) if isinstance(mkt.get("ltpc", {}), dict) else {}
            ohlc_obj = mkt.get("marketOHLC", {}) if isinstance(mkt.get("marketOHLC", {}), dict) else {}
            ohlc_list = ohlc_obj.get("ohlc", [{}]) if isinstance(ohlc_obj.get("ohlc", [{}]), list) else [{}]
            ohlc = ohlc_list[0] if ohlc_list else {}
            if not isinstance(ohlc, dict):
                ohlc = {}

            ticks.append(
                {
                    "instrument_key": instrument_key,
                    "ltp": ltpc.get("ltp", 0.0),
                    "close": ltpc.get("cp", 0.0),
                    "open": ohlc.get("open", 0.0),
                    "high": ohlc.get("high", 0.0),
                    "low": ohlc.get("low", 0.0),
                    "volume": ohlc.get("vol", 0),
                    "ts": ts,
                }
            )
    except Exception as exc:  # noqa: BLE001
        logger.debug("Parse error: %s", exc)
    return ticks


class UpstoxWebSocket:
    """Connects to Upstox feed, normalizes tick frames, and invokes callbacks."""

    def __init__(self, auth_manager: BrokerAuthManager):
        self._auth = auth_manager
        self._callbacks: list[Callable[[list[dict[str, Any]]], Awaitable[None]]] = []
        self._mgr = ReconnectManager(
            ws_url=WS_URL,
            get_headers=self._headers,
            on_message=self._on_raw,
            heartbeat_interval=30,
        )
        self._connect_task: asyncio.Task | None = None

    async def connect(self) -> None:
        """Start the reconnect loop in the background."""
        try:
            if self._connect_task and not self._connect_task.done():
                return
            self._connect_task = asyncio.create_task(self._mgr.connect())
        except Exception as exc:  # noqa: BLE001
            logger.error("WebSocket connect failed: %s", exc)

    async def subscribe(self, symbols: list[str], mode: str = "full") -> None:
        """Subscribe to one or more symbols."""
        try:
            if not symbols:
                return
            keys = [self._to_key(symbol) for symbol in symbols]
            await self._mgr.send(
                {
                    "guid": f"sub-{int(time.time())}",
                    "method": "sub",
                    "data": {"mode": mode, "instrumentKeys": keys},
                }
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Subscribe failed: %s", exc)

    def on_tick(self, callback: Callable[[list[dict[str, Any]]], Awaitable[None]]) -> None:
        """Register an async callback for parsed tick batches."""
        self._callbacks.append(callback)

    async def close(self) -> None:
        """Stop the reconnect loop and close the socket."""
        try:
            await self._mgr.close()
            if self._connect_task and not self._connect_task.done():
                self._connect_task.cancel()
        except Exception as exc:  # noqa: BLE001
            logger.error("WebSocket close failed: %s", exc)

    async def _headers(self) -> dict[str, str]:
        try:
            token = await self._auth.get_access_token()
            return {"Authorization": f"Bearer {token}", "Api-Version": "2.0"}
        except Exception as exc:  # noqa: BLE001
            logger.error("Header generation failed: %s", exc)
            raise

    async def _on_raw(self, raw: Any) -> None:
        try:
            ticks = _parse(raw)
            if not ticks:
                return
            for callback in self._callbacks:
                try:
                    result = callback(ticks)
                    if asyncio.iscoroutine(result):
                        await result
                except Exception as exc:  # noqa: BLE001
                    logger.error("Tick callback error: %s", exc)
        except Exception as exc:  # noqa: BLE001
            logger.error("Raw tick handling failed: %s", exc)

    @staticmethod
    def _to_key(symbol: str) -> str:
        s = (symbol or "").upper().replace(".NS", "").replace(".BO", "")
        return f"NSE_EQ|{s}"


--- END FILE: trading-dashboard\backend\market_data\upstox_websocket.py ---

--- START FILE: trading-dashboard\backend\market_data\__init__.py ---
"""Market data package for Upstox WebSocket feeds and instrument master lookups."""


--- END FILE: trading-dashboard\backend\market_data\__init__.py ---

--- START FILE: trading-dashboard\backend\notifications\telegram_bot.py ---
"""Telegram inline-button approvals for trade signals and callback polling."""
from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
BASE = f"https://api.telegram.org/bot{TOKEN}" if TOKEN else ""


def _normalize_dashboard_url(raw_url: str | None) -> str:
    """Prefer a loopback-safe dashboard URL for local paper-mode tests."""
    url = str(raw_url or "").strip().rstrip("/")
    if not url:
        return "http://127.0.0.1:8000"
    if url.startswith("http://localhost"):
        return url.replace("localhost", "127.0.0.1", 1)
    if url.startswith("https://localhost"):
        return url.replace("localhost", "127.0.0.1", 1)
    return url


DASHBOARD_URL = _normalize_dashboard_url(os.getenv("DASHBOARD_URL"))
API_TOKEN = os.getenv("DASHBOARD_API_TOKEN", "").strip()


async def send_approval_request(signal: dict[str, Any]) -> bool:
    """Send a signal to Telegram with Approve/Reject inline buttons."""
    try:
        if not TOKEN or not CHAT_ID:
            return False

        sid = signal["id"]
        sym = str(signal.get("symbol") or "").upper()
        side = str(signal.get("side") or signal.get("signal_type") or "BUY").upper()
        qty = int(signal.get("quantity") or signal.get("qty") or signal.get("quantity_to_buy") or 0)
        price = float(signal.get("price") or signal.get("signal_price") or 0)
        score = signal.get("score", signal.get("overall_score", 0))
        reason = str(signal.get("reason") or signal.get("approval_reason") or "Technical signal")

        try:
            from backend.brokerage.charges_engine import ChargesEngine, TradeSegment  # type: ignore
        except ModuleNotFoundError:  # noqa: BLE001
            from brokerage.charges_engine import ChargesEngine, TradeSegment  # type: ignore

        engine = ChargesEngine()
        charges = engine.calculate_charges(TradeSegment.intraday, price, price * 1.05, qty, True)

        text = (
            f"🚨 *{side} SIGNAL — {sym}*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 Price     : ₹{price:.2f}\n"
            f"📦 Quantity  : {qty}\n"
            f"🎯 Score     : {score}/100\n"
            f"📋 Reason    : {reason}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Charges   : ₹{charges.get('total_charges', 0):.2f}\n"
            f"💵 Est. Net  : ₹{charges.get('net_profit', 0):.2f}\n"
            f"📈 Ratio     : {charges.get('profitability_ratio', 0):.1f}x\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⏳ *Approve within 2 minutes*"
        )

        markup = {
            "inline_keyboard": [
                [
                    {"text": "✅ APPROVE", "callback_data": f"approve_{sid}"},
                    {"text": "❌ REJECT", "callback_data": f"reject_{sid}"},
                ]
            ]
        }

        async with httpx.AsyncClient(timeout=10, trust_env=False) as client:
            resp = await client.post(
                f"{BASE}/sendMessage",
                json={
                    "chat_id": CHAT_ID,
                    "text": text,
                    "parse_mode": "Markdown",
                    "reply_markup": markup,
                },
            )
            resp.raise_for_status()
            payload = resp.json()
            return bool(payload.get("ok", False))
    except Exception as exc:  # noqa: BLE001
        logger.error("Telegram send error: %s", exc)
        return False


async def send_message(text: str) -> bool:
    """Send a plain Telegram message."""
    try:
        if not TOKEN or not CHAT_ID:
            return False
        async with httpx.AsyncClient(timeout=10, trust_env=False) as client:
            resp = await client.post(
                f"{BASE}/sendMessage",
                json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"},
            )
            resp.raise_for_status()
            return bool(resp.json().get("ok", False))
    except Exception as exc:  # noqa: BLE001
        logger.error("Telegram message error: %s", exc)
        return False


async def answer_callback(callback_query_id: str, text: str) -> None:
    """Acknowledge a Telegram callback query quickly."""
    try:
        if not TOKEN:
            return
        async with httpx.AsyncClient(timeout=5, trust_env=False) as client:
            await client.post(
                f"{BASE}/answerCallbackQuery",
                json={"callback_query_id": callback_query_id, "text": text},
            )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Answer callback error: %s", exc)


class TelegramCallbackPoller:
    """Polls Telegram updates and updates dashboard signals on button presses."""

    def __init__(self) -> None:
        self._offset = 0
        self._running = False

    async def start(self) -> None:
        """Run the polling loop."""
        try:
            self._running = True
            logger.info("Telegram callback poller started")
            while self._running:
                await self._poll()
                await asyncio.sleep(2)
        except Exception as exc:  # noqa: BLE001
            logger.error("TelegramCallbackPoller start failed: %s", exc)

    async def stop(self) -> None:
        """Stop the polling loop."""
        try:
            self._running = False
        except Exception as exc:  # noqa: BLE001
            logger.error("TelegramCallbackPoller stop failed: %s", exc)

    def _auth_headers(self) -> dict[str, str]:
        if API_TOKEN:
            return {"Authorization": f"Bearer {API_TOKEN}"}
        admin_key = os.getenv("ADMIN_API_KEY", "").strip()
        return {"X-Admin-Key": admin_key} if admin_key else {}

    async def _poll(self) -> None:
        """Fetch new Telegram updates and process callback presses."""
        try:
            if not TOKEN:
                return
            async with httpx.AsyncClient(timeout=10, trust_env=False) as client:
                resp = await client.get(
                    f"{BASE}/getUpdates",
                    params={"offset": self._offset, "timeout": 5},
                )
                resp.raise_for_status()
                payload = resp.json()
                if not payload.get("ok"):
                    return
                updates = payload.get("result", [])

            for update in updates:
                self._offset = int(update.get("update_id", self._offset)) + 1
                callback = update.get("callback_query")
                if callback:
                    await self._handle_callback(callback)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Poll error: %s", exc)

    async def _handle_callback(self, callback: dict[str, Any]) -> None:
        """Handle approve/reject button presses."""
        try:
            data = str(callback.get("data") or "")
            callback_id = str(callback.get("id") or "")
            user = callback.get("from", {}).get("first_name", "User")

            if data.startswith("approve_"):
                signal_id = data.split("_", 1)[1]
                await answer_callback(callback_id, "✅ Signal approved!")
                ok = await self._update_signal(signal_id, "approved", "Telegram approved")
                if ok:
                    await send_message(f"✅ *{user} approved signal #{signal_id}*\nExecuting now…")
                else:
                    await send_message(f"⚠️ *{user} approved signal #{signal_id}* but dashboard update failed")
            elif data.startswith("reject_"):
                signal_id = data.split("_", 1)[1]
                await answer_callback(callback_id, "❌ Signal rejected")
                ok = await self._update_signal(signal_id, "rejected", "Telegram rejected")
                if ok:
                    await send_message(f"❌ *{user} rejected signal #{signal_id}*")
                else:
                    await send_message(f"⚠️ *{user} rejected signal #{signal_id}* but dashboard update failed")
        except Exception as exc:  # noqa: BLE001
            logger.error("Callback handling failed: %s", exc)

    async def _update_signal(self, signal_id: str, status: str, reason: str | None = None) -> bool:
        """Patch the dashboard signal status."""
        try:
            if not signal_id:
                return False
            async with httpx.AsyncClient(timeout=10, trust_env=False) as client:
                resp = await client.patch(
                    f"{DASHBOARD_URL}/api/signals/{signal_id}",
                    json={"status": status, "reason": reason},
                    headers=self._auth_headers(),
                )
                return resp.status_code == 200
        except Exception as exc:  # noqa: BLE001
            logger.error("Update signal error: %s", exc)
            return False

--- END FILE: trading-dashboard\backend\notifications\telegram_bot.py ---

--- START FILE: trading-dashboard\backend\notifications\__init__.py ---
"""Notification helpers for Telegram approvals and signal callbacks."""


--- END FILE: trading-dashboard\backend\notifications\__init__.py ---

--- START FILE: trading-dashboard\backend\portfolio\position_manager.py ---
"""Single source of truth for local positions, fills, and PnL calculations."""
from __future__ import annotations

import asyncio
import logging
import os
import sqlite3
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)
DB_PATH = Path(os.getenv("POSITIONS_DB_PATH", "data/positions.db"))


class PositionManager:
    """SQLite-backed position ledger shared by local agents."""

    def __init__(self) -> None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._cache: dict[str, dict] = {}
        self._lock = asyncio.Lock()
        self._load_from_db()

    def _init_db(self) -> None:
        with sqlite3.connect(DB_PATH) as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    broker TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    avg_entry REAL NOT NULL DEFAULT 0,
                    current_price REAL DEFAULT 0,
                    unrealized_pnl REAL DEFAULT 0,
                    realized_pnl REAL DEFAULT 0,
                    updated_at INTEGER DEFAULT 0,
                    UNIQUE(broker, symbol)
                )
                """
            )

    @staticmethod
    def _normalize_symbol(symbol: str) -> str:
        return (symbol or "").upper().replace(".NS", "").replace(".BO", "").strip()

    def _load_from_db(self) -> None:
        with sqlite3.connect(DB_PATH) as con:
            con.row_factory = sqlite3.Row
            rows = con.execute("SELECT * FROM positions").fetchall()
        for row in rows:
            key = f"{str(row['broker']).lower()}_{self._normalize_symbol(str(row['symbol']))}"
            self._cache[key] = {
                "broker": str(row["broker"]).lower(),
                "symbol": self._normalize_symbol(str(row["symbol"])),
                "side": str(row["side"] or "flat").lower(),
                "quantity": int(row["quantity"] or 0),
                "avg_entry": float(row["avg_entry"] or 0.0),
                "current_price": float(row["current_price"] or 0.0),
                "unrealized_pnl": float(row["unrealized_pnl"] or 0.0),
                "realized_pnl": float(row["realized_pnl"] or 0.0),
            }
        logger.info("Loaded %d positions from DB", len(self._cache))

    @staticmethod
    def _weighted_average(existing_qty: int, existing_price: float, added_qty: int, added_price: float) -> float:
        total_qty = existing_qty + added_qty
        if total_qty == 0:
            return float(added_price)
        return ((existing_qty * existing_price) + (added_qty * added_price)) / total_qty

    def _apply_buy_fill(self, pos: dict, quantity: int, fill_price: float) -> None:
        current_qty = int(pos["quantity"])
        if current_qty >= 0:
            new_qty = current_qty + quantity
            pos["avg_entry"] = self._weighted_average(current_qty, float(pos["avg_entry"]), quantity, fill_price) if new_qty else fill_price
            pos["quantity"] = new_qty
            pos["side"] = "long" if new_qty > 0 else "flat"
        else:
            short_qty = abs(current_qty)
            covered_qty = min(short_qty, quantity)
            pos["realized_pnl"] += (float(pos["avg_entry"]) - fill_price) * covered_qty
            new_qty = current_qty + quantity
            if new_qty < 0:
                pos["quantity"] = new_qty
                pos["side"] = "short"
            elif new_qty == 0:
                pos["quantity"] = 0
                pos["side"] = "flat"
            else:
                pos["quantity"] = new_qty
                pos["avg_entry"] = fill_price
                pos["side"] = "long"
        pos["current_price"] = fill_price

    def _apply_sell_fill(self, pos: dict, quantity: int, fill_price: float) -> None:
        current_qty = int(pos["quantity"])
        if current_qty > 0:
            closed_qty = min(current_qty, quantity)
            pos["realized_pnl"] += (fill_price - float(pos["avg_entry"])) * closed_qty
            new_qty = current_qty - quantity
            if new_qty > 0:
                pos["quantity"] = new_qty
                pos["side"] = "long"
            elif new_qty == 0:
                pos["quantity"] = 0
                pos["side"] = "flat"
            else:
                pos["quantity"] = new_qty
                pos["avg_entry"] = fill_price
                pos["side"] = "short"
        else:
            short_qty = abs(current_qty)
            new_short_qty = short_qty + quantity
            if current_qty < 0:
                pos["avg_entry"] = self._weighted_average(short_qty, float(pos["avg_entry"]), quantity, fill_price)
            pos["quantity"] = -new_short_qty
            pos["side"] = "short"
        pos["current_price"] = fill_price

    async def on_fill(
        self,
        broker: str,
        symbol: str,
        side: str,
        quantity: int,
        fill_price: float,
    ) -> None:
        """Apply a broker-confirmed fill to the local position ledger."""
        try:
            async with self._lock:
                broker_name = (broker or "").lower().strip()
                sym = self._normalize_symbol(symbol)
                fill_qty = abs(int(quantity))
                fill_price = float(fill_price)
                key = f"{broker_name}_{sym}"
                pos = self._cache.get(key)
                if not pos:
                    pos = {
                        "broker": broker_name,
                        "symbol": sym,
                        "side": "flat",
                        "quantity": 0,
                        "avg_entry": fill_price,
                        "current_price": fill_price,
                        "unrealized_pnl": 0.0,
                        "realized_pnl": 0.0,
                    }
                    self._cache[key] = pos

                if str(side).lower().strip() == "buy":
                    self._apply_buy_fill(pos, fill_qty, fill_price)
                else:
                    self._apply_sell_fill(pos, fill_qty, fill_price)

                await self._save(key)
                logger.info("Position updated: %s %s qty=%d", broker_name, sym, pos["quantity"])
        except Exception as exc:  # noqa: BLE001
            logger.error("on_fill failed: %s", exc)

    async def on_price_update(self, symbol: str, price: float) -> None:
        """Update unrealized PnL for any positions matching the symbol."""
        try:
            async with self._lock:
                sym = self._normalize_symbol(symbol)
                for pos in self._cache.values():
                    if pos["symbol"] != sym or int(pos["quantity"]) == 0:
                        continue
                    pos["current_price"] = float(price)
                    qty = int(pos["quantity"])
                    if qty > 0:
                        pos["unrealized_pnl"] = (float(price) - float(pos["avg_entry"])) * qty
                    else:
                        pos["unrealized_pnl"] = (float(pos["avg_entry"]) - float(price)) * abs(qty)
        except Exception as exc:  # noqa: BLE001
            logger.error("on_price_update failed: %s", exc)

    def get_position(self, broker: str, symbol: str) -> Optional[dict]:
        """Fetch one position from cache."""
        key = f"{(broker or '').lower().strip()}_{self._normalize_symbol(symbol)}"
        return self._cache.get(key)

    def get_all(self, broker: Optional[str] = None) -> list[dict]:
        """Return all positions, optionally filtered by broker."""
        if broker:
            broker_name = broker.lower().strip()
            return [pos for pos in self._cache.values() if pos["broker"] == broker_name]
        return list(self._cache.values())

    def get_total_exposure(self, broker: Optional[str] = None) -> float:
        """Return gross exposure for all positions."""
        positions = self.get_all(broker)
        return sum(abs(int(pos["quantity"])) * float(pos["current_price"] or pos["avg_entry"]) for pos in positions)

    def get_net_pnl(self, broker: Optional[str] = None) -> float:
        """Return realized + unrealized PnL."""
        positions = self.get_all(broker)
        return sum(float(pos["realized_pnl"]) + float(pos["unrealized_pnl"]) for pos in positions)

    async def reconcile(self, broker: str, broker_positions: list[dict]) -> list[dict]:
        """Compare local positions with broker-reported positions."""
        discrepancies: list[dict] = []
        try:
            broker_name = broker.lower().strip()
            broker_map: dict[str, dict] = {}
            for remote in broker_positions or []:
                sym = self._normalize_symbol(str(remote.get("symbol") or remote.get("trading_symbol") or ""))
                if sym:
                    broker_map[sym] = remote

            for local in self._cache.values():
                if local["broker"] != broker_name:
                    continue
                sym = local["symbol"]
                remote = broker_map.get(sym)
                if not remote:
                    if int(local["quantity"]) != 0:
                        discrepancies.append(
                            {"symbol": sym, "issue": "missing_at_broker", "local": int(local["quantity"]), "broker": 0}
                        )
                    continue
                remote_qty = int(remote.get("quantity") or remote.get("qty") or 0)
                if remote_qty != int(local["quantity"]):
                    discrepancies.append(
                        {"symbol": sym, "issue": "quantity_mismatch", "local": int(local["quantity"]), "broker": remote_qty}
                    )

            for sym, remote in broker_map.items():
                if not any(pos["broker"] == broker_name and pos["symbol"] == sym for pos in self._cache.values()):
                    remote_qty = int(remote.get("quantity") or remote.get("qty") or 0)
                    if remote_qty != 0:
                        discrepancies.append(
                            {"symbol": sym, "issue": "missing_locally", "local": 0, "broker": remote_qty}
                        )

            if discrepancies:
                logger.warning("Reconciliation found %d discrepancies", len(discrepancies))
            return discrepancies
        except Exception as exc:  # noqa: BLE001
            logger.error("reconcile failed: %s", exc)
            return [{"issue": "reconcile_error", "error": str(exc)}]

    async def _save(self, key: str) -> None:
        """Persist a cached position row to SQLite."""
        try:
            pos = self._cache[key]
            with sqlite3.connect(DB_PATH) as con:
                con.execute(
                    """
                    INSERT INTO positions (
                        broker, symbol, side, quantity, avg_entry, current_price,
                        unrealized_pnl, realized_pnl, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(broker, symbol) DO UPDATE SET
                        side=excluded.side,
                        quantity=excluded.quantity,
                        avg_entry=excluded.avg_entry,
                        current_price=excluded.current_price,
                        unrealized_pnl=excluded.unrealized_pnl,
                        realized_pnl=excluded.realized_pnl,
                        updated_at=excluded.updated_at
                    """,
                    (
                        pos["broker"],
                        pos["symbol"],
                        pos["side"],
                        int(pos["quantity"]),
                        float(pos["avg_entry"]),
                        float(pos["current_price"]),
                        float(pos["unrealized_pnl"]),
                        float(pos["realized_pnl"]),
                        int(time.time()),
                    ),
                )
        except Exception as exc:  # noqa: BLE001
            logger.error("_save failed: %s", exc)


--- END FILE: trading-dashboard\backend\portfolio\position_manager.py ---

--- START FILE: trading-dashboard\backend\portfolio\__init__.py ---
"""Portfolio package containing position management helpers."""


--- END FILE: trading-dashboard\backend\portfolio\__init__.py ---

--- START FILE: trading-dashboard\backend\risk\capital_allocator.py ---
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(slots=True)
class CapitalConfig:
    """
    Institutional capital allocation rules.

    All percentages are expressed as fractions (0.70 = 70%).
    """

    max_capital_deployment: float = 0.70
    risk_per_trade: float = 0.01
    max_position_size: float = 0.10
    max_open_positions: int = 8
    emergency_reserve: float = 0.20


class CapitalAllocator:
    def __init__(self, config: CapitalConfig | None = None) -> None:
        self.config = config or CapitalConfig()

    def calculate_position_size(
        self,
        account_balance: float,
        entry_price: float,
        stop_loss_price: float,
        current_exposure: float,
        open_positions: int,
    ) -> Dict[str, Any]:
        reserve_capital = account_balance * self.config.emergency_reserve
        max_deployable = account_balance * self.config.max_capital_deployment
        remaining_deployable = max_deployable - current_exposure

        if open_positions >= self.config.max_open_positions:
            return {"allowed": False, "reason": "Maximum open positions reached"}

        stop_distance = abs(entry_price - stop_loss_price)
        if stop_distance <= 0:
            return {"allowed": False, "reason": "Invalid stop loss distance"}

        risk_amount = account_balance * self.config.risk_per_trade
        quantity = int(risk_amount / stop_distance)

        if quantity <= 0:
            return {"allowed": False, "reason": "Calculated quantity is 0 (risk too small or stop too wide)"}

        position_value = quantity * entry_price

        max_position_value = account_balance * self.config.max_position_size
        if position_value > max_position_value:
            quantity = int(max_position_value / entry_price)
            position_value = quantity * entry_price

        if position_value > remaining_deployable:
            return {
                "allowed": False,
                "reason": f"Insufficient deployable capital. Available: {remaining_deployable:.2f}",
            }

        return {
            "allowed": True,
            "quantity": quantity,
            "position_value": round(position_value, 2),
            "risk_amount": round(risk_amount, 2),
            "remaining_capital": round(account_balance - current_exposure - position_value, 2),
            "reserved_capital": round(reserve_capital, 2),
        }


--- END FILE: trading-dashboard\backend\risk\capital_allocator.py ---

--- START FILE: trading-dashboard\backend\risk\risk_guardian.py ---
"""Async risk guard that validates basic order sanity before execution."""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

try:
    from backend.brokerage.charges_engine import ChargesEngine, TradeSegment  # type: ignore
except ModuleNotFoundError:  # noqa: BLE001
    from brokerage.charges_engine import ChargesEngine, TradeSegment  # type: ignore

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class RiskGuardian:
    """Basic guardrails used by the execution agent."""

    charges_engine: ChargesEngine
    max_quantity: int = int(os.getenv("MAX_RISK_QTY", "5000"))
    max_order_value: float = float(os.getenv("MAX_RISK_ORDER_VALUE", "2500000"))

    async def evaluate(self, order: dict[str, Any]) -> dict[str, Any]:
        """Approve or reject an order based on simple risk checks and charges."""
        try:
            symbol = str(order.get("symbol") or "").upper().strip()
            side = str(order.get("side") or "buy").lower().strip()
            qty = int(order.get("quantity") or order.get("qty") or 0)
            price = float(order.get("price") or order.get("entry_price") or 0.0)
            expected_exit = float(order.get("expected_exit") or order.get("take_profit") or 0.0)
            segment_name = str(order.get("trade_segment") or "intraday").lower().strip()
            segment = TradeSegment.delivery if segment_name == "delivery" else TradeSegment.intraday

            if not symbol or side not in {"buy", "sell"}:
                return {"action": "REJECT", "reason": "invalid_order_side"}
            if qty <= 0 or price <= 0 or expected_exit <= 0:
                return {"action": "REJECT", "reason": "invalid_order_values"}
            if qty > self.max_quantity:
                return {"action": "REJECT", "reason": f"qty_over_limit_{self.max_quantity}"}
            if price * qty > self.max_order_value:
                return {"action": "REJECT", "reason": f"order_value_over_limit_{self.max_order_value:.0f}"}

            if side == "sell":
                buy_price = expected_exit
                sell_price = price
            else:
                buy_price = price
                sell_price = expected_exit

            charges = self.charges_engine.calculate_charges(
                segment,
                buy_price=buy_price,
                sell_price=sell_price,
                quantity=qty,
                using_api=True,
            )
            if not charges.get("should_execute", True):
                return {
                    "action": "REJECT",
                    "reason": (
                        f"ratio_{charges.get('profitability_ratio', 0)}x_below_min_{self.charges_engine.min_profitability_ratio}x"
                    ),
                    "charges": charges,
                }

            return {"action": "APPROVE", "reason": "ok", "charges": charges}
        except Exception as exc:  # noqa: BLE001
            logger.error("Risk evaluation failed: %s", exc)
            return {"action": "REJECT", "reason": f"risk_error:{exc}"}


--- END FILE: trading-dashboard\backend\risk\risk_guardian.py ---

--- START FILE: trading-dashboard\backend\risk\__init__.py ---

--- END FILE: trading-dashboard\backend\risk\__init__.py ---

--- START FILE: trading-dashboard\backend\runtime\system_runtime.py ---
"""Coordinates market data, signal execution, news, and Telegram polling at startup."""
from __future__ import annotations

import asyncio
import importlib
import logging
import os
from typing import Any, Optional

try:
    from backend.agents.news_sentiment_agent import NewsSentimentAgent  # type: ignore
    from backend.agents.trade_execution_agent import TradeExecutionAgent  # type: ignore
    from backend.brokers.paper_broker import PaperBroker, PaperBrokerRouter  # type: ignore
    from backend.execution.auth.broker_auth_manager import BrokerAuthManager  # type: ignore
    from backend.market_data.market_data_engine import MarketDataEngine  # type: ignore
    from backend.notifications.telegram_bot import TelegramCallbackPoller  # type: ignore
    from backend.portfolio.position_manager import PositionManager  # type: ignore
    from backend.brokerage.charges_engine import ChargesEngine  # type: ignore
    from backend.risk.risk_guardian import RiskGuardian  # type: ignore
    from backend.database import SessionLocal, WatchlistStock  # type: ignore
except ModuleNotFoundError:  # noqa: BLE001
    from agents.news_sentiment_agent import NewsSentimentAgent  # type: ignore
    from agents.trade_execution_agent import TradeExecutionAgent  # type: ignore
    from brokers.paper_broker import PaperBroker, PaperBrokerRouter  # type: ignore
    from execution.auth.broker_auth_manager import BrokerAuthManager  # type: ignore
    from market_data.market_data_engine import MarketDataEngine  # type: ignore
    from notifications.telegram_bot import TelegramCallbackPoller  # type: ignore
    from portfolio.position_manager import PositionManager  # type: ignore
    from brokerage.charges_engine import ChargesEngine  # type: ignore
    from risk.risk_guardian import RiskGuardian  # type: ignore
    from database import SessionLocal, WatchlistStock  # type: ignore

logger = logging.getLogger(__name__)


def _normalize_symbol(symbol: str) -> str:
    return str(symbol or "").upper().replace(".NS", "").replace(".BO", "").strip()


def _flag_enabled(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


class TradingSystemRuntime:
    """Starts and stops the agents that make the dashboard behave like a trading system."""

    def __init__(
        self,
        event_bus: Any,
        symbol_master: Any,
        live_broker: Any | None = None,
        trading_mode: str = "paper",
    ) -> None:
        self.event_bus = event_bus
        self.symbol_master = symbol_master
        self.live_broker = live_broker
        self.trading_mode = str(trading_mode or "paper").lower().strip()
        self.broker_mode = "live" if self.trading_mode == "live" and self.live_broker is not None else "paper"
        self.position_manager = PositionManager()
        self.charges_engine = ChargesEngine(min_profitability_ratio=float(os.getenv("MIN_PROFITABILITY_RATIO", "3.0")))
        self.risk_guardian = RiskGuardian(self.charges_engine)
        self.market_data: MarketDataEngine | None = None
        self.news_agent: NewsSentimentAgent | None = None
        self.telegram_poller: TelegramCallbackPoller | None = None
        self.technical_agent: Any | None = None
        self._tasks: dict[str, asyncio.Task[Any]] = {}
        self._running = False
        self._watchlist_symbols: list[str] = []
        self._market_data_enabled = _flag_enabled("ENABLE_MARKET_DATA") or self.trading_mode == "live"
        self._paper_router = PaperBrokerRouter({"upstox": PaperBroker(broker_name="upstox")})
        self.broker_adapter = self.live_broker if self.broker_mode == "live" and self.live_broker is not None else self._paper_router
        if self.broker_mode == "paper" and self.live_broker is None and self.trading_mode == "live":
            logger.warning("Live trading was requested but no live broker is available. Falling back to paper mode.")
        self.trade_agent = TradeExecutionAgent(
            broker_router=self.broker_adapter,
            risk_guardian=self.risk_guardian,
            charges_engine=self.charges_engine,
            position_manager=self.position_manager,
            event_bus=self.event_bus,
        )

    def _load_watchlist_symbols(self) -> list[str]:
        symbols: set[str] = set()
        try:
            db = SessionLocal()
            try:
                rows = db.query(WatchlistStock).filter(WatchlistStock.status == "active").all()
            finally:
                db.close()
            for row in rows:
                sym = _normalize_symbol(getattr(row, "symbol", ""))
                if sym:
                    symbols.add(sym)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not load watchlist symbols: %s", exc)
        return sorted(symbols)

    def _build_optional_technical_agent(self, watchlist: list[str]) -> Any | None:
        """Load an optional technical-analysis agent if the user's laptop copy provides one."""
        for module_name in (
            "backend.agents.technical_analysis_agent",
            "agents.technical_analysis_agent",
        ):
            try:
                module = importlib.import_module(module_name)
            except Exception:
                continue
            agent_cls = getattr(module, "TechnicalAnalysisAgent", None) or getattr(module, "TechnicalAgent", None)
            if agent_cls is None:
                continue

            keyword_variants = (
                {
                    "event_bus": self.event_bus,
                    "watchlist": watchlist,
                    "symbol_master": self.symbol_master,
                    "market_data_engine": self.market_data,
                },
                {
                    "event_bus": self.event_bus,
                    "watchlist": watchlist,
                    "symbol_master": self.symbol_master,
                    "market_data": self.market_data,
                },
                {"event_bus": self.event_bus, "watchlist": watchlist},
                {"event_bus": self.event_bus},
            )
            positional_variants = (
                (self.event_bus, watchlist),
                (self.event_bus,),
            )

            for kwargs in keyword_variants:
                try:
                    return agent_cls(**kwargs)
                except TypeError:
                    continue
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Technical agent init failed: %s", exc)
                    return None

            for args in positional_variants:
                try:
                    return agent_cls(*args)
                except TypeError:
                    continue
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Technical agent init failed: %s", exc)
                    return None

            logger.warning("Technical analysis agent found, but no known constructor signature matched.")
            return None
        return None

    def _spawn(self, name: str, coro: Any) -> None:
        task = asyncio.create_task(coro)
        def _log_task_result(done: asyncio.Task[Any]) -> None:
            try:
                exc = done.exception()
                if exc is not None:
                    logger.error("%s task failed: %s", name, exc)
            except asyncio.CancelledError:
                pass
            except Exception as exc:  # noqa: BLE001
                logger.error("%s task inspection failed: %s", name, exc)

        task.add_done_callback(_log_task_result)
        self._tasks[name] = task

    def status(self) -> dict[str, Any]:
        """Return a snapshot of the runtime state for health checks."""
        snapshot: dict[str, Any] = {
            "running": self._running,
            "mode": self.trading_mode,
            "broker_mode": self.broker_mode,
            "watchlist_symbols": list(self._watchlist_symbols),
            "watchlist_count": len(self._watchlist_symbols),
            "market_data_enabled": self._market_data_enabled,
            "market_data_online": self.market_data is not None,
            "news_agent_online": self.news_agent is not None,
            "telegram_online": self.telegram_poller is not None,
            "technical_agent_online": self.technical_agent is not None,
            "tasks": {name: not task.done() for name, task in self._tasks.items()},
            "paper_snapshot": self._paper_router.snapshot() if self.broker_mode == "paper" else None,
        }
        return snapshot

    async def start(self) -> None:
        """Start all configured agents without blocking the FastAPI app startup."""
        try:
            if self._running:
                return
            self._running = True
            self._watchlist_symbols = self._load_watchlist_symbols()
            self.event_bus.subscribe("market.tick", self.position_manager.on_price_update)

            if self._market_data_enabled:
                try:
                    self.market_data = MarketDataEngine(self.event_bus, BrokerAuthManager("upstox"))
                    await self.market_data.start()
                    if self._watchlist_symbols:
                        await self.market_data.subscribe(self._watchlist_symbols)
                    logger.info("Market data runtime started")
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Market data startup failed: %s", exc)

            self.technical_agent = self._build_optional_technical_agent(self._watchlist_symbols)
            if self.technical_agent is not None and hasattr(self.technical_agent, "start"):
                self._spawn("technical", self.technical_agent.start())

            if self._watchlist_symbols and os.getenv("NEWSAPI_KEY", "").strip():
                self.news_agent = NewsSentimentAgent(self.event_bus, self._watchlist_symbols)
                self._spawn("news", self.news_agent.start())

            self._spawn("trade", self.trade_agent.start())

            if os.getenv("TELEGRAM_BOT_TOKEN", "").strip() and os.getenv("DASHBOARD_API_TOKEN", "").strip():
                self.telegram_poller = TelegramCallbackPoller()
                self._spawn("telegram", self.telegram_poller.start())

            logger.info(
                "Runtime started (mode=%s, broker_mode=%s, watchlist=%d, market_data=%s)",
                self.trading_mode,
                self.broker_mode,
                len(self._watchlist_symbols),
                "on" if self.market_data is not None else "off",
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("TradingSystemRuntime start failed: %s", exc)

    async def stop(self) -> None:
        """Stop the agents and cancel background tasks."""
        try:
            self._running = False
            for agent in (self.telegram_poller, self.news_agent, self.trade_agent, self.market_data, self.technical_agent):
                try:
                    stop = getattr(agent, "stop", None)
                    if stop is not None:
                        result = stop()
                        if asyncio.iscoroutine(result):
                            await result
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Agent stop failed: %s", exc)

            for name, task in list(self._tasks.items()):
                if not task.done():
                    task.cancel()
            if self._tasks:
                await asyncio.gather(*self._tasks.values(), return_exceptions=True)
            self._tasks.clear()
        except Exception as exc:  # noqa: BLE001
            logger.error("TradingSystemRuntime stop failed: %s", exc)


def build_runtime(
    event_bus: Any,
    symbol_master: Any,
    live_broker: Any | None = None,
    trading_mode: str = "paper",
) -> TradingSystemRuntime:
    """Factory used by the FastAPI app to bootstrap the agent runtime."""
    return TradingSystemRuntime(
        event_bus=event_bus,
        symbol_master=symbol_master,
        live_broker=live_broker,
        trading_mode=trading_mode,
    )

--- END FILE: trading-dashboard\backend\runtime\system_runtime.py ---

--- START FILE: trading-dashboard\backend\runtime\__init__.py ---
"""Runtime orchestration helpers for the trading dashboard backend."""


--- END FILE: trading-dashboard\backend\runtime\__init__.py ---

--- START FILE: trading-dashboard\backend\security\jwt_auth.py ---
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def _now() -> int:
    return int(time.time())


@dataclass(slots=True)
class JwtConfig:
    secret_key: str
    issuer: str = "trading-dashboard"
    algorithm: str = "HS256"
    access_token_ttl_sec: int = 3600


class JwtAuth:
    """
    Minimal HS256 JWT implementation (no external dependencies).

    This is intentionally small so deployments don't fail due to missing crypto libs.
    """

    def __init__(self, cfg: JwtConfig):
        if not cfg.secret_key:
            raise ValueError("JWT secret key is empty")
        self.cfg = cfg

    def create_token(self, subject: str, role: str = "user", extra: Optional[Dict[str, Any]] = None) -> str:
        header = {"alg": self.cfg.algorithm, "typ": "JWT"}
        payload: Dict[str, Any] = {
            "sub": subject,
            "role": role,
            "iss": self.cfg.issuer,
            "iat": _now(),
            "exp": _now() + int(self.cfg.access_token_ttl_sec),
        }
        if extra:
            payload.update(extra)

        h = _b64url_encode(json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8"))
        p = _b64url_encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
        sig = self._sign(f"{h}.{p}".encode("ascii"))
        return f"{h}.{p}.{sig}"

    def verify_token(self, token: str) -> Dict[str, Any]:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid token format")
        h, p, sig = parts
        signing_input = f"{h}.{p}".encode("ascii")
        expected = self._sign(signing_input)
        if not hmac.compare_digest(expected, sig):
            raise ValueError("Invalid token signature")

        payload = json.loads(_b64url_decode(p).decode("utf-8"))
        exp = int(payload.get("exp") or 0)
        if exp and _now() >= exp:
            raise ValueError("Token expired")
        if payload.get("iss") != self.cfg.issuer:
            raise ValueError("Invalid issuer")
        return payload

    def _sign(self, signing_input: bytes) -> str:
        if self.cfg.algorithm != "HS256":
            raise ValueError("Only HS256 is supported")
        mac = hmac.new(self.cfg.secret_key.encode("utf-8"), signing_input, hashlib.sha256).digest()
        return _b64url_encode(mac)


def load_jwt_auth() -> Optional[JwtAuth]:
    secret = os.getenv("JWT_SECRET_KEY", "").strip()
    if not secret:
        return None
    ttl = int(os.getenv("JWT_ACCESS_TTL_SEC", "28800"))
    issuer = os.getenv("JWT_ISSUER", "trading-dashboard")
    return JwtAuth(JwtConfig(secret_key=secret, access_token_ttl_sec=ttl, issuer=issuer))

--- END FILE: trading-dashboard\backend\security\jwt_auth.py ---

--- START FILE: trading-dashboard\backend\security\__init__.py ---

--- END FILE: trading-dashboard\backend\security\__init__.py ---

--- START FILE: trading-dashboard\frontend\build.mjs ---
import { build } from 'vite'
import react from '@vitejs/plugin-react'

await build({
  configFile: false,
  root: process.cwd(),
  plugins: [react()],
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
})

--- END FILE: trading-dashboard\frontend\build.mjs ---

--- START FILE: trading-dashboard\frontend\index.html ---
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Trading Dashboard</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
--- END FILE: trading-dashboard\frontend\index.html ---

--- START FILE: trading-dashboard\frontend\package.json ---
{
  "name": "trading-dashboard-frontend",
  "private": true,
  "version": "0.0.1",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && node build.mjs",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0",
    "recharts": "^2.10.3"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.2.2",
    "vite": "^5.0.8",
    "tailwindcss": "^3.3.6",
    "postcss": "^8.4.31",
    "autoprefixer": "^10.4.16"
  }
}

--- END FILE: trading-dashboard\frontend\package.json ---

--- START FILE: trading-dashboard\frontend\postcss.config.js ---
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};


--- END FILE: trading-dashboard\frontend\postcss.config.js ---

--- START FILE: trading-dashboard\frontend\tailwind.config.js ---
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {},
  },
  plugins: [],
};


--- END FILE: trading-dashboard\frontend\tailwind.config.js ---

--- START FILE: trading-dashboard\frontend\tsconfig.json ---
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "allowImportingTsExtensions": true,
    "strict": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src"]
}
--- END FILE: trading-dashboard\frontend\tsconfig.json ---

--- START FILE: trading-dashboard\frontend\tsconfig.tsbuildinfo ---
{"root":["./src/app.tsx","./src/main.tsx","./src/components/agentanimation.tsx","./src/components/agentmonitor.tsx","./src/components/backtestingpage.tsx","./src/components/chatinterface.tsx","./src/components/errorboundary.tsx","./src/components/overviewpage.tsx","./src/components/portfoliopage.tsx","./src/components/settingspage.tsx","./src/components/signalspage.tsx","./src/components/stockscreener.tsx","./src/components/strategiespage.tsx","./src/components/tradingpage.tsx","./src/components/watchlistpage.tsx","./src/hooks/useapi.ts","./src/hooks/uselocalstorage.ts","./src/hooks/usewebsocket.ts"],"version":"5.9.3"}
--- END FILE: trading-dashboard\frontend\tsconfig.tsbuildinfo ---

--- START FILE: trading-dashboard\frontend\vite.config.js ---
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
--- END FILE: trading-dashboard\frontend\vite.config.js ---

--- START FILE: trading-dashboard\frontend\src\App.css ---
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --bg: #0a0e1a;
  --surface: #0f1629;
  --panel: #141d35;
  --panel-2: #192038;
  --border: #1e2d4a;
  --border-2: #253860;
  --accent: #00d4ff;
  --accent-dim: rgba(0, 212, 255, 0.15);
  --green: #00ff88;
  --green-dim: rgba(0, 255, 136, 0.12);
  --red: #ff3b5c;
  --red-dim: rgba(255, 59, 92, 0.12);
  --yellow: #ffd700;
  --yellow-dim: rgba(255, 215, 0, 0.12);
  --text: #e2eaf8;
  --text-muted: #5a7090;
  --text-dim: #3a5070;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body, #root {
  height: 100%;
  background: var(--bg);
  color: var(--text);
  font-family: 'IBM Plex Sans', system-ui, sans-serif;
  font-size: 13px;
  line-height: 1.5;
  overflow: hidden;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--surface); }
::-webkit-scrollbar-thumb { background: var(--border-2); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* Animations */
@keyframes pulse-green {
  0%, 100% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.4); }
  50% { box-shadow: 0 0 0 4px rgba(0, 255, 136, 0); }
}

@keyframes pulse-red {
  0%, 100% { box-shadow: 0 0 0 0 rgba(255, 59, 92, 0.4); }
  50% { box-shadow: 0 0 0 4px rgba(255, 59, 92, 0); }
}

@keyframes spin-slow {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes slide-in {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes scanline {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(100vh); }
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.animate-slide-in { animation: slide-in 0.2s ease-out; }
.animate-fade-in { animation: fade-in 0.3s ease-out; }
.animate-spin-slow { animation: spin-slow 2s linear infinite; }
.animate-blink { animation: blink 1s step-end infinite; }

/* Status dots */
.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}
.status-dot.online { background: var(--green); animation: pulse-green 2s infinite; }
.status-dot.processing { background: var(--accent); animation: pulse-green 1s infinite; }
.status-dot.idle { background: var(--yellow); }
.status-dot.error { background: var(--red); animation: pulse-red 2s infinite; }
.status-dot.offline { background: var(--text-dim); }

/* Neon text effects */
.text-accent { color: var(--accent); }
.text-green { color: var(--green); }
.text-red { color: var(--red); }
.text-yellow { color: var(--yellow); }
.text-muted { color: var(--text-muted); }

/* Panels */
.panel {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 4px;
}

.panel-header {
  padding: 8px 12px;
  border-bottom: 1px solid var(--border);
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Buttons */
.btn {
  padding: 5px 12px;
  border-radius: 3px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.15s ease;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  outline: none;
}

.btn-accent {
  background: var(--accent);
  color: var(--bg);
}
.btn-accent:hover { background: #00b8d9; transform: translateY(-1px); }

.btn-green {
  background: var(--green);
  color: var(--bg);
}
.btn-green:hover { background: #00e077; transform: translateY(-1px); }

.btn-red {
  background: var(--red);
  color: white;
}
.btn-red:hover { background: #ff1a40; transform: translateY(-1px); }

.btn-ghost {
  background: transparent;
  color: var(--text-muted);
  border: 1px solid var(--border-2);
}
.btn-ghost:hover {
  background: var(--panel-2);
  color: var(--text);
  border-color: var(--accent);
}

/* Inputs */
.input {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 3px;
  padding: 6px 10px;
  color: var(--text);
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  outline: none;
  transition: border-color 0.15s;
  width: 100%;
}
.input:focus { border-color: var(--accent); }
.input::placeholder { color: var(--text-dim); }

select.input {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%235a7090'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 8px center;
  padding-right: 24px;
}

/* Tables */
.table-wrapper { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
thead th {
  padding: 6px 10px;
  text-align: left;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  font-weight: 600;
  color: var(--text-muted);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}
tbody td {
  padding: 7px 10px;
  border-bottom: 1px solid rgba(30, 45, 74, 0.5);
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  white-space: nowrap;
}
tbody tr:hover { background: rgba(0, 212, 255, 0.03); }
tbody tr:last-child td { border-bottom: none; }

/* Progress bar */
.progress-bar {
  height: 3px;
  background: var(--border);
  border-radius: 2px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), var(--green));
  border-radius: 2px;
  transition: width 0.3s ease;
}

/* Tags */
.tag {
  display: inline-flex;
  align-items: center;
  padding: 1px 6px;
  border-radius: 2px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.05em;
}
.tag-buy { background: var(--green-dim); color: var(--green); border: 1px solid rgba(0,255,136,0.2); }
.tag-sell { background: var(--red-dim); color: var(--red); border: 1px solid rgba(255,59,92,0.2); }
.tag-hold { background: var(--yellow-dim); color: var(--yellow); border: 1px solid rgba(255,215,0,0.2); }
.tag-running { background: var(--green-dim); color: var(--green); border: 1px solid rgba(0,255,136,0.2); }
.tag-paused { background: var(--yellow-dim); color: var(--yellow); border: 1px solid rgba(255,215,0,0.2); }
.tag-backtesting { background: var(--accent-dim); color: var(--accent); border: 1px solid rgba(0,212,255,0.2); }

/* Grid scanline overlay for aesthetic */
.scanline-overlay {
  pointer-events: none;
  position: fixed;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0, 0, 0, 0.03) 2px,
    rgba(0, 0, 0, 0.03) 4px
  );
  z-index: 9999;
}

/* Tooltip */
.tooltip {
  position: relative;
}
.tooltip::after {
  content: attr(data-tip);
  position: absolute;
  bottom: 110%;
  left: 50%;
  transform: translateX(-50%);
  background: var(--panel-2);
  border: 1px solid var(--border-2);
  padding: 4px 8px;
  border-radius: 3px;
  font-size: 11px;
  white-space: nowrap;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.15s;
  z-index: 100;
}
.tooltip:hover::after { opacity: 1; }

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(10, 14, 26, 0.85);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fade-in 0.15s ease;
}

.modal-box {
  background: var(--panel);
  border: 1px solid var(--border-2);
  border-radius: 6px;
  max-width: 90vw;
  max-height: 85vh;
  overflow-y: auto;
  animation: slide-in 0.2s ease;
  box-shadow: 0 20px 60px rgba(0,0,0,0.6);
}

/* Neon glow helpers */
.glow-accent { text-shadow: 0 0 8px var(--accent); }
.glow-green { text-shadow: 0 0 8px var(--green); }
.glow-red { text-shadow: 0 0 8px var(--red); }
.border-glow-accent { box-shadow: 0 0 8px rgba(0,212,255,0.2); }

/* Chat markdown */
.prose-chat { color: var(--text); line-height: 1.6; }
.prose-chat h1, .prose-chat h2, .prose-chat h3 { color: var(--accent); margin-bottom: 8px; font-family: 'JetBrains Mono', monospace; }
.prose-chat p { margin-bottom: 8px; }
.prose-chat ul, .prose-chat ol { padding-left: 16px; margin-bottom: 8px; }
.prose-chat li { margin-bottom: 2px; }
.prose-chat code { background: var(--surface); padding: 1px 4px; border-radius: 2px; font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--accent); }
.prose-chat pre { background: var(--surface); padding: 10px; border-radius: 4px; overflow-x: auto; margin-bottom: 8px; border: 1px solid var(--border); }
.prose-chat strong { color: var(--text); font-weight: 700; }
.prose-chat em { color: var(--text-muted); }
.prose-chat table { width: 100%; margin-bottom: 8px; }
.prose-chat thead th { color: var(--accent); padding: 4px 8px; border-bottom: 1px solid var(--border); font-size: 11px; }
.prose-chat tbody td { padding: 4px 8px; border-bottom: 1px solid rgba(30,45,74,0.4); }
--- END FILE: trading-dashboard\frontend\src\App.css ---

--- START FILE: trading-dashboard\frontend\src\App.tsx ---
import React, { useState } from 'react';
import { OverviewPage } from './components/OverviewPage';
import { TradingPage } from './components/TradingPage';
import { StrategiesPage } from './components/StrategiesPage';
import { BacktestingPage } from './components/BacktestingPage';
import { StockScreener } from './components/StockScreener';
import { SettingsPage } from './components/SettingsPage';
import { AgentAnimation } from './components/AgentAnimation';
import { ChatInterface } from './components/ChatInterface';
import { AgentMonitor } from './components/AgentMonitor';
import { WatchlistPage } from './components/WatchlistPage';
import { SignalsPage } from './components/SignalsPage';
import { PortfolioPage } from './components/PortfolioPage';

type Page =
  | 'overview'
  | 'chat'
  | 'watchlist'
  | 'signals'
  | 'portfolio'
  | 'trading'
  | 'strategies'
  | 'backtesting'
  | 'screener'
  | 'settings'
  | 'animation';

function App() {
  const [page, setPage] = useState<Page>('overview');

  const renderPage = () => {
    switch (page) {
      case 'overview': return <OverviewPage />;
      case 'trading': return <TradingPage />;
      case 'strategies': return <StrategiesPage />;
      case 'backtesting': return <BacktestingPage />;
      case 'screener': return <StockScreener />;
      case 'settings': return <SettingsPage />;
      case 'animation': return <AgentAnimation />;
      case 'watchlist': return <WatchlistPage />;
      case 'signals': return <SignalsPage />;
      case 'portfolio': return <PortfolioPage />;
      default:
        return <ChatInterface />;
    }
  };

  return (
    <div className="min-h-screen bg-black text-white grid grid-cols-1 lg:grid-cols-[280px_1fr]">
      <aside className="border-r border-gray-900 p-4">
        <div className="text-lg font-bold mb-3">Trading Dashboard</div>
        <AgentMonitor />
        <div className="h-px bg-gray-800 my-4" />
        <div className="space-y-2">
          {(
            [
              'overview',
              'chat',
              'watchlist',
              'signals',
              'portfolio',
              'trading',
              'strategies',
              'backtesting',
              'screener',
              'settings',
              'animation',
            ] as Page[]
          ).map((p) => (
            <button
              key={p}
              onClick={() => setPage(p)}
              className={`w-full text-left px-3 py-2 rounded font-semibold ${
                page === p ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-900 hover:bg-gray-800'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </aside>
      <main className="min-w-0">{renderPage()}</main>
    </div>
  );
}

export default App;

--- END FILE: trading-dashboard\frontend\src\App.tsx ---

--- START FILE: trading-dashboard\frontend\src\index.css ---
:root { color-scheme: dark; }
* { box-sizing: border-box; }
html, body, #root { margin: 0; padding: 0; min-height: 100%; background: #05070b; color: #e5e7eb; font-family: Inter, Segoe UI, sans-serif; }
button, input, select, textarea { font: inherit; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 8px; border-bottom: 1px solid #1f2937; text-align: left; }
@media (max-width: 375px) {
  main, aside, div { max-width: 100%; overflow-x: auto; }
}

--- END FILE: trading-dashboard\frontend\src\index.css ---

--- START FILE: trading-dashboard\frontend\src\main.tsx ---
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './App.css'
import './index.css'
import { ErrorBoundary } from './components/ErrorBoundary'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>,
)

--- END FILE: trading-dashboard\frontend\src\main.tsx ---

--- START FILE: trading-dashboard\frontend\src\components\AgentAnimation.tsx ---
import React, { useEffect, useState } from 'react';

interface AgentMetrics {
  response_time: number;
  agent_processing: number;
  llm_generation: number;
  network_latency: number;
}

export function AgentAnimationView() {
  const [metrics, setMetrics] = useState<AgentMetrics | null>(null);

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/agent-monitor`);
    ws.onmessage = () => {
      setMetrics({
        response_time: Math.random() * 3,
        agent_processing: Math.random() * 2,
        llm_generation: Math.random() * 1.5,
        network_latency: Math.random() * 0.5,
      });
    };
    return () => ws.close();
  }, []);

  return (
    <div className="p-6 bg-black text-white">
      <h1 className="text-3xl font-bold mb-6">Agent Orchestration</h1>

      <div className="bg-gray-900 p-6 rounded-lg mb-6 overflow-auto">
        <svg width="100%" height="400" viewBox="0 0 600 400" className="mx-auto">
          <rect x="50" y="20" width="120" height="50" fill="#1f2937" stroke="#3b82f6" strokeWidth="2" rx="5" />
          <text x="110" y="50" textAnchor="middle" fill="white" fontSize="12" fontWeight="bold">
            User Input
          </text>

          <rect x="230" y="20" width="120" height="50" fill="#1f2937" stroke="#3b82f6" strokeWidth="2" rx="5" />
          <text x="290" y="50" textAnchor="middle" fill="white" fontSize="12" fontWeight="bold">
            Dashboard
          </text>

          <rect x="230" y="120" width="120" height="50" fill="#1f2937" stroke="#8b5cf6" strokeWidth="2" rx="5" />
          <text x="290" y="150" textAnchor="middle" fill="white" fontSize="12" fontWeight="bold">
            Boss Agent
          </text>

          <rect x="50" y="120" width="120" height="50" fill="#1f2937" stroke="#ec4899" strokeWidth="2" rx="5" />
          <text x="110" y="145" textAnchor="middle" fill="white" fontSize="12" fontWeight="bold">
            Ollama LLM
          </text>
          <text x="110" y="160" textAnchor="middle" fill="#ec4899" fontSize="10">
            local models
          </text>

          <rect x="20" y="240" width="90" height="40" fill="#1f2937" stroke="#10b981" strokeWidth="2" rx="5" />
          <text x="65" y="265" textAnchor="middle" fill="white" fontSize="11" fontWeight="bold">
            Technical
          </text>

          <rect x="125" y="240" width="90" height="40" fill="#1f2937" stroke="#10b981" strokeWidth="2" rx="5" />
          <text x="170" y="265" textAnchor="middle" fill="white" fontSize="11" fontWeight="bold">
            Whale
          </text>

          <rect x="230" y="240" width="90" height="40" fill="#1f2937" stroke="#10b981" strokeWidth="2" rx="5" />
          <text x="275" y="265" textAnchor="middle" fill="white" fontSize="11" fontWeight="bold">
            Macro
          </text>

          <rect x="335" y="240" width="90" height="40" fill="#1f2937" stroke="#10b981" strokeWidth="2" rx="5" />
          <text x="380" y="265" textAnchor="middle" fill="white" fontSize="11" fontWeight="bold">
            News
          </text>

          <rect x="180" y="340" width="240" height="40" fill="#1f2937" stroke="#f59e0b" strokeWidth="2" rx="5" />
          <text x="300" y="365" textAnchor="middle" fill="white" fontSize="12" fontWeight="bold">
            Event Bus
          </text>

          <line x1="110" y1="70" x2="230" y2="20" stroke="#3b82f6" strokeWidth="2" markerEnd="url(#arrowblue)" />
          <line x1="290" y1="70" x2="290" y2="120" stroke="#3b82f6" strokeWidth="2" markerEnd="url(#arrowblue)" />
          <line x1="230" y1="145" x2="170" y2="145" stroke="#8b5cf6" strokeWidth="2" markerEnd="url(#arrowpurple)" />
          <line x1="290" y1="170" x2="290" y2="240" stroke="#8b5cf6" strokeWidth="2" markerEnd="url(#arrowpurple)" />
          <line x1="65" y1="280" x2="210" y2="340" stroke="#10b981" strokeWidth="2" markerEnd="url(#arrowgreen)" />
          <line x1="170" y1="280" x2="240" y2="340" stroke="#10b981" strokeWidth="2" markerEnd="url(#arrowgreen)" />
          <line x1="275" y1="280" x2="290" y2="340" stroke="#10b981" strokeWidth="2" markerEnd="url(#arrowgreen)" />
          <line x1="380" y1="280" x2="350" y2="340" stroke="#10b981" strokeWidth="2" markerEnd="url(#arrowgreen)" />

          <defs>
            <marker id="arrowblue" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
              <path d="M0,0 L0,6 L9,3 z" fill="#3b82f6" />
            </marker>
            <marker id="arrowpurple" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
              <path d="M0,0 L0,6 L9,3 z" fill="#8b5cf6" />
            </marker>
            <marker id="arrowgreen" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
              <path d="M0,0 L0,6 L9,3 z" fill="#10b981" />
            </marker>
          </defs>
        </svg>
      </div>

      {metrics ? (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
          <div className="bg-gray-900 p-4 rounded">
            <p className="text-gray-400 text-sm">Response Time</p>
            <p className="text-2xl font-bold text-blue-400">{metrics.response_time.toFixed(2)}s</p>
          </div>
          <div className="bg-gray-900 p-4 rounded">
            <p className="text-gray-400 text-sm">Agent Processing</p>
            <p className="text-2xl font-bold text-purple-400">{metrics.agent_processing.toFixed(2)}s</p>
          </div>
          <div className="bg-gray-900 p-4 rounded">
            <p className="text-gray-400 text-sm">LLM Generation</p>
            <p className="text-2xl font-bold text-pink-400">{metrics.llm_generation.toFixed(2)}s</p>
          </div>
          <div className="bg-gray-900 p-4 rounded">
            <p className="text-gray-400 text-sm">Network Latency</p>
            <p className="text-2xl font-bold text-amber-400">{metrics.network_latency.toFixed(2)}s</p>
          </div>
        </div>
      ) : null}

      <div className="bg-gray-900 p-4 rounded">
        <h3 className="text-lg font-bold mb-4">Event Timeline</h3>
        <div className="space-y-2 text-sm">
          <div className="flex gap-4">
            <span className="font-mono text-green-400 w-20">00:00</span>
            <span>User sends command: &quot;analyze INFY&quot;</span>
          </div>
          <div className="flex gap-4">
            <span className="font-mono text-blue-400 w-20">00:01</span>
            <span>Boss Agent receives request</span>
          </div>
          <div className="flex gap-4">
            <span className="font-mono text-purple-400 w-20">00:02</span>
            <span>Technical Agent starts analysis</span>
          </div>
          <div className="flex gap-4">
            <span className="font-mono text-pink-400 w-20">00:03</span>
            <span>Ollama LLM generating response...</span>
          </div>
          <div className="flex gap-4">
            <span className="font-mono text-amber-400 w-20">00:04</span>
            <span>Response sent to dashboard</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// Back-compat for existing import in App.tsx
export const AgentAnimation = AgentAnimationView;


--- END FILE: trading-dashboard\frontend\src\components\AgentAnimation.tsx ---

--- START FILE: trading-dashboard\frontend\src\components\AgentMonitor.tsx ---
import React, { useEffect, useState } from 'react';

interface AgentState {
  agent_id: string;
  status: string;
  task: string;
  progress: number;
}

export function AgentMonitor() {
  const [agents, setAgents] = useState<Record<string, AgentState>>({});

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/agent-monitor`);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.agent_id) {
        setAgents((prev) => ({ ...prev, [data.agent_id]: data }));
      }
    };
    return () => ws.close();
  }, []);

  return (
    <div className="space-y-2">
      <div className="text-xs uppercase tracking-wider text-gray-400 font-semibold">Agent Monitor</div>
      {Object.values(agents).length === 0 ? <div className="text-gray-500 text-sm">No agents online</div> : null}
      {Object.values(agents).map((a) => (
        <div key={a.agent_id} className="bg-gray-900 border border-gray-800 rounded p-3">
          <div className="flex items-center justify-between gap-2">
            <div className="font-semibold text-sm">{a.agent_id}</div>
            <div className="text-xs text-gray-300">{a.status}</div>
          </div>
          <div className="text-xs text-gray-400 mt-1">{a.task}</div>
          <div className="mt-2 h-1 bg-gray-800 rounded overflow-hidden">
            <div className="h-full bg-blue-500" style={{ width: `${Math.max(0, Math.min(100, a.progress || 0))}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}

--- END FILE: trading-dashboard\frontend\src\components\AgentMonitor.tsx ---

--- START FILE: trading-dashboard\frontend\src\components\BacktestingPage.tsx ---
import React, { useState } from 'react';
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

const API_URL = '';

interface BacktestResult {
  total_trades: number;
  win_rate: number;
  profit_factor: number;
  sharpe: number;
  max_dd: number;
  net_pnl: number;
  equity_curve: Array<{ date: string; value: number }>;
  trades: Array<{ entry_date: string; exit_date: string; entry_price: number; profit: number }>;
}

export function BacktestingPage() {
  const [config, setConfig] = useState({
    strategy: 'ema_cross',
    symbol: 'INFY',
    timeframe: '4h',
    from_date: '2026-01-01',
    to_date: '2026-05-21',
    capital: '100000',
  });

  const [result, setResult] = useState<BacktestResult | null>(null);
  const [loading, setLoading] = useState(false);

  const safeJson = async (res: Response) => {
    const text = await res.text();
    try {
      return text ? JSON.parse(text) : {};
    } catch {
      return { raw: text };
    }
  };

  const handleRunBacktest = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/backtest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });
      const data = await safeJson(res);
      if (!res.ok) throw new Error(String(data?.detail || data?.raw || `HTTP ${res.status}`));
      setResult(data as BacktestResult);
    } catch (error) {
      console.error('Backtest error:', error);
      alert('Backtest failed');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    if (!result) return;
    const csv = [
      ['Entry Date', 'Exit Date', 'Entry Price', 'Profit'],
      ...(result.trades || []).map((t) => [t.entry_date, t.exit_date, String(t.entry_price), String(t.profit)]),
    ]
      .map((row) => row.join(','))
      .join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `backtest_${config.symbol}.csv`;
    a.click();
  };

  return (
    <div className="p-6 bg-black text-white">
      <h1 className="text-3xl font-bold mb-6">Backtesting Engine</h1>

      <section className="mb-8 bg-gray-900 p-6 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Configuration</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm mb-2">Strategy</label>
            <select
              value={config.strategy}
              onChange={(e) => setConfig({ ...config, strategy: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
            >
              <option value="ema_cross">EMA Crossover</option>
              <option value="rsi_oversold">RSI Oversold</option>
              <option value="macd_momentum">MACD Momentum</option>
            </select>
          </div>
          <div>
            <label className="block text-sm mb-2">Symbol</label>
            <input
              type="text"
              value={config.symbol}
              onChange={(e) => setConfig({ ...config, symbol: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm mb-2">From Date</label>
            <input
              type="date"
              value={config.from_date}
              onChange={(e) => setConfig({ ...config, from_date: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm mb-2">To Date</label>
            <input
              type="date"
              value={config.to_date}
              onChange={(e) => setConfig({ ...config, to_date: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
            />
          </div>
        </div>
        <button
          onClick={handleRunBacktest}
          disabled={loading}
          className="mt-6 w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-bold py-2 rounded"
        >
          {loading ? 'Running...' : 'Run Backtest'}
        </button>
      </section>

      {result ? (
        <section>
          <h2 className="text-xl font-bold mb-4">Results</h2>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
            <div className="bg-gray-900 p-4 rounded">
              <p className="text-gray-400 text-sm">Total Trades</p>
              <p className="text-2xl font-bold">{result.total_trades}</p>
            </div>
            <div className="bg-gray-900 p-4 rounded">
              <p className="text-gray-400 text-sm">Win Rate</p>
              <p className="text-2xl font-bold text-green-400">{result.win_rate}%</p>
            </div>
            <div className="bg-gray-900 p-4 rounded">
              <p className="text-gray-400 text-sm">Net P&amp;L</p>
              <p className={`text-2xl font-bold ${result.net_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {result.net_pnl >= 0 ? '+' : ''}
                {Number(result.net_pnl).toFixed(0)}
              </p>
            </div>
          </div>

          <div className="bg-gray-900 p-4 rounded mb-6">
            <h3 className="text-lg font-semibold mb-4">Equity Curve</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={result.equity_curve || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                <XAxis dataKey="date" stroke="#888" />
                <YAxis stroke="#888" />
                <Tooltip contentStyle={{ backgroundColor: '#1a1a1a' }} />
                <Line type="monotone" dataKey="value" stroke="#3b82f6" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-gray-900 p-4 rounded">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Trade List</h3>
              <button onClick={handleExport} className="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-sm">
                Export CSV
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="border-b border-gray-700">
                  <tr>
                    <th className="px-2 py-2 text-left">Entry Date</th>
                    <th className="px-2 py-2 text-left">Exit Date</th>
                    <th className="px-2 py-2 text-right">Entry Price</th>
                    <th className="px-2 py-2 text-right">Profit</th>
                  </tr>
                </thead>
                <tbody>
                  {(result.trades || []).slice(0, 10).map((trade, idx) => (
                    <tr key={idx} className="border-b border-gray-800">
                      <td className="px-2 py-2">{trade.entry_date}</td>
                      <td className="px-2 py-2">{trade.exit_date}</td>
                      <td className="px-2 py-2 text-right">₹{trade.entry_price}</td>
                      <td className={`px-2 py-2 text-right ${trade.profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {trade.profit >= 0 ? '+' : ''}
                        {trade.profit}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      ) : null}
    </div>
  );
}


--- END FILE: trading-dashboard\frontend\src\components\BacktestingPage.tsx ---

--- START FILE: trading-dashboard\frontend\src\components\ChatInterface.tsx ---
import React, { useState } from 'react';

const API_URL = '';

export function ChatInterface() {
  const [message, setMessage] = useState('');
  const [history, setHistory] = useState<Array<{ role: string; content: string }>>([]);
  const [loading, setLoading] = useState(false);

  const safeJson = async (res: Response): Promise<any> => {
    const text = await res.text();
    try {
      return text ? JSON.parse(text) : {};
    } catch {
      return { raw: text };
    }
  };

  const pollResponse = async (commandId: string, attempts = 240): Promise<string> => {
    for (let i = 0; i < attempts; i += 1) {
      try {
        const res = await fetch(`${API_URL}/chat/response/${commandId}`);
        const data = await safeJson(res);
        if (data.status === 'done' && data.response) return data.response;
      } catch {
        // transient poll failure
      }
      await new Promise((r) => setTimeout(r, 500));
    }
    return 'Agent timed out. Please retry.';
  };

  const sendMessage = async () => {
    if (!message.trim()) return;
    const userMessage = message;
    setMessage('');
    setLoading(true);
    setHistory((p) => [...p, { role: 'user', content: userMessage }, { role: 'assistant', content: 'Agent Processing...' }]);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: userMessage }),
      });
      const data = await safeJson(res);
      if (!res.ok || !data.command_id) {
        const detail = data?.detail || data?.raw || `HTTP ${res.status}`;
        throw new Error(String(detail));
      }
      const ans = await pollResponse(data.command_id);
      setHistory((p) => {
        const n = [...p];
        n[n.length - 1] = { role: 'assistant', content: ans };
        return n;
      });
    } catch (err: any) {
      setHistory((p) => {
        const n = [...p];
        n[n.length - 1] = { role: 'assistant', content: `Error sending message: ${err?.message || 'Unknown error'}` };
        return n;
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-black text-white">
      <h1 className="text-3xl font-bold mb-6">Chat</h1>
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 mb-4 min-h-[320px]">
        {history.length === 0 ? (
          <div className="text-gray-400 text-sm">Type a message to send it to the Boss Agent.</div>
        ) : null}
        <div className="space-y-3">
          {history.map((m, i) => (
            <div key={i} className="text-sm">
              <div className={`font-semibold ${m.role === 'user' ? 'text-blue-300' : 'text-green-300'}`}>
                {m.role === 'user' ? 'You' : 'Agent'}
              </div>
              <div className="text-gray-100 whitespace-pre-wrap">{m.content}</div>
            </div>
          ))}
        </div>
      </div>
      <div className="flex gap-2">
        <input
          className="flex-1 bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !loading && sendMessage()}
          placeholder="Ask: analyze INFY, backtest BTC, generate PineScript strategy..."
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 rounded font-semibold"
        >
          {loading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  );
}

--- END FILE: trading-dashboard\frontend\src\components\ChatInterface.tsx ---

--- START FILE: trading-dashboard\frontend\src\components\ErrorBoundary.tsx ---
import React from 'react';

type Props = { children: React.ReactNode };
type State = { hasError: boolean };

export class ErrorBoundary extends React.Component<Props, State> {
  state: State = { hasError: false };

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Frontend error', { error, errorInfo });
    this.setState({ hasError: true });
  }

  render() {
    if (this.state.hasError) {
      return <div style={{ padding: 24, color: '#fff', background: '#111' }}>Something went wrong. Check logs.</div>;
    }
    return this.props.children;
  }
}

--- END FILE: trading-dashboard\frontend\src\components\ErrorBoundary.tsx ---

--- START FILE: trading-dashboard\frontend\src\components\OverviewPage.tsx ---
import React, { useEffect, useMemo, useState } from 'react';

const API_URL = '';

type Portfolio = {
  total_value: number;
  total_pnl: number;
  total_pnl_pct: number;
  open_positions: number;
};

type SystemHealth = {
  timestamp: string;
  ollama_status: string;
  broker_status: string;
  agents_online: number;
  alert_cooldown_seconds: number;
};

type WatchlistItem = {
  id: string;
  symbol: string;
  strategy_id: string;
  auto_trade: boolean;
  status: string;
};

type TradeSignal = {
  id: string;
  symbol: string;
  approval_status: string;
  signal_price?: number;
  signal_time?: string;
  overall_score?: number;
  technical_score?: number;
  news_score?: number;
  fundamental_score?: number;
  risk_score?: number;
};

export function OverviewPage() {
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [signals, setSignals] = useState<TradeSignal[]>([]);
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);

  const safeJson = async (res: Response) => {
    const text = await res.text();
    try {
      return text ? JSON.parse(text) : {};
    } catch {
      return { raw: text };
    }
  };

  const refresh = async () => {
    setLoading(true);
    try {
      const [wRes, sRes, pRes, hRes] = await Promise.all([
        fetch(`${API_URL}/api/watchlist`),
        fetch(`${API_URL}/api/signals/pending`),
        fetch(`${API_URL}/api/portfolio`),
        fetch(`${API_URL}/api/system/health`),
      ]);
      const [w, s, p, h] = await Promise.all([safeJson(wRes), safeJson(sRes), safeJson(pRes), safeJson(hRes)]);
      setWatchlist(Array.isArray(w) ? w : []);
      setSignals(Array.isArray(s) ? s : []);
      setPortfolio(p && typeof p === 'object' ? (p as Portfolio) : null);
      setHealth(h && typeof h === 'object' ? (h as SystemHealth) : null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 10000);
    return () => clearInterval(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const metrics = useMemo(() => {
    const pending = signals.length;
    return {
      watchCount: watchlist.filter((i) => i.status !== 'removed').length,
      pendingSignals: pending,
    };
  }, [signals, watchlist]);

  return (
    <div className="p-6 bg-black text-white">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Overview</h1>
        <button onClick={refresh} className="px-3 py-2 bg-gray-900 hover:bg-gray-800 rounded text-sm font-semibold">
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-8">
        <div className="bg-gray-900 p-4 rounded border border-gray-800">
          <div className="text-gray-400 text-sm">Active Watches</div>
          <div className="text-2xl font-bold">{metrics.watchCount}</div>
        </div>
        <div className="bg-gray-900 p-4 rounded border border-gray-800">
          <div className="text-gray-400 text-sm">Pending Signals</div>
          <div className="text-2xl font-bold text-yellow-300">{metrics.pendingSignals}</div>
        </div>
        <div className="bg-gray-900 p-4 rounded border border-gray-800">
          <div className="text-gray-400 text-sm">Portfolio Value</div>
          <div className="text-2xl font-bold">₹{(portfolio?.total_value || 0).toFixed(0)}</div>
        </div>
        <div className="bg-gray-900 p-4 rounded border border-gray-800">
          <div className="text-gray-400 text-sm">Total P&amp;L</div>
          <div className={`text-2xl font-bold ${(portfolio?.total_pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {(portfolio?.total_pnl || 0) >= 0 ? '+' : ''}
            {(portfolio?.total_pnl || 0).toFixed(0)} ({(portfolio?.total_pnl_pct || 0).toFixed(2)}%)
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-900 rounded-lg border border-gray-800 overflow-hidden">
          <div className="px-4 py-3 bg-gray-800 font-semibold">Action Required</div>
          <div className="p-4">
            {signals.length === 0 ? (
              <div className="text-gray-400 text-sm">No pending signals right now.</div>
            ) : (
              <div className="space-y-3">
                {signals.slice(0, 5).map((s) => (
                  <div key={s.id} className="p-3 rounded bg-black/30 border border-gray-800">
                    <div className="flex items-center justify-between">
                      <div className="font-semibold">{s.symbol}</div>
                      <div className="text-xs text-gray-400">{s.approval_status}</div>
                    </div>
                    <div className="text-sm text-gray-300 mt-1">
                      Price: ₹{Number(s.signal_price || 0).toFixed(2)} | Score: {Number(s.overall_score || 0).toFixed(0)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="bg-gray-900 rounded-lg border border-gray-800 overflow-hidden">
          <div className="px-4 py-3 bg-gray-800 font-semibold">System Health</div>
          <div className="p-4 space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Agents Online</span>
              <span className="font-semibold">{health?.agents_online ?? 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Broker Status</span>
              <span className="font-semibold">{health?.broker_status ?? 'unknown'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Ollama Status</span>
              <span className="font-semibold">{health?.ollama_status ?? 'unknown'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Telegram Cooldown</span>
              <span className="font-semibold">{health?.alert_cooldown_seconds ?? 60}s</span>
            </div>
            <div className="text-xs text-gray-500 mt-3">Updated: {health?.timestamp || '—'}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

--- END FILE: trading-dashboard\frontend\src\components\OverviewPage.tsx ---

--- START FILE: trading-dashboard\frontend\src\components\PortfolioPage.tsx ---
import React, { useEffect, useState } from 'react';

const API_URL = '';

type Portfolio = {
  total_value: number;
  total_pnl: number;
  total_pnl_pct: number;
  open_positions: number;
};

export function PortfolioPage() {
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [loading, setLoading] = useState(true);

  const safeJson = async (res: Response) => {
    const text = await res.text();
    try {
      return text ? JSON.parse(text) : {};
    } catch {
      return { raw: text };
    }
  };

  const refresh = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/portfolio`);
      const data = await safeJson(res);
      setPortfolio(data && typeof data === 'object' ? (data as Portfolio) : null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 10000);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="p-6 bg-black text-white">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Portfolio</h1>
        <button onClick={refresh} className="px-3 py-2 bg-gray-900 hover:bg-gray-800 rounded text-sm font-semibold">
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="bg-gray-900 border border-gray-800 rounded p-4">
          <div className="text-gray-400 text-sm">Total Value</div>
          <div className="text-2xl font-bold">₹{Number(portfolio?.total_value || 0).toFixed(0)}</div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded p-4">
          <div className="text-gray-400 text-sm">Open Positions</div>
          <div className="text-2xl font-bold">{portfolio?.open_positions ?? 0}</div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded p-4">
          <div className="text-gray-400 text-sm">PnL</div>
          <div className={`text-2xl font-bold ${(portfolio?.total_pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {(portfolio?.total_pnl || 0) >= 0 ? '+' : ''}
            {Number(portfolio?.total_pnl || 0).toFixed(0)}
          </div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded p-4">
          <div className="text-gray-400 text-sm">PnL %</div>
          <div className={`text-2xl font-bold ${(portfolio?.total_pnl_pct || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {(portfolio?.total_pnl_pct || 0) >= 0 ? '+' : ''}
            {Number(portfolio?.total_pnl_pct || 0).toFixed(2)}%
          </div>
        </div>
      </div>

      <div className="mt-6 text-gray-400 text-sm">
        This page uses `GET /api/portfolio` which is derived from active positions. If you want true broker balances and
        holdings, we can wire the broker SDK next.
      </div>
    </div>
  );
}

--- END FILE: trading-dashboard\frontend\src\components\PortfolioPage.tsx ---

--- START FILE: trading-dashboard\frontend\src\components\SettingsPage.tsx ---
import React, { useEffect, useState } from 'react';

const API_URL = '';

type Settings = {
  broker?: string;
  api_key?: string;
  api_secret?: string;
  trading_mode?: 'paper' | 'live';
  max_position_size?: number;
  max_daily_loss?: number;
  max_correlation?: number;
  ollama_model?: string;
  ollama_url?: string;
  telegram_enabled?: boolean;
  telegram_bot_token?: string;
  telegram_chat_id?: string;
};

export function SettingsPage() {
  const [settings, setSettings] = useState<Settings>({
    broker: 'upstox',
    trading_mode: 'paper',
    max_position_size: 5,
    max_daily_loss: 2,
    max_correlation: 0.7,
    ollama_model: 'qwen2.5:3b',
    ollama_url: 'http://localhost:11434',
    telegram_enabled: true,
    telegram_bot_token: '',
    telegram_chat_id: '',
  });

  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(true);
  const [killEnabled, setKillEnabled] = useState<boolean | null>(null);
  const [adminKey, setAdminKey] = useState<string>(() => localStorage.getItem('admin_api_key') || '');
  const [dashboardToken, setDashboardToken] = useState<string>(() => localStorage.getItem('dashboard_jwt') || '');
  const [loginUsername, setLoginUsername] = useState<string>('admin');
  const [loginPassword, setLoginPassword] = useState<string>('');
  const [killBusy, setKillBusy] = useState(false);

  const safeJson = async (res: Response) => {
    const text = await res.text();
    try {
      return text ? JSON.parse(text) : {};
    } catch {
      return { raw: text };
    }
  };

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API_URL}/settings`);
        const data = await safeJson(res);
        if (res.ok && data && typeof data === 'object') {
          setSettings((prev) => ({ ...prev, ...data }));
        }

        const ks = await fetch(`${API_URL}/api/kill-switch`);
        const ksData = await safeJson(ks);
        if (ks.ok && typeof ksData?.trading_enabled === 'boolean') {
          setKillEnabled(ksData.trading_enabled);
        }
      } catch {
        // ignore; keep defaults
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  useEffect(() => {
    localStorage.setItem('admin_api_key', adminKey);
  }, [adminKey]);

  useEffect(() => {
    localStorage.setItem('dashboard_jwt', dashboardToken);
  }, [dashboardToken]);

  const authHeaders = (): Record<string, string> => {
    if (dashboardToken) {
      return { Authorization: `Bearer ${dashboardToken}` };
    }
    if (adminKey) {
      return { 'X-Admin-Key': adminKey };
    }
    return {};
  };

  const handleLogin = async () => {
    try {
      const form = new URLSearchParams();
      form.append('username', loginUsername);
      form.append('password', loginPassword);
      const res = await fetch(`${API_URL}/login`, {
        method: 'POST',
        body: form,
      });
      const data = await safeJson(res);
      if (!res.ok) {
        throw new Error(String(data?.detail || data?.raw || `HTTP ${res.status}`));
      }
      if (data?.access_token) {
        setDashboardToken(String(data.access_token));
        setLoginPassword('');
        alert('JWT login successful');
      } else {
        throw new Error('Login response missing access_token');
      }
    } catch (error) {
      console.error('Login failed:', error);
      alert('Login failed');
    }
  };

  const handleLogout = () => {
    setDashboardToken('');
    localStorage.removeItem('dashboard_jwt');
  };

  const toggleKillSwitch = async (enabled: boolean) => {
    setKillBusy(true);
    try {
      const res = await fetch(`${API_URL}/api/kill-switch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...authHeaders(),
        },
        body: JSON.stringify({ enabled }),
      });
      const data = await safeJson(res);
      if (!res.ok) {
        throw new Error(String(data?.detail || data?.raw || `HTTP ${res.status}`));
      }
      setKillEnabled(Boolean(data?.trading_enabled));
    } catch (error) {
      console.error('Kill switch update failed:', error);
      alert('Kill switch update failed (check JWT login / auth settings).');
    } finally {
      setKillBusy(false);
    }
  };

  const handleSave = async () => {
    try {
      const res = await fetch(`${API_URL}/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings),
      });
      if (!res.ok) {
        const data = await safeJson(res);
        throw new Error(String(data?.detail || data?.raw || `HTTP ${res.status}`));
      }
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('Error saving settings');
    }
  };

  const handleTestConnection = async () => {
    try {
      const url = `${settings.ollama_url || 'http://localhost:11434'}/api/version`;
      const res = await fetch(url);
      if (res.ok) {
        alert('Ollama connection successful!');
      } else {
        alert('Cannot reach Ollama server from the browser.');
      }
    } catch {
      alert('Connection failed. Note: cloud dashboard cannot reach your local Ollama URL.');
    }
  };

  const handleTelegramTest = async () => {
    try {
      const res = await fetch(`${API_URL}/alerts/buy-signal`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol: 'TEST', signal: 'buy' }),
      });
      const data = await safeJson(res);
      alert(`Telegram test: ${data?.status || 'unknown'}`);
    } catch {
      alert('Telegram test failed');
    }
  };

  return (
    <div className="p-6 bg-black text-white">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Settings</h1>
        {loading ? <div className="text-gray-400 text-sm">Loading...</div> : null}
      </div>

      <section className="mb-8 bg-gray-900 p-6 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Broker API Keys</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm mb-2">Broker</label>
            <select
              value={settings.broker || 'upstox'}
              onChange={(e) => setSettings({ ...settings, broker: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
            >
              <option value="upstox">Upstox</option>
              <option value="binance">Binance</option>
              <option value="alpaca">Alpaca</option>
            </select>
          </div>
          <div />

          <div>
            <label className="block text-sm mb-2">API Key</label>
            <input
              type="password"
              value={settings.api_key || ''}
              onChange={(e) => setSettings({ ...settings, api_key: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
              placeholder="***masked***"
            />
          </div>
          <div>
            <label className="block text-sm mb-2">API Secret</label>
            <input
              type="password"
              value={settings.api_secret || ''}
              onChange={(e) => setSettings({ ...settings, api_secret: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
              placeholder="***masked***"
            />
          </div>
        </div>
      </section>

      <section className="mb-8 bg-gray-900 p-6 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Trading Mode</h2>
        <div className="space-y-3">
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="radio"
              name="mode"
              value="paper"
              checked={(settings.trading_mode || 'paper') === 'paper'}
              onChange={(e) => setSettings({ ...settings, trading_mode: e.target.value as 'paper' | 'live' })}
            />
            <span>Paper Trading (Safe for testing)</span>
          </label>
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="radio"
              name="mode"
              value="live"
              checked={(settings.trading_mode || 'paper') === 'live'}
              onChange={(e) => setSettings({ ...settings, trading_mode: e.target.value as 'paper' | 'live' })}
            />
            <span className="text-red-400">LIVE TRADING (Real money)</span>
          </label>
        </div>
      </section>

      <section className="mb-8 bg-gray-900 p-6 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Dashboard Login</h2>
        <div className="text-sm text-gray-400 mb-3">
          Sign in with a dashboard user to receive a JWT for admin actions. The legacy admin key still works as a fallback.
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm mb-2">Username</label>
            <input
              type="text"
              value={loginUsername}
              onChange={(e) => setLoginUsername(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
              placeholder="admin"
            />
          </div>
          <div>
            <label className="block text-sm mb-2">Password</label>
            <input
              type="password"
              value={loginPassword}
              onChange={(e) => setLoginPassword(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
              placeholder="••••••••"
            />
          </div>
        </div>
        <div className="mt-4 flex flex-wrap gap-2 items-center">
          <button onClick={handleLogin} className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 text-sm">
            Login
          </button>
          <button onClick={handleLogout} className="px-4 py-2 bg-gray-700 rounded hover:bg-gray-600 text-sm">
            Logout
          </button>
          <div className="text-sm text-gray-400">
            {dashboardToken ? 'JWT active' : 'No JWT stored'}
          </div>
        </div>
      </section>

      <section className="mb-8 bg-gray-900 p-6 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Kill Switch</h2>
        <div className="text-sm text-gray-400 mb-3">
          Use the dashboard JWT first. If needed, the legacy `ADMIN_API_KEY` fallback still works.
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm mb-2">Legacy Admin Key (X-Admin-Key)</label>
            <input
              type="password"
              value={adminKey}
              onChange={(e) => setAdminKey(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
              placeholder="Legacy fallback"
            />
          </div>
          <div className="flex items-end gap-2">
            <button
              disabled={killBusy}
              onClick={() => toggleKillSwitch(true)}
              className="px-4 py-2 bg-green-600 rounded hover:bg-green-700 disabled:bg-gray-700"
            >
              Enable
            </button>
            <button
              disabled={killBusy}
              onClick={() => toggleKillSwitch(false)}
              className="px-4 py-2 bg-red-600 rounded hover:bg-red-700 disabled:bg-gray-700"
            >
              Disable
            </button>
            <div className="text-sm font-semibold">
              {killEnabled === null ? 'Unknown' : killEnabled ? 'ACTIVE' : 'DISABLED'}
            </div>
          </div>
        </div>
      </section>

      <section className="mb-8 bg-gray-900 p-6 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Risk Parameters</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm mb-2">Max Position Size (%)</label>
            <input
              type="number"
              value={settings.max_position_size ?? 5}
              onChange={(e) => setSettings({ ...settings, max_position_size: parseFloat(e.target.value) })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm mb-2">Max Daily Loss (%)</label>
            <input
              type="number"
              value={settings.max_daily_loss ?? 2}
              onChange={(e) => setSettings({ ...settings, max_daily_loss: parseFloat(e.target.value) })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm mb-2">Max Correlation</label>
            <input
              type="number"
              step="0.01"
              value={settings.max_correlation ?? 0.7}
              onChange={(e) => setSettings({ ...settings, max_correlation: parseFloat(e.target.value) })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
            />
          </div>
        </div>
      </section>

      <section className="mb-8 bg-gray-900 p-6 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Ollama LLM Configuration</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm mb-2">Model</label>
            <select
              value={settings.ollama_model || 'qwen2.5:3b'}
              onChange={(e) => setSettings({ ...settings, ollama_model: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
            >
              <option value="qwen2.5:3b">qwen2.5:3b (Fast)</option>
              <option value="deepseek-r1:7b">deepseek-r1:7b (Reasoning)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm mb-2">Server URL</label>
            <input
              type="text"
              value={settings.ollama_url || 'http://localhost:11434'}
              onChange={(e) => setSettings({ ...settings, ollama_url: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
            />
          </div>
        </div>
        <button onClick={handleTestConnection} className="mt-4 px-4 py-2 bg-green-600 rounded hover:bg-green-700 text-sm">
          Test Connection
        </button>
        <div className="mt-2 text-xs text-gray-400">
          Note: the Render-hosted dashboard cannot reach your laptop's `localhost`. This test is useful only when running the
          frontend locally.
        </div>
      </section>

      <section className="mb-8 bg-gray-900 p-6 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Telegram Notifications</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm mb-2">Enabled</label>
            <select
              value={String(settings.telegram_enabled ?? true)}
              onChange={(e) => setSettings({ ...settings, telegram_enabled: e.target.value === 'true' })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
            >
              <option value="true">Enabled</option>
              <option value="false">Disabled</option>
            </select>
          </div>
          <div />

          <div>
            <label className="block text-sm mb-2">Bot Token</label>
            <input
              type="password"
              value={settings.telegram_bot_token || ''}
              onChange={(e) => setSettings({ ...settings, telegram_bot_token: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
              placeholder="***masked***"
            />
          </div>
          <div>
            <label className="block text-sm mb-2">Chat ID</label>
            <input
              type="text"
              value={settings.telegram_chat_id || ''}
              onChange={(e) => setSettings({ ...settings, telegram_chat_id: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
              placeholder="123456789"
            />
          </div>
        </div>
        <button onClick={handleTelegramTest} className="mt-4 px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 text-sm">
          Test Telegram
        </button>
        <div className="mt-2 text-xs text-gray-400">
          Buy alerts have a 60 second cooldown per symbol (configured by `TELEGRAM_ALERT_COOLDOWN_SECONDS`).
        </div>
      </section>

      <button
        onClick={handleSave}
        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 rounded"
      >
        {saved ? 'Saved!' : 'Save Settings'}
      </button>
    </div>
  );
}

--- END FILE: trading-dashboard\frontend\src\components\SettingsPage.tsx ---

--- START FILE: trading-dashboard\frontend\src\components\SignalsPage.tsx ---
import React, { useEffect, useMemo, useState } from 'react';

const API_URL = '';

type TradeSignal = {
  id: string;
  symbol: string;
  approval_status: 'pending' | 'approved' | 'rejected' | string;
  signal_price?: number;
  signal_time?: string;
  technical_score?: number;
  news_score?: number;
  fundamental_score?: number;
  risk_score?: number;
  overall_score?: number;
};

export function SignalsPage() {
  const [signals, setSignals] = useState<TradeSignal[]>([]);
  const [loading, setLoading] = useState(true);
  const [approving, setApproving] = useState<string | null>(null);
  const [skipping, setSkipping] = useState<string | null>(null);

  const safeJson = async (res: Response) => {
    const text = await res.text();
    try {
      return text ? JSON.parse(text) : {};
    } catch {
      return { raw: text };
    }
  };

  const refresh = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/signals/pending`);
      const data = await safeJson(res);
      setSignals(Array.isArray(data) ? data : []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 10000);
    return () => clearInterval(t);
  }, []);

  const approve = async (id: string) => {
    setApproving(id);
    try {
      const res = await fetch(`${API_URL}/api/signal/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ signal_id: id }),
      });
      const data = await safeJson(res);
      if (!res.ok) {
        alert(data?.detail || data?.raw || `HTTP ${res.status}`);
        return;
      }
      await refresh();
    } finally {
      setApproving(null);
    }
  };

  const skip = async (id: string) => {
    setSkipping(id);
    try {
      const res = await fetch(`${API_URL}/api/signal/skip`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ signal_id: id, reason: 'Skipped from dashboard' }),
      });
      const data = await safeJson(res);
      if (!res.ok) {
        alert(data?.detail || data?.raw || `HTTP ${res.status}`);
        return;
      }
      await refresh();
    } finally {
      setSkipping(null);
    }
  };

  const summary = useMemo(() => {
    const pending = signals.length;
    const avg = pending ? signals.reduce((a, s) => a + Number(s.overall_score || 0), 0) / pending : 0;
    return { pending, avg };
  }, [signals]);

  return (
    <div className="p-6 bg-black text-white">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Signals</h1>
        <button onClick={refresh} className="px-3 py-2 bg-gray-900 hover:bg-gray-800 rounded text-sm font-semibold">
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div className="bg-gray-900 border border-gray-800 rounded p-4">
          <div className="text-gray-400 text-sm">Pending</div>
          <div className="text-2xl font-bold text-yellow-300">{summary.pending}</div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded p-4">
          <div className="text-gray-400 text-sm">Avg Score</div>
          <div className="text-2xl font-bold">{summary.avg.toFixed(0)}%</div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded p-4">
          <div className="text-gray-400 text-sm">Auto-trading</div>
          <div className="text-sm text-gray-300 mt-1">
            Approval updates status now. Execution wiring can be added next (paper broker).
          </div>
        </div>
      </div>

      <div className="bg-gray-900 rounded-lg overflow-hidden border border-gray-800">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-800 border-b border-gray-700">
              <tr>
                <th className="px-4 py-3 text-left">Symbol</th>
                <th className="px-4 py-3 text-left">Status</th>
                <th className="px-4 py-3 text-right">Price</th>
                <th className="px-4 py-3 text-right">Tech</th>
                <th className="px-4 py-3 text-right">News</th>
                <th className="px-4 py-3 text-right">Fund</th>
                <th className="px-4 py-3 text-right">Risk</th>
                <th className="px-4 py-3 text-right">Overall</th>
                <th className="px-4 py-3 text-center">Action</th>
              </tr>
            </thead>
            <tbody>
              {signals.map((s) => (
                <tr key={s.id} className="border-b border-gray-800 hover:bg-gray-800/60">
                  <td className="px-4 py-3 font-semibold">{s.symbol}</td>
                  <td className="px-4 py-3 text-yellow-200">{s.approval_status}</td>
                  <td className="px-4 py-3 text-right">₹{Number(s.signal_price || 0).toFixed(2)}</td>
                  <td className="px-4 py-3 text-right">{Number(s.technical_score || 0).toFixed(0)}</td>
                  <td className="px-4 py-3 text-right">{Number(s.news_score || 0).toFixed(0)}</td>
                  <td className="px-4 py-3 text-right">{Number(s.fundamental_score || 0).toFixed(0)}</td>
                  <td className="px-4 py-3 text-right">{Number(s.risk_score || 0).toFixed(0)}</td>
                  <td className="px-4 py-3 text-right font-semibold">{Number(s.overall_score || 0).toFixed(0)}</td>
                  <td className="px-4 py-3 text-center">
                    <div className="flex items-center justify-center gap-2">
                      <button
                        disabled={approving === s.id}
                        onClick={() => approve(s.id)}
                        className="px-3 py-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 rounded text-sm font-semibold"
                      >
                        {approving === s.id ? 'Approving...' : 'Approve'}
                      </button>
                      <button
                        disabled={skipping === s.id}
                        onClick={() => skip(s.id)}
                        className="px-3 py-1 bg-gray-800 hover:bg-gray-700 disabled:bg-gray-700 rounded text-sm font-semibold"
                      >
                        {skipping === s.id ? 'Skipping...' : 'Skip'}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {signals.length === 0 && !loading ? <div className="p-6 text-center text-gray-400">No pending signals</div> : null}
      </div>
    </div>
  );
}

--- END FILE: trading-dashboard\frontend\src\components\SignalsPage.tsx ---

--- START FILE: trading-dashboard\frontend\src\components\StockScreener.tsx ---
import React, { useEffect, useMemo, useState } from 'react';

const API_URL = '';

interface ScreenerResult {
  rank: number;
  symbol: string;
  price: number;
  change_pct: number;
  pnl_pct: number;
  signal: 'buy' | 'sell' | 'hold';
  timeframe: string;
}

export function StockScreenerPage() {
  const [results, setResults] = useState<ScreenerResult[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchScreenerResults();
    const interval = setInterval(fetchScreenerResults, 30000);
    return () => clearInterval(interval);
  }, []);

  const safeJson = async (res: Response) => {
    const text = await res.text();
    try {
      return text ? JSON.parse(text) : {};
    } catch {
      return { raw: text };
    }
  };

  const fetchScreenerResults = async () => {
    try {
      const res = await fetch(`${API_URL}/screener`);
      const data = await safeJson(res);
      setResults(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error fetching screener:', error);
    } finally {
      setLoading(false);
    }
  };

  const signalColor = (signal: string) => {
    switch (signal) {
      case 'buy':
        return 'text-green-400 bg-green-900';
      case 'sell':
        return 'text-red-400 bg-red-900';
      default:
        return 'text-gray-300 bg-gray-800';
    }
  };

  const summary = useMemo(() => {
    const buy = results.filter((r) => r.signal === 'buy').length;
    const sell = results.filter((r) => r.signal === 'sell').length;
    const hold = results.filter((r) => r.signal === 'hold').length;
    return { buy, sell, hold };
  }, [results]);

  return (
    <div className="p-6 bg-black text-white">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Stock Screener</h1>
        {loading ? <div className="text-gray-400 text-sm">Loading...</div> : null}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div className="bg-green-900 p-4 rounded">
          <p className="text-green-200 text-sm">Buy Signals</p>
          <p className="text-2xl font-bold">{summary.buy}</p>
        </div>
        <div className="bg-red-900 p-4 rounded">
          <p className="text-red-200 text-sm">Sell Signals</p>
          <p className="text-2xl font-bold">{summary.sell}</p>
        </div>
        <div className="bg-gray-900 p-4 rounded">
          <p className="text-gray-300 text-sm">Hold</p>
          <p className="text-2xl font-bold">{summary.hold}</p>
        </div>
      </div>

      <div className="bg-gray-900 rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-800 border-b border-gray-700">
              <tr>
                <th className="px-4 py-3 text-left">#</th>
                <th className="px-4 py-3 text-left">Symbol</th>
                <th className="px-4 py-3 text-right">Price</th>
                <th className="px-4 py-3 text-right">Change%</th>
                <th className="px-4 py-3 text-right">P&amp;L%</th>
                <th className="px-4 py-3 text-left">Signal</th>
                <th className="px-4 py-3 text-left">TF</th>
                <th className="px-4 py-3 text-center">Action</th>
              </tr>
            </thead>
            <tbody>
              {results.map((result) => (
                <tr key={result.symbol} className="border-b border-gray-800 hover:bg-gray-800/60">
                  <td className="px-4 py-3 font-semibold">{result.rank}</td>
                  <td className="px-4 py-3 font-bold">{result.symbol}</td>
                  <td className="px-4 py-3 text-right">₹{Number(result.price).toFixed(2)}</td>
                  <td className={`px-4 py-3 text-right ${result.change_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {result.change_pct >= 0 ? '+' : ''}
                    {Number(result.change_pct).toFixed(2)}%
                  </td>
                  <td className={`px-4 py-3 text-right ${result.pnl_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {result.pnl_pct >= 0 ? '+' : ''}
                    {Number(result.pnl_pct).toFixed(2)}%
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded text-sm font-semibold ${signalColor(result.signal)}`}>
                      {result.signal.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-4 py-3">{result.timeframe}</td>
                  <td className="px-4 py-3 text-center">
                    <button className="px-2 py-1 bg-blue-600 rounded text-sm hover:bg-blue-700">Analyze</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {results.length === 0 && !loading ? (
          <div className="p-6 text-center text-gray-400">No screener results</div>
        ) : null}
      </div>
    </div>
  );
}

// Back-compat for existing import in App.tsx
export const StockScreener = StockScreenerPage;

--- END FILE: trading-dashboard\frontend\src\components\StockScreener.tsx ---

--- START FILE: trading-dashboard\frontend\src\components\StrategiesPage.tsx ---
import React, { useEffect, useMemo, useState } from 'react';
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

const API_URL = '';

interface Strategy {
  id: string;
  name: string;
  symbol: string;
  timeframe: string;
  status: 'running' | 'paused' | 'backtested';
  pnl: number;
  win_rate: number;
  total_trades: number;
  equity_curve: Array<{ date: string; value: number }>;
}

export function StrategiesPage() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [selected, setSelected] = useState<Strategy | null>(null);
  const [showNewForm, setShowNewForm] = useState(false);
  const [creating, setCreating] = useState(false);
  const [newStrategy, setNewStrategy] = useState({
    name: '',
    symbol: 'INFY',
    timeframe: '4h',
    status: 'paused' as 'running' | 'paused' | 'backtested',
    entry_rule: '',
    exit_rule: '',
  });
  const [pineLoading, setPineLoading] = useState(false);
  const [pineScript, setPineScript] = useState('');
  const [pineError, setPineError] = useState<string | null>(null);

  useEffect(() => {
    fetchStrategies();
  }, []);

  const safeJson = async (res: Response) => {
    const text = await res.text();
    try {
      return text ? JSON.parse(text) : {};
    } catch {
      return { raw: text };
    }
  };

  const fetchStrategies = async () => {
    try {
      const res = await fetch(`${API_URL}/strategies`);
      const data = await safeJson(res);
      const list = Array.isArray(data) ? (data as Strategy[]) : [];
      setStrategies(list);
      setSelected(list[0] || null);
    } catch (error) {
      console.error('Error fetching strategies:', error);
      setStrategies([]);
      setSelected(null);
    }
  };

  const sortedStrategies = useMemo(() => {
    return [...strategies].sort((a, b) => (b.pnl || 0) - (a.pnl || 0));
  }, [strategies]);

  const handleDelete = async (id: string) => {
    // eslint-disable-next-line no-restricted-globals
    if (!confirm('Delete this strategy?')) return;
    try {
      await fetch(`${API_URL}/strategy/${encodeURIComponent(id)}`, { method: 'DELETE' });
      await fetchStrategies();
      setSelected(null);
    } catch (error) {
      console.error('Error deleting strategy:', error);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const name = newStrategy.name.trim();
    const symbol = newStrategy.symbol.trim().toUpperCase();
    if (!name || !symbol) {
      alert('Name and symbol are required');
      return;
    }
    setCreating(true);
    try {
      const res = await fetch(`${API_URL}/strategy/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          symbol,
          timeframe: newStrategy.timeframe,
          status: newStrategy.status,
          entry_rule: newStrategy.entry_rule,
          exit_rule: newStrategy.exit_rule,
        }),
      });
      const data = await safeJson(res);
      if (!res.ok) throw new Error(String(data?.detail || data?.raw || `HTTP ${res.status}`));
      setShowNewForm(false);
      setNewStrategy({ name: '', symbol: 'INFY', timeframe: '4h', status: 'paused', entry_rule: '', exit_rule: '' });
      await fetchStrategies();
    } catch (err: any) {
      alert(err?.message || 'Failed to create strategy');
    } finally {
      setCreating(false);
    }
  };

  const generatePineScript = async () => {
    if (!selected) return;
    setPineError(null);
    setPineLoading(true);
    setPineScript('');
    try {
      const res = await fetch(`${API_URL}/strategy/pinescript/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: `${selected.name} (${selected.symbol})` }),
      });
      const data = await safeJson(res);
      if (!res.ok) throw new Error(String(data?.detail || data?.raw || `HTTP ${res.status}`));
      setPineScript(String(data?.script || ''));
    } catch (e: any) {
      setPineError(e?.message || 'Failed to generate PineScript');
    } finally {
      setPineLoading(false);
    }
  };

  return (
    <div className="p-6 bg-black text-white">
      <div className="flex flex-col gap-3 sm:flex-row sm:justify-between sm:items-center mb-6">
        <h1 className="text-3xl font-bold">Trading Strategies</h1>
        <button
          onClick={() => setShowNewForm(!showNewForm)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded font-semibold"
        >
          + New Strategy
        </button>
      </div>

      {showNewForm ? (
        <form onSubmit={handleCreate} className="mb-8 bg-gray-900 border border-gray-800 rounded-lg p-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-300 mb-2">Name</label>
              <input
                value={newStrategy.name}
                onChange={(e) => setNewStrategy({ ...newStrategy, name: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
                placeholder="EMA Cross"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-300 mb-2">Symbol</label>
              <input
                value={newStrategy.symbol}
                onChange={(e) => setNewStrategy({ ...newStrategy, symbol: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
                placeholder="INFY"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-300 mb-2">Timeframe</label>
              <select
                value={newStrategy.timeframe}
                onChange={(e) => setNewStrategy({ ...newStrategy, timeframe: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
              >
                <option value="1h">1h</option>
                <option value="4h">4h</option>
                <option value="1d">1d</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-300 mb-2">Status</label>
              <select
                value={newStrategy.status}
                onChange={(e) => setNewStrategy({ ...newStrategy, status: e.target.value as any })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
              >
                <option value="paused">paused</option>
                <option value="running">running</option>
                <option value="backtested">backtested</option>
              </select>
            </div>
            <div className="sm:col-span-2">
              <label className="block text-sm text-gray-300 mb-2">Entry Rule / Buy Conditions (text or JSON)</label>
              <textarea
                value={newStrategy.entry_rule}
                onChange={(e) => setNewStrategy({ ...newStrategy, entry_rule: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white min-h-[84px]"
                placeholder='Example: {"rsi":{"below":30},"trend":"bullish"}'
              />
            </div>
            <div className="sm:col-span-2">
              <label className="block text-sm text-gray-300 mb-2">Exit Rule / Sell Conditions (text or JSON)</label>
              <textarea
                value={newStrategy.exit_rule}
                onChange={(e) => setNewStrategy({ ...newStrategy, exit_rule: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white min-h-[84px]"
                placeholder='Example: {"rsi":{"above":70}}'
              />
            </div>
          </div>

          <div className="mt-4 flex items-center justify-end gap-2">
            <button
              type="button"
              onClick={() => setShowNewForm(false)}
              className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded font-semibold"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={creating}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 rounded font-semibold"
            >
              {creating ? 'Creating...' : 'Create Strategy'}
            </button>
          </div>
        </form>
      ) : null}

      <section className="mb-8">
        <div className="bg-gray-900 rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-800">
                <tr>
                  <th className="px-4 py-3 text-left">Name</th>
                  <th className="px-4 py-3 text-left">Symbol</th>
                  <th className="px-4 py-3 text-left">Timeframe</th>
                  <th className="px-4 py-3 text-left">Status</th>
                  <th className="px-4 py-3 text-right">P&amp;L</th>
                  <th className="px-4 py-3 text-right">Win%</th>
                  <th className="px-4 py-3 text-center">Actions</th>
                </tr>
              </thead>
              <tbody>
                {sortedStrategies.map((strat) => (
                  <tr
                    key={strat.id}
                    className={`border-b border-gray-800 cursor-pointer hover:bg-gray-800/60 ${
                      selected?.id === strat.id ? 'bg-gray-800/60' : ''
                    }`}
                    onClick={() => setSelected(strat)}
                  >
                    <td className="px-4 py-3 font-semibold">{strat.name}</td>
                    <td className="px-4 py-3">{strat.symbol}</td>
                    <td className="px-4 py-3">{strat.timeframe}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-1 rounded text-sm ${
                          strat.status === 'running'
                            ? 'bg-green-900 text-green-400'
                            : strat.status === 'paused'
                              ? 'bg-yellow-900 text-yellow-400'
                              : 'bg-gray-800 text-gray-300'
                        }`}
                      >
                        {strat.status}
                      </span>
                    </td>
                    <td className={`px-4 py-3 text-right font-semibold ${strat.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {strat.pnl >= 0 ? '+' : ''}
                      {Number(strat.pnl).toFixed(0)}
                    </td>
                    <td className="px-4 py-3 text-right">{strat.win_rate}%</td>
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(strat.id);
                        }}
                        className="px-2 py-1 bg-red-600 rounded text-sm hover:bg-red-700"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {selected ? (
        <section>
          <h2 className="text-xl font-bold mb-4">Strategy Details: {selected.name}</h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
            <div className="bg-gray-900 p-4 rounded">
              <p className="text-gray-400 text-sm">Total Trades</p>
              <p className="text-2xl font-bold">{selected.total_trades}</p>
            </div>
            <div className="bg-gray-900 p-4 rounded">
              <p className="text-gray-400 text-sm">Win Rate</p>
              <p className="text-2xl font-bold text-green-400">{selected.win_rate}%</p>
            </div>
          </div>

          <div className="bg-gray-900 p-4 rounded mb-6">
            <h3 className="text-lg font-semibold mb-4">Equity Curve</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={selected.equity_curve || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                <XAxis dataKey="date" stroke="#888" />
                <YAxis stroke="#888" />
                <Tooltip contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #444' }} />
                <Line type="monotone" dataKey="value" stroke="#3b82f6" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-gray-900 p-4 rounded">
            <div className="flex flex-col gap-3 sm:flex-row sm:justify-between sm:items-center mb-3">
              <h3 className="text-lg font-semibold">PineScript Generator</h3>
              <button
                onClick={generatePineScript}
                disabled={pineLoading}
                className="px-3 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 rounded text-sm font-semibold"
              >
                {pineLoading ? 'Generating...' : 'Generate PineScript'}
              </button>
            </div>
            {pineError ? <div className="text-red-400 text-sm mb-2">{pineError}</div> : null}
            {pineScript ? (
              <pre className="bg-black/40 border border-gray-800 rounded p-3 text-xs overflow-x-auto whitespace-pre">
                {pineScript}
              </pre>
            ) : (
              <div className="text-gray-400 text-sm">Click "Generate PineScript" to create a starter strategy.</div>
            )}
          </div>
        </section>
      ) : null}
    </div>
  );
}

--- END FILE: trading-dashboard\frontend\src\components\StrategiesPage.tsx ---

--- START FILE: trading-dashboard\frontend\src\components\TradingPage.tsx ---
import React, { useEffect, useState } from 'react';

const API_URL = '';

interface Position {
  symbol: string;
  qty: number;
  entry_price: number;
  current_price: number;
  pnl: number;
  pnl_pct: number;
}

interface Order {
  id: string;
  symbol: string;
  side: 'buy' | 'sell';
  qty: number;
  price: number;
  status: 'pending' | 'filled' | 'partial' | 'cancelled';
  timestamp: string;
}

export function TradingPage() {
  const [mode, setMode] = useState<'paper' | 'live'>('paper');
  const [positions, setPositions] = useState<Position[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [formData, setFormData] = useState({
    symbol: '',
    side: 'buy' as 'buy' | 'sell',
    qty: '',
    price: '',
    stopLoss: '',
    takeProfit: '',
  });

  useEffect(() => {
    fetchPositions();
    fetchOrders();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode]);

  const safeJson = async (res: Response) => {
    const text = await res.text();
    try {
      return text ? JSON.parse(text) : {};
    } catch {
      return { raw: text };
    }
  };

  const fetchPositions = async () => {
    try {
      const res = await fetch(`${API_URL}/positions`);
      const data = await safeJson(res);
      setPositions(Array.isArray(data) ? data : []);
    } catch {
      setPositions([]);
    }
  };

  const fetchOrders = async () => {
    try {
      const res = await fetch(`${API_URL}/order-history`);
      const data = await safeJson(res);
      setOrders(Array.isArray(data) ? data : []);
    } catch {
      setOrders([]);
    }
  };

  const handlePlaceOrder = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.symbol || !formData.qty || !formData.price) {
      alert('Please fill all required fields');
      return;
    }

    try {
      const response = await fetch(`${API_URL}/trade`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: formData.symbol,
          side: formData.side,
          quantity: parseFloat(formData.qty),
          price: parseFloat(formData.price),
          stop_loss: formData.stopLoss ? parseFloat(formData.stopLoss) : null,
          take_profit: formData.takeProfit ? parseFloat(formData.takeProfit) : null,
          mode,
        }),
      });

      if (response.ok) {
        setFormData({ symbol: '', side: 'buy', qty: '', price: '', stopLoss: '', takeProfit: '' });
        await Promise.all([fetchPositions(), fetchOrders()]);
      } else {
        const data = await safeJson(response);
        alert(data?.detail || data?.raw || 'Error placing order');
      }
    } catch (error) {
      console.error('Error placing order:', error);
      alert('Error placing order');
    }
  };

  const handleClosePosition = async (symbol: string) => {
    try {
      const res = await fetch(`${API_URL}/positions/${encodeURIComponent(symbol)}`, { method: 'DELETE' });
      if (res.ok) {
        await fetchPositions();
      }
    } catch (error) {
      console.error('Error closing position:', error);
    }
  };

  return (
    <div className="p-6 bg-black text-white">
      <div className="flex flex-col gap-3 sm:flex-row sm:justify-between sm:items-center mb-6">
        <h1 className="text-3xl font-bold">Trading Dashboard</h1>
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-300">Mode:</span>
          <button
            onClick={() => setMode(mode === 'paper' ? 'live' : 'paper')}
            className={`px-4 py-2 rounded font-semibold ${
              mode === 'paper' ? 'bg-blue-600 hover:bg-blue-700' : 'bg-red-600 hover:bg-red-700'
            }`}
          >
            {mode === 'paper' ? 'Paper' : 'LIVE'}
          </button>
        </div>
      </div>

      <section className="mb-8">
        <h2 className="text-xl font-bold mb-4">Active Positions</h2>
        <div className="bg-gray-900 rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-800 border-b border-gray-700">
                <tr>
                  <th className="px-4 py-3 text-left">Symbol</th>
                  <th className="px-4 py-3 text-right">Qty</th>
                  <th className="px-4 py-3 text-right">Entry Price</th>
                  <th className="px-4 py-3 text-right">Current Price</th>
                  <th className="px-4 py-3 text-right">P&L</th>
                  <th className="px-4 py-3 text-right">%</th>
                  <th className="px-4 py-3 text-center">Action</th>
                </tr>
              </thead>
              <tbody>
                {positions.map((pos) => (
                  <tr key={pos.symbol} className="border-b border-gray-800 hover:bg-gray-800/60">
                    <td className="px-4 py-3 font-semibold">{pos.symbol}</td>
                    <td className="px-4 py-3 text-right">{pos.qty}</td>
                    <td className="px-4 py-3 text-right">₹{Number(pos.entry_price).toFixed(2)}</td>
                    <td className="px-4 py-3 text-right">₹{Number(pos.current_price).toFixed(2)}</td>
                    <td
                      className={`px-4 py-3 text-right font-semibold ${
                        pos.pnl >= 0 ? 'text-green-400' : 'text-red-400'
                      }`}
                    >
                      {pos.pnl >= 0 ? '+' : ''}
                      {Number(pos.pnl).toFixed(2)}
                    </td>
                    <td className={`px-4 py-3 text-right ${pos.pnl_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {pos.pnl_pct >= 0 ? '+' : ''}
                      {Number(pos.pnl_pct).toFixed(2)}%
                    </td>
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={() => handleClosePosition(pos.symbol)}
                        className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
                      >
                        Close
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {positions.length === 0 && <div className="p-6 text-center text-gray-400">No active positions</div>}
        </div>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-bold mb-4">Place New Order</h2>
        <form onSubmit={handlePlaceOrder} className="bg-gray-900 p-6 rounded-lg">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium mb-2">Symbol</label>
              <input
                type="text"
                placeholder="INFY"
                value={formData.symbol}
                onChange={(e) => setFormData({ ...formData, symbol: e.target.value.toUpperCase() })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Side</label>
              <select
                value={formData.side}
                onChange={(e) => setFormData({ ...formData, side: e.target.value as 'buy' | 'sell' })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
              >
                <option value="buy">Buy</option>
                <option value="sell">Sell</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium mb-2">Quantity</label>
              <input
                type="number"
                placeholder="100"
                value={formData.qty}
                onChange={(e) => setFormData({ ...formData, qty: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Price</label>
              <input
                type="number"
                step="0.01"
                placeholder="1955.50"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium mb-2">Stop Loss</label>
              <input
                type="number"
                step="0.01"
                placeholder="1920"
                value={formData.stopLoss}
                onChange={(e) => setFormData({ ...formData, stopLoss: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Take Profit</label>
              <input
                type="number"
                step="0.01"
                placeholder="1985"
                value={formData.takeProfit}
                onChange={(e) => setFormData({ ...formData, takeProfit: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
              />
            </div>
          </div>

          <button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 rounded">
            Place Order
          </button>
        </form>
      </section>

      <section>
        <h2 className="text-xl font-bold mb-4">Order History</h2>
        <div className="bg-gray-900 rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-800 border-b border-gray-700">
                <tr>
                  <th className="px-4 py-3 text-left">Date</th>
                  <th className="px-4 py-3 text-left">Symbol</th>
                  <th className="px-4 py-3 text-left">Side</th>
                  <th className="px-4 py-3 text-right">Qty</th>
                  <th className="px-4 py-3 text-right">Price</th>
                  <th className="px-4 py-3 text-left">Status</th>
                </tr>
              </thead>
              <tbody>
                {orders.slice(0, 10).map((order) => (
                  <tr key={order.id} className="border-b border-gray-800 hover:bg-gray-800/60">
                    <td className="px-4 py-3 text-sm">
                      {order.timestamp ? new Date(order.timestamp).toLocaleDateString() : ''}
                    </td>
                    <td className="px-4 py-3 font-semibold">{order.symbol}</td>
                    <td className={`px-4 py-3 ${order.side === 'buy' ? 'text-green-400' : 'text-red-400'}`}>
                      {order.side === 'buy' ? 'Buy' : 'Sell'}
                    </td>
                    <td className="px-4 py-3 text-right">{order.qty}</td>
                    <td className="px-4 py-3 text-right">₹{Number(order.price).toFixed(2)}</td>
                    <td
                      className={`px-4 py-3 text-sm ${
                        order.status === 'filled'
                          ? 'text-green-400'
                          : order.status === 'partial'
                            ? 'text-yellow-400'
                            : 'text-gray-400'
                      }`}
                    >
                      {String(order.status || '').toUpperCase()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {orders.length === 0 && <div className="p-6 text-center text-gray-400">No orders yet</div>}
        </div>
      </section>
    </div>
  );
}


--- END FILE: trading-dashboard\frontend\src\components\TradingPage.tsx ---

--- START FILE: trading-dashboard\frontend\src\components\WatchlistPage.tsx ---
import React, { useEffect, useState } from 'react';

const API_URL = '';

type WatchlistItem = {
  id: string;
  symbol: string;
  strategy_id: string;
  auto_trade: boolean;
  status: string;
  added_date?: string;
  last_checked?: string | null;
  last_signal?: string | null;
  last_signal_price?: number | null;
  quantity_to_buy?: number;
};

export function WatchlistPage() {
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [symbol, setSymbol] = useState('');
  const [strategyId, setStrategyId] = useState('default');
  const [autoTrade, setAutoTrade] = useState(false);
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(true);

  const safeJson = async (res: Response) => {
    const text = await res.text();
    try {
      return text ? JSON.parse(text) : {};
    } catch {
      return { raw: text };
    }
  };

  const refresh = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/watchlist`);
      const data = await safeJson(res);
      setItems(Array.isArray(data) ? data : []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const add = async () => {
    const s = symbol.trim().toUpperCase();
    if (!s) return;
    const res = await fetch(`${API_URL}/api/watchlist/add`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symbol: s, strategy_id: strategyId, auto_trade: autoTrade, quantity_to_buy: quantity }),
    });
    const data = await safeJson(res);
    if (!res.ok) {
      alert(data?.detail || data?.raw || `HTTP ${res.status}`);
      return;
    }
    setSymbol('');
    await refresh();
  };

  const remove = async (sym: string) => {
    const res = await fetch(`${API_URL}/api/watchlist/remove`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symbol: sym }),
    });
    await safeJson(res);
    await refresh();
  };

  return (
    <div className="p-6 bg-black text-white">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Watchlist</h1>
        <button onClick={refresh} className="px-3 py-2 bg-gray-900 hover:bg-gray-800 rounded text-sm font-semibold">
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 mb-6">
        <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
          <div className="sm:col-span-2">
            <label className="block text-sm text-gray-400 mb-1">Symbol</label>
            <input
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
              placeholder="INFY / BTC-USD / RELIANCE"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Strategy</label>
            <input
              value={strategyId}
              onChange={(e) => setStrategyId(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
              placeholder="default"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Qty</label>
            <input
              type="number"
              value={quantity}
              min={1}
              onChange={(e) => setQuantity(parseInt(e.target.value || '1', 10))}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
            />
          </div>
          <div className="flex items-end gap-2">
            <label className="flex items-center gap-2 text-sm text-gray-300">
              <input type="checkbox" checked={autoTrade} onChange={(e) => setAutoTrade(e.target.checked)} />
              Auto trade
            </label>
            <button onClick={add} className="ml-auto px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded font-semibold">
              Add
            </button>
          </div>
        </div>
        <div className="text-xs text-gray-500 mt-3">
          Watchlist is stored in the dashboard database (SQLite by default, Postgres if you attach `DATABASE_URL` on Render).
        </div>
      </div>

      <div className="bg-gray-900 rounded-lg overflow-hidden border border-gray-800">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-800 border-b border-gray-700">
              <tr>
                <th className="px-4 py-3 text-left">Symbol</th>
                <th className="px-4 py-3 text-left">Strategy</th>
                <th className="px-4 py-3 text-left">Auto</th>
                <th className="px-4 py-3 text-right">Qty</th>
                <th className="px-4 py-3 text-left">Last Signal</th>
                <th className="px-4 py-3 text-center">Action</th>
              </tr>
            </thead>
            <tbody>
              {items
                .filter((i) => i.status !== 'removed')
                .map((i) => (
                  <tr key={i.id} className="border-b border-gray-800 hover:bg-gray-800/60">
                    <td className="px-4 py-3 font-semibold">{i.symbol}</td>
                    <td className="px-4 py-3">{i.strategy_id}</td>
                    <td className="px-4 py-3">{i.auto_trade ? 'Yes' : 'No'}</td>
                    <td className="px-4 py-3 text-right">{i.quantity_to_buy ?? 1}</td>
                    <td className="px-4 py-3 text-gray-300">
                      {i.last_signal ? `${i.last_signal} @ ₹${Number(i.last_signal_price || 0).toFixed(2)}` : '—'}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <button onClick={() => remove(i.symbol)} className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-sm">
                        Remove
                      </button>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>

        {items.filter((i) => i.status !== 'removed').length === 0 && !loading ? (
          <div className="p-6 text-center text-gray-400">No watchlist items</div>
        ) : null}
      </div>
    </div>
  );
}

--- END FILE: trading-dashboard\frontend\src\components\WatchlistPage.tsx ---

--- START FILE: trading-dashboard\frontend\src\hooks\useApi.ts ---
import { useState } from 'react';

interface FetchOptions extends RequestInit {
  headers?: Record<string, string>;
}

export function useApi() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const call = async (endpoint: string, options: FetchOptions = {}) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(endpoint, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { call, loading, error };
}

--- END FILE: trading-dashboard\frontend\src\hooks\useApi.ts ---

--- START FILE: trading-dashboard\frontend\src\hooks\useLocalStorage.ts ---
import { useState } from 'react';

export function useLocalStorage(key: string, initialValue: unknown) {
  const [storedValue, setStoredValue] = useState<unknown>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(error);
      return initialValue;
    }
  });

  const setValue = (value: unknown) => {
    try {
      setStoredValue(value);
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(error);
    }
  };

  return [storedValue, setValue];
}

--- END FILE: trading-dashboard\frontend\src\hooks\useLocalStorage.ts ---

--- START FILE: trading-dashboard\frontend\src\hooks\useWebSocket.ts ---
import { useEffect, useState } from 'react';

export function useWebSocket(url: string) {
  const [data, setData] = useState<unknown>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(url);

    ws.onopen = () => setIsConnected(true);
    ws.onmessage = (event) => {
      try {
        setData(JSON.parse(event.data));
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    ws.onclose = () => setIsConnected(false);

    return () => ws.close();
  }, [url]);

  return { data, isConnected };
}

--- END FILE: trading-dashboard\frontend\src\hooks\useWebSocket.ts ---

--- START FILE: trading-dashboard\frontend\src\types\index.txt ---
export interface AgentState {
  agent_id: string;
  status: 'online' | 'processing' | 'idle' | 'error';
  task: string;
  progress: number;
  skills?: string[];
  cpu_percent?: number;
  memory_mb?: number;
  timestamp?: string;
}

export interface Strategy {
  id: string;
  name: string;
  symbol: string;
  timeframe: string;
  status: string;
  pnl: number;
  win_rate: number;
  created_date: string;
}

export interface BacktestResult {
  strategy: string;
  symbol: string;
  total_trades: number;
  win_rate: number;
  pnl: number;
  sharpe_ratio: number;
  max_drawdown: number;
  profit_factor: number;
}

export interface Trade {
  symbol: string;
  quantity: number;
  entry_price: number;
  current_price: number;
  pnl: number;
  pnl_percent: number;
  entry_time: string;
}
--- END FILE: trading-dashboard\frontend\src\types\index.txt ---
