from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def _now() -> int:
    return int(time.time())


@dataclass(slots=True)
class JwtConfig:
    secret_key: str
    issuer: str = "trading-dashboard"
    algorithm: str = "HS256"
    access_token_ttl_sec: int = 3600


class JwtAuth:
    """
    Minimal HS256 JWT implementation (no external dependencies).

    This is intentionally small so deployments don't fail due to missing crypto libs.
    """

    def __init__(self, cfg: JwtConfig):
        if not cfg.secret_key:
            raise ValueError("JWT secret key is empty")
        self.cfg = cfg

    def create_token(self, subject: str, role: str = "user", extra: Optional[Dict[str, Any]] = None) -> str:
        header = {"alg": self.cfg.algorithm, "typ": "JWT"}
        payload: Dict[str, Any] = {
            "sub": subject,
            "role": role,
            "iss": self.cfg.issuer,
            "iat": _now(),
            "exp": _now() + int(self.cfg.access_token_ttl_sec),
        }
        if extra:
            payload.update(extra)

        h = _b64url_encode(json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8"))
        p = _b64url_encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
        sig = self._sign(f"{h}.{p}".encode("ascii"))
        return f"{h}.{p}.{sig}"

    def verify_token(self, token: str) -> Dict[str, Any]:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid token format")
        h, p, sig = parts
        signing_input = f"{h}.{p}".encode("ascii")
        expected = self._sign(signing_input)
        if not hmac.compare_digest(expected, sig):
            raise ValueError("Invalid token signature")

        payload = json.loads(_b64url_decode(p).decode("utf-8"))
        exp = int(payload.get("exp") or 0)
        if exp and _now() >= exp:
            raise ValueError("Token expired")
        if payload.get("iss") != self.cfg.issuer:
            raise ValueError("Invalid issuer")
        return payload

    def _sign(self, signing_input: bytes) -> str:
        if self.cfg.algorithm != "HS256":
            raise ValueError("Only HS256 is supported")
        mac = hmac.new(self.cfg.secret_key.encode("utf-8"), signing_input, hashlib.sha256).digest()
        return _b64url_encode(mac)


def load_jwt_auth() -> Optional[JwtAuth]:
    secret = os.getenv("JWT_SECRET_KEY", "").strip()
    if not secret:
        return None
    ttl = int(os.getenv("JWT_ACCESS_TTL_SEC", "3600"))
    issuer = os.getenv("JWT_ISSUER", "trading-dashboard")
    return JwtAuth(JwtConfig(secret_key=secret, access_token_ttl_sec=ttl, issuer=issuer))

