# D1 results: the reverse domino (run 10 Oct 2026)

Rules: [PREREG.md](PREREG.md), committed before this ran (commit 4fa5db3). Code: `d1.py`. Raw numbers: `d1_results.json`.

## Verdict

**Not supported under the bar set in advance, but there is a real, smaller effect.**

- The bar was a lift of 1.5 or more in **both** looks for the primary cell (same 4-digit industry, leader up 10% or more).
- The forward look cleared it: **1.77** (95% interval 1.67 to 1.87).
- The backward look did not: **1.20** (1.12 to 1.29). It is clearly above 1.0, so it isn't noise, but it is well short of 1.5.

## What the data says

| Leader's move (same 4-digit industry) | Runner days with it in the 5 days before | Matched controls | Backward lift | Chance a small stock doubles in the next 5 days | Forward lift |
|---|---|---|---|---|---|
| any day (base rate) | | | | 0.27% | 1.00 |
| up 5% or more | 67.7% | 62.2% | 1.09 | 0.41% | 1.51 |
| **up 10% or more (primary)** | **47.7%** | **39.7%** | **1.20** | **0.48%** | **1.77** |
| up 20% or more | 24.6% | 17.7% | 1.39 | 0.58% | 2.13 |
| down 5% or more | 66.7% | 60.9% | 1.09 | 0.40% | 1.47 |
| down 10% or more | 39.2% | 32.3% | 1.21 | 0.45% | 1.64 |
| down 20% or more | 14.1% | 11.1% | 1.27 | 0.46% | 1.69 |

1,017 runner days and 10,229 controls had usable data. About 93% of both groups had at least one bigger linked stock.

Four things stand out:

1. **The bigger the leader's move, the stronger the effect.** 5%, 10%, 20% go 1.09, 1.20, 1.39 backward and 1.51, 1.77, 2.13 forward. That pattern holds in every table, which is what a real effect looks like.
2. **Direction barely matters for one-day doubles.** A leader falling 10% is followed by small-stock runners almost as often as a leader rising 10% (1.64 against 1.77). So this is less "a domino knocks the next one over" and more "the industry is in play": when big names in an industry are moving hard, either way, its small names are more likely to run.
3. **Without drug and biotech stocks it is stronger.** Same cell: backward 1.27, forward **2.00**. For a leader up 20% or more: backward **1.75** (1.48 to 2.07), forward **2.84** (2.45 to 3.24). Drug stocks run on their own trial news, so they dilute it.
4. **For +300% in a week, direction does matter.** There were 263 such episodes. After a leader rises 10% or more the chance is 0.124% against a 0.067% base, a lift of **1.85** (1.65 to 2.05). After a leader falls 10% it is 1.40. Without drug stocks and with a leader up 20% or more: **3.46** (2.63 to 4.37), from 67 stock-days.

## Why this is not a trade yet

- **The base rates are tiny.** Even at the strongest cell, a small stock has under a 1% chance of doubling in the next 5 days. You would be buying a hundred or more stocks to catch one, and the runners study found the median runner is down 39% twenty days later.
- **"First" isn't proven.** A small stock that starts a two-day run on the same day as the leader's move counts here as "after". The test doesn't yet require the small stock to be quiet on the leader's day.
- **Industry codes are a crude link.** Two companies with the same code can have nothing in common.
- All 36 cells are shown above or in the JSON. The strong ones are not the primary cell, so they are leads, not findings.

## What it is good for

- A **"this industry is in play" flag** for the link graph: when a liquid stock makes a 20% move, list its small linked names and look at them that day.
- A reason to build **better links than industry codes** (same customer, same contract office, same holder, same theme). If crude codes give 1.8x to 2.8x, real links may give more. That is now testable as the graph fills up.

## Next test (D2, to be written down before it is run)

1. Require the small stock to be quiet (under +10%) on the leader's day, so the order is real.
2. Measure **returns**, not just runner flags: buy the small linked names at the next open after a leader's +20% day, hold 5 days, net of costs, against matched controls.
3. Repeat with graph links once there are enough of them.
