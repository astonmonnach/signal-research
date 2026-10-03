"""Basis, squeeze/liquidation and book-depth analysis for the HL carry audit."""
import json, numpy as np, pandas as pd

out = {}
# ---------------- basis: spot UBTC/USDC (@142) vs BTC perp ----------------
for iv in ["15m", "1h", "1d"]:
    p = pd.read_csv(f"hl_perp_{iv}.csv", parse_dates=["ts"]); s = pd.read_csv(f"hl_spot_{iv}.csv", parse_dates=["ts"])
    m = p.merge(s, on="ts", suffixes=("_p", "_s"))
    m = m[m.v_s > 0]  # only spot candles that actually traded
    sp = m.c_s / m.c_p - 1
    q = sp.quantile([0.01, 0.05, 0.5, 0.95, 0.99])
    d1 = sp.diff()
    out[f"basis_{iv}"] = {"n": int(len(m)), "from": str(m.ts.min()), "to": str(m.ts.max()),
        "mean_bp": sp.mean() * 1e4, "std_bp": sp.std() * 1e4, "p01_bp": q[0.01] * 1e4, "p05_bp": q[0.05] * 1e4, "median_bp": q[0.5] * 1e4,
        "p95_bp": q[0.95] * 1e4, "p99_bp": q[0.99] * 1e4, "min_bp": sp.min() * 1e4, "min_at": str(m.ts[sp.idxmin()]),
        "max_bp": sp.max() * 1e4, "max_at": str(m.ts[sp.idxmax()]),
        "abs_change_1bar_p99_bp": d1.abs().quantile(0.99) * 1e4, "worst_change_1bar_bp": d1.min() * 1e4}
    # worst basis move against a long-spot/short-perp entered at any bar and exited k bars later
    for k, lab in {"1h": [(24, "24h"), (24 * 7, "7d")], "1d": [(7, "7d"), (30, "30d")], "15m": [(96, "24h")]}[iv]:
        ch = sp.shift(-k) - sp
        out[f"basis_{iv}"][f"spread_change_{lab}_p01_bp"] = ch.quantile(0.01) * 1e4
        out[f"basis_{iv}"][f"spread_change_{lab}_min_bp"] = ch.min() * 1e4
    # also intrabar extreme divergence using highs/lows (spot high vs perp low etc)
    out[f"basis_{iv}"]["intrabar_max_spot_over_perp_bp"] = ((m.h_s / m.l_p) - 1).max() * 1e4
    out[f"basis_{iv}"]["intrabar_max_perp_over_spot_bp"] = ((m.h_p / m.l_s) - 1).max() * 1e4

# ---------------- squeeze / liquidation ----------------
b = pd.read_csv("binance_btcusdt_perp_1h.csv", parse_dates=["ts"]).sort_values("ts").reset_index(drop=True)
c, h = b.c.values, b.h.values
MM = 0.0125  # HL BTC base-tier maintenance margin = half of initial margin at 40x max leverage
sq = {}
for W in [1, 4, 24, 72, 168, 720, 2160]:
    # entry at close of bar i, worst high over bars i+1..i+W
    hh = pd.Series(h[::-1]).rolling(W, min_periods=1).max().values[::-1]  # max h over i..i+W-1
    fut = np.append(hh[1:], np.nan)  # max over i+1..i+W
    rise = fut / c - 1
    i = int(np.nanargmax(rise))
    x = rise[i]
    sq[f"{W}h"] = {"max_rise_pct": x * 100, "entry_ts": str(b.ts[i]), "entry_px": c[i],
                   "max_leverage_survive": 1 / (x * (1 + MM) + MM),
                   "n_hours_where_3x_liq": int(np.nansum(rise > (1 / 3 - MM) / (1 + MM)))}
out["squeeze"] = sq
out["liq_threshold_rise_pct"] = {L: ((1 / L - MM) / (1 + MM)) * 100 for L in [1, 1.5, 2, 3, 5]}
# never rebalanced: rise from first entry to the maximum high after
e0 = b[b.ts >= "2023-05-12"].index[0]
out["since_entry_2023-05-12"] = {"entry_px": c[e0], "max_high_after": float(h[e0 + 1:].max()), "rise_pct": (h[e0 + 1:].max() / c[e0] - 1) * 100,
                                  "first_3x_liq_ts": str(b.ts[e0 + 1 + int(np.argmax(h[e0 + 1:] / c[e0] - 1 > (1 / 3 - MM) / (1 + MM)))])}


# simulate a 3x short that tops up / rebalances every k days back to 3x: count liquidations
def sim(L, k_hours):
    liqs, i = 0, e0
    thr = (1 / L - MM) / (1 + MM)
    while i < len(c) - 1:
        j = min(i + k_hours, len(c) - 1)
        seg = h[i + 1 : j + 1] / c[i] - 1
        if (seg > thr).any():
            liqs += 1; i = i + 1 + int(np.argmax(seg > thr))
        else:
            i = j
    return liqs
out["liquidations_if_rebalanced_every"] = {f"{L}x_every_{k//24}d": sim(L, k) for L in [2, 3, 5] for k in [24, 24 * 7, 24 * 30]}

# ---------------- order books ----------------
snaps = json.load(open("l2_snapshots.json"))


def analyse(book):
    bids = [(float(l["px"]), float(l["sz"])) for l in book["levels"][0]]
    asks = [(float(l["px"]), float(l["sz"])) for l in book["levels"][1]]
    mid = (bids[0][0] + asks[0][0]) / 2
    r = {"mid": mid, "spread_bp": (asks[0][0] - bids[0][0]) / mid * 1e4, "levels": (len(bids), len(asks)),
         "ask_reach_bp": (asks[-1][0] / mid - 1) * 1e4, "bid_reach_bp": (1 - bids[-1][0] / mid) * 1e4}
    for pct in [0.001, 0.005]:
        r[f"bid_usd_{pct*100:g}pct"] = sum(p * s for p, s in bids if p >= mid * (1 - pct))
        r[f"ask_usd_{pct*100:g}pct"] = sum(p * s for p, s in asks if p <= mid * (1 + pct))
    for usd in [1e3, 1e4, 1e5]:
        for side, lv, sgn in [("buy", asks, 1), ("sell", bids, -1)]:
            rem, cost, qty = usd, 0.0, 0.0
            for p, s in lv:
                take = min(rem, p * s); cost += take; qty += take / p; rem -= take
                if rem <= 1e-9: break
            r[f"{side}_{int(usd)}_slip_bp"] = (sgn * ((cost / qty) / mid - 1) * 1e4) if rem <= 1e-9 else None
    return r


bk = {}
for coin in ["BTC", "@142"]:
    for var in ["", "_agg4", "_agg3"]:
        rows = [analyse(sn[coin + var]) for sn in snaps]
        df = pd.DataFrame(rows)
        bk[coin + var] = {"n_snaps": len(rows), "first_snap": snaps[0]["t"], "last_snap": snaps[-1]["t"],
                          "median": df.drop(columns=["levels"]).median(numeric_only=True).to_dict(),
                          "worst": {k: (df[k].max() if ("slip" in k or "spread" in k) else df[k].min()) for k in df.columns if k not in ("levels",) and df[k].notna().all()},
                          "levels": rows[0]["levels"], "null_slips": {k: int(df[k].isna().sum()) for k in df.columns if "slip" in k}}
out["books"] = bk
json.dump(out, open("audit_risk_results.json", "w"), indent=1, default=float)
print(json.dumps(out, indent=1, default=float))
