# GStack Skill Adaptation for Hermes WebUI

## Problem

GStack skills (plan-ceo-review, plan-eng-review, plan-design-review, cso,
health, etc.) are designed for Claude Code with gstack CLI binaries installed.
In Hermes WebUI, these binaries don't exist, so the preamble scripts fail.

## Solution: Extract Methodology, Skip Infrastructure

The gstack skills are large SKILL.md files that contain:
1. **Preamble scripts** — CLI binary checks, telemetry, session tracking (skip these)
2. **Persona/methodology frameworks** — the actual review logic (USE THESE)
3. **AskUserQuestion formats** — decision briefs (adapt to clarify tool)
4. **Telemetry/analytics** — usage tracking (skip these)

### Steps to Adapt

1. **Load the skill** via `skill_view(name='gstack/<skill-name>')`
   - If ambiguous, use full path from the matches list
   - Common names: `gstack/plan-ceo-review`, `gstack/plan-eng-review`,
     `gstack/plan-design-review`, `gstack/cso`, `gstack/health`,
     `gstack/devex-review`

2. **Read the content** — the SKILL.md is large (70-90KB). Look for:
   - "## When to invoke this skill" — confirms purpose
   - "## Plan Review Mode" or the actual methodology section
   - Review checklists, scoring rubrics, output formats
   - Cognitive patterns (in plan-eng-review: "How Great Eng Managers Think")

3. **Extract the useful parts:**
   - Persona checklists and review dimensions
   - Scoring rubrics (0-10 scales, severity levels)
   - Output format templates
   - Pitfall lists
   - Skip: preamble bash scripts, telemetry, AskUserQuestion format specs,
     artifact sync, context recovery

4. **Apply directly** without CLI infrastructure:
   - Read project files manually (search_files, read_file)
   - Use delegate_task for parallel reads on large projects
   - Synthesize findings across personas
   - Produce consolidated report

### Skill Name Mapping

| GStack Skill | What It Reviews | Key Output |
|-------------|----------------|------------|
| `plan-ceo-review` | Product strategy, scope, ambition | 4 scope modes, product viability |
| `plan-eng-review` | Architecture, data flow, tests, perf | 4-section review (Arch/Code/Tests/Perf) |
| `plan-design-review` | UX design dimensions | 0-10 scores per design dimension |
| `cso` | Security (STRIDE, OWASP) | Threat model + findings |
| `health` | Code quality metrics | Composite 0-10 score + dashboard |
| `devex-review` | Developer experience | DX scorecard with evidence |

### Common Failure Modes

- **Skill name collision**: gstack skills exist in multiple directories
  (.agents, .cursor, .factory, .gbrain, .hermes, .kiro, .openclaw, .opencode,
  .slate, plus root). Always use the root `gstack/` prefix.
- **Content too large**: Some skills are 80-90KB. Use offset/limit on read_file
  to read sections, or rely on the preview in skill_view output.
- **Asking questions the skill expects**: Skills use AskUserQuestion for
  interactive decisions. In Hermes WebUI, use the `clarify` tool instead, or
  make reasonable default choices and note them in the report.
