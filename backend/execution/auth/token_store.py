from __future__ import annotations

import os
import sqlite3
import time
from pathlib import Path

from cryptography.fernet import Fernet

DB_PATH = Path(os.getenv("BROKER_TOKEN_DB_PATH", "data/broker_tokens.db"))
KEY_PATH = Path(os.getenv("BROKER_TOKEN_KEY_PATH", "data/.token_key"))


class TokenStore:
    """
    Encrypted token store using Fernet.

    Notes:
    - This encrypts tokens at rest. The encryption key is stored on disk (KEY_PATH).
      For production, prefer storing KEY_PATH on a persistent disk and protect it
      with OS permissions / secret management.
    - SQLite is used for simplicity. If you run multiple workers, use a real DB.
    """

    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        KEY_PATH.parent.mkdir(parents=True, exist_ok=True)

        if KEY_PATH.exists():
            self._key = KEY_PATH.read_bytes()
        else:
            self._key = Fernet.generate_key()
            KEY_PATH.write_bytes(self._key)
            try:
                os.chmod(KEY_PATH, 0o600)
            except Exception:
                pass

        self._cipher = Fernet(self._key)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(str(DB_PATH))

    def _init_db(self):
        con = self._connect()
        try:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS broker_tokens (
                    broker      TEXT PRIMARY KEY,
                    access_enc  TEXT NOT NULL,
                    refresh_enc TEXT NOT NULL,
                    expires_at  INTEGER NOT NULL,
                    updated_at  INTEGER NOT NULL
                )
                """
            )
            con.commit()
        finally:
            con.close()

    def save(self, broker: str, access_token: str, refresh_token: str, expires_in: int = 86400):
        broker = (broker or "").strip().lower()
        if not broker:
            raise ValueError("broker is required")
        if not access_token:
            raise ValueError("access_token is required")

        enc_a = self._cipher.encrypt(access_token.encode("utf-8")).decode("utf-8")
        enc_r = self._cipher.encrypt((refresh_token or "").encode("utf-8")).decode("utf-8")
        now = int(time.time())

        con = self._connect()
        try:
            con.execute(
                """
                INSERT INTO broker_tokens (broker, access_enc, refresh_enc, expires_at, updated_at)
                VALUES (?,?,?,?,?)
                ON CONFLICT(broker) DO UPDATE SET
                    access_enc=excluded.access_enc,
                    refresh_enc=excluded.refresh_enc,
                    expires_at=excluded.expires_at,
                    updated_at=excluded.updated_at
                """,
                (broker, enc_a, enc_r, now + int(expires_in or 0), now),
            )
            con.commit()
        finally:
            con.close()

    def get(self, broker: str) -> dict | None:
        broker = (broker or "").strip().lower()
        if not broker:
            return None

        con = self._connect()
        try:
            row = con.execute(
                "SELECT access_enc, refresh_enc, expires_at FROM broker_tokens WHERE broker=?",
                (broker,),
            ).fetchone()
        finally:
            con.close()

        if not row:
            return None

        return {
            "access_token": self._cipher.decrypt(row[0].encode("utf-8")).decode("utf-8"),
            "refresh_token": self._cipher.decrypt(row[1].encode("utf-8")).decode("utf-8"),
            "expires_at": int(row[2]),
        }

    def is_expired(self, broker: str, buffer_sec: int = 300) -> bool:
        row = self.get(broker)
        if not row:
            return True
        return int(time.time()) >= int(row["expires_at"]) - int(buffer_sec or 0)

    def delete(self, broker: str):
        broker = (broker or "").strip().lower()
        if not broker:
            return
        con = self._connect()
        try:
            con.execute("DELETE FROM broker_tokens WHERE broker=?", (broker,))
            con.commit()
        finally:
            con.close()

