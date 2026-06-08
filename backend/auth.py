"""Dashboard JWT helpers and FastAPI authentication dependencies."""
from __future__ import annotations

import hmac
import logging
import os
from typing import Optional

from fastapi import Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

try:
    from backend.security.jwt_auth import JwtAuth, load_jwt_auth  # type: ignore
except ModuleNotFoundError:  # noqa: BLE001
    from security.jwt_auth import JwtAuth, load_jwt_auth  # type: ignore

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


def _get_auth() -> Optional[JwtAuth]:
    try:
        return load_jwt_auth()
    except Exception as exc:  # noqa: BLE001
        logger.error("JWT auth loader failed: %s", exc)
        return None


def create_token(username: str, role: str = "user") -> str:
    """Create a signed JWT for the supplied username."""
    auth = _get_auth()
    if not auth:
        raise RuntimeError("JWT_SECRET_KEY is not configured")
    return auth.create_token(username, role=role)


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT. Returns None if invalid."""
    try:
        auth = _get_auth()
        if not auth:
            return None
        return auth.verify_token(token)
    except Exception as exc:  # noqa: BLE001
        logger.debug("decode_token failed: %s", exc)
        return None


async def verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    """FastAPI dependency that extracts and validates a Bearer token."""
    try:
        if not credentials:
            raise HTTPException(status_code=401, detail="Not authenticated")
        payload = decode_token(credentials.credentials)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return {"username": payload.get("sub", ""), "role": payload.get("role", "user")}
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc


async def require_admin(user: dict = Depends(verify_token)) -> dict:
    """Dependency that enforces admin role."""
    if str(user.get("role") or "") != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return user


async def verify_token_or_service(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    """Verify a JWT or accept DASHBOARD_API_TOKEN as a service bearer token."""
    try:
        if not credentials:
            raise HTTPException(status_code=401, detail="Not authenticated")
        # Try JWT first
        payload = decode_token(credentials.credentials)
        if payload:
            return {"username": payload.get("sub", ""), "role": payload.get("role", "user")}
        # Fall back to service token (constant-time comparison to prevent timing attacks)
        service_token = os.getenv("DASHBOARD_API_TOKEN", "").strip()
        if service_token and hmac.compare_digest(credentials.credentials, service_token):
            return {"username": "service", "role": "admin"}
        admin_key = os.getenv("ADMIN_API_KEY", "").strip()
        if admin_key and hmac.compare_digest(credentials.credentials, admin_key):
            return {"username": "service", "role": "admin"}
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc

