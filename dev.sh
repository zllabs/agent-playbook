#!/usr/bin/env bash
# Start API + web for local development. Ctrl+C stops both.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
API_PORT="${API_PORT:-8000}"
WEB_PORT="${WEB_PORT:-5173}"
pids=()

cleanup() {
  trap - EXIT INT TERM
  local pid
  for pid in "${pids[@]:-}"; do
    pkill -TERM -P "$pid" 2>/dev/null || true
    kill -TERM "$pid" 2>/dev/null || true
  done
  sleep 0.3
  for pid in "${pids[@]:-}"; do
    pkill -KILL -P "$pid" 2>/dev/null || true
    kill -KILL "$pid" 2>/dev/null || true
  done
  wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "==> API deps"
cd "$ROOT/apps/api"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r requirements.txt

echo "==> Web deps"
cd "$ROOT/apps/web"
if [[ ! -d node_modules ]]; then
  npm ci
fi

echo "==> Starting API :$API_PORT and web :$WEB_PORT"
cd "$ROOT/apps/api"
uvicorn main:app --reload --port "$API_PORT" &
pids+=($!)

cd "$ROOT/apps/web"
npm run dev -- --host 127.0.0.1 --port "$WEB_PORT" &
pids+=($!)

echo "Open http://127.0.0.1:$WEB_PORT  (Ctrl+C to stop)"
wait
