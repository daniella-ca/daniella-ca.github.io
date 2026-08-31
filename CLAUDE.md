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
