# GitHub Publishing with Credits

## Pattern

When publishing tools/projects to GitHub, ALWAYS:
1. Search GitHub first for existing solutions before building from scratch
2. Credit all source projects prominently in README
3. Include LICENSE (MIT unless sources require otherwise)
4. Sanitize sensitive data before committing (API keys, sessions, tokens, .env)

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
## Credits and Acknowledgments

This project would not be possible without these amazing open-source projects.

| Project | Author | Repository | Used For |
|---------|--------|------------|----------|
| **ProjectName** | author | [github.com/author/repo](link) | Description |

### Special Thanks
- **ProjectName** — For what they contributed
```

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

Based on:
- SourceProject (author/repo) - what it provides
- AnotherProject (author/repo) - what it provides

Credits to all open-source projects."
```

## Pitfalls

1. Never commit API keys — Even in "test" commits. Git history is permanent.
2. Never commit .session files — They contain auth tokens.
3. Always credit sources — Even if you heavily modified the code.
4. Check license compatibility — MIT + MIT = OK. MIT + GPL = check requirements.
5. Use .env.example — Show users what vars they need without exposing real values.
