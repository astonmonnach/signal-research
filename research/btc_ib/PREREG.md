# Pre-registration: BTC session range-break retest (mechanical range skeleton)
Frozen 2026-10-03, BEFORE any result. Any change = a new, logged trial.

## Idea
A mechanical version of his range skeleton, applied per session: the session's opening range = the box (0 / 0.5 / 1). A break of one edge, a retest of the broken edge, with 0.5 as invalidation, targeting 2R. At most one trade per session = **at most 3 trades a day**. "Decent moves" is enforced by a minimum range width.

## Data
Desktop/crypto-flow/btcusdt_flow_1m.parquet: Binance BTCUSDT perp 1m, 2022-01-01 → 2026-07-05 (gaps exist; sessions with any missing minute in the opening range are skipped).
**In-sample:** 2022-01-01 → 2024-12-31. **Out-of-sample:** 2025-01-01 → 2026-07-05.

## Rules (UTC)
- Sessions: Asia 00:00, London 07:00, New York 13:30. Opening range (OR) = high/low of the first **60 minutes**.
- **Width filter:** OR width ≥ **0.30%** of the OR midpoint; otherwise there's no trade that session.
- **Break:** the first 5-minute close beyond an OR edge, within 4h of the session start. Direction = the side of the break.
- **Entry:** a limit order at the broken edge (the retest), live from the break until 4h after the session start. It fills only if price trades **through** the level by ≥ 1 tick ($0.10). It's cancelled if price touches the OR midpoint before the fill.
- **Stop:** the OR midpoint (0.5). **Target:** 2R from entry. **Time exit:** at the next session's start, at the close.
- If the stop and target are both inside the same 1m bar → **stop first** (conservative).
- One trade per session, at most 3 per UTC day.

## Costs (Hyperliquid base tier, conservative)
Entry maker 0.015%, exit taker 0.045% (target or time) / taker + 0.02% slippage (stop). Results are in R and in % of notional, net.

## Variants (trial count = 2)
- **A:** all days.
- **B:** only days where the prior UTC day's range ≥ the trailing 60-day median daily range (the regime gate from WHEN-not-WHAT, no look-ahead).

## Pass mark (per variant)
OOS profit factor ≥ **1.20** net, **≥ 150 OOS trades**, OOS net expectancy > 0 in **both** 2025 and 2026H1, and IS net expectancy > 0. Then an **independent rebuild** from this spec must reproduce it before any paper trading.

## Reported
Trades per day, win rate, avg R, PF, net expectancy (R and %), max drawdown in R, by session, by year, IS vs OOS, plus results with the top 5% of trades removed.
