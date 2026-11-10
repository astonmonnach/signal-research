"""B. The research layer: every OWN / WATCH pick from the day it was given, kills, public calls, tracked groups."""
import sys, csv, pickle
from bench import *

sys.stdout.reconfigure(encoding="utf-8")

# Every WATCH or OWN verdict as first given in a note or dossier (date of the note; entry = next open after it).
PICKS = [
    ("2026-10-05", "MTUS", "OWN", "funded DLA contract (bought 1 Oct at $19.37)"),
    ("2026-10-05", "RYAM", "WATCH", "strategic review"),
    ("2026-10-05", "MOD", "WATCH", "spin/merger with THRM unit"),
    ("2026-10-05", "THRM", "WATCH", "special dividend + deal"),
    ("2026-10-05", "WHF", "WATCH", "BDC sale review, below NAV"),
    ("2026-10-05", "CTVA", "WATCH", "spin-off"),
    ("2026-10-05", "VYLR", "WATCH", "spin-off"),
    ("2026-10-05", "HMH", "WATCH", "overhang clears"),
    ("2026-10-06", "ESRT", "WATCH", "13D asking for a review"),
    ("2026-10-10", "MSGS", "WATCH", "Rangers spin-off"),
    ("2026-10-12", "BORR", "WATCH", "director's $32M of buying"),
    ("2026-10-12", "SKYA", "WATCH", "$3.00 tender, 16% gap"),
    ("2026-10-14", "PED", "WATCH", "34% holder buys $1.9M"),
    ("2026-10-15", "IMSR", "WATCH", "CEO + 2 directors buy"),
    ("2026-10-16", "SRTA", "WATCH", "Third Point 13D asks for a sale"),
    ("2026-10-20", "DIBS", "WATCH", "billionaire family keeps buying"),
    ("2026-10-20", "ACB", "WATCH", "hostile bid, rival possible"),
    ("2026-10-21", "XPOF", "WATCH", "holder at 19.9% cap inside a sale review"),
    ("2026-10-22", "CPAC", "WATCH", "Holcim going-private tender"),
    ("2026-10-23", "DOLE", "WATCH", "Pale Fire buying a fifth"),
    ("2026-11-01", "SEER", "WATCH", "bids rejected, at half of net cash"),
    ("2026-11-05", "VVR", "WATCH", "Saba 13D at a 12.5% discount"),
]
KILLS = [("2026-10-05", "CHDN", "killed: false-positive review"), ("2026-10-05", "ELMT", "AVOID: already ran"),
         ("2026-10-05", "TWST", "AVOID 3/10"), ("2026-10-20", "THRM", "killed: closed below the line"), ("2026-11-05", "MOD", "dropped")]


def show(title, items, sign=1):
    print("\n==", title)
    print(f"{'date':10} {'tkr':5} {'what':7} {'entry':>8} {'5d':>7} {'10d':>7} {'20d':>7} {'now':>7} | vs IWM {'5d':>6} {'10d':>6} {'20d':>6} {'now':>6} {'maxUp':>6} {'maxDn':>6} why")
    ms = []
    for d, t, what, *why in items:
        m = measure(t, d)
        if not m:
            print(d, t, "no data"); continue
        matched(t, m); m["ticker"] = t; m["what"] = what; m["why"] = why[0] if why else ""; m["date"] = d
        ms.append(m)
        g = lambda k: f"{m[k]:+7.1f}" if m.get(k) is not None else "    n/a"
        print(f"{d} {t:5} {what[:7]:7} {m['entry_raw']:8.2f} {g('r5')} {g('r10')} {g('r20')} {g('r_now')} |        {g('x5')[1:]} {g('x10')[1:]} {g('x20')[1:]} {g('x_now')[1:]} | vsMATCH {g('c5')[1:]} {g('c10')[1:]} {g('c20')[1:]} | {PB[m['pb']]:8} {m['max_up']:+6.1f} {m['max_dn']:+6.1f} {why[0] if why else ''}")
    for k in ("r5", "r10", "r20", "r_now", "x5", "x10", "x20", "x_now", "c5", "c10", "c20"):
        s = stats([m.get(k) for m in ms])
        if s["n"]:
            print(f"   {k:6} n={s['n']:2} median {s['med']:+6.1f} mean {s['mean']:+6.1f} positive {s['pos']:3.0f}%")
    return ms


picks = show("OWN / WATCH picks, from the next open after the verdict", PICKS)
show("Kills and AVOID verdicts on names we had looked at as longs", [(d, t, "kill", w) for d, t, w in KILLS])

# Public calls
M = list(csv.DictReader(open(ROOT / "calls/marks.csv", encoding="utf-8")))
print("\n== Public calls (calls/marks.csv)")
for r in M:
    print(r["id"], r["ticker"], r["direction"], r["entry_date"], r["entry"], "->", r["end_price"], r["ret_pct"], "vs IWM", r["excess_bench"], "ctrl", r["control"], r["excess_control"], r["status"])

# found.csv tracked groups at fixed horizons
F = list(csv.DictReader(open(ROOT / "research/found/found.csv", encoding="utf-8")))
print("\n== found.csv by view and group (fixed horizons, vs IWM), takeable = $1+ and $150k/day")
import collections
G = collections.defaultdict(list)
for r in F:
    m = measure(r["ticker"], r["found"])
    if not m:
        continue
    matched(r["ticker"], m)
    m["take"] = bool(m["entry_raw"] >= 1 and (m["mdv20"] or 0) >= 150_000)
    m["ticker"] = r["ticker"]; m["view"] = r["view"]; m["group"] = r["group"]; m["found"] = r["found"]
    G[(r["view"], r["group"])].append(m)
for (v, g), ms in sorted(G.items()):
    for label, sub in (("all", ms), ("takeable", [m for m in ms if m["take"]])):
        if not sub:
            continue
        parts = []
        for h in (5, 10, 20):
            s = stats([m.get(f"c{h}") for m in sub]); sx = stats([m.get(f"x{h}") for m in sub])
            parts.append(f"{h}d IWM {fmt(sx):>6} MATCH {fmt(s):>6} med/{fmt(s,'wmean'):>6} avg beat {s.get('pos',0):3.0f}% n{s['n']:<3}")
        s = stats([m.get("x_now") for m in sub])
        print(f"{v:7} {g[:34]:34} {label:8} n={len(sub):3} | " + " | ".join(parts) + f" | now {fmt(s)} med")
pickle.dump(dict(G), open(HERE / "found_groups.pkl", "wb")); pickle.dump(picks, open(HERE / "picks.pkl", "wb"))
