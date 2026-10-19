# PUT1 pre-registration: would buying puts on fading gainers have paid after the option's price?

Written 19 Oct 2026, before any option price for these events was looked at. Committed before the run.

## Why
The trader has a cash account and can't short. Our AVOID calls and the MV1 study say certain stocks fall, but a stock falling only pays a cash account through a bought put, and a put's price already includes the drop the market expects. MV1 (`research/movers/mv1/RESULTS.md`) found that takeable top-10 gainers with warning flags (fresh share-sale filings, earlier +50% spikes, or the whole share count traded in a day) fell 14.5% on average over 20 sessions, against 1.7% for clean ones. PUT1 asks whether a put bought the next day would have paid once its premium is counted. Our own AVOID list is only three weeks old, so the backdated test uses the MV1 events.

**Warning written before the run:** MV1 chose the flags on this same data, so a pass here earns a forward paper log, nothing more.

## Data
- **Events:** `research/movers/mv1/listB.csv`, the takeable top-10 gainers from 1 Oct 2024 to 30 Sep 2026 (price $1 or more, 20-day median dollar volume $250k or more).
- **Options:** Massive (Polygon) options reference data (`/v3/reference/options/contracts` with `as_of`) and daily option bars (`/v2/aggs/ticker/O:...`), which include expired contracts.
- **Stock prices at expiry:** Massive or Yahoo daily closes, unadjusted, matched to the option's own strike basis.

## The trade
- **Entry day:** the session after the mover day (t+1).
- **Contract:** a put on the standard monthly expiry that is the first at least 20 trading days after t+1, with the listed strike closest to the mover day's raw close (ties go to the higher strike).
- **Entry price:** the option's daily volume-weighted price on t+1; if it did not trade on t+1, its price on t+2; if neither, the event is a **no fill**, excluded and counted.
- **Costs:** 10% of the premium added to the entry price, for the bid/ask spread and commission on thin options. 0% and 20% are also reported.
- **Exit:** held to expiry. Payoff per share = max(strike − the stock's raw close on expiry day, 0).
- **Return:** payoff ÷ entry cost − 1 (−100% if it expires worthless).
- **Excluded and counted:** no listed put that day; no fill; a split or other adjustment to the contract before expiry; no stock close at expiry.

## Tests (one test, one comparison)
- **T1 (does the put pay on flagged fades?):** a random sample of 300 events from the rows with any MV1 flag (fresh share-sale filing in 60 days, two or more +50% days in the prior year, or turnover of 1x or more) and a market-value bucket other than "under $50M", drawn with seed 20261019. It **pays** only if the mean return after 10% costs is above zero, with a day-clustered bootstrap 95% interval above zero (2,000 draws, seed 20261014), and the mean is above zero in both halves (events before and from 1 Oct 2025).
- **T2 (comparison, description only):** 150 random events from the unflagged rows outside the under-$50M bucket, same seed and method. Reported next to T1, never tested on its own.

## Also reported
- How many sampled events had a listed put, and how many filled.
- Median return, the share of puts that paid anything, and the share that returned more than 100%.
- The stock's own 20-session return for the same events, to show how much of the fall the premium already priced in.
- The average implied cost of the put as a share of the stock price.

## What would change things
Any change to the sample, contract choice, entry, costs or pass mark after a result is seen is a new, separately named study (PUT2). A pass leads only to a forward paper log of puts on new AVOID calls, logged on the day of the call.
