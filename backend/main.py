import os
import uuid
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

import json
import urllib.request
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

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
        'signal_type': 'buy',
        'signal_price': float(payload.get('price') or payload.get('signal_price') or 0.0),
        'signal_time': datetime.now().isoformat(),
        'technical_score': float(payload.get('technical_score') or 0.0),
        'news_score': float(payload.get('news_score') or 0.0),
        'fundamental_score': float(payload.get('fundamental_score') or 0.0),
        'risk_score': float(payload.get('risk_score') or 0.0),
        'overall_score': float(payload.get('overall_score') or 0.0),
        'approval_status': 'pending',
    }
    trade_signals.insert(0, signal_rec)

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
    return positions

@app.get('/api/positions')
async def get_positions_api():
    return await get_positions()

@app.delete('/positions/{symbol}')
async def close_position(symbol: str):
    global positions
    positions = [p for p in positions if p['symbol'] != symbol.upper()]
    return {'status': 'ok'}

@app.post('/trade')
async def place_trade(data: dict):
    symbol = str(data.get('symbol', '')).upper()
    side = data.get('side', 'buy')
    qty = float(data.get('quantity', 0))
    price = float(data.get('price', 0))
    if not symbol or qty <= 0 or price <= 0:
        raise HTTPException(status_code=400, detail='Invalid order payload')
    o = {'id': str(uuid.uuid4()), 'symbol': symbol, 'side': side, 'qty': qty, 'price': price, 'status': 'filled', 'timestamp': datetime.now().isoformat()}
    order_history.insert(0, o)
    positions.append({'symbol': symbol, 'qty': qty, 'entry_price': price, 'current_price': price, 'pnl': 0, 'pnl_pct': 0})
    return {'status': 'success', 'order_id': o['id']}

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
    return [
        {'id': '1', 'name': 'EMA Cross', 'symbol': 'INFY', 'timeframe': '4h', 'status': 'running', 'pnl': 8500, 'win_rate': 72, 'total_trades': 45, 'equity_curve': [{'date': '2026-05-18', 'value': 100000}]},
        {'id': '2', 'name': 'Pine Momentum', 'symbol': 'NIFTY', 'timeframe': '1h', 'status': 'backtested', 'pnl': 4200, 'win_rate': 64, 'total_trades': 33, 'equity_curve': [{'date': '2026-05-18', 'value': 100000}]},
    ]

@app.get('/api/strategies')
async def get_strategies_api():
    return await get_strategies()

@app.post('/strategy/create')
async def create_strategy(payload: dict):
    return {'status': 'created', 'strategy': payload}

@app.delete('/strategy/{strategy_id}')
async def delete_strategy(strategy_id: str):
    return {'status': 'deleted', 'id': strategy_id}

@app.get('/strategy/{strategy_id}/metrics')
async def metrics(strategy_id: str):
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
# Watchlist + signal approval endpoints (used by the extra scripts / UI file)
# ---------------------------------------------------------------------------

@app.get('/api/watchlist')
async def api_get_watchlist():
    return watchlist_items

@app.post('/api/watchlist/add')
async def api_add_watchlist(payload: dict):
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
    if not symbol:
        raise HTTPException(status_code=400, detail='symbol required')
    for item in watchlist_items:
        if item.get('symbol') == symbol and item.get('status') != 'removed':
            item['status'] = 'removed'
            return {'status': 'removed', 'symbol': symbol}
    return {'status': 'not_found', 'symbol': symbol}

@app.get('/api/signals/pending')
async def api_pending_signals():
    return [s for s in trade_signals if s.get('approval_status') == 'pending']

@app.post('/api/signal/approve')
async def api_approve_signal(payload: dict):
    sid = payload.get('signal_id') or payload.get('id')
    if not sid:
        raise HTTPException(status_code=400, detail='signal_id required')
    for s in trade_signals:
        if str(s.get('id')) == str(sid):
            s['approval_status'] = 'approved'
            s['approval_time'] = datetime.now().isoformat()
            return {'status': 'approved', 'signal': s}
    return {'status': 'not_found', 'signal_id': sid}

@app.get('/api/system/health')
async def api_system_health():
    # Minimal health payload for UI; you can expand this later.
    return {
        'timestamp': datetime.now().isoformat(),
        'ollama_status': 'unknown',
        'broker_status': 'unknown',
        'agents_online': len(agent_states),
        'alert_cooldown_seconds': ALERT_COOLDOWN_SECONDS,
    }

@app.get('/api/portfolio')
async def api_portfolio():
    total_value = 0.0
    total_pnl = 0.0
    for p in positions:
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
