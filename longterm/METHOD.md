# Long-term research: how it works

Medium/long-term ideas (6–36 months) use the same nth-order method as everything else in this repo
([the skill](../.claude/skills/nth-order/SKILL.md): primary sources only, absence is a finding, check
whether it has already run, go deeper on every branch, gates G1–G5 and the 0–10 score). A long holding
period adds risks a two-week trade doesn't face, so there are six extra checks.

## The six extra checks

1. **The theme is in the reported numbers.** It shows up in segment revenue, backlog/RPO or a funded
   order in the latest 10-K, 10-Q or 8-K (or the company's own press release). An article or a CEO
   quote doesn't count.
2. **The balance sheet survives two bad years.** Cash, total debt, the nearest big maturity and free
   cash flow, all from the latest 10-Q.
3. **Dilution.** The diluted share count over 3 years. A company that funds itself by issuing shares
   shrinks your slice even when the theme is right.
4. **Already run?** The 1-year and 3-year move against SPY, and the valuation (EV/sales or P/E) against
   its own 5-year range and two peers. A real theme that's fully priced is "already run", not a
   candidate.
5. **Liquidity.** Large and mid caps, with average daily $ volume of $5M or more. Anything smaller is
   flagged.
6. **Benchmark.** SPY plus the sector ETF. A long-term idea that only matches the index added nothing.

## Verdicts

| Score | Verdict | Meaning |
|---|---|---|
| ≥ 8 | **long-term candidate** | Passes every gate and check. Can become a public call (horizon `long`) only when Aston says yes. |
| 5–7 | **watch** | Real, but something is missing (often the numbers don't show it yet, or the valuation is stretched). Each has a dated review trigger. |
| — | **already run** | The theme is real and already in the price. |
| ≤ 4 | **kill** | Logged with the reason. Kills are part of the record. |

## How a long-term call works

It uses the same [calls record](../calls/README.md) as swing calls, with `horizon = long`:
- it's measured against **SPY**, not IWM;
- the review date is about 12 months out, with a review at each quarterly report;
- the invalidation is a **thesis break** stated up front (for example the theme's segment revenue
  falling two quarters running), and optionally a price floor.

## Where this fits

This is research on single stocks. For most long-term investors a broad, low-cost index fund is the
core, and single-stock ideas are the small satellite part. These pages are a research log, not
advice.

The candidates are in [candidates.csv](candidates.csv), the tracking table is in
[README.md](README.md), and the research reports are under `research/longterm-*/`.
