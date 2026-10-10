# D1: the reverse domino (does a bigger linked stock move first, before a small stock runs?)

Status: **rules written and committed on 2026-10-10, before any result was computed.** This is exploration (the period ends 30 Nov 2026). There is no untouched data left in this dataset, so a positive result is only a lead: it must then be forward-tested in the ledger.

## The idea

Small stocks that double in a day (or do +300% in a week) might be the small dominoes at the end of a chain: a bigger company in the same line of business moves first, and the small ones follow days later.

## Data

- The runners study panel: 6,924 US common stocks, 501 trading days (1 Oct 2024 to 30 Sep 2026), split-adjusted (`research/runners/work/panel.npz`).
- The 1,136 runner days and their 11,360 matched controls (`research/runners/events.csv`, `controls.csv`): 10 controls per event, same date, similar dollar volume.
- Industry codes (SIC) from SEC submissions for 6,442 of the 6,924 stocks (`sic_map.csv`). Stocks without a code are left out and counted.

## Definitions (fixed)

- **Linked** (primary): same 4-digit SIC code. Variants: same 3-digit, same 2-digit.
- **Size**: a stock's median daily dollar volume (raw close x raw volume) over the 20 trading days ending 6 days before the date. It is a liquidity measure, used because share counts aren't available for every stock.
- **Bigger linked stock ("leader")** for small stock X on day t: a linked stock whose size is at least **10x** X's size and at least **$20M a day**.
- **"Fell first"** (primary): at least one leader closed **up 10% or more** on any of the 5 trading days before t (t-5 to t-1). Day t itself never counts. Variants: +5%, +20%, and the down versions (-5%, -10%, -20%).

## The two looks

1. **Backward (same method as the runners lift table):** the share of runner days with a leader move in the 5 days before, against the share of their matched controls (each control uses its own industry and its own leaders). Lift = runner share / control share. 95% interval from a bootstrap that resamples whole events with their controls (2,000 draws).
2. **Forward (the tradeable question):** take every (small stock, day) where the stock has at least one leader. Base rate = how often that stock has a runner day in the next 5 trading days. Conditional rate = the same, but only on days when one of its leaders closed up 10% or more **that day**. Lift = conditional / base. 95% interval from a bootstrap over days (2,000 draws).

Also reported: the same forward look for **+300% in 5 trading days** (adjusted and raw close both at least 4x the close 5 days earlier; first day of each episode per stock, episodes at least 10 days apart). If there are fewer than 50 such episodes with a leader, it is reported as too few to judge.

## What counts as support

The idea is **supported** only if the primary cell (4-digit SIC, +10%, up) shows a lift of **1.5 or more with a 95% interval that excludes 1.0, in both looks**. Anything else is "not supported".

All 18 cells (3 link levels x 3 thresholds x 2 directions) are reported for both looks, plus one robustness run that drops drug and biotech codes (2833-2836, 8731), because those stocks run on their own trial news. No other variants.

## Known limits

- SIC codes are crude: two companies with the same code can be unrelated, and real links (supplier, customer, shared holder, same theme) often cross codes. A null result here would not kill the link-graph idea; it would say industry codes alone aren't the link.
- Dollar volume is a stand-in for company size.
- Controls were matched on dollar volume, not on industry.
