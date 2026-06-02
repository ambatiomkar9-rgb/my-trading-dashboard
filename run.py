"""Simple launcher for the Telegram System Controller.

Usage:
    python run.py

Starts the controller which manages the full trading system via Telegram.
"""
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent / "backend"
CONTROLLER = BACKEND_DIR / "controller.py"

if __name__ == "__main__":
    print("Starting Telegram System Controller...")
    print("Press Ctrl+C to stop.")
    print()
    subprocess.run([sys.executable, str(CONTROLLER)])
