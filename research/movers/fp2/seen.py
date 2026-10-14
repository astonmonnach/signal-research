"""FP2 already-seen numbers: close-to-next-open on the two-year panel (never a pass; see PREREG_FP2.md)."""
import json, os
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
z = np.load(os.path.join(HERE, "..", "..", "runners", "work", "panel.npz"), allow_pickle=True)
o, cp, craw, vraw = z["o"], z["c_prev"], z["craw"], z["vraw"]
crp, relvol, rs90, valid = z["craw_prev"], z["relvol"], z["rs90"], z["valid"]
T = o.shape[0]
med20 = pd.DataFrame(craw * vraw).shift(1).rolling(20, min_periods=15).median().values
with np.errstate(invalid="ignore", divide="ignore"):
    on = o / cp - 1
ok = valid & np.isfinite(on) & np.isfinite(crp) & (cp > 0) & (crp >= 1) & (crp < 3) & (med20 >= 250e3) & (relvol >= 5)
S = {"S1": ok & rs90, "S2": ok}
rng = np.random.default_rng(20261014); out = {}
for k, m in S.items():
    d, j = np.nonzero(m); x = on[d, j]
    days = np.unique(d); s = np.array([x[d == q].sum() for q in days]); n = np.array([(d == q).sum() for q in days])
    dr = rng.integers(0, len(days), (2000, len(days)))
    bm = s[dr].sum(1) / n[dr].sum(1) - 0.02
    h1 = d < 250
    r = dict(n=int(len(x)), gross=float(x.mean()), net2=float(x.mean() - 0.02), lo=float(np.percentile(bm, 2.5)), hi=float(np.percentile(bm, 97.5)),
             net1=float(x.mean() - 0.01), net4=float(x.mean() - 0.04), median_net2=float(np.median(x - 0.02)), pos_net2=float((x - 0.02 > 0).mean()),
             half1=float(x[h1].mean() - 0.02), half2=float(x[~h1].mean() - 0.02), gap_up_10=float((x >= 0.10).mean()), gap_down_10=float((x <= -0.10).mean()))
    out[k] = r
    print(f"{k}: n {r['n']} | gross {r['gross']:+.2%} | after 2% {r['net2']:+.2%} [{r['lo']:+.2%}, {r['hi']:+.2%}] | 1% {r['net1']:+.2%} 4% {r['net4']:+.2%} | median {r['median_net2']:+.2%} pos {r['pos_net2']:.0%} | halves {r['half1']:+.2%} / {r['half2']:+.2%} | gap >=+10% {r['gap_up_10']:.1%} <=-10% {r['gap_down_10']:.1%}")
json.dump(out, open(os.path.join(HERE, "seen_results.json"), "w"), indent=1)
