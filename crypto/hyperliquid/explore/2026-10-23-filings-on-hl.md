# Our SEC sections on Hyperliquid stock perps: a backdated check

Exploration, run 23 Oct 2026. Filing days 2026-03-29 to 2026-10-15. Not a pre-registered test.

Only what was known on the filing day T: a market counts only if it already traded on T; the side comes from the form type; entry is the next US business day at 13:00 UTC, before the cash open. Returns are in the direction of the side (a fall is a gain for a short). 'vs same market' subtracts that market's average move over every day in the window, so a short does not look good just because the stock fell all year. 'after cost' takes off an assumed 0.2% round trip; funding is not included. 'Takeable' = at least $500k traded on the market in the 24 hours before entry. The SHORT side and LONG side rows count a stock once per filing day; the section rows below them can share an event (an IPO's EFFECT and 424B4 land on the same day).

- Events found: 105 · with a Hyperliquid price at entry: 83 · takeable: 67

## All with a price

| group | horizon | n | mean | median | went our way | vs same market | after cost |
|---|---|---|---|---|---|---|---|
| SHORT side | 1 day | 49 | -0.87% | +0.13% | 26/49 | -1.06% | -1.07% |
| SHORT side | 5 days | 48 | +0.00% | +1.32% | 26/48 | -0.94% | -0.20% |
| LONG side | 1 day | 4 | +2.17% | +2.88% | 3/4 | +2.73% | +1.97% |
| LONG side | 5 days | 4 | -0.44% | +1.26% | 2/4 | +2.71% | -0.64% |
| Activists / new 5%+ holders | 1 day | 4 | +2.17% | +2.88% | 3/4 | +2.73% | +1.97% |
| Activists / new 5%+ holders | 5 days | 4 | -0.44% | +1.26% | 2/4 | +2.71% | -0.64% |
| Late filings | 1 day | 1 | +2.77% | +2.77% | 1/1 | +1.85% | +2.57% |
| Late filings | 5 days | 1 | +2.12% | +2.12% | 1/1 | -2.04% | +1.92% |
| Offering priced | 1 day | 4 | -7.22% | -7.07% | 1/4 | -7.51% | -7.42% |
| Offering priced | 5 days | 4 | -0.94% | -2.39% | 1/4 | -2.72% | -1.14% |
| Registrations effective | 1 day | 9 | -0.42% | +2.94% | 5/9 | -0.83% | -0.62% |
| Registrations effective | 5 days | 9 | +3.39% | +0.86% | 5/9 | +1.23% | +3.19% |
| Share registrations | 1 day | 3 | -7.56% | -6.38% | 1/3 | -8.38% | -7.76% |
| Share registrations | 5 days | 3 | +1.22% | +3.93% | 2/3 | -2.55% | +1.02% |
| Share sales and shelves | 1 day | 35 | -0.36% | +0.13% | 19/35 | -0.40% | -0.56% |
| Share sales and shelves | 5 days | 34 | -1.05% | +1.04% | 18/34 | -1.25% | -1.25% |

## Takeable only

| group | horizon | n | mean | median | went our way | vs same market | after cost |
|---|---|---|---|---|---|---|---|
| SHORT side | 1 day | 35 | -0.77% | +0.13% | 18/35 | -0.84% | -0.97% |
| SHORT side | 5 days | 35 | +0.75% | +0.86% | 19/35 | +0.35% | +0.55% |
| LONG side | 1 day | 3 | +2.02% | +3.14% | 2/3 | +2.39% | +1.82% |
| LONG side | 5 days | 3 | -2.90% | -4.46% | 1/3 | -0.45% | -3.10% |
| Activists / new 5%+ holders | 1 day | 3 | +2.02% | +3.14% | 2/3 | +2.39% | +1.82% |
| Activists / new 5%+ holders | 5 days | 3 | -2.90% | -4.46% | 1/3 | -0.45% | -3.10% |
| Offering priced | 1 day | 4 | -7.22% | -7.07% | 1/4 | -7.51% | -7.42% |
| Offering priced | 5 days | 4 | -0.94% | -2.39% | 1/4 | -2.72% | -1.14% |
| Registrations effective | 1 day | 8 | -0.43% | +3.10% | 5/8 | -0.76% | -0.63% |
| Registrations effective | 5 days | 8 | +2.40% | -0.10% | 4/8 | +0.63% | +2.20% |
| Share registrations | 1 day | 2 | -2.79% | -2.79% | 1/2 | -3.45% | -2.99% |
| Share registrations | 5 days | 2 | +4.76% | +4.76% | 2/2 | +1.72% | +4.56% |
| Share sales and shelves | 1 day | 24 | -0.47% | -0.11% | 12/24 | -0.39% | -0.67% |
| Share sales and shelves | 5 days | 24 | -0.07% | +1.04% | 13/24 | +0.33% | -0.27% |

## Every event

| filed | ticker | section | form | side | market | price move 1 day | price move 5 days | $ traded 24h before |
|---|---|---|---|---|---|---|---|---|
| 2026-03-30 | SHAZ | Activists / new 5%+ holders | SCHEDULE 13D | LONG | no Hyperliquid market on T | | | |
| 2026-04-01 | IONQ | Effective, not supply (S-4) | EFFECT | none | no Hyperliquid market on T | | | |
| 2026-04-06 | MRVL | Debt sale (prospectus for notes) | 424B5 | none | no Hyperliquid market on T | | | |
| 2026-04-08 | SHAZ | Activists / new 5%+ holders | SCHEDULE 13D | LONG | no Hyperliquid market on T | | | |
| 2026-04-13 | SHAZ | Activists / new 5%+ holders | SCHEDULE 13D | LONG | no Hyperliquid market on T | | | |
| 2026-04-17 | CBRS | Share registrations | S-1 | SHORT | no Hyperliquid market on T | | | |
| 2026-04-22 | SHAZ | Registrations effective | EFFECT | SHORT | no Hyperliquid market on T | | | |
| 2026-04-24 | BMNR | Share sales and shelves | S-3 | SHORT | km:BMNR | -4.2% | +0.7% | $0.3M |
| 2026-04-24 | GLW | Share sales and shelves | S-3ASR | SHORT | no Hyperliquid market on T | | | |
| 2026-04-27 | INTC | Debt sale (prospectus for notes) | 424B5 | none | cash:INTC | +5.6% | +22.1% | $36.3M |
| 2026-04-28 | BMNR | Share sales and shelves | S-3ASR | SHORT | km:BMNR | -2.9% | +8.4% | $0.1M |
| 2026-04-29 | BIRD | Share sales and shelves | 424B5 | SHORT | xyz:BIRD | +3.2% | -3.6% | $0.2M |
| 2026-04-29 | INTC | Debt sale (prospectus for notes) | 424B5 | none | xyz:INTC | -4.2% | +13.1% | $83.3M |
| 2026-04-30 | META | Share sales and shelves | S-3ASR | SHORT | xyz:META | -1.0% | +0.6% | $16.4M |
| 2026-04-30 | RIVN | Share sales and shelves | S-3ASR | SHORT | xyz:RIVN | -4.9% | -10.1% | $2.2M |
| 2026-05-04 | BMNR | Share sales and shelves | S-3ASR | SHORT | km:BMNR | -0.2% | -3.7% | $0.2M |
| 2026-05-04 | EBAY | Activists / new 5%+ holders | SCHEDULE 13D | LONG | no Hyperliquid market on T | | | |
| 2026-05-05 | GOOGL | Debt sale (prospectus for notes) | 424B5 | none | xyz:GOOGL | +1.6% | -2.1% | $20.5M |
| 2026-05-06 | BOT | Effective, not supply (N-2) | EFFECT | none | no Hyperliquid market on T | | | |
| 2026-05-08 | QNT | Share registrations | S-1 | SHORT | no Hyperliquid market on T | | | |
| 2026-05-11 | GOOGL | Debt sale (prospectus for notes) | 424B5 | none | xyz:GOOGL | -0.4% | +3.1% | $13.4M |
| 2026-05-13 | USAR | Share sales and shelves | S-3 | SHORT | xyz:USAR | -4.2% | -6.9% | $2.5M |
| 2026-05-14 | AAOI | Share sales and shelves | 424B5 | SHORT | no Hyperliquid market on T | | | |
| 2026-05-14 | CBRS | Offering priced | 424B4 | SHORT | xyz:CBRS | -4.0% | -7.2% | $298.6M |
| 2026-05-14 | CBRS | Registrations effective | EFFECT | SHORT | xyz:CBRS | -4.0% | -7.2% | $298.6M |
| 2026-05-18 | GOOGL | Debt sale (prospectus for notes) | 424B5 | none | xyz:GOOGL | -3.4% | -4.2% | $17.4M |
| 2026-05-20 | RKLB | Share sales and shelves | 424B5 | SHORT | xyz:RKLB | +4.3% | +17.9% | $10.0M |
| 2026-05-20 | SPCX | Share registrations | S-1 | SHORT | xyz:SPCX | -0.8% | -5.6% | $30.7M |
| 2026-05-22 | CBRS | Activists / new 5%+ holders | SCHEDULE 13D | LONG | xyz:CBRS | -1.8% | -12.0% | $2.6M |
| 2026-06-01 | GOOGL | Share sales and shelves | S-3ASR | SHORT | xyz:GOOGL | -2.0% | +0.2% | $32.7M |
| 2026-06-01 | TTWO | Share sales and shelves | S-3ASR | SHORT | no Hyperliquid market on T | | | |
| 2026-06-02 | GOOGL | Share sales and shelves | 424B5 | SHORT | xyz:GOOGL | +0.3% | +1.0% | $31.3M |
| 2026-06-03 | BMNR | Share sales and shelves | 424B5 | SHORT | km:BMNR | +0.6% | -5.2% | $0.3M |
| 2026-06-03 | COST | Share sales and shelves | S-3ASR | SHORT | xyz:COST | -1.0% | -0.3% | $0.6M |
| 2026-06-03 | GPRO | Registrations effective | EFFECT | SHORT | no Hyperliquid market on T | | | |
| 2026-06-04 | GOOGL | Share sales and shelves | 424B5 | SHORT | xyz:GOOGL | -0.1% | -1.8% | $20.1M |
| 2026-06-04 | QNT | Registrations effective | EFFECT | SHORT | xyz:QNT | -3.3% | -5.2% | $68.9M |
| 2026-06-05 | BMNR | Share sales and shelves | 424B5 | SHORT | km:BMNR | -0.0% |  | $0.1M |
| 2026-06-05 | CRWV | Share sales and shelves | S-3ASR | SHORT | xyz:CRWV | +1.7% | +1.9% | $4.0M |
| 2026-06-05 | QNT | Offering priced | 424B4 | SHORT | xyz:QNT | +6.6% | +0.6% | $0.9M |
| 2026-06-05 | SHAZ | Share registrations | S-1 | SHORT | no Hyperliquid market on T | | | |
| 2026-06-08 | AMZN | Debt sale (prospectus for notes) | 424B5 | none | xyz:AMZN | -1.8% | +0.1% | $5.4M |
| 2026-06-08 | USAR | Registrations effective | EFFECT | SHORT | xyz:USAR | -8.2% | +1.1% | $1.1M |
| 2026-06-09 | SMCI | Share sales and shelves | S-3ASR | SHORT | no Hyperliquid market on T | | | |
| 2026-06-10 | AMZN | Debt sale (prospectus for notes) | 424B5 | none | xyz:AMZN | +1.3% | -0.1% | $6.1M |
| 2026-06-10 | SMCI | Share sales and shelves | 424B5 | SHORT | no Hyperliquid market on T | | | |
| 2026-06-11 | BIRD | Share sales and shelves | 424B5 | SHORT | xyz:BIRD | -0.6% | +49.7% | $0.1M |
| 2026-06-11 | DELL | Share sales and shelves | S-3ASR | SHORT | xyz:DELL | +5.7% | +6.0% | $0.5M |
| 2026-06-12 | SHAZ | Registrations effective | EFFECT | SHORT | no Hyperliquid market on T | | | |
| 2026-06-12 | SMCI | Share sales and shelves | 424B5 | SHORT | no Hyperliquid market on T | | | |
| 2026-06-12 | SPCX | Offering priced | 424B4 | SHORT | xyz:SPCX | +18.7% | +4.2% | $159.0M |
| 2026-06-12 | SPCX | Registrations effective | EFFECT | SHORT | xyz:SPCX | +18.7% | +4.2% | $159.0M |
| 2026-06-15 | NVDA | Debt sale (prospectus for notes) | 424B5 | none | xyz:NVDA | -1.2% | -3.8% | $47.5M |
| 2026-06-17 | NVDA | Debt sale (prospectus for notes) | 424B5 | none | xyz:NVDA | +0.8% | -2.8% | $39.9M |
| 2026-06-18 | AVGO | Effective, not supply (S-4) | EFFECT | none | xyz:AVGO | +0.8% | -9.6% | $2.5M |
| 2026-06-18 | TWST | Share sales and shelves | S-3ASR | SHORT | no Hyperliquid market on T | | | |
| 2026-06-23 | ORCL | Share sales and shelves | 424B5 | SHORT | xyz:ORCL | -3.7% | -11.9% | $8.0M |
| 2026-06-23 | STRC | Share sales and shelves | 424B5 | SHORT | xyz:STRC | -7.1% | -3.9% | $0.6M |
| 2026-06-30 | USAR | Effective, not supply (S-4) | EFFECT | none | xyz:USAR | -5.2% | -18.1% | $0.5M |
| 2026-07-06 | RIVN | Share sales and shelves | 424B5 | SHORT | xyz:RIVN | -12.2% | -3.0% | $2.1M |
| 2026-07-07 | AMZN | Debt sale (prospectus for notes) | 424B5 | none | xyz:AMZN | -1.4% | +2.4% | $13.4M |
| 2026-07-08 | AMZN | Debt sale (prospectus for notes) | 424B5 | none | xyz:AMZN | +3.4% | +6.3% | $7.7M |
| 2026-07-08 | RIVN | Share sales and shelves | 424B5 | SHORT | xyz:RIVN | +10.0% | +6.4% | $1.8M |
| 2026-07-10 | SKHY | Effective, not supply (F-6) | EFFECT | none | xyz:SKHY | +7.6% | +6.1% | $148.8M |
| 2026-07-10 | SKHY | Offering priced | 424B4 | SHORT | xyz:SKHY | +7.6% | +6.1% | $148.8M |
| 2026-07-10 | SKHY | Registrations effective | EFFECT | SHORT | xyz:SKHY | +7.6% | +6.1% | $148.8M |
| 2026-07-17 | BOT | Effective, not supply (N-2) | EFFECT | none | xyz:BOT | -5.2% | -11.4% | $1.1M |
| 2026-07-21 | NFLX | Debt sale (prospectus for notes) | 424B5 | none | xyz:NFLX | -0.1% | +5.2% | $4.7M |
| 2026-07-31 | SHAZ | Share registrations | S-1 | SHORT | xyz:SHAZ | +17.1% | +5.9% | $0.5M |
| 2026-08-04 | TWST | Share sales and shelves | 424B5 | SHORT | no Hyperliquid market on T | | | |
| 2026-08-05 | CRCL | Share sales and shelves | S-3ASR | SHORT | xyz:CRCL | +5.8% | +14.7% | $38.0M |
| 2026-08-05 | TWST | Share sales and shelves | 424B5 | SHORT | no Hyperliquid market on T | | | |
| 2026-08-06 | GOOGL | Debt sale (prospectus for notes) | 424B5 | none | xyz:GOOGL | -0.7% | -3.4% | $30.8M |
| 2026-08-06 | GOOGL | Share sales and shelves | 424B5 | SHORT | xyz:GOOGL | -0.7% | -3.4% | $30.8M |
| 2026-08-07 | BOT | Effective, not supply (N-2) | EFFECT | none | xyz:BOT | -0.6% | +15.8% | $0.2M |
| 2026-08-10 | INTC | Share sales and shelves | 424B5 | SHORT | xyz:INTC | +2.9% | +1.4% | $40.8M |
| 2026-08-11 | IBM | Debt sale (prospectus for notes) | 424B5 | none | xyz:IBM | +1.3% | -1.4% | $1.1M |
| 2026-08-12 | INTC | Share sales and shelves | 424B5 | SHORT | xyz:INTC | +4.2% | -9.4% | $79.2M |
| 2026-08-12 | SHAZ | Share registrations | S-1 | SHORT | xyz:SHAZ | +6.4% | -3.9% | $2.0M |
| 2026-08-13 | AMD | Debt sale (prospectus for notes) | 424B5 | none | xyz:AMD | +5.5% | -2.2% | $9.7M |
| 2026-08-13 | AMD | Share sales and shelves | S-3ASR | SHORT | xyz:AMD | +5.5% | -2.2% | $9.7M |
| 2026-08-13 | RKLB | Share sales and shelves | 424B5 | SHORT | xyz:RKLB | -0.8% | -8.7% | $4.5M |
| 2026-08-14 | AMD | Debt sale (prospectus for notes) | 424B5 | none | xyz:AMD | -4.7% | -9.4% | $6.1M |
| 2026-08-17 | BIRD | Late filings | NT 10-Q | SHORT | xyz:BIRD | -2.8% | -2.1% | $0.1M |
| 2026-08-17 | SHAZ | Registrations effective | EFFECT | SHORT | xyz:SHAZ | -4.8% | -18.8% | $2.0M |
| 2026-08-19 | AMZN | Effective, not supply (S-4) | EFFECT | none | xyz:AMZN | -0.8% | -1.3% | $11.7M |
| 2026-08-21 | AAOI | Share sales and shelves | 424B5 | SHORT | xyz:AAOI | +3.3% | -3.1% | $1.0M |
| 2026-08-24 | SHAZ | Registrations effective | EFFECT | SHORT | xyz:SHAZ | +0.3% | -11.3% | $0.3M |
| 2026-08-27 | RKLB | Effective, not supply (S-4) | EFFECT | none | xyz:RKLB | -5.5% | -3.7% | $1.5M |
| 2026-08-28 | SHAZ | Activists / new 5%+ holders | SCHEDULE 13D | LONG | xyz:SHAZ | +2.6% | +7.0% | $0.2M |
| 2026-09-04 | USAR | Share sales and shelves | S-3 | SHORT | xyz:USAR | -0.2% | -14.4% | $0.1M |
| 2026-09-09 | AMZN | Debt sale (prospectus for notes) | 424B5 | none | xyz:AMZN | +1.8% | +0.4% | $6.1M |
| 2026-09-09 | GPRO | Activists / new 5%+ holders | SCHEDULE 13D | LONG | io:GPRO | +4.7% | -4.5% | $0.7M |
| 2026-09-09 | VST | Share sales and shelves | S-3ASR | SHORT | para:VST | +1.2% | -2.2% | $0.2M |
| 2026-09-10 | VST | Debt sale (prospectus for notes) | 424B5 | none | para:VST | -3.9% | -4.3% | $0.7M |
| 2026-09-11 | AMZN | Debt sale (prospectus for notes) | 424B5 | none | xyz:AMZN | -0.4% | +0.5% | $6.1M |
| 2026-09-11 | CRWD | Share sales and shelves | S-3ASR | SHORT | xyz:CRWD | +5.8% | +8.7% | $0.6M |
| 2026-09-11 | GLW | Share sales and shelves | 424B5 | SHORT | para:GLW | -3.5% | +4.0% | $0.1M |
| 2026-09-11 | USAR | Activists / new 5%+ holders | SCHEDULE 13D | LONG | xyz:USAR | +3.1% | +7.7% | $0.6M |
| 2026-09-16 | USAR | Registrations effective | EFFECT | SHORT | xyz:USAR | +0.3% | -0.9% | $0.9M |
| 2026-09-17 | CRWV | Share sales and shelves | 424B5 | SHORT | xyz:CRWV | +2.0% | +13.9% | $10.7M |
| 2026-09-21 | AVGO | Effective, not supply (S-4) | EFFECT | none | xyz:AVGO | -0.2% | -2.6% | $13.7M |
| 2026-10-02 | QCOM | Share sales and shelves | S-3 | SHORT | xyz:QCOM | -2.7% | -6.2% | $2.9M |
| 2026-10-13 | QCOM | Registrations effective | EFFECT | SHORT | xyz:QCOM | -2.9% | +1.4% | $1.1M |
| 2026-10-14 | IONQ | Share sales and shelves | 424B5 | SHORT | io:IONQ | +7.9% | +0.1% | $0.2M |
