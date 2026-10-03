# Independent audit: HL BTC funding carry (PREREG.md)
Auditor run 2026-10-03 (~11:00 UTC). This was built from PREREG.md alone. carry_test.py, RESULTS.md and hl_btc_funding.csv were **not** opened.
All numbers below come from the scripts and data in this folder:
- Data pulls: `pull_funding.py`, `pull_candles_books.py`, `pull_binance.py`
- Analysis: `audit_backtest.py` (writes `audit_results.json`) and `audit_risk.py` (writes `audit_risk_results.json`)

## 1. Rebuilt results vs the pass rule

**Data.** I re-pulled `fundingHistory` for BTC and got **29,202 prints**, from 2023-05-12 00:00 to 2026-10-03 11:00 UTC. The spec says 29,201. The extra print is most likely the 11:00 print, which was published after the spec was frozen.
- The first **82 prints** (2023-05-12 to 2023-06-08 00:00) are **8-hourly**. Each one carries an 8-hour rate.
- After that the prints are hourly, apart from 3 missing hours (2-hour gaps on 2023-07-02, 2023-08-23 and 2024-08-15).
- I count each print as one payment. I annualise over calendar time, not over the number of prints.

**My conventions.**
- A position decided at print t−1 earns the print at t.
- The 0.31% round trip is charged as 0.155% on entry and 0.155% on exit.
- Returns are simple (not compounded): the sum of net carry divided by elapsed years (365.25 days per year).
- Return on capital = return on N ÷ 1.333.
- V2's trailing mean uses a time-based 24-hour window that includes print t−1.
- In V1, the entry cost falls in IS and the exit cost falls in OOS.

| | V1 always-on | V2 gated |
|---|---|---|
| IS 2023-05-12→2024-12-31, ann. net on N / on capital | **19.96% / 14.97%** | 14.46% / 10.85% |
| OOS 2025-01-01→2026-10-03, ann. net on N / on capital | **8.17% / 6.13%** | **−2.48% / −1.86%** |
| Whole period, ann. net on N / on capital | 13.87% / 10.40% | 5.72% / 4.29% |
| 2023 (partial, 0.64 yr): net sum on N (ann. N / cap) | 8.59% (13.40% / 10.05%) | 3.63% (5.66% / 4.25%) |
| 2024 (full year): net on N (on capital) | **24.20%** (18.12%) | 20.13% (15.07%) |
| 2025 (full year): net on N (on capital) | **10.63%** (7.98%) | 2.64% (1.98%) |
| 2026 YTD (0.75 yr): net sum on N (ann. N / cap) | 3.69% (4.89% / 3.67%) | −6.99% (−9.27% / −6.95%) |
| % of months positive (42 months) | 88.1% | 66.7% |
| Worst month (on N) | −0.77% (2023-05) | −2.98% (2025-04) |
| Worst drawdown of cumulative net (on N) | −1.12% (2023-07-23 → 2023-09-18) | −9.49% (2025-11-24 → 2026-06-27) |
| Switches | 2 (1 round trip) | 196 (98 round trips, 30.4% of N in costs, in market 88.8% of the time) |
| **Verdict** | **PASS** (OOS > 0 and both full years > 0) | **FAIL** (OOS < 0) |

**Decay.** The carry is clearly shrinking. Gross annualised funding on N, by year:

| 2023 | 2024 | 2025 | 2026 YTD | Last 365 days | Last 180 days |
|---|---|---|---|---|---|
| 15.1% | 24.2% | 10.6% | 5.1% | 5.95% | 6.23% |

- The share of hours with a positive rate fell from 96% (2024) to 78% (2026).
- The rate sits exactly at the 0.00125%/h interest floor in 52% of all prints.
- That floor alone is worth about 10.95%/yr. The 2026 figure is below it, which means the premium has been negative for much of 2026.
- At last-365-day rates, V1 earns about **4.5% a year on capital before any extra costs**.

## 2. Expected differences from the original (unseen)
- **One extra print** (29,202 vs 29,201). The effect is negligible.
- **8-hour era (82 prints, which sum to −0.58% of N).** An implementation that treated these as hourly rates and forward-filled them across each 8-hour gap would book about 8× this, roughly −4.6% of N in IS 2023. One that annualised by print count × 8,760 would also misstate the early months. Neither would change the verdict.
- **First print.** Whether the print at entry is earned shifts the result by 0.06% of N.
- **V1 cost split.** If the original charged the full 0.31% in each period, or reported OOS as a standalone trade, OOS moves by about 0.09%/yr.
- **V2 window.** A 24-print window and a 24-hour window differ only in the 8-hour era, so expect a few switches' difference at most.
- **Constant USD notional.** My model, like the spec, holds N fixed in USD. A real position fixed in BTC units earns funding on its current USD value, so dollar P&L would scale with the BTC price (27k → 126k → 85k). This needs rebalancing, which is costed in §4.

## 3. Sign convention: CONFIRMED (the result is not inverted)
Hyperliquid's docs (https://hyperliquid.gitbook.io/hyperliquid-docs/trading/funding) say:
- When the perp trades above the oracle, the premium and the funding rate are positive, and "the long position will pay the short position".
- Funding is **paid every hour**, at one eighth of the computed 8-hour rate.
- The payment is `position_size * oracle_price * funding_rate`, i.e. it is applied to notional at the oracle price.
- The interest component is fixed at 0.01% per 8 hours. Funding is capped at 4%/h.

**Independent checks.**
- The stored hourly rates match `(premium + clamp(0.0001 − premium, ±0.0005)) / 8` exactly in 89.6% of hourly prints, and the sign always follows the premium.
- The live check (`metaAndAssetCtxs`, 2026-10-03 11:04 UTC) gave BTC funding = 0.0000078338 with premium −0.000437. The formula gives 0.0000079, which matches. The latest `fundingHistory` prints that morning were 0.0000104721, 0.0000074688, 0.0000079489, 0.0000022379, 0.000000194 and 0.000006387, the same order of magnitude.
- So with a positive rate, the short perp receives. The spec's sign is correct.

## 4. Things the spec ignored

### 4a. Feasibility gap: the hedge leg did not exist for most of the in-sample period
Hyperliquid's BTC spot pair is **UBTC/USDC (`@142`)**. UBTC is "Unit Bitcoin", a bridged or wrapped asset, which adds bridge and custodian risk.
- Its first daily candle is **2025-02-03**, and it had dust volume until about 2025-02-14.
- So the whole IS period (2023-05 → 2024-12) **could not have been run on Hyperliquid spot**. It would have needed a hedge on another venue, with cross-venue margin and transfer risk.
- Only the OOS period was executable as specified.

### 4b. Basis risk (spot UBTC minus perp, from candle closes; spot candles with zero volume dropped)

| Sample | n | Mean | p1 | p99 | Worst close divergence |
|---|---|---|---|---|---|
| 1h, 2026-03-09→2026-10-03 | 5,001 | −0.3 bp | −11.4 bp | +13.1 bp | −21 bp (2026-09-21 18:00); **+102 bp** (2026-07-08 11:00) |
| 15m, 2026-08-12→2026-10-03 | 5,002 | −1.0 bp | −10.6 bp | +7.9 bp | −21 bp; +51 bp (2026-08-27 18:15) |
| 1d, 2025-02-15→2026-10-03 | 596 | +0.7 bp | −15.3 bp | +13.9 bp | −26 bp (2025-02-26); +27 bp (2025-07-11) |

The 1d series is cleaned: the listing-week candles had prints at 6,969,696 and 7,979,573, which are bogus and were excluded.

**Basis moves against the position.** Long spot / short perp loses when spot/perp falls.
- Over 24 hours (1h data), the 1st percentile move is −9.5 bp and the worst is −108 bp.
- Over 7 days, the 1st percentile is −12 bp and the worst is −110 bp.

**Intrabar wicks** are much larger. The spot high/low diverged from the perp by up to:
- **−91 bp** (spot low 79,600 vs perp low 80,333, 2026-09-20 12:00)
- **+189 bp** (2026-07-08 11:00)

**Practical meaning.**
- Normal entry and exit cost about ±10–15 bp of basis on top of fees.
- A market order on spot during a dislocation can cost 1–2%. Use limit orders, and never exit in a wick.
- A 1% basis hit equals about 1.5 months of carry at 2026 rates.

### 4c. Squeeze / liquidation at 3x short
Source: Binance BTCUSDT perp 1h klines, 2023-05-01 → 2026-10-03, 30,036 bars. Each window measures entry at the bar close to the maximum high over the next W hours.

**Liquidation threshold.** HL's maintenance margin is half the initial margin at max leverage. BTC's max leverage is 40x, so maintenance margin is 1.25%. The liquidation rise is (1/L − 0.0125)/1.0125:

| Leverage | 1x | 1.5x | 2x | 3x | 5x |
|---|---|---|---|---|---|
| Rise to liquidation | 97.5% | 64.6% | 48.1% | **31.7%** | 18.5% |

| Window | Largest rise | Entry | Highest leverage that survives every window | Entry-hours where 3x is liquidated |
|---|---|---|---|---|
| 1h | 13.8% | 2023-10-23 | 6.6x | 0 |
| 24h | **20.0%** | 2023-10-22 23:00 | 4.6x | 0 |
| 72h | **26.1%** | 2024-02-26 09:00 | **3.6x** | 0 |
| 7d | 32.4% | 2024-11-04 23:00 | 2.9x | **5** |
| 30d | 63.8% | 2024-02-05 | 1.5x | 1,972 |
| 90d | 97.9% | 2024-09-06 | <1x | 9,428 |

Hyperliquid's own daily candles cross-check this: 1-day 21.6%, 3-day 24.3%, 7-day 32.1%.

- **A 3x short survived every 24h and 72h window.** The tightest buffer was 26.1% against 31.7%, about 5.6 points.
- **It did not survive every 7-day window without a top-up.** The Nov-2024 election rally exceeded 31.7% within a week.
- **"Always-on" with no top-ups fails outright.** A 3x short opened on 2023-05-12 at 27,020 would have been **liquidated on 2023-10-23 22:00**. BTC then went on to 126,209 (+367%).
- **With rebalancing** (moving spot gains to perp margin and resetting to the target leverage), the backtest gave these liquidation counts:

| Rebalance every | 2x | 3x | 5x |
|---|---|---|---|
| 1 day | 0 | 0 | 1 |
| 7 days | 0 | 0 | 6 |
| 30 days | 2 | 3 | 11 |

- **Cost of weekly rebalancing.** Rises summed to 481% of N over 3.39 years. At 0.155% per side on both legs, that costs about **0.75% of N in total (~0.2%/yr)**. This is small but not zero, and it assumes discipline every week.

## 5. Spot and perp liquidity, and fees
Snapshot: 6 L2 books taken 2026-10-03 11:06–11:08 UTC, a Saturday morning, so this is a single calm moment.
- Slippage is measured against mid from the raw 20-level book.
- Depth uses the aggregated books: `nSigFigs=4` (≈1.2 bp buckets) for 0.1%, and `nSigFigs=3` (≈12 bp buckets) for 0.5%. Both are approximate.

| | UBTC/USDC spot `@142` | BTC perp |
|---|---|---|
| 24h notional volume | $29.9M | $2.48B |
| Spread | 0.12 bp | 0.12 bp |
| Depth within 0.1% (bid / ask) | ~$1.23M / ~$1.07M | ~$28M / ~$21M |
| Depth within 0.5% (bid / ask) | ~$2.2–2.4M / ~$2.1–2.4M | ~$46–75M / ~$44–57M |
| Slippage to buy $1k / $10k / $100k (median; worst of 6) | 0.06 bp / 0.06 bp / 0.36 bp (worst 0.43 bp) | 0.06 bp at all three sizes |
| Slippage to sell $100k (median; worst of 6) | 0.38 bp (worst 0.47 bp) | 0.06 bp |

The raw top-20 levels reached only about 3–4 bp from mid on spot, but they already held more than $100k.

**Base-tier fees (tier 0)**, from https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees:

| | Taker | Maker |
|---|---|---|
| Perp | 0.045% | 0.015% |
| Spot | 0.070% | 0.040% |

- Spot volume counts double towards fee tiers.
- HYPE staking gives 5–40% discounts.
- Aligned quote assets get 20% lower taker fees.
- **Realistic taker round trip on both legs** = 2 × (0.045% + 0.07%) + under 0.01% slippage ≈ **0.24%**. The spec's 0.31% is conservative.
- Basis at entry and exit (±10–15 bp, §4b) roughly eats that margin.

**Margining.** Hyperliquid's portfolio margin (https://hyperliquid.gitbook.io/hyperliquid-docs/trading/portfolio-margin) lets a spot BTC balance collateralise the short perp, so spot and perp P&L offset each other. But:
- It is **in beta**.
- It requires **more than $10k account value** (or more than $5M weighted volume).
- BTC counts at **LTV 0.5**, with global and user caps.
- Below $10k, the perp margin is separate USDC, and you have to top it up by hand.

## 6. Plain-English verdict
**Is the carry real?** Yes, as accounting.
- The sign is right, and the rebuild reproduces a V1 PASS: OOS 8.2%/yr on N, 6.1% on capital.
- V2 FAILS, killed by 98 round trips of costs.
- But the edge is decaying fast. 2026 YTD gross is about 5% on N, or about 3.7% on capital net.
- Roughly 11%/yr of the historical gross is just Hyperliquid's fixed interest term, which is paid only when the premium is not strongly negative. In 2026 it often was.
- The IS years (2023–24, about 20%/yr on N) **were not executable on Hyperliquid spot**, because UBTC only listed in Feb 2025. Judge the trade on OOS and recent data only.

**Small account ($500–$5,000).**
- It is executable: liquidity is a non-issue at these sizes, and HL's minimum order is $10.
- But the economics are thin. About 4–6% on capital is **$20–$300/yr**, before:
  - bridge and withdrawal costs
  - UBTC bridge risk
  - the work of weekly margin top-ups (no portfolio margin below $10k)
- One bad basis exit (1%) or one liquidation wipes out years of carry. Marginal at best.

**Larger account ($50k).**
- Executable: spot depth is about $1M within 0.1%, and the $37.5k notional has under 0.5 bp slippage.
- Portfolio margin (beta, BTC LTV 0.5) removes most of the liquidation mechanics.
- Expected about $2–3k/yr at recent rates.
- The remaining risks are UBTC custody, portfolio-margin beta caps, and basis.

**Minimum safety rules.**
1. **Leverage ≤ 2x on the perp leg**, giving about 48% rise headroom, if margin is separate (no portfolio margin). 3x survived every 72-hour window but not every 7-day window, and with only a 5.6-point buffer on 72 hours.
2. **Top up or rebalance the perp margin at least weekly.** Also rebalance on any +15% move: sell that much spot and buy back that much perp.
3. **Keep a free USDC buffer of at least 25% of N** in the perp account, or use portfolio margin (more than $10k accounts only).
4. **Use limit orders** on the UBTC spot leg. Never enter or exit when |spot/perp − 1| > 15 bp.
5. **Kill switch.** Exit if the trailing 30-day carry falls below the risk-free stablecoin yield available to you. The 2026 numbers are already close to that test.
