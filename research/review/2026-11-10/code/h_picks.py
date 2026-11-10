"""H. For every name we gave a verdict on or tracked: each company filing after the verdict (results, deals, holder
filings, tenders), at its actual time, and what the price did in the next hours and days. Plus peaks and when."""
import sys, csv, json, pickle, datetime as dt
from statistics import median, mean
from intraday import *
from core import excursion, S as daily

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[4]
FIL = json.load(open(HERE / ("filings_picks.json" if "--picks" in sys.argv else "filings.json")))
tick = json.load(open(ROOT / "research/movers/mv1/cache/company_tickers.json"))
T2C = {v["ticker"]: str(v["cik_str"]) for v in tick.values()}
T2C["MSGS"] = T2C.get("MSGK", T2C.get("MSGS"))
KEEP = ("8-K", "6-K", "10-Q", "10-K", "SC 13D", "SC 13D/A", "SCHEDULE 13D", "SCHEDULE 13D/A", "SC TO-I", "SC TO-I/A", "SC TO-T", "SC TO-T/A",
        "SC 14D9", "SC 14D9/A", "425", "DEFM14A", "PREM14A", "S-1", "S-3", "EFFECT", "424B5", "424B3", "144")
ITEM = {"2.02": "results", "1.01": "material agreement", "2.01": "deal completed", "5.02": "officer/director change", "7.01": "Reg FD", "8.01": "other event",
        "2.05": "restructuring", "3.01": "listing notice", "5.07": "holder vote", "1.02": "agreement ended", "2.03": "new debt", "3.02": "unregistered sale", "5.03": "bylaws"}

PICKS = [("2026-10-05", "MTUS", "OWN"), ("2026-10-05", "RYAM", "WATCH"), ("2026-10-05", "MOD", "WATCH"), ("2026-10-05", "THRM", "WATCH"), ("2026-10-05", "WHF", "WATCH"),
         ("2026-10-05", "CTVA", "WATCH"), ("2026-10-05", "VYLR", "WATCH"), ("2026-10-05", "HMH", "WATCH"), ("2026-10-06", "ESRT", "WATCH"), ("2026-10-10", "MSGS", "WATCH"),
         ("2026-10-12", "BORR", "WATCH"), ("2026-10-12", "SKYA", "WATCH"), ("2026-10-14", "PED", "WATCH"), ("2026-10-15", "IMSR", "WATCH"), ("2026-10-16", "SRTA", "WATCH"),
         ("2026-10-20", "DIBS", "WATCH"), ("2026-10-20", "ACB", "WATCH"), ("2026-10-21", "XPOF", "WATCH"), ("2026-10-22", "CPAC", "WATCH"), ("2026-10-23", "DOLE", "WATCH"),
         ("2026-11-01", "SEER", "WATCH"), ("2026-11-05", "VVR", "WATCH")]
F = list(csv.DictReader(open(ROOT / "research/found/found.csv", encoding="utf-8")))
have = {t for _, t, _ in PICKS}
NAMES = PICKS if "--picks" in sys.argv else PICKS + [(r["found"], r["ticker"], r["view"]) for r in F if r["view"] in ("TRACKED",) and r["ticker"] not in have]


def label(form, items):
    if form == "8-K":
        its = [ITEM.get(i.strip(), i.strip()) for i in (items or "").split(",") if i.strip() and i.strip() != "9.01"]
        return "8-K: " + ", ".join(its[:3]) if its else "8-K"
    return form


all_ev = []
out_lines = []
for d, t, view in NAMES:
    tk = "MSGK" if t == "MSGS" else t
    c = T2C.get(tk) or T2C.get(t)
    rows = FIL.get(c, {}).get("rows", []) if c else []
    evs = []
    for acc, form, fd, adt, items in rows:
        if form not in KEEP or fd <= d or fd > "2026-11-09":
            continue
        t0 = dt.datetime.fromisoformat(adt.replace("Z", "+00:00"))
        x = react(tk, t0)
        if not x:
            continue
        x.update(ticker=t, form=form, items=items, what=label(form, items), fd=fd, view=view, verdict_date=d, is_pick=(d, t, view) in PICKS)
        evs.append(x)
    # one line per filing moment (results 8-K and 10-Q often land together): keep the first of filings within 30 minutes
    evs.sort(key=lambda e: e["t0"])
    kept = []
    for e in evs:
        if kept and ((e["t0"] - kept[-1]["t0"]).total_seconds() < 1800 or e["entry_time"] == kept[-1]["entry_time"]):
            if e["what"] not in kept[-1]["what"]:
                kept[-1]["what"] += " + " + e["what"]
            continue
        kept.append(e)
    all_ev += kept
    if (d, t, view) in PICKS:
        ex = excursion(tk, d)
        out_lines.append(f"\n### {t} ({view} {d[8:]}/{d[5:7]}): peak {ex['peak']:+.1f}% on {ex['peak_date'].strftime('%d %b')} (session {ex['peak_day']}), low {ex['trough']:+.1f}% on {ex['trough_date'].strftime('%d %b')}, now {ex['now']:+.1f}%")
        for e in kept:
            ny = e["t0"].astimezone(NY); uk = e["t0"].astimezone(LON)
            g = lambda k: f"{e[k]:+6.1f}" if e.get(k) is not None else "   n/a"
            out_lines.append(f"  {ny.strftime('%d %b %H:%M')} ET ({uk.strftime('%H:%M')} UK) {e['what'][:44]:44} | before ${e['p0']:<8.2f} gap {g('gap')} | +30m {g('r30')} +1h {g('r60')} +2h {g('r120')} close {g('rclose')} next {g('rnext')} 3rd {g('r3')} | peak 3 sessions {g('peak_3d')} after {e.get('peak_3d_min', 0) / 60:5.1f}h, low {g('low_3d')}")
print("\n".join(out_lines))
pickle.dump(all_ev, open(HERE / "pick_events.pkl", "wb"))


def S_(v):
    v = [x for x in v if x is not None]
    return "   n/a" if not v else f"{median(v):+5.1f}/{mean(v):+5.1f}/{100 * sum(x > 0 for x in v) / len(v):3.0f}% n{len(v)}"


print("\n\n== All filings after a verdict or a find, names we wrote up (median / mean / share positive)")
kinds = {"Results (8-K item 2.02)": lambda e: e["form"] == "8-K" and "2.02" in (e["items"] or ""),
         "Deal or agreement 8-K (1.01, 2.01)": lambda e: e["form"] == "8-K" and ("1.01" in (e["items"] or "") or "2.01" in (e["items"] or "")) and "2.02" not in (e["items"] or ""),
         "Other 8-K / 6-K": lambda e: e["form"] in ("8-K", "6-K") and not any(i in (e["items"] or "") for i in ("2.02", "1.01", "2.01")),
         "13D or 13D/A": lambda e: "13D" in e["form"],
         "Tender documents (SC TO, 14D-9)": lambda e: e["form"].startswith("SC TO") or e["form"].startswith("SC 14D9"),
         "Merger communications (425, proxies)": lambda e: e["form"] in ("425", "DEFM14A", "PREM14A")}
for k, f in kinds.items():
    es = [e for e in all_ev if f(e)]
    if len(es) < 4:
        continue
    absgap = [abs(e["gap"]) for e in es]
    print(f"{k:38} n={len(es):3} | size of the gap before we could act: median {median(absgap):4.1f}% | from entry: +30m {S_([e['r30'] for e in es])} | +2h {S_([e['r120'] for e in es])} | close {S_([e['rclose'] for e in es])} | next {S_([e.get('rnext') for e in es])} | 3rd {S_([e.get('r3') for e in es])}")
    up = [e for e in es if e["gap"] >= 3]; dn = [e for e in es if e["gap"] <= -3]
    for lab, s in (("   gapped up 3%+", up), ("   gapped down 3%+", dn)):
        if len(s) >= 3:
            print(f"{lab:38} n={len(s):3} | +30m {S_([e['r30'] for e in s])} | +2h {S_([e['r120'] for e in s])} | close {S_([e['rclose'] for e in s])} | next {S_([e.get('rnext') for e in s])} | 3rd {S_([e.get('r3') for e in s])}")
