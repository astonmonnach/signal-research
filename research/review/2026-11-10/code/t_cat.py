import sys, pickle
from core import *
sys.stdout.reconfigure(encoding="utf-8")
rows = pickle.load(open(HERE / "rows.pkl", "rb"))
GROUPS = {
    "LONG signals (scanner says buy-side)": ["8k_strategic_review", "activist_13d", "tender_issuer_buyback", "s1_dod_contract"],
    "DEALS (price pinned to an offer)": ["8k_merger_agreement", "merger_vote", "8k_tender_offer", "tender_third_party", "merger_arb"],
    "EVENTS tracked": ["8k_spin_off", "8k_lock_up", "8k_special_dividend", "ipo_priced", "delisting"],
    "SUPPLY flags (scanner says avoid)": ["8k_reverse_split", "registration_effective", "share_registration"],
    "RESEARCH tracked": ["insider_cluster", "insider_buy", "holder_buying", "linked_peer", "longterm_research", "deal_peer"],
}
def first(rs):
    seen, out = set(), []
    for r in sorted(rs, key=lambda r: r["found"]):
        if r["ticker"] not in seen:
            seen.add(r["ticker"]); out.append(r)
    return out
def line(name, rs):
    out = [f"{name:34} n={len(rs):4}"]
    for h in (5, 10, 20):
        a, x, c = stats([r.get(f"r{h}") for r in rs]), stats([r.get(f"x{h}") for r in rs]), stats([r.get(f"c{h}") for r in rs])
        if c.get("n"):
            out.append(f"{h:>2}d raw {fmt(a):>6} | vsIWM {fmt(x):>6} | vsMATCH {fmt(c):>6} med {fmt(c,'wmean'):>6} avg, beat {c['pos']:3.0f}% (n{c['n']})")
        else:
            out.append(f"{h:>2}d n/a")
    return "\n      ".join(out)
for g, cats in GROUPS.items():
    print("\n==", g)
    allr = first([r for r in rows if r["cat"] in cats])
    print(line("ALL (first flag per stock)", allr))
    print(line("  takeable ($1+, $150k/day)", [r for r in allr if r["take"]]))
    print(line("  not takeable", [r for r in allr if not r["take"]]))
    for c in cats:
        rs = first([r for r in rows if r["cat"] == c])
        if len(rs) >= 3:
            print(line("  " + c, rs)); print(line("     takeable", [r for r in rs if r["take"]]))
