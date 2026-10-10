"""D2: is there money in the domino? Rules are in PREREG_D2.md (committed before this ran). Usage: python d2.py

For every day a $20M+/day stock closes up 20%+ (variants: +10%, -20%, -10%), buy its quiet, much smaller same-industry
stocks at the next open, sell at the close 5 days later, and compare with matched quiet stocks from industries with no
big mover that day.
"""
import json, os
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RW = os.path.join(HERE, "..", "runners", "work")
rng = np.random.default_rng(20261010)
FLOOR, MULT, HOLD, NBOOT, BLOCK = 20e6, 10.0, 5, 2000, 5
DRUG = {"2833", "2834", "2835", "2836", "8731"}
VARIANTS = {"up20": 0.20, "up10": 0.10, "dn20": -0.20, "dn10": -0.10}

z = np.load(os.path.join(RW, "panel.npz"), allow_pickle=True)
tick = [str(t) for t in z["tick"]]; dates = [str(d) for d in z["dates"]]
T, N = len(dates), len(tick)
valid, o, c, craw = z["valid"], z["o"], z["c"], z["craw"]
ev = z["evmask"].astype(bool)
with np.errstate(divide="ignore", invalid="ignore"):
    ret = np.where(valid & (z["c_prev"] > 0), c / z["c_prev"] - 1.0, np.nan)
    fac = np.where(craw > 0, c / craw, np.nan)
size = pd.DataFrame(craw * z["vraw"]).rolling(20, min_periods=15).median().shift(6).to_numpy()
m = pd.read_csv(os.path.join(HERE, "sic_map.csv"), dtype=str).fillna("").set_index("ticker")
sic = np.array([m.sic.get(t, "") for t in tick]); hq = np.array([m.hq.get(t, "") for t in tick])
has_sic = sic != ""; is_drug = np.isin(sic, list(DRUG)); is_china = np.isin(hq, ["F4", "K3"])
members = {k: np.flatnonzero(sic == k) for k in set(sic[has_sic])}

# trade return for entering at the open of d+1 and leaving at the close of d+5 (or the last close before it)
R = np.full((T, N), np.nan); split_drop = 0
for d in range(T - HOLD):
    entry = o[d + 1]; ok = valid[d + 1] & np.isfinite(entry) & (entry > 0)
    exitp = np.full(N, np.nan); exitf = np.full(N, np.nan)
    for k in range(HOLD, 0, -1):
        take = np.isnan(exitp) & valid[d + k] & np.isfinite(c[d + k]) & (c[d + k] > 0)
        exitp[take] = c[d + k][take]; exitf[take] = fac[d + k][take]
    with np.errstate(divide="ignore", invalid="ignore"):
        r = exitp / entry - 1.0
        split = np.abs(exitf / fac[d + 1] - 1.0) > 0.01
    split_drop += int((ok & np.isfinite(r) & split).sum())
    R[d] = np.where(ok & ~split, r, np.nan)

quiet = np.zeros((T, N), bool)
for d in range(2, T - HOLD):
    quiet[d] = (valid[d] & np.isfinite(ret[d]) & (ret[d] < 0.10) & ~ev[d] & ~ev[d - 1] & ~ev[d - 2]
                & np.isfinite(size[d]) & (size[d] > 0) & has_sic & np.isfinite(R[d]))
takeable = (craw >= 1.0) & (size >= 250_000)


def run(thr):
    rows = []; leader_days = 0; no_ctrl = 0; per_leader = []
    for d in range(26, T - HOLD):
        big = valid[d] & np.isfinite(size[d]) & (size[d] >= FLOOR) & np.isfinite(ret[d]) & has_sic
        lead = np.flatnonzero(big & ((ret[d] >= thr) if thr > 0 else (ret[d] <= thr)))
        if not len(lead): continue
        hot = set(sic[big & (np.abs(ret[d]) >= 0.10)])
        fol = set()
        for y in lead:
            g = members[sic[y]]
            f = g[(g != y) & quiet[d, g] & (size[d, g] <= size[d, y] / MULT)]
            per_leader.append(len(f)); fol.update(f.tolist())
        leader_days += 1
        if not fol: continue
        pool = np.flatnonzero(quiet[d] & ~np.isin(sic, list(hot)))
        psize = size[d, pool]
        for s in fol:
            cand = pool[(psize >= 0.5 * size[d, s]) & (psize <= 2.0 * size[d, s])]
            if len(cand) < 3:
                no_ctrl += 1; continue
            pick = rng.choice(cand, size=min(10, len(cand)), replace=False)
            rows.append((d, s, R[d, s], float(np.mean(R[d, pick])), bool(takeable[d, s]), bool(is_drug[s]), bool(is_china[s])))
    t = pd.DataFrame(rows, columns=["d", "s", "r", "ctrl", "takeable", "drug", "china"]); t["ex"] = t.r - t.ctrl
    return t, dict(leader_days=leader_days, followers_per_leader_median=float(np.median(per_leader)) if per_leader else 0, no_controls=no_ctrl)


def block_ci(series):
    """series: per-trading-day values (NaN when no basket). 95% interval of the mean by 5-day block bootstrap."""
    nb = int(np.ceil(T / BLOCK)); out = []
    for _ in range(NBOOT):
        starts = rng.integers(0, T - BLOCK + 1, nb)
        idx = (starts[:, None] + np.arange(BLOCK)).ravel()[:T]
        v = series[idx]
        out.append(np.nanmean(v) if np.isfinite(v).any() else np.nan)
    return [float(x) for x in np.nanpercentile(out, [2.5, 97.5])]


def summary(t):
    if len(t) < 30:
        return dict(n=int(len(t)), note="fewer than 30 trades: too few to judge")
    day_ex = np.full(T, np.nan); day_r = np.full(T, np.nan)
    g = t.groupby("d"); day_ex[g.ex.mean().index] = g.ex.mean().values; day_r[g.r.mean().index] = g.r.mean().values
    lo, hi = block_ci(day_ex)
    q1, q99 = t.r.quantile([0.01, 0.99])
    return dict(n=int(len(t)), days=int(g.ngroups), per_day_median=float(g.size().median()),
                excess=float(np.nanmean(day_ex)), ex_lo=lo, ex_hi=hi, basket=float(np.nanmean(day_r)), ctrl=float(g.ctrl.mean().mean()),
                net1=float(np.nanmean(day_r) - 0.01), net35=float(np.nanmean(day_r) - 0.035),
                median=float(t.r.median()), pos=float((t.r > 0).mean()), big_win=float((t.r >= 0.5).mean()), big_loss=float((t.r <= -0.3).mean()),
                trimmed=float(t.r[(t.r > q1) & (t.r < q99)].mean()), best=float(t.r.max()), worst=float(t.r.min()))


if __name__ == "__main__":
    print(f"panel {T} days x {N} stocks | trades dropped for a split inside the window: {split_drop} | China/HK HQ stocks: {int(is_china.sum())}")
    out = {}
    for name, thr in VARIANTS.items():
        t, info = run(thr)
        cuts = {"takeable": t[t.takeable], "all": t, "takeable_nodrug": t[t.takeable & ~t.drug], "china_hk": t[t.china], "china_hk_takeable": t[t.china & t.takeable]}
        out[name] = dict(info=info, **{k: summary(v) for k, v in cuts.items()})
        print(f"\n=== leader {name} === {info['leader_days']} days with a leader move | median followers per leader {info['followers_per_leader_median']:.0f} | followers without 3 controls: {info['no_controls']}")
        for k, s in out[name].items():
            if k == "info": continue
            if "note" in s:
                print(f"  {k:18s} n={s['n']} ({s['note']})"); continue
            print(f"  {k:18s} n={s['n']:5d} days={s['days']:3d} | excess vs controls {s['excess']:+.2%} [{s['ex_lo']:+.2%}, {s['ex_hi']:+.2%}] | basket {s['basket']:+.2%} (controls {s['ctrl']:+.2%}) "
                  f"net1% {s['net1']:+.2%} net3.5% {s['net35']:+.2%} | median {s['median']:+.2%} pos {s['pos']:.0%} >=+50% {s['big_win']:.1%} <=-30% {s['big_loss']:.1%} trimmed {s['trimmed']:+.2%} best {s['best']:+.0%} worst {s['worst']:+.0%}")
    json.dump(out, open(os.path.join(HERE, "d2_results.json"), "w"), indent=1)
