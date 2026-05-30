"""Market data router for agents.

Goal: fetch *real* market data from the best available source.

Order of preference:
1) Exchange/broker public market data (e.g. Binance OHLCV via CCXT for crypto).
2) yfinance as universal fallback (equities, indices, crypto tickers like BTC-USD).

This is read-only market data. Trading/execution stays in execution layer.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


def _normalize_yfinance(frame: pd.DataFrame) -> pd.DataFrame:
    df = frame.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [str(col[0]) for col in df.columns]
    if "Close" not in df:
        raise ValueError("yfinance frame missing Close column")
    close_obj = df["Close"]
    if isinstance(close_obj, pd.DataFrame):
        close_obj = close_obj.iloc[:, 0]
    df["Close"] = pd.to_numeric(close_obj, errors="coerce")
    return df.dropna().copy()


async def _yf_download(symbol: str, lookback_days: int, interval: str) -> pd.DataFrame:
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=lookback_days)
    frame = await asyncio.to_thread(
        yf.download,
        tickers=symbol,
        start=start,
        end=end,
        interval=interval,
        auto_adjust=False,
        progress=False,
    )
    if frame.empty:
        raise ValueError(f"No yfinance data for symbol={symbol} interval={interval}")
    return _normalize_yfinance(frame)


async def _ccxt_ohlcv(exchange_id: str, symbol: str, timeframe: str, limit: int) -> pd.DataFrame:
    try:
        import ccxt.async_support as ccxt_async  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("ccxt is required for exchange market data") from exc

    ex_cls = getattr(ccxt_async, exchange_id)
    ex = ex_cls({"enableRateLimit": True})
    try:
        bars = await ex.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    finally:
        try:
            await ex.close()
        except Exception:
            pass
    # bars: [timestamp, open, high, low, close, volume]
    df = pd.DataFrame(bars, columns=["ts", "Open", "High", "Low", "Close", "Volume"])
    df["Date"] = pd.to_datetime(df["ts"], unit="ms", utc=True)
    df = df.drop(columns=["ts"]).set_index("Date")
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
    return df.dropna().copy()


@dataclass(slots=True)
class MarketDataRouter:
    """Market data router with best-effort provider selection."""

    crypto_exchange_id: str = "binance"

    def _is_ccxt_symbol(self, symbol: str) -> bool:
        return "/" in symbol and len(symbol.split("/")) == 2

    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1d",
        lookback_days: int = 180,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Return (dataframe, meta) where dataframe contains at least Close.
        """
        if self._is_ccxt_symbol(symbol):
            # Approximate limit for daily/hours.
            limit = min(max(int(lookback_days * 2), 50), 1000)
            df = await _ccxt_ohlcv(self.crypto_exchange_id, symbol, timeframe, limit=limit)
            return df, {"provider": f"ccxt:{self.crypto_exchange_id}"}
        df = await _yf_download(symbol, lookback_days=lookback_days, interval=timeframe)
        return df, {"provider": "yfinance"}

    async def get_latest_price(self, symbol: str) -> Tuple[float, Dict[str, Any]]:
        df, meta = await self.get_ohlcv(symbol, timeframe="1d", lookback_days=10)
        close = df["Close"].iloc[-1]
        if isinstance(close, pd.Series):
            close = close.iloc[0]
        return float(close), meta

