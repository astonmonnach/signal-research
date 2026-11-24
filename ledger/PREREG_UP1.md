# UP1: the buy-side rule, fixed before the first call (24 Nov 2026)

Written on 24 Nov 2026 at the trader's request ("Yeah I like this"), before any call under it was entered. The numbers below do not change while the test runs; a change makes a new rule (UP2) with its own record.

## Why this rule
- Buying everything we flag lost money (112 buy-side finds since 29 Sep, $70 each, +20% target or -$10 stop: about -$350 in all; research note 2026-11-24 and the 23 Nov chat test).
- The WATCH-grade finds under $5 did better (4 of 7 hit +20% first; small sample).
- On the path of 45 listed finds, the first 10% move pointed the way in most cases: 10 of 14 "up 10% first" were still up, and 15 of 17 "down 10% first" were still down (24 Nov, hindsight, not a rule until tested).
- Many finds peaked 25-75% and gave it back, so the exit matters as much as the pick.
- Research often gives a ceiling: a deal or tender price, a big buyer's price, cash or asset value per share.

## Who qualifies
A name the research run made WATCH (or better), with a dated trigger row in ledger/triggers.csv, that is:
- buyable by a UK retail client (not a US fund without a PRIIPs KID; ledger/not_buyable_uk.csv),
- $1 or more, with a 20-day median of $150k a day or more,
- logged in calls/CALLS.csv with direction 1 and horizon `up1` in the same hour it is posted, with its evidence file (calls/evidence/<id>.csv).

## Entry and exits (closing prices)
- **Entry:** the first US open after the call is logged.
- **Stop:** out on a close 10% or more below the entry.
- **Research ceiling:** if the call states one (column `target`, with its source in the evidence file), out on a close at or above it.
- **Trailing exit:** once any close is 20% or more above the entry, out on a close 10% below the highest close so far.
- **Time:** otherwise out at the close on the review date, 20 trading days after entry.
- Whichever comes first. Marked by calls/build_calls.py (horizon `up1`), against IWM and a named control.

## How it is judged
- After 20 closed UP1 calls: the average return, the share that made money, and the average against IWM, all before and after a 3.5% round-trip cost.
- Real money is the trader's own decision at any time; the record counts the rule, not his trades.
- Every call stays on the record, wrong ones included.
