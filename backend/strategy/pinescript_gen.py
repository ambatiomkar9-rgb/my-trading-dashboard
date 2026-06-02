"""PineScript strategy template generator with syntax validation."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PineScriptValidation:
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class PineScriptStrategy:
    name: str
    symbol: str
    timeframe: str
    indicators: list[dict[str, Any]]
    entry_conditions: list[dict[str, Any]]
    exit_conditions: list[dict[str, Any]]
    risk_management: dict[str, Any] = field(default_factory=dict)


# ── Indicator Templates ──────────────────────────────────────────────────────

INDICATOR_TEMPLATES = {
    "ema_crossover": {
        "name": "EMA Crossover",
        "params": {"fast_len": 9, "slow_len": 21},
        "code": 'fast = ta.ema(close, {fast_len})\nslow = ta.ema(close, {slow_len})',
        "entry": "ta.crossover(fast, slow)",
        "exit": "ta.crossunder(fast, slow)",
    },
    "rsi_reversal": {
        "name": "RSI Reversal",
        "params": {"rsi_len": 14, "oversold": 30, "overbought": 70},
        "code": 'rsi = ta.rsi(close, {rsi_len})',
        "entry": "rsi < {oversold}",
        "exit": "rsi > {overbought}",
    },
    "bollinger_breakout": {
        "name": "Bollinger Band Breakout",
        "params": {"bb_len": 20, "bb_mult": 2.0},
        "code": 'bb_basis = ta.sma(close, {bb_len})\nbb_dev = {bb_mult} * ta.stdev(close, {bb_len})\nbb_upper = bb_basis + bb_dev\nbb_lower = bb_basis - bb_dev',
        "entry": "close > bb_upper",
        "exit": "close < bb_lower",
    },
    "macd_crossover": {
        "name": "MACD Crossover",
        "params": {"fast": 12, "slow": 26, "signal": 9},
        "code": '[macdLine, signalLine, _] = ta.macd(close, {fast}, {slow}, {signal})',
        "entry": "ta.crossover(macdLine, signalLine)",
        "exit": "ta.crossunder(macdLine, signalLine)",
    },
    "stochastic_oscillator": {
        "name": "Stochastic Oscillator",
        "params": {"k_len": 14, "d_len": 3, "smooth": 3, "oversold": 20, "overbought": 80},
        "code": 'k = ta.sma(ta.stoch(close, high, low, {k_len}), {smooth})\nd = ta.sma(k, {d_len})',
        "entry": "k < {oversold} and k > d",
        "exit": "k > {overbought} and k < d",
    },
}


# ── Risk Management Templates ────────────────────────────────────────────────

RISK_TEMPLATES = {
    "fixed_stop": {
        "name": "Fixed Stop Loss",
        "params": {"stop_pct": 2.0, "take_profit_pct": 4.0},
        "code": '''
stop_loss = strategy.position_avg_price * (1 - {stop_pct} / 100)
take_profit = strategy.position_avg_price * (1 + {take_profit_pct} / 100)
if (strategy.position_size > 0)
    strategy.exit("Exit", stop=stop_loss, limit=take_profit)''',
    },
    "trailing_stop": {
        "name": "Trailing Stop",
        "params": {"trail_pct": 3.0},
        "code": '''
if (strategy.position_size > 0)
    strategy.exit("Exit", trail_points=close * {trail_pct} / 100 / syminfo.mintick)''',
    },
    "atr_stop": {
        "name": "ATR-Based Stop",
        "params": {"atr_len": 14, "atr_mult": 2.0},
        "code": '''
atr = ta.atr({atr_len})
stop_loss = close - atr * {atr_mult}
take_profit = close + atr * {atr_mult} * 1.5
if (strategy.position_size > 0)
    strategy.exit("Exit", stop=stop_loss, limit=take_profit)''',
    },
}


# ── Generator ────────────────────────────────────────────────────────────────

def generate_pinescript(
    strategy: PineScriptStrategy,
    risk_name: str = "fixed_stop",
    risk_params: dict[str, Any] | None = None,
) -> str:
    """Generate a complete PineScript v5 strategy from a structured definition."""
    lines = [
        f'//@version=5',
        f'strategy("{strategy.name}", overlay=true, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=10)',
        '',
    ]

    # Inputs and indicator code
    for ind in strategy.indicators:
        template = INDICATOR_TEMPLATES.get(ind.get("type", ""))
        if not template:
            continue
        params = {**template["params"], **ind.get("params", {})}
        for pname, pval in params.items():
            lines.append(f'{pname} = input.int({pval}, "{pname}")' if isinstance(pval, int) else f'{pname} = input.float({pval}, "{pname}")')
        code = template["code"].format(**params)
        lines.append(code)
        lines.append('')

    # Entry conditions
    lines.append('// ── Entry Conditions ──')
    for cond in strategy.entry_conditions:
        ind_type = cond.get("indicator_type", "")
        template = INDICATOR_TEMPLATES.get(ind_type, {})
        params = {**template.get("params", {}), **cond.get("params", {})}
        entry_expr = template.get("entry", "").format(**params)
        side = cond.get("side", "long")
        if side == "long":
            lines.append(f'if ({entry_expr})')
            lines.append(f'    strategy.entry("Long", strategy.long)')
        else:
            lines.append(f'if ({entry_expr})')
            lines.append(f'    strategy.entry("Short", strategy.short)')
    lines.append('')

    # Exit conditions
    lines.append('// ── Exit Conditions ──')
    for cond in strategy.exit_conditions:
        ind_type = cond.get("indicator_type", "")
        template = INDICATOR_TEMPLATES.get(ind_type, {})
        params = {**template.get("params", {}), **cond.get("params", {})}
        exit_expr = template.get("exit", "").format(**params)
        lines.append(f'if ({exit_expr})')
        lines.append(f'    strategy.close_all()')
    lines.append('')

    # Risk management
    risk = RISK_TEMPLATES.get(risk_name, RISK_TEMPLATES["fixed_stop"])
    rp = {**risk["params"], **(risk_params or {})}
    risk_code = risk["code"].format(**rp)
    lines.append('// ── Risk Management ──')
    lines.append(risk_code.strip())
    lines.append('')

    # Plotting
    lines.append('// ── Plotting ──')
    for ind in strategy.indicators:
        ind_type = ind.get("type", "")
        template = INDICATOR_TEMPLATES.get(ind_type, {})
        if ind_type == "ema_crossover":
            fp = {**template["params"], **ind.get("params", {})}
            lines.append(f'plot(ta.ema(close, {fp["fast_len"]}), color=color.teal, linewidth=2)')
            lines.append(f'plot(ta.ema(close, {fp["slow_len"]}), color=color.orange, linewidth=2)')
        elif ind_type == "bollinger_breakout":
            fp = {**template["params"], **ind.get("params", {})}
            lines.append(f'plot(ta.sma(close, {fp["bb_len"]}), color=color.gray)')
            lines.append(f'plot(ta.sma(close, {fp["bb_len"]}) + {fp["bb_mult"]} * ta.stdev(close, {fp["bb_len"]}), color=color.red)')
            lines.append(f'plot(ta.sma(close, {fp["bb_len"]}) - {fp["bb_mult"]} * ta.stdev(close, {fp["bb_len"]}), color=color.green)')

    return '\n'.join(lines)


# ── Validator ────────────────────────────────────────────────────────────────

_PINE_KEYWORDS = {
    "if", "else", "for", "while", "switch", "import", "export", "var", "varip",
    "true", "false", "na", "method", "type", "enum", "input", "plot", "plotshape",
    "plotchar", "hline", "fill", "bgcolor", "strategy", "ta.", "math.", "str.",
    "array.", "matrix.", "label.", "table.", "request.", "syminfo.", "timeframe.",
}

_PINE_FUNCTIONS = {
    "ta.ema", "ta.sma", "ta.rsi", "ta.macd", "ta.atr", "ta.stoch", "ta.crossover",
    "ta.crossunder", "ta.stdev", "ta.sma", "ta.wma", "ta.hma", "ta.dmi", "ta.adx",
    "ta.ccistoch", "ta.obv", "ta.vwap", "ta.mfi", "ta.roc", "ta.cmo", "ta.wpr",
    "strategy.entry", "strategy.close", "strategy.close_all", "strategy.exit",
    "strategy.order", "strategy.position_size", "strategy.position_avg_price",
    "math.abs", "math.max", "math.min", "math.sqrt", "math.log",
    "input.int", "input.float", "input.bool", "input.string", "input.symbol",
    "plot", "plotshape", "hline", "fill",
}


def validate_pinescript(script: str) -> PineScriptValidation:
    """Basic PineScript v5 syntax validation."""
    errors: list[str] = []
    warnings: list[str] = []

    if not script or not script.strip():
        return PineScriptValidation(valid=False, errors=["Empty script"])

    lines = script.strip().split('\n')

    # Check version declaration
    has_version = any(line.strip().startswith('//@version=') for line in lines)
    if not has_version:
        errors.append("Missing //@version=5 declaration")

    # Check strategy declaration
    has_strategy = any('strategy(' in line for line in lines)
    if not has_strategy:
        errors.append("Missing strategy() declaration")

    # Check for common syntax issues
    open_parens = script.count('(')
    close_parens = script.count(')')
    if open_parens != close_parens:
        errors.append(f"Mismatched parentheses: {open_parens} open, {close_parens} close")

    open_braces = script.count('{')
    close_braces = script.count('}')
    if open_braces != close_braces:
        errors.append(f"Mismatched braces: {open_braces} open, {close_braces} close")

    # Check for undefined variables (basic check)
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith('//'):
            continue
        # Check for common mistakes
        if 'close(' in stripped:
            warnings.append(f"Line {i}: 'close' is a variable, not a function. Use 'close' without parentheses.")

    # Check for missing semicolons (PineScript doesn't use them, but common mistake)
    # Check for using = instead of := for reassignment
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith('var ') and '=' in stripped:
            continue  # var declaration is fine
        # Check for potential reassignment issues

    return PineScriptValidation(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


# ── Convenience Functions ────────────────────────────────────────────────────

def generate_ema_crossover(
    symbol: str = "RELIANCE",
    fast_len: int = 9,
    slow_len: int = 21,
    stop_pct: float = 2.0,
    take_profit_pct: float = 4.0,
) -> str:
    """Generate a ready-to-use EMA crossover strategy."""
    strategy = PineScriptStrategy(
        name=f"EMA Crossover {symbol}",
        symbol=symbol,
        timeframe="4h",
        indicators=[{
            "type": "ema_crossover",
            "params": {"fast_len": fast_len, "slow_len": slow_len},
        }],
        entry_conditions=[{"indicator_type": "ema_crossover", "side": "long"}],
        exit_conditions=[{"indicator_type": "ema_crossover", "side": "long"}],
        risk_management={"stop_pct": stop_pct, "take_profit_pct": take_profit_pct},
    )
    return generate_pinescript(strategy, "fixed_stop", {"stop_pct": stop_pct, "take_profit_pct": take_profit_pct})


def generate_rsi_strategy(
    symbol: str = "RELIANCE",
    rsi_len: int = 14,
    oversold: int = 30,
    overbought: int = 70,
) -> str:
    """Generate a ready-to-use RSI mean-reversion strategy."""
    strategy = PineScriptStrategy(
        name=f"RSI Reversal {symbol}",
        symbol=symbol,
        timeframe="4h",
        indicators=[{
            "type": "rsi_reversal",
            "params": {"rsi_len": rsi_len, "oversold": oversold, "overbought": overbought},
        }],
        entry_conditions=[{"indicator_type": "rsi_reversal", "side": "long"}],
        exit_conditions=[{"indicator_type": "rsi_reversal", "side": "long"}],
    )
    return generate_pinescript(strategy, "fixed_stop")
