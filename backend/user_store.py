"""SQLite-backed dashboard user store with password hashing and admin bootstrap."""
from __future__ import annotations

import hashlib
import logging
import os
import secrets
import sqlite3
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)
DB_PATH = Path(os.getenv("USER_DB_PATH", "data/users.db"))
PBKDF2_ITERS = int(os.getenv("PASSWORD_HASH_ITERATIONS", "210000"))


def _normalize_username(username: str) -> str:
    return (username or "").strip().lower()


def _init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at INTEGER,
                last_login INTEGER
            )
            """
        )


def _hash(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERS,
    ).hex()


def create_user(username: str, password: str, role: str = "user") -> bool:
    """Create a user with a salted password hash."""
    _init_db()
    try:
        uname = _normalize_username(username)
        if not uname or not password:
            return False
        salt = secrets.token_hex(16)
        password_hash = _hash(password, salt)
        with sqlite3.connect(DB_PATH) as con:
            con.execute(
                """
                INSERT INTO users (username, password_hash, salt, role, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (uname, password_hash, salt, str(role or "user"), int(time.time())),
            )
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as exc:  # noqa: BLE001
        logger.error("create_user failed: %s", exc)
        return False


def verify_user(username: str, password: str) -> Optional[dict]:
    """Verify a username/password pair and return the user payload on success."""
    _init_db()
    try:
        uname = _normalize_username(username)
        with sqlite3.connect(DB_PATH) as con:
            row = con.execute(
                "SELECT id, password_hash, salt, role FROM users WHERE username=?",
                (uname,),
            ).fetchone()
        if not row:
            return None
        user_id, password_hash, salt, role = row
        if _hash(password, str(salt)) != str(password_hash):
            return None
        with sqlite3.connect(DB_PATH) as con:
            con.execute(
                "UPDATE users SET last_login=? WHERE id=?",
                (int(time.time()), int(user_id)),
            )
        return {"id": int(user_id), "username": uname, "role": str(role or "user")}
    except Exception as exc:  # noqa: BLE001
        logger.error("verify_user failed: %s", exc)
        return None


def update_password(username: str, new_password: str) -> bool:
    """Update an existing user's password."""
    _init_db()
    try:
        uname = _normalize_username(username)
        if not uname or not new_password:
            return False
        salt = secrets.token_hex(16)
        password_hash = _hash(new_password, salt)
        with sqlite3.connect(DB_PATH) as con:
            cur = con.execute(
                "UPDATE users SET password_hash=?, salt=? WHERE username=?",
                (password_hash, salt, uname),
            )
            return bool(cur.rowcount)
    except Exception as exc:  # noqa: BLE001
        logger.error("update_password failed: %s", exc)
        return False


def ensure_default_admin() -> None:
    """Create a default admin user if the database is empty."""
    _init_db()
    try:
        with sqlite3.connect(DB_PATH) as con:
            count = int(con.execute("SELECT COUNT(*) FROM users").fetchone()[0] or 0)
        if count == 0:
            admin_pw = os.getenv("ADMIN_PASSWORD", "change-me-now")
            if create_user("admin", admin_pw, "admin"):
                logger.warning("Default admin created. Set ADMIN_PASSWORD to replace the default password.")
    except Exception as exc:  # noqa: BLE001
        logger.error("ensure_default_admin failed: %s", exc)
