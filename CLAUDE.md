# daniella-ca.github.io

Public GitHub Pages site. Everything committed here is world-readable and
search-indexable at https://daniella-ca.github.io

## Hard rule: never commit client-identifying HTML outside `public-encrypted/`

Anything containing client names, spend figures, revenue, or account IDs goes
through encryption. **No exceptions.**

There is no "just this once" and no "it's only a draft". A file committed to
this repo is public the moment it is pushed, and deleting it later does not
help — git history retains it and Pages has already served it.

If you are unsure whether something is client-identifying, it is. Encrypt it,
or put it in the private `daniella-workspace` repo instead.

## How encryption works here

    public-encrypted/_src/report.html   plaintext   GITIGNORED, never committed
    public-encrypted/report.html        encrypted   committed and served

Write the plaintext page into `public-encrypted/_src/`. On `git commit`, the
pre-commit hook encrypts it with StatiCrypt and stages the encrypted copy. You
never commit the plaintext — the hook blocks it outright if you try.

Viewers open the published page and are prompted for the master password.

## Passwords: one per client, never the master

**When publishing a report for a client who has no password in `.env` yet,
STOP and prompt to run `bin/new-client-password` first. Never fall back to the
master password for a client-facing page.**

The master password is for internal pages only. Using it for a client page
would hand that client the key to every other client's report, and to anything
internal published here. The pre-commit hook enforces this: a page with no
entry in `.page-keys` blocks the commit rather than guessing.

    bin/new-client-password acme-corp report-2026-q3.html

That maps the page to the client in `.page-keys`. It generates and stores
nothing: the passphrase is **derived** from `ENCRYPT_SECRET` and the client
slug, so the same slug always yields the same five words. Read it back only
when you are ready to send it:

    bin/client-password acme-corp

Send the link and the password through **different channels**.

Use one password per client, not per report. A client with five reports should
not need five passphrases: map each of their pages to the same slug.

### Why passphrases must be generated, never invented

StatiCrypt derives its key with PBKDF2 at roughly 15,000 iterations
(`node_modules/staticrypt/lib/cryptoEngine.js:142,155`) — far below current
guidance. The ciphertext is public, so an attacker can guess offline forever
with no rate limit. Password entropy is doing nearly all the security work:
five random words is about 65 bits, while a hand-picked `Acme2026!` is about 30
and would not survive a targeted attempt.

The words come from `bin/wordlist.txt`: the EFF long wordlist, 7,772 entries,
committed here so derivation cannot drift. It replaced `/usr/share/dict/words`,
which is unabridged and produced phrases like `conceity-unstrain-premium` that
cannot be read down a phone line. The trade is 81 bits to 65, still far beyond
what an offline attempt will reach.

**The wordlist is frozen.** Changing it changes every client's passphrase.

### `.page-keys`

Maps each page to its client slug. Gitignored, because the slugs are client
names, and publishing it would leak exactly what the encryption protects.

Losing it no longer loses any password, only the record of which page belongs
to which client. Every passphrase regenerates from `ENCRYPT_SECRET` plus the
slug. The hook still blocks any page that has no mapping.

### Rotation does not undo exposure

Re-encrypting with a new password protects only future versions. The old
ciphertext remains in git history and in any cache, and stays crackable with
the leaked password. Treat a leaked password as permanent exposure for anything
already published.

### The master secret

`.env` at the root of this repo holds three values, gitignored, mode 600:

    STATICRYPT_PASSWORD   master password, internal pages only
    STATICRYPT_SALT       fixed salt, keeps encrypted output stable
    ENCRYPT_SECRET        the key every client passphrase is derived from

These are **separate** from `~/claude-work/.env`, which is untouched by any of
this.

If `.env` is lost, every encrypted page becomes permanently unrecoverable and
no client passphrase can be regenerated. There is no reset. Keep a copy in a
password manager. It is now the only thing that must be backed up, because the
file no longer grows a new secret per client.

### What encryption does NOT protect

- **Filenames.** `acme-corp-q3-spend.html` leaks the client name to anyone
  browsing the repo, even though its contents are encrypted. Name files
  neutrally: `report-2026-q3.html`.
- **Git history.** Anything ever committed in plaintext stays in history
  forever, even after deletion.
- **Commit messages.** Do not name clients or quote figures in them.

## Working on this repo

Node lives at `~/.local/bin` (installed outside Homebrew). After a fresh clone,
two steps are required before the hook will run:

    npm install
    git config core.hooksPath .githooks

`core.hooksPath` is local repo config and is not carried by `git clone`, so a
fresh clone has NO active hook until you set it. The `.env` must also be
restored from your password manager.
