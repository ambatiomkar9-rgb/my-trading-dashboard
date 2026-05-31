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
from trading_system.agents.research_service import ResearchService
from trading_system.agents.validation_service import ValidationService
from trading_system.registry.registry_service import RegistryService
from trading_system.ha_layer.raft_witness import RaftWitness
from trading_system.ha_layer.runtime_adapter_follower import RuntimeAdapterFollower
from trading_system.ha_layer.runtime_adapter_leader import RuntimeAdapterLeader
from trading_system.compliance.compliance_service import ComplianceService
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
from trading_system.execution.reconciliation_engine import ReconciliationEngine
from trading_system.memory.global_state import GlobalState
from trading_system.memory.reflexion_memory import ReflexionMemoryRepository
from trading_system.memory.trade_memory import TradeMemoryRepository
from trading_system.memory.audit_memory import AuditMemoryRepository
from trading_system.memory.vector_memory import VectorMemory
from trading_system.skills.backtesting_skill import BacktestingSkill
from trading_system.skills.chatbot_command_parser import ChatbotCommandParser
from trading_system.skills.news_intelligence_skill import NewsIntelligenceSkill
from trading_system.skills.pinescript_strategy_generator import MultiModelRouter, PineScriptStrategyGenerator
from trading_system.skills.technical_analysis_skill import TechnicalAnalysisSkill
from trading_system.skills.whale_tracker_skill import WhaleTrackerSkill
from trading_system.integrations.hermes_client import HermesClient # Added for completeness

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
    audit_memory = AuditMemoryRepository(sqlite_path=db_path)
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
    reconciliation_engine = ReconciliationEngine(
        broker_router=broker_router,
        sqlite_path=db_path,
        kill_switch=kill_switch,
        interval_seconds=30
    )

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
    hermes_client = HermesClient() # Initialize HermesClient

    # Agents
    technical_agent = TechnicalAnalysisAgent(technical_skill)
    whale_agent = WhaleIntelligenceAgent(whale_skill)
    macro_agent = MacroIntelligenceAgent()
    news_agent = NewsSentimentAgent(news_skill)
    _ = PineScriptGenerationAgent(generator=pinescript_generator)
    _ = ReflexionAgent(repo=reflexion_memory, vector_memory=vector_memory)

    # HERMES v5.2 Research & Validation Services
    research_service = ResearchService(
        sqlite_path=db_path,
        event_bus=event_bus,
        hermes_client=hermes_client,
        multi_model_router=model_router,
        interval_seconds=settings.research.generation_interval_seconds,
    )
    validation_service = ValidationService(
        sqlite_path=db_path,
        event_bus=event_bus,
        hermes_client=hermes_client,
        interval_seconds=settings.research.validation_interval_seconds,
    )

    registry_service = RegistryService(
        sqlite_path=db_path,
        event_bus=event_bus,
        hermes_client=hermes_client,
        interval_seconds=settings.research.validation_interval_seconds, # Using same interval for now
        required_approval_weight=settings.risk_limits.required_approval_weight,
    )
    
    # HERMES v5.2 HA Layer
    runtime_adapter_leader = None
    runtime_adapter_follower = None
    raft_witness = None
    node_role = settings.ha_settings.node_role
    
    if node_role == "leader":
        runtime_adapter_leader = RuntimeAdapterLeader(
            instance_id=os.getenv("NODE_INSTANCE_ID", "local-leader"),
            event_bus=event_bus,
            hermes_client=hermes_client,
            strategy_vm=pinescript_generator, # Use pinescript_generator as a stand-in for strategy VM
            interval_seconds=settings.ha_settings.raft_heartbeat_interval_seconds,
        )
    elif node_role == "follower":
        runtime_adapter_follower = RuntimeAdapterFollower(
            instance_id=os.getenv("NODE_INSTANCE_ID", "local-follower"),
            event_bus=event_bus,
            hermes_client=hermes_client,
            strategy_vm=pinescript_generator,
            leader_instance_id=settings.ha_settings.leader_instance_id or "unknown-leader",
            interval_seconds=settings.ha_settings.raft_heartbeat_interval_seconds,
        )
    elif node_role == "witness":
        raft_witness = RaftWitness(
            instance_id=os.getenv("NODE_INSTANCE_ID", "local-witness"),
            interval_seconds=settings.ha_settings.raft_heartbeat_interval_seconds,
        )

    # HERMES v5.2 Compliance Service
    compliance_service = ComplianceService(
        sqlite_path=db_path,
        event_bus=event_bus,
        audit_memory=audit_memory,
        order_to_trade_ratio_threshold=settings.compliance.order_to_trade_ratio_threshold,
        physical_kill_switch_test_time_utc=settings.compliance.physical_kill_switch_test_time_utc,
        certification_check_interval_seconds=settings.compliance.certification_check_interval_seconds,
        compliance_check_interval_seconds=settings.compliance.compliance_check_interval_seconds,
    )

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
    register_default_handlers(event_bus, global_state, trade_memory, audit_memory)

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
        audit_memory=audit_memory,
        reconciliation_engine=reconciliation_engine,
        research_service=research_service,
        validation_service=validation_service,
        registry_service=registry_service,
        runtime_adapter_leader=runtime_adapter_leader,
        runtime_adapter_follower=runtime_adapter_follower,
        raft_witness=raft_witness,
        compliance_service=compliance_service,
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
        if container.reconciliation_engine:
            app.state.reconciliation_task = asyncio.create_task(container.reconciliation_engine.start())
        if container.research_service:
            app.state.research_task = asyncio.create_task(container.research_service.start())
        if container.validation_service:
            app.state.validation_task = asyncio.create_task(container.validation_service.start())
        if container.registry_service:
            app.state.registry_task = asyncio.create_task(container.registry_service.start())
        
        # Start HA layer components based on node role
        if container.settings.ha_settings.node_role == "leader" and container.runtime_adapter_leader:
            app.state.runtime_adapter_leader_task = asyncio.create_task(container.runtime_adapter_leader.start())
        elif container.settings.ha_settings.node_role == "follower" and container.runtime_adapter_follower:
            app.state.runtime_adapter_follower_task = asyncio.create_task(container.runtime_adapter_follower.start())
        elif container.settings.ha_settings.node_role == "witness" and container.raft_witness:
            app.state.raft_witness_task = asyncio.create_task(container.raft_witness.start())

        if container.compliance_service:
            app.state.compliance_task = asyncio.create_task(container.compliance_service.start())

        logger.info("Trading system startup completed")

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        app.state.stop_event.set()
        recovery_task = app.state.recovery_task
        if recovery_task:
            recovery_task.cancel()
        reconciliation_task = getattr(app.state, 'reconciliation_task', None)
        if reconciliation_task:
            reconciliation_task.cancel()
        research_task = getattr(app.state, 'research_task', None)
        if research_task:
            research_task.cancel()
        validation_task = getattr(app.state, 'validation_task', None)
        if validation_task:
            validation_task.cancel()
        registry_task = getattr(app.state, 'registry_task', None)
        if registry_task:
            registry_task.cancel()
        
        runtime_adapter_leader_task = getattr(app.state, 'runtime_adapter_leader_task', None)
        if runtime_adapter_leader_task:
            runtime_adapter_leader_task.cancel()
        runtime_adapter_follower_task = getattr(app.state, 'runtime_adapter_follower_task', None)
        if runtime_adapter_follower_task:
            runtime_adapter_follower_task.cancel()
        raft_witness_task = getattr(app.state, 'raft_witness_task', None)
        if raft_witness_task:
            raft_witness_task.cancel()
        compliance_task = getattr(app.state, 'compliance_task', None)
        if compliance_task:
            compliance_task.cancel()
        
        await asyncio.gather(
            recovery_task, 
            reconciliation_task, 
            research_task, 
            validation_task, 
            registry_task,
            runtime_adapter_leader_task,
            runtime_adapter_follower_task,
            raft_witness_task,
            compliance_task,
            return_exceptions=True
        )
        container = app.state.container
        if container:
            await container.event_bus.stop()
        logger.info("Trading system shutdown completed")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("trading_system.main:app", host="0.0.0.0", port=8000, reload=False)
