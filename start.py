"""Single command to start the full trading system.

Usage:
    python start.py

Starts Ollama (if installed) + FastAPI app with all agents:
  - MarketDataEngine (WebSocket price feed)
  - TechnicalAnalysisAgent (signal generation)
  - NewsSentimentAgent (news analysis)
  - TradeExecutionAgent (order execution)
  - MacroIntelligenceAgent (macro analysis)
  - WhaleIntelligenceAgent (institutional flows)
  - TelegramCallbackPoller (Telegram button handling)
  - StrategyEngine (rule evaluation)
  - ServiceSupervisor (health monitoring)
"""
from __future__ import annotations

import asyncio
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = REPO_ROOT / "backend"
LOG_DIR = REPO_ROOT / "logs"
MAIN_PY = BACKEND_DIR / "main.py"


def _find_ollama() -> str | None:
    """Find ollama executable."""
    candidates = [
        Path(r"C:\Program Files\Ollama\ollama.exe"),
        Path.home() / "AppData" / "Local" / "Programs" / "Ollama" / "ollama.exe",
        Path(r"/usr/local/bin/ollama"),
        Path(r"/usr/bin/ollama"),
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return shutil.which("ollama")


async def _is_ollama_running() -> bool:
    """Check if Ollama server is reachable."""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=2) as client:
            r = await client.get("http://localhost:11434/api/tags")
            return r.status_code == 200
    except Exception:
        return False


async def _start_ollama() -> bool:
    """Start Ollama serve if not already running."""
    if await _is_ollama_running():
        print("[OK] Ollama already running")
        return True

    ollama_bin = _find_ollama()
    if not ollama_bin:
        print("[SKIP] Ollama not found — chat agent will use fallback mode")
        return False

    LOG_DIR.mkdir(exist_ok=True)
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    try:
        proc = subprocess.Popen(
            [ollama_bin, "serve"],
            stdout=open(LOG_DIR / "ollama.log", "a"),
            stderr=subprocess.STDOUT,
            creationflags=flags,
        )
        for _ in range(10):
            await asyncio.sleep(1)
            if await _is_ollama_running():
                print(f"[OK] Ollama started (pid={proc.pid})")
                return True
        print("[WARN] Ollama started but not responding yet")
        return True
    except Exception as exc:
        print(f"[WARN] Failed to start Ollama: {exc}")
        return False


def _start_dashboard() -> subprocess.Popen:
    """Start the FastAPI dashboard (all agents start via lifespan)."""
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    proc = subprocess.Popen(
        [sys.executable, str(MAIN_PY)],
        cwd=str(REPO_ROOT),
        creationflags=flags,
    )
    print(f"[OK] Dashboard started (pid={proc.pid})")
    return proc


async def main():
    """Start Ollama + Dashboard with all agents."""
    print("=" * 50)
    print("  Trading System — Starting all agents")
    print("=" * 50)
    print()
    print("Agents:")
    print("  1. MarketDataEngine      — WebSocket price feed")
    print("  2. TechnicalAnalysisAgent — signal generation")
    print("  3. NewsSentimentAgent     — news analysis")
    print("  4. TradeExecutionAgent    — order execution")
    print("  5. MacroIntelligenceAgent — macro analysis")
    print("  6. WhaleIntelligenceAgent — institutional flows")
    print("  7. TelegramCallbackPoller — Telegram buttons")
    print("  8. StrategyEngine         — rule evaluation")
    print("  9. ServiceSupervisor      — health monitoring")
    print()

    # Phase 1: Start Ollama
    await _start_ollama()
    print()

    # Phase 2: Start Dashboard (triggers all agents via lifespan)
    print("Starting dashboard (all agents start automatically)...")
    proc = _start_dashboard()

    print()
    print("=" * 50)
    print("  System is starting up")
    print("  Dashboard: http://localhost:8000")
    print("  Press Ctrl+C to stop")
    print("=" * 50)

    try:
        proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("Stopped.")


if __name__ == "__main__":
    asyncio.run(main())
