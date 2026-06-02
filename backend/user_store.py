"""PostgreSQL-backed dashboard user store with password hashing and admin bootstrap."""
from __future__ import annotations

import hashlib
import logging
import os
import secrets
import time
from typing import Optional

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.exc import IntegrityError

from backend.database import Base, SessionLocal

logger = logging.getLogger(__name__)
PBKDF2_ITERS = int(os.getenv("PASSWORD_HASH_ITERATIONS", "210000"))


class User(Base):
    __tablename__ = "dashboard_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    salt = Column(Text, nullable=False)
    role = Column(String(20), nullable=False, default="user")
    created_at = Column(Integer, nullable=True)
    last_login = Column(Integer, nullable=True)


def _ensure_table() -> None:
    from backend.database import engine
    User.__table__.create(engine, checkfirst=True)


def _normalize_username(username: str) -> str:
    return (username or "").strip().lower()


def _hash(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERS,
    ).hex()


def create_user(username: str, password: str, role: str = "user") -> bool:
    _ensure_table()
    session = SessionLocal()
    try:
        uname = _normalize_username(username)
        if not uname or not password:
            return False
        salt = secrets.token_hex(16)
        password_hash = _hash(password, salt)
        session.add(User(
            username=uname,
            password_hash=password_hash,
            salt=salt,
            role=str(role or "user"),
            created_at=int(time.time()),
        ))
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False
    except Exception as exc:
        logger.error("create_user failed: %s", exc)
        session.rollback()
        return False
    finally:
        session.close()


def verify_user(username: str, password: str) -> Optional[dict]:
    _ensure_table()
    session = SessionLocal()
    try:
        uname = _normalize_username(username)
        row = session.query(User).filter(User.username == uname).first()
        if not row:
            return None
        if _hash(password, str(row.salt)) != str(row.password_hash):
            return None
        row.last_login = int(time.time())
        session.commit()
        return {"id": int(row.id), "username": uname, "role": str(row.role or "user")}
    except Exception as exc:
        logger.error("verify_user failed: %s", exc)
        return None
    finally:
        session.close()


def update_password(username: str, new_password: str) -> bool:
    _ensure_table()
    session = SessionLocal()
    try:
        uname = _normalize_username(username)
        if not uname or not new_password:
            return False
        salt = secrets.token_hex(16)
        password_hash = _hash(new_password, salt)
        row = session.query(User).filter(User.username == uname).first()
        if not row:
            return False
        row.password_hash = password_hash
        row.salt = salt
        session.commit()
        return True
    except Exception as exc:
        logger.error("update_password failed: %s", exc)
        session.rollback()
        return False
    finally:
        session.close()


def ensure_default_admin() -> None:
    _ensure_table()
    session = SessionLocal()
    try:
        count = session.query(User).count()
        if count == 0:
            admin_pw = os.getenv("ADMIN_PASSWORD", "change-me-now")
            session.close()
            if create_user("admin", admin_pw, "admin"):
                logger.warning("Default admin created. Set ADMIN_PASSWORD env var to change it.")
    except Exception as exc:
        logger.error("ensure_default_admin failed: %s", exc)
    finally:
        try:
            session.close()
        except Exception:
            pass
