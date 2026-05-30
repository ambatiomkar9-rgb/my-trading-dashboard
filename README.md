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
