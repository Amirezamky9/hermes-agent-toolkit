# Hermes Backup Workflow

## What to Backup

| Path | Content | Sanitize? |
|------|---------|-----------|
| `~/.hermes/config.yaml` | Main config | Yes — redact token/key/secret/password |
| `~/.hermes/SOUL.md` | Personality | No |
| `~/.hermes/skills/` | All skills | No |
| `~/.hermes/memories/MEMORY.md` | Persistent notes | Yes — redact long strings |
| `~/.hermes/scripts/` | Scripts (.py, .sh) | No (but .env files excluded) |
| `~/.hermes/cron/jobs.json` | Cron definitions | No |
| `~/.mcporter/mcporter.json` | Exa/MCP config | Yes — redact API keys |
| `~/.config/gh/hosts.yml` | GitHub auth | Skip entirely (has token) |
| WebUI patches | Modified routes.py, server.py | No |

## What to NEVER Backup

- `~/.hermes/.env` (raw secrets)
- `~/.hermes/webui/.signing_key` (security)
- `~/.hermes/webui/.pbkdf2_key` (security)
- `~/.agent-reach/cookies/` (auth cookies)
- `~/.agent-reach/credentials*` (service credentials)
- Any `.env` file with actual values
- `git.env` or similar token files

## Secrets Management Rules

1. **Never store tokens in workspace** — workspace can be wiped. Use `~/.hermes/`, `~/.mcporter/`, `~/.config/`.
2. **Never display tokens** — use `cat file | grep token | command` pipeline.
3. **Config files with real keys go to dotfile dirs** (`~/.mcporter/`, not `/workspace/config/`).
4. **Template .env files** with placeholder values are fine for backup.

## Restore Order

1. `config.yaml` → `~/.hermes/config.yaml`
2. `hermes-skills/*` → `~/.hermes/skills/`
3. `MEMORY.md` → `~/.hermes/memories/MEMORY.md`
4. `scripts/*` → `~/.hermes/scripts/`
5. `jobs.json` → `~/.hermes/cron/jobs.json`
6. `mcporter.json` → `~/.mcporter/mcporter.json`
7. Re-enter all secrets manually (tokens, API keys, passwords)
