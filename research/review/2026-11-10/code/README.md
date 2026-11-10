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
