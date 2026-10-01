# Spin-offs: buy after the unwanted shares are sold
Stage: RETIRED (rule v1) · Created: 2026-09-30

> **Retired 2026-09-30.** The backtest covered 22 US spin-offs, Oct 2024 – Aug 2026 (`backtest-2026-09-30.md`). With the rule and its stop, the median result was **−11.5% net** and only 2 of 22 beat SPY. The entry fired on day 11 in 15 of 22 cases, but the real low typically came around **day 28** (median 14% below the day-1 close). So the rule bought too early. The stop then sold 18 of 22, including SOLS, MRP, RHLD and TRAX before they rallied 42–96%.
> **The one hint:** small spins (< $2bn) bought and held from day 1 returned +13.5% net at 60 days (n=7, beat SPY by 6.9%). That's too few to trust. Possible v2 at IDEA stage: small spins, entry after ~day 25–30, 3–6 month hold, no tight stop. It needs out-of-sample testing on pre-2024 spins first.

## Why it should work
- **Who is on the other side:** parent-company holders who receive shares they never chose, including index funds whose index doesn't include the spin-off, and funds with size or sector limits.
- **Why they're forced:** they sell regardless of price, and usually in the first weeks.
- **Why it isn't arbitraged away:** big funds can't take size in small spins, and buying something "everyone is selling" feels wrong.
- **Evidence:** Cusatis, Miles & Woolridge (1993), *Journal of Financial Economics*: spin-offs outperformed over the 3 years after the spin. Greenblatt, *You Can Be a Stock Market Genius*, ch. 3. **To do:** our own backtest on recent spins (2015–2025).

## Trigger
- `watch/scan_market.py` flags new Form 10-12B and 10-12B/A filings.
- The distribution date comes from the parent's 8-K. Add it to the calendar.

## Entry rules
1. Never on day one. Wait at least 10 trading days after regular-way trading starts.
2. The nth-order deep dive is done, and the business-quality answer is positive.
3. The selling looks exhausted: volume falls back towards normal and the price stops making new lows for 5 days.
4. Written thesis in `ideas/TICKER.md` before entry.

## Exit rules
- Invalidation: close below the post-spin low → out.
- Thesis check at the first standalone quarterly results.
- Time stop: 6 months, then reassess.

## Sizing
£40–50, max 2 open spin-off positions.

## What would prove this wrong
Our own backtest shows no post-spin rebound net of fees, or 20 live trades lose money after fees.

## Change log
- 2026-09-30: created. First case: VYLR (Corteva seed spin, trading from 1 Oct 2026).
