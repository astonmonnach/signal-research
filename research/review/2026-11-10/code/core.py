"""Shared loader for the two-month review: prices, benchmark, and fixed-horizon returns for any (ticker, found date).

Returns are from the first open after the found date (the first price that could be acted on), using dividend- and
split-adjusted prices, to the close 1, 5, 10 and 20 market sessions later. Excess is against IWM over the same dates.
"""
import csv, json, datetime as dt, bisect
from pathlib import Path
from statistics import median, mean

HERE = Path(__file__).parent
ROOT = Path(__file__).resolve().parents[4]
PX = json.load(open(HERE / "px.json"))
H = (1, 5, 10, 20)


ASOF = dt.date(2026, 11, 9)
ALIAS = {"MSGS": "MSGK"}
BAD = {}          # ticker -> why its prices were left out
SPL = {}          # ticker -> [(date, factor)] reverse/forward splits Yahoo has already applied to its history


def clean(t, d, out):
    """Fix reverse splits Yahoo lists but has not applied, and reject series with glitches (a jump that reverses, or an
    unexplained one-day rise of 4x or more). out rows: [date, adj_open, adj_close, volume, raw_open, raw_close]."""
    out = [list(b) for b in out if b[0] <= ASOF]
    for sd, num, den in d.get("splits", []) or []:
        sdate = dt.datetime.fromtimestamp(sd, dt.UTC).date()
        if not num or not den or num == den:
            continue
        exp = den / num                                    # 1:25 reverse split -> price x25
        fixed = False
        for i in range(1, len(out)):
            if abs((out[i][0] - sdate).days) <= 5 and out[i - 1][2]:
                r = out[i][2] / out[i - 1][2]
                if exp > 1.5 and 0.6 < r / exp < 1.6 or exp < 0.67 and 0.6 < r / exp < 1.6:
                    for j in range(i):
                        out[j][1] *= exp; out[j][2] *= exp; out[j][6] *= exp; out[j][7] *= exp
                    fixed = True
                    break
        if not fixed:
            SPL.setdefault(t, []).append((sdate, exp))     # Yahoo applied it: raw prices before sdate are already scaled
    W0 = dt.date(2026, 8, 20)                               # only the window the review uses
    for i in range(1, len(out)):
        if not out[i - 1][2] or out[i][0] < W0:
            continue
        r = out[i][2] / out[i - 1][2]
        vols = [b[3] for b in out[max(0, i - 20):i] if b[3]]
        surge = out[i][3] >= 3 * (sum(vols) / len(vols)) if vols else False
        if r >= 4 and not surge:                            # a real squeeze comes with a volume surge; a glitch does not
            BAD[t] = f"unexplained x{r:.1f} on {out[i][0]}"; return None
        if r >= 2.5 or r <= 0.4:
            for k in range(i + 1, min(i + 4, len(out))):
                if 0.6 < out[k][2] / out[i - 1][2] < 1.6 and not surge and (r >= 2.5 and out[k][2] / out[i][2] <= 0.5 or r <= 0.4 and out[k][2] / out[i][2] >= 2):
                    BAD[t] = f"spike and revert around {out[i][0]}"; return None
    return [tuple(b) for b in out]


def series(t):
    t = ALIAS.get(t, t)
    d = PX.get(t)
    if not d or "err" in d or not d.get("ts"):
        return None
    out = []
    a = d.get("a") or d["c"]
    for i, ts in enumerate(d["ts"]):
        o, c, v = d["o"][i], d["c"][i], d["v"][i]
        if not o or not c:
            continue
        adj = a[i] if a and a[i] else c
        k = adj / c
        hh = (d.get("h") or [None] * len(d["ts"]))[i] or max(o, c)
        ll = (d.get("l") or [None] * len(d["ts"]))[i] or min(o, c)
        out.append((dt.datetime.fromtimestamp(ts, dt.UTC).date(), o * k, adj, v or 0, o, c, hh * k, ll * k))
    if not out:
        return None
    return clean(t, d, out) or None


_S = {}


def S(t):
    if t not in _S:
        _S[t] = series(t)
    return _S[t]


IWM = S("IWM")
IDATES = [b[0] for b in IWM]


def measure(t, found, bench=IWM):
    """dict with entry date/price, raw entry price, returns and excess at each horizon, the daily excess path, and to-now."""
    s = S(t)
    if not s:
        return None
    if isinstance(found, str):
        found = dt.date.fromisoformat(found)
    dates = [b[0] for b in s]
    e = bisect.bisect_right(dates, found)
    if e >= len(s):
        return None
    ed = dates[e]
    bi = bisect.bisect_left(IDATES, ed)
    if bi >= len(IDATES) or IDATES[bi] != ed:
        bi = min(bi, len(IDATES) - 1)
    eo, bo = s[e][1], bench[bi][1]
    k = 1.0
    for sdate, exp in SPL.get(ALIAS.get(t, t), []):
        if sdate > ed:
            k *= exp
    out = {"entry_date": ed, "entry": eo, "entry_raw": s[e][4] / k, "sessions": len(IDATES) - bi, "split_k": k}
    # 20-day median dollar volume up to the found day
    pre = s[max(0, e - 20):e]
    out["mdv20"] = median(b[5] * b[3] for b in pre) if pre else None      # price x volume is unchanged by a split
    out["pre5"] = (s[e - 1][2] / s[e - 6][2] - 1) * 100 if e >= 6 else None
    out["found_day"] = (s[e - 1][2] / s[e - 2][2] - 1) * 100 if e >= 2 else None
    out["gap"] = (eo / s[e - 1][2] - 1) * 100 if e >= 1 else None          # found-day close to entry open
    hi = max(b[2] for b in s[max(0, e - 252):e]) if e else None
    out["from_high"] = (s[e - 1][2] / hi - 1) * 100 if hi else None
    path = []
    for k in range(0, 31):                                                  # k=0 is the entry-day close
        j = bi + k
        if j >= len(IDATES):
            break
        d = IDATES[j]
        si = bisect.bisect_right(dates, d) - 1                              # last stock bar on or before that session
        if si < e:
            si = e
        r = s[si][2] / eo - 1
        b = bench[j][2] / bo - 1
        path.append(((r) * 100, (r - b) * 100))
    out["path"] = path
    for h in H:
        if len(path) >= h:
            out[f"r{h}"], out[f"x{h}"] = path[h - 1]
    out["now"] = s[-1][2]
    out["r_now"] = (s[-1][2] / eo - 1) * 100
    out["x_now"] = out["r_now"] - (bench[-1][2] / bo - 1) * 100
    out["last_date"] = dates[-1]
    w = [p[0] for p in path]
    out["max_up"], out["max_dn"] = (max(w), min(w)) if w else (None, None)
    return out


def ledger():
    return list(csv.DictReader(open(ROOT / "ledger/ledger.csv", encoding="utf-8")))


def stats(vals):
    v = [x for x in vals if x is not None]
    if not v:
        return dict(n=0)
    v2 = sorted(v)
    lo, hi = v2[int(0.05 * (len(v2) - 1))], v2[int(0.95 * (len(v2) - 1))]
    wins = [min(max(x, lo), hi) for x in v]
    return dict(n=len(v), med=median(v), mean=mean(v), wmean=mean(wins), pos=100 * sum(x > 0 for x in v) / len(v))


def fmt(s, key="med"):
    return "n/a" if not s.get("n") else f"{s[key]:+.1f}"


def excursion(t, found, upto=None):
    """Peak and trough after the first open we could act on, from daily highs and lows.
    Returns entry, peak % and its session number and date, the worst low before the peak, the lowest low and its session, and now."""
    s = S(t)
    if not s:
        return None
    if isinstance(found, str):
        found = dt.date.fromisoformat(found)
    dates = [b[0] for b in s]
    e = bisect.bisect_right(dates, found)
    if e >= len(s):
        return None
    w = s[e:] if upto is None else s[e:e + upto]
    eo = s[e][1]
    pk = max(range(len(w)), key=lambda i: w[i][6])
    tr = min(range(len(w)), key=lambda i: w[i][7])
    return {"entry_date": dates[e], "entry": eo, "sessions": len(w),
            "peak": (w[pk][6] / eo - 1) * 100, "peak_day": pk + 1, "peak_date": w[pk][0],
            "pain_before_peak": (min(b[7] for b in w[:pk + 1]) / eo - 1) * 100,
            "trough": (w[tr][7] / eo - 1) * 100, "trough_day": tr + 1, "trough_date": w[tr][0],
            "now": (w[-1][2] / eo - 1) * 100, "day1_high": (w[0][6] / eo - 1) * 100, "day1_low": (w[0][7] / eo - 1) * 100, "day1_close": (w[0][2] / eo - 1) * 100}
