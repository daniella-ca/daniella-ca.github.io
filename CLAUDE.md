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

That generates a five-word passphrase, appends `CLIENT_ACME_CORP_PW` to `.env`
without printing it, and maps the page to it in `.page-keys`. To send it:

    grep '^CLIENT_ACME_CORP_PW=' .env | cut -d= -f2-

Send the link and the password through **different channels**.

Use one password per client, not per report — a client with five reports
should not need five passphrases. Map each of their pages to the same variable.

### Why passphrases must be generated, never invented

StatiCrypt derives its key with PBKDF2 at roughly 15,000 iterations
(`node_modules/staticrypt/lib/cryptoEngine.js:142,155`) — far below current
guidance. The ciphertext is public, so an attacker can guess offline forever
with no rate limit. Password entropy is doing nearly all the security work:
five random words is about 81 bits, while a hand-picked `Acme2026!` is about 30
and would not survive a targeted attempt.

### `.page-keys`

Maps each page to its password variable. Gitignored, because the variable names
contain client names — publishing it would leak exactly what the encryption
protects. **Back it up alongside `.env`**; without it the hook blocks every
page.

### Rotation does not undo exposure

Re-encrypting with a new password protects only future versions. The old
ciphertext remains in git history and in any cache, and stays crackable with
the leaked password. Treat a leaked password as permanent exposure for anything
already published.

### The master secret

Lives in `.env` at the root of this repo — gitignored, mode 600. This is a
**separate** secret from `~/claude-work/.env`, which is untouched by any of this.

If `.env` is lost, every encrypted page becomes permanently unrecoverable.
There is no reset. Keep a copy in a password manager.

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
