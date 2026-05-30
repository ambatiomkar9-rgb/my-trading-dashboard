"""Technical analysis utilities for research agents."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Dict, List
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class TechnicalSnapshot:
    """Indicator snapshot for a symbol/timeframe."""

    symbol: str
    timeframe: str
    close: float
    ema_fast: float
    ema_slow: float
    rsi: float
    trend: str
    signal: str


class TechnicalAnalysisSkill:
    """
    Multi-timeframe technical analysis skill.

    Unit-test example:
        >>> skill = TechnicalAnalysisSkill()
        >>> isinstance(skill._compute_rsi(pd.Series([1,2,3,2,4])), pd.Series)
        True
    """

    def __init__(self, ema_fast: int = 21, ema_slow: int = 55, rsi_period: int = 14) -> None:
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow
        self.rsi_period = rsi_period

    async def analyze_symbol(self, symbol: str, timeframe: str = "1d", lookback: str = "6mo") -> TechnicalSnapshot:
        """Download OHLCV and compute indicator snapshot."""
        frame = await asyncio.to_thread(
            yf.download,
            tickers=symbol,
            period=lookback,
            interval=timeframe,
            auto_adjust=False,
            progress=False,
        )
        if frame.empty:
            raise ValueError(f"No data returned for symbol={symbol} timeframe={timeframe}")
        frame = self._normalize_columns(frame).copy()
        close = self._extract_close(frame)
        frame = frame.loc[close.dropna().index].copy()
        close = close.loc[frame.index]
        frame["Close"] = close
        frame["ema_fast"] = close.ewm(span=self.ema_fast, adjust=False).mean()
        frame["ema_slow"] = close.ewm(span=self.ema_slow, adjust=False).mean()
        frame["rsi"] = self._compute_rsi(close)
        last = frame.iloc[-1]
        ema_fast = self._as_scalar(last["ema_fast"])
        ema_slow = self._as_scalar(last["ema_slow"])
        rsi = self._as_scalar(last["rsi"])
        close_last = self._as_scalar(last["Close"])
        trend = "bullish" if ema_fast > ema_slow else "bearish"
        signal = "hold"
        if trend == "bullish" and rsi < 70:
            signal = "buy_bias"
        elif trend == "bearish" and rsi > 30:
            signal = "sell_bias"
        return TechnicalSnapshot(
            symbol=symbol,
            timeframe=timeframe,
            close=close_last,
            ema_fast=ema_fast,
            ema_slow=ema_slow,
            rsi=rsi,
            trend=trend,
            signal=signal,
        )

    async def analyze_multi_asset(
        self, symbols: List[str], timeframe: str = "1d", lookback: str = "6mo"
    ) -> Dict[str, TechnicalSnapshot]:
        """Analyze multiple symbols concurrently."""
        tasks = [self.analyze_symbol(symbol=s, timeframe=timeframe, lookback=lookback) for s in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        output: Dict[str, TechnicalSnapshot] = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                logger.exception("Technical analysis failed for symbol=%s", symbol, exc_info=result)
                continue
            output[symbol] = result
        return output

    def _compute_rsi(self, close: pd.Series) -> pd.Series:
        """Compute RSI with Wilder smoothing."""
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)
        avg_gain = gain.ewm(alpha=1 / self.rsi_period, min_periods=self.rsi_period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / self.rsi_period, min_periods=self.rsi_period, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, pd.NA)
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50.0)

    def _normalize_columns(self, frame: pd.DataFrame) -> pd.DataFrame:
        """Flatten yfinance multi-index columns to single level."""
        if isinstance(frame.columns, pd.MultiIndex):
            frame = frame.copy()
            frame.columns = [str(col[0]) for col in frame.columns]
        return frame

    def _extract_close(self, frame: pd.DataFrame) -> pd.Series:
        """Extract one numeric close series from dataframe."""
        close_obj = frame["Close"]
        if isinstance(close_obj, pd.DataFrame):
            close_obj = close_obj.iloc[:, 0]
        close = pd.to_numeric(close_obj, errors="coerce")
        if close.empty:
            raise ValueError("No valid close series available for analysis.")
        return close

    def _as_scalar(self, value: object) -> float:
        """Convert pandas scalar/1-item series to float safely."""
        if isinstance(value, pd.Series):
            if value.empty:
                raise ValueError("Received empty series where scalar was expected.")
            value = value.iloc[0]
        return float(value)
