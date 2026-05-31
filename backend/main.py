"""Launcher for the trading dashboard FastAPI app."""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app import app  # noqa: E402


def main() -> None:
    """Run the dashboard backend with Uvicorn."""
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    reload_enabled = os.getenv("UVICORN_RELOAD", "false").strip().lower() in {"1", "true", "yes", "on"}
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=port,
        reload=reload_enabled,
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
    )


if __name__ == "__main__":
    main()

