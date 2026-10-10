# D3 results: the funnel (run 10 Oct 2026)

Rules and the industry list: [PREREG_D3.md](PREREG_D3.md), committed before any per-sector number was seen (commit 662bc88). Code: `d3.py`, `d3_check.py`. Numbers: `d3_results.json`.

This is a description, not a pass or fail. Anything that looks good here is a lead to test on new trades.

## The funnel

Start: a $20M-a-day stock closes up 20% or more; its quiet, much smaller same-industry stocks are bought at the next open.

| Stage | Trades | Different stocks | Per year | Close after 5 days | After 10 days | Median after 10 days |
|---|---|---|---|---|---|---|
| 0. Every follower | 55,737 | 2,999 | ~30,300 | +0.8% | +1.5% | -0.8% |
| 1. Kept industries only (the continent test) | 6,951 | 645 | ~3,800 | +2.3% | +3.5% | 0.0% |
| 2. + takeable ($1+, $250k a day+) | 4,711 | 549 | ~2,600 | +1.4% | +2.8% | 0.0% |
| 3. + holds up (not China/HK, no recent reverse split) | 4,569 | 531 | ~2,500 | +1.5% | +2.9% | 0.0% |
| 4a. + own volume 2x that day | 342 | 185 | ~190 | +1.8% | +4.0% | +0.8% |
| 4b. + own volume 5x that day | 27 | 22 | ~15 | -1.1% | -2.1% | -0.6% |

Returns are averages before costs. **92% of the trades are gone by stage 3**, and stage 4a cuts it to under 1%.

## The industry cut worked

Same filters (takeable, holds up), three industry buckets, measured against size-matched controls:

| Bucket | Trades | Edge after 5 days | Edge after 10 days |
|---|---|---|---|
| **Kept** (chips, power, energy, metals, defence, compute, freight) | 4,569 | **+1.52%** (+0.29% to +3.07%) | **+2.58%** (+0.93% to +4.47%) |
| Cut and "maybe" (drugs, software, finance, retail and the rest) | 24,154 | +0.07% (-0.51% to +0.65%) | -0.55% (-1.84% to +0.48%) |

In the cut industries a big stock's move tells you nothing about the small ones. In the kept ones it does. Both years agree (2024-25: +2.6% after 10 days; 2025-26: +3.2%).

By group, after 10 days (average / median): chips and hardware +4.3% / +0.3% (2,095 trades); compute hosting +2.0% / +0.1% (1,090); power and electrical +3.0% / -0.4% (496); mining and metals +1.5% / +0.7% (458); energy -0.9% / -1.2% (360, nothing there); defence (45) and freight (25) are too few to read.

## How much of it is the domino, and how much is just good sectors

Chips, power and metals went up for two years, so their small stocks look good on any day. Two checks (`d3_check.py`):

| Compared with | Edge after 5 days | Edge after 10 days |
|---|---|---|
| The **same stocks on their ordinary quiet days** | +1.40% (+0.11% to +2.90%) | **+2.23%** (+0.46% to +4.16%) |
| **Other favoured-sector stocks on the same day** (no big mover in their own industry) | +0.98% (-0.14% to +2.43%) | +1.22% (-0.22% to +2.79%) |

So the effect is real against the stocks' own normal behaviour. But roughly half of it is "a good week for the favoured sectors in general"; the part that belongs to the specific link is about +1.2% over 10 days and can't be told apart from zero.

## What actually happens after entry (stage 3)

- **Day 1 is a coin flip.** Average open-to-high +3.3%, open-to-low -3.2%, open-to-close +0.1%. There is no edge "within hours" on daily data.
- **The gain builds slowly.** +0.5% after 2 days, +0.6% after 3, +1.5% after 5, +2.9% after 10. The best close falls on days 4 to 10 in 62% of trades.
- **Best and worst points within 5 days:** average best +10.7% (median +5.5%), average worst -7.3%. Controls' average best is +7.0%.
- **Reaching +20% / +50% / +100% within 5 days:** 10.9% / 1.8% / 0.4% of trades (controls: 0.3% reach +50%).
- **Still lottery-shaped, but less so.** After 10 days the median trade is 0.0% and half are positive. Without the top and bottom 1% the average is +1.5% (in D2 it was negative). The top 1% of trades supply two thirds of the total.

## The China/HK and reverse-split names (cut at stage 3) behave differently

142 trades. They spike the most and keep the least:

- 24% reach +20% within 5 days, 7.7% reach +50%, 2.8% double (against 10.9% / 1.8% / 0.4% for stage 3).
- Their best close is on **day 1 a third of the time**.
- Then they fade: median -3.0% after 5 days and **-7.2% after 10**.

If anything is a "hours, not days" move, it's these. Daily bars can't show whether the spike is catchable; that needs minute data.

## The volume filter

- **5x volume while the price is still quiet almost never happens**: 27 trades in two years, and those lost. The runners study's volume tell comes with a price move; a quiet price with 5x volume is a different thing.
- **2x volume** leaves 342 trades and is the best-looking set: edge +2.9% after 5 days (+1.0% to +5.0%) and +3.4% after 10 (+0.8% to +6.0%), median +0.8%, 55% positive, and it doesn't depend on the top 1%. It is also the smallest sample and the last filter added, so it is the most likely to be luck.

## Costs

Stage 3 averages +2.9% over 10 days before costs. After the ledger's 1% that is about +1.9%. **After this account's 3.5% it is about -0.5%.** Stage 4a: +4.0% before, about +0.5% after 3.5%, with a median below zero after costs. At £40-50 a trade the fees are bigger than the edge.

## Where this leaves it

- The instinct was right: most of the 30,000 trades were junk, and cutting by "does the world rely on this industry" removed 88% of them and kept the part that works.
- What's left is a real but modest tilt, about +2% over 10 days against normal, half of it sector tailwind, built from a flat median and a few big winners.
- 2,500 trades a year is still far too many. A signal day has a basket of about 14 stocks. **Choosing 1 or 2 of the 14 is the remaining problem**, and that is a research job, not another mechanical filter.
- Next: score the 531 surviving stocks on whether the business holds up (cash runway, revenue, how fast the share count grows), written down first, and see whether the good ones carry the result.
