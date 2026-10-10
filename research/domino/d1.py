"""D1: the reverse domino. Rules are in PREREG.md (committed before this ran). Usage: python d1.py

Backward look: runner days vs matched controls: did a bigger linked stock close up/down X% in the 5 days before?
Forward look : small stock-days with a leader: runner rate over the next 5 days, base vs "a leader moved X% today".
"""
import json, os
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RW = os.path.join(HERE, "..", "runners")
rng = np.random.default_rng(20261010)
THRS = [0.05, 0.10, 0.20]
DRUG = {"2833", "2834", "2835", "2836", "8731"}
MULT, FLOOR, LOOKBACK, FWD, NBOOT = 10.0, 20e6, 5, 5, 2000

z = np.load(os.path.join(RW, "work", "panel.npz"), allow_pickle=True)
tick = [str(t) for t in z["tick"]]; dates = [str(d) for d in z["dates"]]
T, N = len(dates), len(tick)
tix = {t: i for i, t in enumerate(tick)}; dix = {d: i for i, d in enumerate(dates)}
valid = z["valid"]
with np.errstate(divide="ignore", invalid="ignore"):
    ret = np.where(valid & (z["c_prev"] > 0), z["c"] / z["c_prev"] - 1.0, np.nan)
dv = pd.DataFrame(z["craw"] * z["vraw"])
size = dv.rolling(20, min_periods=15).median().shift(6).to_numpy()      # 20 days ending 6 days before the date
ev = z["evmask"].astype(bool)
# +300% in 5 trading days: adjusted AND raw close both >= 4x; first day of each episode, episodes >= 10 days apart
c, craw = z["c"], z["craw"]
with np.errstate(divide="ignore", invalid="ignore"):
    w = np.zeros((T, N), bool)
    w[5:] = (c[5:] / c[:-5] >= 4.0) & (craw[5:] / craw[:-5] >= 4.0) & valid[5:] & valid[:-5]
wk = np.zeros((T, N), bool)
for j in np.flatnonzero(w.any(0)):
    last = -99
    for t in np.flatnonzero(w[:, j]):
        if t - last >= 10: wk[t, j] = True
        last = t


def fut(mask):
    """fut[t] = any mask[t+1 .. t+FWD]"""
    out = np.zeros_like(mask)
    for k in range(1, FWD + 1):
        out[:-k] |= mask[k:]
    return out


fut_ev, fut_wk = fut(ev), fut(wk)
sic = pd.read_csv(os.path.join(HERE, "sic_map.csv"), dtype=str).set_index("ticker")["sic"].to_dict()
sic_arr = np.array([sic.get(t, "") for t in tick])


def groups(level, drop_drug):
    g = {}
    for i, s in enumerate(sic_arr):
        if not s or (drop_drug and s in DRUG): continue
        g.setdefault(s[:level], []).append(i)
    return {k: np.array(v) for k, v in g.items() if len(v) >= 2}


def backward(level, drop_drug):
    g = groups(level, drop_drug)
    member = {}
    for k, idx in g.items():
        for i in idx: member[i] = idx
    e = pd.read_csv(os.path.join(RW, "events.csv"), usecols=["ticker", "date"]); e["event"] = e.ticker + "|" + e.date; e["grp"] = "runner"
    cdf = pd.read_csv(os.path.join(RW, "controls.csv"), usecols=["event_ticker", "date", "ticker"]); cdf["event"] = cdf.event_ticker + "|" + cdf.date; cdf["grp"] = "control"
    rows = pd.concat([e[["event", "grp", "ticker", "date"]], cdf[["event", "grp", "ticker", "date"]]], ignore_index=True)
    out = []
    for r in rows.itertuples(index=False):
        i, t = tix.get(r.ticker), dix.get(r.date)
        rec = dict(event=r.event, grp=r.grp, ok=False, has=False)
        if i is not None and t is not None and i in member and t >= 26 and np.isfinite(size[t, i]) and size[t, i] > 0:
            idx = member[i]; idx = idx[idx != i]
            lead = idx[(size[t, idx] >= MULT * size[t, i]) & (size[t, idx] >= FLOOR)]
            rec["ok"] = True; rec["has"] = len(lead) > 0
            win = ret[t - LOOKBACK:t][:, lead] if len(lead) else np.empty((LOOKBACK, 0))
            for thr in THRS:
                rec[f"up{thr}"] = bool((win >= thr).any()); rec[f"dn{thr}"] = bool((win <= -thr).any())
        out.append(rec)
    d = pd.DataFrame(out).fillna(False)
    d = d[d.ok]
    res = {"n_runner": int((d.grp == "runner").sum()), "n_control": int((d.grp == "control").sum()),
           "has_leader_runner": float(d[d.grp == "runner"].has.mean()), "has_leader_control": float(d[d.grp == "control"].has.mean())}
    evs = d.event.unique(); eidx = {k: n for n, k in enumerate(evs)}; d["e"] = d.event.map(eidx)
    for col in [f"{a}{thr}" for a in ("up", "dn") for thr in THRS]:
        R, C = d[d.grp == "runner"], d[d.grp == "control"]
        rh = np.bincount(R.e, weights=R[col].astype(float), minlength=len(evs)); rn = np.bincount(R.e, minlength=len(evs)).astype(float)
        ch = np.bincount(C.e, weights=C[col].astype(float), minlength=len(evs)); cn = np.bincount(C.e, minlength=len(evs)).astype(float)
        pr, pc = rh.sum() / rn.sum(), ch.sum() / cn.sum()
        bs = []
        for _ in range(NBOOT):
            s = rng.integers(0, len(evs), len(evs))
            a, b = rh[s].sum() / max(rn[s].sum(), 1), ch[s].sum() / max(cn[s].sum(), 1)
            bs.append(a / b if b > 0 else np.nan)
        lo, hi = np.nanpercentile(bs, [2.5, 97.5])
        res[col] = dict(runner=float(pr), control=float(pc), lift=float(pr / pc) if pc > 0 else None, lo=float(lo), hi=float(hi))
    return res


def forward(level, drop_drug):
    g = groups(level, drop_drug)
    keys = [f"{a}{thr}" for a in ("up", "dn") for thr in THRS]
    base_n = np.zeros(T); base_e = np.zeros(T); base_w = np.zeros(T)
    cn = {k: np.zeros(T) for k in keys}; ce = {k: np.zeros(T) for k in keys}; cw = {k: np.zeros(T) for k in keys}
    for idx in g.values():
        S = size[:, idx]; R = ret[:, idx]; V = valid[:, idx]
        big = S >= FLOOR
        if not big.any(): continue
        flags = {f"up{thr}": (R >= thr) & big for thr in THRS}; flags.update({f"dn{thr}": (R <= -thr) & big for thr in THRS})
        FE, FW = fut_ev[:, idx], fut_wk[:, idx]
        for j in range(len(idx)):
            sj = S[:, j]
            okj = V[:, j] & np.isfinite(sj) & (sj > 0)
            if not okj.any(): continue
            lead = big & (S >= MULT * sj[:, None]); lead[:, j] = False
            has = lead.any(1) & okj; has[T - FWD:] = False
            if not has.any(): continue
            base_n += has; base_e += has & FE[:, j]; base_w += has & FW[:, j]
            for k in keys:
                mv = (lead & flags[k]).any(1) & has
                cn[k] += mv; ce[k] += mv & FE[:, j]; cw[k] += mv & FW[:, j]
    res = {"obs": float(base_n.sum()), "base_runner": float(base_e.sum() / base_n.sum()), "base_300": float(base_w.sum() / base_n.sum()),
           "runner_events_in_base": float(base_e.sum()), "w300_events_in_base": float(base_w.sum())}
    for k in keys:
        def lift(num_c, den_c, num_b, den_b):
            p, b = num_c.sum() / max(den_c.sum(), 1), num_b.sum() / den_b.sum()
            bs = []
            for _ in range(NBOOT):
                s = rng.integers(0, T, T)
                pp, bb = num_c[s].sum() / max(den_c[s].sum(), 1), num_b[s].sum() / max(den_b[s].sum(), 1)
                bs.append(pp / bb if bb > 0 else np.nan)
            lo, hi = np.nanpercentile(bs, [2.5, 97.5])
            return dict(cond=float(p), lift=float(p / b) if b > 0 else None, lo=float(lo), hi=float(hi), n=float(den_c.sum()), hits=float(num_c.sum()))
        res[k] = dict(runner=lift(ce[k], cn[k], base_e, base_n), w300=lift(cw[k], cn[k], base_w, base_n))
    return res


if __name__ == "__main__":
    print(f"panel {T} days x {N} stocks | with SIC {int((sic_arr != '').sum())} | runner flags {int(ev.sum())} | +300%/5d episodes {int(wk.sum())}")
    out = {}
    for drop in (False, True):
        for level in (4, 3, 2):
            tag = f"sic{level}" + ("_nodrug" if drop else "")
            out[tag] = {"backward": backward(level, drop), "forward": forward(level, drop)}
            b, f = out[tag]["backward"], out[tag]["forward"]
            print(f"\n=== {tag} === backward: {b['n_runner']} runner days, {b['n_control']} controls | has a leader: runners {b['has_leader_runner']:.1%}, controls {b['has_leader_control']:.1%}")
            for k in [f"{a}{thr}" for a in ("up", "dn") for thr in THRS]:
                x = b[k]; y = f[k]["runner"]; w3 = f[k]["w300"]
                print(f"  {k:7s} BACK runner {x['runner']:.1%} vs control {x['control']:.1%} lift {x['lift']:.2f} [{x['lo']:.2f}, {x['hi']:.2f}]"
                      f" | FWD base {f['base_runner']:.3%} cond {y['cond']:.3%} lift {y['lift']:.2f} [{y['lo']:.2f}, {y['hi']:.2f}] (n={y['n']:.0f}, hits={y['hits']:.0f})"
                      f" | +300% cond {w3['cond']:.4%} vs base {f['base_300']:.4%} hits={w3['hits']:.0f}")
    json.dump(out, open(os.path.join(HERE, "d1_results.json"), "w"), indent=1)
