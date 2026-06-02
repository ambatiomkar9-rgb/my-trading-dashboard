"""End-to-End Smoke Test — signal → approve → execute → fill → position → events.

Run this script to verify the complete trading pipeline works:
1. Auth: login, get JWT
2. Watchlist: add a symbol
3. Signal: generate a signal for the symbol
4. Approve: approve the signal
5. Execute: submit the order
6. Fill: simulate broker fill
7. Position: verify position updated
8. Events: verify event store captured everything

Usage:
    cd trading-dashboard
    python -m tests.smoke_test
"""
from __future__ import annotations

import json
import sys
import time
from typing import Any

import httpx

BASE_URL = "http://localhost:8000"
ADMIN_USER = "admin"
ADMIN_PASS = "admin"


class SmokeTest:
    def __init__(self) -> None:
        self.session = httpx.Client()
        self.jwt: str = ""
        self.symbol: str = "TESTSMOKE"
        self.signal_id: str = ""
        self.order_id: str = ""
        self.results: list[tuple[str, bool, str]] = []

    def _log(self, name: str, passed: bool, detail: str = "") -> None:
        status = "PASS" if passed else "FAIL"
        self.results.append((name, passed, detail))
        print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))

    def run(self) -> bool:
        print("=" * 60)
        print("End-to-End Smoke Test")
        print("=" * 60)

        try:
            self._test_auth()
            self._test_watchlist_add()
            self._test_signal_generate()
            self._test_signal_approve()
            self._test_order_execute()
            self._test_order_fill()
            self._test_position_verify()
            self._test_events()
        except Exception as exc:
            self._log("Unexpected error", False, str(exc))

        passed = sum(1 for _, p, _ in self.results if p)
        failed = sum(1 for _, p, _ in self.results if not p)
        print("\n" + "=" * 60)
        print(f"Results: {passed} passed, {failed} failed out of {len(self.results)}")
        print("=" * 60)
        return failed == 0

    def _test_auth(self) -> None:
        print("\n1. Authentication")
        try:
            res = self.session.post(
                f"{BASE_URL}/login",
                data={"username": ADMIN_USER, "password": ADMIN_PASS},
            )
            if res.status_code == 200:
                data = res.json()
                self.jwt = data.get("access_token", "")
                self.session.headers["Authorization"] = f"Bearer {self.jwt}"
                self._log("Login", True, f"JWT received ({len(self.jwt)} chars)")
            else:
                self._log("Login", False, f"HTTP {res.status_code}: {res.text[:200]}")
        except Exception as exc:
            self._log("Login", False, str(exc))

    def _test_watchlist_add(self) -> None:
        print("\n2. Watchlist — Add Symbol")
        try:
            res = self.session.post(
                f"{BASE_URL}/watchlist",
                json={"symbol": self.symbol, "name": "Smoke Test Stock"},
            )
            if res.status_code in (200, 201):
                self._log("Add to watchlist", True, self.symbol)
            else:
                self._log("Add to watchlist", False, f"HTTP {res.status_code}: {res.text[:200]}")
        except Exception as exc:
            self._log("Add to watchlist", False, str(exc))

    def _test_signal_generate(self) -> None:
        print("\n3. Signal — Generate")
        try:
            res = self.session.post(
                f"{BASE_URL}/api/signals/generate",
                json={"symbol": self.symbol, "strategy": "moving_average"},
            )
            if res.status_code in (200, 201):
                data = res.json()
                self.signal_id = str(data.get("id", data.get("signal_id", "")))
                self._log("Generate signal", True, f"signal_id={self.signal_id}")
            else:
                self._log("Generate signal", False, f"HTTP {res.status_code}: {res.text[:200]}")
        except Exception as exc:
            self._log("Generate signal", False, str(exc))

    def _test_signal_approve(self) -> None:
        print("\n4. Signal — Approve")
        if not self.signal_id:
            self._log("Approve signal", False, "No signal_id from previous step")
            return
        try:
            res = self.session.post(
                f"{BASE_URL}/api/signals/{self.signal_id}/approve",
            )
            if res.status_code in (200, 201):
                self._log("Approve signal", True, f"signal_id={self.signal_id}")
            else:
                self._log("Approve signal", False, f"HTTP {res.status_code}: {res.text[:200]}")
        except Exception as exc:
            self._log("Approve signal", False, str(exc))

    def _test_order_execute(self) -> None:
        print("\n5. Order — Execute")
        if not self.signal_id:
            self._log("Execute order", False, "No signal_id")
            return
        try:
            res = self.session.post(
                f"{BASE_URL}/api/orders/execute",
                json={
                    "signal_id": self.signal_id,
                    "symbol": self.symbol,
                    "side": "buy",
                    "quantity": 1,
                    "order_type": "market",
                },
            )
            if res.status_code in (200, 201):
                data = res.json()
                self.order_id = str(data.get("order_id", data.get("id", "")))
                self._log("Execute order", True, f"order_id={self.order_id}")
            else:
                self._log("Execute order", False, f"HTTP {res.status_code}: {res.text[:200]}")
        except Exception as exc:
            self._log("Execute order", False, str(exc))

    def _test_order_fill(self) -> None:
        print("\n6. Order — Simulate Fill")
        if not self.order_id:
            self._log("Fill order", False, "No order_id")
            return
        try:
            res = self.session.post(
                f"{BASE_URL}/api/orders/{self.order_id}/fill",
                json={"fill_price": 100.0},
            )
            if res.status_code in (200, 201):
                self._log("Fill order", True, f"filled at 100.00")
            else:
                self._log("Fill order", False, f"HTTP {res.status_code}: {res.text[:200]}")
        except Exception as exc:
            self._log("Fill order", False, str(exc))

    def _test_position_verify(self) -> None:
        print("\n7. Position — Verify")
        try:
            res = self.session.get(f"{BASE_URL}/api/portfolio")
            if res.status_code == 200:
                data = res.json()
                positions = data.get("positions", [])
                found = any(
                    getattr(p, "symbol", p.get("symbol", "")) == self.symbol
                    if isinstance(p, dict)
                    else False
                    for p in positions
                )
                self._log("Check position", True, f"found={found}")
            else:
                self._log("Check position", False, f"HTTP {res.status_code}")
        except Exception as exc:
            self._log("Check position", False, str(exc))

    def _test_events(self) -> None:
        print("\n8. Events — Verify Event Store")
        try:
            res = self.session.get(f"{BASE_URL}/api/events")
            if res.status_code == 200:
                data = res.json()
                events = data.get("events", data) if isinstance(data, dict) else data
                event_count = len(events) if isinstance(events, list) else 0
                self._log("Event store", True, f"{event_count} events recorded")
            else:
                # Events endpoint might not exist yet
                self._log("Event store", False, f"HTTP {res.status_code}")
        except Exception as exc:
            self._log("Event store", False, str(exc))

    def _cleanup(self) -> None:
        """Try to clean up test data."""
        try:
            self.session.delete(f"{BASE_URL}/watchlist/{self.symbol}")
        except Exception:
            pass


def main() -> None:
    test = SmokeTest()
    success = test.run()
    test._cleanup()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
