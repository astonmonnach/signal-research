"""C. Does reading add anything over the raw scan? Plus the AVOID register, public calls, and the exploration-set state cuts."""
import sys, csv, pickle, random, collections
from bench import *

sys.stdout.reconfigure(encoding="utf-8")
rows = pickle.load(open(HERE / "rows.pkl", "rb"))
G = pickle.load(open(HERE / "found_groups.pkl", "rb"))


def first(rs):
    seen, out = set(), []
    for r in sorted(rs, key=lambda r: r["found"]):
        if r["ticker"] not in seen:
            seen.add(r["ticker"]); out.append(r)
    return out


def perm(a, b, n=20000, seed=7):
    """Two-sided permutation p-value for the difference in means of a and b."""
    a, b = [x for x in a if x is not None], [x for x in b if x is not None]
    if len(a) < 4 or len(b) < 4:
        return None
    obs = mean(a) - mean(b)
    pool = a + b
    rng = random.Random(seed)
    hit = 0
    for _ in range(n):
        rng.shuffle(pool)
        if abs(mean(pool[:len(a)]) - mean(pool[len(a):])) >= abs(obs):
            hit += 1
    return hit / n


def boot_ci(v, n=10000, seed=11, f=mean):
    v = [x for x in v if x is not None]
    if len(v) < 5:
        return None
    rng = random.Random(seed)
    xs = sorted(f([rng.choice(v) for _ in v]) for _ in range(n))
    return xs[int(0.025 * n)], xs[int(0.975 * n)]


def desc(name, ms, keys=("c5", "c10", "c20")):
    parts = [f"{name:44} n={len(ms):3}"]
    for k in keys:
        s = stats([m.get(k) for m in ms])
        if s.get("n"):
            ci = boot_ci([m.get(k) for m in ms])
            parts.append(f"{k}: med {s['med']:+6.1f} mean {s['mean']:+6.1f}" + (f" [{ci[0]:+.1f},{ci[1]:+.1f}]" if ci else "") + f" beat {s['pos']:3.0f}% (n{s['n']})")
    print(" | ".join(parts))


print("=== 1. READING vs RAW SCAN (excess vs matched unflagged stocks) ===")
act_read = G.get(("TRACKED", "Activists and big holders"), []) + G.get(("WATCH", "Activists and big holders"), [])
read_t = {m["ticker"] for m in act_read}
act_raw = first([r for r in rows if r["cat"] == "activist_13d" and r["take"] and r["ticker"] not in read_t])
act_read1 = first(sorted(act_read, key=lambda m: m["found"]))
desc("13D names we read and kept (tracked/WATCH)", act_read1)
desc("13D raw flags we did not keep (takeable)", act_raw)
for k in ("c5", "c10"):
    print("   permutation p, difference in means,", k, perm([m.get(k) for m in act_read1], [m.get(k) for m in act_raw]))
ins = G.get(("TRACKED", "Insider buying"), [])
con = G.get(("TRACKED", "Contracts and catalysts"), []) + G.get(("WATCH", "Contracts and catalysts"), []) + G.get(("OWN", "Contracts and catalysts"), [])
arb = G.get(("TRACKED", "Merger arb and tenders"), []) + G.get(("WATCH", "Merger arb and tenders"), [])
desc("Insider buying we tracked", first(ins))
desc("Contracts and catalysts we tracked", first(con))
desc("Merger arb and tenders we tracked", first(arb))
allread = first([m for (v, g), ms in G.items() if v in ("TRACKED", "WATCH", "OWN") for m in ms])
desc("EVERY long-side name we wrote up", allread)
rawlong = first([r for r in rows if r["cat"] in ("8k_strategic_review", "activist_13d", "tender_issuer_buyback") and r["take"] and r["ticker"] not in {m["ticker"] for m in allread}])
desc("Raw long flags we did not write up (takeable)", rawlong)
for k in ("c5", "c10"):
    print("   permutation p,", k, perm([m.get(k) for m in allread], [m.get(k) for m in rawlong]))

print("\n=== 2. AVOID register vs raw supply flags (excess vs matched) ===")
A = list(csv.DictReader(open(ROOT / "ledger/avoid_register.csv", encoding="utf-8")))
reg = []
for r in A:
    m = measure(r["ticker"], r["date"])
    if not m:
        continue
    matched(r["ticker"], m)
    m.update(ticker=r["ticker"], date=r["date"], typ=r["supply_type"], status=r["status"], call=r["public_call_id"])
    m["take"] = bool(m["entry_raw"] >= 1 and (m["mdv20"] or 0) >= 150_000)
    reg.append(m)
pickle.dump(reg, open(HERE / "reg.pkl", "wb"))
print(len(A), "register rows;", len(reg), "measured")
desc("ALL register AVOIDs", reg)
desc("  takeable", [m for m in reg if m["take"]])
desc("  not takeable", [m for m in reg if not m["take"]])
for t in ("ongoing_supply", "distress", "warrant_supply", "deal_dilution", "holder_selling", "one_off_offering", "other"):
    ms = [m for m in reg if m["typ"] == t]
    desc("  " + t, ms); desc("     takeable", [m for m in ms if m["take"]])
for pb in range(4):
    desc(f"  price {PB[pb]}", [m for m in reg if m["pb"] == pb])
regt = {m["ticker"] for m in reg}
raw_sup = first([r for r in rows if r["cat"] in ("8k_reverse_split", "registration_effective", "share_registration") and r["ticker"] not in regt])
desc("Raw supply flags never put on the register", raw_sup)
desc("  takeable", [r for r in raw_sup if r["take"]])
for pb in range(4):
    desc(f"  price {PB[pb]}", [r for r in raw_sup if r["pb"] == pb])
for k in ("c5", "c10"):
    print("   register vs raw supply, permutation p,", k, perm([m.get(k) for m in reg], [m.get(k) for m in raw_sup]))

print("\n=== 3. Public calls vs matched unflagged stocks (to the 9 Nov close) ===")
M = list(csv.DictReader(open(ROOT / "calls/CALLS.csv", encoding="utf-8")))
calls = []
for r in M:
    d = r.get("posted_utc", r.get("date", ""))[:10]
    m = measure(r["ticker"], d)
    if not m:
        print(r["id"], r["ticker"], "no data"); continue
    matched(r["ticker"], m)
    last = m["cpath"][-1] if m.get("cpath") else None
    print(f"#{r['id']:>2} {r['ticker']:5} dir {r['direction']:>2} posted {d} entry {m['entry_date']} ${m['entry_raw']:.2f} sessions {len(m['path'])} | stock {m['path'][-1][0]:+6.1f}% | vs IWM {m['path'][-1][1]:+6.1f} | similar stocks {m['bench_path'][-1] if m.get('bench_path') else float('nan'):+6.1f}% | vs matched {last if last is not None else float('nan'):+6.1f} | {PB[m['pb']]}")
    m["id"] = r["id"]; m["dirn"] = int(r["direction"]); m["last_c"] = last; m["last_x"] = m["path"][-1][1]; m["last_r"] = m["path"][-1][0]; m["ticker"] = r["ticker"]
    calls.append(m)
av = [m for m in calls if m["dirn"] == -1]
print(f"AVOID calls n={len(av)}: stock median {median(m['last_r'] for m in av):+.1f}% | vs IWM median {median(m['last_x'] for m in av):+.1f} | vs matched median {median(m['last_c'] for m in av):+.1f}, mean {mean(m['last_c'] for m in av):+.1f}, fell more than similar stocks {sum(m['last_c'] < 0 for m in av)}/{len(av)}")
pickle.dump(calls, open(HERE / "calls.pkl", "wb"))

print("\n=== 4. State at the found day, exploration set only (found on or before 21 Oct; TF1's test items are NOT touched) ===")
ex = first([r for r in rows if r["found"] <= "2026-10-21" and r["dirn"] >= 0 and not r["cat"].startswith("setup_supply")
            and r["cat"] not in ("delisting", "8k_lock_up", "8k_merger_agreement", "merger_vote", "8k_tender_offer", "tender_issuer_buyback", "tender_third_party", "merger_arb", "idea_merger", "merger_hostile", "issuer_tender_intent")])
print(len(ex), "buy-side, not deal-pinned items")
def fl(x):
    try: return float(x)
    except Exception: return None
def cut(name, f):
    for lab, test in f:
        ms = [r for r in ex if test(r)]
        parts = [f"{name+': '+lab:44} n={len(ms):3}"]
        for k in ("x20", "c20"):
            s = stats([m.get(k) for m in ms])
            if s.get("n"): parts.append(f"{'vs IWM' if k=='x20' else 'vs matched'} 20d: med {s['med']:+6.1f} mean {s['mean']:+6.1f} beat {s['pos']:3.0f}% (n{s['n']})")
        print(" | ".join(parts))
cut("entry price", [("$5 or more", lambda r: r["entry_raw"] >= 5), ("under $5", lambda r: r["entry_raw"] < 5)])
cut("vs 52-week high", [("within 30%", lambda r: fl(r["l_from_high"]) is not None and fl(r["l_from_high"]) > -30), ("30%+ below", lambda r: fl(r["l_from_high"]) is not None and fl(r["l_from_high"]) <= -30)])
cut("50-day average", [("above", lambda r: r["l_above50"] == "yes"), ("below", lambda r: r["l_above50"] == "no")])
cut("5 days before", [("fell 10%+", lambda r: fl(r["l_pre5"]) is not None and fl(r["l_pre5"]) <= -10), ("did not", lambda r: fl(r["l_pre5"]) is not None and fl(r["l_pre5"]) > -10)])
tf = lambda r: r["entry_raw"] >= 5 and (fl(r["l_from_high"]) or -99) > -30 and r["l_above50"] == "yes" and (fl(r["l_pre5"]) or -99) > -10
cut("TF1-style filter", [("passes all four", tf), ("fails", lambda r: not tf(r))])
