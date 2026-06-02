"""Telegram System Controller — starts/stops the full trading system from Telegram.

Usage:
    python backend/controller.py

This lightweight script:
1. Runs a Telegram bot that listens for commands and button presses
2. On "Start System": launches Ollama + FastAPI app as subprocesses
3. On "Stop System": kills the subprocesses
4. On "Status": reports what's running
5. Forwards signal approve/reject callbacks to the FastAPI app via HTTP

The Telegram bot in this controller is THE only bot. The main app's
TelegramCallbackPoller is disabled via TELEGRAM_DISABLED=true env var.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Optional

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("controller")

# ─── Paths ──────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
MAIN_PY = BACKEND_DIR / "main.py"
STATE_FILE = BACKEND_DIR / "controller_state.json"

OLLAMA_PATHS = [
    Path(r"C:\Users\ambat\AppData\Local\Programs\Ollama\ollama.exe"),
    Path(r"C:\Program Files\Ollama\ollama.exe"),
    Path.home() / "AppData" / "Local" / "Programs" / "Ollama" / "ollama.exe",
]

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "http://127.0.0.1:8000")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "hermes3:3b")


# ─── State Persistence ──────────────────────────────────────────────────────

class SystemState:
    """Persisted state for process management across restarts."""

    def __init__(self) -> None:
        self.ollama_pid: Optional[int] = None
        self.ollama_running: bool = False
        self.main_pid: Optional[int] = None
        self.main_running: bool = False
        self.started_at: Optional[str] = None
        self.load()

    def load(self) -> None:
        try:
            if STATE_FILE.exists():
                data = json.loads(STATE_FILE.read_text())
                self.ollama_pid = data.get("ollama_pid")
                self.ollama_running = data.get("ollama_running", False)
                self.main_pid = data.get("main_pid")
                self.main_running = data.get("main_running", False)
                self.started_at = data.get("started_at")
        except Exception:
            pass

    def save(self) -> None:
        try:
            STATE_FILE.write_text(json.dumps({
                "ollama_pid": self.ollama_pid,
                "ollama_running": self.ollama_running,
                "main_pid": self.main_pid,
                "main_running": self.main_running,
                "started_at": self.started_at,
            }, indent=2))
        except Exception:
            pass

    def clear(self) -> None:
        self.ollama_pid = None
        self.ollama_running = False
        self.main_pid = None
        self.main_running = False
        self.started_at = None
        self.save()


# ─── Ollama Management ──────────────────────────────────────────────────────

def _find_ollama_executable() -> Optional[str]:
    for p in OLLAMA_PATHS:
        if p.is_file():
            return str(p)
    import shutil
    return shutil.which("ollama")


async def is_ollama_running() -> bool:
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.get(f"{OLLAMA_HOST}/api/version")
            return resp.status_code == 200
    except Exception:
        return False


async def start_ollama() -> tuple[bool, Optional[int], str]:
    if await is_ollama_running():
        return True, None, "Ollama already running"

    ollama_bin = _find_ollama_executable()
    if not ollama_bin:
        return False, None, "Ollama not found. Install from https://ollama.com"

    try:
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        proc = subprocess.Popen(
            [ollama_bin, "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=flags,
        )
        logger.info("Ollama started with PID %d", proc.pid)

        for _ in range(30):
            await asyncio.sleep(1)
            if await is_ollama_running():
                return True, proc.pid, f"Ollama started (PID {proc.pid})"

        return False, proc.pid, "Ollama started but health check timed out"
    except Exception as exc:
        return False, None, f"Failed to start Ollama: {exc}"


async def stop_ollama(pid: Optional[int] = None) -> str:
    if not await is_ollama_running():
        return "Ollama not running"

    if pid:
        try:
            import psutil
            proc = psutil.Process(pid)
            proc.terminate()
            proc.wait(timeout=10)
            return f"Ollama stopped (PID {pid})"
        except (ImportError, Exception):
            if sys.platform == "win32":
                subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
                return f"Ollama killed (PID {pid})"

    if sys.platform == "win32":
        try:
            result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, timeout=5)
            for line in result.stdout.splitlines():
                if "11434" in line and "LISTENING" in line:
                    kill_pid = line.split()[-1]
                    subprocess.run(["taskkill", "/F", "/PID", kill_pid], capture_output=True)
                    return f"Ollama killed (PID {kill_pid})"
        except Exception:
            pass

    return "Could not determine Ollama PID"


async def list_models() -> str:
    ollama_bin = _find_ollama_executable()
    if not ollama_bin:
        return "Ollama not found"
    try:
        result = subprocess.run([ollama_bin, "list"], capture_output=True, text=True, timeout=10)
        return result.stdout.strip() or "No models installed"
    except Exception as exc:
        return f"Error: {exc}"


async def pull_model(model_name: str) -> str:
    ollama_bin = _find_ollama_executable()
    if not ollama_bin:
        return "Ollama not found"
    try:
        result = subprocess.run(
            [ollama_bin, "pull", model_name],
            capture_output=True, text=True, timeout=600,
        )
        return result.stdout.strip() or f"Pull completed for {model_name}"
    except subprocess.TimeoutExpired:
        return f"Pull timed out for {model_name}"
    except Exception as exc:
        return f"Error: {exc}"


# ─── Dashboard Management ───────────────────────────────────────────────────

async def is_dashboard_running() -> bool:
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.get(f"{DASHBOARD_HOST}/health")
            return resp.status_code == 200
    except Exception:
        return False


async def start_dashboard() -> tuple[bool, Optional[int], str]:
    if await is_dashboard_running():
        return True, None, "Dashboard already running"

    if not MAIN_PY.exists():
        return False, None, f"main.py not found at {MAIN_PY}"

    try:
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        env = os.environ.copy()
        env["TELEGRAM_DISABLED"] = "true"
        env["DASHBOARD_URL"] = DASHBOARD_HOST

        proc = subprocess.Popen(
            [sys.executable, str(MAIN_PY)],
            cwd=str(REPO_ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=flags,
            env=env,
        )
        logger.info("Dashboard started with PID %d", proc.pid)

        for _ in range(60):
            await asyncio.sleep(1)
            if await is_dashboard_running():
                return True, proc.pid, f"Dashboard started (PID {proc.pid})"

        return False, proc.pid, "Dashboard started but health check timed out"
    except Exception as exc:
        return False, None, f"Failed to start dashboard: {exc}"


async def stop_dashboard(pid: Optional[int] = None) -> str:
    if not await is_dashboard_running():
        return "Dashboard not running"

    if pid:
        try:
            import psutil
            proc = psutil.Process(pid)
            proc.terminate()
            try:
                proc.wait(timeout=10)
                return f"Dashboard stopped (PID {pid})"
            except Exception:
                proc.kill()
                proc.wait(timeout=5)
                return f"Dashboard force-killed (PID {pid})"
        except (ImportError, Exception):
            if sys.platform == "win32":
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True)
                return f"Dashboard killed (PID {pid})"

    if sys.platform == "win32":
        try:
            result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, timeout=5)
            for line in result.stdout.splitlines():
                if ":8000" in line and "LISTENING" in line:
                    kill_pid = line.split()[-1]
                    subprocess.run(["taskkill", "/F", "/T", "/PID", kill_pid], capture_output=True)
                    return f"Dashboard killed (PID {kill_pid})"
        except Exception:
            pass

    return "Could not determine dashboard PID"


async def get_system_status() -> dict[str, Any]:
    ollama_ok = await is_ollama_running()
    dashboard_ok = await is_dashboard_running()
    status: dict[str, Any] = {
        "ollama": {"running": ollama_ok},
        "dashboard": {"running": dashboard_ok},
        "agents": {},
    }
    if ollama_ok:
        try:
            async with httpx.AsyncClient(timeout=3) as client:
                resp = await client.get(f"{OLLAMA_HOST}/api/version")
                if resp.status_code == 200:
                    status["ollama"]["version"] = resp.json().get("version", "unknown")
        except Exception:
            pass
        status["ollama"]["models"] = await list_models()

    if dashboard_ok:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{DASHBOARD_HOST}/api/system/health")
                if resp.status_code == 200:
                    health = resp.json()
                    status["agents"] = {
                        "ollama_status": health.get("ollama_status", "unknown"),
                        "hermes_status": health.get("hermes_status", "unknown"),
                        "broker_status": health.get("broker_status", "unknown"),
                        "agents_online": health.get("agents_online", 0),
                        "runtime_mode": health.get("runtime_mode", "unknown"),
                        "trading_enabled": health.get("trading_enabled", False),
                    }
        except Exception:
            pass

    return status


# ─── Telegram Bot ───────────────────────────────────────────────────────────

class TelegramController:
    """Telegram bot that manages the trading system and handles signal callbacks."""

    def __init__(self) -> None:
        self._token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        self._chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
        self._offset = 0
        self._running = False
        self._state = SystemState()
        self._base = f"https://api.telegram.org/bot{self._token}" if self._token else ""

    def _auth_headers(self) -> dict[str, str]:
        api_token = os.getenv("DASHBOARD_API_TOKEN", "").strip()
        if api_token:
            return {"Authorization": f"Bearer {api_token}"}
        admin_key = os.getenv("ADMIN_API_KEY", "").strip()
        return {"X-Admin-Key": admin_key} if admin_key else {}

    async def _send(self, text: str, reply_markup: Optional[dict] = None) -> bool:
        if not self._base or not self._chat_id:
            return False
        try:
            payload: dict[str, Any] = {
                "chat_id": self._chat_id,
                "text": text,
                "parse_mode": "Markdown",
            }
            if reply_markup:
                payload["reply_markup"] = reply_markup
            async with httpx.AsyncClient(timeout=10, trust_env=False) as client:
                resp = await client.post(f"{self._base}/sendMessage", json=payload)
                resp.raise_for_status()
                return bool(resp.json().get("ok", False))
        except Exception as exc:
            logger.error("Telegram send error: %s", exc)
            return False

    async def _answer_cb(self, cb_id: str, text: str) -> None:
        if not self._base:
            return
        try:
            async with httpx.AsyncClient(timeout=5, trust_env=False) as client:
                await client.post(
                    f"{self._base}/answerCallbackQuery",
                    json={"callback_query_id": cb_id, "text": text},
                )
        except Exception:
            pass

    # ── Menu ────────────────────────────────────────────────────────────

    async def send_main_menu(self) -> None:
        text = (
            "🖥️ *Trading System Controller*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Select an action:"
        )
        markup = {
            "inline_keyboard": [
                [
                    {"text": "▶️ Start System", "callback_data": "ctrl_start"},
                    {"text": "⏹️ Stop System", "callback_data": "ctrl_stop"},
                ],
                [
                    {"text": "📊 Status", "callback_data": "ctrl_status"},
                    {"text": "📋 Models", "callback_data": "ctrl_models"},
                ],
                [{"text": "🔄 Refresh Menu", "callback_data": "ctrl_menu"}],
            ]
        }
        await self._send(text, reply_markup=markup)

    # ── System Commands ─────────────────────────────────────────────────

    async def handle_start_system(self, cb_id: str) -> None:
        await self._answer_cb(cb_id, "Starting system...")
        await self._send("⏳ *Starting system...*\n\n1️⃣ Checking Ollama...")

        ok, pid, msg = await start_ollama()
        if pid:
            self._state.ollama_pid = pid
            self._state.ollama_running = True
            self._state.save()

        if not ok:
            await self._send(f"❌ Ollama: {msg}\n\nCannot continue without Ollama.")
            return
        await self._send(f"✅ Ollama: {msg}\n\n2️⃣ Starting dashboard...")

        ok, pid, msg = await start_dashboard()
        if pid:
            self._state.main_pid = pid
            self._state.main_running = True
            self._state.started_at = time.strftime("%Y-%m-%d %H:%M:%S")
            self._state.save()

        if ok:
            status = await get_system_status()
            agents_online = status.get("agents", {}).get("agents_online", 0)
            mode = status.get("agents", {}).get("runtime_mode", "paper")
            await self._send(
                f"✅ *System Started!*\n\n"
                f"🖥️ Dashboard: {DASHBOARD_HOST}\n"
                f"🤖 Agents online: {agents_online}\n"
                f"📊 Trading mode: {mode}\n"
                f"🧠 Ollama: {DEFAULT_MODEL}\n\n"
                f"_Trade signals will appear here with Approve/Reject buttons._"
            )
        else:
            await self._send(f"❌ Dashboard: {msg}")

    async def handle_stop_system(self, cb_id: str) -> None:
        await self._answer_cb(cb_id, "Stopping system...")
        await self._send("⏳ *Stopping system...*")

        results = []
        r = await stop_dashboard(self._state.main_pid)
        results.append(f"Dashboard: {r}")
        r = await stop_ollama(self._state.ollama_pid)
        results.append(f"Ollama: {r}")

        self._state.clear()
        report = "\n".join(f"• {r}" for r in results)
        await self._send(f"✅ *System Stopped*\n\n{report}\n\n_Send /start for menu._")

    async def handle_status(self, cb_id: str) -> None:
        if cb_id:
            await self._answer_cb(cb_id, "Checking status...")
        status = await get_system_status()

        o_icon = "🟢" if status["ollama"]["running"] else "🔴"
        d_icon = "🟢" if status["dashboard"]["running"] else "🔴"

        text = (
            f"📊 *System Status*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{o_icon} *Ollama:* {'Running' if status['ollama']['running'] else 'Stopped'}\n"
        )
        if status["ollama"].get("version"):
            text += f"   Version: {status['ollama']['version']}\n"
        text += f"\n{d_icon} *Dashboard:* {'Running' if status['dashboard']['running'] else 'Stopped'}\n"

        if status["agents"]:
            a = status["agents"]
            text += (
                f"\n🤖 *Agents:* {a.get('agents_online', 0)} online\n"
                f"📊 *Mode:* {a.get('runtime_mode', 'N/A')}\n"
                f"💰 *Trading:* {'Enabled' if a.get('trading_enabled') else 'Disabled'}\n"
                f"🏦 *Broker:* {a.get('broker_status', 'N/A')}\n"
                f"🧠 *Ollama:* {a.get('ollama_status', 'N/A')}\n"
                f"🔮 *Hermes:* {a.get('hermes_status', 'N/A')}\n"
            )
        text += f"\n━━━━━━━━━━━━━━━━━━━━\n_Send /start for menu._"
        await self._send(text)

    async def handle_models(self, cb_id: str) -> None:
        if cb_id:
            await self._answer_cb(cb_id, "Fetching models...")
        models_text = await list_models()
        await self._send(
            f"📋 *Installed Models*\n\n```\n{models_text}\n```\n\n"
            f"_To pull a new model, send:_\n`/pull model_name`"
        )

    async def handle_pull(self, model_name: str) -> None:
        if not model_name:
            await self._send("Usage: `/pull model_name`\nExample: `/pull hermes3:3b`")
            return
        await self._send(f"⏳ *Pulling {model_name}...*\nThis may take several minutes.")
        result = await pull_model(model_name)
        await self._send(f"✅ *Pull Result:*\n\n```\n{result}\n```")

    # ── Signal Callbacks (forwarded to FastAPI) ─────────────────────────

    async def handle_signal_callback(self, data: str, cb_id: str, user: str) -> None:
        if data.startswith("approve_"):
            signal_id = data.split("_", 1)[1]
            await self._answer_cb(cb_id, "✅ Signal approved!")
            ok = await self._forward_action(signal_id, "approved", "Telegram approved")
            msg = f"✅ *{user} approved signal #{signal_id}*\nExecuting..." if ok else \
                  f"⚠️ *{user} approved signal #{signal_id}* but dashboard update failed"
            await self._send(msg)

        elif data.startswith("reject_"):
            signal_id = data.split("_", 1)[1]
            await self._answer_cb(cb_id, "❌ Signal rejected")
            ok = await self._forward_action(signal_id, "rejected", "Telegram rejected")
            msg = f"❌ *{user} rejected signal #{signal_id}*" if ok else \
                  f"⚠️ *{user} rejected signal #{signal_id}* but dashboard update failed"
            await self._send(msg)

    async def _forward_action(self, signal_id: str, status: str, reason: str) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10, trust_env=False) as client:
                resp = await client.patch(
                    f"{DASHBOARD_HOST}/api/signals/{signal_id}",
                    json={"status": status, "reason": reason},
                    headers=self._auth_headers(),
                )
                return resp.status_code == 200
        except Exception as exc:
            logger.error("Forward action failed: %s", exc)
            return False

    # ── Polling Loop ────────────────────────────────────────────────────

    async def _poll(self) -> None:
        if not self._base:
            return
        try:
            async with httpx.AsyncClient(timeout=10, trust_env=False) as client:
                resp = await client.get(
                    f"{self._base}/getUpdates",
                    params={"offset": self._offset, "timeout": 5},
                )
                resp.raise_for_status()
                payload = resp.json()
                if not payload.get("ok"):
                    return
                updates = payload.get("result", [])

            for update in updates:
                self._offset = int(update.get("update_id", self._offset)) + 1

                callback = update.get("callback_query")
                if callback:
                    await self._on_callback(callback)
                    continue

                message = update.get("message")
                if message:
                    await self._on_message(message)
        except Exception as exc:
            logger.warning("Poll error: %s", exc)

    async def _on_callback(self, cb: dict[str, Any]) -> None:
        data = str(cb.get("data") or "")
        cb_id = str(cb.get("id") or "")
        user = cb.get("from", {}).get("first_name", "User")

        handlers = {
            "ctrl_start": lambda: self.handle_start_system(cb_id),
            "ctrl_stop": lambda: self.handle_stop_system(cb_id),
            "ctrl_status": lambda: self.handle_status(cb_id),
            "ctrl_models": lambda: self.handle_models(cb_id),
            "ctrl_menu": lambda: self._refresh_menu(cb_id),
        }
        if data in handlers:
            await handlers[data]()
        elif data.startswith("approve_") or data.startswith("reject_"):
            await self.handle_signal_callback(data, cb_id, user)

    async def _refresh_menu(self, cb_id: str) -> None:
        await self._answer_cb(cb_id, "Menu refreshed")
        await self.send_main_menu()

    async def _on_message(self, msg: dict[str, Any]) -> None:
        text = str(msg.get("text") or "").strip()
        chat_id = str(msg.get("chat", {}).get("id") or "")

        if self._chat_id and chat_id != self._chat_id:
            return

        cmd = text.split()[0].lower() if text else ""
        arg = text.split(" ", 1)[1].strip() if " " in text else ""

        commands = {
            "/start": lambda: self.send_main_menu(),
            "/menu": lambda: self.send_main_menu(),
            "/status": lambda: self.handle_status(""),
            "/models": lambda: self.handle_models(""),
            "/stop": lambda: self.handle_stop_system(""),
            "/start_system": lambda: self.handle_start_system(""),
            "/help": self._send_help,
        }
        if cmd in commands:
            await commands[cmd]()
        elif cmd == "/pull":
            await self.handle_pull(arg)

    async def _send_help(self) -> None:
        await self._send(
            "📖 *Commands*\n\n"
            "/start — Show control menu\n"
            "/status — System status\n"
            "/models — List Ollama models\n"
            "/pull <model> — Pull a model\n"
            "/stop — Stop the system\n"
            "/help — This message"
        )

    async def run(self) -> None:
        if not self._token:
            logger.error("TELEGRAM_BOT_TOKEN not set. Cannot start controller.")
            return
        if not self._chat_id:
            logger.error("TELEGRAM_CHAT_ID not set. Cannot start controller.")
            return

        self._running = True
        logger.info("Telegram controller started (chat_id=%s)", self._chat_id)
        await self._send("🤖 *Controller online*\n\n_Send /start for menu._")

        if self._state.main_running and not await is_dashboard_running():
            self._state.clear()

        while self._running:
            await self._poll()
            await asyncio.sleep(2)

    async def stop(self) -> None:
        self._running = False


# ─── Entry Point ────────────────────────────────────────────────────────────

async def _main() -> None:
    controller = TelegramController()

    if sys.platform != "win32":
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.ensure_future(controller.stop()))

    try:
        await controller.run()
    except KeyboardInterrupt:
        pass
    finally:
        await controller.stop()
        logger.info("Controller stopped")


if __name__ == "__main__":
    asyncio.run(_main())
