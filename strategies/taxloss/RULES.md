# Tax-loss rebound: buy December losers once the selling ends
Stage: RETIRED (at this account size) · Created: 2026-09-30

> **Retired 2026-09-30.** It met both kill rules: the median net of fees is negative in every variant, and the one positive mean came from a single stock (BNAI, +967%). The test only covers the 2025 season plus a 2024 proxy, because the data plan only goes back to Sep 2024. That makes it underpowered. Revisit only with pre-2024 data **and** a position size where fees are under 1%. See `backtest-2026-09-30.md`.

## Why it should work
- **Who is on the other side:** US taxable investors selling their losing stocks before 31 Dec to offset capital gains.
- **Why they're forced:** the tax deadline is fixed, so they sell for the calendar, not for the business.
- **Why it isn't arbitraged away:** it mostly sits in small, illiquid losers that big funds avoid, and buying the year's worst stocks is uncomfortable.
- **Evidence:** the "January effect" literature (e.g. Roll 1983; Reinganum 1983). The effect has reportedly weakened since those papers, so **our own backtest decides**: `backtest-2026-09-30.md`.

## Trigger
Early December: a scan for stocks down ≥40% year-to-date that still pass the tradability filters.

## Entry rules (draft, to be fixed by the backtest)
1. Down ≥40% YTD by mid-December.
2. Price and liquidity filters from the backtest's best variant.
3. The four-question thesis is written. The business isn't about to fail: check for a going-concern warning, cash runway and pending dilution filings.
4. Enter in the last weeks of December.

## Exit rules
- Time exit: end of January.
- Invalidation: a new dilution filing (S-1/S-3/424B5) or a going-concern warning → out.

## Sizing
£40–50, max 3 positions.

## What would prove this wrong
The backtest median net of fees is ≤ 0, or the result depends on a handful of huge winners.

## Change log
- 2026-09-30: created. Backtest running.
