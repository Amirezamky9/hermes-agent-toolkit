# GitHub Implementation Research Pattern

Reusable methodology for finding and evaluating open-source implementations of any project/concept on GitHub.

## Search Strategy: Multiple Angles

Run 3-4 `gh search repos` queries in parallel, each targeting a different angle:

```bash
# Angle 1: By exact/concept name
gh search repos "coup game" --sort stars --limit 15

# Angle 2: By networking approach
gh search repos "coup multiplayer websocket" --sort stars --limit 10

# Angle 3: By related tech stack
gh search repos "boardgame.io" --sort stars --limit 10

# Angle 4: Broader category (card game engines, etc.)
gh search repos "card game engine javascript" --sort stars --limit 10
```

**Pitfall:** GitHub search uses fuzzy matching. "coup" also returns coupon/couple repos. Filter by name+description relevance manually or via post-processing.

## Repo Triage: Metadata Inspection

For each promising repo, pull metadata in parallel:

```bash
gh repo view OWNER/REPO --json description,url,primaryLanguage,languages,repositoryTopics,stargazerCount
```

**Filter criteria:**
- Has relevant languages (not just one-offs)
- Has description matching the intent
- Stars indicate community interest
- Recent activity (check defaultBranchRef or last push)

## Deep Dive: File Tree Analysis

Map the codebase structure without cloning:

```bash
gh api repos/OWNER/REPO/git/trees/main?recursive=1 --jq '.tree[] | select(.type=="blob") | .path'
```

**What to look for:**
- `server/` + `client/` split → client-server architecture
- `socket.io` / `websocket` / `firebase` in file paths → networking approach
- `Dockerfile` / `docker-compose` → deployment strategy
- `__tests__/` / `*.test.*` → test coverage
- `components/` / `pages/` → UI framework (React, Next.js, etc.)
- `lib/game/` or `engine.ts` → game logic separation

## Source Reading: Direct Raw GitHub (Preferred) + Jina Reader (Fallback)

### Direct curl to raw.githubusercontent.com (fastest, no chrome)
```bash
# README — cleanest output, no Jina wrapping
curl -s "https://raw.githubusercontent.com/OWNER/REPO/main/README.md" | head -80

# package.json — dependency/tech stack discovery
curl -s "https://raw.githubusercontent.com/OWNER/REPO/main/package.json" | head -40
# Or extract just dependencies:
curl -s "https://raw.githubusercontent.com/OWNER/REPO/main/package.json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d.get('dependencies',{}), indent=2))"
```

**Why raw over Jina:** No markdown wrapping, no GitHub chrome, faster, works for any text file. Use `head -N` to trim large files.

### Jina Reader (for HTML pages, live deployments)
```bash
# Full repo page with README rendering
curl -s "https://r.jina.ai/https://github.com/OWNER/REPO" | head -100

# Live deployment check (if homepageUrl exists)
curl -s "https://r.jina.ai/https://coup-game-delta.vercel.app" | head -30
```

**Pitfall:** Jina Reader returns markdown with GitHub chrome (nav menus, sidebars). `head -N` to trim.

## Dependency Discovery: package.json Inspection

After identifying promising repos, inspect their dependency files to map tech stacks:

```bash
# Full package.json (top-level)
curl -s "https://raw.githubusercontent.com/OWNER/REPO/main/package.json" | head -60

# Just dependencies object (faster comparison)
curl -s "https://raw.githubusercontent.com/OWNER/REPO/main/package.json" | python3 -c "
import sys,json
d=json.load(sys.stdin)
deps = d.get('dependencies',{})
devdeps = d.get('devDependencies',{})
print('DEPS:', list(deps.keys()))
print('DEV:', list(devdeps.keys()))
"

# Multi-repo parallel comparison
for repo in owner1/repo1 owner2/repo2 owner3/repo3; do
  echo "=== $repo ==="
  curl -s "https://raw.githubusercontent.com/$repo/main/package.json" 2>/dev/null | head -40 &
done
wait
```

**Key signals from package.json:**
- `socket.io` / `socket.io-client` → WebSocket multiplayer
- `firebase` → Firebase Realtime DB / Firestore
- `next` → Next.js framework
- `react` + `react-dom` → React UI
- `tailwindcss` → Tailwind CSS
- `typescript` → TypeScript
- `boardgame.io` → turn-based game engine

## Targeted Directory Exploration

For repos with deep structures, explore specific directories without fetching the full tree:

```bash
# List files in a specific directory
gh api repos/OWNER/REPO/contents/DIRECTORY --jq '.[].name'

# Example: check what's in src/components/
gh api repos/OWNER/REPO/contents/src/components --jq '.[].name'
```

**Why over git/trees:** `contents/` returns only the immediate children of a directory, which is faster and more focused than fetching the full recursive tree. Use `git/trees` for top-level structure, `contents/` for drilling into specific directories.

## Live Deployment Verification

Check if a repo has a live deployment via the homepageUrl field:

```bash
# Pull homepageUrl from repo metadata
gh repo view OWNER/REPO --json homepageUrl

# If a URL exists, verify it's live
curl -s "https://THE_URL" | head -10
```

**Use case:** Confirms the code actually works in production and lets you inspect the deployed UI/tech choices (e.g., Next.js chunk names in HTML reveal the framework).

## Framework/Engine Discovery

Search for the underlying frameworks used:

```bash
# By framework name
gh search repos "boardgame.io" --sort stars --limit 10

# By feature + tech
gh search repos "supabase realtime multiplayer" --sort stars --limit 10
gh search repos "firebase realtime game" --sort stars --limit 10
```

## Parallel Execution Pattern

Batch independent calls. A typical research burst:

```
Turn 1: 4x gh search repos (parallel, different angles)
Turn 2: 6-8x gh repo view --json (parallel, top repos)
Turn 3: 3x raw README curl + 3x gh api contents/DIR (parallel)
Turn 4: 4x package.json curl (parallel, for tech stack comparison)
Turn 5: 2x Jina Reader for live deployments + framework docs (parallel)
Turn 6: Synthesize into structured output
```

**Batching rules:**
- `gh search repos` calls are safe to parallel (different queries, same API)
- `gh repo view --json` calls are safe to parallel (read-only)
- `curl` to raw.githubusercontent.com are safe to parallel
- `gh api repos/.../contents/` are safe to parallel
- Avoid mixing `git/trees` (full) with `contents/` (targeted) on the same repo — pick one

## Output Format

Structure findings by the user's requested dimensions:
- Tables with Tech Stack, Multiplayer approach, Stars, URL
- Key architectural patterns extracted from file trees
- Specific file paths to important source code
- Actionable recommendations with lazy alternatives

## Fallback: GitHub API without `gh` CLI

When `gh` is not installed, use Python `urllib.request` to query GitHub's REST API directly. Write a self-contained script to `/tmp/` (never use `python3 -c` — see web-research security scanner pitfall):

```python
#!/usr/bin/env python3
"""GitHub API search — no deps, no gh CLI needed"""
import urllib.request, json

queries = [
    "gstack hermes agent",
    "gstack browser",
]

for q in queries:
    url = f"https://api.github.com/search/repositories?q={q.replace(' ', '+')}&sort=stars&order=desc&per_page=10"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.v3+json", "User-Agent": "research-agent/1.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        print(f"\n=== {q} === Total: {data.get('total_count', 0)}")
        for item in data.get("items", [])[:10]:
            print(f"REPO: {item['full_name']} ({item['stargazers_count']} stars)")
            print(f"URL: {item['html_url']}")
            print(f"DESC: {(item.get('description') or 'N/A')[:200]}")
            print("---")
    except Exception as e:
        print(f"ERROR for '{q}': {e}")
```

**Tree mapping without `gh`:**
```python
url = "https://api.github.com/repos/OWNER/REPO/git/trees/main?recursive=1"
req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.v3+json", "User-Agent": "research-agent/1.0"})
resp = urllib.request.urlopen(req, timeout=15)
data = json.loads(resp.read())
files = [t["path"] for t in data.get("tree", []) if t["type"] == "blob"]
```

**Why this works:** GitHub's REST API (`api.github.com`) is unauthenticated for read operations (60 req/hour limit). The `Accept: application/vnd.github.v3+json` header is required. `User-Agent` header is mandatory (GitHub rejects requests without it).

## Cross-Repo Ecosystem Search Pattern

When researching whether tool A integrates with tool B (or how a community uses a combination of tools), search BOTH repos for mentions of the other. This finds real usage evidence that single-repo searches miss.

### The pattern

```
# Step 1: Search the "host" repo for mentions of the "tool"
curl -s "https://api.github.com/search/issues?q=TOOL_KEYWORD+repo:OWNER/HOST_REPO&per_page=30" \
  -H "Accept: application/vnd.github.v3+json" -o /tmp/results_1.json

# Step 2: Search the "tool" repo for mentions of the "host"
curl -s "https://api.github.com/search/issues?q=HOST_KEYWORD+repo:OWNER/TOOL_REPO&per_page=30" \
  -H "Accept: application/vnd.github.v3+json" -o /tmp/results_2.json

# Step 3: Parse both, look for:
#   - Issues/PRs implementing integration (highest signal)
#   - Bug reports about the integration (shows real usage)
#   - Feature requests (shows demand)
#   - User comments describing their setup (highest fidelity)
```

### What to extract from results

- **PRs that add host support** → confirms integration exists and how it works
- **Issues about broken integration paths** → shows what real users hit
- **User comments with setup details** → exact commands, config, workarounds
- **Changelog entries** → official confirmation of support

### API gotcha: response format varies by endpoint

| Endpoint | Response format |
|----------|----------------|
| `/search/issues?q=...` | `{"total_count": N, "items": [...]}` — object with `items` |
| `/repos/{owner}/{repo}/issues` | `[...]` — plain list, no wrapping object |
| `/repos/{owner}/{repo}/pulls/{n}/comments` | `[...]` — plain list (PR review comments) |
| `/repos/{owner}/{repo}/issues/{n}/comments` | `[...]` — plain list (issue comments) |

**Pitfall:** Never assume `.get('items', [])` works on all endpoints. The `/repos/.../issues` endpoint returns a bare list. Always check with `isinstance(data, list)`:
```python
items = data if isinstance(data, list) else data.get('items', [])
```

### Parallel search pattern for cross-repo research

For researching "does X work with Y", fan out all searches in one batch:
```
Turn 1 (parallel):
  - curl: search/issues?q=X+repo:Y/repo (X mentioned in Y's repo)
  - curl: search/issues?q=Y+repo:X/repo (Y mentioned in X's repo)
  - curl: search/code?q=X+repo:Y/repo (code references)
  - curl: repos/X/repo/contents/hosts/ or similar (config files)

Turn 2 (parallel): Parse all JSON files, extract Hermes-relevant items

Turn 3 (parallel): Fetch detailed comments on top items
  - curl: repos/X/repo/issues/N/comments for issue bodies
  - curl: repos/X/repo/pulls/N for PR descriptions

Turn 4: Synthesize cross-referenced findings
```

## Common Pitfalls

1. **Exa/mcporter not configured** → fall back to `gh search` + `curl r.jina.ai/URL`. Don't block on missing search backends.
2. **Empty search results** → broaden query. "coup multiplayer websocket" → "board game multiplayer"
3. **No README** → check file tree for clues. Minimal README ≠ bad repo.
4. **Jina Reader rate limits** → space requests, use `head -N` to read less per call. Prefer direct `curl` to raw.githubusercontent.com when possible.
5. **`gh search` script execution blocked** → pipe through `cat` or use `--json` flag instead of inline python.
6. **Defaulting to Socket.IO for multiplayer** → Firebase Realtime DB is a viable serverless alternative. Check if repos use Firebase before assuming WebSocket servers are the only pattern. Key tradeoff: Firebase = no backend to maintain but less control; Socket.IO = full control but requires a running server.
7. **Missing dependency inspection** → always check package.json (or requirements.txt, go.mod, etc.) to understand the actual tech stack. README may be outdated or incomplete.
8. **GitHub code search returns 401** → `api.github.com/search/code` requires authentication (personal access token). Fall back to `search/repositories` (works unauthenticated) + manual file reading via `raw.githubusercontent.com`.
9. **GitHub API rate limit (60/hr unauthenticated)** → batch queries in one script, cache results to `/tmp/`, avoid re-fetching the same data across multiple terminal calls.
