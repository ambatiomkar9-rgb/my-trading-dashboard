#!/bin/bash
set -e

# Install main trading_system dependencies
echo "Installing main trading_system Python dependencies..."
pip install -r requirements.txt

# Build frontend if not skipped (assuming frontend is in trading-dashboard/frontend)
if [ "${SKIP_FRONTEND_BUILD}" = "true" ]; then
  echo "SKIP_FRONTEND_BUILD=true; skipping frontend build."
else
  echo "Building frontend..."
  cd trading-dashboard/frontend
  if [ -f package-lock.json ]; then
    npm ci
  else
    npm install
  fi
  npm run build
  cd ../.. # Go back to root
fi

echo "Build complete!"
