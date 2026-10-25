#!/usr/bin/env bash
# Screenshots of all screens with a seeded progress file (a few done steps, review cards due).
set -euo pipefail
APP="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$(realpath -m "${1:-$APP/tests/shots/ui}")"
TMP="$(mktemp -d)"
trap 'kill $SERVER 2>/dev/null; rm -rf "$TMP"' EXIT

cat >"$TMP/progress.json" <<'EOF'
{"version": 1, "saved_at": "2026-10-27T09:00:00.000Z",
 "steps": {"w01-mon-01": {"status": "done", "done_at": "2026-10-26T10:00:00Z"},
           "w01-mon-02": {"status": "done", "done_at": "2026-10-26T11:00:00Z", "attempts": 2},
           "w01-mon-03": {"status": "done", "done_at": "2026-10-26T12:00:00Z"},
           "w01-mon-04": {"status": "done", "done_at": "2026-10-26T12:30:00Z"}},
 "code": {}, "quiz": {}, "checklist": {}, "notes": {}, "review": {}, "events": []}
EOF
python3 "$APP/server.py" --port 8798 --progress "$TMP/progress.json" >"$TMP/server.log" 2>&1 &
SERVER=$!
PW="$(dirname "$(find ~/.npm/_npx -maxdepth 3 -type d -path '*node_modules/playwright' | head -1)")"
for _ in $(seq 20); do curl -fs http://127.0.0.1:8798/ >/dev/null 2>&1 && break; sleep 0.2; done
NODE_PATH="$PW" BASE=http://127.0.0.1:8798 OUT="$OUT" node "$APP/tests/shots.cjs"
