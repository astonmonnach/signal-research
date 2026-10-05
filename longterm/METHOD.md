# Long-term research: how it works

Medium/long-term ideas (6–36 months) use the same nth-order method as everything else in this repo
([the skill](../.claude/skills/nth-order/SKILL.md), v3): primary sources only, absence is a finding,
check whether it has already run, go deeper on every branch, gates G1–G5 and the 0–10 score. A long
hold is exposed to things a two-week trade isn't, so long-term mode adds six gates.

## The six long-term gates

| Gate | Passes when | Source |
|---|---|---|
| **LT1 In the numbers** | The theme shows up in **reported** segment revenue, backlog/RPO or a funded order. An article, a CEO quote or a contract ceiling isn't enough. | Latest 10-K / 10-Q / 8-K, or the company's own release |
| **LT2 Survives two bad years** | Cash plus undrawn credit covers the next big maturity and two years of negative free cash flow (or FCF is positive). | Latest 10-Q: balance sheet, debt note, cash-flow statement |
| **LT3 Dilution** | The diluted share count grew under ~3% a year over 3 years, with no live equity line or at-the-market programme funding the company. | SEC companyfacts XBRL, S-3 / 424B filings |
| **LT4 Not already run** | The 1-year and 3-year moves against SPY plus the valuation (EV/sales or P/E) against its own 5-year range and two peers leave room. A real but fully priced theme is "already run". | Yahoo closes; filings for EV |
| **LT5 Liquidity** | Average daily $ volume of $5M or more. Large and mid caps preferred; anything smaller is flagged. | Yahoo volume × price |
| **LT6 Benchmark** | Measured against **SPY** and its sector ETF from the day it's added, and the thesis says what would make it beat both. | [README.md](README.md), built by `build_longterm.py` |

## Verdicts

| Verdict | When | Meaning |
|---|---|---|
| **long-term candidate** | Score ≥ 8 and every gate passes | Can become a public call (horizon `long`), but only when Aston says yes. |
| **watch** | Score 5–7, or LT1 / LT4 not met yet | Real, but something is missing. Each one has a dated review trigger. |
| **already run** | Fails LT4 | The theme is real and already in the price. |
| **kill** | A failed G-gate, or a failure of LT2 or LT3 | Logged with the reason. Kills are part of the record. |

## How a long-term call works

It uses the same [calls record](../calls/README.md) as swing calls, with `horizon = long`:
- it's measured against **SPY**, not IWM;
- the review date is about 12 months out, with a check at every quarterly report;
- the invalidation is a **thesis break** stated up front (for example the theme's segment revenue
  falling two quarters running), and optionally a price floor.

## Where this fits

This is research on single stocks. For most long-term investors a broad, low-cost index fund is the
core, and single-stock ideas are the small satellite part. These pages are a research log, not
advice.

The candidates are in [candidates.csv](candidates.csv), the tracking table is in
[README.md](README.md), and the research reports are under `research/longterm-*/`.
