# Scavenge Interesting Content (Reddit + GitHub)

## When to use

User asks: "find something interesting", "show me cool tech discussions", "what's trending", "find 3 interesting things from Reddit/GitHub", or any open-ended exploration request without a specific query. This is NOT for answering a specific question — that's what the main agent-reach skill and `web-research` are for.

## Workflow (proven, do not modify)

### 1. Health check

```bash
rdt whoami                   # verify Reddit auth before investing in searches
gh auth status 2>&1 || true  # verify GitHub auth (may fail if unauthenticated — fine, use curl fallback)
```

### 2. Scan Reddit for interesting content

Use `rdt sub` to browse subreddits by their most recent hot posts. Process output with regex-based parsing (rdt-cli YAML uses custom tags like `!!int`, `!!bool` — `yaml.safe_load()` will crash).

**Target subreddits for tech content:**
- `programming` — highest signal-to-noise for technical discussions
- `artificial` — AI/ML news and discussions (subscribers: 1.3M)
- `MachineLearning` — ML research (note: may return empty children if hit during quiet hours)
- `opensource`, `linux`, `rust`, `python` — more niche but high quality

```bash
# Browse a subreddit
rdt sub "programming" --limit 10 2>&1 > /tmp/rd_sub_programming.txt

# Parse with regex (NOT yaml.safe_load!)
python3 -c "
import re, sys
data = open('/tmp/rd_sub_programming.txt').read()
blocks = re.split(r'\s+- \"kind\": \"t3\"', data)
for block in blocks[1:]:
    title = re.search(r'\"title\": \"((?:[^\"\\\\]|\\\\.)*)\"', block)
    score = re.search(r'\"score\": !!int \"(\d+)\"', block)
    comments = re.search(r'\"num_comments\": !!int \"(\d+)\"', block)
    pid = re.search(r'\"id\": \"((?:[^\"\\\\]|\\\\.)*)\"', block)
    sub = re.search(r'\"subreddit\": \"((?:[^\"\\\\]|\\\\.)*)\"', block)
    if title:
        clean = re.sub(r'\\\\[nt\"]', ' ', title.group(1)).strip()
        s = int(score.group(1)) if score else 0
        c = int(comments.group(1)) if comments else 0
        pid_v = pid.group(1) if pid else '?'
        print(f'{pid_v} | [{s} pts, {c} com] {clean[:120]}')
"
```

### 3. Read interesting posts in depth

Pick posts with high comment counts (discussion quality) or unique topics:

```bash
# Convention: temp files go under /tmp/rd_*
rdt read POST_ID -n 20 --compact > /tmp/rd_post_POSTID.txt

# Extract title + top comments via regex
python3 -c "
import re
data = open('/tmp/rd_post_POSTID.txt').read()
title = re.search(r'\"title\": \"((?:[^\"\\\\]|\\\\.)*)\"', data)
text = re.search(r'\"selftext\": \"((?:[^\"\\\\]|\\\\.)*)\"', data)
comments = re.findall(r'\"body\": \"((?:[^\"\\\\]|\\\\.)*)\"', data)
scores = re.findall(r'\"score\": !!int \"(\d+)\"', data)  # first = post score
print(f'Title: {title.group(1) if title else \"?\"} [{scores[0] if scores else \"?\"} pts]')
if text: print(f'Selftext: {re.sub(r\"\\\\[nt\"]\", \" \", text.group(1))[:300]}')
for i, (c, s) in enumerate(zip(comments[:10], scores[1:11]), 1):
    body = re.sub(r'\\\\[nt\"]', ' ', c)[:200]
    print(f'  {i}. [+{s}] {body}')
"
```

### 4. Scan GitHub trending

Two complementary approaches:

**A) GitHub CLI (authenticated):**
```bash
gh search repos "stars:>1000 created:>2025-01-01" --limit 5 --sort stars 2>&1 | head -20
gh search repos "LLM agent" --sort stars --limit 5 2>&1 | head -10
```

**B) GitHub trending page (no auth needed):**
```bash
curl -sL "https://github.com/trending" -H "User-Agent: Mozilla/5.0" 2>/dev/null | python3 -c "
import re, sys, html as h
data = sys.stdin.read()
blocks = re.findall(r'<h2[^>]*class=\"h3 lh-condensed\">(.*?)</h2>', data, re.DOTALL)
for block in blocks[:8]:
    href = re.search(r'href=\"/([^\"]+)\"', block)
    if href: print(f'  {href.group(1)}')
"
```

**Pitfall:** The GitHub API (`api.github.com/search/repositories`) can return empty or rate-limited responses without auth. The `gh search repos` CLI works if authenticated. The `github.com/trending` HTML scrape always works but requires extracting repo name/language/description from HTML classes.

Alternative approach for GitHub (more reliable extraction):
```bash
curl -sL "https://github.com/trending" -H "User-Agent: Mozilla/5.0" 2>/dev/null | python3 -c "
import re, sys, html as h
data = sys.stdin.read()
repos = re.findall(
    r'href=\"/trending\">Trending</a>.*?<article class=\"Box-row\">',
    data, re.DOTALL
)
if not repos:
    # Fallback: direct extraction from page
    blocks = re.findall(r'<article class=\"Box-row\".*?</article>', data, re.DOTALL)
    for block in blocks[:8]:
        name = re.search(r'href=\"/([^\"]+?/[^\"]+?)\"', block)
        lang = re.search(r'<span itemprop=\"programmingLanguage\">([^<]+)</span>', block)
        desc = re.search(r'<p class=\"col-9[^\"]*\".*?>(.*?)</p>', block, re.DOTALL)
        stars = re.search(r'<span[^>]*class=\"d-inline-block float-sm-right\">(.*?)</span>', block)
        if name:
            n = h.unescape(name.group(1)).strip()
            d = h.unescape(re.sub(r'<[^>]+>', '', desc.group(1))).strip()[:100] if desc else ''
            l = lang.group(1) if lang else '?'
            s = ''.join(re.findall(r'\d', stars.group(1))) if stars else '?'
            print(f'{n} [{l}] ⭐{s} — {d}')
"
```

### 5. Synthesis

Pick 3 items with genuinely interesting stories — prefer:
- **Technical depth** (not just hype, has actual substance in the discussion)
- **Recency** (posted within the last 3-5 days)
- **Engagement** (high comment count or polarizing topic)
- **Novelty** (not rehashed mainstream news)

Output format: plain bullet points, 2-3 points each, no fluff.
- Each item starts with source label (e.g., "r/programming:" or "GitHub trending:")
- Then title in italics
- Then 2-3 factual bullet points describing what's interesting

## Pitfalls

1. **rdt-cli subreddit name is case-sensitive** — `rdt sub "MachineLearning"` often returns empty children (listing kind with 0 entries) while `rdt sub "programming"` works fine. If a sub returns empty, either the sub name is wrong or the sub has only moderator posts visible.
2. **rdt-cli YAML breaks yaml.safe_load()** — always use regex extraction. Never pipe through Python's yaml module.
3. **rdt read takes a post ID, not a URL path** — e.g. `rdt read 1upo7f6` not `rdt read /r/programming/comments/1upo7f6/...`
4. **`--compact` is mandatory for `rdt read`** — without it, output is too verbose to parse.
5. **`-n 20` limits comments** to a representative sample. For posts with 80+ comments, 20 is enough for sentiment.
6. **GitHub trending HTML class names change occasionally** — the Python regex extraction is fragile. If no repos are found, inspect the raw HTML with `grep -o 'h3.*'` first.
7. **rdt search vs rdt sub** — `rdt search "query"` searches all of Reddit by relevance; `rdt sub "name"` shows the recent hot posts of a specific subreddit. For "find interesting things", `rdt sub` is preferred since we want discovery, not a specific topic.