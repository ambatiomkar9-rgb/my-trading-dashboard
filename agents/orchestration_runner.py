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
