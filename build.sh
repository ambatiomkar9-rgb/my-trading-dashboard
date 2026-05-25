#!/bin/bash
set -e

echo "Building frontend (optional)..."
if command -v npm >/dev/null 2>&1; then
  cd frontend
  npm install
  npm run build
  cd ..
else
  echo "npm not found; skipping frontend build (using committed frontend/dist)."
fi

echo "Installing Python dependencies..."
python -m pip install -r requirements.txt

echo "Build complete!"

