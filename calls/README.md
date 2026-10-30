# Public calls: the track record

Every stock we commit to publicly. **Append-only:** calls are never edited or deleted, losers stay. Each one is marked from the **next session's open** after it was posted, on a standard **$1,000** notional, against the market (**IWM** for swing calls, **SPY** for long-term calls) and a named control stock, and closed only by its own pre-stated rule (an invalidation close or the review date). These are research calls, not trades or advice.

## Scoreboard

- Calls: **9** · marked: 9 · open: 8 · closed: 1
- Total P&L on $1,000 per call: **$+347.91**
- Average vs the market: **+4.3%** · beat it: 7/9 · t-stat 1.86 (need about 2 and 20+ calls before it means anything)

## Every call

| # | posted | call | thesis | entry | now / exit | return | vs market | vs control | days | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2026-10-05 | LONG **MTUS** | [$125M funded DLA order under the $995M HF-1 steel stockpile IDIQ; Q3 (6 Nov) should show it in backlog and A&D sales](../stocks/MTUS.md) | $21.13 (2026-10-06) | $21.26 | +0.6% | +2.1% (IWM) | +5.2% (IIIN) | 24 | open |
| 2 | 2026-10-26 | AVOID **DFNS** | [Registered 19.0M sellable shares, 5.8x its 3.25M shares: a 10M-share equity line priced at 97.5% of the lowest 15-day VWAP plus PIPE resales; EFFECT 22 Oct](../research/daily/2026-10-26.md) | $3.91 (2026-10-27) | $3.50 | +10.5% | +11.3% (IWM) | +12.5% (ITA) | 3 | open |
| 3 | 2026-10-26 | AVOID **NCT** | [Registered direct of 15M new Class A shares at $1.30 ($19.5M), 4.8x the 3.12M shares outstanding, delivered 26 Oct; Monday's +17% to $1.48 hands those buyers an exit](../research/daily/2026-10-26.md) | $1.55 (2026-10-27) | $1.46 | +5.8% | +6.6% (IWM) | +0.6% (GLBS) | 3 | open |
| 4 | 2026-10-26 | AVOID **TMCR** | [F-1s effective 22 Oct: a $100M Yorkville standby equity line (23.6M shares, 35% of 67.4M) at 96% of market, plus 4.37M consideration shares free to sell now](../research/daily/2026-10-26.md) | $2.10 (2026-10-27) | $2.05 | +2.4% | +3.2% (IWM) | -3.9% (GROY) | 3 | open |
| 5 | 2026-10-26 | AVOID **OSTX** | [Warrant inducement at $1.30: 5.52M new shares (12% of 46.1M) issued with up to 3.93M more by 30 Oct and new $1.40 warrants capping rallies](../research/daily/2026-10-26.md) | $1.22 (2026-10-27) | $1.28 | -4.9% | -4.1% (IWM) | -0.5% (XBI) | 3 | open |
| 6 | 2026-10-27 | AVOID **NNBR** | [PIPE holders (AIGH, Alyeska, Polar, Special Situations, Empery) free to resell 16.1M shares (17.2% of 93.7M) since the 23 Oct EFFECT; the price sits 1.8% above their $3.30 cost](../research/daily/2026-10-27.md) | $3.60 (2026-10-28) | $3.96 | -10.0% | -8.7% (IWM) | -9.3% (XLI) | 1 | closed: invalidation close 3.96 vs 3.83 |
| 7 | 2026-10-27 | AVOID **NAUT** | [Unused $125M TD Cowen at-the-market programme, about 51M shares (40% of the company) at Monday's price, after a 2.5x run; -24.7% on Monday](../research/daily/2026-10-27.md) | $3.00 (2026-10-28) | $2.73 | +9.0% | +8.9% (IWM) | -8.4% (SEER) | 2 | open |
| 8 | 2026-10-28 | AVOID **WORX** | [Resale S-3 effective 26 Oct lets Iroquois and other warrant holders sell 8.25M shares (595% of 1.39M outstanding), with exercise-price resets; listing depends on a Nasdaq panel after two reverse splits this year](../research/daily/2026-10-28.md) | $1.83 (2026-10-29) | $1.60 | +12.6% | +11.8% (IWM) | +14.2% (XLV) | 1 | open |
| 9 | 2026-10-28 | AVOID **NIVF** | [Fourth reverse split since July (1:8 on 23 Oct) after a 30 Sep sale at $0.07; a $100M White Lion equity line and three convertible holders sell into any rise; new $100M F-3](../research/daily/2026-10-28.md) | $1.13 (2026-10-29) | $1.03 | +8.8% | +8.0% (IWM) | +10.5% (XLV) | 1 | open |

## Rules

1. A call is posted publicly (X) and added here in the same hour. The git commit time is the timestamp.
2. Entry is the next session's open. No cherry-picking a better fill.
3. Each call states its invalidation close and review date up front. It closes only by those rules.
4. Nothing is ever deleted or edited. A mistake gets a new row that says so.
5. Judge the record after 20+ closed calls, against the market and the controls, not by the best winner.
6. Long-term calls (horizon `long`) are measured against SPY and can also close on a pre-stated thesis break (for example the theme's segment revenue falling two quarters running), recorded in the exit columns with the reason.
