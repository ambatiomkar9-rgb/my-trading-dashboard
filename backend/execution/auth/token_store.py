"""PostgreSQL-backed encrypted broker token store."""
from __future__ import annotations

import logging
import os
import time

from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

KEY_PATH = os.getenv("BROKER_TOKEN_KEY_PATH", ".token_key")


class TokenStore:
    """
    Encrypted token store using Fernet + PostgreSQL.

    Tokens are encrypted at rest. The encryption key is stored on disk
    or loaded from the BROKER_TOKEN_KEY environment variable.
    """

    def __init__(self):
        key_env = os.getenv("BROKER_TOKEN_KEY", "").strip()
        if key_env:
            self._key = key_env.encode("utf-8") if isinstance(key_env, str) else key_env
        elif os.path.exists(KEY_PATH):
            with open(KEY_PATH, "rb") as f:
                self._key = f.read().strip()
        else:
            self._key = Fernet.generate_key()
            try:
                with open(KEY_PATH, "wb") as f:
                    f.write(self._key)
                os.chmod(KEY_PATH, 0o600)
            except Exception:
                pass

        self._cipher = Fernet(self._key)
        self._init_db()

    def _init_db(self):
        try:
            from backend.database import engine
            from sqlalchemy import text

            with engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS broker_tokens (
                        broker      VARCHAR(50) PRIMARY KEY,
                        access_enc  TEXT NOT NULL,
                        refresh_enc TEXT NOT NULL,
                        expires_at  BIGINT NOT NULL,
                        updated_at  BIGINT NOT NULL
                    )
                """))
                conn.commit()
        except Exception as exc:
            logger.error("TokenStore._init_db failed (tokens will be unavailable): %s", exc)

    def save(self, broker: str, access_token: str, refresh_token: str, expires_in: int = 86400):
        broker = (broker or "").strip().lower()
        if not broker:
            raise ValueError("broker is required")
        if not access_token:
            raise ValueError("access_token is required")

        enc_a = self._cipher.encrypt(access_token.encode("utf-8")).decode("utf-8")
        enc_r = self._cipher.encrypt((refresh_token or "").encode("utf-8")).decode("utf-8")
        now = int(time.time())

        try:
            from backend.database import engine
            from sqlalchemy import text

            with engine.connect() as conn:
                conn.execute(
                    text("""
                        INSERT INTO broker_tokens (broker, access_enc, refresh_enc, expires_at, updated_at)
                        VALUES (:broker, :access_enc, :refresh_enc, :expires_at, :updated_at)
                        ON CONFLICT (broker) DO UPDATE SET
                            access_enc=EXCLUDED.access_enc,
                            refresh_enc=EXCLUDED.refresh_enc,
                            expires_at=EXCLUDED.expires_at,
                            updated_at=EXCLUDED.updated_at
                    """),
                    {
                        "broker": broker,
                        "access_enc": enc_a,
                        "refresh_enc": enc_r,
                        "expires_at": now + int(expires_in or 0),
                        "updated_at": now,
                    },
                )
                conn.commit()
        except Exception as exc:
            logger.error("TokenStore.save failed for broker %s: %s", broker, exc)
            raise

    def get(self, broker: str) -> dict | None:
        broker = (broker or "").strip().lower()
        if not broker:
            return None

        try:
            from backend.database import engine
            from sqlalchemy import text

            with engine.connect() as conn:
                result = conn.execute(
                    text("SELECT access_enc, refresh_enc, expires_at FROM broker_tokens WHERE broker = :broker"),
                    {"broker": broker},
                )
                row = result.fetchone()
        except Exception as exc:
            logger.error("TokenStore.get failed for broker %s: %s", broker, exc)
            return None

        if not row:
            return None

        try:
            return {
                "access_token": self._cipher.decrypt(row[0].encode("utf-8")).decode("utf-8"),
                "refresh_token": self._cipher.decrypt(row[1].encode("utf-8")).decode("utf-8"),
                "expires_at": int(row[2]),
            }
        except Exception as exc:
            logger.error("TokenStore.get decrypt failed for broker %s: %s", broker, exc)
            return None

    def is_expired(self, broker: str, buffer_sec: int = 300) -> bool:
        row = self.get(broker)
        if not row:
            return True
        return int(time.time()) >= int(row["expires_at"]) - int(buffer_sec or 0)

    def delete(self, broker: str):
        broker = (broker or "").strip().lower()
        if not broker:
            return

        try:
            from backend.database import engine
            from sqlalchemy import text

            with engine.connect() as conn:
                conn.execute(text("DELETE FROM broker_tokens WHERE broker = :broker"), {"broker": broker})
                conn.commit()
        except Exception as exc:
            logger.error("TokenStore.delete failed for broker %s: %s", broker, exc)
