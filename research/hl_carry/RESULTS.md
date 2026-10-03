# Results: Hyperliquid BTC funding carry (spec frozen in PREREG.md)

## V1 always-on
Switches: 1  |  time in carry: 100.0%

| period | years | net on N | annualised on N | annualised on capital | months + | worst DD (on N) |
|---|---|---|---|---|---|---|
| ALL | 3.4 | 47.05% | 13.85% | **10.39%** | 88.1% | -1.12% |
| IS 2023-05→2024 | 1.64 | 32.73% | 19.92% | **14.94%** | 85.0% | -1.12% |
| OOS 2025→2026-10 | 1.75 | 14.32% | 8.17% | **6.13%** | 90.9% | -0.15% |

By calendar year (net on N, partial years marked): 2023*: +8.52%, 2024: +24.20%, 2025: +10.63%, 2026*: +3.69%

**Verdict: PASS** (OOS annualised on capital > 0 and full years 2024, 2025 > 0)

## V2 gated (24h mean > 0)
Switches: 189  |  time in carry: 88.7%

| period | years | net on N | annualised on N | annualised on capital | months + | worst DD (on N) |
|---|---|---|---|---|---|---|
| ALL | 3.4 | 20.41% | 6.01% | **4.51%** | 69.0% | -9.49% |
| IS 2023-05→2024 | 1.64 | 24.6% | 14.97% | **11.23%** | 80.0% | -4.66% |
| OOS 2025→2026-10 | 1.75 | -4.19% | -2.39% | **-1.79%** | 59.1% | -9.49% |

By calendar year (net on N, partial years marked): 2023*: +4.47%, 2024: +20.13%, 2025: +2.64%, 2026*: -6.83%

**Verdict: FAIL** (OOS annualised on capital > 0 and full years 2024, 2025 > 0)

## Context
Mean hourly funding annualised (gross, always short): 14.21% on N. Share of hours with negative funding: 12.8%.
Not modelled: spot–perp basis moves, liquidation of the short in a fast squeeze (3x margin), exchange risk.
