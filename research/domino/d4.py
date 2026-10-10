"""D4: the scorecard. Rules are in PREREG_D4.md (committed before this ran). Usage: python d4.py

For each stage-3 trade, scores the company on three questions using only SEC facts filed on or before the trade date:
R real business (annual revenue >= $10M), C can pay its bills (positive operating cash flow, or cash >= 12 months of
burn), D not printing shares (share count up < 25% in a year). Reads d3_trades_cap.csv (returns capped at +300%).
"""
import json, os, time, urllib.request
from datetime import date, timedelta
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "PersonalResearch research@example.com"}
CACHE = os.path.join(HERE, "facts_cache"); os.makedirs(CACHE, exist_ok=True)
ANNUAL = {"10-K", "10-K/A", "10-KT", "20-F", "20-F/A", "40-F", "40-F/A"}
TAGS = {"rev": [("us-gaap", "Revenues"), ("us-gaap", "RevenueFromContractWithCustomerExcludingAssessedTax"),
                ("us-gaap", "RevenueFromContractWithCustomerIncludingAssessedTax"), ("us-gaap", "SalesRevenueNet"),
                ("us-gaap", "RevenuesNetOfInterestExpense"), ("ifrs-full", "Revenue")],
        "ocf": [("us-gaap", "NetCashProvidedByUsedInOperatingActivities"), ("us-gaap", "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"),
                ("ifrs-full", "CashFlowsFromUsedInOperatingActivities")],
        "cash": [("us-gaap", "CashAndCashEquivalentsAtCarryingValue"), ("us-gaap", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"),
                 ("us-gaap", "Cash"), ("ifrs-full", "CashAndCashEquivalents")],
        "shares": [("dei", "EntityCommonStockSharesOutstanding"), ("us-gaap", "CommonStockSharesOutstanding")]}

z = np.load(os.path.join(HERE, "..", "runners", "work", "panel.npz"), allow_pickle=True)
tick = [str(x) for x in z["tick"]]; dates = [str(x) for x in z["dates"]]; T = len(dates)
with np.errstate(divide="ignore", invalid="ignore"):
    fac = np.where(z["craw"] > 0, z["c"] / z["craw"], np.nan)
cikmap = pd.read_csv(os.path.join(HERE, "sic_map.csv"), dtype=str).set_index("ticker").cik.to_dict()
KEEP = set("3674 3672 3670 3679 3559 3571 3572 3576 3577 3661 3663 3669 3825 3827 3620 3621 3690 3443 3585 4911 4931 4924 1623 1731 1600 1311 1381 1389 3533 1000 1040 1090 1220 1400 3312 3330 3721 3760 3812 3480 7374 7373 4412 4400 4213".split())
t = pd.read_csv(os.path.join(HERE, "d3_trades_cap.csv"), dtype={"sic": str})
s3 = t[t.sic.isin(KEEP) & t.takeable & ~t.china & ~t.rs90].copy()
s3["ticker"] = [tick[s] for s in s3.s]; s3["date"] = [dates[d] for d in s3.d]


def facts(cik):
    p = os.path.join(CACHE, f"CIK{cik}.json")
    if os.path.exists(p):
        return json.load(open(p, encoding="utf-8"))
    out = {k: [] for k in TAGS}
    try:
        j = json.loads(urllib.request.urlopen(urllib.request.Request(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json", headers=UA), timeout=60).read())
        for k, tags in TAGS.items():
            for tax, tag in tags:
                units = j.get("facts", {}).get(tax, {}).get(tag, {}).get("units", {})
                for unit, rows in units.items():
                    if unit not in ("USD", "shares"): continue
                    for r in rows:
                        out[k].append([r.get("start"), r.get("end"), r.get("val"), r.get("form"), r.get("filed")])
        time.sleep(0.13)
    except Exception as ex:
        out["error"] = str(ex)[:80]
    json.dump(out, open(p, "w", encoding="utf-8"))
    return out


def days(a, b):
    return (date.fromisoformat(b) - date.fromisoformat(a)).days


def annual(rows, asof):
    best = None
    for start, end, val, form, filed in rows:
        if not (start and end and filed) or form not in ANNUAL or filed > asof or val is None: continue
        if not 330 <= days(start, end) <= 400: continue
        if best is None or (end, filed) > (best[0], best[1]): best = (end, filed, val)
    return best[2] if best else None


def instant(rows, asof):
    best = None
    for start, end, val, form, filed in rows:
        if not (end and filed) or filed > asof or val is None: continue
        if best is None or (end, filed) > (best[0], best[1]): best = (end, filed, val)
    return best


def fac_at(j, day):
    """split factor of stock j on the last panel day on or before `day` (None outside the panel)."""
    if day < dates[0]: return None
    i = np.searchsorted(dates, day, side="right") - 1
    while i >= 0 and not np.isfinite(fac[i, j]): i -= 1
    return float(fac[i, j]) if i >= 0 else None


def score(j, cik, asof):
    f = facts(cik)
    rev, ocf, cash = annual(f["rev"], asof), annual(f["ocf"], asof), instant(f["cash"], asof)
    R = None if rev is None else rev >= 10e6
    C = None
    if ocf is not None:
        C = True if ocf >= 0 else (None if cash is None else cash[2] >= -ocf)
    D = None
    cur = instant(f["shares"], asof)
    if cur:
        prior = None
        for start, end, val, form, filed in f["shares"]:
            if not (end and filed) or filed > asof or not val: continue
            gap = days(end, cur[0])
            if 270 <= gap <= 460 and (prior is None or abs(gap - 365) < abs(days(prior[0], cur[0]) - 365)): prior = (end, val)
        if prior and prior[1] > 0:
            growth = cur[2] / prior[1]
            f1, f0 = fac_at(j, cur[0]), fac_at(j, prior[0])
            if f1 and f0 and f1 > 0: growth *= f0 / f1          # put both counts on the same share basis across splits
            D = growth - 1 < 0.25
    return R, C, D


stocks = sorted(s3.ticker.unique()); miss = [x for x in stocks if x not in cikmap]
print(f"stage-3 stocks: {len(stocks)} | without a CIK: {len(miss)}")
res = [score(s, cikmap[tk], dt) if tk in cikmap else (None, None, None) for s, tk, dt in zip(s3.s, s3.ticker, s3.date)]
s3["R"], s3["C"], s3["D"] = zip(*res)
known = s3[["R", "C", "D"]].notna().all(axis=1)
s3["score"] = np.where(known, s3[["R", "C", "D"]].fillna(False).astype(bool).sum(axis=1), -1)
s3.to_csv(os.path.join(HERE, "d4_trades.csv"), index=False)
YEARS = (T - 37) / 252; rng = np.random.default_rng(20261010)


def edge(x, col):
    ex = x[col] - x["ctl_" + col]; day = np.full(T, np.nan); g = ex.groupby(x.d).mean(); day[g.index] = g.values
    bs = []
    for _ in range(2000):
        st = rng.integers(0, T - 4, 101); bs.append(np.nanmean(day[(st[:, None] + np.arange(5)).ravel()[:T]]))
    lo, hi = np.nanpercentile(bs, [2.5, 97.5]); return float(np.nanmean(day)), float(lo), float(hi)


def row(name, x):
    if len(x) < 20:
        print(f"{name:34s} {len(x):5d} trades (too few)"); return dict(group=name, trades=int(len(x)))
    e5, e10 = edge(x, "c5"), edge(x, "c10"); nd = x.d.nunique()
    r = dict(group=name, trades=int(len(x)), stocks=int(x.ticker.nunique()), per_year=round(len(x) / YEARS), signal_days=int(nd), per_signal_day=float(x.groupby("d").size().median()),
             c1=float(x.c1.mean()), c5=float(x.c5.mean()), c10=float(x.c10.mean()), med5=float(x.c5.median()), med10=float(x.c10.median()), pos10=float((x.c10 > 0).mean()),
             edge5=e5, edge10=e10, hit20_5=float((x.mfe5 >= .2).mean()), hit50_5=float((x.mfe5 >= .5).mean()), hit20_10=float((x.mfe10 >= .2).mean()), hit50_10=float((x.mfe10 >= .5).mean()),
             worst10=float(x.mae10.mean()), net1=float(x.c10.mean() - .01), net35=float(x.c10.mean() - .035))
    print(f"{name:34s} {r['trades']:5d} trades {r['stocks']:4d} stocks {r['per_year']:5d}/yr {nd:4d} days x{r['per_signal_day']:.0f} | avg d1 {r['c1']:+.1%} d5 {r['c5']:+.1%} d10 {r['c10']:+.1%} | median d5 {r['med5']:+.1%} d10 {r['med10']:+.1%} pos {r['pos10']:.0%} | "
          f"edge d5 {e5[0]:+.2%} [{e5[1]:+.2%},{e5[2]:+.2%}] d10 {e10[0]:+.2%} [{e10[1]:+.2%},{e10[2]:+.2%}] | +20%/+50% in 10d {r['hit20_10']:.1%}/{r['hit50_10']:.1%} worst {r['worst10']:+.1%} | net 1% {r['net1']:+.1%} net 3.5% {r['net35']:+.1%}")
    return r


print(f"answers known for {known.mean():.0%} of trades | R pass {s3.R.mean():.0%} C pass {s3.C.mean():.0%} D pass {s3.D.mean():.0%} (of known)\n")
out = [row("all stage 3 (capped)", s3), row("score 3: holds up", s3[s3.score == 3]), row("score 2", s3[s3.score == 2]), row("score 0-1", s3[s3.score.isin([0, 1])]),
       row("unknown", s3[s3.score == -1]), row("score 3 + own volume 2x", s3[(s3.score == 3) & (s3.relvol >= 2)]),
       row("score 2-3 + own volume 2x", s3[(s3.score >= 2) & (s3.relvol >= 2)])]
print("\nby question (known answers only):")
for q, lab in (("R", "revenue >= $10M"), ("C", "can pay its bills"), ("D", "not printing shares")):
    for v in (True, False):
        out.append(row(f"{lab}: {'yes' if v else 'no'}", s3[s3[q] == v]))
json.dump(out, open(os.path.join(HERE, "d4_results.json"), "w"), indent=1)
