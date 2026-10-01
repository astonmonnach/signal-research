# Discord stock calls, Oct–Nov 2025: graded against SPY

*Prepared 2026-09-30. Authors are identified only by the style of reasoning they used.*

## Bottom line

**Across 49 directional calls, no style of reasoning showed any evidence of predictive value.** The median call trailed SPY by 12.9 points after 20 trading days. Only 12 of 49 calls (24%) beat simply holding SPY at +20 days, and only 5 of 49 (10%) had beaten it by 2026-09-29. Options-flow and momentum/volume-spike calls did clearly worse than the market. The fundamental calls lost the least, but that came from the low-volatility things they picked (Treasury ETFs), not from being right. Their stated theses were wrong at 60 days and are still wrong today.

## Data and method

- **Prices.** Daily bars come from the Yahoo Finance chart API, pulled 2026-09-30. Three tickers needed extra work:
  - **FORD** (Forward Industries) was renamed **FWDI** on 2025-11-17. The CIK is the same, and Massive reference data confirms the change. I used the FWDI history, which is continuous with FORD.
  - **IOBT** (IO Biotech) has no Yahoo data. Massive shows it delisted from Nasdaq on 2026-04-07, with the last bar on 2026-04-06.
  - **CMBM** (Cambium Networks) has no Yahoo data. Massive shows it delisted on 2026-03-27, with the last bar on 2026-03-26 at about -77% on that day.
  - For IOBT and CMBM, Massive split-adjusted aggregates were used. "To latest" means the last Nasdaq print. I did not look for any later OTC trading.
- **Latest close.** 2026-09-29 is treated as the latest close, because the 2026-09-30 bar was still intraday when the data was pulled.
- **Entry.**
  - A call dated on a trading day enters at that day's close.
  - The weekend calls (GME 10-25, BGIN and KYTX 10-26) enter at the 2025-10-27 open.
  - The "watchlist for 10-29" posted on 10-28 enters at the 10-28 close, which was the last price available when it was posted.
- **Returns.**
  - Returns are measured N trading days after the entry bar (+5, +20, +60) and to the latest close.
  - They are total-return where dividends apply, using Yahoo's adjusted close. For open entries, the adjustment factor is applied to the open.
  - Short calls are sign-flipped so that a positive number always means the call was right.
  - SPY is measured over exactly the same entry and exit bars.
  - **"Beat SPY"** means the direction-adjusted return was higher than SPY's return over the same window. In other words, the call did better than just owning the index.
- **Targets.**
  - A target counts as hit if the intraday high (or the low, for shorts) reached it within 20 trading days. For open entries the window includes the entry day; for close entries it starts the next day.
  - Targets were converted for later reverse splits, which Yahoo back-adjusts: ASST 1:20 on 2026-02-06 and BYND 1:30 on 2026-08-14.
  - The "Entry px" column shows the raw price at the time of the call.
- **Only the underlying's direction is graded.** Many of these were options plays. Strikes, expiries and premiums were not posted, so option P&L can't be reconstructed.
- **Classification.**
  - Calls with more than one style tag (F/N, F/C, O/C, M/O) are counted in each group they carry. The "ALL" row counts each call once.
  - Watchlist items and bare "X long" posts with no reasoning are grouped as **U (unclassified)**. That covers HAYW, LUNG, the 10-28 watchlist BYND/UUUU/ASST-short, and SPY-short into FOMC.
  - AZTR was a "wait for trial results" watch, not a buy. It appears in the table but is left out of every group statistic. For reference, it fell 36% by +20d and 78% by the latest close, so the advice to wait was sound.
- **Skipped:** RGTI "either way" (10-28 watchlist), VIVK and WYFI (no direction), and POET's "target equal lows" (no number, so it can't be graded as a target; its direction is graded).
- **Judgement calls:**
  - SPY-short 10-21 "support 669.78" is treated as a downside target. It was only 0.2% below entry, so hitting it tells you little.
  - BGIN's "could 5x" is not a 20-day target, so it isn't scored as one. For the record, the stock never got near 5x.
  - TZA "long" is a 3x inverse small-cap ETF, so it is really a bearish call. It is graded as a long on TZA, as stated.

Script and raw data are in the session scratchpad (`grade.py`, `px/*.json`, `massive.csv`).

## Summary by style

| Style | N | Median +5d | Median +20d | Median +60d | Median to 9/29 | Beat SPY +5d | Beat SPY +20d | Beat SPY +60d | Beat SPY to 9/29 | Median excess vs SPY, +20d | Sign test p (+20d) | Targets hit ≤20d |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F: fundamental | 8 | -1.7% | -1.4% | -2.8% | -10.5% | 2/8 (25%) | 5/8 (62%) | 0/8 (0%) | 0/8 (0%) | +1.0% | 0.73 | 0/1 |
| O: options flow | 20 | -8.1% | -18.0% | -15.9% | -32.9% | 5/20 (25%) | 3/20 (15%) | 5/20 (25%) | 4/20 (20%) | -16.7% | 0.003 | 2/4 |
| C: chart pattern | 11 | -2.4% | -8.6% | -3.3% | -16.3% | 1/11 (9%) | 2/11 (18%) | 2/11 (18%) | 0/11 (0%) | -7.8% | 0.07 | 1/2 |
| M: momentum / volume spike | 5 | -13.3% | -29.3% | -39.8% | -85.7% | 1/5 (20%) | 0/5 (0%) | 0/5 (0%) | 1/5 (20%) | -28.4% | 0.06 | 1/1 |
| N: narrative / news | 3 | -3.8% | -9.5% | -12.0% | -28.3% | 1/3 (33%) | 0/3 (0%) | 1/3 (33%) | 0/3 (0%) | -9.3% | 0.25 | n/a |
| U: unclassified / watchlist | 6 | -5.7% | -6.2% | +3.1% | -16.0% | 3/6 (50%) | 3/6 (50%) | 3/6 (50%) | 0/6 (0%) | -4.4% | 1.00 | 1/1 |
| **ALL (each call once)** | **49** | **-5.3%** | **-14.1%** | **-6.2%** | **-21.1%** | **12/49 (24%)** | **12/49 (24%)** | **11/49 (22%)** | **5/49 (10%)** | **-12.9%** | **0.0005** | **4/7** |

How to read this table:

- **Returns are direction-adjusted,** so positive means the call was right.
- **Target hit-rate uses each call's first target.** Among the two-target calls, BYND hit both $2 and $4, and TLT missed both 92.40 and 94.
- **The sign-test p values are optimistic.** They assume independent calls. These calls were made within two weeks of each other, many in correlated high-beta names, so there are far fewer truly independent bets than rows. Treat the p values as a rough sign of consistency, not as proof.

### Sensitivity checks

- **The F group is mostly one bet.** Five of its eight calls are the same Fed-cuts → long-duration-Treasuries trade (TLT, VGLT, SPTL, IEF, SHY). Keeping only TLT leaves 4 F calls: TLT, TCEHY, RBLX and BGIN. Their medians are -6.1% at +5d, -10.6% at +20d, -17.7% at +60d and -41.1% to date. They beat SPY in 1/4, 1/4, 0/4 and 0/4 of cases. The good-looking 5/8 at +20 days happened because bonds lost less than SPY during a short equity dip. The bond thesis itself was wrong: TLT is -11.2% total return to date.
- **Pure options-flow calls,** leaving out the O/C and M/O double tags, give N=18. Medians are -8.1% at +5d, -16.7% at +20d, -11.6% at +60d and -31.3% to date. Only 3/18 beat SPY at +20 days (sign-test p ≈ 0.008).
- **Means vs. medians.** Group means are similar or worse at +20d: F -7.9%, O -17.2%, C -18.0%, M -30.2%, N -16.3%. Holding to date, the O group has two huge winners, MRNA (+649%, 27 → 203) and AMD (+134%). They lift the O mean but not its median, and neither was ahead at +20 days (MRNA -11%, AMD -17%). Nobody trading a short-dated options call would have held for 11 months.
- **Most target hits were in squeezes that were already happening or were trivially close:**
  - BYND's $2 and $4 were hit on 10-21 and 10-22, during a meme squeeze already under way. The stock was then -29% at +20d and -81% to date.
  - DNUT's 4.50 was hit intraday (8% above entry), but the stock was -12.7% at +20d.
  - SPY 669.78 was only 0.2% away.
  - The ASST short to 1.18 is the one clean target hit on a thesis: the 20-day low was 0.94, and the short was +22.9% at +20d and +45.4% at +60d.

## Per-call table

| # | Call date | Ticker | Style | Dir | Entry (day, basis) | Entry px | +5d | SPY +5d | +20d | SPY +20d | +60d | SPY +60d | To 2026-09-29 | SPY same | Target (<=20d) | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2025-10-26 | BGIN | F/N | L | 2025-10-27 open | 4.97 | -20.9% | +0.1% | -38.4% | -2.1% | -29.7% | +1.3% | -48.3% | +13.1% |  | "could 5x"; Nasdaq IPO/crypto narrative |
| 2 | 2025-10-27 | TLT | F/C | L | 2025-10-27 close | 91.78 | -1.9% | -0.3% | -1.6% | -2.4% | -3.1% | +0.9% | -11.2% | +12.7% | 92.4: miss; 94: miss (20d high 92.18) | Fed cuts -> long bonds; break resistance |
| 3 | 2025-10-27 | VGLT | F | L | 2025-10-27 close | 58.22 | -1.6% | -0.3% | -1.3% | -2.4% | -2.5% | +0.9% | -9.8% | +12.7% |  | Fed cuts -> long bonds |
| 4 | 2025-10-27 | SPTL | F | L | 2025-10-27 close | 27.6 | -1.7% | -0.3% | -1.3% | -2.4% | -2.6% | +0.9% | -9.8% | +12.7% |  | Fed cuts -> long bonds |
| 5 | 2025-10-27 | IEF | F | L | 2025-10-27 close | 97.49 | -0.7% | -0.3% | +0.2% | -2.4% | -0.7% | +0.9% | -4.9% | +12.7% |  | Fed cuts -> long bonds |
| 6 | 2025-10-27 | SHY | F | L | 2025-10-27 close | 83.09 | -0.1% | -0.3% | +0.3% | -2.4% | +0.6% | +0.9% | +0.9% | +12.7% |  | Fed cuts -> long bonds |
| 7 | 2025-10-30 | TCEHY | F | L | 2025-10-30 close | 83.47 | -1.3% | -1.4% | -5.3% | +0.5% | -5.8% | +2.6% | -33.9% | +13.6% |  | long-term long |
| 8 | 2025-10-30 | RBLX | F | L | 2025-10-30 close | 113 | -10.4% | -1.4% | -15.9% | +0.5% | -33.4% | +2.6% | -63.6% | +13.6% |  | "risky short term, long term potential" |
| 9 | 2025-10-27 | RBLX | O | L | 2025-10-27 close | 128.5 | -16.2% | -0.3% | -29.5% | -2.4% | -42.3% | +0.9% | -68.0% | +12.7% |  | "premium flowing in" |
| 10 | 2025-10-30 | AZTR | F | W | 2025-10-30 close | 0.59 | -25.9% | -1.4% | -36.1% | +0.5% | -53.1% | +2.6% | -77.8% | +13.6% |  | WATCH only: wait for trial results |
| 11 | 2025-10-31 | BABA | C | L | 2025-10-31 close | 170.4 | -2.4% | -1.6% | -3.6% | -0.3% | +2.2% | +2.1% | -36.2% | +13.3% |  | 20 EMA / fair value gap |
| 12 | 2025-10-31 | BIDU | N | L | 2025-10-31 close | 120.9 | +4.2% | -1.6% | -1.0% | -0.3% | +30.3% | +2.1% | -28.3% | +13.3% |  | "more room to run" |
| 13 | 2025-10-31 | JD | N | L | 2025-10-31 close | 33.04 | -3.8% | -1.6% | -9.5% | -0.3% | -12.0% | +2.1% | -17.6% | +13.3% |  | "more room to run" |
| 14 | 2025-10-31 | IOBT | M | L | 2025-10-31 close | 1.04 | -13.3% | -1.6% | -34.4% | -0.3% | -69.6% | +2.1% | -95.4% (last trade 2026-04-06) | -2.8% |  | long at ~$1.05 |
| 15 | 2025-10-27 | UUUU | O | L | 2025-10-27 close | 19.1 | -6.8% | -0.3% | -26.9% | -2.4% | +33.5% | +0.9% | -42.5% | +12.7% |  |  |
| 16 | 2025-10-27 | DNUT | O | L | 2025-10-27 close | 4.16 | -11.5% | -0.3% | -12.7% | -2.4% | -18.5% | +0.9% | -30.8% | +12.7% | 4.5: HIT 2025-11-06 (20d high 4.53) |  |
| 17 | 2025-10-27 | TZA | O | L | 2025-10-27 close | 7.34 | +6.3% | -0.3% | +12.5% | -2.4% | -17.4% | +0.9% | -33.8% | +12.7% |  | "potential bottom" (3x inverse small-cap ETF) |
| 18 | 2025-10-27 | CHTR | O | L | 2025-10-27 close | 245.4 | -9.5% | -0.3% | -18.9% | -2.4% | -21.9% | +0.9% | -54.9% | +12.7% |  |  |
| 19 | 2025-10-27 | CAT | O | L | 2025-10-27 close | 527.1 | +8.3% | -0.3% | +6.2% | -2.4% | +19.2% | +0.9% | +57.8% | +12.7% |  |  |
| 20 | 2025-10-26 | KYTX | O | L | 2025-10-27 open | 7.88 | -12.7% | +0.1% | -4.9% | -2.1% | +23.9% | +1.3% | -13.2% | +13.1% | 10: miss (20d high 8.45) | "continuation to $10" |
| 21 | 2025-10-25 | GME | O | L | 2025-10-27 open | 24.5 | -9.8% | +0.1% | -16.4% | -2.1% | -6.2% | +1.3% | -3.0% | +13.1% |  | "run-up now" |
| 22 | 2025-10-27 | KURA | O | L | 2025-10-27 close | 11.04 | -11.5% | -0.3% | +6.2% | -2.4% | -21.8% | +0.9% | -2.1% | +12.7% |  |  |
| 23 | 2025-10-27 | TGS | C | L | 2025-10-27 close | 30.75 | -0.8% | -0.3% | -4.3% | -2.4% | +0.8% | +0.9% | -16.3% | +12.7% |  |  |
| 24 | 2025-10-27 | ASST | C | L | 2025-10-27 close | 1.64 | -22.6% | -0.3% | -31.1% | -2.4% | -46.9% | +0.9% | -10.6% | +12.7% |  |  |
| 25 | 2025-10-28 | GSIT | O/C | L | 2025-10-28 close | 11.43 | -23.4% | -1.7% | -47.5% | -1.8% | -35.5% | +1.1% | -52.2% | +12.4% |  |  |
| 26 | 2025-10-28 | PDSB | O | L | 2025-10-28 close | 0.933 | -4.7% | -1.7% | -20.0% | -1.8% | -3.3% | +1.1% | -20.4% | +12.4% |  |  |
| 27 | 2025-10-28 | HAYW | U | L | 2025-10-28 close | 15.33 | +5.6% | -1.7% | +7.7% | -1.8% | +7.2% | +1.1% | -19.5% | +12.4% |  | no style stated |
| 28 | 2025-10-28 | LUNG | U | L | 2025-10-28 close | 1.98 | -13.1% | -1.7% | -14.1% | -1.8% | -9.6% | +1.1% | +0.0% | +12.4% |  | no style stated |
| 29 | 2025-10-28 | RGTI | O | L | 2025-10-28 close | 37.07 | -5.1% | -1.7% | -29.6% | -1.8% | -41.3% | +1.1% | -57.5% | +12.4% |  |  |
| 30 | 2025-10-28 | BYND | U | L | 2025-10-28 close | 1.975 | -32.7% | -1.7% | -56.6% | -1.8% | -55.3% | +1.1% | -86.1% | +12.4% |  | watchlist for 10-29 |
| 31 | 2025-10-28 | ASST | U | S | 2025-10-28 close | 1.44 | +13.2% | -1.7% | +22.9% | -1.8% | +45.4% | +1.1% | -1.8% | +12.4% | 1.18: HIT 2025-10-30 (20d low 0.94) | watchlist for 10-29, SHORT |
| 32 | 2025-10-28 | SPY | U | S | 2025-10-28 close | 687.1 | +1.7% | -1.7% | +1.8% | -1.8% | -1.1% | +1.1% | -12.4% | +12.4% |  | watchlist for 10-29, SHORT into FOMC |
| 33 | 2025-10-28 | UUUU | U | L | 2025-10-28 close | 20.03 | -15.1% | -1.7% | -27.6% | -1.8% | +16.5% | +1.1% | -45.1% | +12.4% |  | watchlist for 10-29 |
| 34 | 2025-10-29 | FORD | C | L | 2025-10-29 close | 14.4 | -25.8% | -1.4% | -40.7% | -1.1% | -50.9% | +1.5% | -44.4% | +12.4% |  | renamed FWDI 2025-11-17 (same CIK) |
| 35 | 2025-10-29 | PPBT | M | L | 2025-10-29 close | 1.06 | -23.8% | -1.4% | -25.1% | -1.1% | -39.8% | +1.5% | -85.7% | +12.4% |  | volume spike |
| 36 | 2025-10-29 | CMBM | M | L | 2025-10-29 close | 2.95 | -7.5% | -1.4% | -28.8% | -1.1% | -44.1% | +1.5% | -86.4% (last trade 2026-03-26) | -5.6% |  | volume spike |
| 37 | 2025-10-29 | TLIH | M | L | 2025-10-29 close | 0.5 | -15.8% | -1.4% | -33.2% | -1.1% | -24.0% | +1.5% | +14.0% | +12.4% |  | volume spike |
| 38 | 2025-10-29 | CIFR | C | L | 2025-10-29 close | 19.59 | +26.1% | -1.4% | -2.2% | -1.1% | -4.3% | +1.5% | -15.7% | +12.4% |  | breakout |
| 39 | 2025-10-31 | MRNA | O | L | 2025-10-31 close | 27.16 | -9.6% | -1.6% | -11.0% | -0.3% | +72.5% | +2.1% | +649.1% | +13.3% |  |  |
| 40 | 2025-10-31 | GLXY | O | L | 2025-10-31 close | 35.01 | -9.9% | -1.6% | -29.2% | -0.3% | -14.4% | +2.1% | -34.1% | +13.3% |  |  |
| 41 | 2025-10-31 | HIMS | C | L | 2025-10-31 close | 45.46 | -9.7% | -1.6% | -17.5% | -0.3% | -34.3% | +2.1% | -36.9% | +13.3% |  | break resistance |
| 42 | 2025-10-31 | IREN | O | L | 2025-10-31 close | 60.75 | +2.7% | -1.6% | -20.2% | -0.3% | -1.5% | +2.1% | -31.9% | +13.3% |  |  |
| 43 | 2025-11-03 | AMD | O | L | 2025-11-03 close | 259.6 | -6.0% | -0.3% | -17.1% | -0.3% | -8.8% | +1.6% | +134.0% | +13.0% |  |  |
| 44 | 2025-10-20 | ACHR | O | L | 2025-10-20 close | 11.98 | -5.3% | +2.1% | -38.1% | -0.8% | -26.0% | +3.4% | -57.8% | +15.1% |  |  |
| 45 | 2025-10-20 | TSLA | C | L | 2025-10-20 close | 447.4 | +1.1% | +2.1% | -8.6% | -0.8% | -2.0% | +3.4% | -21.1% | +15.1% |  |  |
| 46 | 2025-10-20 | BYND | M/O | L | 2025-10-20 close | 1.47 | +23.1% | +2.1% | -29.3% | -0.8% | -29.3% | +3.4% | -81.3% | +15.1% | 2: HIT 2025-10-21; 4: HIT 2025-10-22 (20d high 7.69) | targets $2 / $4 |
| 47 | 2025-10-20 | RANI | O | L | 2025-10-20 close | 2.25 | -20.9% | +2.1% | -13.8% | -0.8% | -38.2% | +3.4% | -64.4% | +15.1% | 4.5: miss (20d high 3.87) |  |
| 48 | 2025-10-20 | BEN | O | L | 2025-10-20 close | 22.65 | +3.2% | +2.1% | -4.8% | -0.8% | +16.2% | +3.4% | +49.8% | +15.1% |  |  |
| 49 | 2025-10-21 | POET | C | L | 2025-10-21 close | 7.45 | -5.1% | +2.3% | -42.4% | -1.7% | +11.4% | +3.3% | +3.0% | +15.1% |  | 0.5 fib; "target equal lows" (no number, not graded) |
| 50 | 2025-10-21 | SPY | C | S | 2025-10-21 close | 671.3 | -2.3% | +2.3% | +1.7% | -1.7% | -3.3% | +3.3% | -15.1% | +15.1% | 669.78: HIT 2025-10-22 (20d low 655.86) | short; "support 669.78" treated as downside target |
Column notes: Dir L means long, S means short, and W means watch only. Returns are direction-adjusted. The SPY columns show SPY's own (unadjusted) return over the same bars. For delisted names, "To 2026-09-29" runs to the last trade, and the SPY column runs to the same date.

## Caveats

1. **Small N.** There are 49 graded calls, 3 to 20 per style. Several are duplicates: the five bond ETFs, UUUU twice, BYND twice, and ASST long then short a day later. One or two outliers can move a group median a lot. The N group (3 calls) and the M group (5 calls) can't support any conclusion alone.
2. **One short window in one market regime.** Every call was made between 2025-10-20 and 2025-11-03, the peak of a speculative run in small-cap, quantum, crypto-miner, nuclear and meme names. Many of those names dropped sharply in November. SPY was roughly flat to -2% over most of the +20-day windows. A different two weeks could give a different ranking. That mostly matters for O and M, which were concentrated in exactly those names.
3. **Survivorship and selection.** This grades what was posted, not what anyone traded, at what size, or when they exited. Any wins that were taken and not posted, and any calls that were deleted or never made, are invisible here. Posting-time entries are also idealised; many of these names gapped.
4. **Options leverage and decay.** Many calls were options plays, but only the underlying's direction was graded. A -10% to -30% move in the underlying over 20 days usually means a near-total loss on short-dated calls, from both delta and theta. Even flat underlyings lose premium to time decay. So for the losing O, M and C calls, **these underlying returns understate the real losses**. The few winners would have been magnified, but they were rare at the 5- and 20-day horizons that matter for options.
5. **No proper risk adjustment.** The comparison is against SPY only. Most of these names are far more volatile than SPY, so a beta-adjusted benchmark would change the numbers somewhat. In a flat-to-down tape, though, it would not change the verdict that the calls did not add value.
6. **Classification is subjective.** Styles were assigned from short posts, and calls with more than one tag are counted in each group.

## Plain-English takeaway

**No style showed a real edge in this sample.**

- **Options flow / gamma / net premium** was the worst-performing large group. Its median call was down 18% after a month, only 3 of 20 beat SPY at that point, and the ones that later paid off (MRNA, AMD) were underwater during any window an options holder would realistically have held. Because of leverage and decay, the actual option trades were probably worse than these numbers show.
- **Momentum / volume-spike** calls did even worse. All five lagged SPY at +20 and +60 days, two of the names were later delisted, and the median call was down 86% to date. Buying the day after a 4–5x volume spike in a sub-$3 stock was buying the top.
- **Chart-pattern** calls lost less than those two groups but still lagged SPY about 80–90% of the time at every horizon.
- **Fundamental** write-ups lost the least in the short run. That is not evidence of skill: most of the group was low-volatility Treasury ETFs that simply moved less than stocks during a small dip. The actual theses (bonds rally on cuts, TCEHY, RBLX, BGIN) were all behind SPY at 60 days and are behind it today.

If there is anything to take from this, it is negative. Short-term calls in hot, high-beta names, whatever reasoning is attached, were mostly bought near a local top. Posted targets say little: most hits came during squeezes already under way or were trivially close to entry. Tracking these calls longer, and on more than one market regime, would be needed before crediting any style with skill.
