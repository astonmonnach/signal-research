"""K. Results days at actual times, for every company that appeared in our scans (not only the names we wrote up).
An 8-K with item 2.02 is a results release. Gap = last trade before the release -> first regular open after it.
Then what the stock did from that open: 30 minutes, 1 hour, 2 hours, the close, the next close and the third close."""
import sys, json, pickle, datetime as dt
from statistics import median, mean
from intraday import *

sys.stdout.reconfigure(encoding="utf-8")
FIL = json.load(open(HERE / "filings.json"))
have = {p.name[:-8] for p in (HERE / "i5").glob("*.json.gz")}
ev, seen = [], set()
for c, d in FIL.items():
    tk = next((t for t in d.get("tickers", []) if t in have), None)
    if not tk:
        continue
    for acc, form, fd, adt, items in d.get("rows", []):
        if form != "8-K" or "2.02" not in (items or "") or fd > "2026-11-09":
            continue
        t0 = dt.datetime.fromisoformat(adt.replace("Z", "+00:00"))
        x = react(tk, t0)
        if not x or (tk, x["entry_time"]) in seen:
            continue
        seen.add((tk, x["entry_time"]))
        x.update(ticker=tk, fd=fd, acc=acc)
        ev.append(x)
pickle.dump(ev, open(HERE / "results_events.pkl", "wb"))
liq = [e for e in ev if e["entry"] >= 1 and e["dollar_vol_day"] >= 500_000]
print(len(ev), "results releases with 5-minute bars;", len(liq), "on stocks at $1+ that traded $500k+ that day;", sum(1 for e in liq if not e["in_hours"]), "released outside market hours")


def S_(v):
    v = [x for x in v if x is not None]
    return "    n/a" if not v else f"{median(v):+5.1f}/{mean(v):+5.1f}/{100 * sum(x > 0 for x in v) / len(v):3.0f}%"


B = [("gap down 10%+", -99, -10), ("gap down 5 to 10%", -10, -5), ("gap down 2 to 5%", -5, -2), ("flat (within 2%)", -2, 2), ("gap up 2 to 5%", 2, 5), ("gap up 5 to 10%", 5, 10), ("gap up 10%+", 10, 999)]
print("\nmedian / mean / share positive, from the first regular open after the release")
print(f"{'overnight gap':20} {'n':>4} | {'+30m':>17} | {'+1h':>17} | {'+2h':>17} | {'close':>17} | {'close vs IWM':>17} | {'next close':>17} | {'3rd close':>17} | peak 2h / low 2h (median)")
for lab, lo, hi in B:
    s = [e for e in liq if lo <= e["gap"] < hi and not e["in_hours"]]
    if len(s) < 5:
        print(f"{lab:20} {len(s):4} | too few"); continue
    print(f"{lab:20} {len(s):4} | {S_([e['r30'] for e in s])} | {S_([e['r60'] for e in s])} | {S_([e['r120'] for e in s])} | {S_([e['rclose'] for e in s])} | {S_([e.get('xclose') for e in s])} | {S_([e.get('rnext') for e in s])} | {S_([e.get('r3') for e in s])} | {median(e['peak_2h'] for e in s):+5.1f} / {median(e['low_2h'] for e in s):+5.1f}")
# simple shuffle-free check: is the gap-down bounce different from zero? bootstrap the mean
import random
for lab, lo, hi in (("gap down 5%+", -99, -5), ("gap up 5%+", 5, 999)):
    s = [e for e in liq if lo <= e["gap"] < hi and not e["in_hours"]]
    for k in ("r30", "r120", "rclose", "xclose", "rnext"):
        v = [e[k] for e in s if e.get(k) is not None]
        if len(v) < 8:
            continue
        rng = random.Random(9); xs = sorted(mean([rng.choice(v) for _ in v]) for _ in range(8000))
        print(f"{lab:14} {k:7} n={len(v):3} mean {mean(v):+5.2f} [{xs[200]:+5.2f}, {xs[7800]:+5.2f}] median {median(v):+5.2f} positive {100 * sum(x > 0 for x in v) / len(v):.0f}%")
print("\nprice bands for the gap-down-5%+ group:")
s = [e for e in liq if e["gap"] < -5 and not e["in_hours"]]
for lab, f in (("under $5", lambda e: e["entry"] < 5), ("$5 to $20", lambda e: 5 <= e["entry"] < 20), ("$20+", lambda e: e["entry"] >= 20)):
    w = [e for e in s if f(e)]
    if len(w) >= 5:
        print(f"  {lab:10} n={len(w):3} | +30m {S_([e['r30'] for e in w])} | +2h {S_([e['r120'] for e in w])} | close {S_([e['rclose'] for e in w])} | next {S_([e.get('rnext') for e in w])}")
