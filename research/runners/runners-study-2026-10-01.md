# What do +100% microcap runners have in common, and how much does that matter?

Study date: 2026-10-01. Data: Massive grouped daily bars (unadjusted, OTC excluded) for **all 501 NYSE trading days from 2024-10-01 to 2026-09-30, with no sampling**, plus Massive split records and SEC EDGAR (submissions and dei shares outstanding). Files in this folder: `events.csv` (1,136 runner events), `controls.csv` (11,360 control stock-days). Scripts and intermediate files are in `work/`.

## Short answer

1. **Runners are tiny, already-beaten-down, sub-$1 to $3 stocks, and roughly 3 in 4 of them had no company filing before the move.** The traits that really separate them from look-alikes are: **a volume spike the day before** (lift 8.9x), **a market cap under $10M or under 5M shares** (3.0x to 3.5x), **a crash over the prior 5 or 20 days** (3.2x to 3.9x), **a reverse split in the prior 90 days** (3.5x) and **a sub-$1 price** (2.7x). Being biotech, being "crypto" by name, being a SPAC, or having an S-3 shelf on file barely separates them (lift 0.7x to 1.2x). Those traits are common, not predictive.
2. **Even the best combination of traits rarely produces a runner.** Of sub-$3 stocks that did a reverse split in the prior 90 days and had a 5x volume day, **2.4% ran +100% the next day and 11.8% within 20 trading days**. For the typical sub-$3 stock the next-day rate is 0.15%. The best traits raise the odds about 16-fold, from very unlikely to still unlikely.
3. **The edge is in the fade, and a cash account can't short it.** From the close at the end of the run, the median runner is **-12.8% the next day, -23.1% after 5 days and -39.1% after 20 days**, and only 17.9% are higher after 20 days. Buying the open after a 50%+ gap loses money on the median (-29.8% after 5 days). For a long-only cash account, the practical lesson is to sell into the spike and never chase or hold it. There isn't a long trade here that the data supports.

## Method

**Runner event (step 1).** A US common stock (Massive ticker type CS, taken as the union of 9 point-in-time snapshots between 2024-10-01 and 2026-09-29, which keeps names that later delisted) qualifies if `close / prior close >= 2.0`, or `close at t+1 / close at t-1 >= 2.0` (+100% over two sessions). "Prior close" is always the **immediately preceding NYSE trading day**. The panel is built on the full exchange calendar, so a missing day can never be bridged. In the end no day was missing (501/501 downloaded). Prices are split-adjusted with Massive split factors before computing ratios. **Any day within 2 trading days of a recorded split is excluded**, so a reverse split can't show up as a fake +100% day. If a 2-day window qualifies only because day 2 was itself +100%, the event is dated to day 2. One event per ticker per 10 trading days.
Result: **1,136 events in 824 tickers, 2024-10-02 to 2026-09-29**, roughly 24 to 83 a month. That's more than the "few hundred" expected, because 2024 to 2026 was a busy period for microcap runners.
- 791 were 1-day +100% moves. The rest qualified only on the 2-day rule.
- Median day-of dollar volume was $247M, so these were not thin prints.
- 54 events were flagged by a heuristic for a possible *unrecorded* split: the whole day traded at 1.8x or more the prior close, with a ratio near a common split ratio. Yahoo split history was checked for all of them: one (ILLR) had a split 2 days earlier and is now excluded by the 2-day rule, one had a split 9 trading days earlier, and the rest showed no split. They are kept and marked `suspect_split` in `events.csv`.

**Controls (step 2).** For each event day, 10 random common stocks that did **not** run within ±10 trading days. Each had to have a prior close under $10, trade on both days, and have a **prior-day dollar volume within 2x of the runner's** (the band was widened for only 50 of 11,360). Matching on dollar volume means dollar volume has no lift by construction. Controls are all under $10, so the ">$10" bucket has no controls (71 runners, 6.2%, started above $10).

**Features (step 3).** All features are measured as of the prior close unless marked day-of.
- Sources: SEC submissions JSON, a ticker-to-CIK map (Massive CIK first, then SEC company_tickers), and dei EntityCommonStockSharesOutstanding (the latest value filed before the run, adjusted for splits since, and dropped if more than 15 months old).
- SEC data was found for 97.9% of runners and 97.2% of controls. Share counts were usable for 77% of runners and 79% of controls.
- SEC acceptance timestamps are UTC (they peak at 20-21Z, i.e. 4-5pm ET) and were converted to New York time. "Day-of filing" means accepted after 4:00pm ET on the prior day or before 4:00pm ET on the run day.

## Lift table (step 4)

Lift = % of runners with the trait ÷ % of matched controls with it. The denominators differ when data was missing.

| Group | Feature | Runners | % runners | Controls | % controls | **Lift** |
|---|---|---|---|---|---|---|
| Price | prior close < $1 | 502/1136 | 44.2% | 1858/11360 | 16.4% | **2.70x** |
| Price | prior close $1-3 | 363/1136 | 32.0% | 3678/11360 | 32.4% | 0.99x |
| Price | prior close $3-10 | 200/1136 | 17.6% | 5824/11360 | 51.3% | 0.34x |
| Price | prior close > $10 | 71/1136 | 6.2% | 0 (controls are <$10 by design) | 0% | n/a |
| Size | shares outstanding < 5M | 345/874 | 39.5% | 1174/8959 | 13.1% | **3.01x** |
| Size | shares outstanding 5-20M | 240/874 | 27.5% | 2001/8959 | 22.3% | 1.23x |
| Size | shares outstanding >= 20M | 289/874 | 33.1% | 5784/8959 | 64.6% | 0.51x |
| Size | market cap < $10M | 514/874 | 58.8% | 1504/8959 | 16.8% | **3.50x** |
| Size | market cap $10-50M | 195/874 | 22.3% | 1971/8959 | 22.0% | 1.01x |
| Size | market cap $50-300M | 114/874 | 13.0% | 2801/8959 | 31.3% | 0.42x |
| Size | market cap >= $300M | 51/874 | 5.8% | 2683/8959 | 29.9% | 0.19x |
| Momentum | prior 5d return <= -20% | 213/1098 | 19.4% | 553/11186 | 4.9% | **3.92x** |
| Momentum | prior 5d return >= +20% | 176/1098 | 16.0% | 614/11186 | 5.5% | **2.92x** |
| Momentum | prior 20d return <= -30% | 347/1050 | 33.0% | 1099/10754 | 10.2% | **3.23x** |
| Momentum | prior 20d return >= +30% | 121/1050 | 11.5% | 890/10754 | 8.3% | 1.39x |
| Volume | prior-day volume >= 2x 20d avg | 394/1064 | 37.0% | 1111/10838 | 10.3% | **3.61x** |
| Volume | prior-day volume >= 5x 20d avg | 268/1064 | 25.2% | 306/10838 | 2.8% | **8.92x** |
| Volume | prior-day volume <= 0.5x 20d avg | 292/1064 | 27.4% | 3042/10838 | 28.1% | 0.98x |
| Structure | reverse split in prior 90d (median ratio 1-for-18) | 186/1136 | 16.4% | 529/11360 | 4.7% | **3.52x** |
| Structure | IPO/listing filing (8-A12B/8-A12G/424B4) in prior 365d | 290/1112 | 26.1% | 1661/11046 | 15.0% | 1.73x |
| Structure | first traded in this dataset < 1y earlier (events from 2025-03 on) | 188/869 | 21.6% | 1064/8690 | 12.2% | 1.77x |
| Origin | HQ China / Hong Kong | 85/1112 | 7.6% | 445/11046 | 4.0% | 1.90x |
| Origin | HQ outside US | 430/1112 | 38.7% | 3026/11046 | 27.4% | 1.41x |
| Origin | foreign private issuer (files 20-F/6-K) | 411/1112 | 37.0% | 2905/11046 | 26.3% | 1.41x |
| Sector | biotech/pharma/medtech | 320/1112 | 28.8% | 3004/11046 | 27.2% | 1.06x |
| Sector | tech/software/semis/telecom | 203/1112 | 18.3% | 1646/11046 | 14.9% | 1.23x |
| Sector | shipping | 7/1112 | 0.6% | 139/11046 | 1.3% | 0.50x |
| Sector | finance/real estate | 98/1112 | 8.8% | 988/11046 | 8.9% | 0.99x |
| Sector | mining/energy | 20/1112 | 1.8% | 630/11046 | 5.7% | 0.32x |
| Sector | blank check (SPAC) | 8/1112 | 0.7% | 81/11046 | 0.7% | 0.98x |
| Sector | crypto/blockchain in name or SIC text | 16/1112 | 1.4% | 221/11046 | 2.0% | 0.72x |
| Dilution capacity | any S-1/S-3/F-1/F-3/424B in prior 90d | 500/1112 | 45.0% | 3244/11046 | 29.4% | 1.53x |
| Dilution capacity | S-3/F-3 shelf in prior 90d | 136/1112 | 12.2% | 1127/11046 | 10.2% | 1.20x |
| Dilution capacity | S-1/F-1 in prior 90d | 237/1112 | 21.3% | 923/11046 | 8.4% | **2.55x** |
| Dilution capacity | 424B prospectus in prior 90d | 363/1112 | 32.6% | 2443/11046 | 22.1% | 1.48x |
| Insiders | Form 4 in prior 90d | 406/1112 | 36.5% | 6368/11046 | 57.6% | 0.63x |
| Day-of | 8-K or 6-K filed run day / prior evening | 325/1112 | 29.2% | 621/11046 | 5.6% | **5.20x** |
| Day-of | 8-K item 1.01 (material agreement) | 119/1112 | 10.7% | 79/11046 | 0.7% | **14.96x** |
| Day-of | 8-K item 8.01 (other events) | 108/1112 | 9.7% | 87/11046 | 0.8% | **12.33x** |
| Day-of | 8-K item 7.01 (Reg FD / press release) | 111/1112 | 10.0% | 123/11046 | 1.1% | **8.96x** |
| Day-of | 8-K item 2.02 (earnings) | 32/1112 | 2.9% | 102/11046 | 0.9% | 3.12x |
| Day-of | 8-K item 3.01 (listing deficiency) | 7/1112 | 0.6% | 29/11046 | 0.3% | 2.40x |
| Day-of | offering filing (S-x/F-x/424B/EFFECT) on run day | 53/1112 | 4.8% | 132/11046 | 1.2% | 3.99x |
| **After** | **S-1/S-3/F-1/F-3/424B/EFFECT within 10 days AFTER** | 272/1112 | **24.5%** | 726/11046 | 6.6% | **3.72x** |

Medians, runners vs controls:
- Prior close: $1.23 vs $3.10.
- Market cap: $7.3M (n=874) vs $94M (n=8,959).
- Shares outstanding: 8.5M vs 37.8M.
- Prior 20-day return: -14.8% vs -3.6%.
- Prior-day relative volume: 1.11x vs 0.76x.

**Catalysts for runners.** These come from keyword classification of the day-of 8-K/6-K exhibit text. It is approximate: a spot check found some misclassified headlines.

| Catalyst | n | % of runners | median +20d return |
|---|---|---|---|
| **No 8-K/6-K on the run day or prior evening** | 811 | **71.4%** | -41.5% |
| FDA / clinical | 73 | 6.4% | -15.2% |
| Financing / listing compliance / reverse split | 64 | 5.6% | -44.2% |
| Other / unclear | 55 | 4.8% | -45.4% |
| Merger / acquisition / buyout | 48 | 4.2% | -36.7% |
| Earnings / business update | 28 | 2.5% | -3.1% |
| Crypto treasury / digital assets | 28 | 2.5% | -19.7% |
| AI pivot / AI product | 16 | 1.4% | -29.6% |
| Contract / partnership | 13 | 1.1% | -34.0% |

The 71% with no filing may still have had a newswire release, social media promotion, or no news at all. No news feed was checked, so "none found" means "no SEC filing", not "no catalyst".

## Day-of shape: did they fade during the session?

Across the 1,136 runners:
- Median 1-day move: 2.23x.
- 47.5% opened already +50% or more above the prior close (median gap at the open: +40%). Much of the move happens before a cash-account trader can buy at the open.
- Median close / intraday high = 0.82. 25.8% closed at 70% of the high or lower, and 20.3% closed below their own open.
- The fade during the day predicts the next day: runners that closed at ≤70% of their high had a median next-day return of -17.9%, versus -7.3% for the 372 that closed within 10% of the high.

## What happens after (the most important table)

Returns from the close at the end of the run (day t for 1-day events, t+1 for 2-day events), split-adjusted. Stocks that stopped trading count at their last close: 40 are marked `stale_last_close` at the +20d horizon and 6 had no trades after the run.

| Group | Horizon | n | Median | % positive | Mean | % down ≥50% | % up ≥100% |
|---|---|---|---|---|---|---|---|
| Runners | +1d | 1128 | **-12.8%** | 30.3% | -4.6% | 6.0% | 2.9% |
| Runners | +5d | 1120 | **-23.1%** | 27.8% | -9.7% | 17.4% | 4.1% |
| Runners | +20d | 1093 | **-39.1%** | **17.9%** | -21.9% | 34.9% | 3.0% |
| Controls | +1d | 11324 | -0.2% | 45.2% | -0.0% | 0.1% | 0.0% |
| Controls | +5d | 11272 | -0.7% | 44.8% | -0.3% | 0.4% | 0.1% |
| Controls | +20d | 11003 | -2.7% | 42.6% | -0.5% | 2.9% | 1.1% |
| Runners bought at the next day's open | +5d | 1103 | -15.9% | 30.7% | -5.4% | 9.6% | 4.0% |
| Runners bought at the next day's open | +20d | 1048 | -33.4% | 20.0% | -16.5% | 27.7% | 3.0% |

**Dilution follows the run.**
- 24.5% of runners filed an S-1/S-3/F-1/F-3/424B/EFFECT within 10 calendar days after the run, versus 6.6% of controls (3.7x). The most common filing was the 424B5 (146 filings).
- Runners that filed one had a median +20d return of -48.3% (n=266), versus -37.2% for those that didn't (n=805).
- The fade is the same in every subgroup:
  - Year: -37.7% in 2024, -37.7% in 2025, -43.3% in 2026.
  - Price bucket: -28.8% for >$10, -42.1% for <$1.
  - Reverse split: -45.5% after a recent reverse split, -38.1% without one.
  - Filing on the run day: -33.3% with a day-of filing, -41.6% without.
  - Prior-day volume of 5x or more: -45.3%.
- Earnings-driven (-3.1%) and FDA/clinical (-15.2%) runs held up best, but the samples are small (28 and 73).

## Conditional probabilities: how rare is a runner even with the best traits?

These come from the **whole universe**: 2,722,284 CS stock-days with a valid prior close, excluding split windows. "Ran next day" means a +100% move (1-day or 2-day rule) **started** on that day, counting only the first day of a cluster. Price, volume and reverse-split traits are known at the prior close.

| Condition at prior close | stock-days | runs next day | **P(run next day)** | **P(run within 20 trading days)** |
|---|---|---|---|---|
| all CS stock-days | 2,722,284 | 1,124 | 0.041% | 0.77% |
| prior close < $1 | 198,056 | 498 | 0.25% | 4.6% |
| prior close $1-3 | 376,492 | 360 | 0.10% | 1.9% |
| prior close $3-10 | 521,880 | 196 | 0.04% | 0.68% |
| prior close > $10 | 1,625,856 | 70 | 0.004% | 0.07% |
| prior close < $3 | 574,548 | 858 | 0.15% | 2.8% |
| reverse split in prior 90d | 75,148 | 180 | 0.24% | 4.2% |
| **< $3 & reverse split in prior 90d** | 27,276 | 110 | **0.40%** | **7.1%** |
| < $1 & reverse split in prior 90d | 4,647 | 29 | 0.62% | 11.1% |
| prior-day volume ≥ 5x avg | 40,244 | 278 | 0.69% | 3.3% |
| < $1 & prior-day volume ≥ 5x | 7,805 | 135 | 1.73% | 8.4% |
| < $3 & prior-day volume ≥ 3x | 32,515 | 271 | 0.83% | 5.1% |
| < $3 & 20d return ≤ -50% | 25,875 | 176 | 0.68% | 9.1% |
| < $3 & 5d return ≥ +20% | 31,227 | 127 | 0.41% | 3.8% |
| < $3 & reverse split 90d & 20d return ≤ -30% | 12,279 | 64 | 0.52% | 9.4% |
| < $3 & reverse split 90d & prior-day volume ≥ 3x | 1,902 | 35 | 1.84% | 11.0% |
| **< $3 & reverse split 90d & prior-day volume ≥ 5x** | 1,285 | 31 | **2.41%** | **11.8%** |

**Pre-open news**, from all 8-K/6-K filings in the SEC data. This table covers only the 5,828 tickers with a downloaded SEC file. A filing counts if it was accepted after the prior close or before 9:30 ET, so it was knowable before the open.

| Condition | stock-days | ran that day | P(run) |
|---|---|---|---|
| any price, filing before the open | 110,524 | 269 | 0.24% |
| < $3, filing before the open | 28,149 | 180 | 0.64% |
| < $1, filing before the open | 10,827 | 95 | 0.88% |
| < $3, **no** filing before the open | 496,088 | 568 | 0.11% |

Of the 976 run starts in that ticker set, 27.6% had a filing before the open. Most runners had no pre-open filing, and more than 99% of pre-open filings by sub-$3 companies did *not* produce a run.

## Conclusions in plain English

**What actually predicts a run (high lift):**
- A **volume spike the day before** (5x the 20-day average: 8.9x lift). This is the strongest pre-move signal. Often it is the first leg of the move or news leaking out.
- **Tiny float or market cap** (under 5M shares: 3.0x; market cap under $10M: 3.5x).
- **A recent crash** (5-day return of -20% or worse: 3.9x; 20-day return of -30% or worse: 3.2x).
- **A reverse split in the prior 90 days** (3.5x; median ratio 1-for-18).
- **A sub-$1 price** (2.7x).
- **An S-1/F-1 on file in the prior 90 days** (2.6x). This is usually a company that has just IPO'd or is raising money.
- Moderate: a listing in the past year (1.7x), China/HK HQ (1.9x), foreign private issuer status (1.4x), any recent registration or prospectus (1.5x).

On the day itself, an 8-K with item 1.01, 8.01 or 7.01 has a big lift (9x to 15x), but most of those are only visible on the day, and most runs had no filing at all.

**What is common but not predictive (lift near 1):**
- Biotech (29% of runners, but 27% of controls).
- $1-3 price (32% vs 32%).
- Having an S-3 shelf (12% vs 10%).
- Being a SPAC.
- "Crypto" in the name or SIC (0.7x).
- Low prior volume.

Shipping and mining/energy were *under*-represented. A list of what runners "have in common" would put biotech and shelf registrations at the top, and that would be misleading.

**How rare is it?** Even in the best bucket (sub-$3, a recent reverse split and a 5x volume day), about **1 in 40** stock-days ran the next day and about **1 in 8.5** ran within 20 trading days. In the broader "sub-$3 with a recent reverse split" bucket, it's 1 in 250 next day and 1 in 14 over 20 days. These traits make a good watchlist filter but a poor signal to buy before the move.

**The run or the fade?**
- **The run itself is mostly not capturable from a cash account.** Half the runners had already gapped up 40% or more by the open. Buying any sub-$10 stock that opened up 50-100% had a median open-to-close return of -10.8%, and it closed up on the day only 28% of the time. Buying a 50%+ gap at the open and holding 5 days had a median return of -29.8% (only 20% were higher).
- **The reliable pattern is the fade**: median -12.8% next day, -23.1% after 5 days, -39.1% after 20 days, with 35% losing half or more within a month. A dilutive filing often follows within 10 days (1 in 4).
- A cash account can't short, so the fade is not directly tradeable. The practical value is defensive: **if you hold a runner, sell into the spike. Don't buy the day after. Treat a new 424B5/S-1/EFFECT as an exit signal.**
- The rare runner that keeps going (3% doubled again within 20 days) can't be told apart in advance with these features.

## Caveats (survivorship, data, method)

- **Survivorship.** The universe is the union of 9 point-in-time CS lists, and the price data includes stocks that later delisted, so delisted runners are in the sample. Post-run returns for stocks that stopped trading use their last close (40 at +20d), which probably *understates* their losses. Six events had no trades at all after the run.
- **Adjusted vs actual prices.** Detection and returns use split-adjusted prices built from Massive split records applied to the unadjusted bars. `prior_close_raw` and `day_*_raw` in `events.csv` are the real traded prices. Unrecorded splits are a residual risk: 54 suspect events were checked against Yahoo, and 1 is now excluded. The `day_open/high/close` columns without `_raw` are on an adjusted basis.
- **No sampling of days.** All 501 trading days were downloaded. The 10-day dedup means base rates count the start of each run cluster only.
- **Universe definition.** Massive type CS only, so **ADRs (ADRC) and OTC are excluded**, and some foreign runners trade as ADRs. 141 tickers in events/controls could not be mapped to a CIK. The page-5 rows of 8 ticker snapshots (about 150 rows each, tickers near the end of the alphabet) were transcribed by hand from inline API responses, so a few type labels could be wrong.
- **Controls** are matched on prior-day dollar volume and limited to stocks under $10. That makes dollar-volume lift about 1 by design and leaves the >$10 bucket without controls. The lift figures compare runners with *liquid sub-$10 look-alikes*. The universe conditional probabilities are not matched.
- **SEC features.** Share counts come from dei cover-page values (stale or missing for about 22%). "Listing in the past year" uses 8-A/424B4 filing dates as a proxy. The submissions "recent" list was supplemented with older pages only when it didn't reach back to 2024-06.
- **Catalysts** are keyword-classified from exhibit text and are approximate. The 71% "no filing" group was not checked against newswires or social media.
- **No significance tests.** Small cells (e.g. SPAC n=8, shipping n=7, item 3.01 n=7) should be treated as noise.
- **No costs** are included. On sub-$1 runners the spreads are large and borrow is often unavailable, so even short-sellers would struggle to collect the full fade.

## Files

- `events.csv`: one row per runner, with price features, SEC features, catalyst and forward returns.
- `controls.csv`: 10 matched controls per event, with the same features (`event_ticker` links each control to its event).
- `work/build_panel.py`: detection, controls, universe base rates (`work/universe_rates.csv`).
- `work/sec_features.py`: SEC features.
- `work/catalysts.py`: catalyst classification.
- `work/analyze.py`: lift table (`work/lift_table.csv`, `work/results.md`).
- `work/extra.py`: gap-up and pre-open-filing analyses (`work/extra.md`).
- `work/raw/`: 501 daily CSVs. `work/ref/`: ticker lists and splits. `work/sec/`: cached EDGAR JSON.
