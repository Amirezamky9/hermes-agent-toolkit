---
name: deep-research
description: >-
  Use when the user asks for deep investigation, research, comparison, evaluation,
  source verification, architecture decision, or any question where a shallow answer
  would be unreliable. Loads before web-research when multi-angle evidence is required.
  Triggers: "research", "investigate", "compare", "evaluate", "deep dive", "source
  verification", "architecture decision", "implement vs buy", "should we use",
  "landscape", "ecosystem", "tradeoff study".
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [research, kanban, orchestration, rate-limit, subagent, execution, task-management]
    related_skills: [agent-reach, web-research, plan, todo]
---

# Deep Research — Execution Engine with Kanban & Workload Control

## Overview

This skill turns a user's request into a **managed research project**. It behaves like a
research project manager, not a search assistant. Every request is decomposed into
atomic Kanban tasks, executed in rate-limit-aware waves, tracked persistently, and
synthesized into a senior-analyst-quality conclusion.

**Priority hierarchy:** Accuracy > Evidence quality > Cross-checking > Coverage > Speed > Cost
**Execution philosophy:** Kanban-first, rate-limit-aware, wave-scheduled, subagent-orchestrated.

**Guardrails:** Never trust a single source. Prefer primary sources. Separate discovery
from validation. Track all tasks on the board. Never hide blockers. Never hammer a
limited backend. Never collapse conflicting claims into a fake consensus.

---

## When to Use

**Always load** when the user asks for:
- "Research X" / "Deep dive on Y" / "Landscape of Z"
- "Compare A and B" — tools, libraries, architectures, products
- "Should we use Z?" — evaluation with tradeoffs
- "What's the best way to implement X?"
- "Is X better than Y?" — evidence-grounded comparison
- "Verify / validate this claim" — especially multi-source
- "What are people saying about X?" — multi-platform sentiment
- Architecture or design decisions with alternatives
- Market / ecosystem / landscape research
- Source or contradiction resolution
- Any request with ≥3 distinct subquestions or ≥2 platforms

**Do not use** for:
- Simple lookups (one fact, one source) — use web-research or direct tools
- Single-page reads — use Jina Reader directly
- Platform-bound tasks an existing dedicated skill handles better

When a smaller tool suffices, say so and skip the Kanban workflow.

---

## Core Design Principles

1. **Never trust a single source.** Every claim needs ≥2 independent corroborations.
2. **Prefer primary sources** — source code beats release notes beats issues beats posts.
3. **Separate discovery from validation.** Discovery is broad and cheap; validation is targeted.
4. **Kanban-first.** Every piece of work gets a card. No card, no work.
5. **Rate-limit-aware.** Detect throttle, pause that lane, continue others, resume later.
6. **Wave scheduling.** Group tasks into waves; never launch everything at once.
7. **Subagent per subquestion.** One subagent = one narrow task. No overloaded agents.
8. **Deduplicate aggressively.** Merge overlapping outputs; keep only the strongest evidence.
9. **Track assumptions explicitly.** Every inference is tagged.
10. **Mark uncertainty clearly.** Low-confidence claims get a "(speculative)" tag.
11. **Cheapest tool first.** curl/Jina > browser rendering; GH API > crawling; feedparser > scraping.
12. **Escalate to heavier tools only when necessary.**

---

## 1) Kanban Workflow

### 1.1 Board Columns

| Column | Purpose |
|--------|---------|
| **Backlog** | All tasks after decomposition, not yet ready |
| **Ready** | Tasks with no unmet dependencies, eligible to run |
| **In Progress** | Task currently being worked |
| **Waiting** | Task blocked by external dependency (rate limit, login, key, delayed source) |
| **Review** | Evidence collected, awaiting cross-check or validation |
| **Done** | Completed and synthesised |
| **Blocked** | Cannot proceed without user intervention or unresolved contradiction |

### 1.2 Task Card Schema

Every task card includes:

```
ID: DR-001
Title:
Description:
Priority: P0/P1/P2/P3
Status: Backlog | Ready | In Progress | Waiting | Review | Done | Blocked
Owner: self | subagent-<name>
Dependencies: [DR-002, DR-003]
Estimated Effort: small | medium | large | xlarge
Tool Plan: [tool or command to use]
Source Strategy: [which source types to consult]
Evidence Requirements: [minimum evidence needed]
Completion Criteria: [how we know this task is done]
Created:
Updated:
```

### 1.3 Board Persistence

Store the Kanban board as a file for long-running research.

**Location:** `.hermes/research/<research-slug>/kanban.md` for the human-readable overview,
`.hermes/research/<research-slug>/kanban.json` for machine-readable state.

**Kanban overview format (kanban.md):**

```
# Kanban Board: <Research Title>

## Backlog
| ID | Title | Priority | Dependencies | Est. Effort |
|----|-------|----------|--------------|-------------|

## Ready
...

## In Progress
...

## Waiting
| ID | Title | Waiting On | Since |
|----|-------|-----------|-------|

## Review
...

## Done
...

## Blocked
| ID | Title | Blocked By | Since |
|----|-------|-----------|-------|

## Board Health
- Total tasks: N
- Completed: N
- In progress: N
- Blocked/Waiting: N
- Current phase: Phase N
- Next scheduled wave: Wave N
```

**Task detail format (kanban.json):**

```json
{
  "research_id": "slug",
  "title": "Research Title",
  "created": "2026-07-04T19:00:00Z",
  "updated": "2026-07-04T20:30:00Z",
  "current_phase": 3,
  "current_wave": 2,
  "total_waves": 4,
  "tasks": {
    "DR-001": {
      "title": "",
      "description": "",
      "priority": "P0",
      "status": "Done",
      "owner": "self",
      "dependencies": [],
      "effort": "small",
      "tool_plan": "",
      "source_strategy": "",
      "evidence_requirements": "",
      "completion_criteria": "",
      "created": "",
      "updated": "",
      "result_summary": "",
      "blocked_reason": null,
      "waiting_reason": null
    }
  },
  "log": [
    {"time": "2026-07-04T19:00:00Z", "event": "Board created", "detail": ""},
    {"time": "2026-07-04T19:05:00Z", "event": "Wave 1 started", "detail": "DR-001, DR-002"}
  ]
}
```

### 1.4 Board Update Rules

Update the board **immediately** when:
- A task starts → move to **In Progress**, timestamp it
- A task finishes → move to **Review** (not Done directly)
- A task is blocked → move to **Blocked**, state the blocker and since when
- A task is rescheduled → update its status, log the reason
- A subagent returns → update the task card with the result
- A rate limit is encountered → move affected tasks to **Waiting**, log the cooldown
- A new dependency is discovered → update the depended-upon card
- A wave completes → log completion, prepare next wave
- The board is loaded/resumed → state "Resuming from saved state"

Never leave the board stale for long-running jobs. Every state change is logged.

---

## 2) Execution Strategy

### Phase 0 — Intake

1. Understand the request. Classify depth:
   - **Shallow** (1 subquestion, 1 source type) → skip Kanban, use web-research
   - **Medium** (2–3 subquestions, 1–2 platforms) → lightweight Kanban (markdown only)
   - **Deep** (≥3 subquestions, ≥2 platforms, comparisons) → full Kanban with JSON persistence
2. Estimate effort (small / medium / large / xlarge).
3. Decide whether Kanban tracking is needed. If yes, create the board directory and files.

**Completion criterion:** Depth classified. Board created if medium+.

### Phase 1 — Task Breakdown

Decompose the request into atomic tasks. Each task is:
- One narrow question
- One source cluster
- One tool (or tool sequence)
- Independently completable

**Rules:**
- Separate discovery tasks from validation tasks
- Separate independent tasks from dependent tasks
- Place all tasks into **Backlog** first
- Assign a unique ID to each task (DR-001, DR-002, ...)
- Assign priorities (P0 = essential, P1 = important, P2 = nice to have, P3 = if time)
- Tag dependencies explicitly
- Estimate effort per task

**Completion criterion:** All tasks in Backlog with ID, priority, dependencies, and effort.

### Phase 2 — Plan the Investigation

Produce a short investigation plan:
- **Parallel work:** which tasks are independent and can fan out
- **Sequential work:** which tasks depend on earlier results
- **Rate-limit risk:** which tasks hit the same backend (space them)
- **Source types to consult:** per task
- **Subagent candidates:** which tasks should be delegated
- **Wave breakdown:** group tasks into waves (see Section 4)
- **Time sensitivity:** which claims may have changed recently

Move tasks with no unmet dependencies from Backlog → Ready.

**Completion criterion:** Written plan. Wave breakdown created. Ready queue populated.

### Phase 3 — Breadth Execution (Discovery)

Run **discovery tasks first** — these are broad, cheap, parallelizable.

1. Identify which Ready tasks are discovery (search, source-finding).
2. Execute in parallel where possible:
   - Use `delegate_task` for independent subagent work
   - Use direct tool calls for small discovery tasks
3. For each discovery task:
   - Search the source cluster
   - Extract candidate sources (ranked, with brief note on relevance)
   - Return the source list, not the full content
4. Move completed discovery tasks to **Review**.
5. Update the board after each subagent returns.

**Rate-limit rule:** If two discovery tasks hit the same backend (e.g. both call `gh search`), do not launch them simultaneously. Stagger by ≥2 seconds or put in different waves.

**Completion criterion:** Discovery tasks complete. Candidate sources gathered in Review.

### Phase 4 — Depth Execution (Validation)

Now drill into the collected sources:

1. Move validated discovery cards from Review → Ready for depth pass.
2. Execute validation tasks — these are more expensive (read full docs, inspect code, compare).
3. For each validation task:
   - Read the source in full (Jina Reader, platform-native read, etc.)
   - Extract concrete facts with version/date/repo/doc section
   - Cross-check against ≥1 additional source if possible
   - Return compact evidence notes (3–10 bullet points)
   - Label uncertainty
4. When contradictions appear between sources:
   - Create a new task card for contradiction resolution
   - Place it in Backlog, high priority
   - Execute it in the current wave if possible, else defer to next wave

**Completion criterion:** All important claims verified or flagged as contested/weak.

### Phase 5 — Rate-Limit Recovery

When any backend slows down, throttles, or fails:
1. **Detect** — identify the condition (HTTP 429, timeout, rate limit message)
2. **Pause** — move affected tasks from In Progress/Ready → **Waiting**
   - Log in the Waiting reason: "Rate-limited on <backend>, cooldown <N>s"
3. **Reschedule** — note the estimated cooldown period
4. **Continue** — execute other independent lanes while waiting
5. **Resume** — when cooldown expires, move tasks from Waiting → Ready
6. **Report** — inform the user only if the delay is significant (≥30s cumulative)

**Rule:** Never keep hammering a limited backend. Pause that lane, work other lanes, resume later.
Do not stop the entire workflow because one backend is slow.

**Completion criterion:** Affected tasks in Waiting with cooldown noted. Other lanes progressing.

### Phase 6 — Synthesis

Merge all results back:

1. Collect all Review and Done task cards.
2. Deduplicate overlapping findings.
3. Merge complementary evidence.
4. Resolve contradictions (or explain them honestly).
5. Build the final answer following the output format (Section 7).
6. Summarise the final board state.
7. Remove the board files **only** if research is truly complete and user confirms.

**Completion criterion:** Final answer delivered. Board archived or removed.

---

## 3) Kanban Rules

### Before Execution

- Break the request into atomic tasks
- Separate discovery from validation
- Separate independent from dependent
- Place all into **Backlog** first
- Move only executable tasks (no unmet dependencies) into **Ready**

### During Execution

- Only run tasks that are in **Ready** or **In Progress**
- When a task is blocked → **Blocked**, state the blocker and since when
- When waiting for rate limits, login, keys, or delayed sources → **Waiting**
- When evidence collected but unvalidated → **Review**
- Only move to **Done** after validation pass confirms it
- Do not hide unresolved work. Do not lose task state between phases.

---

## 4) Rate-Limit / Workload Control

### 4.1 Detection

Watch for these signals:
- HTTP 429 / 403 / 503
- "Rate limit exceeded" in output
- Timeout on a normally-fast endpoint
- Degraded response times (significantly slower than baseline)

### 4.2 Mitigation

| Signal | Action |
|--------|--------|
| HTTP 429 | Pause lane, backoff 5s then retry; double backoff each retry |
| Timeout | Retry once with longer timeout; if same, switch to fallback backend |
| Generic failure | Try fallback backend (agent-reach backends have ordered fallbacks) |
| Provider-level limit | Batch work into smaller chunks, spread across time windows |

### 4.3 Scheduling Rules

- **Do not** fire all requests at once
- **Do** batch by source type, topic, or platform
- **Do** reuse cached evidence when possible (session memory, previous card results)
- **Do** prefer cheaper tools before expensive ones (curl/Jina > Crawl4AI)
- **Do** create a staged execution plan if the workload is large
- **Do** spread work across multiple intervals
- **Do** store partial results safely (update task cards with partial findings)

### 4.4 Staged Execution Plan Template

For very large workloads:

```
Total tasks: 12
Estimated waves: 3
Wave 1 (cheap, parallel): discovery tasks — DR-001, DR-002, DR-003, DR-004
Wave 2 (medium, dependent): validation tasks — DR-005, DR-006 (depends on DR-001), DR-007
Wave 3 (expensive, depth): deep reads + comparisons — DR-008, DR-009, DR-010
Wave 4 (synthesis): merge, deduplicate, write — DR-011, DR-012
Estimated total time: ~X min
```

---

## 5) Subagent Expansion Policy

### 5.1 When to Create Subagents

Create subagents when:
- Multiple sources must be checked in parallel (≥3 independent sources)
- Multiple platforms are involved (e.g. GitHub + Twitter + Reddit)
- Multiple claims need independent verification (≥3 distinct claims)
- The request contains many unrelated subquestions (≥4)
- The task would otherwise exceed rate limits or time budget in one pass

### 5.2 Subagent Card

Each subagent receives:

```
goal: one narrow question (exactly one)
context:
  - source cluster to search
  - deliverable: "return compact evidence notes, not essays"
  - effort boundary: "small" (search only), "medium" (read 2-3 pages), "large" (deep analysis)
  - evidence format: 3-10 bullet points, each with source URL
  - rule: "return source-backed evidence only — label speculation as speculation"
  - confidence: required per claim
  - unknowns: list explicitly ("I did not find X")
```

### 5.3 Subagent Output Requirements

Each subagent must return:
- **Concise findings** — 3–10 bullet points max
- **Concrete evidence** — specific URLs, dates, version numbers, repo paths
- **Confidence level** — High / Medium / Low per claim
- **Blockers** — what prevented going deeper
- **Next step** — one recommended follow-up action

### 5.4 Subagent Consolidation

When subagents return overlapping results:
1. Merge and deduplicate
2. Keep the strongest evidence only (per evidence hierarchy)
3. Explain which evidence was discarded and why (one line)
4. Update the corresponding task card with the consolidated result

---

## 6) Subagent Scheduling Rules

### 6.1 Wave-Based Launch

Do not launch all subagents simultaneously. Instead:

1. **Group into waves** based on:
   - Backend affinity (same backend → same wave or staggered)
   - Priority (P0 tasks in earliest waves)
   - Cost (cheap discovery first, expensive validation later)
   - Dependencies (blocking tasks before their dependents)

2. **Wave rules:**
   - Wave 1: all discovery, all cheap tools, all P0 independent
   - Wave 2: medium-cost validation, contradiction resolution
   - Wave 3: expensive deep reads, comparisons, edge cases
   - Wave 4: synthesis (always done by the main agent, never delegated)

3. **Between waves:** update the board, check for rate-limit signals, consolidate partial results.

4. **Stagger within waves:** if two tasks in the same wave hit the same backend, delay the second by 1-2 seconds.

### 6.2 Maximum Concurrency

| Workload | Max simultaneous subagents |
|----------|---------------------------|
| Small (3 tasks) | 2 |
| Medium (4-6 tasks) | 3 |
| Large (7-12 tasks) | 4 |
| XLarge (13+ tasks) | 4 per wave, more waves |

Respect the platform's `delegation.max_concurrent_children` limit. Stay under it.

**Delegation config with multi-provider fallbacks:** See `references/delegation-config.md` for the tested pattern.

### 6.3 Pause and Resume

If too many subagents are needed for one wave:
1. Build a staged queue
2. Execute in rounds (batch of N per round)
3. Wait between rounds (2-5s minimum)
4. Keep the Kanban board updated after each round
5. If a subagent is blocked, move its card to Blocked, continue the wave

---

## 7) Tool Strategy

### 7.1 Search / Discovery

| Order | Tool | When |
|-------|------|------|
| 1 | Exa / semantic search (mcporter) | Broad discovery, multi-concept queries |
| 2 | Hermes web search | General web, fallback |
| 3 | Platform-native search (gh, bili, twitter) | When target is platform-specific |
| 4 | DuckDuckGo HTML / Jina Reader | JS-heavy or rate-limiting sites |
| 5 | Crawl4AI | Site-tree mapping, doc site traversal |

### 7.2 Reading / Extraction

| Order | Tool | When |
|-------|------|------|
| 1 | Jina Reader (curl r.jina.ai/URL) | Any web page, returns clean markdown |
| 2 | Platform-native read (gh repo view, bili info, yt-dlp) | Platform-specific content |
| 3 | feedparser | RSS/Atom feeds |
| 4 | curl + Python regex/BS4 | Static pages the reader fails on |
| 5 | Crawl4AI | JS-rendered content, multi-page extraction |

### 7.3 Platform-Specific Sources

Always run `agent-reach doctor --json` before using any platform-specific tool.
Select the `active_backend`, failover automatically, never assume credentials.

| Platform | Tool | Health check |
|----------|------|-------------|
| GitHub | `gh` CLI | `gh auth status` for private repos |
| YouTube | `yt-dlp --dump-json` | Check yt-dlp installed |
| Bilibili | `bili` CLI | Check bili installed |
| V2EX | curl V2EX API | Public, no check needed |
| RSS | feedparser | No check needed |
| Twitter/X | twitter-cli | doctor → twitter.active_backend |
| Reddit | rdt-cli or opencli | doctor → reddit.active_backend |
| Xiaohongshu | opencli or xiaohongshu-mcp | doctor → xiaohongshu.active_backend |
| LinkedIn | mcporter or Jina Reader | Check linkedin-scraper-mcp running |
| Facebook/Insta | opencli | Desktop-only |
| Xiaoyuzhou | transcribe.sh | Check ffmpeg + Groq key |

---

## 8) Research Quality Rules

Even with task management, maintain these standards:

- **Evidence hierarchy:** source code > official docs > release notes > issues > community > commentary
- **Score sources by:** authority, freshness, completeness, bias, technical depth, reliability
- **Implementation reality:** distinguish documented / experimental / partial / theoretical / unsupported
- **Cross-check claims** against ≥1 additional independent source for high-stakes claims
- **State uncertainty** — every claim gets a confidence level
- **Avoid false consensus** — explain disagreements, do not collapse them
- **Time awareness** — flag sources that may be stale; prefer within current major version

### Comparison Dimensions

When comparing tools, libraries, or agents, evaluate on:

| Dimension | What to check |
|-----------|---------------|
| Architecture | Design model, dependencies, runtime requirements |
| Maintenance | Stars, last commit, release cadence, open issues, PR response |
| Docs quality | Quickstart, API docs, examples, troubleshooting |
| Setup friction | Install steps, deps, config, platform support |
| Runtime cost | Memory, CPU, GPU, API costs, disk, startup |
| Reliability | CI status, known bugs, test coverage, uptime |
| Scope fit | Solves the real problem vs. over-engineered |
| Fallback behavior | Graceful degradation vs. hard failure |
| Integration surface | APIs, plugins, hooks, protocol support |
| Upstream activity | Commits, contributors, governance, bus factor |

Always answer: why it exists, what it's better at, what it's worse at, is it worth installing.

---

## 9) Heavy Task Handling

For very heavy tasks (xlarge effort, estimated >15 min execution):

1. **Split by source type** — web sources, code sources, platform sources, human sources
2. **Split by time range** — current state vs. history
3. **Split by platform** — one wave per platform
4. **Split by language/region** — English sources, Chinese sources, etc.
5. **Split by claim type** — factual claims, comparative claims, predictive claims

If a task cannot finish in one session:
- Create a continuation plan as the final card
- Mark remaining cards clearly with "CONTINUATION REQUIRED"
- Save the board to `.hermes/research/<slug>/kanban.json`
- End with: "This research requires continuation. Run `deep-research resume <slug>` to continue."
- Resume by loading the board file and re-entering the execution loop at the earliest In Progress or Ready task.

**Rule:** Do not force all work into one execution burst. If it's too large, acknowledge it, save state, and plan continuation.

---

## 10) Agent-Reach Integration

Agent-Reach is a **specialized backend selector/router**, not the default.

**Use when:** source is platform-specific (Twitter, Reddit, Xiaohongshu, Bilibili), a dedicated backend is installed, or it has a clear fidelity advantage.

**Do not use when:** curl+Jina for web pages, feedparser for RSS, gh for GitHub — cheaper and cleaner.

**Before each Agent-Reach call:**
1. `agent-reach doctor --json` — check health
2. Select the platform's `active_backend`
3. Detect auth needs (status:warn = needs login)
4. Fall back on failure
5. Never assume cookies/tokens/browser sessions exist

---

## 11) Output Format

When this skill produces a final answer (Phase 6 complete), the response includes:

### Executive Summary
One paragraph with the bottom line.

### Kanban Board Snapshot
```
Phase: 6 — Synthesis complete
Tasks: 12 total | 10 Done | 1 Blocked | 1 Waiting
Waves: 3 of 4 complete
```

### Findings
The main discovered facts, organized by subquestion.

### Evidence
Compact list of most important supporting sources (title, URL, type, date).

### Source Comparison
Where sources agree or differ, and why.

### Work Completed
Cards that reached Done — what was achieved.

### Work Remaining / Blockers
Cards still in Backlog, Blocked, or Waiting — honest status.

### Practical Recommendation
What the user should actually do next.

### Risks / Limitations
What may break, what requires login/cookies/proxy/keys/extra setup.

### Confidence
High / Medium / Low, with the reason.

### Next Scheduled Step
If Kanban board is not fully Done: "Next action: resume Wave N, execute [task IDs]."
If fully Done: "Research complete. Board archived at <path>."

---

## 12) Special Rule for Deep Workloads

If the research request is broad enough to cause rate limits or high latency:
- Do not run everything immediately
- Create subagents
- Stagger execution across waves
- Preserve partial results in task cards
- Continue in waves
- Keep the user informed through the board state
- If it exceeds one session, save the board and plan a continuation

This skill acts like a careful research manager with a Kanban system and workload control,
not a brute-force scraper.

---

## Common Pitfalls

1. **Skipping Phase 0.** Classify the depth first. A shallow lookup doesn't need a Kanban board.

2. **Creating too many subagents.** Max 4 per wave. Beyond that, build more waves.

3. **Firehosing the same backend.** If 3 tasks all call `gh search`, stagger them or put them in different waves.

4. **Overloading subagents.** One subagent = one narrow question. If it should do 3 things, split into 3 tasks.

5. **Stale boards.** Update after every event — task start, finish, block, reschedule, subagent return.

6. **Skipping the validation pass.** Depth (Phase 4) and validation are what separate deep research from shallow search.

7. **False consensus.** If sources disagree, explain it. Do not collapse into a fake unified story.

8. **Assuming credentials exist.** Run health checks. Ask the user if auth is missing. Never guess.

9. **Not saving partial results.** If a task takes 5 minutes and fails on step 4, the 3 successful steps are lost. Save intermediate card updates.

10. **Forcing completion.** If the research is xlarge and the session is running long, save the board and plan continuation instead of rushing.

11. **Kanban toolset disabled.** The `kanban` toolset may be listed in `skills.disabled` or absent from `platform_toolsets.cli`. Before first Kanban use, verify: `grep kanban ~/.hermes/config.yaml`. If missing from `platform_toolsets.cli`, add it. If in `skills.disabled`, remove it. The board files (`~/.hermes/research/`) also need the directory to exist — create `mkdir -p ~/.hermes/research` if absent.

12. **Over-dispatching subagents for well-known subjects.** If the user asks "research X" and X is a well-known product, game, book, or concept with clear canonical sources (Wikipedia, BGG, official docs), do NOT dispatch subagents. Subagents take 2-3 minutes each and return redundant results. Instead: use `curl r.jina.ai/URL` directly on 2-3 canonical sources. The rule is: if you can name the authoritative source from general knowledge (e.g., "Coup rules are on BGG"), use direct Jina/curl. Subagents are for when the sources are UNKNOWN or SCATTERED across many platforms. This saves 3+ minutes of user wait time per request.

---

## Definition of Done

This skill succeeds only when it can:
1. Decompose a hard research request into Kanban tasks with IDs, priorities, and dependencies
2. Track task state persistently (kanban.md + kanban.json)
3. Fan out subagents intelligently in waves
4. Avoid rate-limit failures by scheduling work with backoffs
5. Resume long jobs cleanly from saved board state
6. Still produce high-quality research output at the end (evidence-backed, uncertainty surfaced, contradictions resolved or explained, recommendation clear)

---

## Verification Checklist

- [ ] Phase 0: depth classified (shallow/medium/deep), board created if medium+
- [ ] Phase 1: all tasks decomposed into Backlog with ID, priority, dependencies, effort
- [ ] Phase 2: wave breakdown created, Ready queue populated
- [ ] Phase 3: discovery tasks executed in parallel, candidate sources gathered
- [ ] Phase 4: validation tasks executed, contradictions resolved
- [ ] Phase 5: rate limits detected and handled (tasks moved to Waiting), other lanes continued
- [ ] Phase 6: results merged, deduplicated, synthesised, final answer delivered
- [ ] Board updated after every state change
- [ ] Subagents one-task-one, wave-launched, results consolidated
- [ ] Agent-Reach health-checked before each platform-specific call
- [ ] Sources dated and type-categorized per evidence hierarchy
- [ ] Uncertainty surfaced explicitly (confidence per claim)
- [ ] Conflicts surfaced honestly (no false consensus)
- [ ] Cheapest viable tools used throughout
- [ ] If incomplete: continuation plan created, board saved
