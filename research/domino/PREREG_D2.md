# D2: is there money in the domino? (order proven, returns measured)

Status: **rules written and committed on 2026-10-10, before any D2 result was computed.** Exploration; no untouched data remains in this panel, so a pass here is a lead to forward-test, not proof.

D1 found that small stocks run more often after a bigger same-industry stock makes a big move, but it didn't prove the order and it didn't measure returns. D2 does both.

## Data

Same as D1: the runners panel (6,924 US common stocks, 501 trading days, split-adjusted) and `sic_map.csv` (industry code and headquarters country for 6,442 stocks).

## Definitions (fixed)

- **Size**: median daily dollar volume over the 20 trading days ending 6 days earlier (as in D1).
- **Leader day** (primary): a stock with size of at least **$20M a day** closes **up 20% or more** on day d. The $20M floor applies to the leader only: it has to be a stock the market is already watching, so its move is news and not a thin-trading accident.
- **Followers**: every stock with the same 4-digit SIC code whose size is **one tenth of the leader's or less**. There is **no minimum size for followers**: the tiniest stocks are included.
- **Quiet** (this proves the order): the follower's own close-to-close move on day d is below +10%, and it has no runner flag on d, d-1 or d-2.
- **The trade**: buy at the **open of d+1**, sell at the **close of d+5**. If the stock stops trading before d+5, the last close in that window is used. If it has no open on d+1, there is no trade. A stock that follows several leaders on the same day is one trade.
- **Dropped**: trades where the split-adjustment factor changes between entry and exit (a split inside the window). Counted and reported.
- **Takeable** (the ledger's rule): raw price of $1 or more and size of $250k a day or more on day d. **The headline number uses takeable trades only.**
- **Controls**: for each follower, up to 10 stocks picked at random (fixed seed) from the same day that are also quiet, have an industry code that had **no** $20M-plus stock moving 10% or more in either direction that day, and have a size between half and double the follower's. Same entry and exit. A follower with fewer than 3 controls is left out of the comparison (counted).

## What is measured

1. **Excess return**: each follower's return minus the average of its controls. Each day's followers form one basket (equal weight); the result is the average basket excess across days. 95% interval from a block bootstrap over days (blocks of 5 days, 2,000 draws), because the 5-day holds overlap.
2. **What you would actually have made**: the average basket return, gross, after 1% round-trip costs (ledger rule) and after 3.5% (the real cost on this account).
3. **Shape**: number of trades and days, followers per leader day, median return, share of trades positive, share at +50% or better, share at -30% or worse, and the mean with the top and bottom 1% of trades removed (so one freak print can't carry it).

## What counts as support

**Supported** only if, on the takeable set for the primary definition, the excess return is above zero with a 95% interval that excludes zero **and** the average basket return after 1% costs is above zero. The median is reported next to it: a positive mean with a negative median means lottery-ticket payoffs, and will be described that way.

## Pre-stated extra cuts (all reported, none can replace the primary)

- Leader up 10% or more; leader **down** 20% or more; leader down 10% or more.
- Excluding drug and biotech codes (2833-2836, 8731).
- **Followers headquartered in China or Hong Kong** (SEC codes F4, K3), any size.
- All followers (not just takeable).

No other variants.
