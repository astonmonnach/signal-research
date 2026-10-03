"""Independent rebuild of PREREG.md V1/V2 from audit_hl_btc_funding.csv (re-pulled by pull_funding.py).

Conventions chosen by the auditor (written from the spec only):
- Each funding print is one actual payment to the short: +rate * N (rate>0 => longs pay shorts).
  The first 82 prints (2023-05-12 -> 2023-06-08) are 8-hourly prints carrying an 8h rate; they are
  still one payment each, so summing prints is correct; annualisation uses calendar time, not print count.
- Position decided at print t-1 earns the payment printed at t (interval (t-1, t]).
- Cost 0.31% of N per round trip = 0.155% charged on entry and 0.155% on exit.
- Annualised = simple (non-compounded) sum of net carry / elapsed years. On capital = / 1.333.
"""
import numpy as np, pandas as pd, json, sys

COST_SIDE = 0.0031 / 2
CAP = 1 + 1 / 3
IS_END = pd.Timestamp("2025-01-01", tz="UTC")
END = pd.Timestamp("2026-10-03 11:00", tz="UTC")

d = pd.read_csv("audit_hl_btc_funding.csv")
d["ts"] = pd.to_datetime(d.time, unit="ms", utc=True).dt.floor("h")
d = d[["ts", "fundingRate"]].reset_index(drop=True)
r = d.fundingRate.values
n = len(d)

# trailing 24h mean known at each print (inclusive of that print), time-based window
s = d.set_index("ts").fundingRate
trail = s.rolling("24h").mean().values


def run(pos):
    """pos[t] = position held during interval ending at print t (0/1). Returns per-print net P&L (frac of N)."""
    gross = pos * r
    cost = np.zeros(n)
    prev = 0
    for t in range(n):
        if pos[t] != prev:
            cost[t] += COST_SIDE  # entry or exit, charged at the print where interval starts being (un)held
        prev = pos[t]
    if prev == 1:
        cost[-1] += COST_SIDE  # close at end
    switches = int(np.sum(np.abs(np.diff(np.concatenate([[0], pos, [0]])))))
    return gross, cost, switches


# V1: enter at first print (t=0), earn from print 1 onwards
pos1 = np.ones(n); pos1[0] = 0
# V2: pos for interval ending at t decided at t-1 using trailing mean at t-1
pos2 = np.zeros(n); pos2[1:] = (trail[:-1] > 0).astype(float)


def yrs(a, b):
    return (b - a).total_seconds() / (365.25 * 86400)


def summarise(name, pos):
    gross, cost, sw = run(pos)
    net = gross - cost
    df = pd.DataFrame({"ts": d.ts, "gross": gross, "cost": cost, "net": net, "pos": pos})
    out = {"variant": name, "switches": sw, "round_trips": sw / 2, "time_in_market": float(pos.mean())}
    start = d.ts.iloc[0]
    periods = {"IS": (start, IS_END), "OOS": (IS_END, END + pd.Timedelta(hours=1)), "ALL": (start, END + pd.Timedelta(hours=1))}
    for k, (a, b) in periods.items():
        m = (df.ts >= a) & (df.ts < b)
        y = yrs(a, min(b, END))
        out[k] = {"years": round(y, 3), "gross_sum_N": df.gross[m].sum(), "cost_sum_N": df.cost[m].sum(),
                  "net_sum_N": df.net[m].sum(), "ann_net_N": df.net[m].sum() / y, "ann_net_cap": df.net[m].sum() / y / CAP,
                  "ann_gross_N": df.gross[m].sum() / y}
    by = {}
    for yr, g in df.groupby(df.ts.dt.year):
        a = max(start, pd.Timestamp(f"{yr}-01-01", tz="UTC")); b = min(END, pd.Timestamp(f"{yr+1}-01-01", tz="UTC"))
        y = yrs(a, b)
        by[int(yr)] = {"years": round(y, 3), "net_sum_N": g.net.sum(), "ann_net_N": g.net.sum() / y, "ann_net_cap": g.net.sum() / y / CAP,
                       "full_year": y > 0.99}
    out["by_year"] = by
    mon = df.groupby(df.ts.dt.strftime("%Y-%m")).net.sum()
    out["months"] = len(mon); out["pct_months_pos"] = float((mon > 0).mean())
    out["worst_month_N"] = float(mon.min()); out["worst_month"] = mon.idxmin()
    cum = df.net.cumsum(); dd = cum - cum.cummax()
    out["max_dd_N"] = float(dd.min()); out["max_dd_end"] = str(df.ts[dd.idxmin()])
    pk = cum[: dd.idxmin() + 1].idxmax(); out["max_dd_start"] = str(df.ts[pk])
    full_years_ok = all(v["net_sum_N"] > 0 for v in by.values() if v["full_year"])
    out["PASS"] = bool(out["OOS"]["ann_net_cap"] > 0 and full_years_ok)
    return out, df


res = {}
for name, pos in [("V1_always_on", pos1), ("V2_gated", pos2)]:
    o, df = summarise(name, pos)
    res[name] = o
    df.to_csv(f"audit_{name}_hourly.csv", index=False)

# sensitivity: V1 excluding 8h-era prints (start 2023-06-08 01:00)
m = d.ts >= pd.Timestamp("2023-06-08 01:00", tz="UTC")
res["sens_8h_era_sum"] = float(r[~m.values][1:].sum())
res["n_prints"] = n; res["first"] = str(d.ts.iloc[0]); res["last"] = str(d.ts.iloc[-1])
res["n_8h_prints"] = int((d.ts < pd.Timestamp("2023-06-08 01:00", tz="UTC")).sum())
res["mean_rate_ann_hourly_era"] = float(r[m.values].mean() * 24 * 365.25)
res["frac_positive"] = float((r > 0).mean())
res["frac_at_base_0.00125pct"] = float((np.abs(r - 0.0000125) < 1e-9).mean())
json.dump(res, open("audit_results.json", "w"), indent=1, default=str)
print(json.dumps(res, indent=1, default=str))
