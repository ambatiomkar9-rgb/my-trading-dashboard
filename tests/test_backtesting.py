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
