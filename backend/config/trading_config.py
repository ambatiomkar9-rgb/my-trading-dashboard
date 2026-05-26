from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class TradingFlags:
    """
    Kill switch + safety flags.

    IMPORTANT:
    - Render deployments are stateless across restarts; persist kill switch state in DB if needed.
    - This module provides a process-level default + env override.
    """

    trading_enabled: bool = os.getenv("TRADING_ENABLED", "true").strip().lower() in {"1", "true", "yes", "on"}


FLAGS = TradingFlags()


def is_trading_enabled() -> bool:
    return bool(FLAGS.trading_enabled)


def enable_trading() -> None:
    FLAGS.trading_enabled = True


def disable_trading() -> None:
    FLAGS.trading_enabled = False

