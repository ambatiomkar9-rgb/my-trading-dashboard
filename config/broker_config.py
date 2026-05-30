"""Broker adapter configuration and factory helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from trading_system.config.settings import AppSettings, BrokerCredentials


@dataclass(slots=True)
class BrokerAdapterConfig:
    """Runtime broker adapter configuration."""

    name: str
    credentials: BrokerCredentials
    supports_spot: bool = True
    supports_margin: bool = False
    supports_forex: bool = False
    supports_equities: bool = False
    ccxt_exchange_id: str | None = None


def load_broker_configs(settings: AppSettings) -> Dict[str, BrokerAdapterConfig]:
    """Build normalized adapter configs from app settings."""
    brokers = settings.brokers.brokers
    return {
        "binance": BrokerAdapterConfig(
            name="binance",
            credentials=brokers.get("binance", BrokerCredentials()),
            supports_spot=True,
            supports_margin=True,
            ccxt_exchange_id="binance",
        ),
        "alpaca": BrokerAdapterConfig(
            name="alpaca",
            credentials=brokers.get("alpaca", BrokerCredentials()),
            supports_equities=True,
            supports_spot=False,
            ccxt_exchange_id=None,
        ),
        "oanda": BrokerAdapterConfig(
            name="oanda",
            credentials=brokers.get("oanda", BrokerCredentials()),
            supports_forex=True,
            supports_spot=False,
            ccxt_exchange_id=None,
        ),
        # Upstox adapter currently a stub (execution will be rejected with a clear message)
        # until OAuth + order endpoints are wired.
        "upstox": BrokerAdapterConfig(
            name="upstox",
            credentials=brokers.get("upstox", BrokerCredentials()),
            supports_equities=True,
            supports_spot=False,
            ccxt_exchange_id=None,
        ),
    }
