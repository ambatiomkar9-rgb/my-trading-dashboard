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
