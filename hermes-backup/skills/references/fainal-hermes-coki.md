# fainal_hermes_coki — Client-side Cookie Sync Package

## What this is

This is the user-installed client package for syncing browser cookies from the user's machine to the Hermes backend.
It is the **CacheCat-based front-end piece** of the cookie-sync flow.

## What it does

- Runs on the user's system / browser
- Collects cookies and related storage data from the browser
- Sends them to the Hermes backend over HTTP
- Lets Hermes-backed tools reuse the authenticated state

## What must be included

- Chrome extension / browser-side code
- Backend sync helper if part of the package
- Example config files
- Installation and usage docs
- Credits to CacheCat as the upstream base

## What must NOT be included

- Real API keys
- Real tokens
- Phone numbers
- Session files
- Cookie dumps from the user's account
- Any hardcoded secrets

## Safety checklist before publishing

1. Scan every file for secrets and account data
2. Replace hardcoded credentials with placeholders
3. Remove `.session`, `.env`, raw cookie exports, and backup files
4. Verify `README` only contains placeholders and setup steps
5. Rebuild the repo history if any leak was committed

## Recommended repo layout

```text
fainal_hermes_coki/
├── extension/              # browser extension / frontend pieces
├── backend/                # optional backend example
├── docs/                   # install + sync docs
├── .gitignore
├── LICENSE
└── README.md
```

## Documented integration points

- CacheCat extension is the upstream source of the cookie-collection pattern
- Hermes backend receives cookies and converts them to storage-state format
- Agent-Reach references the cookie-sync flow and should point to this package for client-side setup

## Publish note

If this package is published to GitHub, the repo description should say:

> Browser-side cookie sync client for Hermes, based on CacheCat.

And the README must include a clear "based on CacheCat" credit line.
