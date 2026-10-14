# Daily movers log

One row per stock for the ten biggest US gainers of each session, with why it moved. Started 13 Oct 2026.
The aim is to collect first and judge later: no verdicts and no deep dives until there are at least 20 sessions in `movers.csv`.

- **Where the list comes from:** the gainers table at stockanalysis.com (the market-data connector's all-market bars were not answering on 13 Oct; use them when they work).
- **Why it moved:** one line from the company's own release or filing where there is one, found with the news connector. "No company news found" is a valid answer and is recorded as `no_news`.
- **reason_type** is one of: `deal_signed`, `deal_rumour`, `acquisition_financing`, `contract_pr`, `product_pr`, `earnings`, `clinical`, `filing_6k`, `financing`, `no_news`, `other`.
- **Mechanics, from 14 Oct onward** (added because "no news" is never the whole answer): shares in existence, turnover as a multiple of the whole share count, past +50% days, share-sale or resale filings in the last 60 days, listing-deficiency notices, whether options are listed, and same-theme movers that day.
- Rows are never edited after the day. What happened next is measured later from prices.

Day one, 13 Oct 2026: nine of the ten were under $60M in market value, five had no company news, and one (Bumble) was a signed deal in a liquid stock.
