"""
Trading Dashboard - Database Models
SQLAlchemy ORM models for all tables
"""
import os
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import OperationalError

# ─── Database URL ────────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./trading_dashboard.db")

# Fix for Render PostgreSQL URLs
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ─── Engine ──────────────────────────────────────────────────────────────────
connect_args = {}
engine_kwargs = {"pool_pre_ping": True}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    engine_kwargs["pool_recycle"] = 180
    engine_kwargs["pool_size"] = 5
    engine_kwargs["max_overflow"] = 10

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ─── Models ──────────────────────────────────────────────────────────────────

class AgentState(Base):
    """Stores the latest status of each AI agent."""
    __tablename__ = "agent_states"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # Keep this unique, but avoid double-defining an index with the same name across upgrades.
    agent_id = Column(String(100), unique=True, nullable=False)
    status = Column(String(50), default="offline")  # online | idle | processing | error
    task = Column(String(500), default="Waiting...")
    progress = Column(Integer, default=0)  # 0-100
    skills = Column(Text, default="[]")  # JSON array of skill names
    cpu_percent = Column(Float, default=0.0)
    memory_mb = Column(Float, default=0.0)
    timestamp = Column(String(50), nullable=True)

    # NOTE: Do not define an explicit Index for agent_id here.
    # The unique constraint on agent_id is sufficient for lookups and avoids
    # "index ... already exists" errors on SQLite when schemas evolve.


class Strategy(Base):
    """Trading strategies with their parameters and metrics."""
    __tablename__ = "strategies"

    id = Column(String(100), primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    symbol = Column(String(20), nullable=False)
    timeframe = Column(String(10), default="4h")
    entry_rule = Column(Text, default="")
    exit_rule = Column(Text, default="")
    status = Column(String(50), default="paused")  # running | paused | backtesting
    pnl = Column(Float, default=0.0)
    pnl_percent = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    created_date = Column(String(50), nullable=True)
    last_trade = Column(String(50), nullable=True)

    __table_args__ = (
        Index("ix_strategies_symbol", "symbol"),
        Index("ix_strategies_status", "status"),
    )


class BacktestResult(Base):
    """Backtest execution results."""
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy_name = Column(String(200), nullable=False)
    symbol = Column(String(20), nullable=False)
    timeframe = Column(String(10), default="4h")
    total_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    pnl = Column(Float, default=0.0)
    pnl_percent = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    profit_factor = Column(Float, default=0.0)
    consecutive_losses = Column(Integer, default=0)
    csv_file = Column(String(300), nullable=True)
    created_at = Column(String(50), nullable=True)

    __table_args__ = (
        Index("ix_backtest_results_strategy", "strategy_name"),
        Index("ix_backtest_results_symbol", "symbol"),
    )


class Trade(Base):
    """Executed trades (paper and live)."""
    __tablename__ = "trades_executed"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(50), unique=True, index=True)
    symbol = Column(String(20), nullable=False)
    quantity = Column(Integer, default=0)
    entry_price = Column(Float, default=0.0)
    exit_price = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    broker = Column(String(50), default="upstox")
    mode = Column(String(20), default="paper")  # paper | live
    status = Column(String(50), default="open")  # open | filled | cancelled | rejected
    pnl = Column(Float, nullable=True)
    entry_time = Column(String(50), nullable=True)
    exit_time = Column(String(50), nullable=True)

    __table_args__ = (
        Index("ix_trades_symbol", "symbol"),
        Index("ix_trades_mode", "mode"),
        Index("ix_trades_status", "status"),
    )


class ApiKey(Base):
    """Broker API keys (encoded for storage)."""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    broker = Column(String(50), unique=True, index=True, nullable=False)
    api_key_encoded = Column(Text, nullable=False)
    secret_key_encoded = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    connected_date = Column(String(50), nullable=True)


class ChatHistory(Base):
    """Chat messages between user and AI."""
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), default="user", index=True)
    role = Column(String(20), nullable=False)  # user | assistant
    message = Column(Text, nullable=False)
    timestamp = Column(String(50), nullable=True)

    __table_args__ = (
        Index("ix_chat_history_user", "user_id"),
    )


class ScreenerResult(Base):
    """Stock screener cached results."""
    __tablename__ = "screener_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    pnl = Column(Float, default=0.0)
    pnl_percent = Column(Float, default=0.0)
    in_trade = Column(Boolean, default=False)
    condition = Column(String(20), default="HOLD")  # BUY | HOLD | SELL
    updated_date = Column(String(50), nullable=True)


class Settings(Base):
    """Application settings key-value store."""
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(Text, nullable=True)


class WatchlistStock(Base):
    """
    Watchlist entries stored in the dashboard DB.

    The continuous monitoring loop runs on the user's laptop (agents) and polls
    these records from the cloud dashboard.
    """

    __tablename__ = "watchlist_stocks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(32), unique=True, index=True, nullable=False)
    strategy_id = Column(String(100), default="default")
    auto_trade = Column(Boolean, default=False)
    status = Column(String(20), default="active")  # active | paused | removed
    added_date = Column(String(50), nullable=True)
    last_checked = Column(String(50), nullable=True)
    last_signal = Column(String(20), nullable=True)  # buy | sell | hold
    last_signal_price = Column(Float, nullable=True)
    quantity_to_buy = Column(Integer, default=1)

    __table_args__ = (
        Index("ix_watchlist_stocks_status", "status"),
    )


class TradeSignal(Base):
    """Trade signals pending approval (Telegram + dashboard)."""

    __tablename__ = "trade_signals"

    id = Column(String(64), primary_key=True, index=True)  # UUID string
    symbol = Column(String(32), index=True, nullable=False)
    strategy_id = Column(String(100), default="default")
    signal_type = Column(String(20), default="buy")  # buy | sell
    signal_price = Column(Float, default=0.0)
    signal_time = Column(String(50), nullable=True)

    technical_score = Column(Float, default=0.0)
    news_score = Column(Float, default=0.0)
    fundamental_score = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)

    approval_status = Column(String(20), default="pending")  # pending | approved | skipped | rejected
    approval_time = Column(String(50), nullable=True)
    approval_reason = Column(Text, nullable=True)

    order_id = Column(String(64), nullable=True)
    execution_price = Column(Float, nullable=True)
    execution_time = Column(String(50), nullable=True)

    __table_args__ = (
        Index("ix_trade_signals_approval_status", "approval_status"),
        Index("ix_trade_signals_signal_time", "signal_time"),
    )


class IdempotencyKey(Base):
    """
    Persistent idempotency store for broker orders.

    This prevents accidental duplicate orders when clients retry a request.
    """

    __tablename__ = "idempotency_keys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_order_id = Column(String(80), unique=True, index=True, nullable=False)
    broker = Column(String(50), default="upstox")
    status = Column(String(30), default="pending")  # pending | completed | failed
    broker_order_id = Column(String(80), nullable=True)
    request_payload = Column(Text, nullable=True)
    created_at = Column(String(50), nullable=True)


class Position(Base):
    """Centralized position snapshots (single source of truth for the dashboard)."""

    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    broker = Column(String(50), default="upstox", index=True)
    symbol = Column(String(32), index=True, nullable=False)
    side = Column(String(10), default="long")  # long | short
    quantity = Column(Integer, default=0)
    avg_entry_price = Column(Float, default=0.0)
    current_price = Column(Float, default=0.0)
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    last_updated = Column(String(50), nullable=True)

    __table_args__ = (
        Index("ix_positions_symbol", "symbol"),
        Index("ix_positions_broker_symbol", "broker", "symbol"),
        UniqueConstraint("broker", "symbol", name="uq_positions_broker_symbol"),
    )


class WatchlistAlert(Base):
    """Alerts emitted by agents and optionally sent to Telegram."""

    __tablename__ = "watchlist_alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(32), index=True, nullable=False)
    alert_type = Column(String(50), default="signal_alert")
    alert_message = Column(Text, nullable=False)
    alert_time = Column(String(50), nullable=True)
    telegram_sent = Column(Boolean, default=False)
    telegram_message_id = Column(String(64), nullable=True)


def init_db() -> None:
    """Create all tables if they don't exist (safe to call on startup)."""
    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError as exc:
        # SQLite in particular can raise "index ... already exists" if schema evolved
        # across deploys and SQLAlchemy's index existence detection is out of sync.
        # This dashboard can tolerate missing/extra indexes; prefer booting.
        msg = str(exc).lower()
        if DATABASE_URL.startswith("sqlite") and "index" in msg and "already exists" in msg:
            return
        raise
