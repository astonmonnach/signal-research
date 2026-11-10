"""L. Does any simple exit make the buy side pay? Enter at the first open after the find. Sell at +T% if touched, or at -S% if
touched first (same-day touches count as the stop), else sell at the close of the last session in the window.
Daily highs and lows. Shown before costs and after a 3.5% round trip."""
import sys, pickle, bisect, datetime as dt
from statistics import mean, median
from core import *
sys.stdout.reconfigure(encoding="utf-8")
rows = pickle.load(open(HERE/"rows.pkl","rb")); G = pickle.load(open(HERE/"found_groups.pkl","rb")); picks = pickle.load(open(HERE/"picks.pkl","rb"))
def first(rs, key="found"):
    seen,out=set(),[]
    for r in sorted(rs,key=lambda r:r.get(key) or r.get("date")):
        if r["ticker"] not in seen: seen.add(r["ticker"]); out.append(r)
    return out
def outcome(t, found, n, T, Sx):
    s = S(t)
    if not s: return None
    dates=[b[0] for b in s]; f = dt.date.fromisoformat(found) if isinstance(found,str) else found
    e=bisect.bisect_right(dates,f)
    w=s[e:e+n]
    if len(w)<n: return None
    eo=s[e][1]
    for k,b in enumerate(w):
        if b[1] <= eo*(1-Sx/100) and k>0: return -((1-b[1]/eo)*100), k+1, "gap stop"      # opened below the stop: filled at the open
        if b[7] <= eo*(1-Sx/100): return -Sx, k+1, "stop"
        if b[6] >= eo*(1+T/100): return T, k+1, "target"
    return (w[-1][2]/eo-1)*100, n, "time"
KIND={"ESRT":0,"SKYA":0,"PED":0,"SRTA":0,"DIBS":0,"ACB":0,"XPOF":0,"CPAC":0,"DOLE":0,"SEER":0,"VVR":0}
sets = {
 "Scanner buy-side flags, takeable": [(r["ticker"],r["found"]) for r in first([r for r in rows if r["cat"] in ("8k_strategic_review","activist_13d","tender_issuer_buyback") and r["take"]])],
 "Long-side names we wrote up": [(m["ticker"],m["found"]) for m in first([m for (v,g),ms in G.items() if v in ("TRACKED","WATCH","OWN") for m in ms])],
 "OWN / WATCH picks": [(m["ticker"],m["date"]) for m in picks],
 "Picks: outside buyer or holder acting": [(m["ticker"],m["date"]) for m in picks if m["ticker"] in KIND],
 "Picks: company story or insiders": [(m["ticker"],m["date"]) for m in picks if m["ticker"] not in KIND],
}
for name, items in sets.items():
    print(f"\n== {name}")
    for n in (5, 10):
        print(f"  window {n} sessions: mean result per trade before costs (after 3.5%) | share hitting target / stop / neither | n")
        for T,Sx in ((5,5),(10,5),(10,10),(20,10),(20,20),(999,10),(999,999)):
            o=[outcome(t,f,n,T,Sx) for t,f in items]; o=[x for x in o if x]
            if len(o)<5: print("    too few"); break
            m=mean(x[0] for x in o); tg=100*sum(x[2]=="target" for x in o)/len(o); st=100*sum(x[2] in ("stop","gap stop") for x in o)/len(o)
            lab = f"target +{T}% / stop -{Sx}%" if T<900 and Sx<900 else ("no target / stop -%d%%"%Sx if Sx<900 else "no target, no stop (hold)")
            print(f"    {lab:26} {m:+6.2f}% ({m-3.5:+6.2f}%) | {tg:3.0f}% / {st:3.0f}% / {100-tg-st:3.0f}% | median {median(x[0] for x in o):+5.1f} | n={len(o)}")
