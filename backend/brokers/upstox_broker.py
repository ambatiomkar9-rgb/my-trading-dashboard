from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import httpx

try:
    # When executed as a module (repo root in sys.path)
    from backend.market_data.symbol_master_service import SymbolMasterService, build_symbol_master  # type: ignore
    from backend.execution.auth.broker_auth_manager import BrokerAuthManager  # type: ignore
except ModuleNotFoundError:  # noqa: BLE001
    # When executed from within backend/
    from market_data.symbol_master_service import SymbolMasterService, build_symbol_master  # type: ignore
    from execution.auth.broker_auth_manager import BrokerAuthManager  # type: ignore


class UpstoxError(RuntimeError):
    pass


@dataclass(slots=True)
class UpstoxBroker:
    """
    Async-first Upstox REST client.

    IMPORTANT:
    - This module is safe to deploy to Render, but you should only ENABLE live broker calls
      if you set secrets as Render environment variables.
    - OAuth refresh is supported when UPSTOX_API_KEY/UPSTOX_API_SECRET are configured and you
      have authenticated via /broker-login → /broker-callback.
    """

    # Backward-compatible token mode (env token). If empty, BrokerAuthManager is used.
    access_token: str = ""
    base_url: str = "https://api.upstox.com/v2"
    timeout_sec: float = 30.0
    connect_timeout_sec: float = 10.0
    max_retries: int = 3
    symbol_master: Optional[SymbolMasterService] = None
    # With slots=True, we must declare attributes we set in __post_init__.
    client: httpx.AsyncClient = field(init=False, repr=False)
    auth: BrokerAuthManager = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout_sec, connect=self.connect_timeout_sec),
            limits=httpx.Limits(max_connections=50, max_keepalive_connections=10),
            http2=True,
        )
        if self.symbol_master is None:
            self.symbol_master = build_symbol_master()
        self.auth = BrokerAuthManager("upstox")

    async def close(self) -> None:
        await self.client.aclose()

    async def _headers(self) -> Dict[str, str]:
        token = self.access_token.strip()
        if not token:
            token = await self.auth.get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def _request(self, method: str, path: str, **kwargs: Any) -> Dict[str, Any]:
        url = self.base_url.rstrip("/") + "/" + path.lstrip("/")
        last_exc: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                r = await self.client.request(method, url, headers=await self._headers(), **kwargs)
                if r.status_code == 401:
                    # If we are in OAuth mode, refresh and retry.
                    if not self.access_token.strip():
                        ok = await self.auth.refresh()
                        if ok:
                            continue
                    raise UpstoxError(
                        "Upstox unauthorized (401). Re-authenticate via /broker-login (or update UPSTOX_ACCESS_TOKEN)."
                    )
                r.raise_for_status()
                return r.json()
            except (httpx.HTTPError, UpstoxError) as exc:
                last_exc = exc
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2**attempt)
                    continue
                break
        raise UpstoxError(f"Upstox request failed: {last_exc}")

    async def get_profile(self) -> Dict[str, Any]:
        return await self._request("GET", "/user/profile")

    async def get_funds_and_margin(self) -> Dict[str, Any]:
        # Upstox docs: /user/get-funds-and-margin
        return await self._request("GET", "/user/get-funds-and-margin")

    async def get_positions(self) -> Dict[str, Any]:
        """Fetch the current positions from Upstox."""
        return await self._request("GET", "/portfolio/short-term-positions")

    async def place_order(
        self,
        symbol: str,
        side: str,
        quantity: int,
        client_order_id: Optional[str] = None,
        order_type: str = "MARKET",
        price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        product: str = "D",
        validity: str = "DAY",
        exchange: str = "NSE",
        segment: str = "EQ",
    ) -> Dict[str, Any]:
        """
        Places an order using instrument_token resolved from the symbol master cache.
        """
        if not self.symbol_master:
            raise UpstoxError("symbol_master not available")
        instrument_key = self.symbol_master.get_instrument_key(symbol, exchange=exchange, segment=segment)
        if not instrument_key:
            raise UpstoxError(f"Unknown symbol in symbol master: {symbol} ({exchange}/{segment}). Refresh master file.")

        transaction_type = "BUY" if side.lower() == "buy" else "SELL"
        payload: Dict[str, Any] = {
            "quantity": int(quantity),
            "product": product,  # D=Delivery, I=Intraday, etc (Upstox)
            "validity": validity,
            "price": price if price is not None else 0,
            "tag": (client_order_id or os.getenv("UPSTOX_ORDER_TAG", "trading-dashboard")),
            "instrument_token": instrument_key,
            "order_type": order_type,
            "transaction_type": transaction_type,
            "disclosed_quantity": 0,
            "trigger_price": stop_loss if stop_loss is not None else 0,
        }
        # take_profit is not a standard Upstox field; it's tracked by our risk/strategy layers.
        return await self._request("POST", "/order/place", json=payload)

    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        return await self._request("GET", f"/order/details?order_id={order_id}")


def broker_from_env(symbol_master: Optional[SymbolMasterService] = None) -> Optional[UpstoxBroker]:
    token = os.getenv("UPSTOX_ACCESS_TOKEN", "").strip()
    if token:
        return UpstoxBroker(access_token=token, symbol_master=symbol_master)
    # OAuth mode: only create broker if required OAuth env vars exist.
    if os.getenv("UPSTOX_API_KEY", "").strip() and os.getenv("UPSTOX_API_SECRET", "").strip():
        return UpstoxBroker(access_token="", symbol_master=symbol_master)
    return None
