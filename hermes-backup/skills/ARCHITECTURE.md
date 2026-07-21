# Skill Architecture: n8n-builder

## The Problem
The original n8n-builder SKILL.md was 109KB / 2,154 lines — 10x the recommended size. Models ignored buried rules and defaulted to "archive + SDK recreate" instead of "update_workflow + addNode". 40 traps + 40 rules in one file caused information overload.

## The Solution: One-Page SKILL + Targeted References

```
n8n-builder/
├── SKILL.md                           # 6KB — 5 rules, session flow, tool refs
├── references/
│   ├── update-workflow.md             # 12KB — decision tree + ALL addNode patterns
│   ├── node-sdk-patterns.md           # 10KB — SDK syntax for every node type
│   ├── trap-reference.md              # 6KB — all traps condensed
│   ├── expression-syntax.md           # 17KB — n8n expressions (unchanged)
│   ├── agents.md                      # 23KB — AI Agent nodes (unchanged)
│   └── telegram-bot-routing.md        # 12KB — routing patterns (unchanged)
```

## Key Design Decisions

1. **SKILL.md ≈ 6KB, English-only.** Forces reading. No narrative, just rules.
2. **RULE 0 loads update-workflow.md first.** Not optional. Model reads this before any code.
3. **update-workflow.md has complete addNode JSON.** Every node type with exact parameters. Model copy-pastes instead of guessing.
4. **trap-reference.md is reactive.** Read only on error, not upfront. This cut the always-loaded content from 109KB to 18KB (SKILL.md + update-workflow.md).
5. **node-sdk-patterns.md for NEW workflows only.** If WF exists, model never reads this.
6. **"User said 'از اول بساز'" is the ONLY archive trigger.** Not suggested by agent. Ever.

## The Behavioral Fix

Before: model reads 109KB → confused → chooses "SDK + archive" (path of least resistance)

After: model reads 6KB SKILL → RULE 0 says read update-workflow.md → sees "archive destroys everything" + exact addNode JSON → uses addNode correctly.

## All Files (34.8KB total)
- SKILL.md: 6KB
- references/update-workflow.md: 12KB
- references/node-sdk-patterns.md: 10KB
- references/trap-reference.md: 6KB
- (other refs: unchanged, ~60KB but only read when needed)
