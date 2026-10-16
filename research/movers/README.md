# Daily movers log

One row per stock for the ten biggest US gainers of each session, with why it moved. Started 13 Oct 2026.
The aim is to collect first and judge later: no verdicts and no deep dives until there are at least 20 sessions in `movers.csv`.

- **Where the list comes from:** the gainers table at stockanalysis.com (the market-data connector's all-market bars were not answering on 13 Oct; use them when they work).
- **Why it moved:** one line from the company's own release or filing where there is one, found with the news connector. "No company news found" is a valid answer and is recorded as `no_news`.
- **reason_type** is one of: `deal_signed`, `deal_rumour`, `acquisition_financing`, `contract_pr`, `product_pr`, `earnings`, `clinical`, `filing_6k`, `financing`, `no_news`, `other`.
- **Mechanics, from 14 Oct onward** (added because "no news" is never the whole answer): shares in existence, turnover as a multiple of the whole share count, past +50% days, share-sale or resale filings in the last 60 days, listing-deficiency notices, whether options are listed, and same-theme movers that day.
- Rows are never edited after the day. What happened next is measured later from prices.

Day one, 13 Oct 2026: nine of the ten were under $60M in market value, five had no company news, and one (Bumble) was a signed deal in a liquid stock.

## How the list is built (from the 14 Oct session)

- Massive grouped daily bars (unadjusted, all US-listed stocks) for the session and the sessions before it. The move is the close against the stock's previous close, adjusted for any split in between (Massive split list).
- Common stocks and ADRs only: tickers in the Nasdaq stock screener, with warrants, units, rights, preferreds, notes and ETFs dropped. No minimum price or volume, the same as the stockanalysis.com table (which lists sub-$1 and thin stocks).
- Check: this method gives the same ten names, in the same order, with the same % moves as the 13 Oct rows taken from stockanalysis.com.
- Volume is the Massive figure for the day. It can differ a little from stockanalysis.com.

## Mechanics columns (filled for every row, 13 Oct included)

- `shares_m`: shares in existence, in millions: Nasdaq screener market value divided by its price, read on 16 Oct (ADS count for ADRs). A count stated in a filing dated in the 5 days up to the day is used instead. `shares_src` names the source and gives the SEC cover count where it is missing, stale or more than 20% away.
- `turnover`: the day's volume divided by `shares_m`. For rows from 14 Oct, `mcap_musd` is `shares_m` times the close.
- `spikes50_1y`: days of +50% or more (close against previous close, split-adjusted) in the 250 sessions before the day. From `research/runners/work/raw` and Massive bars after 9 Oct, checked against Yahoo daily bars; differences settled by hand.
- `supply_60d`: S-1, F-1, S-3, F-3 (and amendments), any 424B and EFFECT filed on EDGAR in the 60 calendar days up to and including the day.
- `deficiency_1y`: exchange listing-deficiency notices in the year up to the day: 8-K Item 3.01, and for 6-K filers a text search of every 6-K. A 3.01 that only records a SPAC listing transfer is not counted.
- `options`: listed options on 16 Oct, from the Nasdaq option-chain page (Massive options reference where Nasdaq failed).
- `same_theme`: other names in the day's 30 biggest common-stock gainers with the same story or niche, judged from releases and business descriptions. A shared broad sector alone is written as "none (sector only)".
