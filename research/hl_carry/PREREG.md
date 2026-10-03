# Pre-registration: BTC funding carry on Hyperliquid
Frozen 2026-10-03, BEFORE any result was computed. Changing anything below = a new trial, logged here.

## Question
Does the BTC delta-neutral funding carry that survived on Binance (+~5.9%/yr net, 2022–26; see human-project TRADING-RESEARCH/project_crypto_flow.md) also survive on **Hyperliquid's hourly funding**, net of realistic costs?

## Data
`hl_btc_funding.csv`: Hyperliquid public info API (`fundingHistory`, coin BTC), hourly, 2023-05-12 → 2026-10-03, 29,201 prints. Positive rate = longs pay shorts.

## Position
Short BTC perp (Hyperliquid) + long BTC spot, equal notional N. The short receives `rate × N` each hour (pays when the rate is negative). Price P&L is assumed hedged. **Basis and liquidation risk are NOT modelled**: they're listed as risks, not ignored.

## Costs (conservative, applied per leg per side)
- Perp taker 0.045% + spot taker 0.07% + slippage 0.02% per leg → **round trip, both legs = 0.31% of N**.
- Capital required = N (spot) + N/3 (perp margin at 3x) = **1.333 N**. Returns are reported on N **and** on capital.

## Variants (trial count = 2)
- **V1 always-on:** enter at the first print, hold to the end, one round trip.
- **V2 gated:** hold the carry only while the trailing 24-hour mean funding rate is > 0; otherwise flat. Each entry+exit pays 0.31%. The decision uses data up to t−1 only (no look-ahead).

## Split and pass mark
- In-sample (IS): 2023-05-12 → 2024-12-31. Out-of-sample (OOS): 2025-01-01 → 2026-10-03.
- **PASS** = OOS net annualised return on CAPITAL > 0 **and** every full calendar year net > 0, for that variant. Otherwise FAIL.
- Report: annualised net on N and on capital, by year, % of positive months, worst drawdown of the cumulative carry, number of switches (V2).

## Not tested here (separate trials if pursued)
Funding as a directional signal (already dead on Binance), other coins (SOL carry already failed), leverage above 3x.
