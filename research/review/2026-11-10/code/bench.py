"""Matched benchmark: the median return of unflagged stocks in the same price and market-value bucket over the same dates.

Controls are a seeded random sample of US-listed stocks that never appeared in the ledger, the AVOID register or the
watchlist (fetch_ctrl.py). Buckets are set at each entry date: price under $1, $1-5, $5-20, $20+; market value under $50M,
$50-300M, $300M-2B, $2B+. This follows AV1's design (same price bucket, similar market value) at coarser resolution.
"""
import json, bisect, datetime as dt
from statistics import median
from core import *

CT = json.load(open(HERE / "ctrl.json"))
CAPS = json.load(open(ROOT / "watch/marketcap.json", encoding="utf-8"))["caps"]


def pbucket(p):
    return 0 if p < 1 else 1 if p < 5 else 2 if p < 20 else 3


def cbucket(c):
    return 0 if c < 50e6 else 1 if c < 300e6 else 2 if c < 2e9 else 3


PB = ["under $1", "$1-5", "$5-20", "$20+"]
CB = ["under $50M", "$50-300M", "$300M-2B", "$2B+"]

# The sample took a different share of each current market-value pool (fetch_ctrl.py), so each control is weighted by
# pool size / sample size for its pool. Without this, stocks that fell into a smaller pool would be over-counted.
POOLS = [(0, 50e6, 755, 450), (50e6, 300e6, 776, 450), (300e6, 2e9, 1281, 380), (2e9, 10e9, 999, 180), (10e9, 1e15, 837, 90)]


def weight(cap):
    for lo, hi, pool, n in POOLS:
        if lo <= cap < hi:
            return pool / n
    return 1.0


def wmedian(pairs):
    """Weighted median of (value, weight) pairs."""
    pairs = sorted(pairs)
    tot = sum(w for _, w in pairs)
    acc = 0.0
    for v, w in pairs:
        acc += w
        if acc >= tot / 2:
            return v
    return pairs[-1][0]


CTRL = {}
for t, d in CT.items():
    if "err" in d or not d.get("ts") or d.get("type") not in (None, "EQUITY"):
        continue
    rows = []
    a = d.get("a") or d["c"]
    for i, ts in enumerate(d["ts"]):
        o, c = d["o"][i], d["c"][i]
        if not o or not c:
            continue
        day = dt.datetime.fromtimestamp(ts, dt.UTC).date()
        if day > ASOF:
            continue
        adj = a[i] if a and a[i] else c
        rows.append((day, o * adj / c, adj, c, d["v"][i] or 0))
    if len(rows) < 60:
        continue
    bad = False
    for i in range(1, len(rows)):
        if rows[i][0] >= dt.date(2026, 8, 20):
            r = rows[i][2] / rows[i - 1][2]
            if r >= 4 or r <= 0.15:
                bad = True; break
    if not bad:
        CTRL[t] = (rows, [r[0] for r in rows], d["cap"])

_paths = {}


def ctrl_paths(ed):
    """{(pb, cb): [path...]} for every control on entry date ed, path = % return from that day's open to each later close."""
    if ed in _paths:
        return _paths[ed]
    out = {}
    bi = bisect.bisect_left(IDATES, ed)
    for t, (rows, dates, cap) in CTRL.items():
        e = bisect.bisect_left(dates, ed)
        if e >= len(rows) or dates[e] != ed or e == 0:
            continue
        eo = rows[e][1]
        capd = cap * rows[e][2] / rows[-1][2]
        key = (pbucket(rows[e][3]), cbucket(capd))
        path = []
        for k in range(0, 31):
            j = bi + k
            if j >= len(IDATES):
                break
            si = bisect.bisect_right(dates, IDATES[j]) - 1
            path.append((rows[max(si, e)][2] / eo - 1) * 100)
        out.setdefault(key, []).append((path, weight(cap)))
    _paths[ed] = out
    return out


def matched(t, m):
    """Adds to a measure() dict: bucket, n controls, and excess vs the matched median at each horizon and along the path."""
    ed = m["entry_date"]
    cp = ctrl_paths(ed)
    s = S(t)
    cap = CAPS.get(ALIAS.get(t, t)) or 0
    dates = [b[0] for b in s]
    e = bisect.bisect_left(dates, ed)
    capd = cap * s[e][2] / s[-1][2] if cap else None
    pb = pbucket(m["entry_raw"])
    cb = cbucket(capd) if capd else None
    pool = cp.get((pb, cb), []) if cb is not None else []
    if len(pool) < 8:                                       # too few: fall back to the price bucket alone
        pool = [p for (a, b), ps in cp.items() if a == pb for p in ps]
        cb_used = None
    else:
        cb_used = cb
    m["pb"], m["cb"], m["cap_entry"], m["n_ctrl"] = pb, cb, capd, len(pool)
    if len(pool) < 8:
        return m
    med = [wmedian([(p[k], w) for p, w in pool if len(p) > k]) for k in range(len(m["path"]))]
    m["cpath"] = [m["path"][k][0] - med[k] for k in range(len(m["path"]))]
    m["bench_path"] = med
    for h in H:
        if len(m["path"]) >= h:
            m[f"c{h}"] = m["cpath"][h - 1]
            m[f"b{h}"] = med[h - 1]
    return m
