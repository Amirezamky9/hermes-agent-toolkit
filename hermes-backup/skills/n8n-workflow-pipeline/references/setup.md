# n8n Pipeline — Setup & Verification

## Full install procedure (from scratch)

### Prerequisites
```bash
# 1. Verify Hermes in PATH
export PATH="$HOME/.hermes/hermes-agent:$PATH"
hermes --version

# 2. Verify MCP n8n server
hermes mcp list
# Should show: n8n-mcp enabled, https://n8n.mym8m.cloud

# 3. Verify Node.js + nvm
command -v nvm || export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
node -v   # expected: v22.15.0

# 4. Verify mimo CLI
mimo --version  # expected: 0.1.5
# If missing: npm install -g @mimo-ai/cli
export PATH="$HOME/.local/node/bin:$PATH"  # persist in .bashrc
```

### Copy skills
```bash
# From repo to Hermes skills dir
rm -rf ~/.hermes/skills/n8n-{intake,planner,builder}
cp -r /workspace/n8n-skills/n8n-intake ~/.hermes/skills/
cp -r /workspace/n8n-skills/n8n-planner ~/.hermes/skills/
cp -r /workspace/n8n-skills/n8n-builder ~/.hermes/skills/
```

### Verify each skill
```bash
hermes skills list | grep n8n
# Expected: n8n-intake, n8n-planner, n8n-builder, n8n-workflow-pipeline

# Check file counts
for d in n8n-intake n8n-planner n8n-builder; do
  echo "$d: $(find ~/.hermes/skills/$d -type f | wc -l) files"
done
# Expected: n8n-intake: 12, n8n-planner: 5, n8n-builder: 7
```

### Verify webhook_wrapper
```bash
# Search test (should return results)
python3 ~/.hermes/skills/n8n-builder/webhook_wrapper.py search --query "telegram bot" --category "AI Chatbot"

# Fetch test (use a real UUID from search results)
python3 ~/.hermes/skills/n8n-builder/webhook_wrapper.py fetch <UUID>
```

### Verify MCP tools work
```python
# In Hermes session, call:
mcp_n8n_mcp_list_credentials()  # Should return 10+ credentials
mcp_n8n_mcp_search_projects()   # Should return 1 personal project
```

## Repair guide

| Symptom | Fix |
|---|---|
| `hermes: not found` | Add to .bashrc: `export PATH="$HOME/.hermes/hermes-agent:$PATH"` |
| MCP responds empty | Check config.yaml at ~/.hermes/config.yaml for `mcp_servers.n8n-mcp.headers.Authorization` |
| webhook empty (code 4) | The webhook endpoint on n8n may be down. Try `search` with different query. |
| mimo not found | Add to .bashrc: `export PATH="$HOME/.local/node/bin:$PATH"` |
