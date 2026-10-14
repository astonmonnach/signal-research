"""FP1: footprint signs at one close, held to the next close. Rules: research/movers/PREREG_FP1.md (committed 4ffd46e before this ran).
Usage: python run.py   -> prints the tables and writes results.json and trades_T1.csv / T2 / T3."""
import json, os
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
z = np.load(os.path.join(HERE, "..", "..", "runners", "work", "panel.npz"), allow_pickle=True)
c, o, h, cp, craw, vraw = z["c"], z["o"], z["h"], z["c_prev"], z["craw"], z["vraw"]
crp, relvol, rs90, ret20, valid = z["craw_prev"], z["relvol"], z["rs90"], z["ret20"], z["valid"]
dates = [str(d) for d in z["dates"]]; tick = [str(t) for t in z["tick"]]; T, N = c.shape

dv = craw * vraw                                                     # raw dollar volume each day
med20 = pd.DataFrame(dv).shift(1).rolling(20, min_periods=15).median().values   # 20 sessions ending t-1
with np.errstate(invalid="ignore", divide="ignore"):
    r1 = c / cp - 1; on = o / cp - 1; best = h / cp - 1
ok = valid & np.isfinite(r1) & np.isfinite(crp) & (cp > 0)
take = ok & (crp >= 1) & (med20 >= 250e3)
sub3 = crp < 3
v5 = relvol >= 5
crash = ret20 <= -0.30
TR = {"T1": take & sub3 & rs90 & v5, "T2": take & sub3 & v5, "T3": take & sub3 & v5 & crash}
DESC = {"T1 no $1 floor": ok & sub3 & rs90 & v5, "T2 no $1 floor": ok & sub3 & v5, "T3 no $1 floor": ok & sub3 & v5 & crash}
comp = take & sub3                                                   # comparison pool: takeable under $3
rng = np.random.default_rng(20261014)
MONTHS = T / 21.0


def boot(mask, cost):
    d_idx, j_idx = np.nonzero(mask)
    x = r1[d_idx, j_idx] - cost
    days = np.unique(d_idx)
    s = np.array([x[d_idx == d].sum() for d in days]); n = np.array([(d_idx == d).sum() for d in days])
    draws = rng.integers(0, len(days), (2000, len(days)))
    m = s[draws].sum(1) / n[draws].sum(1)
    return float(x.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def stats(name, mask, write=None):
    d_idx, j_idx = np.nonzero(mask)
    if len(d_idx) == 0:
        return {"name": name, "n": 0}
    x = r1[d_idx, j_idx]
    out = {"name": name, "n": int(len(x)), "per_month": round(len(x) / MONTHS, 1), "days": int(len(np.unique(d_idx)))}
    for cost in (0.01, 0.02, 0.04):
        out[f"mean_{int(cost*100)}pct"] = float((x - cost).mean())
    mean2, lo2, hi2 = boot(mask, 0.02)
    out.update(mean2=mean2, lo2=lo2, hi2=hi2, median2=float(np.median(x - 0.02)), pos2=float(((x - 0.02) > 0).mean()),
               up20=float((x >= 0.20).mean()), down20=float((x <= -0.20).mean()),
               overnight_mean=float(np.nanmean(on[d_idx, j_idx])), best_case_median=float(np.nanmedian(best[d_idx, j_idx])),
               best_case_mean=float(np.nanmean(best[d_idx, j_idx])))
    half = d_idx < 250
    out["mean2_half1"] = float((x[half] - 0.02).mean()) if half.any() else None
    out["mean2_half2"] = float((x[~half] - 0.02).mean()) if (~half).any() else None
    # same-day comparison: mean 1-day return of the takeable under-$3 pool on the signal days
    cm = [np.nanmean(r1[d][comp[d] & ~mask[d]]) for d in np.unique(d_idx)]
    out["comparison_same_days_mean_gross"] = float(np.nanmean(cm))
    out["mean_gross"] = float(x.mean())
    # self-consistency
    y = x - 0.02; w = y > 0
    out["selfcheck"] = float(w.mean() * (y[w].mean() if w.any() else 0) + (~w).mean() * (y[~w].mean() if (~w).any() else 0))
    if write:
        pd.DataFrame({"date": [dates[d] for d in d_idx], "ticker": [tick[j] for j in j_idx], "prior_close_raw": crp[d_idx, j_idx],
                      "relvol_prev": relvol[d_idx, j_idx], "rs90": rs90[d_idx, j_idx], "ret20_prev": ret20[d_idx, j_idx],
                      "ret_1d": x, "overnight": on[d_idx, j_idx], "best_case_high": best[d_idx, j_idx]}).to_csv(os.path.join(HERE, write), index=False)
    return out


res = {"tests": [stats(k, m, f"trades_{k}.csv") for k, m in TR.items()], "description": [stats(k, m) for k, m in DESC.items()],
       "pool": stats("all takeable under $3 (comparison pool)", comp)}
for r in res["tests"] + res["description"] + [res["pool"]]:
    if r["n"] == 0:
        print(f"{r['name']}: no trades"); continue
    verdict = ""
    if r["name"] in TR:
        p = r["lo2"] > 0 and r["mean2"] > 0 and (r["mean2_half1"] or 0) > 0 and (r["mean2_half2"] or 0) > 0
        verdict = "PAYS" if p else "FAILS"; r["verdict"] = verdict
    print(f"{r['name']:38s} n {r['n']:6d} ({r['per_month']}/mo, {r['days']} days) | after 2%: mean {r['mean2']:+.2%} [{r['lo2']:+.2%}, {r['hi2']:+.2%}] "
          f"median {r['median2']:+.2%} pos {r['pos2']:.0%} | gross {r['mean_gross']:+.2%} (1%: {r['mean_1pct']:+.2%}, 4%: {r['mean_4pct']:+.2%}) | "
          f"up20 {r['up20']:.1%} down20 {r['down20']:.1%} | overnight {r['overnight_mean']:+.2%} | best-case high median {r['best_case_median']:+.1%} | "
          f"halves {r['mean2_half1'] if r['mean2_half1'] is None else round(r['mean2_half1']*100,2)}% / {r['mean2_half2'] if r['mean2_half2'] is None else round(r['mean2_half2']*100,2)}% | "
          f"same-day pool {r['comparison_same_days_mean_gross']:+.2%} | selfcheck {r['selfcheck']:+.4%} vs {r['mean2']:+.4%} {verdict}")
json.dump(res, open(os.path.join(HERE, "results.json"), "w"), indent=1)
