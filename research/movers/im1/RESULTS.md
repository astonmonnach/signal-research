# IM1 results: buying the pump at +20% and selling two hours later did not pay

Pre-registration: `../PREREG_IM1.md` (git 210adc4), committed before any intraday price was looked at. Run on
29 Oct 2026. Sample: `sample.csv` (200 events, seed 20261029, from a pool of 17,319). Per-event rows:
`events_raw.csv` (from `extract.sql` run through the market-data connector, collected by `python run.py ingest`).
Scored by `python run.py` -> `results.json` and `trades.csv`. Nothing in the rules changed.

## Verdict: DOES NOT PAY (fails all three pass marks)

| pass mark (2% costs) | result | passed? |
|---|---|---|
| mean above zero | -3.32% | no |
| 95% interval above zero | -5.23% to -1.48% | no |
| mean above zero in both halves | -3.08% (n 74) and -3.52% (n 91) | no |

It fails at 1% costs too (mean -2.32%, interval -4.23% to -0.48%). Before any costs the mean is -1.32% and the
median -1.03%: the trade loses money even if trading were free.

## Counts
- 200 sampled. 3 had no regular-session print at +20% (the move came before or after hours). 32 triggered at
  14:00 or later (reported, not tested). **165 tested.** No event was lost to missing data.

## What the trades looked like (2% costs)

| exit | mean | median | winners | up 10%+ | down 10%+ |
|---|---|---|---|---|---|
| 30 minutes | -2.73% | -2.92% | 24% | 5.5% | 15.2% |
| 60 minutes | -3.39% | -3.50% | 27% | 7.3% | 18.8% |
| **120 minutes (tested)** | **-3.32%** | **-3.03%** | **33%** | **8.5%** | **23.6%** |
| at the close | -2.71% | -3.13% | 36% | 12.7% | 27.3% |

- No holding time works: every exit from 30 minutes to the close loses on average.
- Gap-ups bought at the open (n 52): mean -4.96%. Stocks that crossed +20% during the session (n 113): -2.57%.
- Previous close $1 to $3 (n 55): -3.37%. $3 and up (n 110): -3.30%.
- Entry 09:30 to 09:59 (n 87): -3.24%. 10:00 to 11:29 (n 39): -1.84%. 11:30 to 13:59 (n 39): -4.99%.
- In the two hours after entry, the median best high was +4.1% above entry and the median worst low -6.7% below.
- Largest single loss: FTEL on 18 Dec 2024, -84% in two hours. Without it the mean is still -2.8% after costs.
- Largest gain: USDE on 21 Aug 2026, +43%.

## Caveats
- The panel's "common stock" list includes some leveraged and inverse funds (for example GDXD, TSLZ, ETHD); they
  stay in, as the rules say.
- Fills are modelled at the +20% level or the bar's open. Real buy-stops in fast stocks often fill worse, so the
  true result is likely a little worse than shown.
- Exits use the next traded minute; a halt means waiting for the reopen, as it would in real trading.

## What it means
Buying a stock the moment it is up 20% and holding for minutes or hours lost money in this sample, in both years,
at every cost level and every holding time tested. Under the pre-registration this version of "buy the pump" is
dropped. Any change to the trigger, entry or exit is a new study (IM2).
