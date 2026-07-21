---
name: sports-betting
description: Sports betting research, odds analysis, and match lookup. Covers football (soccer) betting forms, odds formats, match schedules, and prediction research. Uses agent-reach tools (Exa, Jina, DuckDuckGo) to find live odds, fixtures, and betting analysis.
version: 1.0.0
triggers:
  - betting
  - شرط بندی
  - odds
  - ضریب
  - match prediction
  - football bet
  - soccer bet
  - World Cup
  - parlay
  - handicap
---

# Sports Betting — Match Research & Odds Analysis

Football-focused betting research skill. Finds matches, compares odds across sportsbooks, and explains bet types.

## User Style

This user wants **fast results, no lectures**. When asked about matches:
1. Search for today's/upcoming matches immediately
2. Show odds in a clean table
3. Suggest bet types — don't explain what a moneyline is unless asked
4. Persian/Farsi preferred for UI text, English for technical terms

**Pitfall:** Do NOT start with "let me explain how betting works" — the user already knows. Just find the data.

## Odds Formats

| Format | Example | Meaning |
|--------|---------|---------|
| **American (+/-)** | +150 / -200 | +150 = win $150 on $100 bet; -200 = bet $200 to win $100 |
| **Decimal** | 2.50 | Multiply stake by odds for total payout (stake × 2.50) |
| **Fractional** | 3/2 | Win 3 for every 2 staked |
| **Hong Kong** | 0.50 | Profit per unit staked (0.50 = 50% return) |
| **Malay** | 0.50 / -0.67 | Positive = profit per unit; negative = stake needed to win 1 unit |
| **Indo** | 1.50 / -1.50 | Similar to Malay but different scaling |

**Conversion quick refs:**
- American → Decimal: positive → (odds/100)+1; negative → (100/|odds|)+1
- Decimal → Implied probability: 1/decimal × 100

## Bet Types — Quick Reference

### Single Bets
| Type | What it is | When to use |
|------|-----------|-------------|
| **Moneyline (1X2)** | Pick winner or draw | Simplest bet, 3 outcomes in football |
| **Draw No Bet (DNB)** | Pick winner, draw = refund | Reduce risk on close matches |
| **Double Chance (1X, X2, 12)** | Cover 2 of 3 outcomes | Higher hit rate, lower odds |
| **Asian Handicap (AH)** | Goal handicap, removes draw | Best value for experienced bettors |
| **Over/Under (O/U)** | Total goals above/below line | Good when teams are evenly matched |
| **Both Teams to Score (BTTS)** | Yes/No both teams score | Attacking teams, weak defenses |
| **Correct Score** | Exact final score | High odds, low probability |
| **Clean Sheet** | Team keeps zero goals | Strong defensive teams |
| **HT/FT** | Halftime result + Fulltime result | Momentum-based teams |

### Combination Bets
| Type | What it is | Risk |
|------|-----------|------|
| **Parlay/Accumulator** | Multiple selections, all must win | High reward, high risk |
| **Same Game Parlay (SGP)** | Multiple picks from ONE match | Medium-high |
| **Teaser** | Parlay with adjusted spreads | Lower payout, easier to hit |
| **System Bet** | Covers multiple parlay combos | Partial coverage |

### Specials
| Type | What it is |
|------|-----------|
| **Futures** | Tournament/season winner (long-term) |
| **Props** | Specific events (cards, corners, shots) |
| **Player Props** | Individual player stats |
| **Live/In-Play** | Bets placed during the match |
| **Cash Out** | Settle early for profit/loss |

## Research Workflow

### 1. Find Today's Matches
```bash
# Exa (best quality)
export PATH="$HOME/.local/node/bin:$HOME/.local/bin:$PATH"
mcporter call 'exa.web_search_exa(query: "today football matches fixtures odds", numResults: 5)'

# Jina Reader (direct page scrape)
curl -s "https://r.jina.ai/https://www.goal.com/en/fixtures" -H "Accept: text/plain" --max-time 15

# DuckDuckGo fallback
curl -sL "https://html.duckduckgo.com/html/?q=today+football+matches+odds" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
```

### 2. Compare Odds Across Sportsbooks
Search for specific match odds:
```bash
mcporter call 'exa.web_search_exa(query: "SPAIN vs ARGENTINA odds betting DraftKings FanDuel bet365", numResults: 5)'
```

### 3. Research a Specific Bet
```bash
mcporter call 'exa.web_search_exa(query: "Asian handicap strategy football over under 2.5 tips", numResults: 3)'
```

### 4. Check League Standings / Form
```bash
mcporter call 'exa.web_search_exa(query: "Premier League standings 2026 form guide", numResults: 3)'
```

## Output Format

When presenting betting info, use this structure:

```
## ⚽ [Home Team] vs [Away Team]
**Competition:** [League/Tournament]
**Time:** [Date, Time, Timezone]

### 📊 Odds Comparison
| Sportsbook | Home | Draw | Away |
|-----------|------|------|------|
| [Book1]   | +130 | +195 | +255 |
| [Book2]   | +125 | +200 | +250 |

### 🎯 Suggested Bets
| Bet Type | Selection | Odds | Confidence |
|----------|-----------|------|------------|
| Moneyline | [Pick] | [Odds] | ⭐⭐⭐ |
| O/U 2.5 | Over | [Odds] | ⭐⭐ |

### 📝 Analysis
[1-2 sentence key insight]
```

## Persian/Farsi Bet Terminology

| English | فارسی |
|---------|-------|
| Moneyline | شرط برد/باخت |
| Over/Under | بالا/پایین |
| Handicap | هندیکپ |
| Parlay | میکس |
| Odds | ضریب |
| Stake | مبلغ شرط |
| Payout | سود |
| Favorite | فاووریت |
| Underdog | آندرداگ |
| Draw | مساوی |

## ⚠️ Pitfalls

- **Don't explain basics** unless asked — user knows betting
- **Always show odds from multiple sportsbooks** — comparison is key
- **Convert odds to implied probability** when relevant — helps user see value
- **Note if odds are pre-match or live** — they change rapidly
- **World Cup / tournament matches** may have extra time rules — always clarify if 90-min or includes ET
- **Asian handicap lines** like 0.75 split into two bets — explain the split if user asks

## Supported Tools

| Tool | Status | Use for |
|------|--------|---------|
| Exa (mcporter) | ✅ Installed | Best quality search, semantic matching |
| Jina Reader | ✅ Always available | Page scraping, article reading |
| DuckDuckGo | ✅ Always available | Fallback search |
| Yahoo Search | ✅ Always available | When DDG blocks |
| agent-reach CLI | ❌ Not installed | Full platform routing (optional) |
| yt-dlp | ❌ Not installed | Video analysis (optional) |
