"""Local server for the study app.

Serves app/ as static files and keeps progress in ~/ai_career/logs/progress.json.
Run: python3 app/server.py [--port 8765] [--open] [--progress FILE]  (tests pass their own FILE)
"""

import argparse
import json
import os
import tempfile
import threading
import webbrowser
from datetime import UTC, datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

APP = Path(__file__).resolve().parent
PROGRESS = APP.parent / "logs" / "progress.json"
BACKUPS = APP.parent / "logs" / "progress_backups"
MAX_BODY = 5 * 1024 * 1024
LOCK = threading.Lock()


def read_progress():
    if PROGRESS.exists():
        return json.loads(PROGRESS.read_text())
    return {"version": 1, "steps": {}, "code": {}, "events": []}


def write_progress(data):
    PROGRESS.parent.mkdir(parents=True, exist_ok=True)
    # Atomic replace: a crash mid-write never leaves a broken file.
    fd, tmp = tempfile.mkstemp(dir=PROGRESS.parent, prefix=".progress-", suffix=".json")
    with os.fdopen(fd, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, PROGRESS)
    # One backup per day, so a bad save can be undone.
    BACKUPS.mkdir(exist_ok=True)
    daily = BACKUPS / f"progress-{datetime.now():%Y-%m-%d}.json"
    daily.write_text(PROGRESS.read_text())


class Handler(SimpleHTTPRequestHandler):
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".mjs": "text/javascript",
        ".js": "text/javascript",
        ".wasm": "application/wasm",
        ".json": "application/json",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(APP), **kwargs)

    def end_headers(self):
        # Data files change while the app is open; never serve them stale.
        if self.path.startswith(("/data/", "/api/", "/js/", "/css/", "/py/", "/index.html")) or self.path == "/":
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        if "/api/" in self.path:
            super().log_message(fmt, *args)

    def _json(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/progress":
            with LOCK:
                return self._json(200, read_progress())
        if self.path.startswith("/api/"):
            return self._json(404, {"error": "unknown endpoint"})
        return super().do_GET()

    def do_POST(self):
        if self.path != "/api/progress":
            return self._json(404, {"error": "unknown endpoint"})
        length = int(self.headers.get("Content-Length", 0))
        if length > MAX_BODY:
            return self._json(413, {"error": "too large"})
        try:
            data = json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            return self._json(400, {"error": "bad json"})
        if not isinstance(data, dict) or "steps" not in data:
            return self._json(400, {"error": "bad shape"})
        # Keep the client's stamp: the gist copy carries the same one, so "newest wins" compares like with like.
        data.setdefault("saved_at", datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z"))
        with LOCK:
            write_progress(data)
        return self._json(200, {"ok": True, "saved_at": data["saved_at"]})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--open", action="store_true")
    ap.add_argument("--progress", type=Path, help="progress file (default: ~/ai_career/logs/progress.json)")
    opts = ap.parse_args()
    global PROGRESS, BACKUPS
    if opts.progress:
        PROGRESS = opts.progress.resolve()
        BACKUPS = PROGRESS.parent / "progress_backups"
    server = ThreadingHTTPServer(("127.0.0.1", opts.port), Handler)
    url = f"http://127.0.0.1:{opts.port}/"
    print(f"Дорожка: {url}  (прогресс: {PROGRESS})")
    if opts.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
