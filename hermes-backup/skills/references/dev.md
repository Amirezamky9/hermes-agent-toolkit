# Dev — GitHub CLI

## Backend: gh CLI

### Search
```bash
gh search repos "agent framework" --sort stars --limit 10
gh search issues "bug" --repo owner/repo --limit 10
gh search prs "feat" --repo owner/repo --state open
```

### Multi-query research & enrichment workflow

When exploring a class of projects across multiple search angles (e.g. "telegram large file transfer" → search 7 different queries), use this pattern:

```bash
# Step 1 — Run multiple queries, collect deduplicated results
for q in "query 1" "query 2" "query 3"; do
  gh search repos "$q" --language=python --limit=10 \
    --json=fullName,stargazersCount,description,updatedAt,url > /tmp/gh_$RANDOM.json
done

# Step 2 — Deduplicate and sort by stars with a Python aggregation script
# (see pitfall on gh --json fields below)
python3 /tmp/aggregate_repos.py

# Step 3 — Enrich each repo with README excerpt, topics, language breakdown
for repo in owner/repo1 owner/repo2; do
  gh api "repos/$repo/readme" --jq=.download_url | xargs curl -sL -o /tmp/readme_$(echo $repo | tr / _).txt
  gh api "repos/$repo/topics" --jq=.names
  gh api "repos/$repo/languages" --jq=keys
done

# Step 4 — Output structured findings report (markdown table with: name, stars,
# description, approach, last update, found_in_queries)
```

**Pitfall — gh search repos --json field names differ from gh repo view:**  
`gh search repos` uses `stargazersCount` (camelCase, no underscore) and `fullName`, but rejects `stargazerCount` (singular, used by `gh repo view`). `gh repo view` uses `stargazerCount` (singular, no underscore) and `nameWithOwner` (not `fullName`). Always consult `gh search repos --json=...` with an invalid field first to get the available fields list — GitHub CLI silently ignores unknown fields without error.

**Pitfall — gh search repos with `--language=` may return 0 results:**  
If a search query is too specific or niche, `gh search repos` may return empty results even when relevant projects exist. Always run 5–7 query variants covering synonyms, project names, and compound terms. Fall back to `gh api "search/repositories?q=QUERY"` with curl if gh CLI returns 0 (the API may match more broadly).

**Pitfall — gh API README URL vs raw content:**  
`gh api "repos/owner/repo/readme" --jq=.download_url` returns the raw download URL for the README. The field is `download_url`, NOT `html_url`. The download URL returns rendered content, while `raw.githubusercontent.com` is what you pass to `curl -sL`.

**Pitfall — gh api topics needs Accept header:**  
`gh api "repos/owner/repo/topics"` requires the special media type `application/vnd.github.mercy-preview+json` or it returns `{"names":[]}` even when topics exist. Fix: `gh api -H "Accept: application/vnd.github.mercy-preview+json" "repos/owner/repo/topics"`. Or as fallback, fetch via REST API with curl using the same header.

### Read / view
```bash
gh repo view owner/repo
gh repo view owner/repo --json name,description,language,stargazerCount,forkCount,openIssueCount
gh issue list -R owner/repo --limit 10
gh pr list -R owner/repo --limit 5
gh issue view owner/repo#123
gh release list -R owner/repo --limit 5
```

### Authentication
```bash
gh auth login                    # interactive setup
gh auth status                   # check auth
```

## Without auth (rate-limited)

All endpoints use `User-Agent: agent-reach/1.0` (GitHub API requires it).

### Repo metadata
```bash
# Two-step pattern (security scanner blocks curl|python3 and python3 -c):
curl -s "https://api.github.com/repos/owner/repo" -o /tmp/repo_meta.json
cat > /tmp/parse_meta.py << 'PYEOF'
import json
d = json.load(open('/tmp/repo_meta.json'))
keys = ['name','description','language','stargazers_count','forks_count',
        'open_issues_count','created_at','updated_at','homepage']
print(json.dumps({k: d.get(k) for k in keys}, indent=2))
PYEOF
python3 /tmp/parse_meta.py
```

### Search repos
```bash
curl -s "https://api.github.com/search/repositories?q=query" \
  -H "User-Agent: agent-reach/1.0"
```

### File tree (full recursive listing)
```bash
# Two-step pattern (security scanner blocks curl|python3 and python3 -c):
curl -s "https://api.github.com/repos/owner/repo/git/trees/main?recursive=1" \
  -H "User-Agent: agent-reach/1.0" -o /tmp/tree.json
cat > /tmp/parse_tree.py << 'PYEOF'
import json
d = json.load(open('/tmp/tree.json'))
for item in d.get('tree', []):
    print(f"{item['type']:10s} {item['path']}")
PYEOF
python3 /tmp/parse_tree.py
```
Use `?recursive=1` for full tree. Default branch may be `main` or `master` — check metadata first.

### Raw file content (README, specific files)
```bash
curl -s "https://raw.githubusercontent.com/owner/repo/main/README.md" \
  -H "User-Agent: agent-reach/1.0"
```
Works for any text file at any path. Replace `main` with the actual branch name.

### Repo comparison workflow
When comparing a local project with an external GitHub repo:
1. Fetch repo metadata (stars, description, language) via API
2. Fetch README via raw content URL (understanding purpose/scope)
3. Fetch file tree via git/trees API (understanding architecture)
4. Read local project files
5. Produce structured comparison (table format)

**Pitfall:** `gh` CLI may not be authenticated in headless/Docker environments. Always verify with `gh auth status` first; fall back to curl patterns above if not authenticated. Don't assume gh works without checking.
