import sys, pickle, csv, random
from bench import *
sys.stdout.reconfigure(encoding="utf-8")
rows = pickle.load(open(HERE/"rows.pkl","rb")); reg = pickle.load(open(HERE/"reg.pkl","rb")); G = pickle.load(open(HERE/"found_groups.pkl","rb")); picks = pickle.load(open(HERE/"picks.pkl","rb"))
def first(rs):
    seen,out=set(),[]
    for r in sorted(rs,key=lambda r:r.get("found") or r.get("date")):
        if r["ticker"] not in seen: seen.add(r["ticker"]); out.append(r)
    return out
def avgpath(ms, key="cpath", f=median):
    out=[]
    for k in range(21):
        v=[m[key][k] for m in ms if m.get(key) and len(m[key])>k]
        out.append((f(v) if len(v)>=5 else None, len(v)))
    return out
sets = {
 "Supply flags, takeable": first([r for r in rows if r["cat"] in ("8k_reverse_split","registration_effective","share_registration") and r["take"]]),
 "Supply flags, not takeable": first([r for r in rows if r["cat"] in ("8k_reverse_split","registration_effective","share_registration") and not r["take"]]),
 "AVOID register": reg,
 "Raw buy-side flags, takeable": first([r for r in rows if r["cat"] in ("8k_strategic_review","activist_13d","tender_issuer_buyback") and r["take"]]),
 "Names we wrote up (long side)": first([m for (v,g),ms in G.items() if v in ("TRACKED","WATCH","OWN") for m in ms]),
 "WATCH / OWN picks": picks,
 "Signed deals, takeable": first([r for r in rows if r["cat"] in ("8k_merger_agreement","merger_vote","8k_tender_offer","tender_third_party","merger_arb") and r["take"]]),
}
P={}
for name,ms in sets.items():
    p=avgpath(ms); P[name]=p
    print(f"{name:32} n={len(ms):3} | day1 {p[0][0]:+5.1f} d3 {p[2][0]:+5.1f} d5 {p[4][0]:+5.1f} d10 {p[9][0] if p[9][0] is not None else float('nan'):+5.1f} d15 {p[14][0] if p[14][0] is not None else float('nan'):+5.1f} d20 {p[19][0] if p[19][0] is not None else float('nan'):+5.1f} (n at d20 {p[19][1]})")
pickle.dump(P, open(HERE/"paths.pkl","wb"))

print("\n== Small buy-side pockets, with 95% bootstrap intervals on the mean excess vs matched")
def ci(v,n=10000):
    v=[x for x in v if x is not None]
    if len(v)<6: return None
    rng=random.Random(5); xs=sorted(mean([rng.choice(v) for _ in v]) for _ in range(n)); return xs[int(.025*n)], xs[int(.975*n)]
for cat,k in (("8k_special_dividend","c5"),("8k_special_dividend","c10"),("tender_issuer_buyback","c10"),("merger_vote","c20"),("8k_spin_off","c5"),("8k_lock_up","c10"),("8k_lock_up","c20"),("ipo_priced","c5"),("ipo_priced","c10"),("delisting","c20")):
    rs=first([r for r in rows if r["cat"]==cat and r["take"]]); v=[r.get(k) for r in rs if r.get(k) is not None]
    c=ci(v); print(f"{cat:24} {k:4} n={len(v):3} median {median(v):+6.1f} mean {mean(v):+6.1f} CI {c and (round(c[0],1),round(c[1],1))} beat {100*sum(x>0 for x in v)/len(v):.0f}%")

print("\n== How late are we? Buy-side flags: move before we could act vs after (medians, raw %)")
for name,cats in (("strategic review",["8k_strategic_review"]),("activist 13D",["activist_13d"]),("signed merger",["8k_merger_agreement"]),("issuer tender/buyback",["tender_issuer_buyback"]),("special dividend",["8k_special_dividend"])):
    rs=first([r for r in rows if r["cat"] in cats and r["take"]])
    g=lambda k: median([r[k] for r in rs if r.get(k) is not None])
    print(f"{name:22} n={len(rs):3} | 5 days before {g('pre5'):+5.1f} | found day {g('found_day'):+5.1f} | overnight gap to our entry {g('gap'):+5.1f} | next 5d {g('r5'):+5.1f} | next 10d {g('r10'):+5.1f}")
    big=[r for r in rs if (r.get('found_day') or 0)>=10]
    if len(big)>=5: print(f"   {len(big)} of them jumped 10%+ on the found day: next 5d median {median([r['c5'] for r in big if r.get('c5') is not None]):+5.1f} vs matched, next 10d {median([r['c10'] for r in big if r.get('c10') is not None] or [float('nan')]):+5.1f}")
    flat=[r for r in rs if abs(r.get('found_day') or 0)<3]
    if len(flat)>=5: print(f"   {len(flat)} barely moved on the found day (<3%): next 5d {median([r['c5'] for r in flat if r.get('c5') is not None]):+5.1f} vs matched, next 10d {median([r['c10'] for r in flat if r.get('c10') is not None] or [float('nan')]):+5.1f}")

print("\n== Best and worst long-side names we could have bought (takeable, direction 0/+1 flags and write-ups), to the 9 Nov close vs matched (20-session cap)")
pool=first([r for r in rows if r["take"] and r["dirn"]>=0 and r["cat"] not in ("delisting","8k_lock_up","ipo_priced") and not r["cat"].startswith("setup_supply") and r.get("cpath")])
for lab,srt in (("BEST",True),("WORST",False)):
    print(lab)
    for r in sorted(pool,key=lambda r:r["cpath"][-1],reverse=srt)[:14]:
        print(f"  {r['ticker']:6} {r['cat']:22} found {r['found']} ${r['entry_raw']:<7.2f} stock {r['path'][-1][0]:+6.1f}% vs matched {r['cpath'][-1]:+6.1f} ({len(r['path'])} sessions) | {r['note'][:60]}")
print(len(pool),"names in that pool; share that beat matched to date:", round(100*sum(r['cpath'][-1]>0 for r in pool)/len(pool)),"%; median", round(median(r['cpath'][-1] for r in pool),1))
