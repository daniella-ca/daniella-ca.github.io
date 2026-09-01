# daniella-ca.github.io

Public GitHub Pages site, served at https://daniella-ca.github.io

## Structure

- `reports/` — published reports
- `dashboards/` — published dashboards
- `public-encrypted/` — password-protected pages (see CLAUDE.md)

## This repository is PUBLIC

Everything committed here is world-readable and search-indexable, including
anything later deleted — git history keeps it, and Pages serves it.

Before committing a report or dashboard, confirm it contains no client
identifiers, account IDs, spend or revenue figures, or anything a client has
not agreed to publish. Client-confidential work belongs in the private
`daniella-workspace` repo instead.

Nothing secret is ever committed here. This repo does keep its own
gitignored `.env` for the encryption secrets — see CLAUDE.md, "What must be
backed up". It is separate from `~/claude-work/.env` and neither is tracked.
