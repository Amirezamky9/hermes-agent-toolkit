# Bulk Extraction: All MCP Best Practices Techniques

> Extracted 2026-07-09. Run this workflow whenever MCP updates its best-practices docs.

## Pattern: One-per-file extraction

When the user asks for ALL MCP best practices techniques, deliver them as **individual numbered files in a folder**, not one combined file.

```
n8n-best-practices/
  01-chatbot.md
  02-scheduling.md
  03-form-input.md
  ...
  17-web-app.md
```

## Workflow (exact commands)

```bash
# 1. Get the list
mcp_n8n_mcp_get_workflow_best_practices("list")

# 2. Fetch each documented technique individually
mcp_n8n_mcp_get_workflow_best_practices("chatbot")
mcp_n8n_mcp_get_workflow_best_practices("scheduling")
# ... etc for all 17

# 3. After collecting all docs in a single markdown file,
#    split it into individual files by section headers
cd /workspace && mkdir -p n8n-best-practices

python3 -c "
import re, os

with open('n8n-best-practices-all-17.md', 'r') as f:
    full = f.read()

sections = re.split(r'\n(?=# \d+\. )', full.strip())

for s in sections:
    if not s.strip(): continue
    m = re.match(r'^# (\d+)\. ([^\n]+)', s)
    if m:
        num = int(m.group(1))
        name = m.group(2).strip()
        clean = re.sub(r'[✅🟡&]', '', name).strip().lower().replace(' ', '-').replace('--', '-')
        fname = f'{num:02d}-{clean}.md'
        with open(f'n8n-best-practices/{fname}', 'w') as fw:
            fw.write(s.strip() + '\n')
"
```

## Why this pattern

- **MCP rate-limits** each `get_workflow_best_practices` call. For batch extraction call them in groups of 6 (the max parallel tool calls per turn).
- **5 undocumented techniques** (monitoring, enrichment, data_analysis, knowledge_base, human_in_the_loop) return short generic stubs — still extract them so the user has a complete set.
- **The index file** (`mcp-best-practices-index.md` in n8n-patterns skill) should be patched after extraction to reflect the latest count and status of each technique.