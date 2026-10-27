# Public calls: the track record

Every stock we commit to publicly. **Append-only:** calls are never edited or deleted, losers stay. Each one is marked from the **next session's open** after it was posted, on a standard **$1,000** notional, against the market (**IWM** for swing calls, **SPY** for long-term calls) and a named control stock, and closed only by its own pre-stated rule (an invalidation close or the review date). These are research calls, not trades or advice.

## Scoreboard

- Calls: **5** · marked: 5 · open: 5 · closed: 0
- Total P&L on $1,000 per call: **$+78.04**
- Average vs the market: **+2.2%** · beat it: 4/5 · t-stat 1.32 (need about 2 and 20+ calls before it means anything)

## Every call

| # | posted | call | thesis | entry | now / exit | return | vs market | vs control | days | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2026-10-05 | LONG **MTUS** | [$125M funded DLA order under the $995M HF-1 steel stockpile IDIQ; Q3 (6 Nov) should show it in backlog and A&D sales](../stocks/MTUS.md) | $21.13 (2026-10-06) | $20.77 | -1.7% | +0.2% (IWM) | +5.4% (IIIN) | 21 | open |
| 2 | 2026-10-26 | AVOID **DFNS** | [Registered 19.0M sellable shares, 5.8x its 3.25M shares: a 10M-share equity line priced at 97.5% of the lowest 15-day VWAP plus PIPE resales; EFFECT 22 Oct](../research/daily/2026-10-26.md) | $3.91 (2026-10-27) | $3.58 | +8.4% | +8.8% (IWM) | +7.6% (ITA) | 0 | open |
| 3 | 2026-10-26 | AVOID **NCT** | [Registered direct of 15M new Class A shares at $1.30 ($19.5M), 4.8x the 3.12M shares outstanding, delivered 26 Oct; Monday's +17% to $1.48 hands those buyers an exit](../research/daily/2026-10-26.md) | $1.55 (2026-10-27) | $1.52 | +1.6% | +2.0% (IWM) | -0.1% (GLBS) | 0 | open |
| 4 | 2026-10-26 | AVOID **TMCR** | [F-1s effective 22 Oct: a $100M Yorkville standby equity line (23.6M shares, 35% of 67.4M) at 96% of market, plus 4.37M consideration shares free to sell now](../research/daily/2026-10-26.md) | $2.10 (2026-10-27) | $2.12 | -0.9% | -0.6% (IWM) | -1.6% (GROY) | 0 | open |
| 5 | 2026-10-26 | AVOID **OSTX** | [Warrant inducement at $1.30: 5.52M new shares (12% of 46.1M) issued with up to 3.93M more by 30 Oct and new $1.40 warrants capping rallies](../research/daily/2026-10-26.md) | $1.22 (2026-10-27) | $1.22 | +0.4% | +0.8% (IWM) | +2.5% (XBI) | 0 | open |

## Rules

1. A call is posted publicly (X) and added here in the same hour. The git commit time is the timestamp.
2. Entry is the next session's open. No cherry-picking a better fill.
3. Each call states its invalidation close and review date up front. It closes only by those rules.
4. Nothing is ever deleted or edited. A mistake gets a new row that says so.
5. Judge the record after 20+ closed calls, against the market and the controls, not by the best winner.
6. Long-term calls (horizon `long`) are measured against SPY and can also close on a pre-stated thesis break (for example the theme's segment revenue falling two quarters running), recorded in the exit columns with the reason.
