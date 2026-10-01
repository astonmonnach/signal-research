"""Re-grade the frozen C2 wallet panel on current 30-day GMGN data (read-only, no trading).
Usage: python collectors/c2_grade_panel.py  -> data/crypto/c2_panel_grade_YYYY-MM-DD.csv
Same classes as Desktop/Solana Wallet Finder/refresh.py. A changed panel = a new C2 version."""
import csv, sys
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from c2_convergence import gmgn, PANEL, DIR

def classify(rp, created, trades, toks, tags):
    t = set(tags)
    if "sandwich_bot" in t or trades > 20000: return "bot"
    if created > 30: return "dev"
    if trades > 3000 or toks > 800: return "high-freq"
    if trades < 8: return "thin/dormant"
    if rp < 0: return "losing"
    if rp > 0 and trades <= 2500 and toks <= 400: return "copyable"
    return "profitable"

sys.stdout.reconfigure(encoding="utf-8")
rows = []
for w in PANEL["panel"]:
    d = gmgn(["portfolio", "stats", "--chain", "sol", "--period", "30d", "--raw", "--wallet", w]) or {}
    ps, com = d.get("pnl_stat") or {}, d.get("common") or {}
    trades = int(d.get("buy") or 0) + int(d.get("sell") or 0)
    rp = float(d.get("realized_profit") or 0)
    rows.append({"wallet": w, "class": classify(rp, int(com.get("created_token_count") or 0), trades,
                 int(ps.get("token_num") or 0), com.get("tags") or []) if d else "no-data",
                 "realized_pnl_30d": round(rp), "winrate_pct": round(float(ps.get("winrate") or 0) * 100, 1),
                 "trades_30d": trades})
out = DIR / f"c2_panel_grade_{date.today()}.csv"
w = csv.DictWriter(open(out, "w", newline="", encoding="utf-8"), fieldnames=list(rows[0]))
w.writeheader(); w.writerows(rows)
from collections import Counter
print(Counter(r["class"] for r in rows)); print("total 30d realized PnL of panel: $", sum(r["realized_pnl_30d"] for r in rows))
