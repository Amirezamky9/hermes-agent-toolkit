# Hermes Toolkit Repo — Install & Publish Notes

This reference is the canonical source for the combined package layout.

## Include in the repo

- `cookie-sync/` for backend sync server
- `telegram-toolkit/` for Telegram automation
- `research/` for platform research scripts
- `skills/` for reusable Hermes skills
- `docs/installation.md` for install steps on a fresh Hermes instance

## Exclude from the repo

- Real API keys, session files, cookie exports, tokens
- Build artifacts and `node_modules/`
- Any machine-specific `.env` files

## Client-side cookie sync package

If the user provides the `@fainal_hermes_coki` source tree, publish it as a separate top-level package or a sibling folder. Keep the readme explicit that it is:
- CacheCat-based
- Installed on the user's machine/browser
- Responsible only for syncing browser state to the Hermes backend

## Documentation checklist

The combined repository should explain:
1. What runs on the user's machine
2. What runs on the Hermes server
3. How cookies are transmitted
4. How to configure the backend URL / API key
5. How to verify that sync works
6. What files are intentionally excluded
7. Which upstream projects are being credited

## Safe publish pattern

Before any push:
1. Search the tree for secrets
2. Search `git log` for leaked data
3. Remove leaks and rewrite history if necessary
4. Re-scan after rewrite

## Merge guidance

If a new client-side package is added later, link it from this reference and from `docs/installation.md` so a fresh Hermes install sees the client and server pieces in the same place.