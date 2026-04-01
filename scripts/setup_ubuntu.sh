#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Installing backend Python dependencies"
cd "$ROOT_DIR/backend"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

echo "==> Installing frontend Node dependencies"
cd "$ROOT_DIR/frontend"
npm install

echo
echo "Setup complete."
echo "Run backend with: bash scripts/run_backend.sh"
echo "Run frontend with: bash scripts/run_frontend.sh"
