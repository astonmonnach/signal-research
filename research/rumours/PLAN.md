# Rumour trades: the six-month check (plan, written 13 Oct 2026, nothing run yet)

## The question
Does buying a US-listed stock at the close on the day a major outlet first reports takeover talks pay, after costs?
It came from Bumble: the Wall Street Journal reported talks on 12 Oct, the stock closed at $3.80, and the signed deal the next morning was $6.05.

## The sample (fixed before looking at any result)
- **Window:** reports first published from 13 Apr 2026 to 13 Oct 2026.
- **Outlets:** Wall Street Journal, Bloomberg, Reuters, Financial Times. Only the first report counts.
- **How they are found:** the news connector, searched month by month with the same phrases every month: "in advanced talks to be acquired", "in talks to be taken private", "nearing a deal to buy", "exploring a sale", "attracts takeover interest".
- **Every hit is kept whatever happened next.** The search is by date and phrase, never by company, because searching by company only finds the deals that happened.
- **Kept only if:** the target is US-listed, was $1 or more, and traded $250k a day or more before the report. Reports that follow a company announcement are left out.

## What is recorded for each report
- Date and time, outlet, target, and whether a buyer is named.
- The wording: advanced talks, early talks, or exploring.
- Whether a value or a price per share is given. If only a value is given, the price per share it implies read two ways: as equity, and as including debt.
- The close before the report, the close on the report day, and the next open.

## What is measured
- Was a deal signed within 30 and within 90 days, and at what price.
- The return from the report-day close to: the next open, 5 trading days, 20 trading days, and the day after signing (or day 60 if none). Each against IWM.
- The worst point on the way.

## The two results that matter
1. **All reports:** average and middle return from the report-day close to 20 trading days, after 1% costs.
2. **The narrow slice:** named buyer, "advanced" wording, a price per share that can be worked out, and the stock at least 10% below that price at the close.

## Pass mark
The narrow slice has 10 or more cases, a middle return above zero and an average above zero after costs. If it passes, new reports are logged in the daily run on paper. If it fails, the idea is dropped and not re-cut.

## Known weaknesses
- News search still favours stories that came true. The count of hits per month is recorded so a thin month shows.
- Six months is one market mood.
- The first minutes after a report cannot be traded from the UK reliably, so the entry is the close, not the headline.
