"""Historical-only backtesting engine isolated from live execution."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import yfinance as yf

from trading_system.config.models import BacktestMetrics, BacktestRequest, BacktestResult

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class SimTrade:
    """One simulated trade record."""

    symbol: str
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    return_pct: float
    strategy: str


class BacktestingSkill:
    """
    Backtesting engine supporting EMA, RSI, and custom Pine-like strategies.

    Safety:
    - Uses only historical data providers.
    - Never calls broker/exchange endpoints.
    """

    def __init__(self, fee_bps: float = 5.0, slippage_bps: float = 3.0) -> None:
        self.fee_bps = fee_bps
        self.slippage_bps = slippage_bps

    async def run(
        self,
        request: BacktestRequest,
        pinescript_source: Optional[str] = None,
    ) -> BacktestResult:
        """Run full backtest including walk-forward testing."""
        historical = await self._load_multi_asset_data(request)
        if not historical:
            raise ValueError("No historical data loaded for requested symbols")

        trades: List[SimTrade] = []
        equity_curve: List[float] = [request.initial_capital]
        capital_per_symbol = request.initial_capital / max(len(historical), 1)

        for symbol, frame in historical.items():
            symbol_trades, symbol_equity = self._simulate_symbol(
                symbol=symbol,
                frame=frame,
                strategy_name=request.strategy_name,
                strategy_params=request.strategy_params,
                starting_capital=capital_per_symbol,
                pinescript_source=pinescript_source,
            )
            trades.extend(symbol_trades)
            equity_curve.extend(
                [
                    (equity_curve[-1] + (e - capital_per_symbol))
                    for e in symbol_equity[1:]
                ]
            )

        metrics = self._compute_metrics(
            trades=trades,
            equity_curve=equity_curve,
            initial_capital=request.initial_capital,
        )
        walk_forward = self._walk_forward_report(
            historical=historical,
            request=request,
            pinescript_source=pinescript_source,
        )

        return BacktestResult(
            request=request,
            metrics=metrics,
            trades=[asdict(t) for t in trades],
            equity_curve=equity_curve,
            walk_forward=walk_forward,
        )

    async def _load_multi_asset_data(self, request: BacktestRequest) -> Dict[str, pd.DataFrame]:
        """Load historical bars for all symbols."""
        end = request.end or datetime.now(timezone.utc)
        start = request.start or (end - timedelta(days=request.lookback_days))
        tasks = [
            asyncio.to_thread(
                yf.download,
                tickers=symbol,
                start=start,
                end=end,
                interval=request.timeframe,
                auto_adjust=False,
                progress=False,
            )
            for symbol in request.symbols
        ]
        data = await asyncio.gather(*tasks, return_exceptions=True)
        output: Dict[str, pd.DataFrame] = {}
        for symbol, frame in zip(request.symbols, data):
            if isinstance(frame, Exception):
                logger.exception("Failed loading historical data symbol=%s", symbol, exc_info=frame)
                continue
            if frame.empty:
                logger.warning("No historical bars for symbol=%s", symbol)
                continue
            normalized = self._normalize_yfinance_frame(frame)
            output[symbol] = normalized.dropna().copy()
        return output

    def _normalize_yfinance_frame(self, frame: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize yfinance output into a single-index column DataFrame with a numeric Close series.

        yfinance can return MultiIndex columns or a Close DataFrame; both break float(row["Close"]).
        """
        df = frame.copy()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [str(col[0]) for col in df.columns]
        if "Close" not in df:
            raise ValueError("Historical frame missing Close column.")
        close_obj = df["Close"]
        if isinstance(close_obj, pd.DataFrame):
            close_obj = close_obj.iloc[:, 0]
        close = pd.to_numeric(close_obj, errors="coerce")
        if close.empty:
            raise ValueError("Historical frame Close series is empty.")
        df = df.loc[close.dropna().index].copy()
        df["Close"] = close.loc[df.index]
        return df

    def _simulate_symbol(
        self,
        symbol: str,
        frame: pd.DataFrame,
        strategy_name: str,
        strategy_params: Dict[str, Any],
        starting_capital: float,
        pinescript_source: Optional[str],
    ) -> Tuple[List[SimTrade], List[float]]:
        """Run one-symbol historical simulation."""
        df = frame.copy()
        signals = self._build_signals(df, strategy_name, strategy_params, pinescript_source)
        # Execute at next bar close to reduce lookahead bias.
        signals["entry"] = signals["entry"].shift(1).fillna(False)
        signals["exit"] = signals["exit"].shift(1).fillna(False)

        capital = starting_capital
        equity_curve = [capital]
        trades: List[SimTrade] = []
        position_qty = 0.0
        entry_price = 0.0
        entry_time: Optional[datetime] = None

        for idx, row in signals.iterrows():
            close_val = row["Close"]
            if isinstance(close_val, pd.Series):
                close_val = close_val.iloc[0]
            close_price = float(close_val)
            if position_qty == 0 and bool(row["entry"]):
                qty = max(capital // close_price, 0)
                if qty <= 0:
                    equity_curve.append(capital)
                    continue
                executed_price = self._apply_costs(close_price, side="buy")
                position_qty = float(qty)
                entry_price = executed_price
                entry_time = pd.Timestamp(idx).to_pydatetime()
            elif position_qty > 0 and bool(row["exit"]):
                executed_price = self._apply_costs(close_price, side="sell")
                gross_pnl = (executed_price - entry_price) * position_qty
                capital += gross_pnl
                trade = SimTrade(
                    symbol=symbol,
                    entry_time=entry_time or pd.Timestamp(idx).to_pydatetime(),
                    exit_time=pd.Timestamp(idx).to_pydatetime(),
                    entry_price=entry_price,
                    exit_price=executed_price,
                    quantity=position_qty,
                    pnl=gross_pnl,
                    return_pct=(gross_pnl / (entry_price * position_qty)) * 100 if position_qty else 0.0,
                    strategy=strategy_name,
                )
                trades.append(trade)
                position_qty = 0.0
                entry_price = 0.0
                entry_time = None
            # Mark-to-market equity.
            if position_qty > 0:
                mtm = capital + (close_price - entry_price) * position_qty
                equity_curve.append(float(mtm))
            else:
                equity_curve.append(float(capital))

        # Force close at final bar if still open.
        if position_qty > 0:
            tail_close = signals["Close"].iloc[-1]
            if isinstance(tail_close, pd.Series):
                tail_close = tail_close.iloc[0]
            final_price = self._apply_costs(float(tail_close), side="sell")
            gross_pnl = (final_price - entry_price) * position_qty
            capital += gross_pnl
            trades.append(
                SimTrade(
                    symbol=symbol,
                    entry_time=entry_time or signals.index[-1].to_pydatetime(),
                    exit_time=signals.index[-1].to_pydatetime(),
                    entry_price=entry_price,
                    exit_price=final_price,
                    quantity=position_qty,
                    pnl=gross_pnl,
                    return_pct=(gross_pnl / (entry_price * position_qty)) * 100 if position_qty else 0.0,
                    strategy=strategy_name,
                )
            )
            equity_curve[-1] = capital

        return trades, equity_curve

    def _build_signals(
        self,
        df: pd.DataFrame,
        strategy_name: str,
        strategy_params: Dict[str, Any],
        pinescript_source: Optional[str],
    ) -> pd.DataFrame:
        """Create entry/exit boolean signals."""
        signals = df.copy()
        strategy = strategy_name.lower().strip()

        if strategy == "ema" or strategy == "ema_crossover":
            fast = int(strategy_params.get("fast", 21))
            slow = int(strategy_params.get("slow", 55))
            signals["ema_fast"] = signals["Close"].ewm(span=fast, adjust=False).mean()
            signals["ema_slow"] = signals["Close"].ewm(span=slow, adjust=False).mean()
            signals["entry"] = (signals["ema_fast"] > signals["ema_slow"]) & (
                signals["ema_fast"].shift(1) <= signals["ema_slow"].shift(1)
            )
            signals["exit"] = (signals["ema_fast"] < signals["ema_slow"]) & (
                signals["ema_fast"].shift(1) >= signals["ema_slow"].shift(1)
            )
            return signals

        if strategy == "rsi" or strategy == "rsi_reversion":
            period = int(strategy_params.get("period", 14))
            oversold = float(strategy_params.get("oversold", 30))
            mean_exit = float(strategy_params.get("exit", 55))
            rsi = self._rsi(signals["Close"], period=period)
            signals["rsi"] = rsi
            signals["entry"] = rsi < oversold
            signals["exit"] = rsi > mean_exit
            return signals

        if strategy in {"pinescript", "custom_pinescript"}:
            return self._pinescript_to_signals(signals, pinescript_source or "")

        raise ValueError(f"Unsupported strategy: {strategy_name}")

    def _pinescript_to_signals(self, frame: pd.DataFrame, script: str) -> pd.DataFrame:
        """
        Convert simple PineScript indicator patterns into entry/exit signals.

        This intentionally supports a constrained subset for deterministic backtests.
        """
        script_lower = script.lower()
        out = frame.copy()
        out["entry"] = False
        out["exit"] = False

        uses_ema = "ta.ema" in script_lower or "ema(" in script_lower
        uses_rsi = "ta.rsi" in script_lower or "rsi(" in script_lower

        if uses_ema:
            out["ema_fast"] = out["Close"].ewm(span=21, adjust=False).mean()
            out["ema_slow"] = out["Close"].ewm(span=55, adjust=False).mean()
            out["entry"] = (out["ema_fast"] > out["ema_slow"]) & (
                out["ema_fast"].shift(1) <= out["ema_slow"].shift(1)
            )
            out["exit"] = (out["ema_fast"] < out["ema_slow"]) & (
                out["ema_fast"].shift(1) >= out["ema_slow"].shift(1)
            )

        if uses_rsi:
            out["rsi"] = self._rsi(out["Close"], period=14)
            rsi_entry = out["rsi"] < 30
            rsi_exit = out["rsi"] > 60
            out["entry"] = out["entry"] | rsi_entry
            out["exit"] = out["exit"] | rsi_exit

        if not uses_ema and not uses_rsi:
            # Fallback rule if script has no known indicator.
            out["sma_short"] = out["Close"].rolling(10).mean()
            out["sma_long"] = out["Close"].rolling(30).mean()
            out["entry"] = out["sma_short"] > out["sma_long"]
            out["exit"] = out["sma_short"] < out["sma_long"]
        return out

    def _walk_forward_report(
        self,
        historical: Dict[str, pd.DataFrame],
        request: BacktestRequest,
        pinescript_source: Optional[str],
    ) -> List[Dict[str, Any]]:
        """Perform walk-forward evaluation by rolling windows."""
        windows = max(request.walk_forward_windows, 1)
        reports: List[Dict[str, Any]] = []
        for symbol, frame in historical.items():
            if len(frame) < windows * 20:
                continue
            split_size = len(frame) // windows
            for i in range(1, windows):
                train = frame.iloc[: i * split_size]
                test = frame.iloc[i * split_size : (i + 1) * split_size]
                if test.empty:
                    continue
                _, eq = self._simulate_symbol(
                    symbol=symbol,
                    frame=test,
                    strategy_name=request.strategy_name,
                    strategy_params=request.strategy_params,
                    starting_capital=request.initial_capital / max(len(historical), 1),
                    pinescript_source=pinescript_source,
                )
                ret = ((eq[-1] - eq[0]) / eq[0]) * 100 if eq and eq[0] else 0.0
                reports.append(
                    {
                        "symbol": symbol,
                        "window": i,
                        "train_bars": len(train),
                        "test_bars": len(test),
                        "test_return_pct": ret,
                    }
                )
        return reports

    def _compute_metrics(
        self,
        trades: List[SimTrade],
        equity_curve: List[float],
        initial_capital: float,
    ) -> BacktestMetrics:
        """Calculate required performance metrics."""
        if not trades:
            return BacktestMetrics()
        pnl_values = np.array([t.pnl for t in trades], dtype=float)
        wins = pnl_values[pnl_values > 0]
        losses = pnl_values[pnl_values < 0]
        total_trades = len(trades)
        win_rate = float((len(wins) / total_trades) * 100)
        gross_profit = float(wins.sum()) if len(wins) else 0.0
        gross_loss = float(abs(losses.sum())) if len(losses) else 0.0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")
        expectancy = float(np.mean(pnl_values))
        net_profit = float(pnl_values.sum())

        eq = np.array(equity_curve, dtype=float)
        returns = np.diff(eq) / np.where(eq[:-1] == 0, 1, eq[:-1])
        sharpe = 0.0
        if returns.size > 1 and np.std(returns) > 0:
            sharpe = float((np.mean(returns) / np.std(returns)) * np.sqrt(252))

        running_max = np.maximum.accumulate(eq)
        drawdowns = (eq - running_max) / np.where(running_max == 0, 1, running_max)
        max_drawdown = float(abs(np.min(drawdowns))) if drawdowns.size else 0.0
        total_return_pct = ((eq[-1] - initial_capital) / initial_capital) * 100 if initial_capital else 0.0

        return BacktestMetrics(
            total_trades=total_trades,
            win_rate=win_rate,
            sharpe_ratio=sharpe,
            max_drawdown=max_drawdown,
            profit_factor=profit_factor,
            expectancy=expectancy,
            net_profit=net_profit,
            total_return_pct=total_return_pct,
        )

    def _rsi(self, close: pd.Series, period: int = 14) -> pd.Series:
        """RSI implementation."""
        delta = close.diff()
        up = delta.clip(lower=0)
        down = (-delta).clip(lower=0)
        avg_up = up.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        avg_down = down.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        rs = avg_up / avg_down.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)

    def _apply_costs(self, price: float, side: str) -> float:
        """Apply fee and slippage costs to execution price."""
        fee = self.fee_bps / 10000
        slippage = self.slippage_bps / 10000
        if side == "buy":
            return price * (1 + fee + slippage)
        return price * (1 - fee - slippage)
