"""Multi-broker execution routing with retries and balance checks."""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol

import aiohttp

from trading_system.config.broker_config import BrokerAdapterConfig
from trading_system.config.models import ExecutionResult, OrderRequest, TradingMode

logger = logging.getLogger(__name__)


class BrokerAdapter(Protocol):
    """Protocol for broker implementations."""

    async def get_balance(self) -> Dict[str, Any]:
        """Return account balance payload."""

    async def place_order(self, order: OrderRequest) -> ExecutionResult:
        """Place order and return normalized result."""

    async def fetch_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Fetch order status."""


@dataclass(slots=True)
class RetryPolicy:
    """Retry policy for broker calls."""

    retries: int = 3
    initial_backoff_sec: float = 0.5


class BinanceCcxtAdapter:
    """CCXT adapter for Binance."""

    def __init__(self, config: BrokerAdapterConfig) -> None:
        self.config = config
        self._exchange: Any = None

    async def _ensure_exchange(self) -> Any:
        if self._exchange is not None:
            return self._exchange
        try:
            import ccxt.async_support as ccxt_async  # type: ignore
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError("ccxt is required for Binance live execution") from exc
        exchange_cls = getattr(ccxt_async, self.config.ccxt_exchange_id or "binance")
        self._exchange = exchange_cls(
            {
                "apiKey": self.config.credentials.api_key,
                "secret": self.config.credentials.api_secret,
                "enableRateLimit": True,
            }
        )
        if self.config.credentials.sandbox:
            await self._exchange.set_sandbox_mode(True)
        return self._exchange

    async def get_balance(self) -> Dict[str, Any]:
        ex = await self._ensure_exchange()
        return await ex.fetch_balance()

    async def place_order(self, order: OrderRequest) -> ExecutionResult:
        ex = await self._ensure_exchange()
        if order.order_type.value == "limit":
            response = await ex.create_limit_order(
                symbol=order.symbol,
                side=order.side.value,
                amount=order.quantity,
                price=order.limit_price,
            )
        else:
            response = await ex.create_market_order(
                symbol=order.symbol,
                side=order.side.value,
                amount=order.quantity,
            )
        return ExecutionResult(
            accepted=True,
            mode=order.mode,
            broker="binance",
            order_id=str(response.get("id")),
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            average_price=float(response.get("average") or response.get("price") or 0.0),
            status=str(response.get("status") or "submitted"),
            message="Live order submitted via Binance",
            metadata={"raw": response},
        )

    async def fetch_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        ex = await self._ensure_exchange()
        return await ex.fetch_order(order_id, symbol)


class AlpacaAdapter:
    """REST adapter for Alpaca."""

    BASE_URL = "https://paper-api.alpaca.markets"
    LIVE_URL = "https://api.alpaca.markets"

    def __init__(self, config: BrokerAdapterConfig) -> None:
        self.config = config

    @property
    def _url(self) -> str:
        return self.BASE_URL if self.config.credentials.sandbox else self.LIVE_URL

    def _headers(self) -> Dict[str, str]:
        return {
            "APCA-API-KEY-ID": self.config.credentials.api_key or "",
            "APCA-API-SECRET-KEY": self.config.credentials.api_secret or "",
            "Content-Type": "application/json",
        }

    async def get_balance(self) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self._url}/v2/account", headers=self._headers()) as response:
                response.raise_for_status()
                return await response.json()

    async def place_order(self, order: OrderRequest) -> ExecutionResult:
        payload = {
            "symbol": order.symbol.replace("/", ""),
            "qty": str(order.quantity),
            "side": order.side.value,
            "type": order.order_type.value,
            "time_in_force": "day",
        }
        if order.order_type.value == "limit":
            payload["limit_price"] = str(order.limit_price)
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self._url}/v2/orders", headers=self._headers(), json=payload) as response:
                response.raise_for_status()
                data = await response.json()
        return ExecutionResult(
            accepted=True,
            mode=order.mode,
            broker="alpaca",
            order_id=str(data.get("id")),
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            average_price=float(data.get("filled_avg_price") or 0.0),
            status=str(data.get("status") or "submitted"),
            message="Live order submitted via Alpaca",
            metadata={"raw": data},
        )

    async def fetch_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self._url}/v2/orders/{order_id}", headers=self._headers()) as response:
                response.raise_for_status()
                return await response.json()


class UpstoxAdapter:
    """Upstox adapter (stub).

    Upstox requires OAuth and an access token. Until the order + positions
    endpoints are wired, we fail safely with a clear message.
    """

    def __init__(self, config: BrokerAdapterConfig) -> None:
        self.config = config

    async def get_balance(self) -> Dict[str, Any]:
        # Placeholder: return unknown. BrokerRouter balance guard will not block
        # when available cash cannot be inferred.
        return {"available": None, "message": "Upstox balance not implemented"}

    async def place_order(self, order: OrderRequest) -> ExecutionResult:
        token = (self.config.credentials.passphrase or "").strip()
        if not (self.config.credentials.api_key and token):
            return ExecutionResult(
                accepted=False,
                mode=TradingMode.LIVE,
                broker="upstox",
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                status="rejected",
                message="Upstox credentials missing. Set UPSTOX_API_KEY and UPSTOX_ACCESS_TOKEN in .env.",
            )
        return ExecutionResult(
            accepted=False,
            mode=TradingMode.LIVE,
            broker="upstox",
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            status="not_implemented",
            message="Upstox adapter not implemented yet (OAuth + order endpoints required).",
            metadata={"hint": "Use broker=binance or broker=alpaca for live execution until wired."},
        )

    async def fetch_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        return {
            "status": "unknown",
            "message": "Upstox fetch_order not implemented",
            "order_id": order_id,
            "symbol": symbol,
        }


class OandaAdapter:
    """REST adapter for OANDA."""

    PRACTICE_URL = "https://api-fxpractice.oanda.com"
    LIVE_URL = "https://api-fxtrade.oanda.com"

    def __init__(self, config: BrokerAdapterConfig) -> None:
        self.config = config

    @property
    def _url(self) -> str:
        return self.PRACTICE_URL if self.config.credentials.sandbox else self.LIVE_URL

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.config.credentials.api_key or ''}",
            "Content-Type": "application/json",
        }

    async def get_balance(self) -> Dict[str, Any]:
        account_id = self.config.credentials.account_id or ""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self._url}/v3/accounts/{account_id}/summary", headers=self._headers()) as response:
                response.raise_for_status()
                return await response.json()

    async def place_order(self, order: OrderRequest) -> ExecutionResult:
        account_id = self.config.credentials.account_id or ""
        payload = {
            "order": {
                "type": "MARKET" if order.order_type.value == "market" else "LIMIT",
                "instrument": order.symbol.replace("/", "_"),
                "units": str(order.quantity if order.side.value == "buy" else -order.quantity),
                "timeInForce": "FOK",
                "positionFill": "DEFAULT",
            }
        }
        if order.order_type.value == "limit":
            payload["order"]["price"] = str(order.limit_price)
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self._url}/v3/accounts/{account_id}/orders",
                headers=self._headers(),
                json=payload,
            ) as response:
                response.raise_for_status()
                data = await response.json()
        fill = data.get("orderFillTransaction", {})
        return ExecutionResult(
            accepted=True,
            mode=order.mode,
            broker="oanda",
            order_id=str(fill.get("id", data.get("orderCreateTransaction", {}).get("id"))),
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            average_price=float(fill.get("price") or 0.0),
            status="filled" if fill else "submitted",
            message="Live order submitted via OANDA",
            metadata={"raw": data},
        )

    async def fetch_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        account_id = self.config.credentials.account_id or ""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self._url}/v3/accounts/{account_id}/orders/{order_id}",
                headers=self._headers(),
            ) as response:
                response.raise_for_status()
                return await response.json()


class BrokerRouter:
    """Route live orders to target broker adapters with retry and tracking."""

    def __init__(
        self,
        adapters: Dict[str, BrokerAdapter],
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        self.adapters = adapters
        self.retry_policy = retry_policy or RetryPolicy()
        self.order_registry: Dict[str, Dict[str, Any]] = {}

    async def execute_live_order(self, order: OrderRequest) -> ExecutionResult:
        """Execute order on selected live broker."""
        broker = order.broker.lower()
        adapter = self.adapters.get(broker)
        if not adapter:
            return ExecutionResult(
                accepted=False,
                mode=TradingMode.LIVE,
                broker=broker,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                status="rejected",
                message=f"Unsupported broker: {broker}",
            )
        balance_ok, reason = await self._check_balance(adapter, order)
        if not balance_ok:
            return ExecutionResult(
                accepted=False,
                mode=TradingMode.LIVE,
                broker=broker,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                status="rejected",
                message=reason,
            )

        backoff = self.retry_policy.initial_backoff_sec
        last_error: Optional[Exception] = None
        for _ in range(self.retry_policy.retries):
            try:
                result = await adapter.place_order(order)
                order_id = result.order_id or f"LIVE-{uuid.uuid4().hex[:10]}"
                self.order_registry[order_id] = {
                    "broker": broker,
                    "symbol": order.symbol,
                    "submitted_at": order.submitted_at.isoformat(),
                    "status": result.status,
                }
                return result
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                logger.exception("Live order attempt failed broker=%s symbol=%s", broker, order.symbol)
                await asyncio.sleep(backoff)
                backoff *= 2
        return ExecutionResult(
            accepted=False,
            mode=TradingMode.LIVE,
            broker=broker,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            status="error",
            message=f"Live order failed after retries: {last_error}",
        )

    async def order_status(self, broker: str, order_id: str, symbol: str) -> Dict[str, Any]:
        """Get order status from broker."""
        adapter = self.adapters.get(broker.lower())
        if not adapter:
            return {"status": "unknown", "message": "Unsupported broker"}
        return await adapter.fetch_order(order_id=order_id, symbol=symbol)

    async def _check_balance(self, adapter: BrokerAdapter, order: OrderRequest) -> tuple[bool, str]:
        """Balance check guard before order placement."""
        try:
            balance = await adapter.get_balance()
        except Exception as exc:  # noqa: BLE001
            return False, f"Balance check failed: {exc}"
        # Heuristic fields across brokers.
        possible = [
            balance.get("free", {}).get("USDT"),
            balance.get("cash"),
            balance.get("available"),
            balance.get("account", {}).get("cash"),
            balance.get("account", {}).get("NAV"),
        ]
        available = next((float(v) for v in possible if v is not None), None)
        est_notional = float(order.metadata.get("mark_price", 0) or order.limit_price or 0) * order.quantity
        if order.side.value == "buy" and available is not None and est_notional > available:
            return False, f"Insufficient balance. available={available:.2f} required~{est_notional:.2f}"
        return True, "ok"
