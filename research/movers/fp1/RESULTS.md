# FP1 results: footprint signs at one close, sold at the next close (run 14 Oct 2026)

Rules: [../PREREG_FP1.md](../PREREG_FP1.md), committed (4ffd46e) before this ran. Code: `run.py`. Numbers: `results.json`; trades: `trades_T1.csv`, `trades_T2.csv`, `trades_T3.csv`. Data: 1 Oct 2024 to 30 Sep 2026.

## Verdict: FAIL, all three trials

| Trial | Signs at the close | Trades | A month | Mean after 2% costs | 95% range | Median | Winners | First half / second half |
|---|---|---|---|---|---|---|---|---|
| T1 | $1-3, reverse split in 90 days, volume 5x normal | 391 | 16 | +0.06% | -3.82% to +4.45% | -7.03% | 27% | +3.59% / -1.83% |
| T2 | $1-3, volume 5x normal | 3,046 | 128 | -1.42% | -2.25% to -0.54% | -3.64% | 35% | -1.29% / -1.56% |
| T3 | $1-3, volume 5x normal, down 30% in 20 sessions | 818 | 34 | -3.21% | -4.91% to -1.42% | -5.49% | 31% | -2.55% / -3.74% |

The pass mark was a mean above zero after 2% costs, a 95% range above zero, and both halves above zero. None passes.

## What the trades looked like

| Trial | Mean before costs | Up 20% or more | Down 20% or more | Overnight part (close to next open) | Median best case if sold at the day's high |
|---|---|---|---|---|---|
| T1 | +2.06% | 9.2% | 11.0% | +4.55% | +3.3% |
| T2 | +0.58% | 7.6% | 7.0% | +1.76% | +5.0% |
| T3 | -1.21% | 7.6% | 10.9% | +0.47% | +4.3% |
| All $1-3 takeable stock-days (comparison) | -0.02% | 1.2% | 0.7% | +0.24% | +2.9% |

- The footprint does change the odds of a big day: 8% to 9% of footprint trades rose 20% or more, against 1.2% of ordinary $1-3 stocks.
- It changes the odds of a big loss just as much: 7% to 11% fell 20% or more.
- The typical trade loses. The median is -3.6% to -7.0% after costs, and only 27% to 35% are winners.
- In T1 the average gain arrives overnight (+4.55% from close to next open) and is then given back during the day. This was not tested. Selling at the open is a different trade and would need its own pre-registered test, with opening spreads, which are often wide in these stocks.

## Description only: the same signs below $1 (not takeable)
T1 without the $1 floor: 1,285 trades, mean +1.86% after 2% costs (range -2.13% to +8.17%), median -6.27%. A few huge winners hold up the mean while most trades lose. That is a lottery ticket, not an edge.

## Caveats
- The signs were picked on this same data by the runners study, which should flatter them. They still fail.
- Costs of 2% are an assumption. At 1%, T1 would average +1.06% before the halves check, still with a negative median and an interval spanning zero.
- The self-consistency check passes for every row (share of winners times average win plus losers times average loss equals the mean).

## Plain English
Buying the footprint at the close and selling the next day doesn't pay. It raises the chance of a big jump from about 1 in 80 to about 1 in 11, but it raises the chance of a big fall just as much, and most trades lose a few percent. The one thing worth a separate look is that T1's gain comes overnight and disappears after the open.
