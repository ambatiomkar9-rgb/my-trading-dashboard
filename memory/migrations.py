"""HERMES v5.2 Database Migrations and Schema Setup."""

import asyncio
import logging
from pathlib import Path
import aiosqlite
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

async def run_migrations(sqlite_path: str):
    """
    Run HERMES v5.2 schema migrations.
    Matches Task 4.3 and 1.4 of the SPEC.
    """
    logger.info("Running HERMES v5.2 database migrations on %s", sqlite_path)
    
    async with aiosqlite.connect(sqlite_path) as db:
        # 1. Strategies Table (Task 4.3)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS strategies (
                id TEXT PRIMARY KEY,
                genome_hash TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL,
                version INTEGER NOT NULL DEFAULT 1,
                bytecode TEXT NOT NULL,
                bytecode_checksum TEXT NOT NULL,
                ed25519_signature TEXT NOT NULL,
                regime_params_json TEXT NOT NULL,
                max_capacity_rupees REAL NOT NULL,
                sector TEXT NOT NULL,
                category TEXT NOT NULL,
                approved_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                retired_at TEXT,
                retired_reason TEXT
            )
        """)

        # 2. Enhanced Orders Table (Task 4.3)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders_v2 (
                id TEXT PRIMARY KEY,
                client_order_id TEXT NOT NULL UNIQUE,
                broker_order_id TEXT,
                strategy_id TEXT NOT NULL,
                account_id TEXT NOT NULL,
                broker_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                qty REAL NOT NULL,
                price REAL NOT NULL,
                order_type TEXT NOT NULL,
                side TEXT NOT NULL,
                status TEXT NOT NULL,
                filled_qty REAL DEFAULT 0,
                remaining_qty REAL DEFAULT 0,
                fill_value REAL DEFAULT 0,
                correlation_id TEXT NOT NULL,
                risk_check_event_id TEXT,
                created_at TEXT NOT NULL,
                submitted_at TEXT,
                filled_at TEXT,
                cancelled_at TEXT,
                rejected_at TEXT
            )
        """)

        # 3. System State Table (Task 4.3 Singleton)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS system_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                kill_switch_active INTEGER DEFAULT 0,
                crisis_mode_active INTEGER DEFAULT 0,
                current_regime TEXT DEFAULT 'normal',
                trading_enabled INTEGER DEFAULT 0,
                market_open INTEGER DEFAULT 0,
                last_reconciliation_at TEXT,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Ensure singleton row exists
        await db.execute("""
            INSERT OR IGNORE INTO system_state (id, updated_at) 
            VALUES (1, ?)
        """, (datetime.now(timezone.utc).isoformat(),))

        # 4. Audit Logs (WORM-like implementation for SQLite)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                source_component TEXT NOT NULL,
                source_instance TEXT NOT NULL,
                correlation_id TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                previous_hash TEXT,
                current_hash TEXT,
                signature TEXT
            )
        """)

        # 5. Outbox for Research Isolation (Task 4.3)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS outbox (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                genome_hash TEXT NOT NULL,
                consumed INTEGER DEFAULT 0,
                consumed_at TEXT,
                retry_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)

        # 6. Positions Table (Task 4.3)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                broker_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                quantity REAL DEFAULT 0,
                avg_price REAL DEFAULT 0,
                side TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(account_id, broker_id, symbol)
            )
        """)

        # 7. Reconciliation Events (Task 4.7)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS reconciliation_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id TEXT NOT NULL,
                broker_id TEXT NOT NULL,
                mismatch_type TEXT NOT NULL,
                broker_value REAL,
                db_value REAL,
                difference_pct REAL,
                consecutive_failures INTEGER DEFAULT 0,
                timestamp TEXT NOT NULL
            )
        """)

        await db.commit()
    
    logger.info("Migrations completed successfully.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    db_path = str(Path(__file__).resolve().parents[1] / "data" / "trading_system.db")
    asyncio.run(run_migrations(db_path))
