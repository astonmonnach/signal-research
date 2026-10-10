"""Ticker -> SIC industry code for every stock in the runners price panel.

Uses the SEC submissions already cached by the runners study (research/runners/work/sec/subm) and fetches the
rest from data.sec.gov (8 requests a second, with a contact User-Agent). Output: sic_map.csv (ticker, cik, sic, sic_desc).
"""
import csv, json, os, sys, time, urllib.request
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RW = os.path.join(HERE, "..", "runners", "work")
UA = {"User-Agent": "PersonalResearch research@example.com"}

tick = list(np.load(os.path.join(RW, "panel.npz"), allow_pickle=True)["tick"])
m = {}
cs = pd.read_csv(os.path.join(RW, "ref", "cs_tickers.csv"), dtype=str, keep_default_na=False)
for _, r in cs.iterrows():
    if r["cik"]: m[r["ticker"]] = r["cik"].zfill(10)
for v in json.load(open(os.path.join(RW, "ref", "company_tickers.json"))).values():
    m.setdefault(v["ticker"], str(v["cik_str"]).zfill(10))

cache = os.path.join(HERE, "subm_cache"); os.makedirs(cache, exist_ok=True)
rows, fetched, miss = [], 0, 0
for t in tick:
    cik = m.get(t)
    if not cik:
        miss += 1; continue
    j = None
    for p in (os.path.join(RW, "sec", "subm", f"CIK{cik}.json"), os.path.join(cache, f"CIK{cik}.json")):
        if os.path.exists(p):
            try: j = json.load(open(p, encoding="utf-8")); break
            except Exception: pass
    if j is None and "--fetch" in sys.argv:
        try:
            raw = urllib.request.urlopen(urllib.request.Request(f"https://data.sec.gov/submissions/CIK{cik}.json", headers=UA), timeout=30).read()
            j = json.loads(raw); fetched += 1
            json.dump({k: j.get(k) for k in ("cik", "sic", "sicDescription", "name", "tickers")}, open(os.path.join(cache, f"CIK{cik}.json"), "w", encoding="utf-8"))
            time.sleep(0.125)
        except Exception as ex:
            j = None
    if j and j.get("sic"):
        rows.append((t, cik, str(j["sic"]).zfill(4), j.get("sicDescription") or ""))
with open(os.path.join(HERE, "sic_map.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["ticker", "cik", "sic", "sic_desc"]); w.writerows(rows)
print(f"panel tickers {len(tick)} | no CIK {miss} | with SIC {len(rows)} | fetched now {fetched}")
