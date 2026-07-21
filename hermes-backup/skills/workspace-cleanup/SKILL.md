---
name: workspace-cleanup
description: "Use when the user asks to clean up, declutter, slim down, or free space in a workspace/directory. Identifies disposable files, categorizes them by deletion risk, presents a categorized list before deleting, and executes in batches sized to avoid tripping mass-deletion guards. Covers duplicate-archive detection, version-chain pruning, one-off script identification, and regenerable-artifact removal (.venv, node_modules, __pycache__)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [workspace, cleanup, disk-hygiene, deletion, declutter]
    related_skills: [careful, guard, local-webapp-access-diagnose]
---

# Workspace Cleanup

## Overview

A workspace accumulates junk: archive copies left after extraction, intermediate version files superseded by a final, one-off research/stress-test scripts, duplicate skill extractions, and regenerable virtualenvs. This skill identifies that junk, categorizes it by deletion risk, and removes it safely.

The discipline is **survey → categorize → present → delete in batches**, not "scan and nuke." The user decides what goes; the agent does the legwork of detecting duplicates and version chains.

## When to Use

- User says "clean up the workspace", "ورک‌اسپیس رو سبک کن", "free up space", "too much junk here", "slim down this directory"
- User asks what's taking up space, or why a directory is large
- After a long project finishes and leftovers (`.tar.gz`, `.rar`, `_out/` folders, stress-test scripts) pile up

## Don't Use For

- Garbage collection inside a running app or DB (use that system's tooling)
- Git history cleanup (separate concern — BFG / filter-repo, not this skill)
- `node_modules` / `.venv` of an *active* project the user is mid-work on without confirmation
- Cleaning `~/.hermes/` itself — that's Hermes state, not workspace junk

## Workflow

### 1. Survey — size first, contents second

Always run both in parallel on the first turn:

```bash
# Top-level size, biggest first
du -sh * .[!.]* 2>/dev/null | sort -rh | head -30

# Full listing with sizes and dates
ls -la
```

Then dig into the largest items and anything that looks like a duplicate or version chain (see Detection Patterns below).

### 2. Detect duplicates and version chains

Run these detection passes. Each is one terminal call; batch the independent ones.

**Archive + extracted folder pairs:**
```bash
# For each .tar.gz / .rar / .zip, check if an extracted folder of the same name exists
for a in *.tar.gz *.rar *.zip; do
  base="${a%.*.*}"; base="${base%.*}"
  [ -d "$base" ] && echo "DUP: $a ↔ $base/"
done
```

**Version chains (keep the final, flag the rest):**
```bash
# Group by stem and list versions — e.g. mega-prompt-v3.1, v3.2, ..., v3.7-final
ls -la <prefix>* | sort
```
Identify the final/stable version (highest number, `-final` / `-NEHAEE` / `-full` suffix, or the one the user treats as canonical) and flag the rest as superseded.

**Duplicate content folders** (e.g. `skills_extracted/`, `skills_extracted_pp/`, `skills_out/` all holding `skills/`):
```bash
for d in */; do
  # compare first child of each suspicious folder
  ls "$d" 2>/dev/null | head -1
done
```
Cross-check with `diff -q` on representative files if unsure.

**Regenerable artifacts:**
```bash
find . -maxdepth 3 -name .venv -o -name node_modules -o -name __pycache__ 2>/dev/null
du -sh <each>  # report size — .venv can be 50-100MB+
```

### 3. Categorize by deletion risk

Present findings in this tier order. This is the core of the skill — the tiering lets the user decide quickly without re-reading each file.

| Tier | Meaning | Examples |
|------|---------|---------|
| **1. Obvious / no-risk** | Regenerable, pure duplicates, or extracted copies of archives still present | `__pycache__/`, `*.rar` when extracted `_out/` exists, `foo.tar.gz` when `foo/` exists, 4-line stub `.md` files |
| **2. Likely extra** | Superseded versions in a chain, duplicate-content folders | `mega-prompt-v3.1` through `v3.6-*` when `v3.7-full.md` is canonical; `skills_extracted/` vs `skills_out/` |
| **3. Needs judgment** | One-off scripts that did their job, regenerable venvs of active projects | `gh_*.py`, `fetch_*.py`, `stress_benchmark*.py`, `game-news/.venv/` (63MB but project is active) |

For each tier, list files with size and a one-line "why extra" reason. Always note what is **kept** (active projects, resumes, personal docs, `.hermes/`).

### 4. Present the list — do NOT pre-pick a deletion tier

**User preference (this user):** when asked how aggressively to clean, this user chose "give me the full list first so I can decide myself" over picking an aggression tier. Default to presenting the full categorized list and letting the user pick, rather than offering "quick / medium / aggressive" presets. Offer the presets only as a secondary option if the user wants speed.

Format the list as a markdown table or grouped bullets with:
- File/folder name
- Size
- One-line reason it's extra
- What gets kept if the tier is removed

End with: "بگو کدوم دسته‌ها رو پاک کنم" (or equivalent) and wait.

### 5. Delete in batches sized under the mass-deletion guard

Hermes' security scan trips on ~15-20+ non-build files deleted within ~20s ("ransomware-like burst"). This is a **false positive for cleanup work** but still requires user approval when it fires.

Strategy: **delete in two batches, not one mega-rm.**

- **Batch A — obvious/no-risk:** `__pycache__`, `*_out/`, `*.rar`, duplicate `*.tar.gz`, stub files. One `rm -rf` + `rm -f` compound command.
- **Batch B — version chains + one-off scripts + dup folders:** separate `rm -f` / `rm -rf` calls, grouped by category with an `echo` label between.

After each batch:
```bash
du -sh . 2>/dev/null   # show new total
```

If the mass-deletion guard fires (it will on Batch A if ≥15 files), the user approves once — that's expected, not an error. Do not re-architect the deletion to avoid it; the approval is the correct path.

### 6. Report and surface the biggest remaining lever

After cleanup, report:
- Total before → after
- What was removed (by category, not file-by-file)
- The single biggest remaining removable item (often a `.venv` or `node_modules` of an active project) with a one-line "regenerable via X" note and ask if the user wants it gone too

## Detection Patterns — Quick Reference

| Pattern | Detection | Action |
|---------|-----------|--------|
| Archive + extracted folder | `for a in *.tar.gz; do base="${a%.*.*}"; [ -d "$base" ] && echo "DUP"; done` | Flag archive for deletion (folder is the source of truth) |
| Version chain | `ls <prefix>-v*` and sort | Keep highest / `-final`, flag rest |
| Duplicate content folders | `diff -q` a representative file across folders | Keep one, flag rest |
| `__pycache__` | `find . -name __pycache__` | Always deletable |
| `.venv` / `node_modules` | `find . -maxdepth 3 -name .venv -o -name node_modules` | Regenerable — ask if project is active |
| Empty/tiny JSON results | `ls -la *.json` and check sizes (≤10 bytes usually = failed run) | Deletable with the script that produced them |
| One-off scripts | Prefix families: `gh_*.py`, `fetch_*.py`, `search_*.py`, `token_*.py`, `reddit_*.py`, `stress_*.py` | Deletable if the research/test is done |

## Common Pitfalls

1. **Deleting an archive before confirming the extracted folder is complete.** Always `ls` the extracted folder and `tar tzf <archive> | head` to confirm contents match before flagging the archive as redundant. A truncated extract + a full archive = data loss.

2. **Pruning a version chain and keeping the wrong "final".** A file named `-final` isn't always the latest — check mtimes and ask the user which is canonical if two candidates exist (e.g. `v3.6-NEHAEE` vs `v3.6-final` vs `v3.7-full`).

3. **Nuking `.venv` of an active project without asking.** `.venv` is the single biggest space win but also the most disruptive to remove. Always surface it separately with the regeneration command (`pip install -r requirements.txt`) and let the user decide.

4. **Offering aggression tiers before showing the list.** This user prefers to see the full categorized list first, then decide. Leading with "quick / medium / aggressive" presets skips the step they want. Show the list; offer presets only as a fallback.

5. **One mega-`rm` that trips the deletion guard and looks like an attack.** Split into two labeled batches. The guard firing is expected — approve and continue, don't work around it by deleting files one at a time (that's slower and hides the pattern from audit logs).

6. **Forgetting to report the after-state.** Always run `du -sh .` after each batch and after the full cleanup. The user wants to see the delta.

7. **Deleting files the user is emotionally attached to without a mention.** Resumes, personal docs (`.xlsx`, `.pdf`, `.docx` with the user's name), and `.hermes/` are never "junk." If in doubt, list them under "kept" explicitly so the user sees they're safe.

## Verification Checklist

- [ ] Surveyed with `du -sh` AND `ls -la` (both, not just one)
- [ ] Ran duplicate-archive detection (tar/rar + matching extracted folder)
- [ ] Identified version chains and named the canonical version being kept
- [ ] Checked for regenerable artifacts (`.venv`, `node_modules`, `__pycache__`)
- [ ] Presented a categorized list (tiered by risk) before any deletion
- [ ] User confirmed which tiers/categories to remove
- [ ] Deleted in ≤2 batches, each batch labeled
- [ ] Reported `du -sh .` before and after each batch
- [ ] Surfaced the biggest remaining removable item with its regeneration command
- [ ] No active-project `.venv` / `node_modules` removed without explicit confirmation