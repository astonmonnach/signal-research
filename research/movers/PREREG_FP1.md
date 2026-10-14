# FP1 pre-registration: can the footprint pick tomorrow's gainers, held for one day?

Written 14 Oct 2026, before any of this was computed. Committed before the run.

## Why
The trader wants to know before a stock jumps, not after, and is happy to hold for one day. The runners study (`research/runners/runners-study-2026-10-01.md`) found which signs at one day's close make a +100% jump the next day more likely. The strongest were volume of 5x normal, a reverse split in the last 90 days, a price under $3, and a crash in the previous weeks. It never measured whether buying on those signs pays once every trade is counted, including the many that do nothing or fall. FP1 measures that.

**Warning written before the run:** the signs were chosen on this same data by the runners study, so a pass here is not proof. A pass earns a forward paper log, nothing more.

## Data
`research/runners/work/panel.npz`: 501 sessions, 1 Oct 2024 to 30 Sep 2026, 6,924 US common stocks, split-adjusted. For a day t its arrays give: the raw close the day before (`craw_prev`), the volume the day before as a multiple of its 20-day average (`relvol`), a reverse split in the 90 days before (`rs90`), the return over the 20 sessions to the day before (`ret20`), the adjusted prior close (`c_prev`), and the day's adjusted open, high and close (`o`, `h`, `c`). Days inside a split window (`valid` False) are not used.

## The trade
- **Signal:** at the close of day t-1, using only the arrays above.
- **Takeable:** a raw close the day before of $1 or more, and a median dollar volume of $250k or more over the 20 sessions ending the day before.
- **Entry:** the close of day t-1. **Exit:** the close of day t. That is one day.
- **Costs:** 2% per round trip (these are low-priced stocks with wide spreads). 1% and 4% are also reported.
- **Comparison:** every other takeable stock under $3 on the same day, averaged.

## Tests (three trials; nothing else is tested)
- **T1:** takeable, prior close under $3, a reverse split in the last 90 days, and volume the day before of 5x normal or more.
- **T2:** takeable, under $3, and volume the day before of 5x normal or more (no split needed).
- **T3:** takeable, under $3, volume of 5x normal or more, and down 30% or more over the previous 20 sessions.

Each trial **pays** only if the mean one-day return after 2% costs is above zero with a day-clustered bootstrap 95% interval above zero, and the mean is above zero in both halves (sessions 1 to 250, and 251 to 501). Bootstrap: resample whole days, 2,000 draws, seed 20261014.

## Reported for each trial
Number of trades and trades a month; mean, median and % positive after costs; % up 20% or more and % down 20% or more; the overnight part (close to next open); the best case if sold at the day's high (not tradeable, shown only to size the spike); the same-day comparison group's mean.

## Description only
The same three signs without the $1 floor (sub-$1 stocks), which the trader can't take.

## What would change things
Any change after a result is seen is a new, separately named study.
