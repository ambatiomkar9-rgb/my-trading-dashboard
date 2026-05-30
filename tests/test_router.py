"""Unit tests for broker routing skill."""

from __future__ import annotations

from trading_system.config.models import OrderRequest, OrderSide, TradingMode
from trading_system.skills.ccxt_broker_router import CCXTBrokerRouterSkill


def test_ccxt_router_modes() -> None:
    router = CCXTBrokerRouterSkill(default_live_broker="binance")
    paper_req = OrderRequest(
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        quantity=1,
        mode=TradingMode.PAPER,
        stop_loss=95000,
        metadata={"mark_price": 100000},
    )
    live_req = OrderRequest(
        symbol="BTCUSDT",
        side=OrderSide.BUY,
        quantity=1,
        mode=TradingMode.LIVE,
        broker="binance",
        stop_loss=95000,
        metadata={"mark_price": 100000},
    )
    assert router.route(paper_req)["route"] == "paper"
    assert router.route(live_req)["route"] == "binance"
    assert router.normalize_symbol("btcusdt", "binance") == "BTC/USDT"
