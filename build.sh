#!/bin/bash
set -e

# Install backend Python dependencies
echo "Installing backend Python dependencies..."
pip install -r trading-dashboard/backend/requirements.txt

# Build frontend if not skipped
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
  cd ../..  # Go back to root
fi

echo "Build complete!"
