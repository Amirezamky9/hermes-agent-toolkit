# Phase Reference

Quick reference for what each phase skill does, its entry/exit artifacts, and its tool permissions.

## Phase 1 — n8n-intake

**Entry:** User request ("یه ربات تلگرام می‌خوام")
**Exit:** `intake.yaml` file written to workspace

**Structure (4 sub-phases):**
| Phase | Focus | Key action | Tools |
|---|---|---|---|
| A | Discovery | clarify() questions → detect pattern | clarify, skill_view |
| B | Search | webhook_wrapper.py search | terminal only |
| C | Credentials | list_credentials | one MCP call |
| D | Output | write intake.yaml | write_file |

**Forbidden:** create_workflow, update_workflow, create_data_table, search_nodes, get_node_types, get_sdk_reference, execute, test, publish, archive, search_workflows (use webhook instead)

**Must NOT skip Phase B** even when user says "from scratch".

## Phase 2 — n8n-planner

**Entry:** `intake.yaml` file
**Exit:** `ARCHITECTURE.md` + task breakdown

**Structure:**
| Phase | Focus | Key action |
|---|---|---|
| 1 | Read intake + fetch | read_file + webhook_wrapper.py fetch for each UUID |
| 2 | List credentials | list_credentials |
| 2.5 | Business model Q&A | clarify() — never assume product type |
| 3 | Architecture design | Write ARCHITECTURE.md with Mermaid diagrams, node tables |
| 4 | Present | Summarize, let user read |
| 5 | STOP | Hand off to builder |

**Key rules:**
- No-code first: prefer native n8n nodes over Code nodes
- State-First routing over Type-First
- editMessageText over sendMessage (except /start)
- Execute Sub-workflow over HTTP Request for cross-WF calls
- Answer Callback Query is mandatory in every callback path

## Phase 3 — n8n-builder

**Entry:** `deck-*.yaml` (primary, from Reviewer) or `ARCHITECTURE.md` (fallback, from Planner) + user confirmation
**Exit:** All workflows built in n8n, credentials set, report files written

**Build order per session:**
1. Read deck-*.yaml (if exists) OR ARCHITECTURE.md → summarize to user
   → Deck has node-level build specs; ARCHITECTURE.md is fallback only
2. Get SDK reference + list credentials
3. Build Data Tables (if any)
4. Build ONE workflow at a time (max ~20 nodes per create call)
5. Set credentials immediately after each create
6. Verify with get_workflow_details
7. Write report YAML → ask user → next workflow

**Key rules:**
- Atomic operations (`update_workflow`) preferred over full SDK rewrite for modifications
- Prevent duplicate Data Table creation (check first)
- Always verify credentials on every Telegram node
- Resume mode via session_search if ARCHITECTURE.md is missing
