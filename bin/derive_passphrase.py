#!/usr/bin/env python3
"""Derive a client's passphrase from the master secret. Deterministic.

    ENCRYPT_SECRET=... bin/derive_passphrase.py <client-slug>

Prints five hyphenated words. The same secret and slug always produce the same
phrase, so nothing needs storing - the passphrase is regenerated on demand
rather than kept in .env.

The secret is read from the environment, never argv: argv is visible to any
local user via `ps`.

Words come from bin/wordlist.txt, committed to this repo so the result cannot
drift. Deriving from /usr/share/dict/words would silently change every client's
password on a machine with a different dictionary - and that dictionary yields
words like "mecodont" that nobody can read down a phone line.

Changing bin/wordlist.txt changes every derived passphrase. Pages already
published keep working only until they are re-encrypted, at which point clients
need the new phrase. Treat the wordlist as frozen.
"""
import hashlib
import hmac
import os
import sys
from pathlib import Path

NWORDS = 5
WORDLIST = Path(__file__).parent / "wordlist.txt"


def _index(secret: bytes, slug: str, position: int, pool: int) -> int:
    """Uniform index into the pool. Rejection-sampled, so no modulo bias."""
    limit = (2**32 // pool) * pool
    counter = 0
    while True:
        msg = f"{slug}:{position}:{counter}".encode("utf-8")
        digest = hmac.new(secret, msg, hashlib.sha256).digest()
        value = int.from_bytes(digest[:4], "big")
        if value < limit:
            return value % pool
        counter += 1


def derive(secret: str, slug: str, words: list) -> str:
    key = secret.encode("utf-8")
    return "-".join(words[_index(key, slug, i, len(words))] for i in range(NWORDS))


def main(argv) -> int:
    if len(argv) != 2:
        print("usage: ENCRYPT_SECRET=... derive_passphrase.py <client-slug>", file=sys.stderr)
        return 2
    slug = argv[1]

    secret = os.environ.get("ENCRYPT_SECRET", "")
    if not secret:
        print("ERROR: ENCRYPT_SECRET is not set in the environment.", file=sys.stderr)
        print("  It lives in .env at the repo root. Without it no passphrase", file=sys.stderr)
        print("  can be regenerated and every encrypted page is unrecoverable.", file=sys.stderr)
        return 1
    if not WORDLIST.exists():
        print(f"ERROR: wordlist missing at {WORDLIST}", file=sys.stderr)
        print("  Without it passphrases cannot be reproduced. Restore it from git.", file=sys.stderr)
        return 1

    words = [w.strip() for w in WORDLIST.read_text().splitlines()
             if w.strip() and not w.startswith("#")]
    if len(words) < 1000:
        print(f"ERROR: wordlist has only {len(words)} entries - refusing to derive.", file=sys.stderr)
        return 1

    print(derive(secret, slug, words))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
