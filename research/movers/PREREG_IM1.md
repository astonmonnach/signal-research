# IM1 pre-registration: buy the pump when it crosses +20%, sell two hours later

Written 29 Oct 2026. Committed before any intraday price for any event was looked at.

## Why
The trader doesn't want to hold for days: "get the pump and leave ... hold it for like 2 hours". MV1, FP1 and PUT1
all held overnight or longer, so none of them answers this. The question: if you buy a takeable stock the moment
it first trades 20% above yesterday's close and sell two hours later, does that pay after costs?

**The trap this design avoids:** the day's top-10 gainers list is chosen at the close, so it only contains stocks
that kept going. IM1 starts from every takeable stock whose high reached +20% at any point in the day, including
the ones that spiked and collapsed.

**Seen before writing this:** the size of the event pool (17,759 takeable stock-days with a high of +20% or more,
2 Oct 2024 to 30 Sep 2026, from the cached daily bars), and that the market-data plan serves minute bars only from
about 4 Nov 2024. No intraday price for any event was looked at.

## Data
- **Events:** the split-adjusted daily panel `research/runners/work/panel.npz` (Massive grouped daily bars, common
  stocks, 1 Oct 2024 to 30 Sep 2026).
- **Minute bars:** Massive `/v2/aggs/ticker/{T}/range/1/minute/{day}/{day}`, unadjusted. The connector stores each
  response server-side, so the minute bars are reduced to one row per event with the SQL in `im1/extract.sql`, run
  through the connector. That row (trigger time, entry, exits) is saved in `im1/events.csv`.
- **Time:** regular session only, 09:30 to 16:00 New York time (daylight saving handled per date).

## The event pool
A stock-day is in the pool if all of these hold:
- the day's high is 20% or more above the previous close (split-adjusted);
- the previous close (actual, unadjusted) is $1 or more;
- the median dollar volume (raw close times raw volume) over the 20 sessions before is $150k or more (at least 15
  sessions with data);
- no split executes within two sessions either side (the panel's split list);
- the day is from 4 Nov 2024 to 30 Sep 2026.

## Sample
200 events drawn at random from the pool, seed 20261029, by `im1/sample.py`. Every event drawn is kept and
counted, whatever happens to it.

## The trade
- **Trigger level:** P = 1.20 x the previous close (unadjusted).
- **Trigger bar:** the first regular-session minute bar whose high is P or more.
- **Entry:** P, or the trigger bar's open if it opened above P (a buy-stop fills at its level or worse; a stock
  that opens the day above P is bought at the 09:30 open).
- **Exit:** the open of the first minute bar at or after entry time + 120 minutes. If no bar comes before the
  close (including a halt into the close), the close of the last regular-session bar.
- **Costs:** 2% round trip (the tested case), for the spread, slippage past P and commission. 1% and 4% are also
  reported.
- **Return:** exit / entry - 1 - costs, capped at +300% before costs.

## The test
- **Tested set:** sampled events with a trigger bar from 09:30 to 13:59 (so the two-hour hold fits the session).
- **Pays only if all three hold:**
  1. the mean return after 2% costs is above zero;
  2. the 95% interval of the mean is above zero (bootstrap over whole event days: 2,000 draws, seed 20261029,
     percentile interval);
  3. the mean after 2% costs is above zero in both halves (events before 1 Oct 2025, and from 1 Oct 2025).

## Excluded and counted (never silently dropped)
- No minute bars returned for the day.
- No regular-session bar reached P (the +20% came before 09:30 or after 16:00 only).
- Trigger at 14:00 or later (reported separately, not tested).

## Also reported (description only, never a pass)
- Median, share of winners, share up 10% or more and down 10% or more.
- Exits after 30 and 60 minutes and at the close, from the same entry.
- Gap-ups (opened at P or above) against stocks that crossed P during the session.
- Previous close $1 to $3 against $3 and up.
- The lowest low and highest high between entry and exit, as a share of entry.

## What would change things
Any change to the trigger, entry, exit, costs, sample or pass marks after a result is seen is a new, separately
named study (IM2). A pass leads only to a forward paper log of live signals, logged in real time, before any money.
A fail means this version of "buy the pump" is dropped.
