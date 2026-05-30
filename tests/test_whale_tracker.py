"""Unit tests for whale tracker logic."""

from __future__ import annotations

import pytest

from trading_system.skills.whale_tracker_skill import WhaleTrackerSkill


def _mock_trades():
    return [
        {"px": "65000", "sz": "10", "side": "B", "hash": "tx1"},
        {"px": "64950", "sz": "8", "side": "B", "hash": "tx2"},
        {"px": "65120", "sz": "3", "side": "S", "hash": "tx3"},
    ]


@pytest.mark.asyncio
async def test_whale_detection_without_network() -> None:
    tracker = WhaleTrackerSkill(large_tx_threshold_usd=200000, accumulation_threshold_usd=300000)

    async def fake_recent_trades(coin: str):
        return _mock_trades()

    tracker.fetch_recent_trades = fake_recent_trades  # type: ignore[method-assign]
    report = await tracker.analyze_whale_activity("BTC")
    assert report["coin"] == "BTC"
    assert report["sentiment"] in {"bullish_whales", "bearish_whales", "neutral_whales"}
    assert isinstance(report["alerts"], list)
    assert report["accumulation"]["detected"] is True
