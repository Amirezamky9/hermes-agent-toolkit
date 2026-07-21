# Installing Skills from skills.sh

Skills from [skills.sh](https://www.skills.sh) can enhance specific agent roles. The SkillDiscoverer automatically picks them up when they are installed with proper tags.

## Workflow

1. **Browse** skills.sh for a relevant skill (e.g. `vercel-react-best-practices`)
2. **Download** from the GitHub source repo (skills.sh is a registry, not a host):
   ```
   curl -sL "https://raw.githubusercontent.com/<org>/<repo>/main/skills/<name>/SKILL.md"
   ```
3. **Adapt frontmatter** to Hermes format:
   ```yaml
   ---
   name: <skill-name>
   description: <one-liner>
   version: 1.0.0
   metadata:
     hermes:
       tags: [frontend, react, ...]   # ← Crucial: tags drive SkillDiscoverer matching
       related_skills: [...]
   ---
   ```
4. **Install** to `~/.hermes/skills/<category>/<name>/SKILL.md`
5. **Update DEFAULT_SKILL_INDEX** in `core/skill_discoverer.py` so the engine knows about it even offline (add an entry with tags + domain matching the agent role keywords)

## Tag Strategy

Tags determine which agent role picks up the skill. The matching uses 3 factors:

| Factor | Weight | Example |
|--------|--------|---------|
| Tag overlap with role keywords | 3×/tag | FRONTEND_DEV keywords contain `frontend`, `react`, `ui`, `spa`, `web`, `mobile` |
| Keyword in description | 1×/match | Description mentioning "React" or "web" |
| Domain exact match | 2× | `domain: frontend` matched to FRONTEND_DEV |

So a frontend skill needs tags like: `frontend`, `react`, `web-app`, `spa`, `ui`, `mobile`.

## Known issue: offline index vs live discovery

The engine ships with a `DEFAULT_SKILL_INDEX` hardcoded in `skill_discoverer.py`. New skills must be added to this index AND physically installed in `~/.hermes/skills/`. The `_try_online_discovery()` method attempts to enrich via Hermes `skills_list()` but this is a best-effort path. Always update DEFAULT_SKILL_INDEX.
