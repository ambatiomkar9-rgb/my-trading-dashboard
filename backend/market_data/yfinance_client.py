"""Real market data client using yfinance for backtesting."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

try:
    import yfinance as yf
except ImportError:
    yf = None  # type: ignore[assignment]

TIMEFRAME_MAP = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "1h": "1h",
    "4h": "1h",
    "1d": "1d",
    "1w": "1wk",
    "1M": "1mo",
}

TIMEFRAME_DELTA = {
    "1m": timedelta(days=7),
    "5m": timedelta(days=60),
    "15m": timedelta(days=60),
    "30m": timedelta(days=60),
    "1h": timedelta(days=730),
    "4h": timedelta(days=730),
    "1d": timedelta(days=3650),
    "1w": timedelta(days=3650),
    "1M": timedelta(days=3650),
}


def _resolve_symbol(symbol: str) -> str:
    """Resolve symbol to yfinance format (add .NS for Indian stocks if needed)."""
    sym = symbol.strip().upper()
    if sym.endswith((".NS", ".BO", ".NSE", ".BSE")):
        return sym
    if len(sym) <= 5 and sym.isalpha():
        return f"{sym}.NS"
    return sym


_yf_breaker = None


def _get_yf_breaker():
    global _yf_breaker
    if _yf_breaker is None:
        from backend.infra.circuit_breaker import get_breaker
        _yf_breaker = get_breaker("yfinance", failure_threshold=5, recovery_timeout=60)
    return _yf_breaker


def fetch_ohlcv(
    symbol: str,
    timeframe: str = "1d",
    start: Optional[str] = None,
    end: Optional[str] = None,
    period: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """
    Fetch OHLCV data from yfinance.

    Args:
        symbol: Stock symbol (e.g., "INFY", "RELIANCE.NS")
        timeframe: Timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M)
        start: Start date string (YYYY-MM-DD)
        end: End date string (YYYY-MM-DD)
        period: Period string (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

    Returns:
        DataFrame with columns: Open, High, Low, Close, Volume or None on error
    """
    breaker = _get_yf_breaker()
    if not breaker.allow_request():
        logger.warning("yfinance circuit breaker is OPEN — skipping %s", symbol)
        return None

    if yf is None:
        logger.warning("yfinance not installed; cannot fetch market data")
        return None

    yf_symbol = _resolve_symbol(symbol)
    yf_interval = TIMEFRAME_MAP.get(timeframe, "1d")

    try:
        ticker = yf.Ticker(yf_symbol)

        if period:
            df = ticker.history(period=period, interval=yf_interval)
        else:
            if not start:
                delta = TIMEFRAME_DELTA.get(timeframe, timedelta(days=365))
                start_dt = datetime.now() - delta
                start = start_dt.strftime("%Y-%m-%d")
            if not end:
                end = datetime.now().strftime("%Y-%m-%d")
            df = ticker.history(start=start, end=end, interval=yf_interval)

        if df is None or df.empty:
            logger.warning("No data returned for %s (%s)", yf_symbol, timeframe)
            return None

        # For 4h timeframe, aggregate 1h data
        if timeframe == "4h" and yf_interval == "1h" and len(df) > 0:
            df = _aggregate_4h(df)

        # Normalize columns
        df = df.rename(columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        })

        # Keep only OHLCV columns
        cols = ["open", "high", "low", "close", "volume"]
        available = [c for c in cols if c in df.columns]
        df = df[available].copy()

        # Add timestamp column
        df["timestamp"] = df.index.strftime("%Y-%m-%d %H:%M:%S")
        df = df.reset_index(drop=True)

        breaker.record_success()
        return df

    except Exception as exc:
        breaker.record_failure()
        logger.error("Failed to fetch OHLCV for %s: %s", yf_symbol, exc)
        return None


def _aggregate_4h(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate 1h data into 4h candles."""
    df = df.copy()
    df["group"] = range(len(df))
    df["group"] = df["group"] // 4

    agg = df.groupby("group").agg({
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum",
    })

    return agg


def fetch_info(symbol: str) -> Optional[dict]:
    """Fetch company info for a symbol."""
    if yf is None:
        return None

    yf_symbol = _resolve_symbol(symbol)
    try:
        ticker = yf.Ticker(yf_symbol)
        info = ticker.info
        return {
            "symbol": symbol,
            "name": info.get("longName", symbol),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
            "market_cap": info.get("marketCap", 0),
            "pe_ratio": info.get("trailingPE"),
            "dividend_yield": info.get("dividendYield"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
        }
    except Exception as exc:
        logger.error("Failed to fetch info for %s: %s", yf_symbol, exc)
        return None


def fetch_current_price(symbol: str) -> Optional[float]:
    """Fetch the current/last price for a symbol."""
    if yf is None:
        return None

    yf_symbol = _resolve_symbol(symbol)
    try:
        ticker = yf.Ticker(yf_symbol)
        data = ticker.history(period="1d")
        if data is not None and not data.empty:
            return float(data["Close"].iloc[-1])
    except Exception as exc:
        logger.error("Failed to fetch price for %s: %s", yf_symbol, exc)
    return None


def compute_technical_indicators(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    Compute technical indicators on OHLCV data.

    Adds: ema_fast, ema_slow, rsi, macd, macd_signal, sma_20, bb_upper, bb_lower,
          stochastic_k, stochastic_d, atr
    """
    if df is None or df.empty or "close" not in df.columns:
        return None

    df = df.copy()

    # EMA
    df["ema_fast"] = df["close"].ewm(span=12, adjust=False).mean()
    df["ema_slow"] = df["close"].ewm(span=26, adjust=False).mean()

    # SMA 20
    df["sma_20"] = df["close"].rolling(window=20).mean()

    # Bollinger Bands
    df["bb_std"] = df["close"].rolling(window=20).std()
    df["bb_upper"] = df["sma_20"] + 2 * df["bb_std"]
    df["bb_lower"] = df["sma_20"] - 2 * df["bb_std"]

    # MACD
    df["macd"] = df["ema_fast"] - df["ema_slow"]
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()

    # RSI (14-period)
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    df["rsi"] = 100 - (100 / (1 + rs))

    # Stochastic Oscillator (14, 3, 3)
    low_14 = df["low"].rolling(window=14).min()
    high_14 = df["high"].rolling(window=14).max()
    df["stochastic_k"] = 100 * (df["close"] - low_14) / (high_14 - low_14 + 1e-10)
    df["stochastic_d"] = df["stochastic_k"].rolling(window=3).mean()

    # ATR (14-period)
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df["atr"] = true_range.rolling(window=14).mean()

    return df
