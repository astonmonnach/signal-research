"""Run research/btc_ib/PREREG.md exactly. Writes RESULTS.md and trades.csv."""
import sys
import numpy as np
import pandas as pd

DATA = r"C:\Users\thoma\Desktop\crypto-flow\btcusdt_flow_1m.parquet"
SESSIONS = {"Asia": (0, 0), "London": (7, 0), "NY": (13, 30)}
OR_MIN, MIN_W, WINDOW_H, TICK = 60, 0.0030, 4, 0.10
FEE_IN, FEE_OUT, SLIP = 0.00015, 0.00045, 0.0002

d = pd.read_parquet(DATA, columns=["ts", "o", "h", "l", "c"]).set_index("ts").sort_index()
d = d[~d.index.duplicated()]
daily = d.resample("1D").agg({"h": "max", "l": "min"})
drng = (daily.h - daily.l)
gate = (drng.shift(1) >= drng.shift(1).rolling(60).median())          # prior day vs trailing median, no look-ahead

starts = []
for day in pd.date_range(d.index[0].normalize(), d.index[-1].normalize(), freq="D"):
    for name, (hh, mm) in SESSIONS.items():
        starts.append((day + pd.Timedelta(hours=hh, minutes=mm), name))
starts.sort()
trades = []
for k, (t0, name) in enumerate(starts):
    t_next = starts[k + 1][0] if k + 1 < len(starts) else t0 + pd.Timedelta(hours=8)
    orb = d.loc[t0: t0 + pd.Timedelta(minutes=OR_MIN - 1)]
    if len(orb) < OR_MIN:
        continue                                                       # gap in the opening range: skip
    hi, lo = orb.h.max(), orb.l.min()
    mid = (hi + lo) / 2
    if (hi - lo) / mid < MIN_W:
        continue
    after = d.loc[t0 + pd.Timedelta(minutes=OR_MIN): t_next - pd.Timedelta(minutes=1)]
    win_end = t0 + pd.Timedelta(hours=WINDOW_H)
    c5 = after.c.resample("5min").last().dropna()
    c5 = c5[c5.index + pd.Timedelta(minutes=4) < win_end]
    brk = c5[(c5 > hi) | (c5 < lo)]
    if brk.empty:
        continue
    bt = brk.index[0] + pd.Timedelta(minutes=5)                        # break known at the 5m bar close
    side = 1 if brk.iloc[0] > hi else -1
    lvl = hi if side == 1 else lo
    stop = mid
    risk = abs(lvl - stop)
    tgt = lvl + side * 2 * risk
    seg = after.loc[bt:]
    entry_t = None
    for t, b in seg.loc[:win_end].iterrows():
        if (side == 1 and b.l <= mid) or (side == -1 and b.h >= mid):
            break                                                      # midpoint touched before the fill: cancel
        if (side == 1 and b.l <= lvl - TICK) or (side == -1 and b.h >= lvl + TICK):
            entry_t = t
            break
    if entry_t is None:
        continue
    exit_px, why, exit_t = None, None, None
    for t, b in seg.loc[entry_t:].iterrows():
        if t == entry_t:
            # on the fill bar only the stop can be judged (we don't know the order of moves inside it)
            if (side == 1 and b.l <= stop) or (side == -1 and b.h >= stop):
                exit_px, why, exit_t = stop, "stop", t
                break
            continue
        hit_s = (b.l <= stop) if side == 1 else (b.h >= stop)
        hit_t = (b.h >= tgt) if side == 1 else (b.l <= tgt)
        if hit_s:
            exit_px, why, exit_t = stop, "stop", t
            break
        if hit_t:
            exit_px, why, exit_t = tgt, "target", t
            break
    if exit_px is None:
        exit_px, why, exit_t = seg.c.iloc[-1], "time", seg.index[-1]
    gross = side * (exit_px - lvl) / lvl
    cost = FEE_IN + FEE_OUT + (SLIP if why == "stop" else 0)
    net = gross - cost
    trades.append({"session_start": t0, "session": name, "side": side, "entry_t": entry_t, "entry": lvl,
                   "stop": stop, "target": tgt, "exit_t": exit_t, "exit": exit_px, "why": why,
                   "or_width_pct": (hi - lo) / mid * 100, "net_pct": net * 100, "R": net / (risk / lvl),
                   "gate": bool(gate.get(t0.normalize(), False))})

T = pd.DataFrame(trades)
T.to_csv(r"C:\Users\thoma\catalyst-research\research\btc_ib\trades.csv", index=False)


def summ(x, label):
    if x.empty:
        return f"| {label} | 0 | | | | | | |"
    days = max((x.session_start.max() - x.session_start.min()).days, 1)
    w, l = x.R[x.R > 0].sum(), -x.R[x.R <= 0].sum()
    eq = x.R.cumsum()
    dd = (eq - eq.cummax()).min()
    trim = x[x.R < x.R.quantile(0.95)]
    return (f"| {label} | {len(x)} | {len(x)/days:.2f} | {(x.R > 0).mean()*100:.0f}% | {x.R.mean():+.3f} | "
            f"{(w / l if l else float('inf')):.2f} | {x.net_pct.mean():+.3f}% | {dd:.1f} | {trim.R.mean():+.3f} |")


out = ["# Results: BTC session range-break retest (PREREG frozen)", "",
       "| set | trades | per day | win | avg R (net) | PF | avg net % | max DD (R) | avg R minus top 5% |",
       "|---|---|---|---|---|---|---|---|---|"]
for var, X in (("A all days", T), ("B gated", T[T.gate])):
    IS, OOS = X[X.session_start < "2025-01-01"], X[X.session_start >= "2025-01-01"]
    o25, o26 = OOS[OOS.session_start < "2026-01-01"], OOS[OOS.session_start >= "2026-01-01"]
    out += [summ(X, f"**{var}** ALL"), summ(IS, f"{var} IS 2022-24"), summ(OOS, f"{var} OOS 2025-26"),
            summ(o25, f"{var} OOS 2025"), summ(o26, f"{var} OOS 2026H1")]
    for s in SESSIONS:
        out.append(summ(OOS[OOS.session == s], f"{var} OOS {s}"))
    w, l = OOS.R[OOS.R > 0].sum(), -OOS.R[OOS.R <= 0].sum()
    ok = (l and w / l >= 1.2) and len(OOS) >= 150 and o25.R.mean() > 0 and o26.R.mean() > 0 and IS.R.mean() > 0
    out.append(f"| **{var} verdict** | {'PASS' if ok else 'FAIL'} | | | | | | | |")
out += ["", "Exit reasons (all): " + ", ".join(f"{k} {v}" for k, v in T.why.value_counts().items())]
open(r"C:\Users\thoma\catalyst-research\research\btc_ib\RESULTS.md", "w", encoding="utf-8").write("\n".join(out) + "\n")
sys.stdout.reconfigure(encoding="utf-8")
print("\n".join(out))
