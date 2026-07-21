# GitHub Publishing with Credits

## Pattern

When publishing tools/projects to GitHub, ALWAYS:
1. Search GitHub first for existing solutions before building from scratch
2. Credit ALL source projects prominently in README (categorized by type)
3. Include LICENSE (MIT unless sources require otherwise)
4. Sanitize sensitive data before committing (API keys, sessions, tokens, .env)
5. Write comprehensive documentation (installation, usage, troubleshooting)
6. Include skills/references if the project is for Hermes

## Pre-publish Checklist

```bash
# 1. Search for existing solutions
gh search repos "topic keywords" --sort stars --limit 10

# 2. Check for sensitive data
grep -r "api_id\|api_hash\|TOKEN\|password\|secret" . --include="*.py" --include="*.yaml" --include="*.json" | grep -v ".example" | grep -v "os.environ"

# 3. Verify .gitignore
cat .gitignore  # Must include: *.session, .env, cookies/, *.json (except config)

# 4. Check for hardcoded values
grep -rn "YOUR_API_ID\|YOUR_API_HASH" .  # Example API ID/hash
```

## README Credits Section Template

```markdown
## 📚 Credits & Acknowledgments

This project would not be possible without these amazing open-source projects and their developers.

### Core Dependencies

| Project | Author | Repository | Used For |
|---------|--------|------------|----------|
| **ProjectName** | author | [github.com/author/repo](link) | Description |

### Research Tools

| Project | Author | Repository | Used For |
|---------|--------|------------|----------|
| **ToolName** | author | [link](url) | Description |

### Special Thanks

- **ProjectName** — What they contributed and why it matters
```

## Credits Categories

When the project uses many sources, categorize them:

1. **Core Dependencies** — Main libraries/frameworks the project builds on
2. **Research Tools** — CLI tools, APIs, search engines
3. **Platform-Specific Tools** — Per-platform CLIs (twitter-cli, rdt-cli, etc.)
4. **Special Thanks** — Brief thank-you notes for major contributions

## Sanitization Rules

| Data Type | Replace With |
|-----------|-------------|
| API keys | YOUR_API_KEY_HERE |
| Tokens | your_token_here |
| Session files | Remove from repo, add to .gitignore |
| .env files | Create .env.example with placeholder values |
| Hardcoded IDs | Remove or use env vars |
| User-specific paths | Use ~/ or $HOME |

## .gitignore Template for Python Projects

```gitignore
# Sensitive
*.session
*.session-journal
.env
!*.env.example
cookies/
*.json
!package.json
!tsconfig.json
!config.yaml.example

# Python
__pycache__/
*.pyc
.venv/
venv/

# IDE
.vscode/
.idea/

# OS
.DS_Store
```

## Git Commit Pattern

```bash
git commit -m "feat: description

Added:
- feature1 (from SourceProject)
- feature2 (from AnotherProject)

Updated:
- documentation
- credits

Based on:
- SourceProject (author/repo) - what it provides
- AnotherProject (author/repo) - what it provides

Credits to all open-source projects."
```

## Documentation Structure

For complex projects, include:

```
docs/
├── installation.md    # Step-by-step install guide
├── usage.md           # How to use each feature
├── troubleshooting.md # Common issues and fixes
└── api.md             # API reference (if applicable)
```

## Pitfalls

1. Never commit API keys — Even in "test" commits. Git history is permanent.
2. Never commit .session files — They contain auth tokens.
3. Always credit sources — Even if you heavily modified the code. The user explicitly asked for this.
4. Check license compatibility — MIT + MIT = OK. MIT + GPL = check requirements.
5. Use .env.example — Show users what vars they need without exposing real values.
6. Categorize credits — Don't just list everything in one table. Group by type (core, tools, platforms).
7. Include stars count — For popular projects (e.g., "2672⭐"), it shows the project's maturity.
8. Write installation guide — Users should be able to install on a fresh system without guessing.
9. **Git history sanitization** — `git rm` + new commit does NOT remove sensitive data from history. `git log -p -S "SECRET"` still finds it. The ONLY reliable fix is: (a) `rm -rf .git`, (b) `git init`, (c) single fresh commit, (d) `git push -f`. Do this BEFORE first push if any commit contained real credentials. After push, GitHub caches history — even force-push may not scrub forks/caches. Prevention (never commit secrets) is always better than cleanup.
10. **Agent-Reach is the mother project** — When crediting Agent-Reach, describe it as "platform router for 16 platforms with multi-backend routing" (Twitter, Reddit, YouTube, GitHub, Bilibili, XiaoHongShu, LinkedIn, Facebook, Instagram, V2EX, Xueqiu, RSS, Telegram, Web, Exa Search, Grok). Do NOT reduce it to "internet access" — the user corrected this.
11. **Git author/email hygiene for public repos** — GitHub maps commit email to accounts. Using a work email (e.g., `hermes@nousresearch.com`) causes GitHub to show the email owner's account as contributor. For anonymous/public repos, use `noreply@<project>.local` as the committer email. After push, if the wrong account appears, the ONLY fix is: delete repo → recreate → force push with clean history. Force-push alone doesn't fix cached contributor mappings.
12. **Complete git history rebuild pattern** — When sensitive data leaked into git history: (1) backup all files, (2) `rm -rf .git`, (3) `git init && git branch -M main`, (4) restore files, (5) verify no sensitive data with `grep -rn "SECRET" .`, (6) single fresh commit, (7) `git push -f origin main`. This is the ONLY way to truly scrub history. `git filter-branch` and BFG are alternatives but more complex.
