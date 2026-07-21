---
name: github-profile-readme
description: 'Create or update a professional GitHub Profile README — personal branding grounded in real repositories, with stats cards, contribution snake, and dark developer aesthetic.'
version: 1.3.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [github, profile, personal-branding, readme]
    related_skills: [project-publisher]
---

# GitHub Profile README

Create or update a developer's personal GitHub profile README (the special `{username}/{username}` repo). This is distinct from project/documentation READMEs — it's a professional portfolio page targeting CTOs and technical recruiters.

## When to Use

- User says "create my GitHub profile README", "update my profile", "make my GitHub look professional"
- User provides their GitHub username and wants a profile README
- User shares a screenshot of their current profile and wants improvements
- User asks for a "personal branding" or "portfolio" GitHub page

## Workflow

```
1. INVENTORY   → Fetch all repos via GH API, analyze descriptions, languages, topics, starred projects
2. READ        → Check each significant repo's README.md to understand architecture and tech
3. GROUND      → Map skills/claims to actual repos — reject anything unsupported
4. WRITE       → Craft the README with honest positioning
5. SNAKE       → Add GitHub Actions workflow for contribution snake animation
6. DEPLOY      → Push to {username}/{username} repo
7. VERIFY      → Confirm it renders on the profile
```

## Step 1: Inventory the User's Repos

Fetch ALL public repos (not just the first page — use pagination):

```python
# Use gh CLI for authenticated access
gh repo list {username} --json name,description,primaryLanguage,repositoryTopics,stargazerCount,forkCount,updatedAt --limit 50
```

Or via the API directly if you need README contents too:

```python
import json, urllib.request, base64

url = "https://api.github.com/users/{username}/repos?per_page=50&sort=updated"
req = urllib.request.Request(url, headers={"User-Agent": "Hermes"})
resp = urllib.request.urlopen(req)
repos = json.loads(resp.read())
```

For each repo, capture: name, description, language, topics, stars, forks, updated date. Then read each README:

```python
readme_url = f"https://raw.githubusercontent.com/{username}/{repo_name}/main/README.md"
# If 404, try master branch
```

### What to analyze in each README
- Architecture and tech stack actually used
- Whether the README is well-written or bare
- Key features the repo actually implements
- Any claims about what the service does (to reference in your profile)

## Step 2: Ground Every Claim in Real Repos

**CRITICAL RULE:** Never invent experience, skills, projects, or achievements. Every claim in the profile README must be supported by either:
- A public repository with matching content, OR
- Information explicitly provided by the user outside the repos

### Role Positioning Rules (MANDATORY — user WILL correct you)

**Use the user's EXACT role title — do not embellish, rephrase, upgrade, or "interpret" it.**
- If user says "AI Automation Engineer" → write "AI Automation Engineer"
- NOT "AI Engineer", "Automation Engineer", "AI Agent Engineer", "Senior Automation Engineer"

**What NEVER to position the user as:**
- AI researcher
- AI agent developer / framework creator
- Creator of AI systems (if they build *with* AI tools)
- Hermes developer or creator (if they just use it)
- Machine Learning Engineer (unless they explicitly say so)
- AI model developer / trainer
- Autonomous agent framework author

### Correct phrasing table

| They use X but didn't build it | Say | DANGER PHRASES TO AVOID |
|---|---|---|
| Use Hermes Agent | "Experience working with Hermes Agent and AI agent workflows" | "Hermes developer", "Hermes creator", "Agent framework development" |
| Use n8n heavily | "n8n — workflow design, webhooks, and API orchestration" | "n8n developer", "n8n architect", "n8n expert" |
| Use LLM APIs (OpenAI, Gemini, Groq) | "LLM integrations", "AI-powered tools and assistants" | "AI research", "AI system creation", "autonomous agent development" |
| Use AI Agent workflows | "AI agent workflows", "automation systems using AI agents" | "Built agent architecture", "Created AI Agent framework" |
| Have Python automation repos | "Python — backend automation, scripting" | "Python expert", "Python architect" |
| Built a Telegram bot | "Telegram Bot development" | Overstating the bot's scope |
| Use PostgreSQL | "PostgreSQL — data persistence and SQL" | "Database architect", "Data engineer" |
| Use Docker | "Docker" (just the tool name) | "DevOps engineer", "Infrastructure architect" |

**GOLDEN RULE FOR PHRASING:**
- "Built" = they wrote the code themselves for repos they created
- "Experience working with" / "Experience using" = they used an existing tool/framework
- If in doubt, use "Experience with" — never assume ownership

### Tone: Engineer's Self-Description, Not Marketer's Pitch

**The user WILL correct you if the tone is wrong.**

**✅ Engineer tone (safe, correct):**
```
I'm an AI Automation Engineer. I build automation workflows,
Telegram and Bale bots, API integrations, data pipelines,
and AI-powered tools — mostly with Python and n8n.
```

**❌ Marketing tone (user will reject):**
```
I build systems that reason, act, and adapt — AI agents with
MCP tools, semantic search over workflow knowledge bases...
```

| Bad phrase | Why it fails | Replace with |
|---|---|---|
| "Systems that reason, act, and adapt" | Marketing copy | "n8n workflows with MCP tools and RAG" |
| "agentic architectures" | Empty buzzword | "AI automation workflows" |
| "intelligent" as catch-all modifier | Vague, overused | Use specific tech names instead |
| "autonomous systems" | Sounds like self-driving tech | "automation systems" |
| "I love [technology]" / "passionate about" | Filler, empty | Drop it — show the work |
| "Transforming how X works" | Extreme exaggeration | "Building X tools" or "Developing Y" |

## Step 3: README Structure

Use this structure for a professional CTO/recruiter-facing profile:

### 3a. Hero Section (Animated Capsule Header + Typing SVG)
Users expect a VISUALLY STUNNING hero — not just text. Use a multi-layer hero with animated elements.

**Layer 1 — Capsule Render animated header** (gradient wave with name + role):
```html
<div align="center">
<a href="https://github.com/{username}">
  <img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:0D1117,50:00D9FF,100:0D1117&height=200&section=header&text={FullName}&fontSize=50&fontColor=ffffff&animation=fadeIn&fontAlignY=35&desc={Role}&descSize=18&descAlignY=55&descAlign=50" alt="header" />
</a>
```
- `type`: `waving`, `venom`, `rect`, `slice`, `shell`, `wave` — `waving` is the most popular
- `color`: gradient stops as `0:hex,50:hex,100:hex` — use the dark theme palette
- `animation=fadeIn` for smooth entry

**Layer 2 — Typing SVG** (animated typing effect):
```html
<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=24&duration=3000&pause=1000&color=00D9FF&center=true&vCenter=true&multiline=true&repeat=true&width=600&height=100&lines=%F0%9F%96%A5+{Line1};%F0%9F%94%84+{Line2};%F0%9F%9A%80+{Line3}" alt="typing animation" />
```
- `multiline=true&repeat=true` for continuous cycling
- Use emoji prefixes (📋 🔄 🚀) to make each line distinctive
- `height` must accommodate all lines (30px per line + padding)

**Layer 3 — Badge row** (for-the-badge style, NOT flat):
```html
<a href="https://github.com/{username}?tab=followers">
  <img src="https://img.shields.io/github/followers/{username}?label=Followers&style=for-the-badge&logo=github&logoColor=white&color=00D9FF" alt="followers" />
</a>
```
- Use `style=for-the-badge` for large, bold, professional badges (NOT `flat` or `flat-square` for hero badges)
- Color-code: followers=cyan(00D9FF), stars=gold(F5A623), email=red(D14836), portfolio=green(238636)
- Wrap in `<a>` tags linking to the relevant page

**Layer 4 — Profile views counter**:
```html
<img src="https://komarev.com/ghpvc/?username={username}&label=Profile%20Views&color=00D9FF&style=for-the-badge" alt="profile views" />
```

**Layer 5 — Animated footer** (capsule-render waving goodbye):
```html
<a href="https://github.com/{username}">
  <img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:0D1117,50:00D9FF,100:0D1117&height=80&section=footer&text=Thanks%20for%20visiting!&fontSize=16&fontColor=ffffff&animation=fadeIn" alt="footer" />
</a>
```

**Full hero structure** (all layers wrapped in `<div align="center">`):
```
<div align="center">
  [capsule header]
  [typing SVG]
  [badge row]
  [profile views]
</div>
[divider SVG]
```

### 3b. About Me (2-3 sentences)

Concise professional intro. No "I love coding", no filler. Lead with the EXACT role the user specified. Mention the core tool categories. Emphasize what they build day-to-day.

**Positioning rule:** Use the EXACT role phrasing the user provided — do not embellish, rephrase, upgrade, or interpret it. If they say "AI Automation Engineer", those exact words go in the README.

#### Tone: Engineer's Self-Description

**Write like an engineer describing their work to another engineer.** Be specific and concrete:

**✅ Correct — engineer tone:**
```
I'm an AI Automation Engineer. I build automation workflows,
Telegram and Bale bots, API integrations, data pipelines,
and AI-powered tools — mostly with Python and n8n.
```

**❌ Wrong — marketing tone that WILL be rejected:**
```
I build systems that reason, act, and adapt — AI agents with
MCP tools, semantic search over workflow knowledge bases...
```

**DO NOT position the user as:**
- AI researcher
- AI agent developer / framework creator
- Creator of AI systems (if they build *with* them)
- Hermes developer or creator (if they just use it)
- Machine Learning Engineer
- AI model developer

**Correct positioning patterns:**

| What they do | Say in About Me | Don't say |
|---|---|---|
| Build automation with n8n/LLMs | "I build automation systems using n8n, Python, and LLMs" | "AI researcher", "agentic architectures" |
| Use AI agent frameworks | "Experience working with Hermes Agent and AI agent workflows" | "Hermes developer/creator", "Built agent architecture" |
| Integrate LLMs into apps | "LLM integrations and AI-powered tools" | "AI research", "autonomous agent development" |
| Write Python scripts/bots | "Python — backend automation, Telegram/Bale bots" | "Python expert", "Python architect" |

**Bad phrases to avoid everywhere in the README:**
- "Systems that reason, act, and adapt" — marketing copy
- "agentic architectures" — empty buzzword
- "intelligent" as catch-all modifier — vague
- "autonomous systems" — sounds like self-driving tech
- "I love [tech]" / "passionate about" — filler
- "Transforming how X works" — extreme exaggeration

### 3c. What I Build (optional, before Featured Projects)
A short section with clear action statements. Two layout options:

**Option A — Plain text** (minimal, clean):
```
Workflow automation systems that connect services, process data, and handle business logic.
Telegram and Bale bots for automation, AI assistance, and data collection.
API integrations between services, with error handling and observability.
Data extraction and scraping pipelines for e-commerce and market research.
```

**Option B — 2×2 Card table** (visually richer, RECOMMENDED for upgrade requests):
```html
<table align="center">
  <tr>
    <td align="center" width="48%">
      <img src="https://img.shields.io/badge/🔄-{Label}-{color}?style=flat-square&labelColor=0D1117" alt="..." /><br/><br/>
      <p><b>Title</b><br/>Description line 1<br/>Description line 2</p>
    </td>
    <td width="4%"><br/></td>
    <td align="center" width="48%">
      <img src="https://img.shields.io/badge/🤖-{Label}-{color}?style=flat-square&labelColor=0D1117" alt="..." /><br/><br/>
      <p><b>Title</b><br/>Description line 1<br/>Description line 2</p>
    </td>
  </tr>
  <!-- second row same pattern -->
</table>
```
- Use `style=flat-square` with `labelColor=0D1117` for card header badges
- Each cell: badge → `<br/><br/>` → `<p><b>Title</b><br/>Description</p>`
- 4 cards (2×2) or 3 cards (1×3) — keep to even numbers for symmetry

### 3d. Current Focus
Bullet list of what the user is actively working on. Prefer bullets that map to actual repo activity.

### 3e. Featured Projects (THE MOST IMPORTANT SECTION)
Pick the **strongest 2-4 repos** based on:
- README quality (well-documented repos are better picks)
- Technical depth
- Relevance to the user's stated role

**Use engineering case-study format** — not a flat feature list. Each project should follow:

1. **Problem** — What need or gap existed
2. **What I built** — The solution, one paragraph
3. **Technical details** — Bullet list of concrete technical decisions, architectures, and challenges
4. **Tech** — Comma-separated or pipe-separated technology list
5. **Link to repo**

Format:
```
### Project Name

> **Problem:** [One sentence: what need or gap existed]

**Solution:** [One paragraph: the solution]

<details>
<summary><b>⚡ Technical Details</b></summary>

- Technical decision or challenge 1
- Technical decision or challenge 2
- ...

</details>

`technology1` · `technology2` · `technology3`

[<img src="https://img.shields.io/badge/📂_View_Repository-{bg}?style=for-the-badge&logo=github&logoColor=white" alt="repo" />](https://github.com/{user}/{repo})
```

Using `<details>/<summary>` keeps the page scannable — recruiters see the one-liner, engineers can expand for depth. The backtick-wrapped tech list and shield badge link look more polished than plain markdown links.
```

### 3f. Tech Stack Section
Two-layer approach: a structured table AND a row of colored shields.io badges.

**Layer 1 — Category table** (2-5 columns, depends on how many categories):
```html
<table align="center">
  <tr>
    <td align="center" width="18%"><b>Category</b><br/><br/><code>Tech1</code><br/><code>Tech2</code></td>
    <!-- more columns -->
  </tr>
</table>
```

**Layer 2 — Animated badge row** (for-the-badge style, with brand logos):
```html
<div align="center">
<img src="https://img.shields.io/badge/{name}-{color}?style=for-the-badge&logo={logo}&logoColor=white" alt="{name}" />
<!-- more badges -->
</div>
```
- Use official brand colors from shields.io
- `style=for-the-badge` for large, professional appearance
- Group: main tools first (n8n, Python, FastAPI, PostgreSQL, Docker), then secondary (Telegram, Linux, Git), then LLM providers (OpenAI, Gemini)

### 3g. GitHub Stats + Activity Graph + Trophies
Use a TABLE layout for stats (side-by-side on desktop, stacked on mobile). Add activity graph and trophies below.

**Stats table** (2 cards side by side + streak below):
```html
<table align="center">
  <tr>
    <td align="center">
      <a href="https://github.com/{user}">
        <img height="180em" src="https://github-readme-stats.vercel.app/api?username={user}&show_icons=true&theme=radical&hide_border=true&bg_color=0D1117&title_color=00D9FF&icon_color=00D9FF&text_color=c9d1d9&ring_color=00D9FF&include_all_commits=true&count_private=true" alt="stats" />
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/{user}">
        <img height="180em" src="https://github-readme-stats.vercel.app/api/top-langs/?username={user}&layout=compact&theme=radical&hide_border=true&bg_color=0D1117&title_color=00D9FF&text_color=c9d1d9&langs_count=8&ring_color=00D9FF" alt="languages" />
      </a>
    </td>
  </tr>
  <tr>
    <td align="center" colspan="2">
      <a href="https://github.com/{user}">
        <img src="https://github-readme-streak-stats.herokuapp.com/?user={user}&theme=radical&hide_border=true&background=0D1117&stroke=00D9FF&ring=00D9FF&fire=FF6B6B&currStreakLabel=00D9FF&sideLabels=c9d1d9" alt="streak" />
      </a>
    </td>
  </tr>
</table>
```

**Activity graph** (shows daily contribution pattern):
```html
<a href="https://github.com/{user}">
  <img src="https://github-readme-activity-graph.vercel.app/graph?username={user}&bg_color=0D1117&color=00D9FF&line=00D9FF&point=FFFFFF&area_color=00D9FF&area=true&hide_border=false&custom_title=GitHub%20Activity%20Graph" alt="activity graph" />
</a>
```

**Trophies** (earned achievement badges):
```html
<a href="https://github.com/ryo-ma/github-profile-trophy">
  <img src="https://github-profile-trophy.vercel.app/?username={user}&theme=radical&no-frame=true&no-bg=true&column=7&margin-w=10&row=1" alt="trophies" />
</a>
```

Use consistent dark theme colors (0D1117 background, 00D9FF accent, c9d1d9 text). Use `theme=radical` for stats/trophies — it matches the dark developer aesthetic best.

### 3h. Contribution Snake
Add a GitHub Actions workflow that auto-generates the snake animation daily.

Workflow file: `.github/workflows/snake.yml`

```yaml
name: Generate snake animation

on:
  schedule:
    - cron: "0 0 * * *"
  workflow_dispatch:

permissions:
  contents: write
  pages: write

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: Platane/snk@v3
        with:
          github_user_name: ${{ github.repository_owner }}
          outputs: |
            dist/github-contribution-grid-snake.svg
            dist/github-contribution-grid-snake-dark.svg?palette=github-dark
      - uses: crazy-max/ghaction-github-pages@v4
        with:
          target_branch: output
          build_dir: dist
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

In the README, include the snake image referencing `output` branch:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/{username}/{username}/output/github-contribution-grid-snake-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/{username}/{username}/output/github-contribution-grid-snake.svg">
  <img alt="GitHub contribution snake animation" src="https://raw.githubusercontent.com/{username}/{username}/output/github-contribution-grid-snake.svg">
</picture>
```

**Note:** The snake only appears after the Action runs at least once. Until then, the image link will 404. Tell the user they can trigger it manually from the Actions tab.

### 3i. Contact Section
GitHub profile link + email. Only include what the user explicitly provides or what's on their profile.

## Step 4: Pushing to the Profile Repo

The profile repo is special — it's `{username}/{username}` and is often empty initially.

```bash
# Clone (may be empty)
git clone https://github.com/{username}/{username}.git _profile_repo

# Set git identity BEFORE committing (fresh clones have no local identity)
cd _profile_repo
git config user.email "{user_email}"    # use the email from their GitHub profile or explicit input
git config user.name "{user_full_name}" # use the full name from their GitHub profile or explicit input

# Add README and workflow
mkdir -p .github/workflows
# Write README.md and .github/workflows/snake.yml

git add -A
git commit -m "Create professional GitHub profile README"
git push origin main
```

If the repo is empty (no default branch yet):
- `git clone` works with a warning "empty repository"
- You must create the initial commit and push to set the default branch
- It will create `main` branch automatically on first push

## Step 5: Verification

After push, verify:

```bash
# Check README content renders
gh repo view {username}/{username} --json description,url

# Optionally fetch the raw README to confirm
curl -s "https://raw.githubusercontent.com/{username}/{username}/main/README.md" | head -5
```

## Style Guide

| Element | Rule |
|---|---|
| **Tone** | Professional, direct, no filler. Written for CTOs/technical recruiters. Write like an engineer, not a marketer — be specific and concrete. |
| Audience | Senior technical people — skip beginner phrasing, "I love", "passionate about" |
| Language | English only unless user asks for bilingual |
| Aesthetic | Dark theme (0D1117 bg, 00D9FF accent, c9d1d9 text). Clean spacing |
| **Visual polish** | Animated capsule header, typing SVG, for-the-badge badges, table layouts for stats/projects. Users EXPECT visual richness — plain markdown looks amateur. |
| Emojis | Use sparingly and professionally (🚀, 🔭, 📦, 🛠️, 📊, 🐍, 📫). Avoid excessive emoji chains |
| Badges | `style=for-the-badge` in hero/stats, `style=flat-square` in card headers. shields.io format. Color-coded by category. GitHub follow + email badges in hero |
| Projects | Each project uses `<details>` for collapsible tech details, shield badge for repo link, backtick tech list |
| Table of Contents | Not needed for a single-page profile (unlike project READMEs) |
| **Section separators** | Use animated SVG dividers between major sections (e.g. Platane/dot horizontal SVG) |

## Pitfalls

1. **Never invent.** The #1 sin in profile READMEs is claiming skills/projects that don't exist in the repos. Every repo link, every technology mention must check out against actual code.
2. **Don't overstate tool relationships.** "Experience working with Hermes Agent" ≠ "Hermes Agent developer/creator". If they didn't build it, say "experience working with" or "using".
3. **Don't claim AI research or framework authorship.** If the user uses AI agent frameworks (n8n agents, Hermes Agent, LangChain, etc.) but didn't build them, do not phrase it as "AI agent architecture development" or "research into autonomous agents". Position: "Experience working with [tool] and AI agent workflows."
4. **Don't exaggerate scope.** If the user integrates AI into automation, say "AI-powered tools and assistants" not "AI systems". "Built" = they wrote the code themselves. "Used" / "Experience with" = they used an existing tool.
5. **Avoid agentic/autonomous/adaptive/marketing buzzwords.** Phrases like "systems that reason, act, and adapt" sound like marketing copy, not a portfolio. Use concrete descriptions ("n8n workflows with MCP tools and RAG capabilities"). The user WILL flag this.
6. **Empty repos look bad on the profile.** Check if the repo actually has content before featuring it. A repo with only a name and no commits is not a featured project.
7. **Snake action won't show immediately.** The 404 until first run is expected — tell the user to trigger it manually via Actions tab.
8. **Avoid generic GitHub stats APIs that require special tokens.** `github-readme-stats` and `github-readme-streak-stats` work without authentication.
9. **Don't fork the profile repo.** Clone it fresh. A profile repo is the user's identity repo — treating it like a forked project confuses things.
10. **Email privacy.** Only include the email the user explicitly provides. Don't scrape it from commits.
11. **Visitor counters: use `komarev.com`, not old services.** The old `visitor-badge.lunaace.dev` and similar services are unreliable. `komarev.com/ghpvc/` is the modern, maintained option — use `style=for-the-badge` and a matching accent color. Only add if the user asks or the profile feels incomplete without it.
12. **Featured projects must be the user's own repos.** Don't feature forks or contributions to someone else's project unless the user explicitly asks.
13. **Excessive emojis look unprofessional.** Use them sparingly (🚀 🔭 📦 🛠️ 📊 🐍 📫) — never emoji chains or decorative emoji lines. One or two per section max.
14. **"I love coding" and similar filler.** Never use. Every line should communicate a specific skill, technology, or achievement.
15. **Don't fudge the role title.** The user's EXACT stated job title goes in — "AI Automation Engineer", not "AI Engineer" or "Automation Engineer". Exact wording only.
16. **What I Build section is optional but often wanted.** If the user likes concrete case studies, add a "What I Build" section before Featured Projects with clear action statements (no emoji bullets). Each line: "what I build — context." Not emoji categories.
17. **Featured Projects must use engineering case-study format** (Problem / What I built / Technical details / Tech), not a flat feature list. The user will ask for this explicitly.
18. **When the user provides a detailed spec document, follow it exactly.** Don't add projects they didn't list, sections they didn't ask for, or descriptions beyond what they provided. If you find extra info on GitHub, ask before adding.
19. **GitHub CDN caching delays pushes from appearing immediately.** After `git push`, the raw URL (`raw.githubusercontent.com/.../main/README.md`) may still serve the old version for 5-30 minutes. Use the commit SHA URL (`raw.githubusercontent.com/.../{commit_sha}/README.md`) to verify the new content was actually pushed. The profile page itself usually updates within minutes.

## Related Skills

- `project-publisher` — for documenting and publishing codebase projects (different class — project docs, not personal profiles)
- `plan` — for writing implementation plans before execution

## References

- `references/github-stats-api-params.md` — params reference for stats cards
- `references/visual-elements-api.md` — capsule-render, activity graph, trophy, komarev, badge styles, brand colors
