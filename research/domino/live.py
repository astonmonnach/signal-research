"""The domino run (DOMINO-1), point in time. Rule: RULE_DOMINO1.md.

    python research/domino/live.py                      # the latest day with prices
    python research/domino/live.py --asof 2026-10-05    # one day, using only what was known that day
    python research/domino/live.py --from 2026-10-05 --to 2026-10-09

For the as-of day D it reads ONLY daily bars dated <= D, splits executed <= D and SEC facts filed <= D, finds the
signals, appends them to live_signals.csv, and then (separately) fills in what happened after with any later bars.

Needs: research/runners/work/raw/YYYY-MM-DD.csv for the last ~45 trading days (pulled with the market-data connector
and converted by research/runners/work/ingest.py), and split events in the runners ref files plus splits_recent.csv.
"""
import csv, glob, json, os, sys, time, urllib.request
from datetime import date, timedelta
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "runners", "work", "raw")
REF = os.path.join(HERE, "..", "runners", "work", "ref")
UA = {"User-Agent": "PersonalResearch research@example.com"}
CACHE = os.path.join(HERE, "facts_cache"); os.makedirs(CACHE, exist_ok=True)

# ---- the rule's numbers (fixed in RULE_DOMINO1.md)
LEADER_SIZE, LEADER_MOVE, SIZE_RATIO = 20e6, 0.20, 10.0
QUIET_MOVE, MIN_PRICE, MIN_SIZE, MIN_RELVOL, RS_DAYS = 0.10, 1.0, 250_000, 2.0, 90
KEEP = set("3674 3672 3670 3679 3559 3571 3572 3576 3577 3661 3663 3669 3825 3827 3620 3621 3690 3443 3585 4911 4931 4924 1623 1731 1600 "
           "1311 1381 1389 3533 1000 1040 1090 1220 1400 3312 3330 3721 3760 3812 3480 7374 7373 4412 4400 4213".split())
ANNUAL = {"10-K", "10-K/A", "10-KT", "20-F", "20-F/A", "40-F", "40-F/A"}
TAGS = {"rev": [("us-gaap", "Revenues"), ("us-gaap", "RevenueFromContractWithCustomerExcludingAssessedTax"),
                ("us-gaap", "RevenueFromContractWithCustomerIncludingAssessedTax"), ("us-gaap", "SalesRevenueNet"),
                ("us-gaap", "RevenuesNetOfInterestExpense"), ("ifrs-full", "Revenue")],
        "ocf": [("us-gaap", "NetCashProvidedByUsedInOperatingActivities"), ("us-gaap", "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"),
                ("ifrs-full", "CashFlowsFromUsedInOperatingActivities")],
        "cash": [("us-gaap", "CashAndCashEquivalentsAtCarryingValue"), ("us-gaap", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"),
                 ("us-gaap", "Cash"), ("ifrs-full", "CashAndCashEquivalents")],
        "shares": [("dei", "EntityCommonStockSharesOutstanding"), ("us-gaap", "CommonStockSharesOutstanding")]}

meta = pd.read_csv(os.path.join(HERE, "sic_map.csv"), dtype=str).fillna("").set_index("ticker")
ALL_DAYS = sorted(os.path.basename(f)[:10] for f in glob.glob(os.path.join(RAW, "*.csv")))

# ---- splits: ticker -> [(execution_date, from, to)]
SPLITS = {}
for f in (os.path.join(REF, "reverse_splits.csv"), os.path.join(REF, "other_splits.csv"), os.path.join(HERE, "splits_recent.csv")):
    if os.path.exists(f):
        for r in csv.DictReader(open(f, encoding="utf-8")):
            try: SPLITS.setdefault(r["ticker"], []).append((r["execution_date"], float(r["split_from"]), float(r["split_to"])))
            except Exception: pass


def split_factor(tk, after, upto):
    """Multiply a price dated <= `after` by this to put it on the share basis of `upto` (splits with after < exec <= upto)."""
    f = 1.0
    for ex, a, b in SPLITS.get(tk, []):
        if after < ex <= upto and b > 0: f *= a / b
    return f


def load(days):
    """dict day -> DataFrame indexed by ticker with raw o,h,l,c,v"""
    out = {}
    for d in days:
        df = pd.read_csv(os.path.join(RAW, d + ".csv"), usecols=["T", "v", "o", "c", "h", "l"], keep_default_na=False, na_values=[""])
        out[d] = df.drop_duplicates("T").set_index("T")
    return out


# ---- scorecard, as of a date (same three questions as D4)
def facts(cik):
    p = os.path.join(CACHE, f"CIK{cik}.json")
    if os.path.exists(p) and time.time() - os.path.getmtime(p) < 20 * 3600:
        return json.load(open(p, encoding="utf-8"))
    out = {k: [] for k in TAGS}
    try:
        j = json.loads(urllib.request.urlopen(urllib.request.Request(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json", headers=UA), timeout=60).read())
        for k, tags in TAGS.items():
            for tax, tag in tags:
                for unit, rows in j.get("facts", {}).get(tax, {}).get(tag, {}).get("units", {}).items():
                    if unit in ("USD", "shares"):
                        out[k] += [[r.get("start"), r.get("end"), r.get("val"), r.get("form"), r.get("filed")] for r in rows]
        time.sleep(0.13)
    except Exception as ex:
        if os.path.exists(p): return json.load(open(p, encoding="utf-8"))
        out["error"] = str(ex)[:80]
    json.dump(out, open(p, "w", encoding="utf-8"))
    return out


def _days(a, b): return (date.fromisoformat(b) - date.fromisoformat(a)).days


def scorecard(tk, asof):
    cik = meta.cik.get(tk, "")
    if not cik: return None, None, None, {}
    f = facts(cik)

    def annual(rows):
        best = None
        for start, end, val, form, filed in rows:
            if not (start and end and filed) or form not in ANNUAL or filed > asof or val is None or not 330 <= _days(start, end) <= 400: continue
            if best is None or (end, filed) > best[:2]: best = (end, filed, val)
        return best

    def instant(rows):
        best = None
        for start, end, val, form, filed in rows:
            if not (end and filed) or filed > asof or val is None: continue
            if best is None or (end, filed) > best[:2]: best = (end, filed, val)
        return best

    rev, ocf, cash, cur = annual(f["rev"]), annual(f["ocf"]), instant(f["cash"]), instant(f["shares"])
    R = None if rev is None else rev[2] >= 10e6
    C = None if ocf is None else (True if ocf[2] >= 0 else (None if cash is None else cash[2] >= -ocf[2]))
    D, growth = None, None
    if cur:
        prior = None
        for start, end, val, form, filed in f["shares"]:
            if not (end and filed) or filed > asof or not val: continue
            gap = _days(end, cur[0])
            if 270 <= gap <= 460 and (prior is None or abs(gap - 365) < abs(_days(prior[0], cur[0]) - 365)): prior = (end, val)
        if prior and prior[1] > 0:
            growth = cur[2] / prior[1] * split_factor(tk, prior[0], cur[0]) - 1     # both counts on the later share basis
            D = growth < 0.25
    detail = dict(revenue=rev[2] if rev else None, op_cash_flow=ocf[2] if ocf else None, cash=cash[2] if cash else None, share_growth=growth,
                  annual_period=rev[0] if rev else (ocf[0] if ocf else None))
    return R, C, D, detail


def signals(asof):
    i = ALL_DAYS.index(asof)
    if i < 30: raise SystemExit("need at least 30 trading days of bars before the as-of day")
    win = ALL_DAYS[i - 40:i + 1]; bars = load(win)                                  # nothing after the as-of day is read here
    tks = [t for t in bars[asof].index if t in meta.index]
    px = pd.DataFrame({d: bars[d].c.reindex(tks) for d in win}); vol = pd.DataFrame({d: bars[d].v.reindex(tks) for d in win})
    adj = np.array([[split_factor(t, d, asof) for d in win] for t in tks])           # put every day on the as-of share basis
    pa = px.to_numpy(float) * adj; va = vol.to_numpy(float) / adj
    dv = px.to_numpy(float) * vol.to_numpy(float)
    with np.errstate(all="ignore"):
        ret = pa[:, -1] / pa[:, -2] - 1
        size = np.array([np.nanmedian(r) if np.isfinite(r).sum() >= 15 else np.nan for r in dv[:, -26:-6]])   # 20 days ending 6 before
        relvol = np.array([va[k, -1] / np.nanmean(va[k, -21:-1]) if np.isfinite(va[k, -21:-1]).sum() >= 10 and np.nanmean(va[k, -21:-1]) > 0 else np.nan for k in range(len(tks))])
        r1 = pa[:, 1:] / pa[:, :-1]; r2 = pa[:, 2:] / pa[:, :-2]
        runner = np.zeros(len(tks), bool)
        for back in (1, 2, 3):                                                      # a +100% day (or two-day) on D, D-1 or D-2
            runner |= (r1[:, -back] >= 2.0) | (r2[:, -back] >= 2.0)
    sic = np.array([meta.sic.get(t, "") for t in tks]); hq = np.array([meta.hq.get(t, "") for t in tks])
    price = px[asof].to_numpy(float)
    cutoff = (date.fromisoformat(asof) - timedelta(days=RS_DAYS)).isoformat()
    rs90 = np.array([any(cutoff <= ex <= asof and a > b for ex, a, b in SPLITS.get(t, [])) for t in tks])
    base_quiet = np.isfinite(ret) & (ret < QUIET_MOVE) & ~runner & np.isfinite(size) & (size > 0)
    big = np.isfinite(size) & (size >= LEADER_SIZE) & np.isfinite(ret)
    leaders = np.flatnonzero(big & (ret >= LEADER_MOVE) & np.isin(sic, list(KEEP)))
    hot = set(sic[big & (np.abs(ret) >= 0.10)])
    funnel = dict(day=asof, leaders=int(len(leaders)), same_industry_smaller_quiet=0, takeable=0, holds_up=0, volume_2x=0, scorecard_3=0)
    rows, seen = [], set()
    for y in leaders:
        cand = np.flatnonzero((sic == sic[y]) & base_quiet & (size <= size[y] / SIZE_RATIO)); cand = cand[cand != y]
        funnel["same_industry_smaller_quiet"] += len(cand)
        cand = cand[(price[cand] >= MIN_PRICE) & (size[cand] >= MIN_SIZE)]; funnel["takeable"] += len(cand)
        cand = cand[~np.isin(hq[cand], ["F4", "K3"]) & ~rs90[cand]]; funnel["holds_up"] += len(cand)
        cand = cand[np.nan_to_num(relvol[cand]) >= MIN_RELVOL]; funnel["volume_2x"] += len(cand)
        for s in cand:
            if tks[s] in seen: continue
            R, C, D, det = scorecard(tks[s], asof); score = None if None in (R, C, D) else int(R) + int(C) + int(D)
            rec = dict(signal_day=asof, ticker=tks[s], leader=tks[y], leader_move=round(float(ret[y]), 4), leader_size=round(float(size[y])), sic=sic[s],
                       industry=meta.sic_desc.get(tks[s], ""), price=round(float(price[s]), 4), size=round(float(size[s])), own_move=round(float(ret[s]), 4),
                       relvol=round(float(relvol[s]), 2), R=R, C=C, D=D, score=score, revenue=det.get("revenue"), op_cash_flow=det.get("op_cash_flow"),
                       cash=det.get("cash"), share_growth=None if det.get("share_growth") is None else round(det["share_growth"], 3), passes=score == 3)
            seen.add(tks[s]); rows.append(rec)
            if score == 3: funnel["scorecard_3"] += 1
    lead_rows = [dict(ticker=tks[y], move=float(ret[y]), size=float(size[y]), industry=meta.sic_desc.get(tks[y], "")) for y in leaders]
    # controls for each passing signal: quiet stocks in industries with no big mover today, half to double the size
    rng = np.random.default_rng(int(asof.replace("-", "")))
    pool = np.flatnonzero(base_quiet & ~np.isin(sic, list(hot)) & (sic != ""))
    for rec in rows:
        if not rec["passes"]: continue
        c = pool[(size[pool] >= 0.5 * rec["size"]) & (size[pool] <= 2.0 * rec["size"])]
        rec["controls"] = ";".join(tks[k] for k in rng.choice(c, size=min(10, len(c)), replace=False)) if len(c) >= 3 else ""
    return funnel, lead_rows, rows


def outcome(tk, signal_day):
    """What happened after: entry at the next day's open, on the entry day's share basis. Uses bars after the signal day."""
    i = ALL_DAYS.index(signal_day)
    later = ALL_DAYS[i + 1:i + 11]
    if not later: return {}
    bars = load(later); e = later[0]
    if tk not in bars[e].index or not np.isfinite(bars[e].o[tk]) or bars[e].o[tk] <= 0: return dict(entry_day=e, note="no open on the entry day")
    entry = float(bars[e].o[tk]); out = dict(entry_day=e, entry=round(entry, 4), days_so_far=0)
    hi, lo, last = -9.0, 9.0, None
    for n, d in enumerate(later, 1):
        if tk not in bars[d].index: continue
        f = 1.0 / split_factor(tk, e, d) if split_factor(tk, e, d) else 1.0          # back to the entry day's basis
        b = bars[d].loc[tk]; c_, h_, l_ = b.c * f / entry - 1, b.h * f / entry - 1, b.l * f / entry - 1
        hi, lo, last = max(hi, h_), min(lo, l_), c_; out["days_so_far"] = n
        if n in (1, 5, 10): out[f"close_d{n}"] = round(float(c_), 4)
    out.update(latest_close=None if last is None else round(float(last), 4), best_so_far=round(float(hi), 4), worst_so_far=round(float(lo), 4))
    return out


def main():
    a = sys.argv[1:]
    def opt(k): return a[a.index(k) + 1] if k in a else None
    days = [d for d in ALL_DAYS if opt("--from") <= d <= (opt("--to") or ALL_DAYS[-1])] if opt("--from") else [opt("--asof") or ALL_DAYS[-1]]
    log = os.path.join(HERE, "live_check.csv" if "--check" in a else "live_signals.csv")   # --check: validation runs, kept out of the real log
    old = pd.read_csv(log, dtype=str) if os.path.exists(log) else pd.DataFrame()
    allrows = []
    for d in days:
        funnel, leaders, rows = signals(d)
        print(f"\n===== {d} ({date.fromisoformat(d):%a}) =====")
        print(f"leaders (kept industry, $20M+ a day, up 20%+): {funnel['leaders']}" + "".join(f"\n   {l['ticker']:6s} {l['move']:+.1%}  ${l['size'] / 1e6:,.0f}M a day  {l['industry']}" for l in leaders))
        print(f"funnel: {funnel['same_industry_smaller_quiet']} smaller quiet same-industry stocks -> {funnel['takeable']} takeable -> {funnel['holds_up']} hold up -> {funnel['volume_2x']} with volume 2x+ -> {funnel['scorecard_3']} pass the scorecard")
        for r in rows:
            tag = "SIGNAL" if r["passes"] else f"dropped (scorecard {r['score'] if r['score'] is not None else 'unknown'}: R={r['R']} C={r['C']} D={r['D']})"
            print(f"   {r['ticker']:6s} after {r['leader']} {r['leader_move']:+.0%} | ${r['price']:.2f}, ${r['size'] / 1e6:.2f}M a day, own move {r['own_move']:+.1%}, volume {r['relvol']:.1f}x | {tag}")
        allrows += rows
    new = pd.DataFrame(allrows)
    if len(new):
        new = new.astype(object).where(new.notna(), "")
        keyset = set(zip(old.get("signal_day", []), old.get("ticker", [])))
        add = new[[(r.signal_day, r.ticker) not in keyset for r in new.itertuples()]]
        full = pd.concat([old, add.astype(str)], ignore_index=True) if len(old) else add.astype(str)
    else:
        full = old
    if len(full):
        outs = []
        for r in full.itertuples():
            o = outcome(r.ticker, r.signal_day) if str(r.passes) == "True" else {}
            if o and str(getattr(r, "controls", "")) not in ("", "nan"):
                cs = [outcome(c, r.signal_day) for c in str(r.controls).split(";")]
                for k in ("close_d1", "close_d5", "close_d10", "latest_close"):
                    v = [c[k] for c in cs if c.get(k) is not None]
                    if v: o["ctl_" + k] = round(float(np.mean(v)), 4)
            outs.append(o)
        res = pd.DataFrame(outs)
        for c in res.columns: full[c] = res[c].values
        full.to_csv(log, index=False)
        sig = full[full.passes.astype(str) == "True"]
        print(f"\n===== signals logged: {len(sig)} (plus {len(full) - len(sig)} dropped at the scorecard) -> live_signals.csv =====")
        cols = [c for c in ["signal_day", "ticker", "leader", "entry_day", "entry", "days_so_far", "close_d1", "close_d5", "latest_close", "ctl_latest_close", "best_so_far", "worst_so_far"] if c in sig.columns]
        if len(sig): print(sig[cols].to_string(index=False))
    else:
        print("\nno signals in the period.")


if __name__ == "__main__":
    main()
