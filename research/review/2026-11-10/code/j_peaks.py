"""J. Peaks, not end points. For each flagged stock: the highest high and lowest low in the 10 and 20 sessions after the
first open we could act on, when the peak came, and which was touched first: +10% or -10% (and +20% / -20%).
The same numbers for unflagged stocks in the same price band give the base rate, because cheap stocks swing anyway."""
import sys, json, pickle, bisect, csv, datetime as dt
from statistics import median, mean
from core import *

sys.stdout.reconfigure(encoding="utf-8")
CT = json.load(open(HERE / "ctrl_hl.json"))
POOLS = [(0, 50e6, 755, 450), (50e6, 300e6, 776, 450), (300e6, 2e9, 1281, 380), (2e9, 10e9, 999, 180), (10e9, 1e15, 837, 90)]
wt = lambda cap: next((pool / n for lo, hi, pool, n in POOLS if lo <= cap < hi), 1.0)
pbucket = lambda p: 0 if p < 1 else 1 if p < 5 else 2 if p < 20 else 3
PB = ["under $1", "$1-5", "$5-20", "$20+"]


def touch(w, eo, up, dn):
    """First touch within the window: 'up', 'down', 'both' (same day, unknown order) or 'none'. w rows carry high [6] and low [7]."""
    for b in w:
        u, d = b[6] >= eo * (1 + up / 100), b[7] <= eo * (1 - dn / 100)
        if u and d:
            return "both"
        if u:
            return "up"
        if d:
            return "down"
    return "none"


def stat(s, e, n):
    w = s[e:e + n]
    if len(w) < min(n, 5):
        return None
    eo = s[e][1]
    pk = max(range(len(w)), key=lambda i: w[i][6]); tr = min(range(len(w)), key=lambda i: w[i][7])
    return {"peak": (w[pk][6] / eo - 1) * 100, "peak_day": pk + 1, "low": (w[tr][7] / eo - 1) * 100, "low_day": tr + 1, "end": (w[-1][2] / eo - 1) * 100,
            "t10": touch(w, eo, 10, 10), "t20": touch(w, eo, 20, 20), "full": len(w) >= n,
            "d1_high": (w[0][6] / eo - 1) * 100, "d1_low": (w[0][7] / eo - 1) * 100}


# control series with highs and lows
CTRL = {}
for t, d in CT.items():
    if "err" in d or not d.get("ts") or d.get("type") not in (None, "EQUITY"):
        continue
    a = d.get("a") or d["c"]; rows = []
    for i, ts in enumerate(d["ts"]):
        o, c = d["o"][i], d["c"][i]
        if not o or not c:
            continue
        day = dt.datetime.fromtimestamp(ts, dt.UTC).date()
        if day > ASOF:
            continue
        k = (a[i] if a and a[i] else c) / c
        rows.append((day, o * k, c * k, d["v"][i] or 0, o, c, (d["h"][i] or max(o, c)) * k, (d["l"][i] or min(o, c)) * k))
    if len(rows) < 60:
        continue
    if any(rows[i][0] >= dt.date(2026, 8, 20) and (rows[i][2] / rows[i - 1][2] >= 4 or rows[i][2] / rows[i - 1][2] <= 0.15) for i in range(1, len(rows))):
        continue
    CTRL[t] = (rows, [r[0] for r in rows], wt(d["cap"]))
_base = {}


def base(ed, pb, n):
    """Weighted base rates for unflagged stocks in price band pb entering on ed: dict of shares and medians."""
    key = (ed, pb, n)
    if key in _base:
        return _base[key]
    xs = []
    for t, (rows, dates, w) in CTRL.items():
        e = bisect.bisect_left(dates, ed)
        if e >= len(rows) or dates[e] != ed or pbucket(rows[e][4]) != pb:
            continue
        st = stat(rows, e, n)
        if st and st["full"]:
            xs.append((st, w))
    _base[key] = xs
    return xs


def wshare(xs, f):
    tot = sum(w for _, w in xs)
    return 100 * sum(w for s, w in xs if f(s)) / tot if tot else None


def wmed(xs, k):
    v = sorted((s[k], w) for s, w in xs); tot = sum(w for _, w in v); acc = 0
    for x, w in v:
        acc += w
        if acc >= tot / 2:
            return x


def group(name, items, n=10, side="long"):
    """items: (ticker, found). Prints flagged numbers next to the base rate for the same price bands and dates."""
    S_, B_ = [], []
    for t, found in items:
        s = S(t)
        if not s:
            continue
        dates = [b[0] for b in s]
        f = dt.date.fromisoformat(found) if isinstance(found, str) else found
        e = bisect.bisect_right(dates, f)
        if e >= len(s):
            continue
        st = stat(s, e, n)
        if not st or not st["full"]:
            continue
        k = 1.0
        for sd, exp in SPL.get(ALIAS.get(t, t), []):
            if sd > dates[e]:
                k *= exp
        S_.append(st)
        B_ += base(dates[e], pbucket(s[e][4] / k), n)
    if len(S_) < 5:
        print(f"{name:46} n={len(S_)} (too few with {n} full sessions)"); return None
    sh = lambda f: 100 * sum(1 for s in S_ if f(s)) / len(S_)
    out = dict(name=name, n=len(S_), sessions=n,
               peak=median(s["peak"] for s in S_), peak_b=wmed(B_, "peak"), low=median(s["low"] for s in S_), low_b=wmed(B_, "low"),
               end=median(s["end"] for s in S_), end_b=wmed(B_, "end"), peak_day=median(s["peak_day"] for s in S_), low_day=median(s["low_day"] for s in S_),
               up10=sh(lambda s: s["t10"] == "up"), up10_b=wshare(B_, lambda s: s["t10"] == "up"), dn10=sh(lambda s: s["t10"] == "down"), dn10_b=wshare(B_, lambda s: s["t10"] == "down"),
               both10=sh(lambda s: s["t10"] == "both"), up20=sh(lambda s: s["t20"] == "up"), up20_b=wshare(B_, lambda s: s["t20"] == "up"),
               dn20=sh(lambda s: s["t20"] == "down"), dn20_b=wshare(B_, lambda s: s["t20"] == "down"),
               pk10=sh(lambda s: s["peak"] >= 10), pk10_b=wshare(B_, lambda s: s["peak"] >= 10), pk20=sh(lambda s: s["peak"] >= 20), pk20_b=wshare(B_, lambda s: s["peak"] >= 20),
               lo10=sh(lambda s: s["low"] <= -10), lo10_b=wshare(B_, lambda s: s["low"] <= -10), lo20=sh(lambda s: s["low"] <= -20), lo20_b=wshare(B_, lambda s: s["low"] <= -20))
    o = out
    print(f"{name:46} n={o['n']:3} {n:2}s | peak {o['peak']:+6.1f} (similar {o['peak_b']:+5.1f}) day {o['peak_day']:4.1f} | low {o['low']:+6.1f} (similar {o['low_b']:+5.1f}) day {o['low_day']:4.1f} | end {o['end']:+6.1f} ({o['end_b']:+5.1f})"
          f" | +10% first {o['up10']:3.0f}% ({o['up10_b']:3.0f}%) -10% first {o['dn10']:3.0f}% ({o['dn10_b']:3.0f}%) | +20% first {o['up20']:3.0f}% ({o['up20_b']:3.0f}%) -20% first {o['dn20']:3.0f}% ({o['dn20_b']:3.0f}%)"
          f" | ever +10% {o['pk10']:3.0f}% ({o['pk10_b']:3.0f}%) ever -10% {o['lo10']:3.0f}% ({o['lo10_b']:3.0f}%)")
    return out


if __name__ == "__main__":
    rows = pickle.load(open(HERE / "rows.pkl", "rb")); reg = pickle.load(open(HERE / "reg.pkl", "rb")); G = pickle.load(open(HERE / "found_groups.pkl", "rb")); picks = pickle.load(open(HERE / "picks.pkl", "rb"))

    def first(rs, key="found"):
        seen, out = set(), []
        for r in sorted(rs, key=lambda r: r.get(key) or r.get("date")):
            if r["ticker"] not in seen:
                seen.add(r["ticker"]); out.append(r)
        return out
    KIND = {"ESRT": 0, "SKYA": 0, "PED": 0, "SRTA": 0, "DIBS": 0, "ACB": 0, "XPOF": 0, "CPAC": 0, "DOLE": 0, "SEER": 0, "VVR": 0,
            "MTUS": 1, "RYAM": 1, "MOD": 1, "THRM": 1, "WHF": 1, "CTVA": 1, "VYLR": 1, "HMH": 1, "MSGS": 1, "BORR": 2, "IMSR": 2}
    res = []
    for n in (5, 10, 20):
        print(f"\n===== first {n} sessions (similar unflagged stocks in brackets) =====")
        sets = [
            ("OWN / WATCH picks", [(m["ticker"], m["date"]) for m in picks]),
            ("  picks: outside buyer or holder acting", [(m["ticker"], m["date"]) for m in picks if KIND[m["ticker"]] == 0]),
            ("  picks: company story, or insiders", [(m["ticker"], m["date"]) for m in picks if KIND[m["ticker"]] != 0]),
            ("Long-side names we wrote up", [(m["ticker"], m["found"]) for m in first([m for (v, g), ms in G.items() if v in ("TRACKED", "WATCH", "OWN") for m in ms])]),
            ("  activists and big holders", [(m["ticker"], m["found"]) for m in first(G[("TRACKED", "Activists and big holders")] + G.get(("WATCH", "Activists and big holders"), []))]),
            ("  contracts and catalysts", [(m["ticker"], m["found"]) for m in first(G[("TRACKED", "Contracts and catalysts")] + G.get(("WATCH", "Contracts and catalysts"), []) + G.get(("OWN", "Contracts and catalysts"), []))]),
            ("  insider buying", [(m["ticker"], m["found"]) for m in first(G[("TRACKED", "Insider buying")])]),
            ("  merger arb and tenders", [(m["ticker"], m["found"]) for m in first(G[("TRACKED", "Merger arb and tenders")] + G.get(("WATCH", "Merger arb and tenders"), []))]),
            ("Scanner buy-side flags, takeable", [(r["ticker"], r["found"]) for r in first([r for r in rows if r["cat"] in ("8k_strategic_review", "activist_13d", "tender_issuer_buyback") and r["take"]])]),
            ("Scanner special dividends, takeable", [(r["ticker"], r["found"]) for r in first([r for r in rows if r["cat"] == "8k_special_dividend" and r["take"]])]),
            ("Scanner supply flags, takeable", [(r["ticker"], r["found"]) for r in first([r for r in rows if r["cat"] in ("8k_reverse_split", "registration_effective", "share_registration") and r["take"]])]),
            ("AVOID register, takeable", [(m["ticker"], m["date"]) for m in reg if m["take"]]),
            ("AVOID register, all", [(m["ticker"], m["date"]) for m in reg]),
        ]
        for name, items in sets:
            o = group(name, items, n)
            if o:
                res.append(o)
    pickle.dump(res, open(HERE / "peaks.pkl", "wb"))
