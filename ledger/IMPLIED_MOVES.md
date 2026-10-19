# Options: expected move vs actual move

Paper only. Before each dated event we record the move the options market expects (the at-the-money straddle). After expiry we record the move that happened, and what buying that straddle would have made. The question: does nth know better than the options market how big a move will be? Judge after 20-30 settled events. Built by `collectors/implied_moves.py` from CBOE delayed quotes.

**Settled:** 3 · actual move bigger than expected in 2/3 · average straddle result +37.7%

| logged | ticker | event | event date | expiry | spot | expected move | straddle cost | spread | nth view | actual | straddle result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-06 | MOD | THRM pays $2.07 special dividend; MOD pro forma 8-K/A due | 2026-10-07 | 2026-10-16 | $191.01 | ±9.6% | $18.20 @ 190.0 | 18.5% | - | 22.1% | 126.0% |
| 2026-10-06 | THRM | THRM pays $2.07 special dividend; MOD pro forma 8-K/A due | 2026-10-07 | 2026-10-16 | $32.30 | ±8.9% | $2.60 @ 32.93 | 47.5% | - | 10.1% | 49.6% |
| 2026-10-12 | SKYA | SKYA: $3.00 issuer tender due to start; offer papers (SC TO- | 2026-10-15 | 2026-10-16 | $2.58 | ±15.5% | $0.40 @ 2.5 | 25.4% | smaller | 2.7% | -62.5% |
| 2026-10-12 | MSGS | MSGS: record date for the Rangers spin-off (1 MSGR per 2 MSG | 2026-10-20 | 2026-11-20 | $402.30 | ±7.3% | $29.45 @ 400.0 | 16.7% | none | open |  |
| 2026-10-12 | MSGS | MSGS: Rangers spin-off effective; MSGS becomes MSGK | 2026-10-26 | 2026-11-20 | $402.30 | ±7.3% | $29.45 @ 400.0 | 16.7% | none | open |  |
| 2026-10-19 | SKYA | SKYA: $3.00 tender expires one minute after 11:59 pm New Yor | 2026-10-29 | 2026-11-20 | $2.57 | ±42.5% | $1.02 @ 2.5 | 50.2% | - | open |  |
| 2026-10-06 | HZO | HZO antitrust (HSR) waiting period ends | 2026-10-30 | 2026-11-20 | $52.35 | ±10.0% | $5.22 @ 50.0 | 175.8% | smaller | open |  |
| 2026-10-06 | MTUS | MTUS Q3 earnings call: thesis check for trade #1 | 2026-11-03 | 2026-11-20 | $21.04 | ±12.7% | $2.65 @ 20.0 | 13.7% | none | open |  |
| 2026-10-14 | MTUS | MTUS Q3 earnings call 14:00 UK: thesis check for trade #1 (r | 2026-11-03 | 2026-11-20 | $20.56 | ±10.3% | $1.93 @ 20.0 | 55.2% | none | open |  |
| 2026-10-06 | HZO | HZO merger vote ($53 cash) | 2026-11-11 | 2026-11-20 | $52.35 | ±10.0% | $5.22 @ 50.0 | 175.8% | smaller | open |  |
| 2026-10-06 | MOD | MOD Investor Day (continuing business outlook) | 2026-11-18 | 2026-11-20 | $191.01 | ±22.4% | $42.50 @ 190.0 | 11.8% | smaller | open |  |
| 2026-10-07 | WHF | WHF: $85M notes mature in December, check refinancing | 2026-12-01 | 2027-01-15 | $7.00 | ±18.2% | $1.27 @ 7.5 | 146.0% | none | open |  |
| 2026-10-13 | HZO | HZO earliest close | 2026-12-07 | 2027-01-15 | $52.33 | ±6.1% | $3.18 @ 50.0 | 82.9% | smaller | open |  |
| 2026-10-16 | RYAM | RYAM: company promised a clear path forward in Q4 2026 | 2026-12-15 | 2026-12-18 | $7.11 | ±20.3% | $1.38 @ 7.0 | 100.0% | none | open |  |
