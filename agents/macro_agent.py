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
