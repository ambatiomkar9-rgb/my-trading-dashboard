"""Single source of truth for local positions, fills, and PnL calculations."""
from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Optional

logger = logging.getLogger(__name__)


def _normalize_symbol(symbol: str) -> str:
    return (symbol or "").upper().replace(".NS", "").replace(".BO", "").strip()


class PositionManager:
    """PostgreSQL-backed position ledger shared by local agents."""

    def __init__(self) -> None:
        self._cache: dict[str, dict] = {}
        self._lock = asyncio.Lock()
        self._load_from_db()

    def _get_session(self):
        from backend.database import SessionLocal
        return SessionLocal()

    def _load_from_db(self) -> None:
        try:
            from backend.database import engine
            from sqlalchemy import text

            with engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM positions"))
                rows = result.mappings().all()
            for row in rows:
                key = f"{str(row['broker']).lower()}_{_normalize_symbol(str(row['symbol']))}"
                self._cache[key] = {
                    "broker": str(row["broker"]).lower(),
                    "symbol": _normalize_symbol(str(row["symbol"])),
                    "side": str(row["side"] or "flat").lower(),
                    "quantity": int(row["quantity"] or 0),
                    "avg_entry": float(row["avg_entry_price"] or 0.0),
                    "current_price": float(row["current_price"] or 0.0),
                    "unrealized_pnl": float(row["unrealized_pnl"] or 0.0),
                    "realized_pnl": float(row["realized_pnl"] or 0.0),
                }
            logger.info("Loaded %d positions from DB", len(self._cache))
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not load positions from DB: %s", exc)

    @staticmethod
    def _weighted_average(existing_qty: int, existing_price: float, added_qty: int, added_price: float) -> float:
        total_qty = existing_qty + added_qty
        if total_qty == 0:
            return float(added_price)
        return ((existing_qty * existing_price) + (added_qty * added_price)) / total_qty

    def _apply_buy_fill(self, pos: dict, quantity: int, fill_price: float) -> None:
        current_qty = int(pos["quantity"])
        if current_qty >= 0:
            new_qty = current_qty + quantity
            pos["avg_entry"] = self._weighted_average(current_qty, float(pos["avg_entry"]), quantity, fill_price) if new_qty else fill_price
            pos["quantity"] = new_qty
            pos["side"] = "long" if new_qty > 0 else "flat"
        else:
            short_qty = abs(current_qty)
            covered_qty = min(short_qty, quantity)
            pos["realized_pnl"] += (float(pos["avg_entry"]) - fill_price) * covered_qty
            new_qty = current_qty + quantity
            if new_qty < 0:
                pos["quantity"] = new_qty
                pos["side"] = "short"
            elif new_qty == 0:
                pos["quantity"] = 0
                pos["side"] = "flat"
            else:
                pos["quantity"] = new_qty
                pos["avg_entry"] = fill_price
                pos["side"] = "long"
        pos["current_price"] = fill_price

    def _apply_sell_fill(self, pos: dict, quantity: int, fill_price: float) -> None:
        current_qty = int(pos["quantity"])
        if current_qty > 0:
            closed_qty = min(current_qty, quantity)
            pos["realized_pnl"] += (fill_price - float(pos["avg_entry"])) * closed_qty
            new_qty = current_qty - quantity
            if new_qty > 0:
                pos["quantity"] = new_qty
                pos["side"] = "long"
            elif new_qty == 0:
                pos["quantity"] = 0
                pos["side"] = "flat"
            else:
                pos["quantity"] = new_qty
                pos["avg_entry"] = fill_price
                pos["side"] = "short"
        elif current_qty == 0:
            logger.warning("Sell rejected: no position to sell for %s", pos.get("symbol"))
            return
        else:
            short_qty = abs(current_qty)
            new_short_qty = short_qty + quantity
            if new_short_qty > 100:
                logger.warning("Sell rejected: naked short would exceed 100 shares for %s", pos.get("symbol"))
                return
            if current_qty < 0:
                pos["avg_entry"] = self._weighted_average(short_qty, float(pos["avg_entry"]), quantity, fill_price)
            pos["quantity"] = -new_short_qty
            pos["side"] = "short"
        pos["current_price"] = fill_price

    async def on_fill(
        self,
        broker: str,
        symbol: str,
        side: str,
        quantity: int,
        fill_price: float,
    ) -> None:
        """Apply a broker-confirmed fill to the local position ledger."""
        try:
            async with self._lock:
                broker_name = (broker or "").lower().strip()
                sym = _normalize_symbol(symbol)
                fill_qty = abs(int(quantity))
                fill_price = float(fill_price)
                key = f"{broker_name}_{sym}"
                pos = self._cache.get(key)
                if not pos:
                    pos = {
                        "broker": broker_name,
                        "symbol": sym,
                        "side": "flat",
                        "quantity": 0,
                        "avg_entry": fill_price,
                        "current_price": fill_price,
                        "unrealized_pnl": 0.0,
                        "realized_pnl": 0.0,
                    }
                    self._cache[key] = pos

                if str(side).lower().strip() == "buy":
                    self._apply_buy_fill(pos, fill_qty, fill_price)
                else:
                    self._apply_sell_fill(pos, fill_qty, fill_price)

                await self._save(key)
                logger.info("Position updated: %s %s qty=%d", broker_name, sym, pos["quantity"])
        except Exception as exc:  # noqa: BLE001
            logger.error("on_fill failed: %s", exc)

    async def on_price_update(self, symbol: str, price: float) -> None:
        """Update unrealized PnL for any positions matching the symbol."""
        try:
            async with self._lock:
                sym = _normalize_symbol(symbol)
                for pos in self._cache.values():
                    if pos["symbol"] != sym or int(pos["quantity"]) == 0:
                        continue
                    pos["current_price"] = float(price)
                    qty = int(pos["quantity"])
                    if qty > 0:
                        pos["unrealized_pnl"] = (float(price) - float(pos["avg_entry"])) * qty
                    else:
                        pos["unrealized_pnl"] = (float(pos["avg_entry"]) - float(price)) * abs(qty)
        except Exception as exc:  # noqa: BLE001
            logger.error("on_price_update failed: %s", exc)

    def get_position(self, broker: str, symbol: str) -> Optional[dict]:
        """Fetch one position from cache."""
        key = f"{(broker or '').lower().strip()}_{_normalize_symbol(symbol)}"
        return self._cache.get(key)

    def get_all(self, broker: Optional[str] = None) -> list[dict]:
        """Return all positions, optionally filtered by broker."""
        if broker:
            broker_name = broker.lower().strip()
            return [pos for pos in self._cache.values() if pos["broker"] == broker_name]
        return list(self._cache.values())

    def get_total_exposure(self, broker: Optional[str] = None) -> float:
        """Return gross exposure for all positions."""
        positions = self.get_all(broker)
        return sum(abs(int(pos["quantity"])) * float(pos["current_price"] or pos["avg_entry"]) for pos in positions)

    def get_net_pnl(self, broker: Optional[str] = None) -> float:
        """Return realized + unrealized PnL."""
        positions = self.get_all(broker)
        return sum(float(pos["realized_pnl"]) + float(pos["unrealized_pnl"]) for pos in positions)

    async def reconcile(self, broker: str, broker_positions: list[dict]) -> list[dict]:
        """Compare local positions with broker-reported positions."""
        discrepancies: list[dict] = []
        try:
            broker_name = broker.lower().strip()
            broker_map: dict[str, dict] = {}
            for remote in broker_positions or []:
                sym = _normalize_symbol(str(remote.get("symbol") or remote.get("trading_symbol") or ""))
                if sym:
                    broker_map[sym] = remote

            for local in self._cache.values():
                if local["broker"] != broker_name:
                    continue
                sym = local["symbol"]
                remote = broker_map.get(sym)
                if not remote:
                    if int(local["quantity"]) != 0:
                        discrepancies.append(
                            {"symbol": sym, "issue": "missing_at_broker", "local": int(local["quantity"]), "broker": 0}
                        )
                    continue
                remote_qty = int(remote.get("quantity") or remote.get("qty") or 0)
                if remote_qty != int(local["quantity"]):
                    discrepancies.append(
                        {"symbol": sym, "issue": "quantity_mismatch", "local": int(local["quantity"]), "broker": remote_qty}
                    )

            for sym, remote in broker_map.items():
                if not any(pos["broker"] == broker_name and pos["symbol"] == sym for pos in self._cache.values()):
                    remote_qty = int(remote.get("quantity") or remote.get("qty") or 0)
                    if remote_qty != 0:
                        discrepancies.append(
                            {"symbol": sym, "issue": "missing_locally", "local": 0, "broker": remote_qty}
                        )

            if discrepancies:
                logger.warning("Reconciliation found %d discrepancies", len(discrepancies))
            return discrepancies
        except Exception as exc:  # noqa: BLE001
            logger.error("reconcile failed: %s", exc)
            return [{"issue": "reconcile_error", "error": str(exc)}]

    async def _save(self, key: str) -> None:
        """Persist a cached position row to PostgreSQL."""
        try:
            pos = self._cache[key]
            from backend.database import engine
            from sqlalchemy import text

            now = int(time.time())
            with engine.connect() as conn:
                conn.execute(
                    text("""
                        INSERT INTO positions (
                            broker, symbol, side, quantity, avg_entry_price, current_price,
                            unrealized_pnl, realized_pnl, last_updated
                        ) VALUES (:broker, :symbol, :side, :quantity, :avg_entry, :current_price,
                                  :unrealized_pnl, :realized_pnl, :last_updated)
                        ON CONFLICT (broker, symbol) DO UPDATE SET
                            side=EXCLUDED.side,
                            quantity=EXCLUDED.quantity,
                            avg_entry_price=EXCLUDED.avg_entry_price,
                            current_price=EXCLUDED.current_price,
                            unrealized_pnl=EXCLUDED.unrealized_pnl,
                            realized_pnl=EXCLUDED.realized_pnl,
                            last_updated=EXCLUDED.last_updated
                    """),
                    {
                        "broker": pos["broker"],
                        "symbol": pos["symbol"],
                        "side": pos["side"],
                        "quantity": int(pos["quantity"]),
                        "avg_entry": float(pos["avg_entry"]),
                        "current_price": float(pos["current_price"]),
                        "unrealized_pnl": float(pos["unrealized_pnl"]),
                        "realized_pnl": float(pos["realized_pnl"]),
                        "last_updated": now,
                    },
                )
                conn.commit()
        except Exception as exc:  # noqa: BLE001
            logger.error("_save failed: %s", exc)
