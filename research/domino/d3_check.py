"""D3 validity check: is the kept-industry result a domino, or just two good years for those sectors?

A. Own-stock baseline: the same stocks' 5- and 10-day returns on every quiet day when they were NOT a follower.
B. Same-day, same-favoured-sector controls: quiet, takeable, holds-up stocks in OTHER kept industries with no big mover that day.
"""
import contextlib, importlib.util, io, os
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
with contextlib.redirect_stdout(io.StringIO()):
    spec = importlib.util.spec_from_file_location("d3", os.path.join(HERE, "d3.py")); d3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(d3)
d2, M, t = d3.d2, d3.M, d3.t
T, N = d2.T, d2.N; rng = np.random.default_rng(7)
keep_stock = np.isin(d2.sic, list(d3.group_of))
ok_stock_day = d2.quiet & d2.takeable & ~d3.rs90 & keep_stock[None, :] & ~d2.is_china[None, :] & np.isfinite(M["c1"])
s3 = t[(t.bucket == "keep") & t.takeable & ~t.china & ~t.rs90].copy()
is_fol = np.zeros((T, N), bool); is_fol[s3.d.to_numpy(), s3.s.to_numpy()] = True

def block_ci(day):
    bs = []
    for _ in range(2000):
        st = rng.integers(0, T - 4, 101); v = day[(st[:, None] + np.arange(5)).ravel()[:T]]; bs.append(np.nanmean(v))
    return np.percentile(bs, [2.5, 97.5])

print(f"stage 3: {len(s3)} trades, {s3.s.nunique()} stocks")
# A. own-stock baseline
for col in ("c5", "c10"):
    base = np.where(ok_stock_day & ~is_fol, M[col], np.nan)
    with np.errstate(all="ignore"): own = np.nanmean(base, axis=0)          # per stock, all its non-follower quiet days
    ex = s3[col].to_numpy() - own[s3.s.to_numpy()]
    day = np.full(T, np.nan); g = pd.Series(ex).groupby(s3.d.to_numpy()).mean(); day[g.index] = g.values
    lo, hi = block_ci(day)
    print(f"A. {col}: follower days {s3[col].mean():+.2%} vs the same stocks on ordinary quiet days {np.nanmean(own[s3.s.to_numpy()]):+.2%} | basket excess {np.nanmean(day):+.2%} [{lo:+.2%}, {hi:+.2%}]")
# universe drift for context
for col in ("c5", "c10"):
    print(f"   all kept-industry, takeable, holds-up, quiet stock-days: {np.nanmean(np.where(ok_stock_day, M[col], np.nan)):+.2%} ({col}); every quiet takeable stock-day in every industry: {np.nanmean(np.where(d2.quiet & d2.takeable, M[col], np.nan)):+.2%}")
# B. same-day controls from other kept industries with no big mover
rows = []
for d, grp in s3.groupby("d"):
    big = d2.valid[d] & np.isfinite(d2.size[d]) & (d2.size[d] >= d2.FLOOR) & np.isfinite(d2.ret[d]) & d2.has_sic
    hot = set(d2.sic[big & (np.abs(d2.ret[d]) >= 0.10)])
    pool = np.flatnonzero(ok_stock_day[d] & ~np.isin(d2.sic, list(hot)) & ~is_fol[d]); ps = d2.size[d, pool]
    for r in grp.itertuples():
        cand = pool[(ps >= 0.5 * d2.size[d, r.s]) & (ps <= 2.0 * d2.size[d, r.s])]
        if len(cand) < 3: continue
        pick = rng.choice(cand, size=min(10, len(cand)), replace=False)
        rows.append((d, r.c5 - np.nanmean(M["c5"][d, pick]), r.c10 - np.nanmean(M["c10"][d, pick])))
b = pd.DataFrame(rows, columns=["d", "ex5", "ex10"])
print(f"B. matched to other favoured-sector stocks the same day: {len(b)} of {len(s3)} trades had 3+ controls")
for col in ("ex5", "ex10"):
    day = np.full(T, np.nan); g = b.groupby("d")[col].mean(); day[g.index] = g.values; lo, hi = block_ci(day)
    print(f"   {col}: basket excess {np.nanmean(day):+.2%} [{lo:+.2%}, {hi:+.2%}]")
