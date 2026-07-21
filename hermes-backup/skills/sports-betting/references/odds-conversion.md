# Odds Conversion Quick Reference

## American ↔ Decimal

```
American positive → Decimal: (american / 100) + 1
American negative → Decimal: (100 / |american|) + 1

+150 → 2.50    -200 → 1.50
+100 → 2.00    -110 → 1.909
+250 → 3.50    -300 → 1.333
+500 → 6.00    -500 → 1.20
```

## Decimal → Implied Probability

```
Prob = 1 / Decimal × 100

2.00 → 50.0%    1.50 → 66.7%
2.50 → 40.0%    1.33 → 75.2%
3.00 → 33.3%    1.25 → 80.0%
3.50 → 28.6%    1.10 → 90.9%
```

## American → Implied Probability

```
Positive: 100 / (american + 100) × 100
Negative: |american| / (|american| + 100) × 100

+150 → 40.0%    -200 → 66.7%
+100 → 50.0%    -110 → 52.4%
+250 → 28.6%    -300 → 75.0%
```

## Decimal → Fractional

```
fractional = (decimal - 1) expressed as fraction

2.50 → 3/2     1.50 → 1/2
3.00 → 2/1     1.33 → 1/3
4.00 → 3/1     1.25 → 1/4
6.00 → 5/1     1.20 → 1/5
```

## Common Bet Payouts (per $100 stake)

| Bet Type | Odds | Stake | Win | Total Return |
|----------|------|-------|-----|-------------|
| Moneyline | +150 | $100 | $150 | $250 |
| Moneyline | -200 | $200 | $100 | $300 |
| Parlay 2-leg | +264 | $100 | $264 | $364 |
| Parlay 3-leg | +596 | $100 | $596 | $696 |
| Under 2.5 | -160 | $160 | $100 | $260 |
| Over 2.5 | +130 | $100 | $130 | $230 |

## Asian Handicap Lines Explained

| Line | Meaning | Outcome scenarios |
|------|---------|-------------------|
| 0 (PK) | Draw No Bet | Win=pay, Draw=refund, Lose=loss |
| -0.25 | Quarter ball | Half stake on 0, half on -0.5 |
| -0.5 | Half ball | Must win by 1+ |
| -0.75 | Three-quarter | Half on -0.5, half on -1.0 |
| -1.0 | One ball | Must win by 2+; win by 1 = refund |
| +0.5 | Half ball head start | Win or draw = win |
| +1.0 | One ball head start | Win, draw, or lose by 1 = win |

## Value Bet Detection

```
Value exists when: Implied probability < Your estimated probability

Example:
- Sportsbook odds: +150 (implied 40%)
- Your analysis: Team has 50% chance to win
- Value = 50% - 40% = 10% edge → BET

No value when:
- Sportsbook odds: -200 (implied 66.7%)
- Your analysis: Team has 60% chance
- Value = 60% - 66.7% = -6.7% → NO BET
```

## Overround / Vig Calculator

```
Overround = sum of all implied probabilities - 100%

3-way market: (1/Home + 1/Draw + 1/Away) × 100 - 100
Example: (1/2.00 + 1/3.50 + 1/3.50) × 100 - 100 = 107.1% → 7.1% overround

Lower overround = better value for bettor
Typical range: 5-12% for major football markets
```
