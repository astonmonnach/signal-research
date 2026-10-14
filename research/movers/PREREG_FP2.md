# FP2 pre-registration: buy the footprint at the close, sell at the next open

Written 14 Oct 2026. Committed before any FP2 number was computed and before the forward log starts.

## Why
FP1 failed as a one-day hold, but its trades for T1 gained an average of +4.55% from the close to the next open and gave it back after the open (`fp1/RESULTS.md`). That was seen in the FP1 data, so testing it again on the same two years proves nothing. **FP2 is therefore judged only on trades from the forward paper log.** The two-year numbers are reported as "already seen" and cannot pass.

## Signals (the same signs as FP1, unchanged)
- **S1 (FP1 T1):** a price of $1 to $3, a reverse split in the last 90 days, and the day's volume at 5x or more its average over the previous 20 sessions.
- **S2 (FP1 T2):** a price of $1 to $3, and the day's volume at 5x or more its 20-session average.
- Both also need a median dollar volume of $250k or more over the previous 20 sessions.

## The trade
- **Entry:** the official close on the signal day. In real trading that is a market-on-close order, which IBKR takes until 15:50 New York time (20:50 UK).
- **Exit:** the official open the next trading day, as a market-on-open order.
- **Costs:** 2% per round trip, with 1% and 4% also reported.

## The forward paper log (this is the test)
- `research/movers/fp2/live.py signal` runs at about 19:40 UTC (20:40 UK) on US trading days. It takes the day's volume so far from the free Nasdaq stock screener and history from Yahoo, so it uses only what is known about 20 minutes before the close. Volume at that time is short of the full day, which makes the 5x test slightly harder to meet than in the backtest. Each run's time is logged, and a run after 20:00 UTC is flagged as late.
- `live.py fill` runs the next US trading day after the open. It records the official close of the signal day and the next open from Yahoo daily bars.
- Every signal is kept, including ones with missing prices, which are flagged.
- **S2 is judged at 100 forward trades** (several a day, so a few weeks). It **pays** only if the mean after 2% costs is above zero with a day-clustered bootstrap 95% interval above zero (2,000 draws, seed 20261014).
- **S1 is judged at 40 forward trades** (about one a day or less) on the same rule.
- Until then, nothing is traded with real money.

## Already-seen numbers (reported, never a pass)
The same close-to-open trade on the two-year panel (1 Oct 2024 to 30 Sep 2026), for S1 and S2, with the same costs, interval and halves.

## What would change things
Any change to a sign, threshold, timing or pass mark is a new, separately named study. The forward count restarts.
