---
name: research-manager
description: >-
  Top-level research orchestrator. Use BEFORE deep-research or web-research on ANY
  research request. Decides the best research mode, budget, execution shape, and
  quality bar, then delegates to the appropriate handler. Does NOT duplicate
  deep-research — it plans and gates, deep-research executes. Loads first on any
  research-adjacent request. Triggers: "research", "investigate", "compare",
  "evaluate", "deep dive", "analyze", "look into", "find out", "should we",
  "what's the best", "how does X compare", "audit", "review", "landscape".
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [research, orchestrator, planning, budget, mode-selection, critic, gating]
    related_skills: [deep-research, web-research, plan, agent-reach, todo]
---

# Research Manager — Top-Level Orchestrator

## Overview

This is the **first skill loaded** on any research-type request. It does NOT execute
research — it decides what kind of research is needed, whether it is worth doing,
how to shape the work, and which downstream skill should handle execution.

**Role in the skill stack:**

```
User request
  └─ research-manager (you are here)
       ├─ Shallow / Quick  → web-research or direct tools
       ├─ Standard         → direct execution or light delegation
       ├─ Deep / Audit     → deep-research (Kanban + waves + subagents)
       ├─ Architecture     → deep-research (architecture mode)
       ├─ Market / Comp    → deep-research (comparative mode)
       └─ Implementation   → plan skill + deep-research
```

**Key principle:** Prefer the cheapest sufficient path. Do not launch deep-research
for a simple lookup. Do not answer shallowly when the request needs evidence.
The planner is the first and most important decision gate.

**Priority hierarchy (inherited from stack):**
Accuracy > Evidence quality > Cross-checking > Coverage > Speed > Cost

---

## When to Use

**ALWAYS LOAD FIRST** when the user says anything research-adjacent. Research requests can come in **any language** (English, Persian, Arabic, Chinese, etc.) — pattern-match for *research intent*, not just English keywords. Triggers include but are not limited to:

- **English:** "Research X" / "Investigate Y" / "Look into Z" / "Compare A and B" / "Should we use X?" / "What's the best way to implement Y?" / "Audit this repo" / "Review the architecture" / "Market landscape" / "Competitive analysis" / "Implementation plan" / "Find out what people are saying" / "Verify this claim" / "Deep dive on Y"
- **Persian / فارسی:** «راجب X تحقیق کن» / «بررسی کن Y رو» / «ببین چه سرویسی اضافه شده» / «تحقیق می‌کنی ببینی چطوری» / هر درخواستی که حس و حال پژوهش/بررسی داشته باشه
- **Any language:** requests containing research, investigation, comparison, analysis, audit, review, landscape, evaluation, verification, exploration, or «تحقیق», «بررسی», «مقایسه», «ببین چطور» and similar intent signals
- Any request that mentions ≥1 platform (GitHub, Twitter, Reddit, etc.)

**Do NOT use** (let a downstream skill handle):
- Already-executing research (deep-research has the board open)
- A follow-up question about already-delivered research (the critic handles that)
- A pure code-generation task with no research component

---

## Core Architecture

The skill has 8 layers, each with a distinct responsibility:

| Layer | Responsibility | Output |
|-------|---------------|--------|
| 1. Intake & Complexity | Parse the request, classify depth | Complexity rating (Low/Medium/High) |
| 2. Budget & Risk | Estimate cost, time, rate-limit exposure | Budget estimate, risk flag |
| 3. Mode Selection | Pick the right research mode | Selected mode + justification |
| 4. Wave Planning | Group subquestions into safe waves | Wave breakdown |
| 5. Duplicate Detection | Check for overlap between planned agents | Deduped task list |
| 6. Execution Oversight | Monitor progress, adapt, stop early | Status updates |
| 7. Post-Research Critic | Break the answer before finalising | Critic findings or all-clear |
| 8. Final Orchestration | Synthesize or hand off | Final answer or handoff note |

**Rule:** Never skip layers 1–3. Layers 4–8 run only as needed based on mode.
Layers 7 (Critic) is **never** skipped for Medium/High complexity.

---

## 1) Intake & Complexity Assessment

Parse the user's request into a structured understanding:

**Questions the intake must answer:**
1. What is the **core question**? (one sentence)
2. How many **distinct subquestions** does it contain?
3. How many **platforms or source types** are relevant?
4. Does the answer require **cross-checking** (≥2 sources per claim)?
5. Is the topic **time-sensitive** (likely to have changed recently)?
6. Does the user need a **decision or recommendation**, or just facts?
7. Is the request **ambiguous**? (If yes, state the smallest safe interpretation.)

**Complexity classification:**

| Complexity | Criteria | Example |
|-----------|----------|---------|
| **Low** | 1 subquestion, 1 source type, factual, no cross-checking needed | "What's the latest version of Python?" — single look-up |
| **Medium** | 2–3 subquestions, 1–2 source types, some comparison or explanation needed | "Compare Python 3.12 vs 3.13 performance changes" |
| **High** | ≥3 subquestions, ≥2 platforms/source types, cross-checking essential, time-sensitive, needs a recommendation | "Best vector database for production semantic search at scale" |

**Rule:** If complexity is **Low**, do NOT use deep-research. Use web-research or
direct tools. If complexity is **Medium or High**, proceed with full planning.

**Completion criterion:** Complexity classified. Decision made on whether to proceed.

---

## 2) Budget & Risk Estimation

Before committing to execution, estimate the cost and risk:

**Estimates to produce:**
- **Expected token cost** (Low < 5K, Medium < 20K, High < 100K, X-High > 100K)
- **Expected API requests** (tools, searches, reads)
- **Expected runtime** (< 1 min, < 5 min, < 15 min, > 15 min)
- **Rate-limit risk** (None / Low / Medium / High) — based on which backends would be hit
- **Number of subagents needed** (0, 1–2, 3–4, 5+)
- **Number of sources likely** (< 3, 3–10, 10–30, 30+)

**Risk rules:**

| Condition | Action |
|-----------|--------|
| Rate-limit risk is High | Reduce scope, spread across more waves, delay expensive lanes |
| Runtime > 15 min | Split into continuation plan, do not force one session |
| Token cost is X-High | Reduce scope, prefer cheaper tools, ask user for confirmation |
| ≥4 subagents needed | Use wave scheduling (max 4 per wave across all tools) |
| Any backend has auth-warn status | Flag as credential gap, do not proceed on that lane without asking |

**Risk threshold:** If the combined risk score is high (multiple risks flagged),
either reduce scope automatically or, if scope reduction is not possible,
state the risk clearly and ask for confirmation.

**Completion criterion:** Budget estimate produced. Risk flagged if applicable.
Scope reduced if possible. Proceed or ask.

---

## 3) Mode Selection

Select one of 8 research modes:

| Mode | When | How to execute | Max cost |
|------|------|----------------|----------|
| **Quick** | Low complexity, single fact, no cross-check | Direct tool call or web-research | Low |
| **Standard** | Medium complexity, comparison or explanation | Direct tools + light delegation | Medium |
| **Deep** | High complexity, multi-angle, needs cross-check | Hand off to deep-research | High |
| **Code Audit** | Repo/tool/library evaluation | Hand off to deep-research (comparison mode) | Medium-High |
| **Architecture Review** | System design, tradeoffs, orchestration | Hand off to deep-research | Medium-High |
| **Market Intelligence** | Trends, ecosystem, community, adoption | Hand off to deep-research | Medium-High |
| **Competitive Analysis** | Direct comparison across tools/products | Hand off to deep-research (comparison mode) | Medium-High |
| **Implementation Planning** | Practical steps, integration, rollout | Hand off to plan skill + deep-research | Medium |

**Mode selection logic:**

```
IF complexity == Low                          → Quick
ELIF complexity == Medium AND single domain   → Standard
ELIF user asks for "compare" / "vs"           → Competitive Analysis
ELIF user asks for "audit" / "review code"    → Code Audit
ELIF user asks for "architecture"             → Architecture Review
ELIF user asks for "market" / "landscape"     → Market Intelligence
ELIF user asks for "implement" / "plan"       → Implementation Planning
ELSE                                           → Deep (default for High complexity)
```

**Rule:** Explicitly state which mode was selected and the one-line justification.

**Completion criterion:** Mode selected. Execution path determined.

---

## 4) Wave Planning

If the mode requires delegation or deep-research (i.e., not Quick/Standard),
plan the waves before execution:

**Wave structure (always 4 waves max):**

```
Wave 1 — Discovery / Cheap & High-Signal
  - Search for candidate sources
  - Read summaries, abstracts, READMEs, landing pages
  - Cheap tools only (Exa, Jina Reader, gh search)
  - Goal: find the best sources, do NOT deep-read yet

Wave 2 — Validation / Deeper Extraction
  - Read full docs, source code, release notes
  - Extract specific facts with dates and versions
  - Cross-check the strongest claims from Wave 1
  - Goal: validate and deepen

Wave 3 — Contradiction Checks & Edge Cases
  - Resolve disagreements between sources
  - Check edge cases, failure modes, costs
  - Read anything missed in Waves 1–2
  - Goal: fill remaining gaps

Wave 4 — Final Missing Evidence (optional)
  - Only if the question is still not fully answered
  - Narrow, targeted search
  - Goal: one last pass before synthesis
```

**Adaptive rule:** If Wave 1 already answers the question with high confidence,
cancel Waves 2–4. Do not force unnecessary work.

**Backend affinity rule:** If two tasks in the same wave hit the same backend
(e.g. both call `gh search`), either stagger them by ≥2 seconds or move one
to the next wave.

**Completion criterion:** Wave plan written. Early-stop condition stated.

---

## 5) Duplicate Detection

Before launching any subagents, detect overlap:

**Questions to ask:**
1. Are two or more subagents planning to search the same source type?
2. Are two or more subagents planning to answer the same subquestion?
3. Are any planned subagents redundant with existing task cards?
4. Are any planned subagents redundant with cached session results?

**If overlap is detected:**
- Merge overlapping tasks into one
- Remove redundant tasks
- Reassign the merged task to a distinct evidence lane
- Narrow the scope of each remaining task

**Unique evidence lanes** (each subagent should map to exactly one):

| Lane | What it covers |
|------|----------------|
| Official docs | API reference, user guide, getting started, official website |
| Source code | Repo structure, implementation, key files, dependencies |
| Releases / changelog | Version history, breaking changes, migration guides |
| Issues / PRs | Bug reports, feature requests, discussion threads |
| Benchmarks | Performance comparisons, load tests, throughput |
| Community feedback | Forum posts, Stack Overflow, social media sentiment |
| Implementation constraints | Dependencies, platform support, config requirements |
| Usage friction | Setup time, learning curve, known footguns |

**Rule:** Do not launch duplicate subagents for the same lane. Each subagent
must have a unique purpose and a unique target.

**Completion criterion:** All subagents checked for overlap. Merged or eliminated
as needed. No two subagents doing the same work.

---

## 6) Execution Oversight

During execution (whether this skill runs it directly or monitors deep-research):

**Oversight rules:**
1. **Track wave progress** — which wave is active, which tasks are done
2. **Check early-stop condition** — after each wave, ask: is the question answered with sufficient confidence? If yes, stop.
3. **Monitor rate limits** — if a backend slows down, pause that lane, continue others
4. **Adapt scope** — if Wave 1 finds unexpected complexity (e.g. 50 sources instead of 5), adjust the plan. If Wave 1 finds the topic is simpler than expected (e.g. only 1 credible source), reduce Waves 2–4
5. **Preserve partial results** — save card results as they complete, never lose work

**Early stop decision tree:**

```
After Wave 1:
  IF question answered with High confidence AND ≥2 sources agree
    → Stop. Go to Synthesis.
  ELIF question answered with Medium confidence
    → Continue to Wave 2 for validation.
  ELSE
    → Continue to Wave 2.

After Wave 2:
  IF question answered with High confidence AND contradictions resolved
    → Stop. Go to Synthesis.
  ELSE
    → Continue to Wave 3.

After Wave 3:
  IF all subquestions have at least Medium confidence
    → Stop. Synthesis.
  ELSE
    → Wave 4 for remaining gaps.
```

**Completion criterion:** Execution either completes normally, stops early via
adaptive rule, or pauses for continuation.

---

## 7) Post-Research Critic

After research is gathered but BEFORE the final answer is produced, run an
independent critic pass. The critic is never skipped for Medium+ complexity.

**Critic questions (answer all):**

1. **What did we miss?** — Is there a source type, platform, or viewpoint we didn't consult?
2. **What evidence is weak?** — Which claims have only 1 source? Which sources are low-authority?
3. **What assumptions remain untested?** — What did we take for granted that might be wrong?
4. **What would invalidate the conclusion?** — If one key source is wrong, does the whole conclusion collapse?
5. **Where could another researcher disagree?** — What is the strongest counterargument?
6. **What would we verify if we had more time?** — What is the highest-value unanswered question?
7. **Are sources fresh enough?** — Could any claim have changed since the most recent source was published?

**Critic severity:**

| Severity | Action |
|----------|--------|
| **Minor** (1–2 weak claims, easy to fix) | Note them in the final answer as low-confidence areas |
| **Moderate** (3+ weak claims, or 1 uncited central claim) | Reopen planning: add a targeted validation wave, re-check sources |
| **Critical** (central claim unsupported, or found a contradiction we missed) | Stop synthesis. Reopen research. Add a full validation wave. Do not produce a final answer until resolved. |

**Completion criterion:** Critic completed. If Minor: proceed. If Moderate: add
a validation wave first. If Critical: reopen research.

---

## 8) Final Orchestration & Handoff

Based on the mode selected in Layer 3, execute the appropriate handoff:

### Quick Mode (Low complexity)
Execute directly with the cheapest tool:
- 1 tool call (Jina Reader, web_search, or terminal command)
- No delegation, no Kanban, no waves
- Return the answer directly

### Standard Mode (Medium complexity)
Execute with lightweight direct tools:
- 2–4 tool calls, possibly sequential
- Light delegation if the question has 2 independent parts
- No Kanban board (or minimal markdown-only)
- Return structured answer

### Deep / Code Audit / Architecture / Market / Competitive / Implementation (High complexity)
Hand off to deep-research:
- Pass the full structured brief (from Layer 1)
- Pass the budget estimate (from Layer 2)
- Pass the wave plan (from Layer 4)
- Pass the deduped task list (from Layer 5)
- State clearly: "Handing off to deep-research for execution."

**Handoff template:**

```
## Research Manager Handoff to deep-research

### Brief
Core question: <from Layer 1>
Subquestions: <from Layer 1>
Complexity: <from Layer 1>
Mode: <from Layer 3>

### Budget
Token cost: <estimate>
API requests: <estimate>
Runtime: <estimate>
Rate-limit risk: <estimate>
Subagents needed: <estimate>

### Wave Plan
<from Layer 4>

### Deduped Task List
<from Layer 5>

### Credential Gaps
<if any>

### Notes
<special instructions, platform warnings, time sensitivity>
```

---

## 9) Output Format

When this skill produces the final answer (for Quick/Standard/Handoff), the
response includes these sections:

### Intake Summary
```
Core question: <one sentence>
Subquestions: <N>
Complexity: Low | Medium | High
```

### Budget / Risk Estimate
```
Token cost: <estimate>
Runtime: <estimate>
Rate-limit risk: None | Low | Medium | High
Subagents needed: <N>
Sources expected: <N>
```

### Selected Mode
```
Mode: <Quick | Standard | Deep | Code Audit | Architecture Review | Market Intelligence | Competitive Analysis | Implementation Planning>
Justification: <one sentence>
```

### Execution Path
For Quick/Standard: "Executing directly."
For handoff modes: "Handing off to deep-research. See handoff section."

### Post-Research Critic
```
Weak evidence: <items>
Untested assumptions: <items>
Strongest counterargument: <text>
Would invalidate conclusion if: <text>
Critic severity: Minor | Moderate | Critical
Action taken: <proceed | added validation wave | reopened research>
```

### Final Recommendation
<the answer, or the handoff result>

### Confidence
High / Medium / Low, with reason.

### Next Step
What the user should do with the answer, or what the next research action will be.

---

## 10) Handoff Rules Summary

| Mode | Execute via | Kanban? | Subagents? | Waves? | Critic? |
|------|-------------|---------|------------|--------|---------|
| Quick | Direct tools | No | No | No | No |
| Standard | Direct + light delegation | No | 1–2 | No | Optional |
| Deep | deep-research | Yes | Yes | 4 max | Yes |
| Code Audit | deep-research | Yes | Yes | 4 max | Yes |
| Architecture Review | deep-research | Yes | Yes | 4 max | Yes |
| Market Intelligence | deep-research | Yes | Yes | 4 max | Yes |
| Competitive Analysis | deep-research | Yes | Yes | 4 max | Yes |
| Implementation Planning | plan + deep-research | Yes | Yes | 4 max | Yes |

---

## 11) Quality Rules

1. **Cheapest sufficient path** — always use the minimum tooling needed. A curl
   call beats a subagent. A subagent beats a full Kanban board.
2. **Avoid unnecessary subagents** — do not create 4 subagents when 1 direct call
   covers the question.
3. **Avoid unnecessary waves** — stop after Wave 1 if the question is answered.
4. **Avoid duplicate searching** — check for overlap before launching (Layer 5).
5. **Avoid over-researching simple questions** — Low complexity → Quick mode.
   Do not over-engineer.
6. **Escalate only when justified** — never call deep-research for a single fact.
7. **Honest about uncertainty** — if the evidence is weak, say so. Do not pad
   the answer with low-quality sources.
8. **Evidence quality over volume** — 2 high-authority sources beat 20 blog posts.
9. **Never skip the critic for Medium+** — the critic is what separates careful
   research from sloppy search.

---

## Delegation Setup

For configuring Hermes delegation (sub-agent models, concurrency, spawn depth),
see [references/delegation-setup.md](references/delegation-setup.md).

## 12) Relationship to Other Skills

| Skill | Relationship |
|-------|-------------|
| **deep-research** | Downstream executor for all Deep+ modes. research-manager plans and gates; deep-research executes. |
| **web-research** | Downstream for Quick mode. Also used as a fallback tool within any mode when a single web page needs reading. |
| **plan** | Co-executor for Implementation Planning mode. |
| **agent-reach** | Platform-health backend. Called during Risk Estimation (Layer 2) to check status of any platform the request mentions. |
| **todo** | Optional persistence layer for task tracking during Standard mode. |

---

## Common Pitfalls

1. **Skipping the planner.** The most common failure mode. Always classify complexity first. Do not jump to execution.

2. **Calling deep-research for a single fact.** Low complexity → Quick mode → web-research or direct curl. No Kanban, no waves.

3. **Skipping the critic.** The critic prevents low-quality conclusions. Never skip it for Medium+ complexity.

4. **Overlapping subagents.** Two subagents searching the same source type for the same question is wasted work. Always run duplicate detection (Layer 5).

5. **Forcing all waves.** If Wave 1 answers the question, stop. Do not run Waves 2–4 just because they exist in the plan.

6. **Ignoring rate-limit risks.** If 3 tasks hit GitHub in the same wave, they will throttle. Stagger them or move to different waves.

7. **Handing off without a brief.** When handing off to deep-research, always pass the structured brief, budget, and wave plan. Do not dump raw user input.

8. **Assuming credentials exist.** Check agent-reach doctor for platform health before planning platform-specific tasks.

9. **Pretending critic didn't find anything.** If the critic finds weak evidence, address it. Do not suppress critic findings.

10. **Running everything in one burst.** For High complexity, waves exist for a reason — they prevent rate-limit failures and let early results adapt later work.

11. **Subagent terminal approval deadlock.** When delegating tasks that use terminal CLIs (`rdt`, `twitter`, `gh`, etc.), subagents block on `pending_approval` with no user to approve. Verify `approvals.mode: off` is set in config.yaml before launching any delegation that uses terminal tools. See agent-reach skill for full diagnosis and fix.

---

## Verification Checklist

- [ ] Layer 1: Complexity classified (Low/Medium/High). Decision made on whether to proceed.
- [ ] Layer 2: Budget estimated. Risk flagged. Scope reduced if needed.
- [ ] Layer 3: Mode selected and justified. Execution path determined.
- [ ] Layer 4: Waves planned (if applicable). Early-stop condition stated.
- [ ] Layer 5: Duplicate detection run. Subagents merged or eliminated.
- [ ] Layer 6: Execution oversight active (if running) or handed off cleanly.
- [ ] Layer 7: Critic run (if Medium+). Severity assessed. Action taken.
- [ ] Layer 8: Final orchestration complete. Answer or handoff delivered.
- [ ] Handoff (if applicable): structured brief passed to deep-research.
- [ ] Cheapest sufficient path used throughout.
- [ ] Rate-limit risks considered per backend.
- [ ] Uncertainty surfaced. Confidence stated.
