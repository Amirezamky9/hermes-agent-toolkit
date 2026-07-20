# Multi-Platform Ecosystem / Landscape Research

Research pattern for answering: *"What are people building with X, what problems do they hit, what's community sentiment across N platforms?"*

## Strategy: Two-Wave Parallel Discovery

| Wave | Cost | Goal |
|------|------|------|
| **1 — Discovery** | Cheap, parallel | Hit all platforms simultaneously. Find candidate sources only (titles, scores, snippets). |
| **2 — Depth** | Expensive, sequential | Deep-read only the highest-signal results (top upvoted, most comments, non-duplicate). |

## Wave 1 — Per-Platform First Tool

Launch ALL of these in parallel (no dependencies between them):

| Platform | Tool | Notes |
|----------|------|-------|
| **Exa semantic search** | `mcporter call 'exa.web_search_exa(query: "...", numResults: 15)'` | Best for broad discovery. Query from multiple angles. |
| **Reddit** | `rdt search "QUERY" --subreddit all --sort relevance --limit 7 --time year` | Then specific subreddits (`n8n`, `automation`, `selfhosted`, `devops`). |
| **GitHub** | `gh search repos "QUERY" --sort stars --limit 15` | Then `gh repo view OWNER/REPO --json ...` for per-repo stats. |
| **Hacker News** | `curl -s "https://hn.algolia.com/api/v1/search?query=QUERY&tags=story&hitsPerPage=20"` | Algolia API, public. Includes point scores + comment counts. |
| **Community Forums (Discourse)** | `curl -s "https://r.jina.ai/URL"` | Jina Reader works well on Discourse topics. Find them via Exa first (`site:community.n8n.io`). |
| **X / Twitter** | `curl html.duckduckgo.com/html/?q=site:twitter.com+QUERY` | Weak fallback only (snippets, no full tweets). Only useful when twitter-cli has auth. |

## Wave 2 — Culling Rules

After all Wave-1 results arrive:

1. **Rank** by score, comment count, and source freshness
2. **Deduplicate** — discard cross-posted duplicates
3. **Deep-read** only the top 3-5 items per platform (full post + top comments via `rdt read` or Jina Reader)
4. **Cross-check** — if a claim appears in only one source, flag it as weak

## Pitfalls

- **Don't hammer the same backend.** Reddit search + GitHub search in the same wave is fine (different backends). Exa + GitHub in the same wave is fine. Two `rdt search` calls in one wave: stagger by ≥1s.
- **Twitter without auth is nearly useless.** DDG `site:twitter.com` returns only link+title with no text. Don't block on it; just file it under "weak source" and move on.
- **Jina Reader on Reddit URLs:** Works for individual post URLs, **not** for search results. Use `rdt search` for discovery, then optionally Jina for full markdown of a known post.
- **Hacker News Algolia API:** Free, no key needed, but rate-limits at ~10 req/s. Stay under that.
- **Exa token limit:** Free tier is generous (~1000 queries/mo). For a single research session you won't hit it.
