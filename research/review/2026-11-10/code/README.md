# Code for the two-month review (10 Nov 2026)

Run from this folder, in this order. The two fetch scripts download about 2,700 tickers from Yahoo (about 20 minutes) into
`px.json` and `ctrl.json` here; those caches and the `.pkl` files are not committed.

```
python fetch_px.py      # daily bars for every ticker in the ledger, the AVOID register and found.csv
python fetch_ctrl.py    # daily bars for a seeded random sample of 1,550 unflagged stocks (the comparison group)
python a_ledger.py      # every ledger row at fixed horizons -> rows.pkl
python t_cat.py         # table by category
python b_picks.py       # OWN / WATCH picks, kills, found.csv groups
python c_tests.py       # reading vs raw scan, AVOID register, public calls, exploration-set state cuts
python d_paths.py       # day-by-day paths, small pockets, best and worst
python e_charts.py      # the four charts -> img/
```

`core.py` holds the price cleaning and the fixed-horizon measure; `bench.py` holds the matched comparison (same price and
market-value bucket, weighted for how the sample was drawn). Everything is as of the 9 Nov 2026 close (`ASOF` in core.py).

## Part 2: peaks and actual times

```
python fetch_5m.py        # 5-minute bars, last 60 trading days, pre-market and after-hours -> i5/ (about 25 minutes)
python fetch_sub.py       # SEC acceptance times for every filing in the scans -> accept.json, filings.json
python fetch_ctrl_hl.py   # the comparison stocks again, with daily highs and lows -> ctrl_hl.json
python j_peaks.py         # peaks, lows and which level was touched first, against base rates
python g_events.py        # every scanner flag from its SEC timestamp: gap, +30m, +1h, +2h, close, next closes
python h_picks.py         # every filing after a verdict for the names we wrote up (add --picks for the 22 picks only)
python k_results.py       # results days (8-K item 2.02) across every company in the scans
python l_exits.py         # take-profit and stop-loss exits
python i_calendar.py      # the day of each calendar event
python m_charts2.py       # charts 5 and 6
```

`intraday.py` holds the 5-minute loader and the reaction measure. Yahoo only serves 5-minute bars for the last 60 trading
days, so this part cannot be re-run for the same window after early December 2026.
