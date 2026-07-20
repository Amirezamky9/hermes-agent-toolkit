# Technology / Framework Evaluation Methodology

Step-by-step pattern for evaluating competing frontend frameworks, libraries, or tools for a project. Gathered from real Telegram Mini App framework comparison session (July 2026).

## Step 1: Official SDK / Ecosystem Check

Determine which frameworks have official first-party support from the platform.

```bash
# Check monorepo for framework bindings
gh api repos/ORG/REPO/contents/packages --jq '.[].name' 2>/dev/null

# Check official README for supported frameworks
gh api repos/ORG/REPO/readme --jq '.content' 2>/dev/null | base64 -d | head -100
```

**Look for:** official template repos, framework-specific binding packages, framework mentions in README.

## Step 2: GitHub Community Adoption

```bash
# Search for projects using each framework
gh search repos "QUERY FRAMEWORK" --sort stars --limit 20 \
  --json name,owner,stargazersCount,language,description 2>/dev/null

# Get repo metadata for interesting projects
gh api repos/OWNER/REPO 2>/dev/null | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(f'Stars: {d[\"stargazers_count\"]}')
print(f'Lang: {d[\"language\"]}')
print(f'Topics: {d.get(\"topics\",[])}')
"
```

**Key metrics:** star count per project, language distribution across top N repos, whether official org provides templates per framework.

## Step 3: npm Package Stats

```bash
# Package info (version, description)
curl -s "https://registry.npmjs.org/PACKAGE_NAME" 2>/dev/null | python3 -c "
import sys,json
d=json.load(sys.stdin)
latest = d.get('dist-tags',{}).get('latest','?')
desc = d.get('description','?')
print(f'Latest: {latest}')
print(f'Description: {desc}')
"

# Weekly downloads (popularity proxy)
curl -s "https://api.npmjs.org/downloads/point/last-week/PACKAGE_NAME" 2>/dev/null | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(f'{d.get(\"downloads\",0)} weekly downloads')
"

# Check for framework-specific packages
for pkg in "@platform/sdk-react" "@platform/sdk-vue" "@platform/sdk-svelte" "@platform/sdk-solid"; do
  curl -s "https://registry.npmjs.org/$pkg" | python3 -c "
import sys,json
try:
    d=json.load(sys.stdin)
    if 'error' not in d:
        print(f'$pkg: v{d[\"dist-tags\"].get(\"latest\",\"?\")}')
except: pass
"
done
```

**Key metric:** download ratio between framework bindings (e.g., React 20K/wk vs Vue 500/wk = 40x dominance).

## Step 4: Bundle Size Measurement

```bash
# Bundlephobia API for gzipped sizes
for pkg in "FRAMEWORK@VERSION" "FRAMEWORK Binding@VERSION"; do
  curl -s "https://bundlephobia.com/api/size?package=$pkg" 2>/dev/null | python3 -c "
import sys,json
try:
    d=json.load(sys.stdin)
    print(f'{d.get(\"name\",\"?\")}: {d.get(\"size\",0)/1024:.1f}KB raw, {d.get(\"gzip\",0)/1024:.1f}KB gzip')
except: print('ERROR')
"
done
```

**Note:** Some packages return 0/ERROR (not in bundlephobia). Fall back to framework docs or manual webpack analysis.

**Framework baseline sizes (gzipped, approximate 2025-2026):**
| Framework | Core gzip | Notes |
|-----------|-----------|-------|
| React 18 (react+react-dom) | ~42 KB | Largest |
| Vue 3 | ~35 KB | Moderate |
| SolidJS | ~4 KB | Very small, compiled |
| Svelte 4/5 | ~2-5 KB | Compiled away |
| Vanilla TS | 0 KB | No framework overhead |

## Step 5: Charting / UI Library Ecosystem Check

```bash
# Charting library popularity
for pkg in "chart.js" "recharts" "d3" "@nivo/bar" "apexcharts"; do
  curl -s "https://api.npmjs.org/downloads/point/last-week/$pkg" | python3 -c "
import sys,json; d=json.load(sys.stdin); print(f'$pkg: {d.get(\"downloads\",0):,} wkd')
"
done
```

**Framework-specific charting strengths:**
- React: Recharts (41M), Tremor, shadcn/ui charts — purpose-built dashboard components
- Vue: Apache ECharts (powerful, large), vue-chartjs + Chart.js
- Svelte/Solid/Vanilla: Chart.js (10M, framework-agnostic) is the default choice

## Step 6: RTL / i18n Ecosystem Check

Quick assessment of internationalization maturity:
- `react-i18next` / `vue-i18n` / `svelte-i18n` — check npm download counts
- Tailwind CSS RTL plugin — works with all frameworks
- `Intl.NumberFormat` — native browser API, framework-independent
- Persian/Farsi calendar: `moment-hijri` or `date-fns` with locale — works everywhere

## Output Format

Always produce a structured comparison table with these dimensions:

| Criteria | Framework A | Framework B | Framework C | ... |
|----------|-------------|-------------|-------------|-----|
| SDK Compatibility | ⭐ rating + evidence | ... | ... | ... |
| Bundle Size | ⭐ rating + size | ... | ... | ... |
| TypeScript Support | ⭐ rating | ... | ... | ... |
| Charting Libraries | ⭐ rating + top libs | ... | ... | ... |
| RTL / i18n | ⭐ rating | ... | ... | ... |
| Community Adoption | ⭐ rating + numbers | ... | ... | ... |
| UI Components | ⭐ rating | ... | ... | ... |
| Performance | ⭐ rating | ... | ... | ... |
| Learning Curve | ⭐ rating | ... | ... | ... |

**Star rating scale:** ⭐ = poor, ⭐⭐ = weak, ⭐⭐⭐ = adequate, ⭐⭐⭐⭐ = good, ⭐⭐⭐⭐⭐ = excellent.

## Common Pitfalls

1. **Don't confuse npm downloads with GitHub stars.** npm downloads measure ecosystem usage; GitHub stars measure developer interest. A framework can have high stars but low adoption.

2. **Check version maturity.** v2.x bindings are typically more mature than v3.x (which may be recent rewrites). Check `dist-tags.latest` on npm.

3. **Bundle size varies with tree-shaking.** Report gzipped size as the primary metric. Raw size is less relevant with modern bundlers.

4. **Community projects reveal real-world patterns.** The language column in `gh search repos` output tells you what framework developers actually use — not what docs claim.

5. **Official templates are the strongest signal.** If an official org provides a template for Framework A but not Framework B, Framework A has first-class support.

6. **Beware of abandoned frameworks.** Check last commit date and open issues count on GitHub.
