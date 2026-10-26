#!/usr/bin/env bash
# Start a throwaway server (its own progress file) and run the Playwright checks.
set -euo pipefail
APP="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'kill $SERVER 2>/dev/null; rm -rf "$TMP"' EXIT
mkdir -p "$TMP/shots"

python3 "$APP/server.py" --port 8799 --progress "$TMP/progress.json" >"$TMP/server.log" 2>&1 &
SERVER=$!

# Reference solutions the tests submit.
python3 - "$APP" >"$TMP/refs.json" <<'EOF'
import json, sys
app = sys.argv[1]
sys.path.insert(0, f"{app}/tools")
from content.w03 import EXERCISES
from content.m1_site import EXERCISES as SITE
cards = json.load(open(f"{app}/data/anki.json"))["cards"]
print(json.dumps({"lc217": open(f"{app}/data/refs/217.py").read(), "softmax": EXERCISES["ex-w3-softmax"]["ref"],
                  "eda": SITE["ex-w3-eda"]["ref"], "tests": SITE["ex-w1-tests"]["ref"],
                  "ankiDay1": sum(c["day"] <= "2026-10-26" for c in cards),
                  "ankiWeek3Wed": sum(c["day"] <= "2026-11-11" for c in cards)}))
EOF

PW="$(dirname "$(find ~/.npm/_npx -maxdepth 3 -type d -path '*node_modules/playwright' | head -1)")"
for _ in $(seq 20); do curl -fs http://127.0.0.1:8799/ >/dev/null 2>&1 && break; sleep 0.2; done

# Guest account passwords live outside git, in ~/.config/claude; the owner's comes from TEST_PASS.
TEST_PASS_GUEST="${TEST_PASS_GUEST:-$(cat ~/.config/claude/ml-site-smetanka-pass 2>/dev/null || true)}"
TEST_PASS_KESHA="${TEST_PASS_KESHA:-$(cat ~/.config/claude/ml-site-keshapticya-pass 2>/dev/null || true)}"
export TEST_PASS_GUEST TEST_PASS_KESHA

SHOTS="${SHOTS:-$APP/tests/shots}"
mkdir -p "$SHOTS"
NODE_PATH="$PW" BASE=http://127.0.0.1:8799 PROGRESS_FILE="$TMP/progress.json" REFS_FILE="$TMP/refs.json" SHOTS="$SHOTS" \
  node "$APP/tests/e2e.cjs"
