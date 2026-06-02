from __future__ import annotations

import gzip
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx


DEFAULT_MASTER_URL = "https://assets.upstox.com/market-quote/instruments/exchange/complete.json.gz"


@dataclass(slots=True)
class SymbolMasterService:
    """PostgreSQL-backed Upstox instrument master cache."""

    master_url: str = DEFAULT_MASTER_URL

    def __post_init__(self) -> None:
        self._init_db()

    def _init_db(self) -> None:
        from backend.database import engine
        from sqlalchemy import text

        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS instrument_master (
                    instrument_key VARCHAR(100) PRIMARY KEY,
                    trading_symbol VARCHAR(100),
                    name VARCHAR(300),
                    exchange VARCHAR(20),
                    segment VARCHAR(20),
                    instrument_type VARCHAR(30),
                    expiry VARCHAR(20),
                    strike REAL,
                    option_type VARCHAR(10),
                    lot_size INTEGER DEFAULT 1,
                    tick_size REAL DEFAULT 0.05,
                    isin VARCHAR(20)
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_inst_symbol ON instrument_master(trading_symbol)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_inst_name ON instrument_master(name)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_inst_exchange_segment ON instrument_master(exchange, segment)"))
            conn.commit()

    async def download_and_refresh(self) -> Dict[str, Any]:
        """
        Downloads the Upstox master file and refreshes the local PG cache.
        This can take time; call from a background task or admin endpoint.
        """
        timeout = float(os.getenv("SYMBOL_MASTER_TIMEOUT_SEC", "60"))
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(self.master_url)
            r.raise_for_status()
            raw = r.content

        try:
            decompressed = gzip.decompress(raw)
        except Exception:
            decompressed = raw

        instruments = json.loads(decompressed.decode("utf-8"))
        if not isinstance(instruments, list):
            raise ValueError("Instrument master response is not a list")

        from backend.database import engine
        from sqlalchemy import text

        with engine.begin() as conn:
            conn.execute(text("DELETE FROM instrument_master"))

            rows = []
            for item in instruments:
                rows.append({
                    "instrument_key": str(item.get("instrument_key") or ""),
                    "trading_symbol": str(item.get("trading_symbol") or ""),
                    "name": str(item.get("name") or ""),
                    "exchange": str(item.get("exchange") or ""),
                    "segment": str(item.get("segment") or ""),
                    "instrument_type": str(item.get("instrument_type") or ""),
                    "expiry": item.get("expiry"),
                    "strike": item.get("strike"),
                    "option_type": item.get("option_type"),
                    "lot_size": int(item.get("lot_size") or 1),
                    "tick_size": float(item.get("tick_size") or 0.05),
                    "isin": item.get("isin"),
                })

            # Batch insert in chunks of 10000
            for i in range(0, len(rows), 10000):
                chunk = rows[i:i + 10000]
                conn.execute(
                    text("""
                        INSERT INTO instrument_master (
                            instrument_key, trading_symbol, name, exchange, segment, instrument_type,
                            expiry, strike, option_type, lot_size, tick_size, isin
                        ) VALUES (:instrument_key, :trading_symbol, :name, :exchange, :segment, :instrument_type,
                                  :expiry, :strike, :option_type, :lot_size, :tick_size, :isin)
                    """),
                    chunk,
                )

        return {"ok": True, "count": len(instruments)}

    def get_instrument_key(
        self,
        symbol: str,
        exchange: str = "NSE",
        segment: str = "EQ",
    ) -> Optional[str]:
        sym = (symbol or "").strip().upper()
        if not sym:
            return None

        from backend.database import engine
        from sqlalchemy import text

        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT instrument_key
                    FROM instrument_master
                    WHERE trading_symbol = :symbol AND exchange = :exchange AND segment = :segment
                    LIMIT 1
                """),
                {"symbol": sym, "exchange": exchange, "segment": segment},
            )
            row = result.fetchone()
        return str(row[0]) if row else None

    def search_symbols(self, query: str, exchange: str = "NSE", limit: int = 10) -> List[Dict[str, Any]]:
        q = (query or "").strip()
        if not q:
            return []
        like = f"%{q.upper()}%"

        from backend.database import engine
        from sqlalchemy import text

        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT trading_symbol, name, instrument_key, segment
                    FROM instrument_master
                    WHERE exchange = :exchange
                      AND (UPPER(trading_symbol) LIKE :like OR UPPER(name) LIKE :like)
                    LIMIT :limit
                """),
                {"exchange": exchange, "like": like, "limit": int(limit)},
            )
            rows = result.fetchall()
        return [
            {
                "symbol": str(r[0]),
                "name": str(r[1]),
                "instrument_key": str(r[2]),
                "segment": str(r[3]),
            }
            for r in rows
        ]


def build_symbol_master() -> SymbolMasterService:
    return SymbolMasterService()
