# Career — LinkedIn

## Backends

| Backend | When | Command |
|---------|------|---------|
| linkedin-scraper-mcp | full profile + job search | `mcporter call 'linkedin.get_person_profile(public_identifier: "...")'` |
| Jina Reader | public page read only | `curl -s "https://r.jina.ai/https://www.linkedin.com/in/..."` |

## linkedin-scraper-mcp setup

```bash
# Install
pip install linkedin-scraper-mcp

# Login (needs browser UI — VNC on server)
linkedin-scraper-mcp --login --no-headless

# Start service
linkedin-scraper-mcp --transport streamable-http --port 8001

# Register with mcporter
mcporter config add linkedin http://localhost:8001/mcp
```

### Profile lookup
```bash
mcporter call 'linkedin.get_person_profile(public_identifier: "john-doe-123456")'
```

### Job search
```bash
mcporter call 'linkedin.search_jobs(keywords: "software engineer", location: "San Francisco", limit: 10)'
```

### Company page
```bash
mcporter call 'linkedin.get_company(public_identifier: "google")'
```

## Pitfalls
- Login requires a visible browser window — headless servers need VNC
- Session saved to `~/.linkedin-mcp/profile/` after first login
- Rate limits apply; space out calls
