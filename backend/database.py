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
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ─── Database URL ────────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./trading_dashboard.db")

# Fix for Render PostgreSQL URLs
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ─── Engine ──────────────────────────────────────────────────────────────────
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ─── Models ──────────────────────────────────────────────────────────────────

class AgentState(Base):
    """Stores the latest status of each AI agent."""
    __tablename__ = "agent_states"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    agent_id = Column(String(100), unique=True, index=True, nullable=False)
    status = Column(String(50), default="offline")  # online | idle | processing | error
    task = Column(String(500), default="Waiting...")
    progress = Column(Integer, default=0)  # 0-100
    skills = Column(Text, default="[]")  # JSON array of skill names
    cpu_percent = Column(Float, default=0.0)
    memory_mb = Column(Float, default=0.0)
    timestamp = Column(String(50), nullable=True)

    __table_args__ = (
        Index("ix_agent_states_agent_id", "agent_id"),
    )


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