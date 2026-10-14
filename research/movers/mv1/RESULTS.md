# MV1 results: the ten biggest daily gainers, and what came next

Pre-registration: `research/movers/PREREG_MV1.md` (git cab1406). Run on 2026-10-14 with `python run.py`. Every number in this file is written by `run.py` from the runners panel and caches. The run follows the pre-registration except where listed under Deviations.

- List A: the ten biggest daily gains among all common stocks. 5,000 movers on 500 days, 2024-10-02 to 2026-09-30.
- List B (the tested list): the ten biggest gains among takeable stocks (prior close $1 or more, median dollar volume $250k or more over the 20 sessions before). 4,810 movers on 481 days, 2024-10-29 to 2026-09-30.
- 1,823 movers are on both lists.
- Returns are after 1% round-trip costs. A gain above +300% counts as +300%. "20 sessions" means from the mover day's close to the close 20 sessions later.
- The 95% interval resamples whole mover days: 2,000 draws, seed 20261014, percentile interval.

## Verdicts

| Test | Pass mark | Result |
| --- | --- | --- |
| T1: does buying list B at the close pay? | mean above 0, interval above 0, median above 0 | **Does not pay** |
| T2: do event movers hold up better? | interval of the difference above 0, same sign in both halves | **Separates** |
| T3: do the mechanics mark the fade? | interval of the difference below 0, same sign in both halves | **Separates** |

### T1: buying list B at the close does not pay

| List B, 20 sessions | n | mean | median | % positive | 95% interval of the mean |
| --- | --- | --- | --- | --- | --- |
| Bought at the close | 4,609 | -7.0% | -10.8% | 33.4% | -8.6% to -5.3% |
| Mover minus IWM, same days | 4,609 | -8.0% | -11.5% | 32.4% | -9.6% to -6.5% |

- Mean above zero: no. Interval above zero: no. Median above zero: no.
- IWM over the same entry and exit days averaged +1.1% (median +1.8%).
- By half (not part of the pass mark): sessions 1-250 mean -4.2% (n 2,299), sessions 251-501 mean -9.7% (n 2,310).
- 461 mover days had a 20-session outcome.

### T2: event movers held up better

An event is an 8-K or 6-K accepted after 16:00 New York time the session before and before 16:00 on the mover day.

| List B, 20 sessions | n | mean | median | % positive |
| --- | --- | --- | --- | --- |
| With an event | 1,495 | -2.8% | -3.8% | 37.7% |
| No event | 3,114 | -8.9% | -15.8% | 31.4% |

- Difference in means (event minus no event): +6.1 points. 95% interval: +3.5 points to +8.7 points.
- First half: +2.1 points (event -2.7%, n 731; no event -4.9%, n 1,568).
- Second half: +10.2 points (event -2.9%, n 764; no event -13.1%, n 1,546).
- Interval above zero: yes. Same sign in both halves: yes.
- Difference in medians (not part of the pass mark): +12.0 points.
- "Better" is relative. Event movers still averaged -2.8% after 20 sessions, and 37.7% were higher.
- Movers left out for lack of SEC data: 0.

### T3: among no-event movers, the mechanics marked the fade

A mover is flagged if it had any of: fresh supply (S-1, F-1, S-3, F-3, any 424B or EFFECT in the 60 days before), repeat spiker (two or more +50% days in the 250 sessions before), or whole count traded (turnover 1.0 or more).

| List B, no event, 20 sessions | n | mean | median | % positive |
| --- | --- | --- | --- | --- |
| Any flag | 1,669 | -14.5% | -23.5% | 25.4% |
| No flag | 1,081 | -1.7% | -6.8% | 40.2% |

- Difference in means (any minus none): -12.8 points. 95% interval: -16.3 points to -9.1 points.
- First half: -6.7 points (any -7.4%, n 847; none -0.7%, n 537).
- Second half: -19.1 points (any -21.8%, n 822; none -2.7%, n 544).
- Interval below zero: yes. Same sign in both halves: yes.
- Difference in medians (not part of the pass mark): -16.7 points.
- 364 no-event movers were left out. Their share count was unknown and the other two flags were off, so "no flag" could not be confirmed.
- The flags mark the fade. They do not make a long trade: the no-flag group still averaged -1.7% (median -6.8%).

## Description only (not tested, never a result)

### What stands out

1. **Size separated outcomes more than anything else described.** List B movers under $50M averaged -17.9% after 20 sessions (median -25.9%, 21.6% higher, n 1,029). Movers of $300M or more averaged +0.8% (median -3.4%, 40.9% higher, n 1,336). Not tested.
2. **Most movers had no filing, and some filed new share supply soon after.** On a typical day 7 of the ten list B movers had no event (mean 6.80). 14.6% of list B movers filed an S-1, F-1, S-3, F-3, 424B or EFFECT within 10 days after the mover day (15.9% for list A).
3. **Waiting for the next open did not help, and the close location mattered little in list B.** Bought at the next open, list B averaged -7.2% after 20 sessions (median -11.0%), against -7.0% from the close. List B movers that closed strong averaged -5.0%; those that faded into the close averaged -8.3%. In list A the gap was wider: -7.2% against -18.1%.

### What came next, both lists

| List | Entry | Sessions | n | mean | median | % positive | IWM mean | mover minus IWM |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B | close | 1 | 4,798 | -1.4% | -2.6% | 36.6% | +0.1% | -1.5% |
| B | close | 5 | 4,758 | -2.6% | -4.7% | 37.7% | +0.3% | -2.9% |
| B | close | 20 | 4,609 | -7.0% | -10.8% | 33.4% | +1.1% | -8.0% |
| B | next open | 1 | 4,784 | -1.9% | -2.1% | 37.1% | +0.0% | -1.9% |
| B | next open | 5 | 4,744 | -2.9% | -4.7% | 36.8% | +0.2% | -3.1% |
| B | next open | 20 | 4,594 | -7.2% | -11.0% | 33.2% | +1.0% | -8.2% |
| A | close | 1 | 4,972 | -3.9% | -6.2% | 31.6% | +0.1% | -4.0% |
| A | close | 5 | 4,932 | -6.1% | -12.0% | 29.7% | +0.3% | -6.3% |
| A | close | 20 | 4,798 | -13.8% | -23.3% | 25.6% | +1.2% | -15.1% |
| A | next open | 1 | 4,948 | -1.8% | -2.9% | 38.7% | +0.0% | -1.8% |
| A | next open | 5 | 4,908 | -3.8% | -9.3% | 32.8% | +0.2% | -4.0% |
| A | next open | 20 | 4,758 | -11.4% | -20.3% | 27.1% | +1.2% | -12.6% |

### By market value (shares outstanding times prior close), 20 sessions from the close

| List | Market value | movers | n with outcome | mean | median | % positive |
| --- | --- | --- | --- | --- | --- | --- |
| B | <$50M | 1,084 | 1,029 | -17.9% | -25.9% | 21.6% |
| B | $50M-$300M | 1,327 | 1,271 | -3.6% | -7.8% | 37.5% |
| B | >=$300M | 1,384 | 1,336 | +0.8% | -3.4% | 40.9% |
| B | unknown | 1,015 | 973 | -10.4% | -13.9% | 30.4% |
| A | <$50M | 2,642 | 2,528 | -19.5% | -30.5% | 20.0% |
| A | $50M-$300M | 767 | 738 | -4.9% | -13.3% | 34.8% |
| A | >=$300M | 520 | 506 | +1.5% | -1.6% | 41.5% |
| A | unknown | 1,071 | 1,026 | -14.1% | -24.5% | 24.9% |

### By close location (where the close sat between the day's low and high), 20 sessions from the close

| List | Close location | movers | n with outcome | mean | median | % positive |
| --- | --- | --- | --- | --- | --- | --- |
| B | closed strong (>=0.9) | 1,421 | 1,348 | -5.0% | -8.7% | 34.9% |
| B | middle (0.7-0.9) | 1,728 | 1,660 | -7.3% | -11.2% | 34.0% |
| B | faded (<=0.7) | 1,661 | 1,601 | -8.3% | -12.1% | 31.5% |
| B | unknown | 0 | 0 | n/a | n/a | n/a |
| A | closed strong (>=0.9) | 889 | 857 | -7.2% | -13.5% | 32.1% |
| A | middle (0.7-0.9) | 1,420 | 1,366 | -10.1% | -19.4% | 29.4% |
| A | faded (<=0.7) | 2,690 | 2,574 | -18.1% | -28.1% | 21.4% |
| A | unknown | 1 | 1 | -26.0% | -26.0% | 0.0% |

### New share supply within 10 days after the mover day

| List | movers with SEC data | filed S-1/F-1/S-3/F-3/424B/EFFECT | share |
| --- | --- | --- | --- |
| B | 4,810 | 704 | 14.6% |
| A | 4,999 | 794 | 15.9% |

### Movers per day with no event

- List B: 481 days. Movers with no event per day: mean 6.80, median 7. Movers with an event per day: mean 3.20. No SEC data: mean 0.000 per day. Days on which all ten had no event: 37.
- List A: 500 days. Movers with no event per day: mean 7.24, median 7. Movers with an event per day: mean 2.76. No SEC data: mean 0.002 per day. Days on which all ten had no event: 31.

| No-event movers that day | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| List B: days | 6 | 7 | 7 | 17 | 29 | 53 | 71 | 89 | 88 | 77 | 37 |
| List A: days | 0 | 0 | 1 | 5 | 16 | 54 | 85 | 101 | 120 | 87 | 31 |

### Who was on the lists

| Count | List B | List A |
| --- | --- | --- |
| movers | 4,810 | 5,000 |
| median day gain | +28.6% | +47.3% |
| smallest day gain on the list | +7.7% | +17.7% |
| median prior close (actual price) | $5.01 | $1.87 |
| with SEC data | 4,810 | 4,999 |
| event (8-K or 6-K in the window) | 1,541 | 1,378 |
| fresh supply in the 60 days before | 1,480 | 1,639 |
| repeat spiker | 834 | 1,010 |
| share count known | 3,795 | 3,929 |
| whole count traded (turnover 1.0 or more) | 810 | 2,239 |
| median turnover (where known) | 0.16 | 2.02 |
| market value <$50M | 1,084 | 2,642 |
| market value $50M-$300M | 1,327 | 767 |
| market value >=$300M | 1,384 | 520 |
| market value unknown | 1,015 | 1,071 |
| close location closed strong (>=0.9) | 1,421 | 889 |
| close location middle (0.7-0.9) | 1,728 | 1,420 |
| close location faded (<=0.7) | 1,661 | 2,690 |
| close location unknown | 0 | 1 |

## Self-consistency check

For every set of returns: share of wins times average win, minus share of losses times average loss, must equal the mean. Zero returns count as neither. 16 sets were checked. **All passed** (largest gap below 1e-12).

| Set | n | wins | average win | losses | average loss (size) | (wins x average win - losses x average loss) / n | mean | passed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T1: list B, 20 sessions, after costs | 4,609 | 1,541 | 35.2% | 3,068 | 28.1% | -6.9556% | -6.9556% | yes |
| T2: event | 1,495 | 563 | 24.6% | 932 | 19.4% | -2.8056% | -2.8056% | yes |
| T2: no event | 3,114 | 978 | 41.3% | 2,136 | 32.0% | -8.9480% | -8.9480% | yes |
| T3: any flag | 1,669 | 424 | 49.9% | 1,245 | 36.4% | -14.4954% | -14.4954% | yes |
| T3: no flag | 1,081 | 435 | 31.8% | 646 | 24.3% | -1.6951% | -1.6951% | yes |
| T1 (full panel): list B, 20 sessions, after costs | 4,609 | 1,514 | 38.3% | 3,095 | 30.8% | -8.1142% | -8.1142% | yes |
| T2 (full panel): event | 1,307 | 494 | 26.3% | 813 | 20.8% | -3.0318% | -3.0318% | yes |
| T2 (full panel): no event | 2,732 | 828 | 44.2% | 1,904 | 34.1% | -10.3632% | -10.3632% | yes |
| T3 (full panel): any flag | 1,574 | 380 | 51.6% | 1,194 | 38.2% | -16.5507% | -16.5507% | yes |
| T3 (full panel): no flag | 840 | 346 | 34.7% | 494 | 24.8% | -0.3313% | -0.3313% | yes |
| list A 1-session net, close entry | 4,972 | 1,570 | 21.5% | 3,402 | 15.6% | -3.9041% | -3.9041% | yes |
| list A 5-session net, close entry | 4,932 | 1,464 | 36.5% | 3,468 | 24.0% | -6.0588% | -6.0588% | yes |
| list A 20-session net, close entry | 4,798 | 1,228 | 50.3% | 3,570 | 35.9% | -13.8493% | -13.8493% | yes |
| list B 1-session net, close entry | 4,798 | 1,756 | 12.7% | 3,042 | 9.6% | -1.4412% | -1.4412% | yes |
| list B 5-session net, close entry | 4,758 | 1,796 | 21.5% | 2,962 | 17.2% | -2.5756% | -2.5756% | yes |
| list B 20-session net, close entry | 4,609 | 1,541 | 35.2% | 3,068 | 28.1% | -6.9556% | -6.9556% | yes |

## Caveats

- **This is not a long trade.** List B lost money on average at every horizon from both entries. The tests describe which movers fade. A cash account cannot short, and borrow on small movers is often unavailable or costly. Costs of 1% may be too low for the smallest names.
- **Size may confound T2 and T3.** In the T3 sample, 42.1% of flagged movers were under $50M, against 14.2% of unflagged movers. In the T2 sample, 11.6% of event movers were under $50M, against 27.5% of no-event movers. Small movers faded more (see the market value table). Neither test was built to separate its feature from size, and nothing here tests that.
- **"No event" means no SEC 8-K or 6-K in the window.** No newswire or social media was checked. A mover with no filing may still have had news.
- **Share counts can be stale.** They are the latest dei cover-page count filed before the day, up to 15 months old, adjusted for recorded splits since. In list B the median count was 64 days old at the mover day, and 140 were more than a year old. A stale count in a fast-diluting company understates shares, which overstates turnover and understates market value. 350 list B movers showed turnover above 10. Split records start on 2024-06-03, so an older split between the count date and the mover day is not adjusted.
- **Stocks that stopped trading.** At 20 sessions in list B: 80 stopped trading and were marked at their last close; 3 had no trade on the exit day and were marked at the last close before it; 8 had an exit bar inside a split window and used the last close before the window; 1 had no usable close and has no outcome. Marking a delisted stock at its last close probably understates its loss. A ticker change also looks like a stop in this panel.
- **The panel ends on 2026-09-30.** The 200 list B movers from the last 20 sessions have no 20-session outcome. Raw bars to 2026-10-09 exist on disk but are outside the pre-registered data and were not used.
- **Possible unrecorded splits.** 14 list B movers (55 in list A) match the runners study's flag for an unrecorded reverse split. They were kept. Without them, T1 is mean -6.9%, median -10.8% (n 4,595).
- **Cap.** 27 list B 20-session returns were above +300% and were capped.
- **Ticker to CIK** uses `research/domino/sic_map.csv`, then SEC company_tickers.json downloaded on this run. Both are current lists, so a recycled ticker could map to the wrong company [UNVERIFIED]. Where the Massive ticker file also had a CIK, none disagreed (list B: 0, list A: 0).
- **SEC acceptance times** in the submissions files are true UTC. This was checked: converted to New York time, filings accepted after 17:30 carry the next day's filing date, as EDGAR rules say. The event window uses exact times: after 16:00:00 the session before, before 16:00:00 on the mover day.
- **Amendments are not counted** because the pre-registration names the base forms. Counting 8-K/A and 6-K/A would add 2 list B events. Counting S-1/A, F-1/A, S-3/A, F-3/A, MEF and ASR forms would add 59 fresh-supply flags. Neither was tested.
- **SEC cache dates.** The runners SEC cache is complete through 2026-09-30. Movers whose 10-day after-window ends later (80 in list B) used submissions fetched on 2026-10-14.
- **IWM** is Yahoo daily closes (price only, no dividends). They match the IWM bars in the raw files on all 501 sessions; the largest relative gap was 5.5e-08. IWM returns run from the mover day's close to the scheduled exit day and carry no costs.
- **No significance claim beyond the three tests.** The description tables are many cuts of one sample. Read them as description.

## Deviations

1. **Universe: common stocks only, by label.** The pre-registration calls the panel "6,924 US common stocks". 574 of those tickers have no common-stock (CS) label in the runners ticker file. They came in from an untyped ticker source. 264 are on the SEC fund and ETF ticker list. 233 map to an SEC company; a manual look at their names found ETNs, closed-end funds, ADRs, warrants and some genuine common stocks [UNVERIFIED: not counted by type]. 77 are on neither list. The definitions say "common stocks", so the primary run keeps the 6,350 tickers Massive labelled CS. Exact security types could not be fetched: the Massive reference endpoint is not reachable through the connector. Some genuine common stocks, such as recent listings, are therefore left out.
   - Impact check, the panel as-is: list B then has 927 of 4,810 rows from unlabelled tickers (557 of them on the SEC fund list). The most frequent were RGTX (16), AXTU (15), SKYQ (14), SMCX (13), SMCL (13), AXTX (13), UVIX (12), RGTU (12), MSTU (11), SMST (11), MSOX (10), QBTX (10), mostly leveraged single-stock ETFs by name [UNVERIFIED for the rest]. Results: T1 mean -8.1%, median -13.0%, interval -9.9% to -6.2%, does not pay. T2 difference +7.3 points, interval +4.4 points to +10.3 points, halves +3.9 points and +11.3 points, separates. T3 difference -16.2 points, interval -20.2 points to -12.0 points, halves -8.9 points and -24.4 points, separates. The verdicts are the same. That table is `listB_fullpanel.csv`.
2. **List B starts on session 21 (2024-10-29).** The 20-session liquidity window needs data before 2024-10-01, which the panel does not have. So list B has no movers on the first 19 mover days. List A starts on session 2.
3. **Repeat-spiker lookback is shorter in the first half.** The 250 sessions before the mover day are only fully inside the panel from session 252 on. Earlier movers use every session available. This undercounts repeat spikers in the first half, which matters for the T3 halves check.
4. **Exits inside a split window.** The pre-registration says bars inside a split window are not used. An exit that falls in one uses the last usable close before it and is flagged. The next-day open is not used if that day is in a split window. Counts are under Caveats.
5. **The last session.** The panel's stored `valid` array ends on 2026-09-29 for a reason unrelated to splits (the runners study needed a next day). It was rebuilt from the same split records so that 2026-09-30 counts as a mover day. On every other session the rebuilt array matches the stored one (0 differences).
6. **Choices the pre-registration left open.** A session with no trade counts as $0 dollar volume. A stock with no trade between entry and exit is marked at its last close (the entry close) and flagged. The +300% cap is applied before costs. In T2 and T3, movers that cannot be classed (no SEC data, or unknown flags) are left out. "Same sign in both halves" is checked on the difference in means. Ties in daily return are broken by ticker. IWM is from Yahoo, as the brief said, and was cross-checked against the panel's own source.

## Files

- `run.py`: rebuilds everything here with one command. It reads the runners panel and caches and writes only inside this folder.
- `listA.csv`, `listB.csv`: one row per mover with every feature and outcome. `listB_fullpanel.csv`: the impact check for Deviation 1.
- `cache/`: SEC and Yahoo downloads, and `numbers.json` with every number above.
