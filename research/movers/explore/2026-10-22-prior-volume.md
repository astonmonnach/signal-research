# Exploration only (rule 2026-10-06): seven sessions, not a test

**Question.** When a US stock trades a "quiet" volume spike (big volume, small price move) one day, how often does it jump the next day? Or turned round: how many quiet spikes market-wide did *not* jump? Prompted by the movers log (`research/movers/movers.csv`, 70 rows, 13 to 21 Oct 2026), where several top-10 gainers had a quiet spike the day before.

**Short answer.** Over the 7 sessions there were 539 quiet spikes at 5x. 520 of them had a next-session bar, and **6 of those 520 rose 20% or more (1.15%)**, so 514 did not. Stocks without a signal rose 20%+ 0.22% of the time, which makes a signal about 5x more likely to jump. It was also about 8x more likely to *fall* 20%+ (2.31% against 0.30%), and its mean next-session return was -1.23%. Five of the six hits were really after-hours news reactions. In each of those five, most of the signal-day volume traded after the 4pm close, and the price had already moved after hours. So the daily bar looked "quiet" only because its close is set at 4pm.

## Data

- Massive grouped daily bars (`/v2/aggs/grouped/locale/us/market/stocks/{date}`, `adjusted=true`, no OTC), one call per session: 28 sessions from 14 Sep to 21 Oct 2026. All 28 loaded, with 12,562 to 12,683 bars each. None failed.
- **12 Oct 2026 (Columbus Day) was a trading day.** The market was open and the bars returned 12,602 rows. So the signal day for the 13 Oct outcome is 12 Oct, not 9 Oct.
- Ticker types come from Massive `/v3/reference/tickers` as of 12 Oct. The list is types `CS` (common stock) and `ADRC` (ADRs, which the movers log also counts), on primary exchanges XNAS, XNYS, XASE and BATS. ARCX returned no CS. That gives 5,692 tickers. ETFs, warrants, units, rights and preferreds are dropped because they are not on the list, so no suffix rule was needed.
- Massive split list, 14 Sep to 22 Oct: the adjusted bars already reflect listed splits (checked on AMTD 1-for-60 and SHFS 1-for-12).

## Definitions (fixed before any result was seen)

- **Universe on day S:** a stock on the CS/ADRC list, with an S close of $0.50 or more and S volume of 50,000 shares or more. It also needs a bar on the session before S (for the move) and bars on at least 15 of the 20 sessions before S.
- **Signal on S:** S volume of at least 5x the **median** volume of the 20 sessions before S, with the S close-to-close move between -10% and +10% (inclusive). A session with no bar counts as zero volume in the median. The 10x version is the same with 10x.
- **Outcome on N (the next session):** close-to-close return N close / S close - 1, and open gap N open / S close - 1. A signal with no bar on N is counted as fired but left out of the return statistics.
- **Signal days:** 12, 13, 14, 15, 16, 19 and 20 Oct, which give outcomes on 13, 14, 15, 16, 19, 20 and 21 Oct.

## Results at 5x

| S -> N | Universe | Signals (with N bar) | N +20% | N +30% | N -20% | Median N | Mean N | No-signal stocks (with N bar) | No-signal +20% | No-signal +30% | No-signal median / mean | Logged top-10 gainers in signal set |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 12 Oct -> 13 Oct | 4,201 | 53 (51) | 0 | 0 | 2 | -2.41% | -3.72% | 4,148 (4,146) | 16 | 9 | -0.29% / -0.76% | 0 |
| 13 Oct -> 14 Oct | 4,266 | 71 (70) | 2 | 2 | 4 | -0.32% | -2.34% | 4,195 (4,195) | 5 | 3 | -1.46% / -2.30% | 2: TDIC, AEHL |
| 14 Oct -> 15 Oct | 4,343 | 92 (88) | 0 | 0 | 1 | 0.00% | +0.07% | 4,251 (4,249) | 9 | 3 | +1.46% / +1.59% | 0 |
| 15 Oct -> 16 Oct | 4,266 | 97 (93) | 1 (TCRT, not top-10) | 0 | 4 | -0.10% | -2.43% | 4,169 (4,168) | 3 | 1 | -1.30% / -2.06% | 0 |
| 16 Oct -> 19 Oct | 4,228 | 69 (68) | 1 | 1 | 1 | 0.00% | -0.60% | 4,159 (4,157) | 11 | 7 | -0.34% / -0.25% | 1: AAME |
| 19 Oct -> 20 Oct | 4,220 | 79 (77) | 0 | 0 | 0 | 0.00% | -0.55% | 4,141 (4,140) | 10 | 4 | +1.24% / +1.32% | 0 |
| 20 Oct -> 21 Oct | 4,188 | 78 (73) | 2 | 2 | 0 | 0.00% | +0.22% | 4,110 (4,110) | 9 | 8 | +0.03% / +0.29% | 2: SPHL, AHT |
| **Total** | **29,712** | **539 (520)** | **6** | **5** | **12** | **-0.01%** | **-1.23%** | **29,173 (29,165)** | **63** | **35** | **-0.09% / -0.31%** | **5 of 70** |

- **Signals:** +20% in 6/520 (1.15%), +30% in 5/520 (0.96%), -20% in 12/520 (2.31%). Median open gap 0.00%, mean -0.33%. 5 opened 20%+ up.
- **No signal (the base rate):** +20% in 63/29,165 (0.22%), +30% in 35/29,165 (0.12%), -20% in 88/29,165 (0.30%).
- **Did not jump (the false alarms):** 514 of 520 did not reach +20%, and 515 did not reach +30%. Another 19 signals had no bar on N; 15 of them were SPACs.

## Results at 10x

| S -> N | Signals (with N bar) | N +20% | N +30% | N -20% | Median N | Mean N | No-signal stocks (with N bar) | No-signal +20% | No-signal +30% | Logged top-10 gainers in signal set |
|---|---|---|---|---|---|---|---|---|---|---|
| 12 Oct -> 13 Oct | 32 (30) | 0 | 0 | 1 | -1.06% | -3.70% | 4,169 (4,167) | 16 | 9 | 0 |
| 13 Oct -> 14 Oct | 39 (38) | 1 | 1 | 3 | -0.09% | -1.79% | 4,227 (4,227) | 6 | 4 | 1: AEHL |
| 14 Oct -> 15 Oct | 46 (43) | 0 | 0 | 1 | 0.00% | +0.03% | 4,297 (4,294) | 9 | 3 | 0 |
| 15 Oct -> 16 Oct | 65 (62) | 1 (TCRT) | 0 | 4 | -0.09% | -2.41% | 4,201 (4,199) | 3 | 1 | 0 |
| 16 Oct -> 19 Oct | 44 (43) | 1 | 1 | 0 | 0.00% | +0.14% | 4,184 (4,182) | 11 | 7 | 1: AAME |
| 19 Oct -> 20 Oct | 40 (38) | 0 | 0 | 0 | 0.00% | -1.02% | 4,180 (4,179) | 10 | 4 | 0 |
| 20 Oct -> 21 Oct | 40 (36) | 2 | 2 | 0 | 0.00% | +0.63% | 4,148 (4,147) | 9 | 8 | 2: SPHL, AHT |
| **Total** | **306 (290)** | **5** | **4** | **9** | **0.00%** | **-1.16%** | **29,406 (29,395)** | **64** | **36** | **4 of 70** |

- **Signals:** +20% in 5/290 (1.72%), +30% in 4/290 (1.38%), -20% in 9/290 (3.10%). So 285 of 290 did not jump 20%.
- **No signal:** +20% in 64/29,395 (0.22%), +30% in 36/29,395 (0.12%).

## The six hits, and where their signal-day volume traded

Volume splits come from Massive 30-minute bars for the signal day (extended hours included). The SPHL and AHT splits are copied from their movers.csv notes.

| N | Ticker | S vol / median | S move | S close | N open gap | N close-to-close | N open to close | Signal-day volume |
|---|---|---|---|---|---|---|---|---|
| 14 Oct | TDIC | 5.1x | -5.2% | 1.63 | +3.1% | +39.9% | +35.7% | 152k of ~201k (30-minute sum) pre-market on 13 Oct (high $1.85); 43k in regular hours |
| 14 Oct | AEHL | 34.4x | -7.8% | 8.55 | +183.0% | +34.4% | -52.5% | 3.33M of ~3.37M **after the 4pm close**, at $8.99-$22.72 after hours |
| 16 Oct | TCRT | 96.3x | +5.3% | 2.18 | +28.9% | +20.6% | -6.4% | 12.3M of ~16.6M **after the close** (last $2.85); 3.8M in regular hours |
| 19 Oct | AAME | 47.1x | -0.9% | 1.05 | +33.3% | +38.1% | +3.6% | 543k **after the close** (10-K filed after the close; last $1.26); 6.2k in regular hours |
| 21 Oct | SPHL | 254.2x | +8.0% | 2.43 | +18.1% | +45.7% | +23.3% | 3.99M of 4.0M **after the 4pm close**, to $3.16 |
| 21 Oct | AHT | 325.3x | -2.7% | 1.79 | +33.5% | +38.0% | +3.3% | 4.84M from 6pm, **after a 6:15pm release**, up to $2.99 |

Only TDIC's spike happened before the 4pm close. Five of the six opened on N 18% or more above the S close, four of them by 20% or more.

## Context

- **The 69 universe stock-days that rose 20%+ on N:** 6 had a quiet 5x spike the day before (9%), 19 had a 5x spike with a move bigger than 10% (28%), and 44 had no 5x volume at all (64%).
- **"Loud" 5x spikes (S move beyond ±10%), for comparison only:** 289 of them, and 19 of the 287 with an N bar rose 20%+ (6.6%). But 25 fell 20%+ (8.7%), and the mean N return was -2.29%.
- **SPACs:** 131 of the 539 5x signals (103 of the 306 at 10x) were SPACs, judged by "Acquisition", "SPAC" or "Merger Corp" in the Massive name. They explain the 0.00% medians. Without them: 6/404 rose 20%+ at 5x (1.49%), with median -0.23% and mean -1.57%; 5/199 at 10x (2.51%). This is a description only; the fixed definition keeps SPACs in.
- **The movers log's top-10 gainers and this universe:** only 38 of the 70 logged gainers were in the universe on their S day. The other 32 were out because they were under $0.50, under 50,000 shares on S, had fewer than 15 history bars, or had no S bar. Several of the log's quiet spikes are among those excluded:
  - HODO (85x), SHFS (265x), BDRX (103x) and SXTC (319x): under $0.50.
  - ILAG (26.6x): 16,581 shares on S.
  - SAIQ (7.1x, +7.9%): 11 of 20 bars; it rose +100.6% on 20 Oct.

  So the log's "about 9 quiet spikes" and this universe are not the same group. The log also used a 20-day *average*, where this uses the median.

## Data limitations

1. **Extended hours are inside the daily bars.** Massive daily volume includes pre-market and after-hours trading, but the close is the 4pm close. A stock that reacts to news after 4pm shows huge volume with a "quiet" close, even though the after-hours price has already jumped. Five of the six hits were like this. How many of the 514 false alarms had their volume before 4pm (in regular or pre-market trading) was not measured. That would need intraday bars for every stock, and the free tier allows about 5 calls a minute.
2. **The type filter is a snapshot as of 12 Oct.** Stocks listed or renamed after 12 Oct are missing (IAM on 16 Oct had no history anyway). A few odd entries in Massive's CS/ADRC lists were kept: PSNYW listed as ADRC, and some preferred or note tickers listed as CS (WAFDP, WHLRL, XELLL). None of them is a hit.
3. **History rule.** The 15-of-20-bar rule and the zero-volume rule for missing sessions drop new and very thin listings (PFAI 13 bars, SAIQ 11, WORX 7-8).
4. **Share-count changes missing from the split list are not adjusted.** POM's ADS-to-share change on 21 Oct shows as +352.8% instead of the real +35.8%. It is a 20%+ day either way. It sits in the no-signal group (1.6x) and lifts the 21 Oct no-signal mean by under 0.1 point. No other next-session move of 100% or more looked like an artefact (TCRT +189% on 13 Oct and SLN +126% on 19 Oct are real).
5. **This is a small sample: seven sessions in one market spell.** Days are not independent, there are only 6 hits, costs are ignored, and the S-close return is not tradeable for spikes that happen after 4pm. This is a description, not a test.
