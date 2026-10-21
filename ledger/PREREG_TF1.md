# TF1 pre-registration: does a strength-and-price filter pick the found stocks that beat IWM?

Written 21 Oct 2026, before any of the test's items exist. Committed before the first test item is found.

## Why

The trader wants a rule for turning a WATCH into a TRADE.

On 21 Oct, an exploratory look at the ledger compared the items that did well with those that did not. It used 348 items found from 28 Sep to 20 Oct and held 5 or more trading days; the median hold was only 6 days. Results are excess return against IWM (`ret_pct - iwm_pct`):

- **Distance from the 52-week high:** within 10% beat IWM 73% of the time; 60% or more below beat it 17%.
- **Trend:** above the 50-day average, 52%; below it, 29%.
- **Price:** $5 or more, 61%; under $5, 22%.
- **Buy-side events only** (no supply or reverse-split events):

  | Group | n | beat IWM | median vs IWM |
  |---|---|---|---|
  | $5+ and within 30% of the high | 89 | 70% | +1.6% |
  | Under $5 and 30%+ below the high | 44 | 25% | -13.4% |

- **Without deal-pinned stocks:** 61% against 29%.
- **Down 10% or more in the 5 days before being found:** 15%.

**Those items formed the idea, so they cannot test it.** The test is forward only.

## The filter (fixed now)

A found item **passes** when all four hold, using the ledger's state columns, which are recorded at the found day's close:

1. The entry price (the next session's open, `entry_open`) is **$5.00 or more**.
2. `from_52w_high_pct` is **above -30**.
3. `above_50d` is **true**.
4. `pre_move_5d` is **above -10**.

Any other item fails, unless a column is missing. Items missing any of the four columns are excluded and counted.

For a TRADE plan there is also a reading check: the event has a hard number (a deal or tender price, a funded order, or cash or NAV against the price). This check is recorded in the triage and is **not** part of the statistical test.

## Sample

- **Included:** every `ledger/ledger.csv` item **found from 2026-10-22 onward** with direction +1 or 0.
- **Excluded categories:** the supply and avoid ones, which are 8k_reverse_split, registration_effective, share_registration, any setup_supply_*, delisting, 8k_lock_up and shelf_registration.
- **Primary test:** also leaves out the deal-pinned categories, which mostly track a fixed price. These are 8k_merger_agreement, merger_vote, 8k_tender_offer, tender_issuer_buyback, issuer_tender_intent, merger_hostile, tender_third_party, merger_arb and idea_merger.
- **Secondary, description only:** the same comparison with the deal-pinned categories put back.
- **How items are judged:** at **20 trading days** from the entry open. Excess is against IWM over the same window, with **1% taken off for costs** (the ledger convention).
- **Stop:** when both the pass and fail groups have **40 judged items each**, or on **31 Mar 2027**, whichever comes first. The analysis runs once.

## The test

TF1 **passes** only if all three hold:

1. The mean excess of the pass group minus the mean excess of the fail group is above zero.
2. A bootstrap 95% interval on that difference is above zero. Resample whole found days; 2,000 draws, seed 20261021.
3. The difference is above zero in both halves, split at the median found date.

**Also required before any real money:** the pass group's own median excess after costs is above zero. Beating the fail group is not enough if both lose.

- **On a pass:** the filter becomes the dated rule for turning a WATCH into a TRADE (paper first, as the design says).
- **On a fail:** it is dropped. Any change to the filter is a new study, TF2.

## Until the result

- **Before the result:** the filter is a label on WATCHes and paper TRADE plans only. No real money depends on it.
- **The 28 Sep to 20 Oct items:** their 20-day results will be reported as **in-sample**, labelled as such, and never as the test.

## Also reported

- How many items were excluded for missing columns.
- The takeable subset: long, $1 or more, liquid under the dated rule.
- Each filter condition on its own.
- Medians, hit rates, and the mean without the best two.

## Warnings written now

- The four conditions overlap: cheap, beaten-down and volatile are often the same stocks.
- Momentum in small stocks is a known effect. So a pass would show the pattern holds in our own pipeline. It would not be a new edge.
- With 3.5% round-trip costs on £40 to £50 positions, a 1-2% median edge would not pay at that size. The cost section of any TRADE plan has to say so.
