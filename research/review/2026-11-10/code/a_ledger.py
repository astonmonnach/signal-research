"""A. Every scanner flag at fixed horizons: raw, vs IWM, and vs matched unflagged stocks."""
import sys, pickle
from bench import *
sys.stdout.reconfigure(encoding="utf-8")
L = ledger()
rows, miss = [], 0
for r in L:
    m = measure(r["ticker"], r["found"])
    if not m:
        miss += 1; continue
    matched(r["ticker"], m)
    m.update(ticker=r["ticker"], found=r["found"], cat=r["category"], dirn=int(r["direction"] or 0), note=r["note"][:90],
             l_from_high=r["from_52w_high_pct"], l_above50=r["above_50d"], l_pre5=r["pre_move_5d"], l_fday=r["found_day_move"], l_relvol=r["rel_volume"])
    m["take"] = bool(m["entry_raw"] >= 1 and (m["mdv20"] or 0) >= 150_000)
    rows.append(m)
print(len(L), "ledger rows;", len(rows), "measured;", miss, "without usable prices;", sum(1 for r in rows if "c5" in r or "c1" in r), "with matched controls")
pickle.dump(rows, open(HERE / "rows.pkl", "wb"))
