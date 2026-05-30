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
