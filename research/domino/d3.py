"""D3: the funnel. Rules and the industry list are in PREREG_D3.md (committed before this ran). Usage: python d3.py

Starts from D2's follower trades (leader up 20%+), filters them in stages, and describes the whole path from the
entry (next day's open) instead of fixing an exit. Descriptive: no pass mark.
"""
import glob, importlib.util, json, os
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("d2", os.path.join(HERE, "d2.py")); d2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(d2)
T, N, tick, dates, sic, size, valid, o, c, ret, quiet = d2.T, d2.N, d2.tick, d2.dates, d2.sic, d2.size, d2.valid, d2.o, d2.c, d2.ret, d2.quiet
z = d2.z; h = z["h"]; relvol = z["relvol"]; rs90 = z["rs90"].astype(bool)
rng = np.random.default_rng(20261010)

KEEP = {"chips & hardware": "3674 3672 3670 3679 3559 3571 3572 3576 3577 3661 3663 3669 3825 3827",
        "power & electrical": "3620 3621 3690 3443 3585 4911 4931 4924 1623 1731 1600",
        "energy": "1311 1381 1389 3533", "mining & metals": "1000 1040 1090 1220 1400 3312 3330",
        "defence & aerospace": "3721 3760 3812 3480", "compute hosting": "7374 7373", "freight": "4412 4400 4213"}
MAYBE = set("7370 7371 7372 3569 3560 3561 3590 2800 2810 2860 2890 4899 4812 4813 8711 1700".split())
group_of = {code: g for g, codes in KEEP.items() for code in codes.split()}

# ---- adjusted daily lows (the panel has open/high/close only)
lows_file = os.path.join(HERE, "lows.npz")
if os.path.exists(lows_file):
    low = np.load(lows_file)["low"]
else:
    tix = {t: i for i, t in enumerate(tick)}; lraw = np.full((T, N), np.nan)
    for f in sorted(glob.glob(os.path.join(HERE, "..", "runners", "work", "raw", "*.csv"))):
        d = os.path.basename(f)[:10]
        if d not in dates: continue
        df = pd.read_csv(f, usecols=["T", "l"], keep_default_na=False, na_values=[""])
        j = df["T"].map(tix); ok = j.notna()
        lraw[dates.index(d), j[ok].astype(int)] = df.loc[ok, "l"].to_numpy(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        low = lraw * np.where(z["craw"] > 0, c / z["craw"], np.nan)
    np.savez_compressed(lows_file, low=low)

# ---- path metrics for entering at the open of d+1, for every stock and day
H = [1, 3, 5, 10]
M = {k: np.full((T, N), np.nan, np.float32) for k in ["hi1", "lo1", "c1", "c2", "c3", "c5", "c10", "peak"] + [f"mfe{x}" for x in H] + [f"mae{x}" for x in H]}
for d in range(T - 11):
    E = o[d + 1]; okE = valid[d + 1] & np.isfinite(E) & (E > 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        hh = np.where(valid[d + 1:d + 11], h[d + 1:d + 11], np.nan) / E - 1
        ll = np.where(valid[d + 1:d + 11], low[d + 1:d + 11], np.nan) / E - 1
        cc = np.where(valid[d + 1:d + 11], c[d + 1:d + 11], np.nan) / E - 1
    M["hi1"][d], M["lo1"][d], M["c1"][d] = hh[0], ll[0], cc[0]
    filled = pd.DataFrame(cc).ffill().to_numpy()                       # last close available by each day
    for k in (2, 3, 5, 10): M[f"c{k}"][d] = filled[k - 1]
    for x in H:
        with np.errstate(all="ignore"):
            M[f"mfe{x}"][d] = np.nanmax(hh[:x], axis=0); M[f"mae{x}"][d] = np.nanmin(ll[:x], axis=0)
    anyc = np.isfinite(cc).any(0); pk = np.full(N, np.nan)
    pk[anyc] = np.nanargmax(np.where(np.isfinite(cc[:, anyc]), cc[:, anyc], -np.inf), axis=0) + 1
    M["peak"][d] = pk
    for k in M: M[k][d][~okE] = np.nan

# ---- follower trades with their attributes and controls
rows = []
for d in range(26, T - 11):
    big = valid[d] & np.isfinite(size[d]) & (size[d] >= d2.FLOOR) & np.isfinite(ret[d]) & d2.has_sic
    lead = np.flatnonzero(big & (ret[d] >= 0.20))
    if not len(lead): continue
    hot = set(sic[big & (np.abs(ret[d]) >= 0.10)])
    fol = set()
    for y in lead:
        g = d2.members[sic[y]]
        fol.update(g[(g != y) & quiet[d, g] & (size[d, g] <= size[d, y] / d2.MULT) & np.isfinite(M["c1"][d, g])].tolist())
    if not fol: continue
    pool = np.flatnonzero(quiet[d] & ~np.isin(sic, list(hot)) & np.isfinite(M["c1"][d])); psize = size[d, pool]
    for s in fol:
        cand = pool[(psize >= 0.5 * size[d, s]) & (psize <= 2.0 * size[d, s])]
        if len(cand) < 3: continue
        pick = rng.choice(cand, size=min(10, len(cand)), replace=False)
        rec = dict(d=d, s=s, sic=sic[s], takeable=bool(d2.takeable[d, s]), china=bool(d2.is_china[s]), rs90=bool(rs90[d, s]),
                   relvol=float(relvol[d + 1, s]) if np.isfinite(relvol[d + 1, s]) else np.nan)
        for k in M:
            rec[k] = float(M[k][d, s])
            with np.errstate(all="ignore"): rec["ctl_" + k] = float(np.nanmean(M[k][d, pick]))
        rows.append(rec)
t = pd.DataFrame(rows)
t["bucket"] = np.where(t.sic.isin(group_of), "keep", np.where(t.sic.isin(MAYBE), "maybe", "cut")); t["group"] = t.sic.map(group_of)
YEARS = (T - 37) / 252


def describe(x, name):
    if len(x) < 20:
        return dict(stage=name, trades=int(len(x)), note="fewer than 20 trades")
    r = dict(stage=name, trades=int(len(x)), stocks=int(x.s.nunique()), per_year=round(len(x) / YEARS))
    for k in ["hi1", "lo1", "c1", "c2", "c3", "c5", "c10", "mfe3", "mfe5", "mfe10", "mae5", "mae10"]:
        r[k + "_mean"], r[k + "_med"], r[k + "_ctl"] = float(x[k].mean()), float(x[k].median()), float(x["ctl_" + k].mean())
    for hz in H:
        for lvl in (0.2, 0.5, 1.0):
            r[f"hit{int(lvl * 100)}_d{hz}"] = float((x[f"mfe{hz}"] >= lvl).mean())
    r["peak_day1"] = float((x.peak == 1).mean()); r["peak_day2_3"] = float(x.peak.isin([2, 3]).mean()); r["peak_day4_10"] = float((x.peak >= 4).mean())
    return r


base = t
s1 = t[t.bucket == "keep"]; s2 = s1[s1.takeable]; s3 = s2[~s2.china & ~s2.rs90]
stages = [("0 every follower", base), ("1 kept industries", s1), ("2 + takeable", s2), ("3 + holds up (not China/HK, no recent reverse split)", s3),
          ("4a + own volume 2x", s3[s3.relvol >= 2]), ("4b + own volume 5x", s3[s3.relvol >= 5]),
          ("-- maybe industries, takeable, holds up", t[(t.bucket == "maybe") & t.takeable & ~t.china & ~t.rs90]),
          ("-- cut industries, takeable, holds up", t[(t.bucket == "cut") & t.takeable & ~t.china & ~t.rs90]),
          ("-- cut by stage 3: China/HK or recent reverse split", s2[s2.china | s2.rs90])]
stages += [(f"-- stage 3, {g}", s3[s3.group == g]) for g in KEEP]
out = [describe(x, n) for n, x in stages]
json.dump(out, open(os.path.join(HERE, "d3_results.json"), "w"), indent=1)
t.to_csv(os.path.join(HERE, "d3_trades.csv"), index=False)

pct = lambda v: f"{v:+.1%}"
print(f"{'stage':58s} {'trades':>6s} {'stocks':>6s} {'/yr':>5s} | day1 high   low   close | close d2   d3    d5    d10 | best in 5d (med) worst in 5d | reach +20% / +50% / +100% within 5d | controls: close d5, best 5d, +50% 5d")
for r in out:
    if "note" in r: print(f"{r['stage']:58s} {r['trades']:6d}  ({r['note']})"); continue
    x = [x for n, x in stages if n == r["stage"]][0]
    print(f"{r['stage']:58s} {r['trades']:6d} {r['stocks']:6d} {r['per_year']:5d} | {pct(r['hi1_mean'])} {pct(r['lo1_mean'])} {pct(r['c1_mean'])} | {pct(r['c2_mean'])} {pct(r['c3_mean'])} {pct(r['c5_mean'])} {pct(r['c10_mean'])} | "
          f"{pct(r['mfe5_mean'])} ({pct(r['mfe5_med'])}) {pct(r['mae5_mean'])} | {r['hit20_d5']:.1%} / {r['hit50_d5']:.1%} / {r['hit100_d5']:.2%} | {pct(r['c5_ctl'])}, {pct(r['mfe5_ctl'])}, {float((x['ctl_mfe5'] >= 0.5).mean()):.1%}")
print("\nmedians (close d1 / d5 / d10) and peak-day split (day 1 / days 2-3 / days 4-10):")
for r in out:
    if "note" in r: continue
    print(f"{r['stage']:58s} {pct(r['c1_med'])} / {pct(r['c5_med'])} / {pct(r['c10_med'])}   |  {r['peak_day1']:.0%} / {r['peak_day2_3']:.0%} / {r['peak_day4_10']:.0%}")
