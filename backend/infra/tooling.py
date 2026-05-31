"""Infrastructure configuration helpers for Ollama, Sentry, and related tools."""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    import sentry_sdk
except ImportError:  # Optional dependency.
    sentry_sdk = None  # type: ignore[assignment]


@dataclass(frozen=True, slots=True)
class ToolingConfig:
    """Resolved tooling configuration for the dashboard runtime."""

    ollama_url: str
    ollama_model: str
    ollama_fallback: str
    database_url: str
    sentry_dsn: str
    sentry_environment: str
    sentry_traces_sample_rate: float
    healthcheck_path: str


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _env_float(name: str, default: float) -> float:
    raw = _env(name, "")
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def load_tooling_config() -> ToolingConfig:
    """Load tool defaults from environment variables."""

    database_url = _env("DATABASE_URL") or _env("SUPABASE_DATABASE_URL")
    return ToolingConfig(
        ollama_url=_env("OLLAMA_URL", "http://127.0.0.1:11434"),
        ollama_model=_env("OLLAMA_MODEL", "qwen2.5:3b"),
        ollama_fallback=_env("OLLAMA_FALLBACK", "deepseek-r1:7b"),
        database_url=database_url,
        sentry_dsn=_env("SENTRY_DSN"),
        sentry_environment=_env("SENTRY_ENVIRONMENT", _env("TRADING_ENV", "local")),
        sentry_traces_sample_rate=_env_float("SENTRY_TRACES_SAMPLE_RATE", 0.0),
        healthcheck_path=_env("HEALTHCHECK_PATH", "/health"),
    )


def init_sentry(config: ToolingConfig | None = None) -> bool:
    """Initialize Sentry if a DSN is configured."""

    cfg = config or load_tooling_config()
    if not cfg.sentry_dsn:
        return False
    if sentry_sdk is None:
        logger.warning("sentry-sdk is not installed; skipping Sentry initialization")
        return False

    sentry_sdk.init(
        dsn=cfg.sentry_dsn,
        environment=cfg.sentry_environment,
        traces_sample_rate=max(0.0, cfg.sentry_traces_sample_rate),
        send_default_pii=False,
    )
    logger.info("Sentry initialized for environment=%s", cfg.sentry_environment)
    return True

