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
