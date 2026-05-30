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
