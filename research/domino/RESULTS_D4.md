# D4 results: the scorecard (run 10 Oct 2026)

Rules: [PREREG_D4.md](PREREG_D4.md), committed before this ran (commit 0b8ae7b). Code: `d4.py`. Numbers: `d4_results.json`.

Descriptive, like D3. Returns above +300% are counted as +300% (see the correction in the rules: WOLF's +904% was a bankruptcy share exchange, and TCGL's +1,982% ended with the stock not trading).

## What the scorecard asked

Using only what each company had filed before the trade: **R** revenue of $10M or more, **C** positive operating cash flow or 12 months of cash, **D** share count up less than 25% in a year. The answers were known for 82% of the 4,569 stage-3 trades.

## By score

| Group | Trades | Per year | Average after 10 days | Median | Winners | Edge over controls (10 days) | Reach +20% in 10 days | Average worst point |
|---|---|---|---|---|---|---|---|---|
| All of stage 3 | 4,569 | ~2,480 | +2.4% | 0.0% | 50% | +2.17% (+0.80% to +3.57%) | 21.1% | -10.0% |
| **Score 3: holds up** | 2,508 | ~1,360 | +2.4% | **+0.3%** | 51% | **+1.93% (+0.70% to +3.06%)** | 15.7% | -8.2% |
| Score 2 | 641 | ~350 | +2.8% | +0.2% | 50% | +1.03% (-1.29% to +3.29%) | 27.0% | -12.6% |
| Score 0-1 | 601 | ~330 | +3.9% | **-2.5%** | 44% | +2.62% (-0.98% to +6.54%) | 34.6% | -14.1% |
| Unknown | 819 | ~445 | +1.1% | 0.0% | 50% | +1.67% (-0.71% to +4.28%) | 23.2% | -10.5% |

What was predicted in advance: if quality matters, score 3 should have a better median and a better edge than score 0-1.

- **Median: yes.** +0.3% against -2.5%.
- **Edge: not on the average.** The weak companies have the higher average (+3.9% against +2.4%). But theirs comes from a few big spikes with most trades losing (44% winners, average worst point -14%), and their edge can't be told apart from zero. Score 3's edge is smaller but solid.

Plainly: **quality doesn't make the average bigger. It makes it dependable.** The junk is the lottery ticket; the companies that hold up are the steady version.

## Which question matters most

| Question | Answer | Trades | Median after 10 days | Edge over controls (10 days) |
|---|---|---|---|---|
| Can it pay its bills? | yes | 3,364 | +0.4% | **+2.34% (+1.03% to +3.64%)** |
| | no | 804 | -2.3% | +0.89% (-2.13% to +4.05%) |
| Revenue of $10M or more? | yes | 3,243 | +0.3% | +1.48% (+0.40% to +2.51%) |
| | no | 737 | -1.4% | +3.60% (+0.07% to +7.10%) |
| Not printing shares? | yes | 3,338 | +0.1% | +1.87% (+0.62% to +3.22%) |
| | no | 721 | -0.4% | +1.74% (-0.99% to +4.60%) |

"Can it pay its bills" separates best. The no-revenue companies are where the spikes are (34.5% of them reach +20% within 10 days) and also where the median is negative.

## The realistic set: about 100 trades a year

| Set | Trades | Per year | Signal days | Average after 10 days | Median | Winners | Edge (10 days) | After 1% costs | After 3.5% costs |
|---|---|---|---|---|---|---|---|---|---|
| **Score 3 + own volume 2x** | **181** | **~98** | 94 (1 stock a day) | +3.2% | **+1.0%** | 56% | +3.11% (+0.28% to +6.16%) | +2.2% | -0.3% |
| Score 2-3 + own volume 2x | 233 | ~127 | 108 | +4.1% | +1.1% | 57% | +3.85% (+0.82% to +6.78%) | +3.1% | +0.6% |

This is the first set in the whole series with a **positive median**, more winners than losers, and a size a person can actually take: about two trades a week, usually one stock on a signal day. 22% of them reach +20% within 10 days; the average worst point is -8.9%.

## How much to trust it

- It is the **fourth cut of the same two years**. The lower end of the range is only just above zero (+0.28%). It could be luck.
- The path is the same as D3: nothing on day 1, the gain arrives over 5 to 10 days (edge after 5 days: +1.1%, range -0.7% to +3.2%).
- **Costs decide it.** At 3.5% a round trip it is roughly zero. At about 1% it is +2.2% a trade.
- Roughly half of the stage-3 edge was sector tailwind (D3 check). That check hasn't been repeated on this smaller set.

## What happens next

This becomes a written forward rule, logged on paper from the next signal, and judged only on trades after today:

1. A stock trading $20M a day or more, in a kept industry, closes up 20% or more.
2. List its same-industry stocks one tenth its size or smaller that were quiet that day.
3. Keep: takeable, not China/HK, no reverse split in 90 days, scorecard 3 of 3, own volume at least 2x.
4. Entry at the next open. Track 1, 5 and 10 days against matched controls.
