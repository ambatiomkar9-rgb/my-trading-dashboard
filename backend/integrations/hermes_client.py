"""Hermes Agent CLI bridge.

This lets our Python agents use Hermes as a reasoning + self-learning copilot.

Production target for Windows laptops:
- Hermes runs on an Ubuntu box (your laptop/VM/server) with SSH enabled.
- Windows agents call Hermes over SSH (non-interactive, key-based auth).

We still support:
- Native `hermes` on the same machine.
- WSL `wsl hermes` as a fallback.
"""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from typing import List, Optional, Tuple


def _env_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class HermesClient:
    """
    Minimal Hermes CLI wrapper.

    Env:
    - HERMES_CMD: override executable, e.g. "hermes" or "wsl hermes"
    - HERMES_TIMEOUT_SEC: subprocess timeout (default 120)
    - HERMES_ACCEPT_HOOKS: if "true", sets HERMES_ACCEPT_HOOKS=1 for Hermes
    """

    timeout_sec: int = int(os.getenv("HERMES_TIMEOUT_SEC", "120"))
    cmd: Optional[str] = os.getenv("HERMES_CMD")
    ssh_host: str = os.getenv("HERMES_SSH_HOST", "").strip()
    ssh_user: str = os.getenv("HERMES_SSH_USER", "").strip()
    ssh_port: int = int(os.getenv("HERMES_SSH_PORT", "22"))
    ssh_identity_file: str = os.getenv("HERMES_SSH_IDENTITY_FILE", "").strip()
    ssh_connect_timeout_sec: int = int(os.getenv("HERMES_SSH_CONNECT_TIMEOUT_SEC", "6"))

    def _resolve_base_cmd(self) -> List[str]:
        # 1) Explicit override (highest priority)
        if self.cmd:
            # Allow "ssh ... hermes" or "wsl hermes" etc.
            return shlex.split(self.cmd, posix=(os.name != "nt"))

        # 2) SSH bridge (production on Windows)
        if self.ssh_host:
            return self._build_ssh_cmd()

        # Prefer native hermes if available.
        if shutil.which("hermes"):
            return ["hermes"]

        # Windows: assume Hermes is installed in WSL.
        if os.name == "nt" and shutil.which("wsl"):
            distro = os.getenv("HERMES_WSL_DISTRO", "").strip()
            if distro:
                return ["wsl", "-d", distro, "hermes"]
            return ["wsl", "hermes"]

        # Fallback: still try.
        return ["hermes"]

    def _build_ssh_cmd(self) -> List[str]:
        # Use BatchMode to prevent password prompts (production safety).
        # Use -T to avoid allocating a TTY, which can hang in some setups.
        dest = self.ssh_host
        if self.ssh_user:
            dest = f"{self.ssh_user}@{self.ssh_host}"
        cmd: List[str] = [
            "ssh",
            "-T",
            "-o",
            "BatchMode=yes",
            "-o",
            f"ConnectTimeout={self.ssh_connect_timeout_sec}",
            "-p",
            str(self.ssh_port),
        ]
        if self.ssh_identity_file:
            cmd += ["-i", self.ssh_identity_file]
        cmd += [dest, "hermes"]
        return cmd

    def _query_ollama_direct(self, prompt: str) -> str:
        """Call Ollama's OpenAI-compatible API directly (fast fallback)."""
        import json
        import urllib.request

        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1/chat/completions")
        model = os.getenv("HERMES_MODEL", "hermes3:3b")
        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4096,
            "temperature": 0.3,
        }).encode("utf-8")
        req = urllib.request.Request(
            ollama_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_sec) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
        except Exception as exc:
            return f"OLLAMA_ERROR: {exc}"

    def query(self, prompt: str) -> str:
        """
        Run one-shot Hermes prompt and return stdout.

        Uses: `hermes chat -q "<prompt>"` (non-interactive).
        Falls back to Ollama direct API if CLI is unavailable or times out.
        """
        # If HERMES_CMD is not set and no hermes binary found, go direct
        base = self._resolve_base_cmd()
        args = base + ["chat", "-q", prompt]
        env = os.environ.copy()
        env.setdefault("NO_COLOR", "1")
        if _env_bool("HERMES_ACCEPT_HOOKS", False):
            env["HERMES_ACCEPT_HOOKS"] = "1"
        try:
            proc = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=self.timeout_sec,
                env=env,
            )
        except subprocess.TimeoutExpired:
            return self._query_ollama_direct(prompt)
        except FileNotFoundError:
            return self._query_ollama_direct(prompt)

        out = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()
        if proc.returncode != 0 and not out:
            # Hermes CLI failed — try direct Ollama
            return self._query_ollama_direct(prompt)
        return out or err

    def healthcheck(self) -> Tuple[bool, str]:
        """Fast connectivity check. Never raises."""
        # Try Hermes CLI first
        try:
            base = self._resolve_base_cmd()
            env = os.environ.copy()
            env.setdefault("NO_COLOR", "1")
            proc = subprocess.run(
                base + ["--version"],
                capture_output=True,
                text=True,
                timeout=min(15, self.timeout_sec),
                env=env,
            )
            out = (proc.stdout or "").strip()
            err = (proc.stderr or "").strip()
            if proc.returncode == 0:
                return True, (out or err)
        except Exception:
            pass
        # Fallback: check Ollama API
        try:
            import urllib.request
            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1/models")
            req = urllib.request.Request(ollama_url)
            with urllib.request.urlopen(req, timeout=5) as resp:
                return True, f"ollama_api_ok (status={resp.status})"
        except Exception as exc:
            return False, f"hermes_cli and ollama_api both failed: {exc}"
