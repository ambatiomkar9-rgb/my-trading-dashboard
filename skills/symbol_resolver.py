"""Resolve human-friendly names into tradable symbols/tickers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict


def _canon(text: str) -> str:
    t = text.strip().lower()
    t = re.sub(r"[^a-z0-9]+", " ", t).strip()
    t = re.sub(r"\s+", " ", t)
    if t.startswith("the "):
        t = t[4:]
    return t


@dataclass(slots=True)
class SymbolResolver:
    """
    Resolve phrases like "tata motors" to ticker symbols like "TATAMOTORS.NS".

    This is intentionally conservative and small; expand as needed.
    """

    mapping: Dict[str, str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.mapping is None:
            self.mapping = {
                "tata motors": "TATAMOTORS.NS",
                "tata moters": "TATAMOTORS.NS",
                "tata motor": "TATAMOTORS.NS",
                "tatamotors": "TATAMOTORS.NS",
                "tata steel": "TATASTEEL.NS",
                "tata steeel": "TATASTEEL.NS",
                "tatasteel": "TATASTEEL.NS",
                "infosys": "INFY.NS",
                "infy": "INFY.NS",
                "reliance": "RELIANCE.NS",
                "nifty": "^NSEI",
                "bank nifty": "^NSEBANK",
                "btc": "BTC-USD",
                "bitcoin": "BTC-USD",
                "eth": "ETH-USD",
                "ethereum": "ETH-USD",
            }

    def resolve(self, raw: str) -> str:
        """Return best-effort resolved ticker."""
        text = raw.strip()
        if not text:
            return text
        # If it already looks like a ticker, keep it.
        if " " not in text:
            return text
        key = _canon(text)
        return self.mapping.get(key, text.replace(" ", ""))
