# MV1 pre-registration: two years of daily top-10 gainers, and what came next

Written 14 Oct 2026, before any of this was computed. Committed before the run.

## Why
On 14 Oct the trader asked to backlog the daily movers log and test it over many days. The earlier runners study (`research/runners/runners-study-2026-10-01.md`) covered only +100% days. It found a median fall of 39% over the next 20 days and that 71% had no filing that day. MV1 asks a wider question: the ten biggest gainers every day, which includes +20% to +100% moves and news-driven names. It also asks whether anything known by the close of that day separates the movers that hold from the ones that fade.

## Data
- `research/runners/work/panel.npz`: 501 sessions, 1 Oct 2024 to 30 Sep 2026, 6,924 US common stocks, split-adjusted. Bars inside a split window (`valid` False) are not used.
- SEC caches already on disk: `research/runners/work/sec/subm` (submissions JSON, with acceptance times and item codes) and `research/runners/work/sec/shares` (dei shares outstanding).
- IWM from the same panel source, or Yahoo daily if it is not in the panel.

## Definitions
- **Mover day:** the day's return = close / prior close - 1, using the immediately preceding session.
- **List A (description only):** the 10 largest daily returns among all common stocks with a valid bar.
- **List B (the tested list):** the 10 largest daily returns among takeable stocks. Takeable means a prior close of $1 or more and a median dollar volume of $250k or more over the 20 sessions ending the day before.
- **Entry:** the close of the mover day (the stock is seen on the list, then bought at the close). Also reported: the next day's open.
- **Exits:** the close after 1, 5 and 20 sessions. A stock that stops trading is marked at its last close and flagged. Returns above +300% count as +300%.
- **Costs:** 1% per round trip.
- **IWM:** same entry and exit days.

## Features, all known by the close of the mover day
1. **Event:** an 8-K or 6-K accepted after 16:00 New York time the session before, and before 16:00 on the mover day.
2. **Fresh supply:** an S-1, F-1, S-3, F-3, any 424B or an EFFECT filed in the 60 calendar days before the mover day.
3. **Repeat spiker:** two or more +50% days in the 250 sessions before the mover day.
4. **Turnover:** mover-day volume divided by the latest shares outstanding filed before the day, adjusted for splits since. "Whole count traded" means 1.0 or more. Unknown if no share count within 15 months.
5. **Market value:** shares outstanding times the prior close, in buckets: under $50M, $50M to $300M, $300M or more.
6. **Close location:** the close as a share of the way from the day's low to its high. "Closed strong" is 0.9 or more; "faded" is 0.7 or less.

## Tests (three trials; nothing else is tested)
- **T1 (does buying list B at the close pay?):** the mean and median 20-session return after costs, and the mean against IWM. It **pays** only if the mean after costs is above zero with a day-clustered bootstrap 95% interval above zero, and the median is above zero.
- **T2 (do event movers hold up better?):** within list B, the 20-session return of movers with an event minus those without. The hypothesis, from research on news against no-news moves, is that event movers hold up better. It **separates** if the bootstrap 95% interval of the difference is above zero and the sign is the same in both halves of the period.
- **T3 (do the mechanics mark the fade?):** within list B movers with no event, the 20-session return of those with any of fresh supply, repeat spiker or whole count traded, minus those with none. The hypothesis is that they fade more. It **separates** if the interval of the difference is below zero and the sign holds in both halves.
- **Bootstrap:** resample whole mover days, 2,000 draws, seed 20261014.
- **Halves:** sessions 1 to 250, and 251 to 501.

## Description only (never promoted to a result)
List A with the same outcomes; outcomes by market value bucket and by close location; the share of movers that file new share supply within 10 days after the mover day; the next-open entry; and how many movers each day had no event.

## What would change things
Any change to a definition, threshold or test after a result is seen is a new, separately named study.
