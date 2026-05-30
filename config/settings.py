"""Application settings and dependency-safe configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from trading_system.config.models import RiskLimits, TradingMode, redact_secret


class DatabaseSettings(BaseModel):
    """Database configuration."""

    url: str = Field(default="sqlite+aiosqlite:///./trading_system/data/trading_system.db")


class RedisSettings(BaseModel):
    """Optional Redis configuration."""

    enabled: bool = False
    url: str = "redis://localhost:6379/0"


class BrokerCredentials(BaseModel):
    """Credential bag for a broker account."""

    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    passphrase: Optional[str] = None
    account_id: Optional[str] = None
    sandbox: bool = True

    def safe_dict(self) -> Dict[str, Optional[str]]:
        """Return redacted credentials for diagnostics."""
        return {
            "api_key": redact_secret(self.api_key or ""),
            "api_secret": redact_secret(self.api_secret or ""),
            "passphrase": redact_secret(self.passphrase or ""),
            "account_id": redact_secret(self.account_id or ""),
            "sandbox": str(self.sandbox),
        }


class BrokerSettings(BaseModel):
    """Top-level broker settings."""

    default_live_broker: str = "binance"
    brokers: Dict[str, BrokerCredentials] = Field(default_factory=dict)


class ModelProviderSettings(BaseModel):
    """Provider configuration for model routing."""

    name: str
    model: str
    enabled: bool = True
    base_url: Optional[str] = None
    api_key_env: Optional[str] = None
    # Local models on low-RAM laptops can take time; default to 2 minutes.
    timeout_sec: int = int(os.getenv("OLLAMA_TIMEOUT_SEC", "120"))


class ModelRoutingSettings(BaseModel):
    """Ordered routing preference."""

    local_first: bool = True
    providers: List[ModelProviderSettings] = Field(
        default_factory=lambda: [
            ModelProviderSettings(
                name="ollama",
                model=os.getenv("OLLAMA_MODEL", "qwen2.5:3b"),
                enabled=True,
                base_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
            ),
            ModelProviderSettings(
                name="ollama",
                model=os.getenv("OLLAMA_FALLBACK", "deepseek-r1:7b"),
                enabled=True,
                base_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
            ),
            ModelProviderSettings(
                name="claude", model="claude-3-5-sonnet-latest", enabled=False, api_key_env="ANTHROPIC_API_KEY"
            ),
            ModelProviderSettings(
                name="openai", model="gpt-4o-mini", enabled=False, api_key_env="OPENAI_API_KEY"
            ),
        ]
    )


class ApiSettings(BaseModel):
    """API runtime settings."""

    host: str = "0.0.0.0"
    port: int = 8000
    telegram_webhook_secret: Optional[str] = None
    require_api_key: bool = False
    api_keys: List[str] = Field(default_factory=list)
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 120
    live_approval_ttl_seconds: int = 300


class AppSettings(BaseModel):
    """Global application settings."""

    app_name: str = "Institutional Multi-Agent Trading OS"
    env: str = "dev"
    default_mode: TradingMode = TradingMode.PAPER
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    brokers: BrokerSettings = Field(default_factory=BrokerSettings)
    risk_limits: RiskLimits = Field(default_factory=RiskLimits)
    model_routing: ModelRoutingSettings = Field(default_factory=ModelRoutingSettings)
    api: ApiSettings = Field(default_factory=ApiSettings)
    watchlist: List[str] = Field(default_factory=lambda: ["BTC/USDT", "ETH/USDT", "INFY.NS"])


def _env_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.lower() in {"1", "true", "yes", "on"}


def load_settings() -> AppSettings:
    """Load settings from environment variables with safe defaults."""
    env = os.getenv("TRADING_ENV", "dev")
    default_mode = TradingMode(os.getenv("TRADING_MODE", "paper"))
    db_url = os.getenv("TRADING_DB_URL", "sqlite+aiosqlite:///./trading_system/data/trading_system.db")
    redis_enabled = _env_bool("TRADING_REDIS_ENABLED", False)
    redis_url = os.getenv("TRADING_REDIS_URL", "redis://localhost:6379/0")

    broker_settings = BrokerSettings(
        default_live_broker=os.getenv("TRADING_DEFAULT_LIVE_BROKER", "binance"),
        brokers={
            "binance": BrokerCredentials(
                api_key=os.getenv("BINANCE_API_KEY"),
                api_secret=os.getenv("BINANCE_API_SECRET"),
                sandbox=_env_bool("BINANCE_SANDBOX", True),
            ),
            "alpaca": BrokerCredentials(
                api_key=os.getenv("ALPACA_API_KEY"),
                api_secret=os.getenv("ALPACA_API_SECRET"),
                account_id=os.getenv("ALPACA_ACCOUNT_ID"),
                sandbox=_env_bool("ALPACA_SANDBOX", True),
            ),
            "oanda": BrokerCredentials(
                api_key=os.getenv("OANDA_API_KEY"),
                account_id=os.getenv("OANDA_ACCOUNT_ID"),
                sandbox=_env_bool("OANDA_SANDBOX", True),
            ),
            # Upstox credentials are present for future integration.
            # Store access token in passphrase field for now.
            "upstox": BrokerCredentials(
                api_key=os.getenv("UPSTOX_API_KEY"),
                api_secret=os.getenv("UPSTOX_API_SECRET"),
                passphrase=os.getenv("UPSTOX_ACCESS_TOKEN"),
                sandbox=False,
            ),
        },
    )

    return AppSettings(
        env=env,
        default_mode=default_mode,
        database=DatabaseSettings(url=db_url),
        redis=RedisSettings(enabled=redis_enabled, url=redis_url),
        brokers=broker_settings,
        api=ApiSettings(
            host=os.getenv("TRADING_API_HOST", "0.0.0.0"),
            port=int(os.getenv("TRADING_API_PORT", "8000")),
            telegram_webhook_secret=os.getenv("TELEGRAM_WEBHOOK_SECRET"),
            require_api_key=_env_bool("TRADING_REQUIRE_API_KEY", False),
            api_keys=[k.strip() for k in os.getenv("TRADING_API_KEYS", "").split(",") if k.strip()],
            rate_limit_enabled=_env_bool("TRADING_RATE_LIMIT_ENABLED", True),
            rate_limit_requests_per_minute=int(os.getenv("TRADING_RATE_LIMIT_RPM", "120")),
            live_approval_ttl_seconds=int(os.getenv("TRADING_LIVE_APPROVAL_TTL_SECONDS", "300")),
        ),
    )


@dataclass(slots=True)
class DependencyContainer:
    """Simple dependency injection container."""

    settings: AppSettings
    event_bus: object
    global_state: object
    trade_memory: object
    reflexion_memory: object
    vector_memory: object
    risk_guardian: object
    execution_engine: object
    boss_agent: object
    live_approval_manager: object
