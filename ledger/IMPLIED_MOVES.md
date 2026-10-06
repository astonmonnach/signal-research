# Options: expected move vs actual move

Paper only. Before each dated event we record the move the options market expects (the at-the-money straddle). After expiry we record the move that happened, and what buying that straddle would have made. The question: does nth know better than the options market how big a move will be? Judge after 20-30 settled events. Built by `collectors/implied_moves.py` from CBOE delayed quotes.

**Settled:** 0 (none yet)

| logged | ticker | event | event date | expiry | spot | expected move | straddle cost | spread | nth view | actual | straddle result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-06 | MOD | THRM pays $2.07 special dividend; MOD pro forma 8-K/A due | 2026-10-07 | 2026-10-16 | $191.01 | ±9.6% | $18.20 @ 190.0 | 18.5% | - | open |  |
| 2026-10-06 | THRM | THRM pays $2.07 special dividend; MOD pro forma 8-K/A due | 2026-10-07 | 2026-10-16 | $32.30 | ±8.9% | $2.60 @ 32.93 | 47.5% | - | open |  |
| 2026-10-06 | HZO | HZO antitrust (HSR) waiting period ends | 2026-10-30 | 2026-11-20 | $52.35 | ±10.0% | $5.22 @ 50.0 | 175.8% | - | open |  |
| 2026-10-06 | MTUS | MTUS Q3 earnings call: thesis check for trade #1 | 2026-11-06 | 2026-11-20 | $21.04 | ±12.7% | $2.65 @ 20.0 | 13.7% | - | open |  |
| 2026-10-06 | HZO | HZO merger vote ($53 cash) | 2026-11-11 | 2026-11-20 | $52.35 | ±10.0% | $5.22 @ 50.0 | 175.8% | - | open |  |
| 2026-10-06 | MOD | MOD Investor Day (continuing business outlook) | 2026-11-18 | 2026-11-20 | $191.01 | ±22.4% | $42.50 @ 190.0 | 11.8% | - | open |  |
