"""Create data/auth.json: the site's login.

The GitHub token (scope: gist only) and the gist id are encrypted with a key derived from the
password (PBKDF2-SHA256, 600 000 rounds, AES-256-GCM). Only salt, iv and ciphertext go to the repo;
the password and the token never do. js/auth.js decrypts it in the browser.

Run (password is asked, not passed on the command line):
    uv run --no-project --with cryptography python tools/make_auth.py --user fafakaj \
        --token-file ~/.config/claude/ml-site-token --gist <gist id>
"""

import argparse
import base64
import getpass
import json
import os
from pathlib import Path

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ITER = 600_000
OUT = Path(__file__).resolve().parents[1] / "data" / "auth.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", required=True)
    ap.add_argument("--token-file", type=Path, required=True)
    ap.add_argument("--gist", required=True)
    ap.add_argument("--password-env", help="read the password from this environment variable instead of a prompt")
    opts = ap.parse_args()

    token = opts.token_file.expanduser().read_text().strip()
    password = os.environ[opts.password_env] if opts.password_env else getpass.getpass("Пароль для сайта: ")
    salt, iv = os.urandom(16), os.urandom(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(password.encode())
    payload = json.dumps({"token": token, "gist": opts.gist}).encode()
    ct = AESGCM(key).encrypt(iv, payload, None)
    b64 = lambda b: base64.b64encode(b).decode()  # noqa: E731
    OUT.write_text(json.dumps({"user": opts.user, "iter": ITER, "salt": b64(salt), "iv": b64(iv), "ct": b64(ct)}, indent=1) + "\n")
    print(f"Записано: {OUT}")


if __name__ == "__main__":
    main()
