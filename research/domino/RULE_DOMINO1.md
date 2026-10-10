# DOMINO-1: the forward rule (paper only)

Status: **FROZEN on 2026-10-10, committed before the runner was pointed at any day after 30 Sep 2026.** A change to any number below restarts the count from zero and gets a new name (DOMINO-2).

Where it came from: tests D1 to D4 on two years of data ending 30 Sep 2026 (`RESULTS.md`, `RESULTS_D2.md`, `RESULTS_D3.md`, `RESULTS_D4.md`). In that data this set had about 98 trades a year, a median of +1.0% after 10 days and 56% winners, but it was the fourth cut of the same data. This rule exists to find out whether that was real.

## The rule

On each trading day D, using only prices, splits and SEC filings dated on or before D:

1. **Leader**: a stock in a kept industry (list in `PREREG_D3.md`) whose typical trading is **$20M a day or more** closes **up 20% or more**. "Typical trading" = median daily dollar volume over the 20 trading days ending 6 days before D.
2. **Followers**: every stock with the same 4-digit SIC code whose typical trading is **one tenth of the leader's or less**, and which was **quiet** on D: its own move below +10%, and no +100% day (or two-day move) on D or the two days before.
3. **Filters**, all required:
   - takeable: price $1 or more, typical trading $250k a day or more;
   - not headquartered in China or Hong Kong;
   - no reverse split in the last 90 days;
   - its own volume on D at least **2 times** its average of the previous 20 days;
   - scorecard 3 of 3 from filings made on or before D: annual revenue $10M or more; positive operating cash flow or 12 months of cash; share count up less than 25% in a year. An unknown answer is a fail.
4. **Entry**: the open of D+1. Paper only. One entry per stock per signal day.

## What is tracked

For every signal: the close after 1, 5 and 10 trading days, the best and worst points on the way, and the same for up to 10 size-matched quiet stocks from industries with no big mover that day (picked with a seed fixed by the date). Every stock dropped at the scorecard is logged too, with the reason.

Returns above +300% count as +300%. A stock that stops trading is marked at its last close and flagged.

## How it is judged

- No verdict before **60 signals** (roughly 7 months at the historical rate).
- **Pass**: at 60 or more signals, the average 10-day edge over controls is above zero with t above 2, **and** the median 10-day return is above zero.
- **Kill**: at 60 signals, the average 10-day return after 1% costs is zero or below. If killed, the rule is dead; it is not restarted with tweaks under the same name.
- Until one of those, it stays on paper. Passing is permission to trade it small, nothing more.

## The dry run (5 to 9 Oct 2026)

The week of 5 to 9 Oct 2026 is after the test data ended but before this rule was written. It is run once, day by day, as a check that the runner works and as a first look. Those signals are marked **dry run** and do **not** count towards the 60.

## How to run it

Say **"run domino"**. (Added 10 Oct, after the freeze: this section is the procedure, not the rule. For every signal, also pull the stock's competitors and themes from IBKR (`get_company_themes`, small limits) and add them to the link graph with IBKR named as the source.) That means: pull any missing days of all-market daily prices and recent splits with the market-data connector, convert them (`research/runners/work/ingest.py`, `splits_recent.csv`), run `python research/domino/live.py`, read the filings behind each signal (the link graph and the scorecard numbers are the starting point), and commit `live_signals.csv`.
