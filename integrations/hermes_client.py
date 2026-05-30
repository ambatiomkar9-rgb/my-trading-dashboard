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

    def query(self, prompt: str) -> str:
        """
        Run one-shot Hermes prompt and return stdout.

        Uses: `hermes chat -q "<prompt>"` (non-interactive).
        """
        base = self._resolve_base_cmd()
        args = base + ["chat", "-q", prompt]
        env = os.environ.copy()
        env.setdefault("NO_COLOR", "1")
        # Keep Hermes from waiting on interactive confirmations for shell hooks.
        if _env_bool("HERMES_ACCEPT_HOOKS", False):
            # Some Hermes versions use this env var; also helps with tools.
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
            return "HERMES_TIMEOUT"

        out = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()
        if proc.returncode != 0 and not out:
            return f"HERMES_ERROR: {err[:4000]}"
        return out or err

    def healthcheck(self) -> Tuple[bool, str]:
        """Fast connectivity check. Never raises."""
        base = self._resolve_base_cmd()
        env = os.environ.copy()
        env.setdefault("NO_COLOR", "1")
        try:
            proc = subprocess.run(
                base + ["--version"],
                capture_output=True,
                text=True,
                timeout=min(15, self.timeout_sec),
                env=env,
            )
        except Exception as exc:  # noqa: BLE001
            return False, f"hermes check failed: {exc}"
        out = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()
        if proc.returncode != 0:
            return False, (err or out or f"exit={proc.returncode}")
        return True, (out or err)
