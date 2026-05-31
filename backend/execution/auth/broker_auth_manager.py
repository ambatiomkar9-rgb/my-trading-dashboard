from __future__ import annotations

from urllib.parse import urlencode

import httpx

from .token_store import TokenStore

UPSTOX_TOKEN_URL = "https://api.upstox.com/v2/login/authorization/token"


def _api_key() -> str:
    import os

    return os.getenv("UPSTOX_API_KEY", "").strip()


def _api_secret() -> str:
    import os

    return os.getenv("UPSTOX_API_SECRET", "").strip()


def _redirect_uri() -> str:
    import os

    return os.getenv("UPSTOX_REDIRECT_URI", "http://127.0.0.1:8000/broker-callback").strip()


class BrokerAuthManager:
    """
    Upstox OAuth helper.

    This manager:
    - Builds the login URL for authorization_code grant
    - Exchanges `code` for access/refresh tokens
    - Refreshes tokens when expired or after 401
    - Stores tokens encrypted at rest
    """

    def __init__(self, broker: str = "upstox"):
        self.broker = (broker or "upstox").strip().lower()
        self._store = TokenStore()

    def get_login_url(self) -> str:
        api_key = _api_key()
        if not api_key:
            return "https://api.upstox.com/v2/login/authorization/dialog"
        query = urlencode(
            {
                "response_type": "code",
                "client_id": api_key,
                "redirect_uri": _redirect_uri(),
            }
        )
        return f"https://api.upstox.com/v2/login/authorization/dialog?{query}"

    async def exchange_code(self, code: str) -> bool:
        api_key = _api_key()
        api_secret = _api_secret()
        redirect_uri = _redirect_uri()
        if not api_key or not api_secret:
            raise RuntimeError("UPSTOX_API_KEY/UPSTOX_API_SECRET not configured")
        code = (code or "").strip()
        if not code:
            return False

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                UPSTOX_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": api_key,
                    "client_secret": api_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
                headers={"Accept": "application/json"},
            )
            resp.raise_for_status()
            data = resp.json()

        access = data.get("access_token", "") or ""
        refresh = data.get("refresh_token", "") or ""
        exp = int(data.get("expires_in", 86400) or 86400)
        if not access:
            return False

        self._store.save(self.broker, access, refresh, exp)
        return True

    async def refresh(self) -> bool:
        api_key = _api_key()
        api_secret = _api_secret()
        if not api_key or not api_secret:
            raise RuntimeError("UPSTOX_API_KEY/UPSTOX_API_SECRET not configured")

        row = self._store.get(self.broker)
        if not row or not row.get("refresh_token"):
            return False

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                UPSTOX_TOKEN_URL,
                data={
                    "refresh_token": row["refresh_token"],
                    "client_id": api_key,
                    "client_secret": api_secret,
                    "grant_type": "refresh_token",
                },
                headers={"Accept": "application/json"},
            )
            if resp.status_code != 200:
                return False
            data = resp.json()

        access = data.get("access_token", "") or ""
        refresh = data.get("refresh_token", row["refresh_token"]) or row["refresh_token"]
        exp = int(data.get("expires_in", 86400) or 86400)
        if not access:
            return False

        self._store.save(self.broker, access, refresh, exp)
        return True

    async def get_access_token(self) -> str:
        if self._store.is_expired(self.broker):
            ok = await self.refresh()
            if not ok:
                raise RuntimeError(
                    "Upstox token expired and refresh failed. Visit /broker-login to re-authenticate."
                )
        row = self._store.get(self.broker)
        if not row or not row.get("access_token"):
            raise RuntimeError("Upstox not authenticated. Visit /broker-login.")
        return str(row["access_token"])

    def is_authenticated(self) -> bool:
        row = self._store.get(self.broker)
        return bool(row and row.get("access_token"))
