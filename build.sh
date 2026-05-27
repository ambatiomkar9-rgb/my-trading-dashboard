#!/bin/bash
set -e

if [ "${SKIP_FRONTEND_BUILD}" = "true" ]; then
  echo "SKIP_FRONTEND_BUILD=true; skipping frontend build."
else
  echo "Building frontend..."
  cd frontend
  if [ -f package-lock.json ]; then
    npm ci
  else
    npm install
  fi
  npm run build
  cd ..
fi

echo "Installing Python dependencies..."
python -m pip install -r requirements.txt

echo "Build complete!"
