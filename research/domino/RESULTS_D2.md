# D2 results: is there money in the domino? (run 10 Oct 2026)

Rules: [PREREG_D2.md](PREREG_D2.md), committed before this ran (commit 78dd231). Code: `d2.py`. Raw numbers: `d2_results.json`.

## Verdict

**Not supported. There is a faint real signal, but it comes entirely from rare lottery-ticket wins and it does not survive costs.**

The primary test: a stock trading $20M a day or more closes up 20% or more. Buy its quiet, much smaller same-industry stocks at the next open, hold 5 days. Takeable trades only (price $1 or more, $250k a day or more).

| | Result |
|---|---|
| Trades | 30,659 over 376 days (a typical leader has about 20 followers) |
| Excess over matched controls | **+0.82%** (95% interval **-0.08% to +1.95%**: it includes zero) |
| Average basket return, before costs | +0.88% (controls: +0.07%) |
| After 1% costs (ledger rule) | **-0.12%** |
| After 3.5% costs (this account) | **-2.62%** |
| Median trade | **-0.33%** |
| Trades that made money | 47% |
| Trades at +50% or better | 0.8% |
| Mean without the top and bottom 1% | -0.07% |

Both parts of the bar failed: the interval includes zero, and the return after 1% costs is negative.

## What is really going on

- **It is a lottery ticket.** Across the 30,659 trades, the top 1% (306 trades) made a combined +283 "units" and the other 99% lost a combined -165. Take away a few hundred winners and the strategy loses.
- **The winners are real.** The 8 biggest (TCGL +1,982%, SDOT +882%, ELAB +678%, ZENA, STI...) all had a genuine +100% runner day inside the hold, none flagged as a suspect split. So the D1 effect is real: runners do show up among the followers. There just aren't enough of them (0.25% of trades) to pay for everything else.
- **Order now matters.** With the follower required to be quiet first, only a leader going **up 20%** shows anything. Leader up 10%: +0.08%. Leader down 20%: +0.24%. Leader down 10%: +0.02%. All indistinguishable from zero.
- **Including untakeable stocks** (under $1 or under $250k a day) the excess is +0.96% (interval +0.20% to +1.84%), which does clear zero. But those are the stocks you can't actually trade at the printed price, and after 3.5% costs it is still -2.36%.
- **Without drug stocks:** +1.35% excess (-0.03% to +3.59%) and +0.39% after 1% costs. The closest to a pass, still not one, and the median is -0.31%.

## China and Hong Kong followers: the worst group

| Followers headquartered in China / Hong Kong | Trades | Excess over controls | Basket return | Median |
|---|---|---|---|---|
| Takeable, leader up 20% | 252 | **-3.71%** (-6.38% to -1.13%) | -3.54% | -1.84% |
| Takeable, leader up 10% | 808 | **-3.10%** (-4.96% to -1.36%) | -2.85% | -2.30% |
| Any size, leader up 20% | 1,476 | -0.85% (-1.93% to +0.24%) | -0.28% | -0.44% |

Buying takeable China/HK small caps after a big same-industry stock pops lost about 3.5% in five days, and that result is statistically solid. They are over-represented among runners (7.6% of runner days against 4.0% of controls in the runners study), but as a group you lose money holding them, and 6% of these trades were down 30% or more within the week.

## What this means

- The domino is **real as a pattern and useless as a blind trade**. Buying every small linked name after a leader's move is buying lottery tickets at a negative expected value after costs.
- The edge, if there is one, is in **picking which follower** will run, not in buying the basket. That needs a second filter. The runners study already has the best one: a prior-day volume spike of 5x or more (8.92x lift).
- **Next test (D3, to be written down first):** leader up 20% AND the follower's own volume jumps that day or the next (5x its 20-day average) while its price is still quiet. Fewer trades, and the question is whether the hit rate rises enough to beat costs.
