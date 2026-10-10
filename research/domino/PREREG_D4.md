# D4: the scorecard (does the business hold up?)

Status: **rules written and committed on 2026-10-10, before any scorecard number was computed.** Descriptive, like D3: no pass mark, and whatever looks good becomes a written rule judged on new trades.

D3 left 4,569 trades in 531 stocks (kept industries, takeable, not China/HK, no recent reverse split). That is still about 2,500 trades a year. The aim here is to get that towards something a person can take (about 100 a year) by asking of each company, using only what it had **already filed on the day of the trade**: is this a real business that can pay its bills and isn't printing shares?

## One correction first

Looking at the biggest winners in D3 showed two that no plan should lean on:

- **WOLF, +904%**: Wolfspeed's bankruptcy share exchange on 29 Sep 2025 (old shares swapped for a small fraction of new ones). The price series doesn't know about it. A holder lost about 90%.
- **TCGL, +1,982%**: a real two-day run from $8 to $173, after which the stock has no prices at all (trading stopped).

Rule for D4, applied to followers and controls alike: **any return above +300% is counted as +300%.** D3's stage-3 numbers are restated with the same cap so the two can be compared.

## Data

SEC XBRL "company facts" for each of the 531 companies. For a trade on day d, only facts with a filing date on or before d are used. US filers' tags (us-gaap) and foreign filers' tags (ifrs-full) are both read. Values not reported in US dollars are treated as unknown.

## The three questions

| | Question | Passes if |
|---|---|---|
| **R** | Is it a real business? | Revenue in its latest annual report was **$10M or more** |
| **C** | Can it pay its bills? | Operating cash flow in its latest annual report was positive, **or** its latest reported cash covers **12 months or more** of that year's cash burn |
| **D** | Is it printing shares? | Its share count grew by **less than 25%** over the previous year (latest reported count against the count reported 9 to 15 months earlier) |

- **Score** = how many of the three it passes (0 to 3). "Holds up" = 3 of 3.
- If a question can't be answered from filings made before the trade, the trade goes in an **unknown** bucket, shown separately and never counted as a pass.

## What is reported

For score 3, score 2, score 0-1 and unknown, and for score 3 with the follower's own volume at 2x or more:

- trades, different stocks, trades per year, signal days and stocks per signal day;
- returns after 1, 5 and 10 days: average (capped), median, share positive;
- edge over the D3 controls after 5 and 10 days, with a 95% interval (5-day block bootstrap over days);
- how often +20% and +50% were reached within 5 and 10 days, and the average worst point within 10 days;
- the return after 1% and 3.5% costs.

Stated in advance: if quality matters, **score 3 should have a better median and a better edge than score 0-1**. If the low scores do better, the effect lives in junk, and that will be said plainly.

No other cuts.
