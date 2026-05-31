"""Domain models for the trading operating system."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from decimal import Decimal
from typing import Any, Dict, List, Optional, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class TradingMode(str, Enum):
    """Execution mode for hard isolation of environments."""

    BACKTEST = "backtest"
    PAPER = "paper"
    LIVE = "live"


class OrderSide(str, Enum):
    """Side of an order."""

    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    """Supported order types."""

    MARKET = "market"
    LIMIT = "limit"


class RiskDecision(str, Enum):
    """Decision returned by Risk Guardian."""
    APPROVED = "approved"
    REJECTED = "rejected"


class OrderState(str, Enum):
    """12 states for order lifecycle in HERMES v5.2."""
    CREATED = "CREATED"
    RISK_APPROVED = "RISK_APPROVED"
    SUBMITTED = "SUBMITTED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
    MODIFIED = "MODIFIED"
    CANCEL_PENDING = "CANCEL_PENDING"
    EXPIRED = "EXPIRED"


class CommandIntentType(str, Enum):
    """Supported natural-language command intents."""

    ANALYZE = "analyze"
    BACKTEST = "backtest"
    PLACE_ORDER = "place_order"
    WHALE_ACTIVITY = "whale_activity"
    CURRENT_RISK = "current_risk"
    APPROVE_LIVE = "approve_live"
    UNKNOWN = "unknown"


class RiskLimits(BaseModel):
    """Hard risk limits with conservative defaults."""

    max_daily_loss: float = Field(default=50.0, gt=0)
    max_exposure: float = Field(default=100.0, gt=0)
    max_leverage: float = Field(default=2.0, ge=1.0)
    max_symbol_exposure_pct: float = Field(default=10.0, gt=0, le=100)  # Spec: 10%
    max_sector_exposure_pct: float = Field(default=25.0, gt=0, le=100)  # Spec: 25%
    max_slippage_bps: float = Field(default=35.0, gt=0)
    max_consecutive_losses: int = Field(default=4, gt=0)
    max_correlation: float = Field(default=0.70, ge=0, le=1)  # Spec: 0.70 normal
    min_stop_loss_pct: float = Field(default=0.2, gt=0)
    max_stop_loss_pct: float = Field(default=8.0, gt=0)
    max_strategy_capacity: float = Field(default=1000000.0, gt=0)
    min_volume_percentile: float = Field(default=0.1, ge=0, le=1)
    max_order_adv_pct: float = Field(default=0.1, ge=0, le=1)
    account_health_required: bool = True
    required_approval_weight: int = Field(default=3, gt=0) # HERMES v5.2 spec


class Signal(BaseModel):
    """Trading signal emitted by research/strategy layers."""

    symbol: str
    timeframe: str
    direction: OrderSide
    confidence: float = Field(ge=0, le=1)
    source_agent: str
    reason: str
    price: float = Field(gt=0)
    strategy_id: str = Field(default="default")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OrderRequest(BaseModel):
    """Canonical order request model used across all brokers."""

    symbol: str
    side: OrderSide
    quantity: float = Field(gt=0)
    mode: TradingMode
    broker: str = Field(default="paper")
    order_type: OrderType = Field(default=OrderType.MARKET)
    limit_price: Optional[float] = Field(default=None, gt=0)
    stop_loss: Optional[float] = Field(default=None, gt=0)
    take_profit: Optional[float] = Field(default=None, gt=0)
    leverage: float = Field(default=1.0, ge=1.0)
    expected_slippage_bps: float = Field(default=10.0, ge=0)
    signal_id: Optional[str] = None
    correlation_group: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("limit_price")
    @classmethod
    def validate_limit_price_for_limit_orders(
        cls, value: Optional[float], info: Any
    ) -> Optional[float]:
        """Ensure limit price exists for limit orders."""
        order_type = info.data.get("order_type")
        if order_type == OrderType.LIMIT and value is None:
            raise ValueError("limit_price is required for limit orders")
        return value


class RiskCheckResult(BaseModel):
    """Result of risk evaluation for an order request."""

    decision: RiskDecision
    reasons: List[str] = Field(default_factory=list)
    limits: RiskLimits
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExecutionResult(BaseModel):
    """Order execution output for paper/live brokers."""

    accepted: bool
    mode: TradingMode
    broker: str
    order_id: Optional[str] = None
    symbol: str
    side: OrderSide
    quantity: float
    average_price: Optional[float] = None
    status: str = "rejected"
    message: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)
    executed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CommandIntent(BaseModel):
    """Structured intent parsed from natural-language command."""

    intent: CommandIntentType
    raw_command: str
    symbol: Optional[str] = None
    timeframe: Optional[str] = None
    lookback: Optional[str] = None
    quantity: Optional[float] = None
    mode: Optional[TradingMode] = None
    side: Optional[OrderSide] = None
    strategy: Optional[str] = None
    extra: Dict[str, Any] = Field(default_factory=dict)


class BacktestRequest(BaseModel):
    """Backtest request shape."""

    symbols: List[str]
    timeframe: str = "1d"
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    lookback_days: int = Field(default=180, gt=10)
    strategy_name: str = "ema_crossover"
    strategy_params: Dict[str, Any] = Field(default_factory=dict)
    initial_capital: float = Field(default=100000.0, gt=0)
    walk_forward_windows: int = Field(default=3, gt=0)


class BacktestMetrics(BaseModel):
    """Standard performance metrics for evaluation."""

    total_trades: int = 0
    win_rate: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    profit_factor: float = 0.0
    expectancy: float = 0.0
    net_profit: float = 0.0
    total_return_pct: float = 0.0


class BacktestResult(BaseModel):
    """Backtest result container."""

    request: BacktestRequest
    metrics: BacktestMetrics
    trades: List[Dict[str, Any]] = Field(default_factory=list)
    equity_curve: List[float] = Field(default_factory=list)
    walk_forward: List[Dict[str, Any]] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelRouteRequest(BaseModel):
    """Prompt routing input for multi-model dispatch."""

    task: str
    prompt: str
    prefer_local: bool = True
    max_tokens: int = 1200
    temperature: float = 0.1


class ModelRouteDecision(BaseModel):
    """Selected model/provider."""

    provider: str
    model: str
    reason: str


@dataclass(slots=True)
class PortfolioSnapshot:
    """Shared snapshot for risk checks and reporting."""

    mode: TradingMode
    balance: float
    available_cash: float
    daily_realized_pnl: float
    gross_exposure: float
    positions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    consecutive_losses: int = 0
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def redact_secret(value: str, visible: int = 4) -> str:
    """Redact secrets for safe logs."""
    if not value:
        return ""
    if len(value) <= visible:
        return "*" * len(value)
    hidden = "*" * (len(value) - visible)
    return f"{hidden}{value[-visible:]}"


from decimal import Decimal

class HermesEvent(BaseModel):
    """Universal event schema for HERMES v5.2."""
    event_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: UUID = Field(default_factory=uuid4)
    source_component: str
    source_instance: str
    version: int = 2
    account_id: Optional[UUID] = None
    signature: Optional[str] = None
    payload: Dict[str, Any]


# --- Research Events ---
class StrategyGeneratedPayload(BaseModel):
    genome: str  # Base64-encoded strategy genome (PineScript, Python, etc.)
    genome_hash: str  # SHA-256 of genome
    parent_genome_hash: Optional[str] = None
    hypothesis_id: Optional[str] = None
    sector: str
    category: str
    regime: str
    generated_at: datetime
    outbox_id: int

class StrategyGenerated(HermesEvent):
    event_type: Literal["STRATEGY_GENERATED"] = "STRATEGY_GENERATED"
    payload: StrategyGeneratedPayload


# --- Validation Events ---
class ValidationPassedPayload(BaseModel):
    genome_hash: str
    backtest_id: int
    sharpe_ratio: Decimal
    max_drawdown_pct: Decimal
    total_trades: int
    oos_sharpe_ratio: Decimal
    walk_forward_efficiency: Decimal
    monte_carlo_95th_dd: Decimal
    parameter_stability_score: Decimal
    benchmark_alpha: Decimal
    benchmark_beta: Decimal
    information_ratio: Decimal
    after_tax_alpha: Decimal
    paper_drift_pct: Optional[Decimal] = None
    similarity_score: Decimal
    validation_duration_ms: int
    validated_at: datetime

class ValidationPassed(HermesEvent):
    event_type: Literal["VALIDATION_PASSED"] = "VALIDATION_PASSED"
    payload: ValidationPassedPayload


class ValidationFailedPayload(BaseModel):
    genome_hash: str
    backtest_id: int
    failure_reason: str
    failed_metric: Optional[str] = None
    failed_value: Optional[Decimal] = None
    required_threshold: Optional[Decimal] = None
    validation_duration_ms: int
    validated_at: datetime

class ValidationFailed(HermesEvent):
    event_type: Literal["VALIDATION_FAILED"] = "VALIDATION_FAILED"
    payload: ValidationFailedPayload


# --- Core Execution Events ---
class SignalEmitted(HermesEvent):
    """Event published by Runtime Adapter."""
    event_type: Literal["SIGNAL_EMITTED"] = "SIGNAL_EMITTED"


class RiskCheckRequested(HermesEvent):
    """Event published by BossAgent to RiskGuardian."""
    event_type: Literal["RISK_CHECK_REQUESTED"] = "RISK_CHECK_REQUESTED"


class RiskApproved(HermesEvent):
    """Event published by RiskGuardian."""
    event_type: Literal["RISK_APPROVED"] = "RISK_APPROVED"


class RiskRejected(HermesEvent):
    """Event published by RiskGuardian."""
    event_type: Literal["RISK_REJECTED"] = "RISK_REJECTED"


class ExecutionCommand(HermesEvent):
    """Event published by BossAgent to TradeExecutor."""
    event_type: Literal["EXECUTION_COMMAND"] = "EXECUTION_COMMAND"


# --- Registry Events ---
class ApproverRecord(BaseModel):
    approver_id: UUID
    weight: int
    timestamp: datetime
    signature: str # Ed25519 of approval record


class StrategyApprovedPayload(BaseModel):
    strategy_id: UUID
    genome_hash: str
    version: int
    bytecode: str  # Base64
    bytecode_checksum: str
    regime_params: Dict[str, Any]
    max_capacity_rupees: Decimal
    sector: str
    category: str
    approved_at: datetime
    approvers: List[ApproverRecord]
    quorum_weight: int
    required_weight: int
    hot_swap: bool = False  # If True, Runtime Adapter must hot-swap immediately

class StrategyApproved(HermesEvent):
    event_type: Literal["STRATEGY_APPROVED"] = "STRATEGY_APPROVED"
    payload: StrategyApprovedPayload


class RegistryRollbackPayload(BaseModel):
    strategy_id: UUID
    previous_version_id: UUID
    new_version_id: UUID
    reason: str
    rolled_back_at: datetime
    hot_swap: bool = True

class RegistryRollback(HermesEvent):
    event_type: Literal["REGISTRY_ROLLBACK"] = "REGISTRY_ROLLBACK"
    payload: RegistryRollbackPayload


class OrderSubmitted(HermesEvent):
    """Event published by TradeExecutor."""
    event_type: Literal["ORDER_SUBMITTED"] = "ORDER_SUBMITTED"


class OrderFilled(HermesEvent):
    """Event published by TradeExecutor."""
    event_type: Literal["ORDER_FILLED"] = "ORDER_FILLED"


class OrderRejected(HermesEvent):
    """Event published by TradeExecutor."""
    event_type: Literal["ORDER_REJECTED"] = "ORDER_REJECTED"


class KillSwitchTriggered(HermesEvent):
    """Universal emergency halt event."""
    event_type: Literal["KILL_SWITCH_TRIGGERED"] = "KILL_SWITCH_TRIGGERED"
