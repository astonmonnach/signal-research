# PUT1 results: buying puts on fading gainers did not pay

Pre-registration: `research/movers/PREREG_PUT1.md` (git 60e910c). The run started on 19 Oct 2026 and finished on 20 Oct 2026 with `python run.py`. The headline numbers come from `results.json`, which `run.py` writes from the cached Massive responses. A few extra description numbers come from `trades_T1.csv` and `trades_T2.csv`, and are marked. The run follows the pre-registration except where listed under Deviations.

- The trade: buy the put the session after a top-10 gainer (t+1). It is on the first standard monthly expiry at least 20 trading days after t+1, at the strike closest to the gain-day close. Pay that day's volume-weighted price (or t+2's if t+1 had no trade), plus costs. Hold to expiry.
- Return = payoff at expiry / entry cost - 1. A put that expires worthless is -100%.
- Costs: 10% of the premium is the tested case. 0% and 20% are shown too.
- The 95% interval resamples whole mover days: 2,000 draws, seed 20261014, percentile interval.
- Halves: mover days before 1 Oct 2025, and from 1 Oct 2025.

## Verdict

**T1 does not pay. It fails all three pass marks.** On flagged fading gainers, a put bought the next day lost 31.2% on average after 10% costs. The interval is well below zero, and both halves lost.

| T1 pass mark | Result | Passed? |
| --- | --- | --- |
| Mean after 10% costs above zero | -31.2% | No |
| 95% interval above zero | -47.0% to -14.6% | No |
| Mean above zero in both halves | -33.7% (n 55) and -28.3% (n 48) | No |

Under the pre-registration, only a pass would lead to a forward paper log. This fails, so there is no paper log of puts on AVOID calls.

## T1: flagged gainers (the test)

T1 is 300 random events (seed 20261019) from list B rows with any MV1 flag, outside the under-$50M bucket. The flags are a fresh share-sale filing in the 60 days before, two or more +50% days in the year before, or turnover of 1x or more. The pool had 1,255 rows.

| T1 puts, n 103, 94 mover days | 0% costs | 10% costs (tested) | 20% costs |
| --- | --- | --- | --- |
| Mean return | -24.3% | -31.2% | -36.9% |
| 95% interval of the mean | -41.7% to -6.1% | -47.0% to -14.6% | -51.4% to -21.7% |
| Median return | -63.1% | -66.5% | -69.3% |
| Return above zero | 35.0% | 30.1% | 30.1% |
| Returned more than +100% | 9.7% | 8.7% | 7.8% |
| First half mean (n 55) | -27.1% | -33.7% | -39.2% |
| Second half mean (n 48) | -21.2% | -28.3% | -34.3% |

- It fails even with no costs at all: -24.3%, interval -41.7% to -6.1%.
- 57.3% of the puts paid something at expiry (59 of 103). 42.7% expired worthless (44).
- Average premium paid, as a share of the gain-day close: mean 19.8%, median 18.2%. That is the entry price before costs.
- The strike sat close to the price: median 1.0% below the gain-day close.
- The stocks' own 20-session return (MV1's `ret20_net`, gain-day close to 20 sessions later, after 1% costs), for 100 of the 103 events: mean +5.2%, median -1.3%, 48.0% higher. Before costs: mean +6.2%, median -0.3%. Three events (CHPT, TYRA, BNC) have no MV1 value because their 20 sessions end after MV1's data.
- The stocks from the gain-day close to the expiry close: mean -0.5%, median -5.4%. 42.7% were higher.
- Break-even at 10% costs (computed from `trades_T1.csv`): the stock had to close a median 22.3% below the gain-day close at expiry (mean 23.3%).
- The loss does not depend on a few trades. Without the best trade, the 10% mean is -33.8%. Without the best three, it is -38.4% (from `trades_T1.csv`).
- Self-check: the share of winners times the average win, minus the share of losers times the average loss, equals the mean at every cost level.

## T2: unflagged gainers (comparison, not tested)

T2 is 150 random events from list B rows with no MV1 flag, outside the under-$50M bucket, drawn the same way. The pool had 1,876 rows.

| T2 puts, n 95, 84 mover days | 0% costs | 10% costs | 20% costs |
| --- | --- | --- | --- |
| Mean return | -14.9% | -22.6% | -29.1% |
| 95% interval of the mean | -37.4% to +10.5% | -43.1% to +0.5% | -47.8% to -7.9% |
| Median return | -100.0% | -100.0% | -100.0% |
| Return above zero | 33.7% | 33.7% | 31.6% |
| Returned more than +100% | 14.7% | 14.7% | 12.6% |
| First half mean (n 53) | +3.1% | -6.3% | -14.1% |
| Second half mean (n 42) | -37.6% | -43.3% | -48.0% |

- 48.4% paid something at expiry (46 of 95). 51.6% expired worthless (49), so the median is -100%.
- Average premium as a share of the gain-day close: mean 12.7%, median 10.4%.
- The stocks' own 20-session return (`ret20_net`, 92 of 95 events): mean -1.5%, median -3.2%, 38.0% higher. Before costs: mean -0.5%, median -2.2%.
- The stocks from the gain-day close to the expiry close: mean +2.5%, median +0.7%.
- Break-even at 10% costs (from `trades_T2.csv`): a median 10.8% fall by expiry (mean 12.5%).

### T1 against T2 (description only)

| After 10% costs | T1 flagged | T2 unflagged |
| --- | --- | --- |
| Puts used | 103 | 95 |
| Mean return | -31.2% | -22.6% |
| Median return | -66.5% | -100.0% |
| Paid anything at expiry | 57.3% | 48.4% |
| Over +100% | 8.7% | 14.7% |
| Premium, share of price (mean) | 19.8% | 12.7% |
| Fall needed to break even (median) | 22.3% | 10.8% |
| Stock, gain-day close to expiry (median) | -5.4% | +0.7% |

- Flagged puts lost 8.6 points more on average. The flagged stocks did fall more often, which is why more of their puts paid something. But their puts cost about one and a half times as much (19.8% of the price against 12.7%), and that ate the difference and more.
- Neither group's puts made money on average.

## Counts at each stage

| Stage | T1 | T2 |
| --- | --- | --- |
| Sampled | 300 | 150 |
| Never looked up: no stock bar under that ticker after the gain day | 2 (SRM, BSGM) | 0 |
| No standard put listed on that expiry | 166 | 22 |
| of which only adjusted, non-standard puts were listed | 5 (QMCO, SST, SCLX, WOLF, BTM) | 1 (ARQQ) |
| Put listed, contract chosen | 132 | 128 |
| No fill on t+1 or t+2 | 22 | 32 |
| Filled (had an entry price) | 110 | 96 |
| of which entered on t+2 | 8 | 10 |
| Adjusted before expiry | 3 (MLGO split; WOLF and MFH contracts not found at expiry) | 0 |
| Expiry 20 Nov 2026, after the run date | 4 (SECZ, GLND twice, BFLY) | 1 (VKTX) |
| **Used** | **103** | **95** |

- In T1, 166 of 300 flagged gainers (55%) had no standard put to buy. In T2 it was 22 of 150 (15%).
- `results.json` says T1 `put_listed` 134. That figure counts the 2 events that were never looked up. The true count with a listed put is 132.
- The fills were thin. T1's median entry-day volume was 42 contracts. 12 of the 103 T1 entries traded 5 contracts or fewer that day, and 5 traded one. In T2 the median was 27, with 25 of 95 at 5 or fewer and 14 at one (from the trades files). A daily VWAP on one contract is not a price you could count on getting.

## Description: where the fade was (not a test)

The flagged stocks with no put to buy fell the most. The ones with puts fell the least. MV1 `ret20_net`, all sampled events with a value (from the trades files):

| 20-session stock return | T1 n | T1 mean | T1 median | T2 n | T2 mean | T2 median |
| --- | --- | --- | --- | --- | --- | --- |
| No standard put listed | 159 | -8.8% | -14.9% | 17 | -4.0% | -11.1% |
| Put listed | 125 | +3.2% | -5.3% | 123 | -0.7% | -2.6% |

By market-value bucket, T1 at 10% costs (from `results.json`): $50M-$300M mean -29.4% (n 33), $300M or more -48.3% (n 49), unknown +5.9% (n 21). These are three small cuts of one sample and were not tested. A study of any one of them would be a new pre-registered study (PUT2), not a reading of this one.

## What it means for a cash account that can only buy puts

AVOID calls do not turn into put trades. The warning flags still mark stocks that tend to fall, but the options market already knows that. A one-month put near the price on these names cost about a fifth of the share price. After costs, the stock had to fall about 22% by expiry just to break even. The typical one fell about 5%. So most puts lost money, 43% expired worthless, and the few big winners did not pay for the rest. The fall MV1 found was also biggest in the stocks that had no puts at all. For this account, the value of an AVOID call is in the avoiding: not buying the stock. It is not a trade in its own right. A different strike, expiry, entry day or filter would be a new study (PUT2), written down before any price is seen.

## Deviations

Items 1 to 9 were listed in the 19 Oct pause report and are updated here with final counts. Items 10 to 15 are new on 20 Oct.

1. **Calls made before the sample was drawn.** To learn the API's format, the LTBR 2024-10-29 event's Dec 2024 put list, one option price for it and one contract check were looked up. There were also two lookups on an NVDA contract that was adjusted after its split. LTBR 2024-10-29 is not in either sample. LTBR 2025-02-07 is in T2, with different contracts. The 19 Oct report said the NVDA cache files were deleted, but both NVDA check files were still in `cache/check/` on 20 Oct. They belong to no event and `run.py` never reads them. No choice changed because of these calls.
2. **Pools, built from MV1's own `mech_any` flag.** T1 = `mech_any == True` and market-value bucket not under $50M: 1,255 rows. Unknown market value is kept, because the pre-registration only excludes "under $50M". There is no event filter. T2 = `mech_any == False` and not under $50M: 1,876 rows. The 595 rows with an unknown flag are in neither pool, as in MV1.
3. **How the sample is drawn.** `np.random.default_rng(20261019).choice(len(pool), n, replace=False)` on each pool in `listB.csv` order, with a fresh generator for each test.
4. **Trading days.** A trading day is a day the stock has a bar in the runners' raw unadjusted bars. Once those files end (9 Oct 2026) or the stock stops trading, NYSE weekdays are counted instead (15 T1 and 4 T2 events). The expiry is the first standard monthly on or after the 20th trading day after t+1. Two expiries moved to the Thursday because the Friday was a holiday: 17 Apr 2025 and 18 Jun 2026.
5. **Which contracts count.** Only standard puts count: 100 shares, the root equals the ticker, no extra deliverables. If only adjusted puts were listed, the event counts as "no put listed", with a note (T1: QMCO, SST, SCLX, WOLF, BTM; T2: ARQQ).
6. **How adjustments are found.** Massive split and stock-dividend records dated after the gain day and on or before expiry. Then a lookup of the contract as of expiry day, where "not found" or changed terms means it was adjusted. The pre-registration orders the exclusions no put, then no fill, then adjusted. So an event can be filled and still be excluded later (3 in T1).
7. **The full put list is used.** For names of $300M or more, the run first asks for strikes within 25% either side of the close. The very first calls used 0.5x to 1.5x. Both windows are symmetric, so they always hold the closest strike when they are not empty. An empty window is followed by the full list.
8. **Expiry after the run date.** Seven events had a 20 Nov 2026 expiry, which has not happened yet. Five of them had a fill and are excluded as "no stock close at expiry" (T1: SECZ, GLND twice, BFLY; T2: VKTX). The other two were already out: INDP (no put listed) and SKYA (no fill).
9. **Odd outcomes left as the rule gives them.** QURE: the closest strike listed on t+1 was 25 against a $47.50 close, so the put was far out of the money (it expired worthless). Other strikes far from the close: in T1 NNBR (2.5 vs 3.62), VERU (1 vs 1.28), INV (5 vs 4.03), GSIT (5 vs 3.95) and TE (5 vs 3.83); in T2 ZNTL, QIPT, NB, GAU and INZY (2.5 vs 1.35). NA (2025-06-24): the put did not trade on t+1, so it was entered on t+2.
10. **The split lookup used a different path.** The connector refuses `/v3/reference/splits` ("Path not in allowlist"). The same Massive split records come from `/stocks/v1/splits`, with the same columns as the runners split files. One call covered 1 to 16 Oct 2026 (62 records, one page). `ingest.py` was changed to save that path under the cache file `run.py` expects. The refused call was not cached.
11. **How the cache was filled on 20 Oct.** All responses were saved with `ingest.py`'s transcript method, with this session's transcript passed by path. The default picks the newest four transcripts, and other agents were running at the same time. 631 calls were made, 5 a minute, with no rate-limit errors: 630 saved, plus the refused split call. The 16 Oct grouped daily bars (12,630 rows, one page) were read from the overflow file. They gave the expiry-day stock close for 9 events (5 T1, 4 T2).
12. **RESULTS.md was written by Claude, not by `run.py`.** The docstring says `run.py` writes it, but the writer was never built. Every headline number is copied from `results.json`. The numbers marked "from the trades files" were computed from `trades_T1.csv` and `trades_T2.csv` with a short script: counts by reason, break-even falls, the fade with and without puts, thin fills, and the mean without the best trades.
13. **`results.json` field meanings.** `put_listed` (T1 134) includes the 2 events never looked up. The true count is 132. `filled` means "had an entry price" (T1 110, T2 96). `used` is the count in the return tables (103 and 95).
14. **The stock's own return.** This is MV1's `ret20_net`: gain-day close to the close 20 sessions later, after a 1% round trip, with gains capped at +300%. It is missing for 3 used events in each test, whose 20 sessions end after MV1's data (T1: CHPT, TYRA, BNC; T2: CYPH, ROIV, VRA).
15. **Premium as a share of the price** is the entry VWAP before costs divided by the gain-day close. The pre-registration asked for "the average implied cost of the put as a share of the stock price" without saying which price.

Warning from the pre-registration, kept: MV1 chose the flags on this same data. So even a pass would have earned only a forward paper log.

## Files

- `run.py`: `python run.py plan` lists any calls still missing (none now). `python run.py` rebuilds `trades_T1.csv`, `trades_T2.csv` and `results.json` from `cache/`, with no network.
- `ingest.py`: copies connector responses from Claude transcripts into `cache/`.
- `trades_T1.csv`, `trades_T2.csv`: one row per sampled event, with its status, contract, entry, payoff and returns at 0%, 10% and 20% costs.
- `results.json`: every number in the tables above.
- `sample.csv`: the draw with each event's t+1, t+2, 20th trading day and expiry.
- `cache/`: 930 saved Massive responses, 300 from 19 Oct and 630 from 20 Oct (not in git). `cache/progress.csv` and `cache/interim_2026-10-19.json` are the 19 Oct interim state, kept as a record.
- `STATUS.md`: how the run went.
