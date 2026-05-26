from __future__ import annotations

import gzip
import json
import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx


DEFAULT_MASTER_URL = "https://assets.upstox.com/market-quote/instruments/exchange/complete.json.gz"


def _ensure_dir(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)


@dataclass(slots=True)
class SymbolMasterService:
    """
    Lightweight, DB-backed Upstox instrument master cache.

    We intentionally use sqlite3 directly here to avoid:
    - bloating the main dashboard DB with millions of instrument rows
    - long migrations on Render
    """

    db_path: Path
    master_url: str = DEFAULT_MASTER_URL

    def __post_init__(self) -> None:
        _ensure_dir(self.db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(str(self.db_path))
        con.row_factory = sqlite3.Row
        return con

    def _init_db(self) -> None:
        con = self._connect()
        try:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS instrument_master (
                    instrument_key TEXT PRIMARY KEY,
                    trading_symbol TEXT,
                    name TEXT,
                    exchange TEXT,
                    segment TEXT,
                    instrument_type TEXT,
                    expiry TEXT,
                    strike REAL,
                    option_type TEXT,
                    lot_size INTEGER,
                    tick_size REAL,
                    isin TEXT
                )
                """
            )
            con.execute("CREATE INDEX IF NOT EXISTS ix_inst_symbol ON instrument_master(trading_symbol)")
            con.execute("CREATE INDEX IF NOT EXISTS ix_inst_name ON instrument_master(name)")
            con.execute("CREATE INDEX IF NOT EXISTS ix_inst_exchange_segment ON instrument_master(exchange, segment)")
            con.commit()
        finally:
            con.close()

    async def download_and_refresh(self) -> Dict[str, Any]:
        """
        Downloads the Upstox master file and refreshes the local sqlite cache.
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
            # In case Upstox returns plain JSON in some environments
            decompressed = raw

        instruments = json.loads(decompressed.decode("utf-8"))
        if not isinstance(instruments, list):
            raise ValueError("Instrument master response is not a list")

        con = self._connect()
        try:
            con.execute("DELETE FROM instrument_master")
            con.commit()

            rows = []
            for item in instruments:
                # Defensive parsing: Upstox keys vary by segment/type.
                rows.append(
                    (
                        str(item.get("instrument_key") or ""),
                        str(item.get("trading_symbol") or ""),
                        str(item.get("name") or ""),
                        str(item.get("exchange") or ""),
                        str(item.get("segment") or ""),
                        str(item.get("instrument_type") or ""),
                        item.get("expiry"),
                        item.get("strike"),
                        item.get("option_type"),
                        int(item.get("lot_size") or 1),
                        float(item.get("tick_size") or 0.05),
                        item.get("isin"),
                    )
                )

            con.executemany(
                """
                INSERT INTO instrument_master (
                    instrument_key, trading_symbol, name, exchange, segment, instrument_type,
                    expiry, strike, option_type, lot_size, tick_size, isin
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
            con.commit()
        finally:
            con.close()

        return {"ok": True, "count": len(instruments), "db_path": str(self.db_path)}

    def get_instrument_key(
        self,
        symbol: str,
        exchange: str = "NSE",
        segment: str = "EQ",
    ) -> Optional[str]:
        sym = (symbol or "").strip().upper()
        if not sym:
            return None
        con = self._connect()
        try:
            row = con.execute(
                """
                SELECT instrument_key
                FROM instrument_master
                WHERE trading_symbol = ? AND exchange = ? AND segment = ?
                LIMIT 1
                """,
                (sym, exchange, segment),
            ).fetchone()
            return str(row["instrument_key"]) if row else None
        finally:
            con.close()

    def search_symbols(self, query: str, exchange: str = "NSE", limit: int = 10) -> List[Dict[str, Any]]:
        q = (query or "").strip()
        if not q:
            return []
        like = f"%{q.upper()}%"
        con = self._connect()
        try:
            rows = con.execute(
                """
                SELECT trading_symbol, name, instrument_key, segment
                FROM instrument_master
                WHERE exchange = ?
                  AND (UPPER(trading_symbol) LIKE ? OR UPPER(name) LIKE ?)
                LIMIT ?
                """,
                (exchange, like, like, int(limit)),
            ).fetchall()
            return [
                {
                    "symbol": str(r["trading_symbol"]),
                    "name": str(r["name"]),
                    "instrument_key": str(r["instrument_key"]),
                    "segment": str(r["segment"]),
                }
                for r in rows
            ]
        finally:
            con.close()


def build_symbol_master() -> SymbolMasterService:
    # Default path works on Render (ephemeral FS). For persistence, mount a disk and point to it.
    db_path = Path(os.getenv("SYMBOL_MASTER_DB_PATH", "./data/upstox_instruments.db"))
    return SymbolMasterService(db_path=db_path)

