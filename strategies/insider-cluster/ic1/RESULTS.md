# IC1 results: insider cluster buying

Run of the study in `../PREREG_IC1.md` (git a90d629), built by `run.py` on 2026-10-14. Every number below is printed by that script. Returns are after the 1% round-trip cost on the signal stock. "Excess" is the signal return after costs minus the average return of its matched controls.

## Verdicts

**T1, does the cluster filter pay? DOES NOT PAY.**

| Group | n | Mean | Median | % positive | 95% interval (mean) |
|---|---|---|---|---|---|
| All tested signals, 60-session excess | 1527 | +1.20% | -3.02% | 45.1% | -0.67% to +3.03% |
| First half (2024-10-01 to 2025-06-30) | 741 | +2.13% | -2.69% | 45.7% | -0.50% to +4.96% |
| Second half (2025-07-01 to 2026-03-31) | 786 | +0.32% | -3.45% | 44.4% | -2.19% to +2.97% |

Pass marks: mean above zero (yes); 95% interval above zero (no); median above zero (no); same sign in both halves (yes). All four are needed.

In plain words: following every cluster did not beat similar stocks by a margin we can trust; the interval includes zero and the median is not above zero. The typical signal trailed its controls, and fewer than half beat them. A minority of large winners lifts the mean.

**T2, are small companies stronger? SEPARATES.**

| Group | n | Mean | Median | % positive | 95% interval (mean) |
|---|---|---|---|---|---|
| Market value under $300M | 421 | +6.18% | +0.08% | 50.4% | +1.56% to +10.96% |
| Market value $300M or more | 848 | -0.84% | -3.33% | 44.1% | -2.69% to +1.09% |

Difference (small minus large): +7.02%, 95% interval +2.07% to +12.05% (2000 usable bootstrap draws). Pass mark: interval above zero. 258 tested signals had no usable share count and are left out of T2.

In plain words: clusters in companies under $300M did better against their controls than clusters in larger companies, and the gap clears the pass mark. T2 only compares the two groups; it does not show that the small group pays on its own (its median excess is +0.08% and 50.4% beat their controls).

**T3, do bigger clusters carry more signal? DOES NOT SEPARATE.**

| Group | n | Mean | Median | % positive | 95% interval (mean) |
|---|---|---|---|---|---|
| Cluster worth $250k or more | 838 | -0.40% | -3.61% | 42.2% | -2.71% to +1.97% |
| Cluster worth under $250k | 689 | +3.15% | -1.45% | 48.5% | +0.51% to +5.82% |

Difference (big minus small): -3.55%, 95% interval -6.96% to -0.19% (2000 usable bootstrap draws). Pass mark: interval above zero.

In plain words: bigger clusters did not carry more signal. The gap went the other way: clusters under $250k did better than bigger ones, and that interval sits below zero.

Three tests were run. If none of the three effects were real, each 95% interval would still sit wholly above zero about 2.5% of the time, so the chance that at least one of the three does by luck alone is about 7% (1 - 0.975^3, treating them as independent).

Self-consistency check: for every group in this file, (wins / n) x average win minus (losses / n) x average loss equals the mean to within 1e-9. It ran on 27 groups and passed on all of them. For T1: 688 wins averaging +26.89%, 839 losses averaging -19.87%, n = 1527, giving +1.1996% against a mean of +1.1996%.

## Description only (not tests, never promoted to results)

Each interval here comes from the same day-resampled bootstrap, but none of these rows is a test.

| Group | n | Mean | Median | % positive | 95% interval (mean) |
|---|---|---|---|---|---|
| Signal return after costs, 60 sessions (not excess) | 1527 | +3.69% | -1.00% | 47.3% | +1.69% to +5.45% |
| Controls average return, 60 sessions (no costs) | 1527 | +2.49% | +1.98% | 56.2% | +1.35% to +3.59% |
| Excess, 20 sessions | 1527 | +1.01% | -0.80% | 47.3% | -0.06% to +2.09% |
| Signal return after costs, 20 sessions | 1527 | +1.16% | -0.11% | 49.7% | -0.18% to +2.48% |
| Controls average return, 20 sessions | 1527 | +0.15% | -0.05% | 49.8% | -0.70% to +0.97% |
| Single-insider buys that never became clusters, 60-session excess | 2172 | -0.38% | -1.97% | 45.8% | -1.68% to +0.99% |
| Single-insider buys, 20-session excess | 2172 | -0.58% | -1.25% | 45.9% | -1.31% to +0.13% |
| Clusters with a chief executive or finance chief buying, 60-session excess | 743 | +2.54% | -2.69% | 46.8% | -0.04% to +5.09% |
| Clusters without one, 60-session excess | 784 | -0.07% | -3.35% | 43.4% | -2.58% to +2.42% |
| Clusters with a 10% owner buying, 60-session excess | 364 | +0.31% | -4.74% | 40.4% | -3.90% to +4.49% |
| Clusters without one, 60-session excess | 1163 | +1.48% | -2.55% | 46.5% | -0.54% to +3.63% |
| Next-close entry, 60-session excess | 1527 | +0.53% | -3.35% | 44.0% | -1.27% to +2.36% |
| Next-close entry, 20-session excess | 1527 | +0.39% | -1.06% | 46.3% | -0.66% to +1.44% |
| Clusters made only by joint filers (one buyer group), 60-session excess | 199 | +1.81% | -3.25% | 41.7% | -3.71% to +7.89% |
| Clusters with two or more separate buyer groups, 60-session excess | 1328 | +1.11% | -2.88% | 45.6% | -0.73% to +2.94% |
| Market value under $300M, first half, 60-session excess | 220 | +5.13% | -3.13% | 45.9% | -1.44% to +12.34% |
| Market value under $300M, second half, 60-session excess | 201 | +7.33% | +2.25% | 55.2% | +1.19% to +13.54% |

## How many signals

Over 18 months of filings: 2590 cluster signals after the one-per-60-sessions rule (143.9 a month), 2091 mapped to a stock in the price panel, 1527 takeable (84.8 a month), 1527 tested (84.8 a month).

| Month | All signals | Mapped | Takeable | Tested |
|---|---|---|---|---|
| 2024-10 | 106 | 72 | 41 | 41 |
| 2024-11 | 173 | 147 | 102 | 102 |
| 2024-12 | 177 | 116 | 79 | 79 |
| 2025-01 | 79 | 50 | 29 | 29 |
| 2025-02 | 136 | 111 | 90 | 90 |
| 2025-03 | 210 | 187 | 147 | 147 |
| 2025-04 | 112 | 82 | 53 | 53 |
| 2025-05 | 193 | 172 | 133 | 133 |
| 2025-06 | 131 | 103 | 67 | 67 |
| 2025-07 | 85 | 63 | 38 | 38 |
| 2025-08 | 199 | 173 | 137 | 137 |
| 2025-09 | 115 | 84 | 62 | 62 |
| 2025-10 | 79 | 60 | 42 | 42 |
| 2025-11 | 223 | 203 | 164 | 164 |
| 2025-12 | 160 | 118 | 79 | 79 |
| 2026-01 | 66 | 47 | 31 | 31 |
| 2026-02 | 131 | 118 | 84 | 84 |
| 2026-03 | 215 | 185 | 149 | 149 |

## Five example signals

Drawn at random from the tested signals with the study seed.

| Signal date | Ticker | Buyers | Cluster $ | 60-session return after costs | Controls average | Excess |
|---|---|---|---|---|---|---|
| 2024-11-01 | MTDR | Ehrman Monika U (Dir); Stetson Glenn W (Off:EVP-Production) | 66,861 | +9.40% | +3.33% | +6.07% |
| 2025-02-13 | EAF | Flanagan Timothy K (Dir/Off:CEO and President); O'Donnell Rory F. (Off:Chief Financial Officer & SVP) | 105,500 | -29.79% | -10.91% | -18.88% |
| 2025-09-15 | RYAN | RYAN PATRICK G (10%/Dir/Off:Executive Chairman); RYAN PATRICK G JR (Dir) | 14,346,261 | -1.27% | +0.89% | -2.16% |
| 2025-10-30 | FMNB | Muransky Edward (Dir); Richardson Gina A (Dir) | 1,022,676 | -2.00% | -8.27% | +6.27% |
| 2025-12-09 | VSTS | Barber James J. (Dir/Off:President & CEO); Goetz William (Dir) | 1,091,463 | +7.80% | -2.72% | +10.52% |

## Funnel

| Step | Count |
|---|---|
| Form 3/4/5 filings in the six quarters | 293829 |
| Code P, acquired rows (all forms) | 34375 |
|   of which on Form 4/A (left out) | 715 |
|   of which on Form 5 or 5/A (left out) | 1401 |
| Code P, acquired rows on original Form 4 | 32259 |
|   left out: no director, officer or 10% owner among the reporting owners | 815 |
|   left out: 10b5-1 box ticked on the filing | 2325 |
|   left out: 10b5-1 named in a footnote on the row, box not ticked | 106 |
|   left out: unreadable transaction date | 0 |
|   transaction date after filing date (set to filing date) | 4 |
|   rows with no price (counted as $0 in cluster size) | 225 |
| Insider-buy rows kept | 29013 |
| Insider-buy filings kept | 16807 |
|   of which joint filings (2+ qualifying reporting owners) | 1758 |
| Issuers with an insider buy | 3022 |
| Filings that complete a cluster (before the 60-session rule) | 8848 |
| Cluster signals after the 60-session rule | 2590 |
|   could not be mapped to a panel stock | 499 |
|   mapped, but no price at the entry open | 122 |
|   mapped and priced, not takeable | 442 |
|   takeable, no control found | 0 |
| Tested (T1 n) | 1527 |

Mapping: 2054 signals by the trading symbol on the filing, 37 by CIK through sic_map.csv, 499 not mapped. In 11 signals the symbol on the filing is a panel ticker that sic_map.csv lists under a different CIK; 7 of them passed the price check and were kept, 4 failed it and are counted as not mapped.

Market value for the 1527 tested signals: no_share_data 202, none_filed_before_entry 10, ok 1269, stale_over_15_months 46.

60-session exit flags for tested signals: normal close 1520, stopped 7. Signals capped at +300%: 4. Tested signals with fewer than 10 controls: 0. Control 60-session exits marked at last close because the stock stopped trading: 353 of 15270.

IWM context (Yahoo daily, price only, no dividends): over the same 60-session windows as the 1527 tested signals, IWM returned +5.11% on average. Panel sessions with no IWM bar: 0. Context only; the test uses the matched controls.

## Caveats

- Costs are charged to the signal stock only, which is the literal reading of T1 ("the return after costs minus the controls' average"). If the controls also paid 1%, every excess return would be 1.00 point higher: T1 mean +2.20%, interval +0.33% to +4.03%, median -2.02%, halves +3.13% and +1.32%. Under that reading T1 would still NOT PASS, because the median would still be below zero. T2 and T3 compare groups, so this does not change them.
- A joint Form 4 lists several reporting owners against one set of purchases. Read literally, that is two or more different reporting owners buying, so it counts. 199 of the 1527 tested signals are clusters made only by owners who file together (often one fund and its managers). The table above shows them separately.
- 34 tested signals were triggered by a Form 4 filed more than 30 days after the purchase (late filings, some reporting purchases years old). Read literally they still count. Their mean 60-session excess was -5.70%.
- Code P covers any non-derivative security. 13 tested clusters include a purchase of preferred stock, notes or warrants rather than common stock (mean 60-session excess -15.34%). Code P also covers insiders buying in an IPO or a private placement, which the pre-registration includes.
- The data starts with filings on 1 Oct 2024. A buyer who bought in September 2024 cannot be seen, so early October clusters may be missed, and controls in late 2024 are only screened for insider buys from 1 Oct 2024.
- The price panel starts on 1 Oct 2024, so signals in the first 20 sessions use a shorter dollar-volume lookback.
- The panel holds US common stocks only. Funds, OTC stocks and units are not in it, which is most of the unmapped signals.
- When a company changes ticker, the panel series ends and the stock is marked at its last close, the same as a delisting.
- Share counts come from the dei cover-page tag. Companies with several share classes may report one class only, which understates market value.
- Purchase values are taken as filed. 2 tested clusters are worth more than the company's whole market value (AENT 2025-02-27, CLDI 2025-08-25), which points to an error in a filed purchase price or in the share count. They sit in the $250k-or-more group for T3.
- One period (Oct 2024 to Mar 2026) and one market. A pass here would still need a forward log.

## Deviations and choices

- The 10b5-1 indicator exists (`AFF10B5ONE` in SUBMISSION) but it is a box on the whole filing, not on each trade. A filing with the box ticked is left out in full. Rows whose own footnote says the purchase was made under a 10b5-1 plan are also left out. A footnote that says "non-Rule 10b5-1" is not treated as a plan.
- Only original Form 4 filings are used. Form 4/A amendments are left out so the same purchase is not counted twice, and Form 5 is left out because the signal is defined on a Form 4.
- The data has no link between a purchase row and one owner of a joint filing, so every qualifying owner on the filing is treated as a buyer of every purchase row on it. Cluster dollar value counts each purchase row once.
- "Within 30 calendar days" is measured between transaction dates. A filing triggers when one of its purchases is within 30 days of a purchase by a different owner that was public by then (filed on or before that filing date).
- Cluster size is the dollar value of all insider-buy rows public by the end of the signal date whose transaction date is within 30 days either side of the triggering purchase.
- The 60-session rule is applied to all signals by issuer before the takeable filter and before mapping.
- Exits are the closes 20 and 60 sessions after the entry session (entry session = session 0). Prices are split-adjusted only; dividends are not included.
- A takeable stock also needs an opening price on the entry session. Missing days in the 20-session dollar-volume window count as zero dollar volume.
- Controls are screened for insider buys (as defined) with a transaction date in the 90 calendar days before the entry date, for buys that could be mapped to a panel stock. Share classes of the same issuer are not used as its controls. The seed for each signal is its signal date as YYYYMMDD. Controls are charged no cost.
- Market value uses the latest share count filed before the entry date, rejected if its as-of date is more than 15 months before entry, split-adjusted with the panel split files, times the raw prior close.
- Insider-buy rows with no price count as $0 in cluster size.
- Mapping check (the pre-registration does not say how to map): when the symbol on the filing is a panel ticker that sic_map.csv lists under a different CIK, the match is kept only if the median of the issuer's insider purchase prices (90 days up to the signal) divided by the panel close on each purchase date is between 0.5 and 2. Otherwise the CIK fallback is tried, and if that fails the signal counts as not mapped. This removed a closed-end fund mapped to a bank and an unlisted insurer mapped to a pipeline partnership.
- IWM is used for context only.
